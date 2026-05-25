"""
Scene state machine (Menu / Play / GameOver) plus the top-level App class.
"""
import math
import pygame

from game.config import W, H, FPS, TITLE, GROUND_Y
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
    get_scratch_surface,
    UI_RED,
)
from game import biome as _biome
from game.world import World
from game.hud import HUD, _font
from game import audio
from game import play_log
from game.config import BIRD_X, SCROLL_BASE
from game import intro as _intro
from game.lottery_slot import draw_reveal as _draw_lottery_reveal

# Pixels of `bg_scroll` covered while the gameplay opener is active. After
# the post-ready grace window, the cottage is fully off-screen-left and the
# overlay shuts itself off.
_OPENER_SCROLL_END = int(World.SPAWN_GRACE * SCROLL_BASE)


def _draw_opener(surf: pygame.Surface, world) -> None:
    """Gameplay opener — cottage drifting off-screen-left + parcel tucked
    beneath Pip. Mirrors the intro's beat-2 ending so the cut from menu →
    play preserves the cinematic's final image. Runs for the first
    ``World.SPAWN_GRACE`` seconds after the ready_t freeze expires."""
    progress = world.bg_scroll / _OPENER_SCROLL_END
    if progress >= 1.0:
        return
    # Fade out over the last 30% so the cottage doesn't snap-disappear.
    fade = 1.0 if progress < 0.7 else max(0.0, 1.0 - (progress - 0.7) / 0.3)
    alpha = int(255 * fade)

    house = _intro.get_sprite("skyhouse_post")
    house_cx = int(W * 0.30) - int(world.bg_scroll)
    house_cy = int(H * 0.42)
    hx = house_cx - house.get_width() // 2
    hy = house_cy - house.get_height() // 2
    if hx + house.get_width() > 0 and alpha > 0:
        if alpha < 255:
            faded = house.copy()
            faded.set_alpha(alpha)
            surf.blit(faded, (hx, hy))
        else:
            surf.blit(house, (hx, hy))
    # The parcel itself is now drawn permanently by Bird.draw, so the
    # opener no longer needs its own parcel pass.


# ── Rail powerup render helpers (called from App._render) ──────────────────

_PINE_DK = ( 70,  45,  25)
_PINE    = (135,  90,  50)
_PINE_HI = (180, 130,  75)
_IRON_DK = ( 50,  45,  45)
_IRON    = (110, 100,  95)
_IRON_HI = (190, 180, 175)


