"""Sparse ambient background scenes — distant flocks, distant fireworks,
hot-air balloons, parrot-family flybys, and cherry-blossom drift.

These are RARE punctuating events tied to biome phase. Each event has
a hard cooldown and a one-at-a-time cap so they enrich the world
without crowding the screen. The intent: a player gets one or two of
these per run, not a constant parade.
"""
from __future__ import annotations

import math
import random

import pygame

from game.config import W, H, GROUND_Y


# ── Phase windows & cooldowns (tuned for sparseness) ─────────────────────────
# Biome cycle is 5 minutes (CYCLE_SECONDS=300), 8 keyframes (DAY → GOLDEN →
# SUNSET → DUSK → NIGHT → PREDAWN → SUNRISE → DAY). We gate each event to
# its natural phase window and add a cooldown so even within the window the
# event fires at most once every minute or so.

_FLOCK_PHASES = ((0.10, 0.22), (0.85, 0.95))   # golden hour + sunrise
_FIREWORKS_PHASES = ((0.55, 0.72),)            # night
_BALLOON_PHASES = ((0.10, 0.22),)              # golden hour
_PARROTS_PHASES = ((0.96, 1.0), (0.0, 0.10))   # day (wraps around 0)
_BLOSSOMS_PHASES = ((0.85, 0.95),)             # sunrise
_CAMPFIRE_PHASES = ((0.55, 0.72),)             # night

_FLOCK_COOLDOWN_S = 75.0
_FIREWORKS_COOLDOWN_S = 110.0
_BALLOON_COOLDOWN_S = 90.0
_PARROTS_COOLDOWN_S = 80.0
_CAMPFIRE_COOLDOWN_S = 130.0

# Initial delay before the FIRST event of each kind in a run.
_FLOCK_INITIAL_DELAY = (15.0, 35.0)
_FIREWORKS_INITIAL_DELAY = (30.0, 60.0)
_BALLOON_INITIAL_DELAY = (20.0, 40.0)
_PARROTS_INITIAL_DELAY = (25.0, 50.0)
_CAMPFIRE_INITIAL_DELAY = (40.0, 80.0)


# ── V-formation flock ────────────────────────────────────────────────────────

class _VFlock:
    """A V-formation of seven distant birds drifting slowly across the sky.

    Color is derived from `palette['mtn_far']` so the flock sits at mid-far
    parallax depth alongside the back mountain layer — close enough to read,
    far enough to feel atmospheric.
    """
    SPEED = 18.0          # px/s, slow leftward drift
    DURATION_MAX = 35.0   # safety cap
    SPACING_X = 14
    SPACING_Y = 11

    __slots__ = ("color", "x", "y", "t", "_offsets")

    def __init__(self, palette: dict, screen_y: float):
        base = palette.get('mtn_far', (90, 90, 110))
        self.color = (max(0, base[0] - 60),
                      max(0, base[1] - 60),
                      max(0, base[2] - 60))
        self.x = float(W + 30)   # enter from off-screen right
        self.y = float(screen_y)
        self.t = 0.0
        sx, sy = self.SPACING_X, self.SPACING_Y
        self._offsets = (
            (0, 0),
            (-sx,  sy),    ( sx,  sy),
            (-2*sx, 2*sy), ( 2*sx, 2*sy),
            (-3*sx, 3*sy), ( 3*sx, 3*sy),
        )

    def update(self, dt: float) -> None:
        self.t += dt
        self.x -= self.SPEED * dt

    def is_done(self) -> bool:
        return self.x < -90 or self.t > self.DURATION_MAX

    def draw(self, surf: pygame.Surface) -> None:
        # Subtle wing flap: 2-frame toggle, slightly phase-shifted per bird.
        flap_t = self.t * 2.5
        for ox, oy in self._offsets:
            bx = int(self.x + ox)
            by = int(self.y + oy)
            if bx < -10 or bx > W + 10:
                continue
            phase = (flap_t + ox * 0.04) % 1.0
            tilt = -2 if phase < 0.5 else 0  # wings up on the upbeat
            pygame.draw.line(surf, self.color,
                             (bx - 6, by + 2 + tilt),
                             (bx, by - 2 + tilt), 2)
            pygame.draw.line(surf, self.color,
                             (bx + 6, by + 2 + tilt),
                             (bx, by - 2 + tilt), 2)


