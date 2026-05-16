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
_SHEEP_PHASES = ((0.96, 1.0), (0.0, 0.15))     # day
_RABBITS_PHASES = ((0.85, 0.95), (0.96, 1.0), (0.0, 0.10))  # sunrise + early day
_FOX_PHASES = ((0.30, 0.40), (0.45, 0.55))     # sunset + dusk
_BEEHIVE_PHASES = ((0.0, 0.20),)               # day
_WELL_PHASES = ((0.0, 0.45), (0.78, 1.0))      # any non-night
_SCARECROW_PHASES = ((0.10, 0.22),)            # golden hour
_PICNIC_PHASES = ((0.96, 1.0), (0.0, 0.20))    # day
_MUSHRING_PHASES = ((0.55, 0.72), (0.78, 0.88))  # night + predawn
_CHEST_PHASES = ((0.0, 1.0),)                  # any (rare cooldown)
_WISP_PHASES = ((0.55, 0.72), (0.78, 0.88))    # night + predawn
_BENCH_PHASES = ((0.10, 0.22), (0.0, 0.10), (0.96, 1.0))  # golden hour + day
_NAPPER_PHASES = ((0.0, 0.20), (0.30, 0.40))   # day + sunset
_DOG_PHASES = ((0.0, 0.45),)                   # day → sunset

_FLOCK_COOLDOWN_S = 75.0
_FIREWORKS_COOLDOWN_S = 110.0
_BALLOON_COOLDOWN_S = 90.0
_PARROTS_COOLDOWN_S = 80.0
_CAMPFIRE_COOLDOWN_S = 130.0
_SHEEP_COOLDOWN_S = 100.0
_RABBITS_COOLDOWN_S = 110.0
_FOX_COOLDOWN_S = 140.0
_BEEHIVE_COOLDOWN_S = 120.0
_WELL_COOLDOWN_S = 130.0
_SCARECROW_COOLDOWN_S = 120.0
_PICNIC_COOLDOWN_S = 140.0
_MUSHRING_COOLDOWN_S = 150.0
_CHEST_COOLDOWN_S = 200.0   # rare
_WISP_COOLDOWN_S = 100.0
_BENCH_COOLDOWN_S = 120.0
_NAPPER_COOLDOWN_S = 140.0
_DOG_COOLDOWN_S = 100.0

# Initial delay before the FIRST event of each kind in a run.
_FLOCK_INITIAL_DELAY = (15.0, 35.0)
_FIREWORKS_INITIAL_DELAY = (30.0, 60.0)
_BALLOON_INITIAL_DELAY = (20.0, 40.0)
_PARROTS_INITIAL_DELAY = (25.0, 50.0)
_CAMPFIRE_INITIAL_DELAY = (40.0, 80.0)
_SHEEP_INITIAL_DELAY = (20.0, 40.0)
_RABBITS_INITIAL_DELAY = (30.0, 55.0)
_FOX_INITIAL_DELAY = (40.0, 70.0)
_BEEHIVE_INITIAL_DELAY = (35.0, 60.0)
_WELL_INITIAL_DELAY = (40.0, 70.0)
_SCARECROW_INITIAL_DELAY = (35.0, 60.0)
_PICNIC_INITIAL_DELAY = (50.0, 80.0)
_MUSHRING_INITIAL_DELAY = (45.0, 75.0)
_CHEST_INITIAL_DELAY = (80.0, 140.0)
_WISP_INITIAL_DELAY = (30.0, 60.0)
_BENCH_INITIAL_DELAY = (30.0, 55.0)
_NAPPER_INITIAL_DELAY = (45.0, 75.0)
_DOG_INITIAL_DELAY = (25.0, 50.0)


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


# ── Ground events (drift-by scenery) ─────────────────────────────────────────
#
# Each event mirrors the world-anchored pattern of ``_Campfire`` — scrolls
# left at 0.7× ``bg_scroll`` so it sits on the same plane as the ground
# decoration. Each event builds a small cached sprite in ``__init__`` and
# layers per-frame animation (bobs, particles, glows) on top in ``draw()``.


class _GroundEventBase:
    """Shared scrolling + lifetime for world-anchored ground events."""
    SCROLL_MULT = 0.7
    DURATION_MAX = 60.0
    DESPAWN_MARGIN = 80

    def __init__(self, palette: dict, rng: random.Random | None = None):
        self.x = float(W + 60)
        self.t = 0.0
        self._prev_bg: float | None = None
        self.palette = palette
        self.rng = rng or random.Random()
        self._sprite: pygame.Surface | None = None  # subclass fills if used

    def update(self, dt: float, bg_scroll: float) -> None:
        if self._prev_bg is not None:
            self.x -= (bg_scroll - self._prev_bg) * self.SCROLL_MULT
        self._prev_bg = bg_scroll
        self.t += dt

    def is_done(self) -> bool:
        return self.x < -self.DESPAWN_MARGIN or self.t > self.DURATION_MAX

    def _blit_sprite(self, surf: pygame.Surface, y_off: int = 0) -> None:
        """Blit the cached sprite anchored so its bottom sits on GROUND_Y."""
        if self._sprite is None:
            return
        sw, sh = self._sprite.get_size()
        surf.blit(self._sprite, (int(self.x) - sw // 2,
                                 GROUND_Y - sh + 1 + y_off))