def _draw_parked_cart_at(surf, cx, cy, tilt_deg=0.0):
    """Stationary pine-plank wagon at the given screen position. Used
    both for the pre-lock parked cart on rail_cart_pipe and for the
    locked-ride cart drawn on top of Pip. Tilt rotates the whole
    wagon to follow the rail slope."""
    # Paint to a scratch surface so we can rotate as one piece.
    SW, SH = 60, 38
    scratch = pygame.Surface((SW, SH), pygame.SRCALPHA)
    scx = SW // 2
    scy = SH // 2 - 2

    # Wheels (pine-spoke wheel + iron tire)
    WHEEL_R = 5
    DX = 15
    wheel_y = scy + 22
    for dx in (-DX, DX):
        wx = scx + dx
        pygame.draw.circle(scratch, _IRON_DK, (wx, wheel_y), WHEEL_R)
        pygame.draw.circle(scratch, _IRON,    (wx, wheel_y), WHEEL_R - 1)
        pygame.draw.circle(scratch, _PINE_DK, (wx, wheel_y), WHEEL_R - 2)
        for i in range(6):
            ang = (i / 6) * math.tau
            ex = wx + int(math.cos(ang) * (WHEEL_R - 2))
            ey = wheel_y + int(math.sin(ang) * (WHEEL_R - 2))
            pygame.draw.line(scratch, _PINE_DK, (wx, wheel_y), (ex, ey), 1)
        pygame.draw.circle(scratch, _IRON_DK, (wx, wheel_y), 1)

    # Body (pine planks + iron hoop bands)
    BW = 42
    BH = 18
    body_top = scy + 4
    body_bot = scy + 4 + BH
    pygame.draw.rect(scratch, _PINE_DK,
                     pygame.Rect(scx - BW // 2 - 1, body_top - 1,
                                 BW + 2, BH + 2))
    pygame.draw.rect(scratch, _PINE,
                     pygame.Rect(scx - BW // 2, body_top, BW, BH))
    for i in range(1, BW // 6):
        px = scx - BW // 2 + i * 6
        pygame.draw.line(scratch, _PINE_DK,
                         (px, body_top + 1), (px, body_bot - 1), 1)
        pygame.draw.line(scratch, _PINE_HI,
                         (px + 1, body_top + 1),
                         (px + 1, body_bot - 1), 1)
    for band_y in (body_top + 2, body_bot - 5):
        pygame.draw.rect(scratch, _IRON_DK,
                         pygame.Rect(scx - BW // 2 - 1, band_y,
                                     BW + 2, 3))
        pygame.draw.rect(scratch, _IRON,
                         pygame.Rect(scx - BW // 2 - 1, band_y + 1,
                                     BW + 2, 1))
        pygame.draw.line(scratch, _IRON_HI,
                         (scx - BW // 2 - 1, band_y),
                         (scx + BW // 2 + 1, band_y), 1)

    if abs(tilt_deg) > 0.5:
        scratch = pygame.transform.rotate(scratch, tilt_deg)
    rect = scratch.get_rect(center=(int(cx), int(cy)))
    surf.blit(scratch, rect.topleft)


def _draw_parked_cart(surf, pipe):
    """Pre-lock cart parked on the rail line of `pipe` (the first
    tagged pillar). Removed once Pip locks or the pillar scrolls past."""
    from game.config import PIPE_W
    cx = pipe.x + PIPE_W // 2
    rail_y = pipe.gap_y + pipe.gap_h / 2
    # 32-px lift matches World._CART_LOCKED_OFFSET so the parked cart
    # sits visually identical to the locked-ride cart.
    _draw_parked_cart_at(surf, cx, rail_y - 16)


def _draw_cart_on_bird(surf, world, sx, sy):
    """Locked-ride cart drawn at Pip's screen position with the local
    rail slope rotation. Pip himself still renders separately on top."""
    bx = world.bird.x + sx
    by = world.bird.y + sy
    # Bird sits 32 px above the rail line; the cart wheels need to be
    # on the rail, so anchor the cart slightly below the bird centre.
    _draw_parked_cart_at(surf, bx, by + 16, tilt_deg=world.bird.cart_tilt_deg)


def _draw_rails(surf, rail_pipes):
    """Continuous pine-tie + twin iron-rail polyline across every
    rail-tagged pipe top."""
    from game.config import PIPE_W
    if not rail_pipes:
        return
    pipes_sorted = sorted(rail_pipes, key=lambda p: p.x)
    pts = []
    for p in pipes_sorted:
        rail_y = int(p.gap_y + p.gap_h / 2)
        pts.append((int(p.x), rail_y))
        pts.append((int(p.x + PIPE_W), rail_y))
    _draw_trestle_rail(surf, pts)


def _draw_trestle_rail(surf, pts):
    """Pine ties + twin iron rails along a polyline. Bridges between
    consecutive pipes keep their ties so the result reads as one
    continuous railway."""
    if len(pts) < 2:
        return

    segs, total = [], 0.0
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        d = math.hypot(x1 - x0, y1 - y0)
        segs.append((d, (x0, y0), (x1, y1)))
        total += d
    spacing = 8
    length = 14
    half = length / 2
    n = max(1, int(total / spacing))
    for k in range(n + 1):
        target = (k / n) * total
        acc = 0.0
        for d, p0, p1 in segs:
            if acc + d >= target:
                f = (target - acc) / max(1.0, d)
                cx = int(p0[0] + (p1[0] - p0[0]) * f)
                cy = int(p0[1] + (p1[1] - p0[1]) * f)
                dx = p1[0] - p0[0]
                dy = p1[1] - p0[1]
                seg_len = max(1.0, math.hypot(dx, dy))
                nx = -dy / seg_len
                ny = dx / seg_len
                a = (int(cx + nx * half), int(cy + ny * half))
                b = (int(cx - nx * half), int(cy - ny * half))
                pygame.draw.line(surf, _PINE_DK, a, b, 5)
                pygame.draw.line(surf, _PINE, a, b, 3)
                hi_a = (int(cx + nx * half * 0.55),
                        int(cy + ny * half * 0.55))
                hi_b = (int(cx - nx * half * 0.55),
                        int(cy - ny * half * 0.55))
                pygame.draw.line(surf, _PINE_HI, hi_a, hi_b, 1)
                break
            acc += d

    for dy_off, col, w in (
        ( 3, _IRON_DK, 3), (-3, _IRON_DK, 3),
        ( 3, _IRON,    2), (-3, _IRON,    2),
        ( 2, _IRON_HI, 1), (-4, _IRON_HI, 1),
    ):
        shifted = [(x, y + dy_off) for x, y in pts]
        pygame.draw.lines(surf, col, False, shifted, w)


# Hex grid overlay for the magnet force-field. Built once per radius
# and re-blit each frame — the rings pulse but the hex pattern is
# static, so building it lazily here keeps the per-frame work in the
# magnet draw loop bounded (one blit instead of ~225 polygon draws
# at MAGNET_RADIUS). Cells fade from invisible at the centre to full
# alpha at the rim so the bird stays the focal point.
_MAGNET_HEX_GRID_CACHE: "dict[int, pygame.Surface]" = {}


def _magnet_hex_grid(radius: int) -> pygame.Surface:
    cached = _MAGNET_HEX_GRID_CACHE.get(radius)
    if cached is not None:
        return cached
    surf = pygame.Surface((radius * 2 + 8, radius * 2 + 8),
                          pygame.SRCALPHA)
    cx, cy = radius + 4, radius + 4
    hex_r = max(5, int(radius * 0.085))
    hex_w = hex_r * math.sqrt(3)
    hex_h = hex_r * 1.5
    rows = int(radius * 2 / hex_h) + 3
    cols = int(radius * 2 / hex_w) + 3
    for ri in range(-rows // 2, rows // 2 + 1):
        for ci in range(-cols // 2, cols // 2 + 1):
            hx = cx + ci * hex_w + (hex_w / 2 if ri % 2 else 0)
            hy = cy + ri * hex_h
            dx = hx - cx
            dy = hy - cy
            d = math.hypot(dx, dy)
            if d > radius * 0.92:
                continue
            falloff = d / radius
            a = int(160 * (falloff ** 1.5))
            if a < 12:
                continue
            verts = []
            for v in range(6):
                ang = math.tau * v / 6 + math.pi / 6
                verts.append((hx + math.cos(ang) * hex_r,
                              hy + math.sin(ang) * hex_r))
            pygame.draw.polygon(surf, (255, 215, 100, a), verts, 1)
    _MAGNET_HEX_GRID_CACHE[radius] = surf
    return surf


STATE_MENU = 0
STATE_PLAY = 1
STATE_NAMEENTRY = 2
STATE_GAMEOVER = 3
STATE_PAUSE = 4
STATE_STATS = 5
STATE_LEADERBOARD = 6
STATE_INTRO = 7
STATE_POWERUPS = 8


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        audio.init()
        self.world = World()
        self.hud = HUD()
        self.session_best = 0
        self._new_best = False
        # Which action the player picked on the run-summary screen.
        # Persists across STATE_NAMEENTRY / STATE_LEADERBOARD so that
        # after a top-10 player dismisses the leaderboard they land
        # where they originally chose. Reset on death so each run
        # starts fresh.
        self._post_leaderboard: str = "menu"
        # Intro plays once per program launch — start every session in
        # STATE_INTRO. Within the session (consecutive games after death,
        # menu-tap → play → die → menu) the intro is never replayed since
        # the App stays alive and we already moved past STATE_INTRO.
        from game.intro import IntroScene
        self.intro: object | None = IntroScene()
        # Built lazily when the intro auto-completes (not when the user
        # skips it). Lives until the player taps once on the help screen.
        self.powerup_help: object | None = None
        # True when the intro was launched from the menu's HOW TO PLAY
        # button. _finish_intro reads this to land back on MENU instead
        # of the POWERUPS explainer.
        self._intro_from_menu = False
        self.state = STATE_INTRO
        self._cloud_phase = 0.0
        self._running = True
        self._stats_t = 0.0
        # True while the HTML splash overlay is still painted on top of
        # the canvas; flips False on the first user-visible frame (in
        # async_run, when first_frame_done is set). The intro update
        # gates on this so the cinematic clock doesn't accumulate while
        # pygbag is still booting — without it, by the time the splash
        # dismisses the intro can be ~7 s in (opening on the "avoid
        # pillars" sub-beat instead of the dawn one).
        self._splash_covering = True
        # Touch dedup: SDL emits both FINGERDOWN and a synthetic MOUSEBUTTONDOWN
        # for one tap on mobile, so naive routing types every key twice. After
        # any FINGERDOWN, suppress mouse events for a 0.5 s window. On pure
        # desktop this never fires (no FINGERDOWN ever arrives).
        self._last_finger_t = -1e9
        self._finger_dedup_window = 0.5
        # Leaderboard state
        self._lb_scores: list = []
        self._lb_player_rank = -1
        # Last browser-side fetch error code (empty when the fetch
        # succeeded, even if it returned zero rows from a brand-new
        # database). Set by _on_name_submitted / _show_leaderboard_native
        # before flipping to STATE_LEADERBOARD; rendered by the scene
        # when scores is empty so a network/RLS failure doesn't look
        # like "no scores yet."
        self._lb_fetch_error: str = ""
        self._start_name_entry = False
        self._fetch_pending = False
        self._final_score = 0
        self._name_task = None  # strong ref prevents GC killing the task mid-flight
        self._play_log_task = None  # strong ref for the per-run telemetry POST
        self._lb_task = None  # strong ref for the menu-trophy leaderboard fetch
        self._name_input_buf = ""  # native name-entry text buffer

        # ── Deferred pre-warm queue ─────────────────────────────────────────
        # Two power-ups had per-pickup build cost (GROW: ~50 ms first
        # build; KFC: 7-37 ms per variant per pickup). Building both at
        # startup made initial load 150+ ms slower. Instead we queue the
        # builds and drain ONE per frame in ``_update`` after the first
        # paint — startup pays nothing, and the cache fills over the
        # next ~4 frames (during the intro animation where the small
        # per-frame cost is masked). ``get_cached_mountain`` builds on
        # demand if a pickup happens before its variant is warm.
        from game import parrot
        from game.fries_mountains import LAYER_DRAWERS, get_cached_mountain
        self._prewarm_queue = [
            ("grow",    lambda: parrot._get_grow_frames()),
            ("kfc0",    lambda: get_cached_mountain(0, GROUND_Y, W)),
            ("kfc1",    lambda: get_cached_mountain(1, GROUND_Y, W)),
            ("kfc2",    lambda: get_cached_mountain(2, GROUND_Y, W)),
        ]

    # ── helpers ─────────────────────────────────────────────────────────────

    @property
    def best(self):
        return self.session_best

    # ── input ────────────────────────────────────────────────────────────────

    def _flap_input(self, pos=None):
        if self.state == STATE_INTRO:
            # Any tap during the cinematic skips it. Gate by `_cooldown_t`
            # so the same physical tap that opened the intro (FINGERDOWN
            # → MOUSEBUTTONDOWN echo, or a duplicate FINGERDOWN on flaky
            # devices) can't immediately skip it back out. The cooldown
            # ticks down inside _update so a deliberate skip works a
            # beat later.
            #
            # Also bail while `_splash_covering` is still True: the HTML
            # splash overlay is on top of the canvas, so the player can't
            # see the intro and isn't tapping it deliberately. The pygbag
            # boot kick (inject_theme.fireSyntheticGesture) dispatches a
            # full pointer/mouse/touch sequence to satisfy the UME gate,
            # and those events reach this handler — without the gate they
            # silently skip the intro before the first frame ever renders.
            if self._splash_covering:
                return
            if self._cooldown_t > 0:
                return
            self._finish_intro(skipped=True)
            return
        if self.state == STATE_POWERUPS:
            # Same shape: gate the dismiss-tap on the entry cooldown so
            # the explainer doesn't flicker straight back to MENU.
            if self._cooldown_t > 0:
                return
            self.powerup_help = None
            self.state = STATE_MENU
            self._cooldown_t = 0.25
            return
        if self.state == STATE_MENU:
            # Single shared cooldown gate for every menu action. This is
            # what stops a follow-up event from the same physical tap
            # (e.g. the second FINGERDOWN that dismissed INTRO → MENU)
            # from immediately dispatching a help-button hit at the same
            # screen position. Kept short (0.25 s, set on every menu
            # entry) so a deliberate first tap from a settled menu still
            # feels instant — typical reaction time is well above 0.25 s.
            if self._cooldown_t > 0:
                return
            if pos and self.hud.menu_howto_rect \
                    and self.hud.menu_howto_rect.collidepoint(pos):
                from game.intro import IntroScene
                self.intro = IntroScene()
                self._intro_from_menu = True
                self.state = STATE_INTRO
                self._cooldown_t = 0.25
                return
            if pos and self.hud.menu_powerups_rect \
                    and self.hud.menu_powerups_rect.collidepoint(pos):
                from game.powerup_help import PowerUpHelpScene
                self.powerup_help = PowerUpHelpScene()
                self.state = STATE_POWERUPS
                self._cooldown_t = 0.25
                return
            if pos and self.hud.menu_top10_rect \
                    and self.hud.menu_top10_rect.collidepoint(pos):
                self._open_leaderboard_from_menu()
                return
            # Start a run only when the player hits the START pill (or
            # presses a key — no pos for keyboard events). Taps that
            # land anywhere else on the menu are a no-op so an accidental
            # touch outside the pill can't fling the player into play.
            if pos is None or (self.hud.menu_start_rect
                               and self.hud.menu_start_rect.collidepoint(pos)):
                self._start_play()
        elif self.state == STATE_PLAY:
            if pos and self.hud.pause_btn.contains(pos):
                self.state = STATE_PAUSE
                return
            self.world.flap()
        elif self.state == STATE_PAUSE:
            self.state = STATE_PLAY
        elif self.state == STATE_STATS:
            if self._stats_t < 0.6 or self._fetch_pending:
                return
            # Hit-test the run-summary buttons. The HUD populates these
            # rects each frame in draw_stats; before the 0.6s reveal
            # gate they are empty so taps in that window do nothing.
            play_rect = getattr(self.hud, "stats_play_again_rect", None)
            menu_rect = getattr(self.hud, "stats_main_menu_rect", None)
            if pos and play_rect and play_rect.collidepoint(pos):
                self._post_leaderboard = "play"
                self._advance_past_stats()
            elif pos and menu_rect and menu_rect.collidepoint(pos):
                self._post_leaderboard = "menu"
                self._advance_past_stats()
        elif self.state == STATE_NAMEENTRY:
            pass  # JS overlay handles input
        elif self.state == STATE_LEADERBOARD:
            if self._cooldown_t <= 0:
                # Branch on the run-summary intent so the player lands
                # where they chose on the stats screen after they've
                # dismissed the leaderboard celebration.
                if self._post_leaderboard == "play":
                    self._restart()
                else:
                    self.state = STATE_MENU
                # Keep the menu visible for a beat instead of letting the
                # next event in the same tap (FINGERDOWN / MOUSEBUTTONDOWN
                # echoes, or a fast double-click) skip straight into play.
                self._cooldown_t = 0.4
        elif self.state == STATE_GAMEOVER:
            if self._cooldown_t <= 0:
                self._restart()

    def _toggle_pause(self):
        if self.state == STATE_PLAY:
            self.state = STATE_PAUSE
        elif self.state == STATE_PAUSE:
            self.state = STATE_PLAY

    def _start_play(self):
        # The menu IS the start-of-game screen, so the click that brought
        # us here counts as the first flap — drop the ready_t freeze and
        # apply an initial flap so Pip launches immediately. The gameplay
        # opener (post-house drifting off-screen-left) still plays for
        # the first ~2.5 s of bg_scroll.
        self.world = World()
        self.world.ready_t = 0.0
        self.world.flap()
        self.state = STATE_PLAY

    def _finish_intro(self, skipped: bool):
        """Hand off out of the intro. The next state depends on `skipped`:

          * `skipped=True`  — the player tapped during the cinematic. They
            wanted to bail past the intro flow, so we drop them straight
            on the menu, bypassing the power-ups explainer.
          * `skipped=False` — the cinematic ran to its natural end. Land
            on the power-ups explainer, which stays up until the player
            taps once more to reach the menu.

        Sets a brief cooldown so the same physical tap that triggered the
        skip can't echo into the now-MENU state and immediately call
        ``_start_play`` or open one of the secondary menu buttons. 0.25 s
        is enough to swallow:
          - SDL FINGERDOWN → MOUSEBUTTONDOWN echo (~tens of ms)
          - a duplicate FINGERDOWN that flaky touch firmware can emit
          - a fast follow-up tap that would otherwise cascade

        and short enough that a deliberate first tap from a settled
        menu (well past typical 200–300 ms reaction time) still feels
        instant.

        Mirror of the STATE_LEADERBOARD → MENU pattern in ``_flap_input``."""
        if self.intro is not None:
            self.intro.skip()
        self.intro = None
        if self._intro_from_menu:
            # HOW TO PLAY replay always returns to MENU regardless of
            # whether the player tapped to skip or watched it through.
            self.state = STATE_MENU
            self._intro_from_menu = False
        elif skipped:
            self.state = STATE_MENU
        else:
            from game.powerup_help import PowerUpHelpScene
            self.powerup_help = PowerUpHelpScene()
            self.state = STATE_POWERUPS
        self._cooldown_t = 0.25

    def _restart(self):
        # Same contract as `_start_play`: the tap that triggered the
        # restart counts as the first flap, no ready freeze.
        self.world = World()
        self.world.ready_t = 0.0
        self.world.flap()
        self.state = STATE_PLAY

    # ── run loop ────────────────────────────────────────────────────────────

    def run(self):
        # Sync entry point for native execution. Browser builds (pygbag) must
        # call async_run() directly so the page's event loop stays alive.
        import asyncio
        asyncio.run(self.async_run())

    async def async_run(self):
        import asyncio
        import sys as _sys
        self._cooldown_t = 0.0
        self._start_name_entry = False
        first_frame_done = False
        while self._running:
            dt = min(self.clock.tick(FPS) / 1000.0, 1 / 20.0)
            for e in pygame.event.get():
                self._handle_event(e)
            self._update(dt)
            self._render()
            pygame.display.flip()
            if not first_frame_done:
                first_frame_done = True
                # Splash overlay is about to start fading — let the
                # intro clock start ticking from here. See
                # `self._splash_covering` for the rationale.
                self._splash_covering = False
                # The boot kick (inject_theme.fireSyntheticGesture) retries
                # every 250 ms until it sees skybitGameReady. We just set
                # that flag, but events fired in the last retry interval
                # may still be sitting in the pygame queue. Set a short
                # cooldown so those trailing synthetic taps can't skip the
                # intro the instant the splash lifts.
                self._cooldown_t = max(self._cooldown_t, 0.4)
                # Signal to the JS overlay (inject_theme.py's dismiss()
                # waits on this) that the canvas now has a real Skybit
                # frame on it. Without this, the overlay would fade off
                # while pygbag's bare progress display was still visible
                # underneath -- the "separate screen" the user reported
                # between Skybit splash and the rendered intro.
                if _sys.platform == "emscripten":
                    try:
                        import js  # type: ignore
                        js.window.skybitGameReady = True
                    except Exception:
                        pass
            if self._start_name_entry:
                self._start_name_entry = False
                # create_task keeps the game loop running every frame while the
                # network coroutine makes progress between asyncio.sleep(0) yields.
                # Store strong ref so GC doesn't silently kill the task mid-flight.
                self._name_task = asyncio.create_task(self._on_name_submitted())
            # Yield to the browser's event loop each frame. On native runs
            # this is a zero-cost no-op between ticks.
            await asyncio.sleep(0)
        pygame.quit()

    def _handle_event(self, e):
        if e.type == pygame.QUIT:
            self._running = False
            return
        # Note when a real finger event arrives so we can suppress the
        # synthetic mouse follow-up that SDL fires for the same tap.
        now = pygame.time.get_ticks() / 1000.0
        if e.type == pygame.FINGERDOWN:
            self._last_finger_t = now
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if now - self._last_finger_t < self._finger_dedup_window:
                return  # this MOUSEBUTTONDOWN is a touch echo — ignore
        import sys as _sys
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_p:
                self._toggle_pause()
                return
            if e.key == pygame.K_ESCAPE:
                if self.state in (STATE_PLAY, STATE_PAUSE):
                    self._toggle_pause()
                else:
                    self._running = False
                return
            # Native name-entry keyboard: intercept before flap routing.
            # ENTER submits; ESC no longer skips — there's a clickable
            # SKIP button now.
            if self.state == STATE_NAMEENTRY and _sys.platform != "emscripten":
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._submit_name_native(self._name_input_buf.strip())
                elif e.key == pygame.K_BACKSPACE:
                    self._name_input_buf = self._name_input_buf[:-1]
                elif e.unicode and e.unicode.isprintable() and len(self._name_input_buf) < 16:
                    self._name_input_buf += e.unicode
                return
            if e.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self._flap_input()
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if self._handle_name_entry_click(e.pos):
                return
            self._flap_input(e.pos)
        elif e.type == pygame.FINGERDOWN:
            pos = (int(e.x * W), int(e.y * H))
            if self._handle_name_entry_click(pos):
                return
            self._flap_input(pos)

    def _handle_name_entry_click(self, pos) -> bool:
        """If we're on the native name-entry screen and the click hit the
        SUBMIT or SKIP button, dispatch and return True. Returns False
        otherwise so normal flap routing can proceed."""
        import sys as _sys
        if self.state != STATE_NAMEENTRY or _sys.platform == "emscripten":
            return False
        if self.hud.name_submit_rect.collidepoint(pos):
            if self._name_input_buf.strip():
                self._submit_name_native(self._name_input_buf.strip())
            return True
        if self.hud.name_skip_rect.collidepoint(pos):
            self._submit_name_native("")
            return True
        return False

    # ── update ──────────────────────────────────────────────────────────────

    def _update(self, dt):
        self._cloud_phase += dt
        # Drain one prewarm task per frame after the splash has lifted, so
        # the GROW + KFC caches fill incrementally during the intro
        # rather than blocking startup. Each task takes 7-55 ms.
        if self._prewarm_queue and not self._splash_covering:
            _, task = self._prewarm_queue.pop(0)
            task()
        if self.state == STATE_INTRO:
            if self.intro is None:
                # Defensive: should never happen, but recover gracefully.
                self._finish_intro(skipped=True)
                return
            # Hold the intro at t=0 while the HTML splash is still
            # painting over the canvas — async_run flips this flag the
            # moment the first visible frame fires. Without the gate
            # the cinematic fast-forwards past the dawn beat during
            # pygbag's boot.
            if not self._splash_covering:
                self.intro.update(dt)
            # Tick the cooldown so a HOW-TO-PLAY-launched intro becomes
            # skippable a beat after it opens (see the gate in
            # _flap_input's STATE_INTRO branch).
            self._cooldown_t = max(0.0, self._cooldown_t - dt)
            if self.intro.done:
                # The cinematic ran out — show the power-ups explainer.
                # (User-initiated skips already routed through _flap_input.)
                self._finish_intro(skipped=False)
            return
        if self.state == STATE_POWERUPS:
            if self.powerup_help is not None:
                self.powerup_help.update(dt)
            self._cooldown_t = max(0.0, self._cooldown_t - dt)
            return
        if self.state == STATE_MENU:
            self.world.world_idle_tick(dt)
            self._cooldown_t = max(0.0, self._cooldown_t - dt)
        elif self.state == STATE_PLAY:
            self.world.update(dt)
            if self.world.game_over:
                self._on_death()
        elif self.state == STATE_PAUSE:
            # World is frozen. Still tick the HUD pulse so the overlay animates.
            self.hud.title_t += dt
        elif self.state == STATE_STATS:
            self.world.update(dt)  # let particles/weather keep going behind
            self._stats_t += dt
            # No auto-advance — the screen stays until the player taps
            # (handled in _flap_input).
        elif self.state == STATE_NAMEENTRY:
            self.world.update(dt)  # keep world alive behind JS overlay
        elif self.state == STATE_LEADERBOARD:
            self._cooldown_t = max(0.0, self._cooldown_t - dt)
        elif self.state == STATE_GAMEOVER:
            self.world.update(dt)
            self._cooldown_t = max(0.0, self._cooldown_t - dt)

    def _on_death(self):
        score = self.world.score
        self._new_best = score > self.session_best
        if self._new_best:
            self.session_best = score
        # Fire-and-forget telemetry: send the run summary to Supabase
        # (browser-only; native is a silent no-op). Strong ref on
        # self prevents GC from killing the task mid-flight.
        import asyncio as _asyncio
        try:
            self._play_log_task = _asyncio.create_task(play_log.log_run(self.world))
        except RuntimeError:
            # No running loop (e.g. headless smoke tests) — skip silently.
            pass
        # Game-over screen no longer plays its own jingle — death.ogg
        # at the moment of impact carries the whole "run ended" cue.
        self.state = STATE_STATS
        self._stats_t = 0.0
        # Reset the run-summary intent so a freshly opened stats
        # screen defaults to "main menu" until the player explicitly
        # taps PLAY AGAIN.
        self._post_leaderboard = "menu"

    def _advance_past_stats(self):
        """Tap on run-summary: if the score qualifies for top 10, the
        player flows into name entry and then the leaderboard view
        (so they see where their name landed). Otherwise we route
        straight back to the main menu — the leaderboard is still
        one tap away from there via the TOP 10 trophy."""
        import sys
        self._final_score = self.world.score
        self._name_input_buf = ""
        if sys.platform == "emscripten":
            # Browser: kick off async fetch; _on_name_submitted decides
            # qualifies → NAMEENTRY → LEADERBOARD vs back to MENU.
            self._lb_scores = []
            self._lb_player_rank = -1
            self._fetch_pending = True
            self._start_name_entry = True
        else:
            # Native: top-10 lives in local JSON, fetch is sync.
            from game import leaderboard
            scores = leaderboard._native_fetch()
            if self._qualifies_for_top10(scores, self._final_score):
                self.state = STATE_NAMEENTRY
            else:
                # Non-qualifying: honour the player's stats-screen
                # choice. PLAY AGAIN starts a new run immediately;
                # MAIN MENU lands them on the menu (legacy default).
                self.hud.title_t = 0.0
                if self._post_leaderboard == "play":
                    self._restart()
                else:
                    self.state = STATE_MENU
                self._cooldown_t = 0.25

    @staticmethod
    def _qualifies_for_top10(scores, score) -> bool:
        if score <= 0:
            return False
        if len(scores) < 10:
            return True
        return score > scores[-1]["score"]

    def _open_leaderboard_from_menu(self):
        """Tap on the TOP 10 trophy panel in the main menu. Browser:
        kick off an async Supabase fetch but stay on the menu — the
        async task switches state to STATE_LEADERBOARD once the scores
        are in hand, so the player never sees a 'Loading top 10…'
        flash. Native: synchronous local fetch.

        No player highlight (``_lb_player_rank = -1``) because there's
        no just-finished run to rank. The same STATE_LEADERBOARD → MENU
        tap pattern that lives in ``_flap_input`` handles the way back."""
        import sys
        self._lb_player_rank = -1
        if sys.platform == "emscripten":
            if self._fetch_pending:
                # An earlier tap is still in flight — ignore re-taps
                # so we don't spawn parallel fetch tasks.
                return
            self._lb_scores = []
            self._lb_fetch_error = ""
            self._fetch_pending = True
            import asyncio
            try:
                self._lb_task = asyncio.create_task(
                    self._fetch_leaderboard_from_menu())
            except RuntimeError:
                # No running event loop (smoke tests). Skip the fetch;
                # the player stays on the menu.
                self._fetch_pending = False
        else:
            from game import leaderboard
            scores = leaderboard._native_fetch()
            self._show_leaderboard_native(scores, submitted=False)

    async def _fetch_leaderboard_from_menu(self):
        """Background task for the menu trophy button. Fetches Supabase
        top-10, stores it on the scene, then switches to
        STATE_LEADERBOARD — keeping the player on the menu until the
        scores are ready avoids the transient 'Loading…' screen."""
        try:
            from game import leaderboard
            scores = await leaderboard.fetch_top10()
            self._lb_scores = scores
            self._lb_fetch_error = leaderboard.last_fetch_error()
        except Exception:
            pass
        self._fetch_pending = False
        self.hud.title_t = 0.0
        self.state = STATE_LEADERBOARD
        self._cooldown_t = 0.25

    def _show_leaderboard_native(self, scores, submitted: bool):
        self._lb_scores = scores
        if scores and submitted:
            self._lb_player_rank = next(
                (i for i, e in enumerate(scores) if e["score"] == self._final_score),
                -1,
            )
        else:
            self._lb_player_rank = -1
        self.hud.title_t = 0.0
        self.state = STATE_LEADERBOARD
        self._cooldown_t = 0.25

    def _submit_name_native(self, name: str):
        """Finish native name-entry: save to local JSON, show leaderboard."""
        from game import leaderboard
        if name:
            leaderboard._native_submit(name, self._final_score)
        scores = leaderboard._native_fetch()
        self._show_leaderboard_native(scores, submitted=bool(name))

    async def _on_name_submitted(self):
        """Browser path triggered from _advance_past_stats. Fetches the
        current top 10, then branches on qualification: qualifiers go
        through name entry and land on the leaderboard so they can see
        where their name placed; non-qualifiers go straight back to
        the main menu instead of being parked on the leaderboard."""
        qualified = False
        try:
            from game import leaderboard
            scores = await leaderboard.fetch_top10()
            self._lb_fetch_error = leaderboard.last_fetch_error()
            if self._qualifies_for_top10(scores, self._final_score):
                qualified = True
                # Flip to NAMEENTRY so the Python-side render and the
                # JS overlay come up together — non-qualifiers must
                # never see a name-entry flash for the duration of
                # the fetch.
                self.state = STATE_NAMEENTRY
                name = await leaderboard.open_name_entry()
                if name:
                    await leaderboard.submit(name, self.world)
                    scores = await leaderboard.fetch_top10()
                    self._lb_fetch_error = leaderboard.last_fetch_error()
                    self._lb_player_rank = next(
                        (i for i, e in enumerate(scores) if e["score"] == self._final_score),
                        -1,
                    )
                else:
                    self._lb_player_rank = -1
            else:
                self._lb_player_rank = -1
            self._lb_scores = scores
        except Exception:
            pass
        self._fetch_pending = False
        self.hud.title_t = 0.0
        if qualified:
            self.state = STATE_LEADERBOARD
            self._cooldown_t = 0.25
        else:
            # Non-qualifying browser path: honour the player's stats
            # button choice. PLAY AGAIN bypasses the menu entirely.
            if self._post_leaderboard == "play":
                self._restart()
            else:
                self.state = STATE_MENU
            self._cooldown_t = 0.25

    # ── render ──────────────────────────────────────────────────────────────

    def _draw_background(self, surf):
        phase = self.world.biome_phase
        palette = self.world.biome_palette

        # The sky gradient is cached per phase bucket (see biome.PHASE_BUCKETS).
        # Blending the current bucket with the next one, weighted by how far
        # into the bucket we are, turns the otherwise ~10-second snap into a
        # continuous fade.
        buckets = _biome.PHASE_BUCKETS
        bucket_f = (phase % 1.0) * buckets
        a = int(bucket_f) % buckets
        b = (a + 1) % buckets
        t = bucket_f - int(bucket_f)

        pal_a = _biome.palette_for_phase(a / buckets)
        pal_b = _biome.palette_for_phase(b / buckets)
        sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
        sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)

        sky_a.set_alpha(None)
        surf.blit(sky_a, (0, 0))
        if t > 0:
            sky_b.set_alpha(int(t * 255))
            surf.blit(sky_b, (0, 0))
            sky_b.set_alpha(None)

        scroll = self.world.bg_scroll
        for i, (bx, by, sc, variant) in enumerate((
                (20, 90, 0.9, 0), (180, 140, 1.1, 2),
                (60, 220, 0.8, 3), (230, 60, 0.7, 1),
                (320, 180, 0.9, 4))):
            ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
            draw_cloud(surf, ox,
                       by + math.sin(self._cloud_phase * 0.3 + i) * 3,
                       sc, variant=variant)
        if self.world.kfc_timer > 0 and self.world.kfc_mountain_layers:
            # Pre-rendered fries pile per parallax layer - blit cheaply
            # at the offset since activation so the pile drifts at the
            # same depth-cued speeds as the normal mountains.
            from game.fries_mountains import blit_fries_mountains
            scroll_offset = scroll - self.world.kfc_activation_scroll
            blit_fries_mountains(surf, self.world.kfc_mountain_layers,
                                  scroll_offset)
        else:
            draw_mountains(surf, scroll, GROUND_Y, W,
                            palette['mtn_far'], palette['mtn_near'])
        # Ambient scenes (V-flocks, fireworks) sit between mountains and the
        # ground band so they read as "out there in the world" — behind
        # gameplay entities (pipes, coins, bird) but in front of terrain.
        self.world.ambient.draw(surf)
        draw_ground(surf, GROUND_Y, W, H, scroll,
                    palette['ground_top'], palette['ground_mid'], (60, 40, 25))

    def _render(self):
        # Intro renders its own self-contained scene (sky + pillars + cottage
        # + parrot etc.) and bypasses the in-game world draw entirely.
        if self.state == STATE_INTRO and self.intro is not None:
            self.intro.render(self.screen)
            return
        # Power-ups explainer also paints its own background — no world.
        if self.state == STATE_POWERUPS and self.powerup_help is not None:
            self.powerup_help.render(self.screen)
            return
        sx, sy = self.world.shake_offset() if self.state == STATE_PLAY else (0, 0)
        sx, sy = int(sx), int(sy)
        self._draw_background(self.screen)

        # Menu scene = the gameplay opener as a static frame: pickup post-
        # house on the left with Pip standing in front of it holding the
        # parcel. No pillars or world entities until the user taps to start.
        if self.state == STATE_MENU:
            house = _intro.get_sprite("skyhouse_post")
            hx = int(W * 0.30) - house.get_width() // 2
            hy = int(H * 0.42) - house.get_height() // 2
            self.screen.blit(house, (hx, hy))
            self.world.bird.draw(self.screen, sx, sy)
            self.hud.draw_menu(self.screen, 1 / 60, self.best)
            return

        pipe_palette = self.world.biome_palette
        kfc_active = self.world.bird.kfc_active
        for p in self.world.pipes:
            p.draw(self.screen, pipe_palette, kfc_visual=kfc_active)

        # Weather sits between pillars and collectibles so rain/fog passes
        # behind the coins + bird — same layer a real foreground has.
        self.world.weather.draw(self.screen)

        triple_active = self.world.triple_timer > 0
        for c in self.world.coins:
            c.draw(self.screen, kfc_active=kfc_active,
                   triple_active=triple_active)
        for m in self.world.powerups:
            m.draw(self.screen)

        # Gameplay opener: pickup post-house drifting off-screen-left + the
        # parcel tucked under Pip. Active only during STATE_PLAY's first
        # ~2.5 s, mirroring the intro's beat-2 closing image.
        if self.state == STATE_PLAY:
            _draw_opener(self.screen, self.world)

        # RAIL: track polyline + parked / locked cart go UNDER the bird
        # so Pip always reads on top.
        if getattr(self.world, "rail_pipes", None):
            _draw_rails(self.screen, self.world.rail_pipes)
        cart_pipe = getattr(self.world, "rail_cart_pipe", None)
        if cart_pipe is not None and not self.world.bird.cart_locked:
            _draw_parked_cart(self.screen, cart_pipe)
        if self.world.bird.cart_locked:
            _draw_cart_on_bird(self.screen, self.world, sx, sy)

        self.world.bird.draw(self.screen, sx, sy,
                             flipped=self.world.reverse_timer > 0)

        for p in self.world.particles:
            p.draw(self.screen)

        # Slow-mo: subtle violet tint overlay so the player feels the effect
        # even without looking at the HUD.
        if self.world.slowmo_timer > 0:
            tint = get_scratch_surface(W, H)
            tint.fill((140, 70, 210, 28))
            self.screen.blit(tint, (0, 0))

        # KFC mode: warm amber tint
        if self.world.kfc_timer > 0:
            tint = get_scratch_surface(W, H)
            tint.fill((210, 120, 10, 20))
            self.screen.blit(tint, (0, 0))

        # Ghost mode: cool blue-white screen tint. The ring around the bird
        # was removed — the SPECTRAL parrot palette + breathing-fade alpha
        # already carry the ghost read.
        if self.world.ghost_timer > 0:
            tint = get_scratch_surface(W, H)
            tint.fill((140, 180, 255, 18))
            self.screen.blit(tint, (0, 0))

        # LOTTERY reveal: top-left slot-machine cabinet shows the
        # roll for ~2.2 s. Drawn ON TOP of the world tints so the
        # tier label stays legible.
        if getattr(self.world, "lottery_anim", None) is not None:
            _draw_lottery_reveal(self.screen, self.world.lottery_anim)

        # Magnet force-field — Solar Gold palette: warm amber-gold rings
        # + golden glow + sci-fi hex-grid shield, with a coherent
        # dramatic breath. The rings + glow pulse; the hex grid is
        # static (cached at module load via `_magnet_hex_grid`) so we
        # blit the prebuilt overlay each frame instead of redrawing
        # ~225 polygons. Pulse rate 5.5 ⇒ ~1.14 s cycle.
        if self.world.magnet_timer > 0 or self.world.megamagnet_timer > 0:
            from game.config import MAGNET_RADIUS, MEGAMAGNET_RADIUS
            import math as _math
            t_pulse = self._cloud_phase * 5.5
            # Megamagnet renders the same field at 2x radius. The hex
            # grid cache builds a second entry for the larger size on
            # first activation; rings + glow scale by `rad` naturally.
            rad = (MEGAMAGNET_RADIUS if self.world.megamagnet_timer > 0
                   else MAGNET_RADIUS)
            field = pygame.Surface((rad * 2 + 8, rad * 2 + 8),
                                   pygame.SRCALPHA)
            lcx, lcy = rad + 4, rad + 4

            # Outer-ring pulse factor — drives BOTH the rings and the glow
            BREATH = 0.30
            s_outer = _math.sin(t_pulse + 0.0)
            u_outer = (s_outer + 1) / 2
            outer_factor = 1.0 - BREATH * (1.0 - u_outer)
            glow_rad = rad * outer_factor

            # Inner radial glow — bell-curve falloff peaking near the
            # outer edge, gold colour, scaled by the same pulse.
            GLOW_COL = (245, 175, 40)
            for i in range(18, 0, -1):
                r = int(glow_rad * i / 18)
                inner_t = i / 18
                bell = _math.exp(-((inner_t - 0.85) ** 2) / 0.15)
                a = int(72 * bell)
                if a > 0:
                    pygame.draw.circle(field, (*GLOW_COL, a),
                                       (lcx, lcy), r)

            # Hex-grid overlay — sits on top of the warm glow, under
            # the rings, so the rings remain the brightest read. The
            # cached grid is rendered at full radius once; each frame
            # we smoothscale it down to (rad * outer_factor) so the
            # hex breathes in lockstep with the outer ring instead of
            # sitting statically at full size while everything else
            # pulses. SRCALPHA is preserved through smoothscale.
            hex_full = _magnet_hex_grid(rad)
            scaled_d = int(rad * outer_factor) * 2 + 8
            full_d = int(rad) * 2 + 8
            if scaled_d != full_d:
                hex_layer = pygame.transform.smoothscale(
                    hex_full, (scaled_d, scaled_d))
                offset = (full_d - scaled_d) // 2
                field.blit(hex_layer, (offset, offset))
            else:
                field.blit(hex_full, (0, 0))

            # 3 rings with per-ring gold tints, slightly out of phase.
            AA_COL = (255, 240, 180)
            for rfac, phase, alpha, width, breath_scale, ring_col in (
                    (1.00, 0.0,  180, 3, 1.00, (255, 220, 100)),
                    (0.78, 0.6,  140, 2, 0.85, (255, 195,  60)),
                    (0.55, 1.2,  100, 2, 0.70, (235, 165,  35))):
                amp = BREATH * breath_scale
                s = _math.sin(t_pulse + phase)
                u = (s + 1) / 2
                rr = int(rad * rfac * (1.0 - amp * (1.0 - u)))
                # Anti-alias ring with two ⅓-alpha satellites + main pass
                pygame.draw.circle(field, (*AA_COL, alpha // 3),
                                   (lcx, lcy), rr + 1, width)
                pygame.draw.circle(field, (*AA_COL, alpha // 3),
                                   (lcx, lcy), rr - 1, width)
                pygame.draw.circle(field, (*ring_col, alpha),
                                   (lcx, lcy), rr, width)

            self.screen.blit(field,
                             (int(self.world.bird.x) + sx - lcx,
                              int(self.world.bird.y) + sy - lcy))

        if self.world.hit_flash > 0:
            t = self.world.hit_flash / 0.35
            overlay = get_scratch_surface(W, H)
            overlay.fill((*UI_RED, int(120 * t)))
            self.screen.blit(overlay, (0, 0))

        if self.state == STATE_MENU:
            self.hud.draw_menu(self.screen, 1 / 60, self.best)
        elif self.state == STATE_PLAY:
            self.hud.draw_play(self.screen, self.world, self.best)
        elif self.state == STATE_PAUSE:
            self.hud.draw_play(self.screen, self.world, self.best, paused=True)
            self.hud.draw_pause_overlay(self.screen, score=self.world.score)
        elif self.state == STATE_STATS:
            self.hud.draw_stats(self.screen, self.world, 1 / 60, self._stats_t,
                                best=self.best, new_best=self._new_best,
                                show_prompt=not self._fetch_pending)
        elif self.state == STATE_NAMEENTRY:
            import sys as _sys
            if _sys.platform != "emscripten":
                self.hud.draw_name_entry(self.screen, 1 / 60, self._name_input_buf)
        elif self.state == STATE_LEADERBOARD:
            self.hud.draw_leaderboard(
                self.screen, 1 / 60,
                self._lb_scores, self._lb_player_rank,
                self._cooldown_t,
                fetch_error=self._lb_fetch_error,
            )
        else:  # GAMEOVER
            self.hud.draw_gameover(
                self.screen, 1 / 60, self.world.score, self._new_best,
            )
