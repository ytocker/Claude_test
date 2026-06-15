"""Branch-only scripted prototype of the Pagoda-Warren beat:

    empty sky → a clown walks on with a floating dice power-up → the player
    grabs the die (rolls N = 10..25) → after a beat, a warren route of N fused
    pagodas scrolls in with N on a sign hung from the first pillar → the player
    flies the route → a couple of seconds later Pip falls to its death.

This is a feel-test harness, NOT shipped gameplay: there is no event trigger,
no gating, no DB write. It only runs when `App` decides to launch it (native,
this R&D branch). The clown, die, and route shapes are the already-approved
look-dev designs, reused verbatim by lazily importing the `tools/` renderers
the first time the demo is constructed — after the display exists, and never on
web (where `tools/` isn't even bundled). Every reuse point is wrapped so a
missing/renamed helper degrades to a plain fallback instead of crashing a run.
"""
import math
import random

import pygame

from game.config import W, GROUND_Y, BIRD_X, BIRD_R, PIPE_W
from game.entities import Pipe

# ── script timing (seconds) ──────────────────────────────────────────────────
T_CLOWN_IN = 3.0          # empty-sky flight before the clown arrives
T_SPIN = 0.9              # dice tumble before the rolled number is revealed
T_AFTER_PICKUP = 2.7      # beat between the reveal and the route
CELE_LIFE = 2.2           # result celebration banner life (< T_AFTER_PICKUP)
T_AFTER_ROUTE = 2.0       # free flight after the route before Pip drops

# ── warren geometry ──────────────────────────────────────────────────────────
SP = 72                   # fused centre-to-centre spacing (warren window 62-84)
SPAWN_X = W + 40          # where each route pillar enters from the right
ROUTE_SEED = 0            # one pagoda family for the whole route (stupa canopy)
ROUTE_GAP = 172           # per-pillar gap height (inside the 150-185 window)

# ── clown / die placement ────────────────────────────────────────────────────
DICE_DX = 144             # die sits up-LEFT of the clown, on the pointing-finger
DICE_Y = 347              # line (the chosen design's die position), still reachable
DICE_PICK_R = 30          # generous pickup radius around the die

# Local coords for the cached clown bitmap (its shape never changes — only its
# scroll position does — so it's rendered once and blitted each frame).
# Sized so nothing clips: the staff (total_px=225) rises well above the head and
# the cap horns spill sideways, so the bitmap is taller + wider than the bare body.
CLOWN_W, CLOWN_H = 240, 360
CLOWN_CX, CLOWN_FEET = 120, 250