# ── G1: Grazing sheep ────────────────────────────────────────────────────────

def _build_sheep_sprite() -> pygame.Surface:
    s = pygame.Surface((34, 22), pygame.SRCALPHA)
    # Fluffy body
    pygame.draw.ellipse(s, (240, 240, 235), (3, 6, 26, 12))
    pygame.draw.ellipse(s, (215, 215, 210), (3, 6, 26, 12), 1)
    # Wool bumps on top
    for cx in (8, 13, 18, 23):
        pygame.draw.circle(s, (250, 250, 245), (cx, 6), 2)
    # Head (dark muzzle)
    pygame.draw.ellipse(s, (60, 50, 45), (25, 9, 8, 8))
    pygame.draw.ellipse(s, (90, 75, 65), (25, 9, 8, 5))
    # Ear
    pygame.draw.polygon(s, (50, 40, 35), [(26, 9), (28, 9), (27, 6)])
    # Eye
    pygame.draw.circle(s, (240, 240, 235), (30, 12), 1)
    # Legs
    for lx in (8, 13, 19, 24):
        pygame.draw.line(s, (50, 40, 35), (lx, 17), (lx, 21), 1)
    return s


class _Sheep(_GroundEventBase):
    def __init__(self, palette, rng=None):
        super().__init__(palette, rng)
        self._sprite = _build_sheep_sprite()
        self._look_up_phase = self.rng.uniform(0, math.tau)

    def draw(self, surf):
        bob = int(math.sin(self.t * 1.3 + self._look_up_phase) * 0.7)
        self._blit_sprite(surf, y_off=-bob)


# ── G2: Rabbit hop trio ──────────────────────────────────────────────────────

def _build_rabbit_sprite(body: tuple) -> pygame.Surface:
    s = pygame.Surface((14, 14), pygame.SRCALPHA)
    dark = (max(0, body[0] - 35), max(0, body[1] - 35), max(0, body[2] - 35))
    # Body
    pygame.draw.ellipse(s, body, (1, 7, 11, 6))
    pygame.draw.ellipse(s, dark, (1, 7, 11, 6), 1)
    # Head
    pygame.draw.ellipse(s, body, (7, 4, 6, 6))
    # Tall ears
    pygame.draw.line(s, body, (9, 4), (9, 0), 2)
    pygame.draw.line(s, body, (12, 4), (12, 1), 2)
    pygame.draw.line(s, dark, (9, 4), (9, 1), 1)
    # Eye
    pygame.draw.circle(s, (20, 15, 15), (11, 6), 1)
    # White tail puff
    pygame.draw.circle(s, (250, 245, 240), (2, 9), 2)
    return s


class _RabbitHop(_GroundEventBase):
    def __init__(self, palette, rng=None):
        super().__init__(palette, rng)
        colors = [(150, 120, 95), (110, 90, 70), (180, 150, 120)]
        self._sprites = [_build_rabbit_sprite(c) for c in colors]
        # 3 rabbits in a loose diagonal, each with its own hop phase
        self._offsets = [(-18, 0, 0.0), (0, 4, 0.5), (16, 1, 1.0)]

    def draw(self, surf):
        for (dx, dy, phase), sprite in zip(self._offsets, self._sprites):
            sw, sh = sprite.get_size()
            hop = math.sin(self.t * 5.5 + phase)
            hop_y = -max(0, hop) * 5  # only the up-swing lifts the rabbit
            x = int(self.x) + dx - sw // 2
            y = GROUND_Y - sh + 1 + dy + int(hop_y)
            surf.blit(sprite, (x, y))


# ── G3: Sleeping fox ─────────────────────────────────────────────────────────

def _build_fox_sprite() -> pygame.Surface:
    s = pygame.Surface((32, 16), pygame.SRCALPHA)
    rust = (205, 100, 55)
    rust_dk = (160, 75, 40)
    # Curled body
    pygame.draw.ellipse(s, rust_dk, (3, 5, 24, 10))
    pygame.draw.ellipse(s, rust, (3, 5, 24, 9))
    # Belly (lighter)
    pygame.draw.ellipse(s, (240, 220, 200), (7, 9, 16, 5))
    # Tail wrap around back
    pygame.draw.ellipse(s, rust, (22, 6, 9, 6))
    pygame.draw.ellipse(s, rust_dk, (22, 6, 9, 6), 1)
    # White tail tip
    pygame.draw.circle(s, (250, 245, 240), (29, 9), 2)
    # Head tucked forward-left
    pygame.draw.ellipse(s, rust, (3, 3, 9, 7))
    pygame.draw.ellipse(s, rust_dk, (3, 3, 9, 7), 1)
    # Ears
    pygame.draw.polygon(s, rust_dk, [(4, 3), (7, 3), (5, 0)])
    pygame.draw.polygon(s, rust_dk, [(8, 3), (11, 3), (10, 0)])
    pygame.draw.polygon(s, (40, 25, 20), [(5, 1), (7, 3), (6, 2)])
    # Closed eye
    pygame.draw.line(s, (40, 25, 20), (5, 6), (8, 6), 1)
    # Snout
    pygame.draw.circle(s, (40, 25, 20), (4, 8), 1)
    return s