# ── Distant fireworks ────────────────────────────────────────────────────────

class _Fireworks:
    """Three sequential bursts low on the night horizon.

    Each burst expands and fades; bursts ignite ~1.6 s apart. Whole event
    runs ~5 seconds total. Drawn additively against the dark sky so the
    color punches through but the bursts stay distant-looking.
    """
    BURST_INTERVAL = 1.6   # seconds between burst ignitions
    BURST_LIFE = 1.6       # seconds for each burst to fade
    NUM_BURSTS = 3

    _PALETTE = (
        (255, 180,  90),
        (255, 120, 180),
        (180, 220, 255),
        (140, 255, 160),
    )

    def __init__(self, rng: random.Random | None = None):
        rnd = rng or random.Random()
        self.bursts: list[tuple[int, int, tuple[int, int, int], float]] = []
        # Spread the 3 bursts horizontally so they don't overlap.
        for i in range(self.NUM_BURSTS):
            slot_w = (W - 80) / self.NUM_BURSTS
            xmin = int(40 + i * slot_w)
            xmax = int(40 + (i + 1) * slot_w)
            cx = rnd.randint(xmin, max(xmin + 10, xmax))
            cy = GROUND_Y - rnd.randint(70, 130)
            color = rnd.choice(self._PALETTE)
            t_ignite = i * self.BURST_INTERVAL
            self.bursts.append((cx, cy, color, t_ignite))
        self.t = 0.0

    def update(self, dt: float) -> None:
        self.t += dt

    def is_done(self) -> bool:
        last_ignite = (self.NUM_BURSTS - 1) * self.BURST_INTERVAL
        return self.t > last_ignite + self.BURST_LIFE

    def draw(self, surf: pygame.Surface) -> None:
        layer: pygame.Surface | None = None
        for cx, cy, color, t_ignite in self.bursts:
            age = self.t - t_ignite
            if age < 0 or age > self.BURST_LIFE:
                continue
            if layer is None:
                layer = pygame.Surface((W, H), pygame.SRCALPHA)
            u = age / self.BURST_LIFE
            radius = int(8 + u * 16)
            alpha_mul = (1.0 - u) ** 1.4
            rays = 14
            for i in range(rays):
                ang = (i / rays) * math.tau
                ex = cx + math.cos(ang) * radius
                ey = cy + math.sin(ang) * radius
                for step, base_a in ((0.0, 235), (0.45, 160), (0.85, 60)):
                    px = cx + (ex - cx) * step
                    py = cy + (ey - cy) * step
                    a = int(base_a * alpha_mul)
                    if a > 4:
                        pygame.draw.circle(layer, (*color, a),
                                           (int(px), int(py)), 1)
            core_a = int(240 * alpha_mul)
            if core_a > 4:
                pygame.draw.circle(layer, (255, 255, 240, core_a), (cx, cy), 2)
                pygame.draw.circle(layer, (*color, int(90 * alpha_mul)),
                                   (cx, cy), 5)
        if layer is not None:
            surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


# ── Hot-air balloon (paneled, 07a1 rigging style) ───────────────────────────

_BALLOON_PALETTES = (
    # panel_a, panel_b, seam
    ((220,  60,  60), (250, 230, 200), ( 90,  50,  30)),  # red / cream
    (( 40, 140, 200), (240, 240, 240), ( 30,  70, 110)),  # blue / white
    ((245, 175,  80), ( 90,  60, 130), ( 90,  60,  25)),  # orange / purple
    (( 90, 170,  90), (240, 240, 200), ( 40,  80,  30)),  # green / cream
    ((220, 100, 180), (250, 220, 210), (110,  50,  90)),  # pink / blush
)


def _teardrop_polygon(cx: float, cy: float, w: float, h: float, n: int = 36):
    """Closed polygon: rounded top, gently pinched bottom mouth."""
    pts = []
    rx, ry = w / 2, h / 2
    for i in range(n):
        ang = -math.pi / 2 + (i / n) * math.tau
        x = math.cos(ang) * rx
        y = math.sin(ang) * ry
        if y > 0:
            pinch = 1.0 - 0.62 * (y / ry) ** 2
            x *= pinch
        pts.append((cx + x, cy + y))
    return pts