class WarrenDemo:
    def __init__(self):
        # Lazy reuse of the look-dev kit. Constructed only when the demo runs,
        # so this import happens after the real display is up (the modules'
        # SDL_VIDEODRIVER=dummy setdefault is then a no-op) and never on web.
        from tools.render_jester_variants import (
            build_jester, _draw_die_face_noshadow, JESTERS,
        )
        from tools.render_warren_routes import Route
        from tools.render_warren_mockup import assert_passable

        self._build_jester = build_jester
        self._draw_die_face = _draw_die_face_noshadow
        self._Route = Route
        self._assert_passable = assert_passable
        # Hero clown #13 ("Plum & Lime — FINAL"); `no_shadow` is a render_cell
        # flag, not a build_jester kwarg, so drop it (we draw our own shadow).
        spec = dict(JESTERS[-1][1])
        spec.pop("no_shadow", None)
        self.spec = spec

        self.phase = "fly_in"
        self.t = 0.0               # global elapsed
        self.pt = 0.0              # current-phase timer
        self.pulse = 0.0           # die bob/sparkle clock
        self.input_locked = False

        self.clown_x = None        # world x of the clown's feet (None until in)
        self.dice_x = None
        self.dice_y = DICE_Y
        self.collected = False
        self.roll = None
        self.ghost_run = False     # GHOST outcome: phase through the whole route
        self.spin_t = 0.0          # dice tumble clock (phase "rolling")
        self._spin_face = 15       # number shown on the tumbling cube
        self._spin_face_t = 0.0    # countdown to the next tumble face
        self.die_pop_t = 0.0       # celebration-banner life after the reveal

        self.route = None          # list of (gap_cy, gap_h) for N pillars
        self.route_pipes = []      # Pipes we spawned, in order
        self.spawned = 0

        self._clown_surf = None    # cached clown bitmap (built on first draw)
        self._clown_ok = True      # cleared if build_jester ever throws
        self._cele_base = None     # cached true-size celebration popup (design E)
        self._cele_key = None      # (roll, ghost) the cached popup was built for

    # ── public hooks ─────────────────────────────────────────────────────────
    def gates_flap(self):
        """True once Pip's input is cut (the final scripted fall)."""
        return self.input_locked

    def update(self, world, dt):
        self.t += dt
        self.pt += dt
        self.pulse += dt * 3.5
        if self.die_pop_t > 0.0:
            self.die_pop_t = max(0.0, self.die_pop_t - dt)   # celebration life

        # The clown + die are world-anchored scenery in a static pose: once they
        # enter (a few seconds in) they ride the world scroll leftward and slide
        # off the left edge — they never walk or hold position on screen. The die
        # rides at the clown's hand until it's grabbed.
        if self.clown_x is not None:
            self.clown_x -= world._current_scroll() * dt
            if not self.collected:
                self.dice_x = self.clown_x - DICE_DX
            if self.clown_x < -160:
                self.clown_x = None

        if self.phase == "fly_in":
            if self.t >= T_CLOWN_IN:
                # Spawn far enough right that the DIE (which sits DICE_DX left of
                # the clown) starts off-screen at SPAWN_X and scrolls IN from the
                # edge — otherwise it pops in mid-screen while the clown is still
                # off the right. The die leads, the clown trails by DICE_DX.
                self.clown_x = float(SPAWN_X + DICE_DX)
                self.dice_x = self.clown_x - DICE_DX   # == SPAWN_X (off-screen right)
                self._goto("offer")

        elif self.phase == "offer":
            # grab on contact, or auto-grab once the die has scrolled past Pip
            if self._dice_hit(world) or self.dice_x < BIRD_X - 60:
                self._collect(world)
                self._goto("rolling")

        elif self.phase == "rolling":
            # the cube tumbles in place; the displayed face flickers, settling
            # onto the real roll for the last stretch, then the number reveals.
            self.spin_t += dt
            if self.spin_t >= T_SPIN - 0.18:
                self._spin_face = self.roll
            else:
                self._spin_face_t -= dt
                if self._spin_face_t <= 0.0:
                    self._spin_face = random.randint(10, 25)
                    self._spin_face_t = 0.06
            if self.spin_t >= T_SPIN:
                self._reveal_roll(world)
                self._goto("wait_route")

        elif self.phase == "wait_route":
            # the result celebration is up; the clown keeps scrolling off-screen
            if self.pt >= T_AFTER_PICKUP:
                self._make_route(world)
                if self.ghost_run:
                    world.ghost_timer = max(world.ghost_timer, 2.0)  # ghost on from route start
                self._goto("running")

        elif self.phase == "running":
            # feed pillars in from the right at the fused spacing
            while (self.spawned < len(self.route)
                   and (not self.route_pipes
                        or self.route_pipes[-1].x <= SPAWN_X - SP)):
                self._spawn_next(world)
            # GHOST roll: phase through the whole route. World decays ghost_timer
            # each frame, so keep it topped up while flying the route.
            if self.ghost_run:
                world.ghost_timer = max(world.ghost_timer, 2.0)
            # route done once the last pillar has slipped past Pip
            if (self.spawned >= len(self.route) and self.route_pipes
                    and self.route_pipes[-1].x + PIPE_W < BIRD_X):
                if self.ghost_run:
                    world.ghost_timer = 1.0   # ... then stay a ghost one more second
                self._goto("post_route")

        elif self.phase == "post_route":
            if self.pt >= T_AFTER_ROUTE:
                self.input_locked = True        # let gravity carry Pip down
                self._goto("falling")

        # "falling": nothing to drive — the normal ground collision ends the run.

    def draw_world(self, surf, world, sx, sy):
        """Clown + floating die — drawn BEFORE the pillars so the route occludes
        the strolling clown the way the celebration crowd is layered."""
        if self.clown_x is not None and self.clown_x > -140:
            cx = int(self.clown_x + sx)
            fy = int(GROUND_Y + sy)
            shadow = pygame.Surface((84, 14), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, 84, 14))
            surf.blit(shadow, (cx - 42, fy - 6))
            cs = self._clown_surface()
            if cs is not None:
                surf.blit(cs, (cx - CLOWN_CX, fy - CLOWN_FEET))
            else:
                pygame.draw.circle(surf, (150, 90, 200), (cx, fy - 80), 36)

        if self.dice_x is not None:
            dx = int(self.dice_x + sx)
            if not self.collected:                       # floating, pre-grab
                self._draw_floating_die(surf, dx, int(self.dice_y + sy))
            elif self.phase == "rolling":                # tumbling roll
                self._draw_spinning_die(surf, dx, int(self.dice_y + sy))
            # The settled result is NOT painted on the cube — it pops as a
            # celebration banner in a fixed spot (see _draw_celebration).

    def draw_sign(self, surf, world, sx, sy):
        """Hosts the result celebration banner — drawn AFTER the pillars so it
        layers in front of the route. (The old N-of-pillars plaque that hung
        from the first pagoda was removed; the banner already shows N.)"""
        self._draw_celebration(surf)               # fixed-spot popup; self-gated

    # ── internals ────────────────────────────────────────────────────────────
    def _clown_surface(self):
        """Render the clown once into a local bitmap (its shape is constant —
        only its scroll position changes) and reuse it each frame instead of
        re-running build_jester (which rotates a scratch surface) per frame."""
        if self._clown_surf is None and self._clown_ok:
            try:
                s = pygame.Surface((CLOWN_W, CLOWN_H), pygame.SRCALPHA)
                # The settled hero: build_jester body + a hand pointing up-left at
                # the floating die + the design-8 Carousel-Barker staff gripped in
                # the down hand (the chosen final look), composed by pillar_staff so
                # no tools/ import is needed.
                from game.pillar_staff import draw_chosen_hero
                draw_chosen_hero(s, CLOWN_CX, CLOWN_FEET,
                                 build_jester=self._build_jester, spec=self.spec)
                self._clown_surf = s
            except Exception:
                self._clown_ok = False
        return self._clown_surf

    def _draw_floating_die(self, surf, dx, dy):
        """The pre-grab die: a clean bobbing 3D cube with a few orbiting
        sparkles — NO glow/aura halo (it washed white on the pale sky)."""
        cy = int(dy + math.sin(self.pulse * 1.1) * 3)
        try:
            self._draw_die_face(surf, dx, cy, 40, pips=5)
        except Exception:
            pygame.draw.rect(surf, (250, 246, 230), (dx - 16, cy - 16, 32, 32))
            return
        for i in range(4):
            a = i * math.tau / 4 + self.pulse * 0.4
            rr = 30 + 4 * math.sin(self.pulse * 0.9 + i)
            sxp = int(dx + math.cos(a) * rr)
            syp = int(cy + math.sin(a) * rr * 0.85)
            tw = 0.5 + 0.5 * math.sin(self.pulse * 2.0 + i * 1.7)
            al = int(110 + 130 * tw)
            sz = 3 + int(2 * tw)
            spark = pygame.Surface((sz * 4, sz * 4), pygame.SRCALPHA)
            c = (255, 244, 200, al)
            pygame.draw.line(spark, c, (sz * 2, 0), (sz * 2, sz * 4), 1)
            pygame.draw.line(spark, c, (0, sz * 2), (sz * 4, sz * 2), 1)
            pygame.draw.circle(spark, (255, 255, 230, al), (sz * 2, sz * 2), sz)
            surf.blit(spark, (sxp - sz * 2, syp - sz * 2),
                      special_flags=pygame.BLEND_ADD)

    def _draw_celebration(self, surf):
        """The settled roll, popped as a celebration in a fixed on-screen spot
        (not painted on the cube): the chosen design "E" — a high-res jester
        prize-wheel with the rolled N as the hero, crowned by the staff's
        mini-clown bauble seated on the rim (see game.warren_celebration). A GHOST
        roll re-skins the wheel cyan/periwinkle. The static popup is rendered once
        per roll and pop-scaled each frame (ease-out-back over ~0.3s)."""
        if self.roll is None or self.die_pop_t <= 0.0:
            return
        age = max(0.0, CELE_LIFE - self.die_pop_t)        # secs since the reveal
        p = min(1.0, age / 0.30)
        s = 1.70158
        e = 1 + (s + 1) * (p - 1) ** 3 + s * (p - 1) ** 2
        scale = 0.35 + 0.65 * e

        key = (self.roll, self.ghost_run)
        if self._cele_base is None or self._cele_key != key:
            try:
                from game import warren_celebration
                canvas, dw, dh = warren_celebration.render(
                    self.roll, self.ghost_run, ss=4, b_hr_ss=24)
                self._cele_base = pygame.transform.smoothscale(canvas, (dw, dh))
                self._cele_key = key
            except Exception:
                self._cele_base = None
        if self._cele_base is None:
            return

        w = max(1, int(self._cele_base.get_width() * scale))
        h = max(1, int(self._cele_base.get_height() * scale))
        out = pygame.transform.smoothscale(self._cele_base, (w, h))
        # Centred a bit low so the bauble crown overlays the top-centre score
        # counter (this popup is drawn after the HUD, so it covers it).
        surf.blit(out, out.get_rect(center=(W // 2, 210)))

    def _draw_spinning_die(self, surf, dx, dy):
        """A short cube tumble before the reveal: the die spun by an ease-out
        angle (settling upright) with its face flickering through numbers, so
        it reads as a real dice roll. No glow/aura (kept off, per the clean look)."""
        u = min(1.0, self.spin_t / T_SPIN)
        try:
            sc = pygame.Surface((96, 96), pygame.SRCALPHA)
            self._draw_die_face(sc, 48, 48, 40, number=self._spin_face,
                                body=(255, 246, 224))
            deg = 360.0 * 3 * (1.0 - (1.0 - u) ** 2)   # 3 turns, decelerate to upright
            rot = pygame.transform.rotate(sc, deg)
            surf.blit(rot, (dx - rot.get_width() // 2, dy - rot.get_height() // 2))
        except Exception:
            pygame.draw.rect(surf, (250, 246, 230), (dx - 16, dy - 16, 32, 32))

    def _goto(self, phase):
        self.phase = phase
        self.pt = 0.0

    def _dice_hit(self, world):
        b = world.bird
        ddx = self.dice_x - b.x
        ddy = self.dice_y - b.y
        return ddx * ddx + ddy * ddy <= (DICE_PICK_R + BIRD_R) ** 2

    def _collect(self, world):
        # Grab → the cube tumbles (phase "rolling"); the number is revealed
        # only once the spin settles (see _reveal_roll). One extra slot in the
        # roll pool is GHOST: the die lands on the range minimum and Pip phases
        # through the whole route (applied in the "running" phase).
        self.collected = True
        pick = random.choice(list(range(10, 26)) + ["ghost"])
        self.ghost_run = pick == "ghost"
        self.roll = 10 if self.ghost_run else pick
        self.spin_t = 0.0
        self._spin_face = random.randint(10, 25)
        self._spin_face_t = 0.06

    def _reveal_roll(self, world):
        # Spin done — arm the celebration banner (drawn in a fixed spot, not on
        # the cube). die_pop_t is its life clock; _draw_celebration reads it.
        self.die_pop_t = CELE_LIFE

    def _spawn_next(self, world):
        gap_cy, gap_h = self.route[self.spawned]
        p = Pipe(float(SPAWN_X), gap_cy, gap_h)
        p.seed = ROUTE_SEED
        p.spawn_index = self.spawned + 1          # >=1: keep ornaments (no quiet rule)
        p.is_rush = False
        p.is_kfc = False
        p.is_staff = True
        world.pipes.append(p)
        self.route_pipes.append(p)
        self.spawned += 1

    def _make_route(self, world):
        """Build EXACTLY N (=roll) passable pagodas of a random difficulty-1-5
        archetype; on any passability failure fall back to a flat tube."""
        n = self.roll
        archetype = random.choice([
            self._r_plunge, self._r_ascent, self._r_rolling,
            self._r_valley, self._r_crest,
        ])
        try:
            route = archetype(n)
            self._assert_passable(route.name, route.pagodas)
        except Exception:
            route = self._Route("Flat Tube", "fallback")
            route.hold("flat", n, 300, ROUTE_GAP)
        self.route = [(cy, gap_h) for (_x, cy, gap_h, _seed) in route.pagodas]
        self.spawned = 0
        self.route_pipes = []

    def _pads(self, n):
        pad = 2 if n >= 8 else 1
        return pad, pad

    def _r_plunge(self, n):               # d2 — the long gentle dip
        r = self._Route("Long Plunge", "ride the fall")
        h, t = self._pads(n); m = n - h - t
        r.hold("in", h, 210, ROUTE_GAP).ramp("plunge", 410, m, ROUTE_GAP) \
            .hold("out", t, r.cy, ROUTE_GAP)
        return r

    def _r_ascent(self, n):               # d3 — steady climb
        r = self._Route("The Ascent", "steady climb")
        h, t = self._pads(n); m = n - h - t
        r.hold("in", h, 410, ROUTE_GAP).ramp("climb", 210, m, ROUTE_GAP) \
            .hold("out", t, r.cy, ROUTE_GAP)
        return r

    def _r_rolling(self, n):              # d3 — smooth sine
        r = self._Route("Rolling Hills", "smooth alternation")
        h, t = self._pads(n); m = n - h - t
        r.hold("in", h, 300, ROUTE_GAP).sine("roll", 62, 10, m, ROUTE_GAP, base=300) \
            .hold("out", t, r.cy, ROUTE_GAP)
        return r

    def _r_valley(self, n):               # d4 — fall then climb (V)
        # Endpoints kept within 50px/pagoda even when each leg is only 3 long
        # (N=10), so the V stays inside the drift budget at every length.
        r = self._Route("The Valley", "fall to climb")
        h, t = self._pads(n); m = n - h - t
        m1 = m // 2; m2 = m - m1
        r.hold("in", h, 255, ROUTE_GAP).ramp("fall", 405, m1, ROUTE_GAP) \
            .ramp("climb", 255, m2, ROUTE_GAP).hold("out", t, r.cy, ROUTE_GAP)
        return r

    def _r_crest(self, n):                # d4 — climb then fall (hill)
        r = self._Route("The Crest", "apex management")
        h, t = self._pads(n); m = n - h - t
        m1 = m // 2; m2 = m - m1
        r.hold("in", h, 405, ROUTE_GAP).ramp("climb", 255, m1, ROUTE_GAP) \
            .ramp("fall", 405, m2, ROUTE_GAP).hold("out", t, r.cy, ROUTE_GAP)
        return r