class _SleepingFox(_GroundEventBase):
    def __init__(self, palette, rng=None):
        super().__init__(palette, rng)
        self._sprite = _build_fox_sprite()
        self._ear_phase = self.rng.uniform(0, math.tau)

    def draw(self, surf):
        # Static plus a tiny ear flick now and then
        self._blit_sprite(surf)
        if math.sin(self.t * 0.7 + self._ear_phase) > 0.95:
            # Brief ear twitch — bright pixel near ear
            x = int(self.x) - 8
            y = GROUND_Y - 15
            pygame.draw.line(surf, (240, 220, 200), (x, y), (x + 1, y - 1), 1)


# ── G4: Beehive on stump ─────────────────────────────────────────────────────

def _build_beehive_sprite() -> pygame.Surface:
    s = pygame.Surface((24, 38), pygame.SRCALPHA)
    # Stump
    pygame.draw.rect(s, (115, 80, 50), (6, 28, 13, 10))
    pygame.draw.rect(s, (85, 55, 30), (6, 28, 13, 10), 1)
    pygame.draw.ellipse(s, (155, 115, 75), (5, 26, 14, 5))
    pygame.draw.ellipse(s, (100, 70, 40), (8, 27, 8, 3))
    # Hive (3 stacked layers)
    for i in range(3):
        y = 8 + i * 6
        inset = 2 - i
        x = 3 + inset
        w = 18 - inset * 2
        pygame.draw.ellipse(s, (200, 145, 70), (x, y, w, 8))
        pygame.draw.ellipse(s, (155, 100, 50), (x, y, w, 8), 1)
        pygame.draw.line(s, (170, 115, 55), (x + 1, y + 4), (x + w - 2, y + 4), 1)
    # Top dome
    pygame.draw.ellipse(s, (215, 160, 85), (8, 4, 8, 6))
    pygame.draw.ellipse(s, (155, 100, 50), (8, 4, 8, 6), 1)
    # Hole
    pygame.draw.circle(s, (40, 25, 15), (12, 20), 2)
    pygame.draw.circle(s, (90, 55, 25), (12, 20), 2, 1)
    return s


class _Beehive(_GroundEventBase):
    def __init__(self, palette, rng=None):
        super().__init__(palette, rng)
        self._sprite = _build_beehive_sprite()
        # 5 bees, each with its own orbit phase and radius
        self._bees = [
            (self.rng.uniform(0, math.tau),
             self.rng.uniform(6.0, 10.0),
             self.rng.uniform(1.0, 1.6))
            for _ in range(5)
        ]

    def draw(self, surf):
        self._blit_sprite(surf)
        cx = int(self.x)
        cy = GROUND_Y - 22  # roughly at hive centre
        for phase, radius, freq in self._bees:
            bx = cx + int(math.cos(self.t * freq + phase) * radius)
            by = cy + int(math.sin(self.t * freq * 1.3 + phase) * radius * 0.55)
            pygame.draw.circle(surf, (245, 210, 70), (bx, by), 1)
            pygame.draw.circle(surf, (30, 25, 20), (bx + 1, by), 1)


# ── G5: Wishing well ─────────────────────────────────────────────────────────

def _build_well_sprite() -> pygame.Surface:
    s = pygame.Surface((28, 40), pygame.SRCALPHA)
    # Stone base
    pygame.draw.ellipse(s, (140, 135, 125), (3, 22, 22, 16))
    pygame.draw.ellipse(s, (105, 100, 90), (3, 26, 22, 12))
    # Stone blocks pattern
    block = (175, 170, 160)
    block_dk = (115, 110, 100)
    for cx, cy in ((6, 26), (12, 28), (18, 27), (21, 31), (8, 33), (16, 33)):
        pygame.draw.rect(s, block, (cx, cy, 4, 3))
        pygame.draw.rect(s, block_dk, (cx, cy, 4, 3), 1)
    # Water surface
    pygame.draw.ellipse(s, (50, 80, 130), (5, 22, 18, 5))
    pygame.draw.ellipse(s, (100, 145, 200), (7, 23, 14, 2))
    # Wooden posts
    post_col = (110, 75, 40)
    post_dk = (80, 50, 25)
    pygame.draw.rect(s, post_col, (4, 4, 3, 22))
    pygame.draw.rect(s, post_dk, (4, 4, 3, 22), 1)
    pygame.draw.rect(s, post_col, (21, 4, 3, 22))
    pygame.draw.rect(s, post_dk, (21, 4, 3, 22), 1)
    # Crossbar with peaked roof
    pygame.draw.polygon(s, (140, 95, 50),
                       [(2, 6), (26, 6), (24, 2), (4, 2)])
    pygame.draw.line(s, (90, 60, 30), (4, 2), (24, 2), 1)
    pygame.draw.line(s, (90, 60, 30), (2, 6), (26, 6), 1)
    # Bucket hanging
    pygame.draw.rect(s, (95, 65, 35), (12, 10, 5, 6))
    pygame.draw.rect(s, (140, 95, 50), (12, 10, 5, 1))
    # Rope
    pygame.draw.line(s, (220, 200, 150), (14, 6), (14, 10), 1)
    return s