def _envelope_extent_at_y(cx: float, cy: float, w: float, h: float, y: float):
    rx, ry = w / 2, h / 2
    dy = y - cy
    if abs(dy) >= ry:
        return None
    x_ell = rx * math.sqrt(max(0.0, 1 - (dy / ry) ** 2))
    if dy > 0:
        x_ell *= 1.0 - 0.62 * (dy / ry) ** 2
    return cx - x_ell, cx + x_ell


_balloon_surface_cache: dict = {}


def _build_balloon_surface(scale_idx: int, palette_idx: int) -> tuple:
    """Render a paneled balloon (envelope + skirt + ropes + basket) onto a
    SRCALPHA surface and return (surface, env_cx, env_cy) in surface-local
    coordinates. Cached by (scale_idx, palette_idx)."""
    key = (scale_idx, palette_idx)
    cached = _balloon_surface_cache.get(key)
    if cached is not None:
        return cached

    scales = (0.85, 1.0, 1.15)
    scale = scales[scale_idx]
    base_w, base_h = 30, 38
    w = int(base_w * scale)
    h = int(base_h * scale)
    pa, pb, seam = _BALLOON_PALETTES[palette_idx]

    basket_w = max(10, int(w * 0.36))
    basket_h = max(6, int(h * 0.20))
    rope_gap = 5
    pad = 4
    surf_w = max(w, basket_w) + pad * 2
    surf_h = h + rope_gap + basket_h + pad + 2  # passenger head clearance
    surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)

    cx = surf_w // 2
    cy = pad + h // 2

    # Envelope — paneled multi-gore
    outline = _teardrop_polygon(cx, cy, w, h)
    pygame.draw.polygon(surf, pa, outline)
    n_panels = 8
    for i in range(n_panels):
        if i % 2 == 0:
            continue
        x0 = cx - w / 2 + i * (w / n_panels)
        x1 = cx - w / 2 + (i + 1) * (w / n_panels)
        for y_int in range(int(cy - h / 2), int(cy + h / 2) + 1):
            ext = _envelope_extent_at_y(cx, cy, w, h, y_int)
            if ext is None:
                continue
            lx, rx_ = ext
            dx0 = max(x0, lx)
            dx1 = min(x1, rx_)
            if dx1 > dx0:
                pygame.draw.line(surf, pb,
                                 (int(dx0), y_int), (int(dx1), y_int), 1)
    for i in range(1, n_panels):
        sx = cx - w / 2 + i * (w / n_panels)
        for y_int in range(int(cy - h / 2 + 2), int(cy + h / 2 - 1)):
            ext = _envelope_extent_at_y(cx, cy, w, h, y_int)
            if ext is None:
                continue
            lx, rx_ = ext
            if lx + 1 <= sx <= rx_ - 1:
                surf.set_at((int(sx), y_int), seam)
    ext = _envelope_extent_at_y(cx, cy, w, h, cy + 1)
    if ext is not None:
        lx, rx_ = ext
        pygame.draw.line(surf, seam, (int(lx + 1), int(cy + 1)),
                         (int(rx_ - 1), int(cy + 1)), 1)
    pygame.draw.polygon(surf, seam, outline, 1)
    # Highlight
    hi = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(hi, (255, 255, 255, 60),
                        (3, 3, max(5, w // 3), max(5, h // 3)))
    surf.blit(hi, (cx - w // 2, cy - h // 2))

    # Skirt band (2-px darker stripe)
    skirt_y = int(cy + h * 0.40)
    skirt_color = (max(0, seam[0] - 10), max(0, seam[1] - 10), max(0, seam[2] - 10))
    ext = _envelope_extent_at_y(cx, cy, w, h, skirt_y)
    if ext is not None:
        lx, rx_ = ext
        for off in range(-1, 3):
            pygame.draw.line(surf, skirt_color,
                             (int(lx) + 1, skirt_y + off),
                             (int(rx_) - 1, skirt_y + off), 1)

    # Ropes — 6 fanning ropes from skirt anchors to basket-top points
    env_bottom_y = int(cy + h / 2)
    basket_top_y = env_bottom_y + rope_gap
    bx0 = cx - basket_w // 2
    bx1 = cx + basket_w // 2
    rope = (40, 28, 18)
    for k in range(3):
        u = (k + 0.5) / 3
        anchor_y = cy + h * (0.05 + u * 0.35)
        ae = _envelope_extent_at_y(cx, cy, w, h, anchor_y)
        if ae is None:
            continue
        ae_l, ae_r = ae
        target_l = bx0 + (k * (basket_w - 1)) // 3
        target_r = bx1 - (k * (basket_w - 1)) // 3
        pygame.draw.line(surf, rope, (int(ae_l), int(anchor_y)),
                         (target_l, basket_top_y), 1)
        pygame.draw.line(surf, rope, (int(ae_r), int(anchor_y)),
                         (target_r, basket_top_y), 1)

    # Basket
    pygame.draw.rect(surf, (130, 85, 40),
                     (cx - basket_w // 2, basket_top_y, basket_w, basket_h))
    pygame.draw.rect(surf, (60, 40, 20),
                     (cx - basket_w // 2, basket_top_y, basket_w, basket_h), 1)
    for k in range(1, 3):
        ly = basket_top_y + basket_h * k // 3
        pygame.draw.line(surf, (90, 60, 30),
                         (cx - basket_w // 2 + 1, ly),
                         (cx + basket_w // 2 - 1, ly), 1)
    for vx in (cx - basket_w // 4, cx, cx + basket_w // 4):
        pygame.draw.line(surf, (95, 65, 32),
                         (vx, basket_top_y + 1),
                         (vx, basket_top_y + basket_h - 1), 1)
    # Passenger silhouette
    pygame.draw.circle(surf, (35, 25, 20), (cx, basket_top_y - 2), 2)

    _balloon_surface_cache[key] = (surf, cx, cy)
    return surf, cx, cy


class _PaneledBalloon:
    """One paneled hot-air balloon drifting calmly leftward across the sky.
    Pre-rendered to a cached surface; per-frame draw is a single blit.

    SPEED tuned so the balloon visibly traverses the screen in roughly
    20 s — 'calm' but not stationary. With W=360 and a ~50px balloon
    surface, total travel ≈ 410 px, so ~20 px/s gives ~20 s of screen
    time."""
    SPEED = 22.0
    DURATION_MAX = 28.0

    __slots__ = ("_surf", "_env_cx", "_env_cy", "x", "_y0",
                 "_bob_phase", "t")

    def __init__(self, rng: random.Random):
        scale_idx = rng.randint(0, 2)
        pal_idx = rng.randint(0, len(_BALLOON_PALETTES) - 1)
        self._surf, self._env_cx, self._env_cy = _build_balloon_surface(
            scale_idx, pal_idx)
        self.x = float(W + self._surf.get_width())
        self._y0 = rng.uniform(H * 0.22, H * 0.50)
        self._bob_phase = rng.uniform(0, math.tau)
        self.t = 0.0

    def update(self, dt: float) -> None:
        self.t += dt
        self.x -= self.SPEED * dt

    def is_done(self) -> bool:
        return self.x < -self._surf.get_width() - 5 or self.t > self.DURATION_MAX

    def draw(self, surf: pygame.Surface) -> None:
        # Center of balloon envelope at (self.x, self._y0 + bob)
        bob = math.sin(self.t * 0.55 + self._bob_phase) * 4
        env_x = int(self.x)
        env_y = int(self._y0 + bob)
        surf.blit(self._surf,
                  (env_x - self._env_cx, env_y - self._env_cy))


# ── Parrot family flyby ──────────────────────────────────────────────────────

_PARROT_BODY_PALETTE = (
    (235,  60,  55),
    (240, 180,  60),
    ( 90, 170, 235),
    ( 90, 200,  90),
    (235, 110, 200),
)


class _ParrotFamily:
    """Five small colorful parrots in a loose diagonal formation drifting
    leftward across the sky during day phase."""
    SPEED = 22.0
    DURATION_MAX = 28.0
    N_PARROTS = 5

    __slots__ = ("x", "_y_top", "t", "_colors", "_offsets")

    def __init__(self, rng: random.Random):
        # Loose diagonal: each parrot is offset (-spacing_x, +spacing_y)
        # from the previous, creating a left-sloping line.
        sx, sy = 18, 8
        self._offsets = tuple(
            (i * sx, i * sy) for i in range(self.N_PARROTS)
        )
        colors = list(_PARROT_BODY_PALETTE)
        rng.shuffle(colors)
        self._colors = tuple(colors)
        # Enter from off-screen right; pick altitude that keeps the entire
        # diagonal in the upper half of the sky.
        formation_h = sy * (self.N_PARROTS - 1)
        self._y_top = rng.uniform(H * 0.20, H * 0.45 - formation_h)
        # Position the leader off-screen right
        self.x = float(W + 30)
        self.t = 0.0

    def update(self, dt: float) -> None:
        self.t += dt
        self.x -= self.SPEED * dt

    def is_done(self) -> bool:
        # Trailing parrot is the last in offsets list, at +sx*4 from leader.
        last_x = self.x + self._offsets[-1][0]
        return last_x < -25 or self.t > self.DURATION_MAX

    def draw(self, surf: pygame.Surface) -> None:
        # Wing flap toggle every 0.25 s
        flap_up = (int(self.t * 4) % 2) == 0
        for (ox, oy), color in zip(self._offsets, self._colors):
            px = int(self.x + ox)
            py = int(self._y_top + oy)
            if px < -10 or px > W + 10:
                continue
            # Body
            pygame.draw.ellipse(surf, color, (px - 5, py - 3, 10, 6))
            # Wings (animated up/flat)
            wing_dark = (max(0, color[0] - 90),
                         max(0, color[1] - 90),
                         max(0, color[2] - 90))
            wing_y = py - 6 if flap_up else py - 4
            pygame.draw.line(surf, wing_dark,
                             (px - 4, py - 3), (px - 6, wing_y), 2)
            pygame.draw.line(surf, wing_dark,
                             (px + 4, py - 3), (px + 6, wing_y), 2)
            # Beak (pointing left — direction of travel)
            pygame.draw.polygon(surf, (240, 200, 80), [
                (px - 5, py - 1), (px - 8, py), (px - 5, py + 1),
            ])
            # Eye
            pygame.draw.circle(surf, (20, 15, 20), (px - 2, py - 1), 1)


# ── Cherry-blossom drift ────────────────────────────────────────────────────

_PETAL_COLORS = (
    (255, 195, 215),
    (250, 175, 200),
    (245, 210, 225),
    (255, 220, 230),
)


class _Petal:
    __slots__ = ("x", "y", "vx", "vy", "spin", "phase", "color", "size")

    def __init__(self, x, y, vx, vy, color, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.spin = random.uniform(0, math.tau)
        self.phase = random.uniform(0, math.tau)
        self.color = color
        self.size = size

    def update(self, dt: float) -> None:
        self.phase += dt * 2.5
        self.spin += dt * 1.6
        self.x += (self.vx + math.sin(self.phase) * 14) * dt
        self.y += self.vy * dt

    def off_screen(self) -> bool:
        return self.x < -10 or self.x > W + 10 or self.y > GROUND_Y

    def draw(self, surf: pygame.Surface) -> None:
        # Tilted ellipse: width modulates with cos(spin), so the petal
        # appears to flutter as it falls.
        sx = math.cos(self.spin)
        rx = max(1, int(abs(sx) * self.size))
        ry = self.size
        pygame.draw.ellipse(surf, self.color,
                            (int(self.x) - rx, int(self.y) - ry,
                             rx * 2, ry * 2))


def _blossom_intensity(phase: float) -> float:
    """Smoothstep ramp through the sunrise window."""
    lo, hi = _BLOSSOMS_PHASES[0]
    if phase < lo or phase > hi:
        return 0.0
    t = (phase - lo) / (hi - lo)
    # Bell curve: peak in the middle of the window, fade at edges.
    bell = 1.0 - abs(t * 2 - 1)  # 0 at edges, 1 at center
    return max(0.0, min(1.0, bell))


class _CherryBlossomDrift:
    """A continuous-but-bounded particle stream of pink petals across the
    sky, gated by the sunrise phase window. Spawns gradually, drifts off
    naturally as petals leave the screen."""
    MAX_PETALS = 26

    __slots__ = ("petals",)

    def __init__(self):
        self.petals: list[_Petal] = []

    def update(self, dt: float, phase: float) -> None:
        intensity = _blossom_intensity(phase)
        target = int(intensity * self.MAX_PETALS)
        # Top up the pool gradually
        while len(self.petals) < target:
            self._spawn(intensity)
        # Tick all petals
        for p in self.petals:
            p.update(dt)
        self.petals = [p for p in self.petals if not p.off_screen()]

    def _spawn(self, intensity: float) -> None:
        # Petals enter from the right or top edge, drifting left + down.
        side = random.random()
        if side < 0.7:
            x = W + random.uniform(0, 40)
            y = random.uniform(20, GROUND_Y - 80)
        else:
            x = random.uniform(0, W)
            y = -random.uniform(0, 40)
        vx = -random.uniform(28, 60)
        vy = random.uniform(20, 50)
        color = random.choice(_PETAL_COLORS)
        size = random.choice((2, 2, 3, 3, 4))
        self.petals.append(_Petal(x, y, vx, vy, color, size))

    def is_done(self) -> bool:
        # Drift is "active" as long as petals exist on screen; the controller
        # treats it as a phase-gated continuous effect.
        return False

    def draw(self, surf: pygame.Surface) -> None:
        for p in self.petals:
            p.draw(surf)


# ── Campfire ────────────────────────────────────────────────────────────────

_CAMPFIRE_HALO_RADIUS = 30
_CAMPFIRE_HALO_PEAK = (160, 80, 32)

# Local layout inside the cached static surface.
_CAMP_SURF_W, _CAMP_SURF_H = 100, 70
_CAMP_FIRE_LX, _CAMP_FIRE_LY = 40, 40

# Module-level halo cache — built once, reused by every campfire instance.
_campfire_halo_cache: pygame.Surface | None = None


def _build_campfire_halo() -> pygame.Surface:
    """Per-pixel radial gradient halo (smooth, no concentric-ring artefacts).
    Scaled so additive blits give a warm firelight bleed without saturation."""
    global _campfire_halo_cache
    if _campfire_halo_cache is not None:
        return _campfire_halo_cache
    r = _CAMPFIRE_HALO_RADIUS
    size = r * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    peak = _CAMPFIRE_HALO_PEAK
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - cx, y - cy)
            if d > r:
                continue
            u = d / r
            intensity = (1.0 - u) ** 2.4
            rr = int(peak[0] * intensity)
            gg = int(peak[1] * intensity)
            bb = int(peak[2] * intensity)
            if rr + gg + bb > 0:
                surf.set_at((x, y), (rr, gg, bb, 255))
    _campfire_halo_cache = surf
    return surf


def _build_campfire_solid() -> pygame.Surface:
    """Tent + logs baked once, reused by every instance. The fire and
    sparks animate on top each frame, so they're not in here."""
    surf = pygame.Surface((_CAMP_SURF_W, _CAMP_SURF_H), pygame.SRCALPHA)
    fcx, fcy = _CAMP_FIRE_LX, _CAMP_FIRE_LY
    tent_silh = (165, 90, 65)
    tent_dark = (90, 50, 35)
    tent_cx = fcx + 28
    tent_h = 22
    tent_half_w = 14
    pygame.draw.polygon(surf, tent_silh, [
        (tent_cx - tent_half_w, fcy),
        (tent_cx + tent_half_w, fcy),
        (tent_cx,               fcy - tent_h),
    ])
    # Tent door
    pygame.draw.polygon(surf, tent_dark, [
        (tent_cx - 4, fcy),
        (tent_cx + 4, fcy),
        (tent_cx,     fcy - 12),
    ])
    # Center seam
    pygame.draw.line(surf, tent_dark,
                     (tent_cx, fcy - tent_h),
                     (tent_cx, fcy - 12), 1)
    # Side seams
    pygame.draw.line(surf, tent_dark,
                     (tent_cx - tent_half_w + 1, fcy - 1),
                     (tent_cx, fcy - tent_h + 1), 1)
    pygame.draw.line(surf, tent_dark,
                     (tent_cx + tent_half_w - 1, fcy - 1),
                     (tent_cx, fcy - tent_h + 1), 1)
    # Logs at the fire base
    pygame.draw.line(surf, (40, 25, 15),
                     (fcx - 5, fcy - 1), (fcx + 5, fcy - 1), 2)
    pygame.draw.line(surf, (45, 28, 16),
                     (fcx - 4, fcy - 2), (fcx + 4, fcy - 2), 1)
    return surf


_campfire_solid_cache: pygame.Surface | None = None


def _get_campfire_solid() -> pygame.Surface:
    global _campfire_solid_cache
    if _campfire_solid_cache is None:
        _campfire_solid_cache = _build_campfire_solid()
    return _campfire_solid_cache


_SPARK_COLORS = (
    (255, 220, 130),
    (255, 180,  90),
    (255, 240, 200),
)


class _Campfire:
    """Night-time campsite (tent + flickering fire + sparks + warm halo).

    Anchored to the world rather than drifting on its own — the campfire
    is a piece of scenery the bird passes by. It scrolls at 0.7× the
    background scroll rate, matching the foreground grass-blade texture
    (see `draw_ground` in game/draw.py), so it visually sits on the same
    plane as the ground."""
    SCROLL_MULT = 0.7
    DURATION_MAX = 60.0
    SPARK_INTERVAL = 0.10
    SPARK_CAP = 14

    __slots__ = ("x", "y", "t", "_sparks", "_spark_t",
                 "_flicker_seed", "_prev_bg")

    def __init__(self, rng: random.Random):
        self.x = float(W + 20)
        self.y = float(GROUND_Y - 24)
        self.t = 0.0
        self._sparks: list = []
        self._spark_t = 0.0
        self._flicker_seed = rng.uniform(0, math.tau)
        self._prev_bg: float | None = None
        # Warm up caches the first time a campfire spawns
        _build_campfire_halo()
        _get_campfire_solid()

    def update(self, dt: float, bg_scroll: float) -> None:
        # World-anchored motion: x decreases by the change in bg_scroll
        # since the previous tick (scaled by parallax multiplier).
        if self._prev_bg is not None:
            self.x -= (bg_scroll - self._prev_bg) * self.SCROLL_MULT
        self._prev_bg = bg_scroll

        self.t += dt
        # Spark physics
        new = []
        for s in self._sparks:
            s[0] += s[2] * dt
            s[1] += s[3] * dt
            s[4] -= dt
            if s[4] > 0:
                new.append(s)
        self._sparks = new
        # Spark spawn — bounded interval AND population cap
        self._spark_t += dt
        while (self._spark_t > self.SPARK_INTERVAL and
               len(self._sparks) < self.SPARK_CAP):
            self._spark_t -= self.SPARK_INTERVAL
            self._sparks.append([
                random.uniform(-4, 4),       # rel x
                -2.0,                         # rel y (just above logs)
                random.uniform(-8, 8),       # vx
                random.uniform(-50, -28),    # vy (rising)
                random.uniform(0.7, 1.3),    # life
                random.choice(_SPARK_COLORS),
            ])

    def is_done(self) -> bool:
        return self.x < -60 or self.t > self.DURATION_MAX

    def draw(self, surf: pygame.Surface) -> None:
        x = int(self.x)
        y = int(self.y)
        # Halo (additive) — centred a few pixels above the fire base
        halo = _build_campfire_halo()
        hr = _CAMPFIRE_HALO_RADIUS
        surf.blit(halo, (x - hr, y - 4 - hr),
                  special_flags=pygame.BLEND_RGB_ADD)
        # Solid (tent + logs) blitted with normal alpha
        solid = _get_campfire_solid()
        surf.blit(solid, (x - _CAMP_FIRE_LX, y - _CAMP_FIRE_LY))
        # Flame — flicker via two summed sines so it doesn't look periodic
        flicker = (math.sin(self.t * 12.0 + self._flicker_seed) * 0.5 +
                   math.sin(self.t * 7.5 + self._flicker_seed * 2) * 0.5)
        h_off = int(round(flicker * 1.5))   # -1..+1 px height jitter
        flame = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.ellipse(flame, (255,  90,  50, 200),
                            (x - 5, y - 7 - h_off, 10, 8 + h_off))
        pygame.draw.ellipse(flame, (255, 150,  60, 230),
                            (x - 4, y - 8 - h_off, 8, 8 + h_off))
        pygame.draw.ellipse(flame, (255, 210, 110, 240),
                            (x - 2, y - 8 - h_off, 5, 7 + h_off))
        pygame.draw.ellipse(flame, (255, 240, 180, 250),
                            (x - 1, y - 6 - h_off, 3, 4 + h_off))
        pygame.draw.ellipse(flame, (255, 200, 100, 200),
                            (x - 1, y - 11 - h_off, 3, 5))
        surf.blit(flame, (0, 0))
        pygame.draw.circle(surf, (255, 250, 220), (x, y - 5), 1)
        # Sparks (additive)
        spark_layer = pygame.Surface((W, H), pygame.SRCALPHA)
        for sx, sy, _, _, life, color in self._sparks:
            life_u = max(0.0, min(1.0, life / 1.3))
            a = int(220 * life_u)
            if a > 4:
                pygame.draw.circle(spark_layer, (*color, a),
                                   (x + int(sx), y + int(sy)), 1)
        surf.blit(spark_layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


# ── Controller ───────────────────────────────────────────────────────────────

class AmbientScenes:
    """Sparse ambient event director.

    Five event types, each with its own phase window and cooldown. Hard
    cap of one of each kind active at any time. Outside its window, an
    event's cooldown counter pauses (no spawning until phase re-enters).
    """

    def __init__(self):
        self.flock: _VFlock | None = None
        self.fireworks: _Fireworks | None = None
        self.balloon: _PaneledBalloon | None = None
        self.parrots: _ParrotFamily | None = None
        self.campfire: _Campfire | None = None
        self.blossoms: _CherryBlossomDrift = _CherryBlossomDrift()  # always live, gated
        self._flock_cool = random.uniform(*_FLOCK_INITIAL_DELAY)
        self._fireworks_cool = random.uniform(*_FIREWORKS_INITIAL_DELAY)
        self._balloon_cool = random.uniform(*_BALLOON_INITIAL_DELAY)
        self._parrots_cool = random.uniform(*_PARROTS_INITIAL_DELAY)
        self._campfire_cool = random.uniform(*_CAMPFIRE_INITIAL_DELAY)

    @staticmethod
    def _in_window(phase: float, windows) -> bool:
        return any(lo <= phase <= hi for lo, hi in windows)

    def update(self, dt: float, phase: float, palette: dict,
               bg_scroll: float) -> None:
        # ── V-flock ──
        if self.flock is not None:
            self.flock.update(dt)
            if self.flock.is_done():
                self.flock = None
        elif self._in_window(phase, _FLOCK_PHASES):
            self._flock_cool -= dt
            if self._flock_cool <= 0:
                y = random.uniform(H * 0.18, H * 0.40)
                self.flock = _VFlock(palette, y)
                self._flock_cool = _FLOCK_COOLDOWN_S + random.uniform(-15, 30)

        # ── Fireworks ──
        if self.fireworks is not None:
            self.fireworks.update(dt)
            if self.fireworks.is_done():
                self.fireworks = None
        elif self._in_window(phase, _FIREWORKS_PHASES):
            self._fireworks_cool -= dt
            if self._fireworks_cool <= 0:
                self.fireworks = _Fireworks()
                self._fireworks_cool = _FIREWORKS_COOLDOWN_S + random.uniform(-20, 40)

        # ── Hot-air balloon ──
        if self.balloon is not None:
            self.balloon.update(dt)
            if self.balloon.is_done():
                self.balloon = None
        elif self._in_window(phase, _BALLOON_PHASES):
            self._balloon_cool -= dt
            if self._balloon_cool <= 0:
                self.balloon = _PaneledBalloon(random.Random())
                self._balloon_cool = _BALLOON_COOLDOWN_S + random.uniform(-20, 40)

        # ── Parrot family ──
        if self.parrots is not None:
            self.parrots.update(dt)
            if self.parrots.is_done():
                self.parrots = None
        elif self._in_window(phase, _PARROTS_PHASES):
            self._parrots_cool -= dt
            if self._parrots_cool <= 0:
                self.parrots = _ParrotFamily(random.Random())
                self._parrots_cool = _PARROTS_COOLDOWN_S + random.uniform(-20, 40)

        # ── Campfire ──
        if self.campfire is not None:
            self.campfire.update(dt, bg_scroll)
            if self.campfire.is_done():
                self.campfire = None
        elif self._in_window(phase, _CAMPFIRE_PHASES):
            self._campfire_cool -= dt
            if self._campfire_cool <= 0:
                self.campfire = _Campfire(random.Random())
                self._campfire_cool = _CAMPFIRE_COOLDOWN_S + random.uniform(-25, 50)

        # ── Cherry blossoms (continuous, phase-gated) ──
        self.blossoms.update(dt, phase)

    def draw(self, surf: pygame.Surface) -> None:
        if self.flock is not None:
            self.flock.draw(surf)
        if self.fireworks is not None:
            self.fireworks.draw(surf)
        if self.balloon is not None:
            self.balloon.draw(surf)
        if self.parrots is not None:
            self.parrots.draw(surf)
        if self.campfire is not None:
            self.campfire.draw(surf)
        self.blossoms.draw(surf)