class _WishingWell(_GroundEventBase):
    def __init__(self, palette, rng=None):
        super().__init__(palette, rng)
        self._sprite = _build_well_sprite()
        self._twinkle_phase = self.rng.uniform(0, math.tau)

    def draw(self, surf):
        self._blit_sprite(surf)
        # Tiny water sparkle
        if math.sin(self.t * 2.4 + self._twinkle_phase) > 0.7:
            x = int(self.x) + self.rng.choice((-3, -1, 1, 3))
            y = GROUND_Y - 17
            pygame.draw.circle(surf, (240, 250, 255), (x, y), 1)


# ── G6: Scarecrow ────────────────────────────────────────────────────────────

def _build_scarecrow_sprite(has_crow: bool) -> pygame.Surface:
    width = 22 if has_crow else 18
    s = pygame.Surface((width, 44), pygame.SRCALPHA)
    bx = 9
    pole = (90, 60, 35)
    pole_dk = (60, 40, 20)
    # Pole + arms
    pygame.draw.line(s, pole, (bx, 8), (bx, 43), 3)
    pygame.draw.line(s, pole_dk, (bx + 1, 8), (bx + 1, 43), 1)
    pygame.draw.line(s, pole, (bx - 7, 16), (bx + 7, 16), 2)
    # Shirt
    pygame.draw.rect(s, (165, 95, 55), (bx - 5, 16, 11, 14))
    pygame.draw.rect(s, (115, 60, 30), (bx - 5, 16, 11, 14), 1)
    # Patch
    pygame.draw.rect(s, (90, 130, 70), (bx + 1, 22, 3, 3))
    pygame.draw.rect(s, (50, 90, 35), (bx + 1, 22, 3, 3), 1)
    # Straw at sleeves
    for off in (-7, 7):
        pygame.draw.line(s, (220, 180, 80),
                         (bx + off, 15), (bx + off - 1, 13), 1)
        pygame.draw.line(s, (220, 180, 80),
                         (bx + off, 17), (bx + off + 1, 19), 1)
    # Straw at waist
    for ox in (-4, 0, 4):
        pygame.draw.line(s, (220, 180, 80),
                         (bx + ox, 30), (bx + ox, 33), 1)
    # Head
    pygame.draw.circle(s, (220, 180, 130), (bx, 8), 5)
    pygame.draw.circle(s, (165, 130, 85), (bx, 8), 5, 1)
    # Floppy hat
    pygame.draw.ellipse(s, (75, 45, 25), (bx - 7, 1, 14, 4))
    pygame.draw.rect(s, (50, 30, 15), (bx - 3, -1, 6, 4))
    # Eyes + stitched mouth
    pygame.draw.circle(s, (30, 20, 15), (bx - 2, 8), 1)
    pygame.draw.circle(s, (30, 20, 15), (bx + 2, 8), 1)
    pygame.draw.line(s, (30, 20, 15), (bx - 2, 10), (bx + 2, 10), 1)
    # Straw fringe under hat
    pygame.draw.line(s, (220, 180, 80), (bx - 5, 5), (bx - 6, 7), 1)
    pygame.draw.line(s, (220, 180, 80), (bx + 5, 5), (bx + 6, 7), 1)
    if has_crow:
        cx = bx + 8
        cy = 14
        pygame.draw.ellipse(s, (35, 30, 35), (cx - 2, cy, 6, 3))
        pygame.draw.circle(s, (35, 30, 35), (cx + 3, cy), 2)
        pygame.draw.line(s, (245, 180, 60), (cx + 4, cy), (cx + 5, cy), 1)
        pygame.draw.circle(s, (220, 200, 60), (cx + 3, cy), 0)
    return s


class _Scarecrow(_GroundEventBase):
    def __init__(self, palette, rng=None):
        super().__init__(palette, rng)
        has_crow = self.rng.random() < 0.5
        self._sprite = _build_scarecrow_sprite(has_crow)

    def draw(self, surf):
        self._blit_sprite(surf)


# ── G7: Picnic blanket ───────────────────────────────────────────────────────

def _build_picnic_sprite() -> pygame.Surface:
    s = pygame.Surface((40, 18), pygame.SRCALPHA)
    # Checkered blanket
    for r in range(3):
        for c in range(9):
            x = c * 4 + 2
            y = r * 3 + 7
            col = (220, 60, 60) if (r + c) % 2 == 0 else (250, 245, 230)
            pygame.draw.rect(s, col, (x, y, 4, 3))
    pygame.draw.rect(s, (170, 35, 35), (2, 7, 36, 9), 1)
    # Basket
    pygame.draw.rect(s, (155, 105, 55), (4, 1, 9, 7))
    pygame.draw.line(s, (95, 60, 30), (4, 1), (12, 1), 1)
    pygame.draw.line(s, (130, 85, 40), (4, 3), (12, 3), 1)
    pygame.draw.line(s, (130, 85, 40), (4, 5), (12, 5), 1)
    pygame.draw.arc(s, (95, 60, 30), (4, -3, 9, 6), 0.0, math.pi, 1)
    # Apples
    pygame.draw.circle(s, (215, 50, 40), (18, 4), 2)
    pygame.draw.circle(s, (245, 100, 80), (17, 3), 1)
    pygame.draw.circle(s, (215, 50, 40), (24, 5), 2)
    pygame.draw.circle(s, (245, 100, 80), (23, 4), 1)
    # Glass / bottle
    pygame.draw.rect(s, (90, 150, 90), (30, 1, 3, 7))
    pygame.draw.rect(s, (140, 200, 140), (30, 1, 1, 7))
    return s


class _Picnic(_GroundEventBase):
    def __init__(self, palette, rng=None):
        super().__init__(palette, rng)
        self._sprite = _build_picnic_sprite()
        self._butterfly_phase = self.rng.uniform(0, math.tau)

    def draw(self, surf):
        self._blit_sprite(surf)
        # Occasional butterfly above basket
        if math.sin(self.t * 0.4 + self._butterfly_phase) > 0.3:
            bx = int(self.x) - 12 + int(math.cos(self.t * 1.6) * 2)
            by = GROUND_Y - 22 + int(math.sin(self.t * 2.0) * 1)
            col = (255, 220, 90)
            pygame.draw.circle(surf, col, (bx - 1, by), 2)
            pygame.draw.circle(surf, col, (bx + 2, by), 2)
            pygame.draw.line(surf, (30, 20, 15), (bx, by - 1), (bx, by + 1), 1)


# ── G8: Fairy mushroom ring ──────────────────────────────────────────────────

def _build_mushring_sprite() -> pygame.Surface:
    s = pygame.Surface((52, 24), pygame.SRCALPHA)
    # Soft cyan glow under the ring (drawn into RGBA, additively blitted)
    for r in (12, 8, 5, 3):
        a = max(20, 90 - r * 4)
        pygame.draw.ellipse(s, (140, 230, 255, a),
                            (26 - int(r * 1.6), 18 - int(r * 0.55),
                             int(r * 3.2), int(r * 1.1)))
    # 6 mushrooms — elliptical perspective
    positions = [(8, 19), (16, 14), (26, 12), (36, 14), (44, 19), (26, 21)]
    for px, py in positions:
        pygame.draw.rect(s, (245, 235, 210), (px - 1, py - 2, 2, 4))
        pygame.draw.ellipse(s, (130, 30, 30), (px - 4, py - 6, 8, 5))
        pygame.draw.ellipse(s, (210, 60, 60), (px - 4, py - 6, 8, 4))
        pygame.draw.circle(s, (250, 250, 245), (px - 1, py - 5), 1)
        pygame.draw.circle(s, (250, 250, 245), (px + 1, py - 4), 1)
    return s


class _MushroomRing(_GroundEventBase):
    def __init__(self, palette, rng=None):
        super().__init__(palette, rng)
        self._sprite = _build_mushring_sprite()
        # 4 sparkle particles floating up over the ring
        self._sparkles = [
            (self.rng.uniform(-18, 18),
             self.rng.uniform(0, math.tau))
            for _ in range(4)
        ]

    def draw(self, surf):
        self._blit_sprite(surf)
        # Upward-drifting sparkles
        layer = pygame.Surface((W, H), pygame.SRCALPHA)
        for off_x, phase in self._sparkles:
            cycle = (self.t * 0.4 + phase / math.tau) % 1.0  # 0..1
            sx = int(self.x) + int(off_x + math.sin(cycle * math.tau) * 3)
            sy = GROUND_Y - 8 - int(cycle * 26)
            a = int(230 * (1.0 - cycle))
            if a > 8:
                pygame.draw.circle(layer, (200, 240, 255, a), (sx, sy), 2)
                pygame.draw.circle(layer, (255, 255, 255, a), (sx, sy), 1)
        surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


# ── G9: Treasure chest ───────────────────────────────────────────────────────

def _build_chest_sprite() -> pygame.Surface:
    s = pygame.Surface((28, 22), pygame.SRCALPHA)
    # Lower box
    pygame.draw.rect(s, (105, 70, 35), (3, 11, 22, 11))
    pygame.draw.rect(s, (60, 35, 15), (3, 11, 22, 11), 1)
    # Curved lid
    pygame.draw.ellipse(s, (130, 90, 50), (3, 4, 22, 10))
    pygame.draw.rect(s, (130, 90, 50), (3, 9, 22, 4))
    pygame.draw.line(s, (60, 35, 15), (3, 10), (25, 10), 1)
    pygame.draw.ellipse(s, (60, 35, 15), (3, 4, 22, 10), 1)
    # Wood grain lines
    pygame.draw.line(s, (85, 55, 25), (3, 14), (25, 14), 1)
    pygame.draw.line(s, (85, 55, 25), (3, 17), (25, 17), 1)
    # Iron bands
    for bx in (6, 13, 20):
        pygame.draw.rect(s, (65, 60, 55), (bx, 4, 2, 18))
        pygame.draw.line(s, (110, 105, 100), (bx, 4), (bx, 22), 1)
    # Brass lock plate
    pygame.draw.rect(s, (215, 175, 75), (12, 12, 4, 5))
    pygame.draw.rect(s, (150, 110, 35), (12, 12, 4, 5), 1)
    # Keyhole
    pygame.draw.circle(s, (60, 40, 20), (14, 14), 1)
    pygame.draw.line(s, (60, 40, 20), (14, 14), (14, 16), 1)
    # Grass tufts at base
    pygame.draw.line(s, (60, 130, 60), (2, 22), (2, 19), 1)
    pygame.draw.line(s, (60, 130, 60), (25, 22), (25, 19), 1)
    return s


class _TreasureChest(_GroundEventBase):
    def __init__(self, palette, rng=None):
        super().__init__(palette, rng)
        self._sprite = _build_chest_sprite()
        self._glint_phase = self.rng.uniform(0, math.tau)

    def draw(self, surf):
        self._blit_sprite(surf)
        # Gold glint near keyhole
        if math.sin(self.t * 1.8 + self._glint_phase) > 0.85:
            x = int(self.x)
            y = GROUND_Y - 10
            pygame.draw.circle(surf, (255, 235, 130), (x, y), 1)
            pygame.draw.circle(surf, (255, 255, 220), (x - 1, y - 1), 1)


# ── G10: Will-o-the-wisp ─────────────────────────────────────────────────────

class _WillOWisp(_GroundEventBase):
    def __init__(self, palette, rng=None):
        super().__init__(palette, rng)
        self._bob_phase = self.rng.uniform(0, math.tau)
        self._pulse_phase = self.rng.uniform(0, math.tau)

    def draw(self, surf):
        x = int(self.x)
        bob = math.sin(self.t * 1.6 + self._bob_phase) * 4.0
        y = GROUND_Y - 18 + int(bob)
        pulse = 0.7 + 0.3 * math.sin(self.t * 2.4 + self._pulse_phase)
        layer = pygame.Surface((W, H), pygame.SRCALPHA)
        for r, base_a in ((12, 35), (8, 70), (5, 130), (3, 200)):
            a = int(base_a * pulse)
            pygame.draw.circle(layer, (170, 235, 255, a), (x, y), r)
        surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        pygame.draw.circle(surf, (235, 250, 255), (x, y), 1)


# ── G11: Bench with two people ───────────────────────────────────────────────

def _build_bench_sprite() -> pygame.Surface:
    s = pygame.Surface((42, 28), pygame.SRCALPHA)
    bench_top_y = 19
    # Seat
    pygame.draw.rect(s, (110, 75, 40), (2, bench_top_y, 38, 3))
    pygame.draw.line(s, (75, 50, 25), (2, bench_top_y), (40, bench_top_y), 1)
    # Legs
    pygame.draw.rect(s, (75, 50, 25), (4, bench_top_y + 3, 3, 6))
    pygame.draw.rect(s, (75, 50, 25), (35, bench_top_y + 3, 3, 6))
    # Backrest top rail
    pygame.draw.rect(s, (125, 85, 50), (2, 11, 38, 2))
    # Backrest slats
    for sx in (6, 14, 22, 30):
        pygame.draw.line(s, (95, 65, 35), (sx, 13), (sx, bench_top_y), 1)
    # Person 1 (left, pink shirt)
    p1x = 12
    pygame.draw.rect(s, (215, 85, 100), (p1x, 11, 6, 8))
    pygame.draw.rect(s, (175, 50, 70), (p1x, 11, 6, 8), 1)
    # Head + hair
    pygame.draw.circle(s, (235, 195, 150), (p1x + 3, 8), 3)
    pygame.draw.polygon(s, (80, 50, 30),
                       [(p1x, 8), (p1x + 6, 8), (p1x + 3, 4)])
    pygame.draw.circle(s, (30, 20, 15), (p1x + 2, 9), 0)
    pygame.draw.circle(s, (30, 20, 15), (p1x + 4, 9), 0)
    # Person 2 (right, blue shirt)
    p2x = 26
    pygame.draw.rect(s, (75, 120, 200), (p2x, 11, 6, 8))
    pygame.draw.rect(s, (45, 80, 150), (p2x, 11, 6, 8), 1)
    pygame.draw.circle(s, (235, 195, 150), (p2x + 3, 8), 3)
    pygame.draw.polygon(s, (105, 75, 40),
                       [(p2x, 8), (p2x + 6, 8), (p2x + 3, 4)])
    pygame.draw.circle(s, (30, 20, 15), (p2x + 2, 9), 0)
    pygame.draw.circle(s, (30, 20, 15), (p2x + 4, 9), 0)
    # Arms / hands resting between them (suggests they're chatting)
    pygame.draw.line(s, (215, 85, 100), (p1x + 6, 13), (p2x, 13), 1)
    return s


class _Bench(_GroundEventBase):
    def __init__(self, palette, rng=None):
        super().__init__(palette, rng)
        self._sprite = _build_bench_sprite()

    def draw(self, surf):
        self._blit_sprite(surf)


# ── G12: Napping person on the ground ────────────────────────────────────────

def _build_napper_sprite() -> pygame.Surface:
    s = pygame.Surface((34, 14), pygame.SRCALPHA)
    # Sleeping pad / pillow
    pygame.draw.ellipse(s, (135, 95, 130), (1, 10, 32, 4))
    pygame.draw.ellipse(s, (180, 140, 170), (1, 10, 32, 2))
    # Body lying horizontal (head right, feet left)
    pygame.draw.ellipse(s, (60, 130, 165), (5, 6, 22, 5))
    pygame.draw.ellipse(s, (30, 95, 130), (5, 6, 22, 5), 1)
    # Arm tucked
    pygame.draw.ellipse(s, (235, 195, 150), (7, 9, 6, 2))
    # Head
    pygame.draw.circle(s, (235, 195, 150), (29, 8), 3)
    pygame.draw.ellipse(s, (100, 60, 30), (26, 5, 6, 4))
    # Closed eye
    pygame.draw.line(s, (40, 25, 20), (28, 8), (30, 8), 1)
    # Z's above for sleep
    pygame.draw.line(s, (200, 200, 220), (14, 2), (17, 2), 1)
    pygame.draw.line(s, (200, 200, 220), (17, 2), (14, 4), 1)
    pygame.draw.line(s, (200, 200, 220), (14, 4), (17, 4), 1)
    pygame.draw.line(s, (200, 200, 220), (19, 0), (21, 0), 1)
    pygame.draw.line(s, (200, 200, 220), (21, 0), (19, 2), 1)
    pygame.draw.line(s, (200, 200, 220), (19, 2), (21, 2), 1)
    return s


class _Napper(_GroundEventBase):
    def __init__(self, palette, rng=None):
        super().__init__(palette, rng)
        self._sprite = _build_napper_sprite()
        self._z_phase = self.rng.uniform(0, math.tau)

    def draw(self, surf):
        # Soft breath bob — body moves up/down by ~1 px slowly
        bob = int(math.sin(self.t * 1.2 + self._z_phase) * 0.6)
        self._blit_sprite(surf, y_off=bob)


# ── G13: Lightly running dog (2-frame anim) ─────────────────────────────────

def _build_dog_frames() -> list[pygame.Surface]:
    frames = []
    body = (185, 130, 75)
    body_dk = (135, 85, 40)
    for f in range(2):
        s = pygame.Surface((26, 18), pygame.SRCALPHA)
        # Tail wagging up/down between frames
        tail_y = 6 if f == 0 else 4
        pygame.draw.line(s, body, (3, 8), (1, tail_y), 2)
        pygame.draw.line(s, body_dk, (3, 8), (1, tail_y), 1)
        # Body
        pygame.draw.ellipse(s, body, (3, 6, 18, 7))
        pygame.draw.ellipse(s, body_dk, (3, 6, 18, 7), 1)
        # Belly
        pygame.draw.ellipse(s, (235, 215, 185), (6, 10, 12, 3))
        # Head
        pygame.draw.ellipse(s, body, (17, 4, 8, 7))
        pygame.draw.ellipse(s, body_dk, (17, 4, 8, 7), 1)
        # Floppy ear
        pygame.draw.polygon(s, body_dk,
                           [(18, 4), (21, 4), (20, 8)])
        # Eye + nose
        pygame.draw.circle(s, (30, 20, 15), (22, 7), 1)
        pygame.draw.circle(s, (40, 25, 20), (24, 8), 1)
        # Tongue (small pink)
        pygame.draw.line(s, (240, 110, 130), (24, 10), (25, 11), 1)
        # Legs — two frames give the run animation
        if f == 0:
            # Front legs stretched fwd, back legs stretched back
            pygame.draw.line(s, body_dk, (17, 12), (20, 17), 2)
            pygame.draw.line(s, body_dk, (14, 12), (12, 17), 2)
            pygame.draw.line(s, body_dk, (8, 12), (5, 17), 2)
            pygame.draw.line(s, body_dk, (5, 12), (7, 17), 2)
        else:
            # Front legs gathered, back legs gathered
            pygame.draw.line(s, body_dk, (17, 12), (16, 17), 2)
            pygame.draw.line(s, body_dk, (14, 12), (15, 17), 2)
            pygame.draw.line(s, body_dk, (8, 12), (9, 17), 2)
            pygame.draw.line(s, body_dk, (5, 12), (4, 17), 2)
        frames.append(s)
    return frames


class _RunningDog(_GroundEventBase):
    def __init__(self, palette, rng=None):
        super().__init__(palette, rng)
        self._frames = _build_dog_frames()

    def draw(self, surf):
        frame_idx = int(self.t * 9) % 2
        sprite = self._frames[frame_idx]
        sw, sh = sprite.get_size()
        # Body bob in sync with strides
        bob = int(math.sin(self.t * 18) * 0.7)
        surf.blit(sprite, (int(self.x) - sw // 2,
                           GROUND_Y - sh + 1 + bob))


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
        # Ground events (drift-by scenery)
        self.sheep: _Sheep | None = None
        self.rabbits: _RabbitHop | None = None
        self.fox: _SleepingFox | None = None
        self.beehive: _Beehive | None = None
        self.well: _WishingWell | None = None
        self.scarecrow: _Scarecrow | None = None
        self.picnic: _Picnic | None = None
        self.mushring: _MushroomRing | None = None
        self.chest: _TreasureChest | None = None
        self.wisp: _WillOWisp | None = None
        self.bench: _Bench | None = None
        self.napper: _Napper | None = None
        self.dog: _RunningDog | None = None
        self._flock_cool = random.uniform(*_FLOCK_INITIAL_DELAY)
        self._fireworks_cool = random.uniform(*_FIREWORKS_INITIAL_DELAY)
        self._balloon_cool = random.uniform(*_BALLOON_INITIAL_DELAY)
        self._parrots_cool = random.uniform(*_PARROTS_INITIAL_DELAY)
        self._campfire_cool = random.uniform(*_CAMPFIRE_INITIAL_DELAY)
        self._sheep_cool = random.uniform(*_SHEEP_INITIAL_DELAY)
        self._rabbits_cool = random.uniform(*_RABBITS_INITIAL_DELAY)
        self._fox_cool = random.uniform(*_FOX_INITIAL_DELAY)
        self._beehive_cool = random.uniform(*_BEEHIVE_INITIAL_DELAY)
        self._well_cool = random.uniform(*_WELL_INITIAL_DELAY)
        self._scarecrow_cool = random.uniform(*_SCARECROW_INITIAL_DELAY)
        self._picnic_cool = random.uniform(*_PICNIC_INITIAL_DELAY)
        self._mushring_cool = random.uniform(*_MUSHRING_INITIAL_DELAY)
        self._chest_cool = random.uniform(*_CHEST_INITIAL_DELAY)
        self._wisp_cool = random.uniform(*_WISP_INITIAL_DELAY)
        self._bench_cool = random.uniform(*_BENCH_INITIAL_DELAY)
        self._napper_cool = random.uniform(*_NAPPER_INITIAL_DELAY)
        self._dog_cool = random.uniform(*_DOG_INITIAL_DELAY)

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

        # ── Ground events (all world-anchored, same pattern as campfire) ──
        for slot_name, cls, phases, cool_attr, cool_const, jitter in (
            ("sheep", _Sheep, _SHEEP_PHASES, "_sheep_cool",
             _SHEEP_COOLDOWN_S, 25),
            ("rabbits", _RabbitHop, _RABBITS_PHASES, "_rabbits_cool",
             _RABBITS_COOLDOWN_S, 30),
            ("fox", _SleepingFox, _FOX_PHASES, "_fox_cool",
             _FOX_COOLDOWN_S, 30),
            ("beehive", _Beehive, _BEEHIVE_PHASES, "_beehive_cool",
             _BEEHIVE_COOLDOWN_S, 25),
            ("well", _WishingWell, _WELL_PHASES, "_well_cool",
             _WELL_COOLDOWN_S, 30),
            ("scarecrow", _Scarecrow, _SCARECROW_PHASES, "_scarecrow_cool",
             _SCARECROW_COOLDOWN_S, 30),
            ("picnic", _Picnic, _PICNIC_PHASES, "_picnic_cool",
             _PICNIC_COOLDOWN_S, 35),
            ("mushring", _MushroomRing, _MUSHRING_PHASES, "_mushring_cool",
             _MUSHRING_COOLDOWN_S, 35),
            ("chest", _TreasureChest, _CHEST_PHASES, "_chest_cool",
             _CHEST_COOLDOWN_S, 50),
            ("wisp", _WillOWisp, _WISP_PHASES, "_wisp_cool",
             _WISP_COOLDOWN_S, 25),
            ("bench", _Bench, _BENCH_PHASES, "_bench_cool",
             _BENCH_COOLDOWN_S, 30),
            ("napper", _Napper, _NAPPER_PHASES, "_napper_cool",
             _NAPPER_COOLDOWN_S, 30),
            ("dog", _RunningDog, _DOG_PHASES, "_dog_cool",
             _DOG_COOLDOWN_S, 25),
        ):
            inst = getattr(self, slot_name)
            if inst is not None:
                inst.update(dt, bg_scroll)
                if inst.is_done():
                    setattr(self, slot_name, None)
            elif self._in_window(phase, phases):
                cool = getattr(self, cool_attr) - dt
                if cool <= 0:
                    setattr(self, slot_name, cls(palette, random.Random()))
                    cool = cool_const + random.uniform(-jitter, jitter)
                setattr(self, cool_attr, cool)

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
        # Ground events — static / opaque first, then glow events on top so
        # halos sit over (not under) the structures.
        for slot_name in ("sheep", "rabbits", "fox", "beehive", "well",
                          "scarecrow", "picnic", "chest", "bench", "napper",
                          "dog", "mushring", "wisp"):
            inst = getattr(self, slot_name)
            if inst is not None:
                inst.draw(surf)
        self.blossoms.draw(surf)
