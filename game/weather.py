"""
Biome-driven weather: rain streaks, lightning flashes, wind-blown leaves.

Weather is keyed to `biome_phase` rather than `biome_time` so it follows the
sky. Everything is procedural — particle-style rain streaks and a brief
full-surface alpha pulse for lightning.
"""
from __future__ import annotations

import math
import random

import pygame

from game.config import W, H, GROUND_Y
from game import audio


# ── phase → intensity curves ────────────────────────────────────────────────

def _bump(phase: float, center: float, width: float) -> float:
    """Smooth bump peaking at `center` and fading over ±width. Returns 0..1."""
    d = abs(((phase - center + 0.5) % 1.0) - 0.5)
    if d >= width:
        return 0.0
    t = 1.0 - d / width
    return t * t * (3 - 2 * t)  # smoothstep


def rain_intensity(phase: float) -> float:
    """Rain: amber-warm at sunset (0.32), cool-blue at dusk (0.48),
    sparse at night (0.62)."""
    a = _bump(phase, 0.35, 0.12) * 0.55   # sunset drizzle
    b = _bump(phase, 0.50, 0.10) * 1.00   # dusk storm
    c = _bump(phase, 0.62, 0.10) * 0.45   # night residual
    return max(0.0, min(1.0, a + b + c))


def rain_color(phase: float):
    """Blend between warm amber (sunset) and cool slate (dusk/night)."""
    warm = (255, 200, 140)
    cool = (140, 170, 220)
    # Closer to 0.35 → warmer; closer to 0.50+ → cooler
    t_cool = min(1.0, max(0.0, (phase - 0.35) / 0.2))
    return (
        int(warm[0] + (cool[0] - warm[0]) * t_cool),
        int(warm[1] + (cool[1] - warm[1]) * t_cool),
        int(warm[2] + (cool[2] - warm[2]) * t_cool),
    )


def lightning_active(phase: float) -> bool:
    """Lightning only during the night window."""
    return 0.55 <= phase <= 0.72


def calm_breeze(phase: float) -> float:
    """Golden-hour calm breeze (phase 0.18) — drives the ambient
    drifting autumn leaves only, no gameplay effect."""
    return _bump(phase, 0.18, 0.10) * 0.35


def storm_intensity(phase: float) -> float:
    """The predawn SNOW SQUALL event (phase 0.85) — the single
    bump that drives the snow visuals, the cold atmospheric wash,
    AND the tailwind gameplay (Pip's forward push + scroll boost).
    A ~8-second plateau at the peak (phase 0.8375-0.8625) keeps
    the climax sustained: the smoothstep bump is scaled 1.045 then
    clamped at 1.0, flattening the top while the ramps stay
    smooth. 0 everywhere outside the predawn window, so the
    golden-hour breeze (calm_breeze) never triggers snow."""
    return min(1.0, _bump(phase, 0.85, 0.10) * 1.045)


def wind_intensity(phase: float) -> float:
    """Combined curve (calm breeze + storm) kept for any caller
    that wants the union. Snow visuals + gameplay use
    storm_intensity directly; leaves use calm_breeze."""
    return max(0.0, min(1.0, calm_breeze(phase) + storm_intensity(phase)))


def sand_intensity(phase: float) -> float:
    """The daytime SANDSTORM (haboob). Asymmetric: a long slow
    rise (the tease), a short plateau (peak haboob), a quicker
    fade — all inside the bright-day window and fully clear before
    the sunset rain turns on (~0.23), so the two never overlap.
      0 below 0.03 / above 0.22
      rise   0.03 -> 0.15   (long tease + approach)
      plateau 0.15 -> 0.17  (peak)
      fade   0.17 -> 0.22
    Read in bands by the renderer: <0.35 tease (distant wall +
    devils only), 0.35-0.65 encroaching, >=0.65 peak."""
    if phase < 0.03 or phase > 0.22:
        return 0.0
    if phase <= 0.15:
        t = (phase - 0.03) / (0.15 - 0.03)
        return t * t * (3 - 2 * t)
    if phase <= 0.17:
        return 1.0
    t = 1.0 - (phase - 0.17) / (0.22 - 0.17)
    return t * t * (3 - 2 * t)


# Sandstorm (haboob) palette — the EXACT original-haboob tones.
SAND_HI   = ((250, 210, 150), (255, 225, 170))      # sunlit rim
SAND_BODY = ((150, 100, 58), (130, 86, 48), (168, 116, 70))
SAND_DEEP = ((96, 62, 36), (80, 52, 30))
SAND_HAZE = (198, 148, 82)                          # warm cast / veil
SAND_HORIZON = GROUND_Y - 70


# Cold wash colour for the snow squall — a deep blue-grey that
# cools the whole scene so the bright white snow pops against it.
SNOW_TINT = (74, 96, 130)
SNOW_TINT_PEAK_A = 130
_WHITE = (255, 255, 255)


# Cached soft round snowflake sprites — pre-rendered once per
# (radius, alpha-bucket) so each flake is a cheap blit of a smooth
# anti-aliased disc (no per-frame surface building, no aliased
# pixels). Mirrors the project's glow-cache convention.
_FLAKE_CACHE: dict = {}


def _snow_flake(radius: int, alpha: int):
    radius = max(1, int(radius))
    abucket = max(16, min(255, (int(alpha) // 16) * 16))
    key = (radius, abucket)
    cached = _FLAKE_CACHE.get(key)
    if cached is not None:
        return cached
    d = radius * 2 + 2
    surf = pygame.Surface((d, d), pygame.SRCALPHA)
    cx = cy = radius + 1
    steps = max(3, radius)
    for i in range(steps, 0, -1):
        rr = max(1, int(radius * i / steps))
        frac = i / steps                         # 1 rim → ~0 centre
        a = int(abucket * (1.0 - frac) ** 1.4)   # 0 rim → alpha centre
        pygame.draw.circle(surf, (255, 255, 255, a), (cx, cy), rr)
    _FLAKE_CACHE[key] = surf
    return surf


# ── sandstorm helpers ────────────────────────────────────────────────────────

_SAND_DISC_CACHE: dict = {}
_SAND_SS = 2                                 # supersample for smooth walls
SAND_MOTE_COL = (196, 156, 100)


def _sand_disc(radius, color, alpha):
    """Cached soft ochre puff (smooth radial falloff)."""
    radius = max(1, int(radius))
    ab = max(16, min(255, (int(alpha) // 16) * 16))
    key = (radius, ab, color)
    cached = _SAND_DISC_CACHE.get(key)
    if cached is not None:
        return cached
    d = radius * 2 + 2
    surf = pygame.Surface((d, d), pygame.SRCALPHA)
    c = radius + 1
    steps = max(3, radius)
    for i in range(steps, 0, -1):
        rr = max(1, int(radius * i / steps))
        frac = i / steps
        a = int(ab * (1.0 - frac) ** 1.3)
        pygame.draw.circle(surf, (*color, a), (c, c), rr)
    _SAND_DISC_CACHE[key] = surf
    return surf


class _SandMote:
    """A drifting sand speck blowing rightward across the playfield."""
    __slots__ = ("x", "y", "vx", "vy", "r", "alpha")

    def __init__(self):
        self.x = random.uniform(-10, W)
        self.y = random.uniform(0, GROUND_Y)
        self.vx = random.uniform(120, 270)
        self.vy = random.uniform(-15, 28)
        self.r = random.randint(2, 5)
        self.alpha = random.randint(70, 150)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def off_screen(self):
        return self.x > W + 8 or self.y > GROUND_Y or self.y < -12

    def draw(self, surf):
        spr = _sand_disc(self.r, SAND_MOTE_COL, self.alpha)
        surf.blit(spr, (int(self.x) - spr.get_width() // 2,
                        int(self.y) - spr.get_height() // 2))


def _render_sand_wall(s, kind, seed):
    """Render a haboob dust wall to a smooth (supersampled) Surface,
    cached by the caller per intensity bucket. `kind`:
      'far'   — distant wall + dust-devils on the horizon (tease)
      'front' — foreground engulfing wall rising from the ground.
    Uses the exact original-haboob palette."""
    SS = _SAND_SS
    rng = random.Random(seed)
    big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    gy0 = GROUND_Y * SS

    if kind == "far":
        base_y = (SAND_HORIZON + 12) * SS
        height = (0.20 + s * 0.28) * H * SS

        def top_y(xf):
            lump = (math.sin(xf * 7 + 0.5) * 0.11
                    + math.sin(xf * 17 + 2.0) * 0.05) * height
            return base_y - height + lump

        cols = int(80 + s * 40)
        for ci in range(cols):
            xf = ci / (cols - 1)
            gx = xf * W * SS
            top = top_y(xf)
            for _ in range(int(5 + s * 5)):
                yy = rng.uniform(top, base_y + 10 * SS)
                d = (yy - top) / max(1.0, base_y - top)
                r = int(rng.uniform(13, 24) * SS)
                col = (rng.choice(SAND_DEEP) if rng.random() < d * 0.85
                       else rng.choice(SAND_BODY))
                big.blit(_sand_disc(r, col, rng.randint(85, 145)),
                         (gx - r + rng.uniform(-12, 12) * SS, yy - r))
            if rng.random() < 0.6:
                rr = int(rng.uniform(8, 16) * SS)
                big.blit(_sand_disc(rr, rng.choice(SAND_HI), rng.randint(90, 150)),
                         (gx - rr, top - rr * 0.4))
        # dust-devils on the horizon
        for k, dx in enumerate((0.30, 0.72)):
            cx = W * SS * dx
            h = (110 + s * 120) * SS
            steps = int(h / (5 * SS))
            for i in range(steps):
                t = i / steps
                wob = math.sin(t * 7.0 + k * 2.0) * 11 * SS * (1 - t)
                r = int((3 + (1 - t) * 9) * SS * (0.6 + s * 0.5))
                a = int((55 + s * 110) * (0.4 + 0.6 * (1 - t)))
                col = rng.choice(SAND_HI) if t > 0.85 else rng.choice(SAND_BODY)
                big.blit(_sand_disc(r, col, a),
                         (cx + wob - r, (SAND_HORIZON + 4) * SS - t * h - r))
    else:  # front
        fs = max(0.0, (s - 0.40) / 0.60)
        top_frac = 0.92 - 0.50 * fs

        def wall_top(xf):
            base = gy0 * (top_frac - xf * 0.10 * fs)
            lump = (math.sin(xf * 9) * 0.045
                    + math.sin(xf * 23 + 1.7) * 0.028) * gy0 * (0.4 + fs)
            return base + lump

        cols = int(55 + fs * 50)
        for ci in range(cols):
            xf = ci / (cols - 1)
            gx = xf * W * SS
            top = wall_top(xf)
            for _ in range(int(5 + fs * 8)):
                yy = rng.uniform(top - 8 * SS, gy0)
                d = (yy - top) / max(1.0, gy0 - top)
                r = int(rng.uniform(18, 34) * SS)
                col = (rng.choice(SAND_DEEP) if rng.random() < d * 0.85
                       else rng.choice(SAND_BODY))
                big.blit(_sand_disc(r, col, rng.randint(95, 150)),
                         (gx - r + rng.uniform(-14, 14) * SS, yy - r))
            if rng.random() < 0.5:
                rr = int(rng.uniform(10, 20) * SS)
                big.blit(_sand_disc(rr, rng.choice(SAND_HI), rng.randint(60, 110)),
                         (gx - rr, top - rr * 0.5))
        for _ in range(int(fs * 170)):
            xf = rng.random() ** 0.5
            gx = xf * W * SS
            gy = rng.uniform(wall_top(xf) - 130 * SS, wall_top(xf))
            if gy < 0:
                continue
            r = rng.randint(3, 8) * SS
            big.blit(_sand_disc(r, rng.choice(SAND_BODY), rng.randint(50, 110)),
                     (gx - r, gy - r))
    return pygame.transform.smoothscale(big, (W, H))


# ── particle: a single rain streak ──────────────────────────────────────────

class _Streak:
    __slots__ = ("x", "y", "vx", "vy", "len", "color")

    def __init__(self, x, y, vx, vy, length, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.len = length
        self.color = color

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def off_screen(self):
        return self.y > GROUND_Y or self.x < -8 or self.x > W + 8

    def draw(self, surf):
        dx = self.vx / max(1.0, abs(self.vy)) * self.len
        dy = self.len
        pygame.draw.line(surf, self.color,
                         (int(self.x), int(self.y)),
                         (int(self.x - dx), int(self.y - dy)), 1)


class _Leaf:
    __slots__ = ("x", "y", "vx", "vy", "spin", "phase", "color")

    def __init__(self, x, y, vx, vy, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.spin = random.uniform(0, math.tau)
        self.phase = random.uniform(0, math.tau)
        self.color = color

    def update(self, dt):
        self.phase += dt * 3.0
        self.spin += dt * 2.0
        # Lateral flutter
        self.x += (self.vx + math.sin(self.phase) * 20) * dt
        self.y += self.vy * dt

    def off_screen(self):
        return self.x < -20 or self.x > W + 20 or self.y > GROUND_Y

    def draw(self, surf):
        r = 3
        sx = math.cos(self.spin)
        rx = max(1, int(abs(sx) * r))
        pygame.draw.ellipse(surf, self.color,
                            (int(self.x) - rx, int(self.y) - r, rx * 2, r * 2))


class _WindStreak:
    """Driven-snow streak — the fast, near-horizontal lines of
    snow blown hard by the tailwind (the storm's headline cue).
    Drawn as a TAPERED white motion-blur trail (3 sub-segments,
    faded → peak → faded) with a bright core; a gentle sine
    wobble curves the path so it reads as wind-driven."""
    __slots__ = ("x", "y", "vx", "vy", "len", "color", "alpha",
                 "wobble_phase", "wobble_freq", "wobble_amp", "t")

    def __init__(self, x, y, vx, vy, length, color, alpha,
                 wobble_amp=2.5, wobble_freq=10.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.len = length
        self.color = color
        self.alpha = alpha
        self.wobble_phase = random.uniform(0, math.tau)
        self.wobble_freq = wobble_freq
        self.wobble_amp = wobble_amp
        self.t = 0.0

    def update(self, dt):
        self.t += dt
        # Sine waver on the y as the streak travels — wind doesn't
        # go in straight lines.
        self.x += self.vx * dt
        wobble_dy = math.cos(self.wobble_phase + self.t * self.wobble_freq) \
                    * self.wobble_amp * self.wobble_freq * dt
        self.y += self.vy * dt + wobble_dy

    def off_screen(self):
        return self.x > W + 40 or self.y > GROUND_Y or self.y < -30

    def draw(self, surf):
        # Tail extends opposite the motion. Length scales with the
        # configured `len`; faster streaks naturally have longer
        # visible trails.
        speed = math.hypot(self.vx, self.vy)
        if speed < 1.0:
            return
        ux = self.vx / speed
        uy = self.vy / speed
        # Trail goes opposite the motion direction
        tail_x = self.x - ux * self.len
        tail_y = self.y - uy * self.len
        # Tapered alpha: paint the streak as 3 sub-segments with
        # alphas in a triangular envelope (faded → peak → faded).
        # 3 segments (not 5) keep the streak reading as one
        # continuous motion-blur trail rather than a chain of
        # disconnected dashes.
        n = 3
        envelope = (0.50, 1.00, 0.50)
        # Compute padded bounds for the SRCALPHA scratch surface
        x1 = int(self.x);     y1 = int(self.y)
        x2 = int(tail_x);     y2 = int(tail_y)
        ox = min(x1, x2) - 3
        oy = min(y1, y2) - 3
        sw = abs(x2 - x1) + 6
        sh = abs(y2 - y1) + 6
        sub = pygame.Surface((sw, sh), pygame.SRCALPHA)
        for i in range(n):
            t0 = i / n
            t1 = (i + 1) / n
            sx0 = self.x + (tail_x - self.x) * t0
            sy0 = self.y + (tail_y - self.y) * t0
            sx1 = self.x + (tail_x - self.x) * t1
            sy1 = self.y + (tail_y - self.y) * t1
            a = int(self.alpha * envelope[i])
            if a <= 0:
                continue
            pygame.draw.line(sub, (*self.color, a),
                             (int(sx0 - ox), int(sy0 - oy)),
                             (int(sx1 - ox), int(sy1 - oy)), 2)
            # Bright 1-px white core along the same path
            core_a = min(255, a + 60)
            pygame.draw.line(sub, (255, 255, 255, core_a),
                             (int(sx0 - ox), int(sy0 - oy)),
                             (int(sx1 - ox), int(sy1 - oy)), 1)
        surf.blit(sub, (ox, oy))


class _WindDrift:
    """Big soft foreground snowflakes — the slow, near, slightly
    blurred flakes that give the snow depth (parallax against the
    smaller/faster `_WindDust` flakes). `len` is reused as the
    flake radius. Rendered via the cached smooth-disc sprite."""
    __slots__ = ("x", "y", "vx", "vy", "len", "color", "alpha")

    def __init__(self, x, y, vx, vy, length, color, alpha):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.len = length
        self.color = color
        self.alpha = alpha

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def off_screen(self):
        return self.x > W + 30 or self.y > GROUND_Y or self.y < -30

    def draw(self, surf):
        spr = _snow_flake(self.len, self.alpha)
        surf.blit(spr, (int(self.x) - spr.get_width() // 2,
                        int(self.y) - spr.get_height() // 2))


class _WindSwirl:
    """Iconic cartoon-wind shorthand: a small S/spiral motif
    drifting across the screen. Three layered strokes (outer
    halo / mid / bright core) along an arc. Rotates slowly as it
    drifts so each swirl shape evolves over its lifetime."""
    __slots__ = ("x", "y", "vx", "vy", "size", "color",
                 "alpha", "rot", "rot_rate", "phase", "life", "life_max")

    def __init__(self, x, y, vx, vy, size, color, alpha,
                 rot_rate, life):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.alpha = alpha
        self.rot = random.uniform(0, math.tau)
        self.rot_rate = rot_rate
        self.phase = random.uniform(0, math.tau)
        self.life = life
        self.life_max = life

    def update(self, dt):
        self.x += self.vx * dt
        # Slight up/down wobble as it drifts
        self.y += (self.vy + math.sin(self.phase + self.life * 4.0) * 12) * dt
        self.rot += self.rot_rate * dt
        self.life -= dt

    def off_screen(self):
        return self.x > W + 40 or self.life <= 0

    def draw(self, surf):
        # Fade in at birth and fade out at death — life curve.
        t = self.life / self.life_max
        # Envelope: ease-in at start (fade in over first 20%),
        # ease-out at end (fade out over last 30%).
        if t > 0.80:
            env = (1.0 - t) / 0.20    # rising from 0 → 1
        elif t < 0.30:
            env = t / 0.30            # falling from 1 → 0
        else:
            env = 1.0
        a_base = int(self.alpha * env)
        if a_base <= 5:
            return
        # The swirl is a smooth S-curve sampled at 12 points along
        # a quadratic Bezier-like arc. Sweep is ~220° (3/4 of a
        # full circle) so it reads clearly as a curve, not a
        # closed loop. Smoother than the previous 7-point spiral
        # at small render sizes.
        pts = []
        cos_r = math.cos(self.rot)
        sin_r = math.sin(self.rot)
        n_pts = 12
        for k in range(n_pts):
            tt = k / (n_pts - 1)
            # Parametric spiral coords: angle goes 0 → 220°,
            # radius eases from 30% to 100% of size so the inner
            # tip is tighter than the outer tip
            theta = tt * math.radians(220.0)
            r = self.size * (0.30 + 0.70 * tt)
            px = math.cos(theta) * r
            py = math.sin(theta) * r * 0.60   # flatten slightly
            rx = px * cos_r - py * sin_r
            ry = px * sin_r + py * cos_r
            pts.append((self.x + rx, self.y + ry))
        # 3-layer polyline: halo / mid / bright core
        ox = int(min(p[0] for p in pts)) - 4
        oy = int(min(p[1] for p in pts)) - 4
        sw = int(max(p[0] for p in pts)) - ox + 4
        sh = int(max(p[1] for p in pts)) - oy + 4
        sub = pygame.Surface((sw, sh), pygame.SRCALPHA)
        local_pts = [(int(p[0]) - ox, int(p[1]) - oy) for p in pts]
        for w, col, a_mul in (
            (4, self.color,        0.35),   # outer halo
            (2, self.color,        0.85),   # mid stroke
            (1, (255, 255, 255),   1.10),   # bright core
        ):
            a = min(255, int(a_base * a_mul))
            if a <= 0:
                continue
            pygame.draw.lines(sub, (*col, a), False, local_pts, w)
        surf.blit(sub, (ox, oy))


class _WindDust:
    """Snowflake — the bulk of the snow field. Small-to-medium
    soft round white flakes drifting rightward + down with the
    tailwind. `size` is the flake radius; rendered via the cached
    smooth-disc sprite so edges stay soft, never pixelated."""
    __slots__ = ("x", "y", "vx", "vy", "size", "color", "alpha")

    def __init__(self, x, y, vx, vy, size, color, alpha):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.alpha = alpha

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def off_screen(self):
        return self.x > W + 12 or self.y > GROUND_Y or self.y < -20

    def draw(self, surf):
        spr = _snow_flake(self.size, self.alpha)
        surf.blit(spr, (int(self.x) - spr.get_width() // 2,
                        int(self.y) - spr.get_height() // 2))


# ── main Weather controller ────────────────────────────────────────────────

class Weather:
    def __init__(self):
        self.streaks: list[_Streak] = []
        self.leaves: list[_Leaf] = []
        # Wind-event particle pools — layered for parallax depth:
        #   drift   = slow background, longest visible early
        #   dust    = fast foreground specks (textural density)
        #   streaks = mid-ground fast streaks (the headline)
        #   swirls  = iconic cartoon-wind cue (peak only)
        # All four scale spawn rate with wind_intensity, gated at
        # different thresholds so the buildup reads as "more
        # types of wind appearing" not just more of the same.
        self.wind_drifts: list[_WindDrift] = []
        self.wind_dust: list[_WindDust] = []
        self.wind_streaks: list[_WindStreak] = []
        self.wind_swirls: list[_WindSwirl] = []
        self.phase: float = 0.0

        # Lightning state: countdown to next strike, and flash envelope 0..1.
        self.flash_remaining: float = 0.0
        self.next_strike: float = random.uniform(4.0, 9.0)

        # Sandstorm: live mote pool + cached wall surfaces (the
        # walls are expensive supersampled puff masses, so we
        # rebuild them only when the intensity BUCKET changes and
        # blit the cache each frame — see _sand_wall).
        self.sand_motes: list[_SandMote] = []
        self._sand_far_cache = None       # (bucket, Surface) distant wall
        self._sand_front_cache = None     # (bucket, Surface) foreground wall

    def update(self, dt, phase):
        self.phase = phase

        # Rain
        intensity = rain_intensity(phase)
        if intensity > 0:
            color = rain_color(phase)
            target = int(50 + intensity * 90)
            # Top up the pool — streaks spawn above the screen and fall.
            while len(self.streaks) < target:
                self._spawn_streak(intensity, color)
            for s in self.streaks:
                s.update(dt)
            self.streaks = [s for s in self.streaks if not s.off_screen()]
        else:
            # Fade out lingering rain
            self.streaks = [s for s in self.streaks if not s.off_screen()][:max(0, len(self.streaks) - 2)]
            for s in self.streaks:
                s.update(dt)

        # Golden-hour leaves — ambient autumn drift, driven only by
        # the calm breeze bump (phase 0.18) so they never mix with
        # the predawn snow squall.
        breeze = calm_breeze(phase)
        if breeze > 0:
            target = int(breeze * 10)
            while len(self.leaves) < target:
                self._spawn_leaf(breeze)
            for lf in self.leaves:
                lf.update(dt)
            self.leaves = [lf for lf in self.leaves if not lf.off_screen()]
        else:
            self.leaves = []

        # SNOW SQUALL — four layered snow particle types driven by
        # the storm bump (phase 0.85). Each layer gates in at a
        # different threshold so the buildup reads as the snow
        # thickening, not just appearing all at once:
        #   storm > 0.10  big drift flakes + bulk flakes
        #   storm > 0.15  driven-snow streaks
        #   storm > 0.30  turbulence curls
        storm = storm_intensity(phase)

        # Big soft foreground flakes (slow parallax depth).
        if storm > 0.10:
            drift_t = (storm - 0.10) / 0.90
            target = int(drift_t * 30)
            while len(self.wind_drifts) < target:
                self._spawn_wind_drift(drift_t, phase)
        for wd in self.wind_drifts:
            wd.update(dt)
        self.wind_drifts = [wd for wd in self.wind_drifts
                             if not wd.off_screen()]

        # Bulk snowflakes — dense at peak (the body of the squall).
        if storm > 0.10:
            dust_t = (storm - 0.10) / 0.90
            target = int(dust_t * 200)
            while len(self.wind_dust) < target:
                self._spawn_wind_dust(dust_t, phase)
        for du in self.wind_dust:
            du.update(dt)
        self.wind_dust = [du for du in self.wind_dust
                          if not du.off_screen()]

        # Driven-snow streaks (the wind-blown headline).
        if storm > 0.15:
            streak_t = (storm - 0.15) / 0.85
            target = int(streak_t * 70)
            while len(self.wind_streaks) < target:
                self._spawn_wind_streak(streak_t, phase)
        for ws in self.wind_streaks:
            ws.update(dt)
        self.wind_streaks = [ws for ws in self.wind_streaks
                             if not ws.off_screen()]

        # Turbulence curls — small white eddies, peak only.
        if storm > 0.30:
            swirl_t = (storm - 0.30) / 0.70
            target = int(swirl_t * 10)
            while len(self.wind_swirls) < target:
                self._spawn_wind_swirl(swirl_t, phase)
        for sw_ in self.wind_swirls:
            sw_.update(dt)
        self.wind_swirls = [sw_ for sw_ in self.wind_swirls
                             if not sw_.off_screen()]

        # Lightning (only in night window)
        if lightning_active(phase):
            self.next_strike -= dt
            if self.next_strike <= 0 and self.flash_remaining <= 0:
                self.flash_remaining = 0.18
                self.next_strike = random.uniform(6.0, 12.0)
                audio.play_thunder()
        else:
            self.next_strike = max(self.next_strike, random.uniform(4.0, 9.0))
        if self.flash_remaining > 0:
            self.flash_remaining = max(0.0, self.flash_remaining - dt)

        # Sandstorm motes — drifting sand specks blowing across the
        # playfield once the storm starts encroaching (s>0.22).
        sand = sand_intensity(phase)
        if sand > 0.22:
            target = int((sand - 0.22) / 0.78 * 120)
            while len(self.sand_motes) < target:
                self.sand_motes.append(_SandMote())
        for m in self.sand_motes:
            m.update(dt)
        self.sand_motes = [m for m in self.sand_motes if not m.off_screen()]

    def _spawn_streak(self, intensity, color):
        x = random.uniform(-20, W + 20)
        y = random.uniform(-80, -4)
        vx = -60 - intensity * 60
        vy = 420 + intensity * 220
        length = 10 + int(intensity * 14)
        self.streaks.append(_Streak(x, y, vx, vy, length, color))

    def _spawn_leaf(self, wind):
        x = -10
        y = random.uniform(60, GROUND_Y - 60)
        vx = 80 + wind * 40 + random.uniform(-15, 30)
        vy = random.uniform(-15, 40)
        hue = random.choice((
            (255, 210, 100),
            (245, 180, 80),
            (220, 140, 60),
            (230, 200, 120),
        ))
        self.leaves.append(_Leaf(x, y, vx, vy, hue))

    def _spawn_wind_streak(self, streak_t, phase):
        """Driven-snow streak — TAILWIND direction. Spawns at the
        left edge (or above-left) and races RIGHTWARD + slightly
        down across the canvas. Length, speed, alpha scale with
        `streak_t`."""
        if random.random() < 0.6:
            x = -random.uniform(0, 20)
            y = random.uniform(20, GROUND_Y - 40)
        else:
            x = random.uniform(-20, W * 0.6)
            y = random.uniform(-30, 0)
        vx = (360 + streak_t * 260) + random.uniform(0, 90)
        vy = 50 + random.uniform(-10, 45)
        length = int(12 + streak_t * 18)
        alpha = int(150 + streak_t * 70)
        wobble_amp = random.uniform(1.5, 3.5)
        wobble_freq = random.uniform(8.0, 13.0)
        self.wind_streaks.append(
            _WindStreak(x, y, vx, vy, length, _WHITE, alpha,
                        wobble_amp=wobble_amp,
                        wobble_freq=wobble_freq))

    def _spawn_wind_drift(self, drift_t, phase):
        """Big soft foreground snowflake — slow, near, slightly
        transparent (parallax depth against the smaller flakes)."""
        x = -random.uniform(0, 30)
        y = random.uniform(-10, GROUND_Y - 20)
        vx = (60 + drift_t * 70) + random.uniform(0, 30)
        vy = 25 + random.uniform(0, 30)
        radius = int(6 + drift_t * 5)        # 6..11 px
        alpha = int(60 + drift_t * 50)       # 60..110
        self.wind_drifts.append(
            _WindDrift(x, y, vx, vy, radius, _WHITE, alpha))

    def _spawn_wind_swirl(self, swirl_t, phase):
        """Turbulence curl — a small white snow eddy drifting
        RIGHTWARD with the tailwind. Sizes bimodal."""
        x = -random.uniform(0, 20)
        y = random.uniform(40, GROUND_Y - 60)
        vx = (110 + swirl_t * 90) + random.uniform(0, 40)
        vy = random.uniform(-10, 14)
        size_pick = random.random()
        if size_pick < 0.15:
            size = random.randint(12, 16)
        elif size_pick < 0.45:
            size = random.randint(5, 7)
        else:
            size = random.randint(8, 11)
        alpha = int(120 + swirl_t * 80)
        rot_rate = random.choice((-1.0, 1.0)) * random.uniform(0.8, 1.8)
        life = random.uniform(1.4, 2.2)
        self.wind_swirls.append(
            _WindSwirl(x, y, vx, vy, size, _WHITE, alpha,
                        rot_rate, life))

    def _spawn_wind_dust(self, dust_t, phase):
        """Small-to-medium snowflake — the bulk of the snow field,
        drifting RIGHTWARD + down with the tailwind."""
        x = -random.uniform(0, 15)
        y = random.uniform(-10, GROUND_Y - 10)
        vx = (140 + dust_t * 140) + random.uniform(0, 50)
        vy = 35 + random.uniform(0, 45)
        radius = random.randint(2, 6)
        alpha = int(150 + dust_t * 90)
        self.wind_dust.append(
            _WindDust(x, y, vx, vy, radius, _WHITE, alpha))

    def draw(self, surf):
        # Rain
        for s in self.streaks:
            s.draw(surf)
        # Cold atmospheric wash for the snow squall — a full-screen
        # blue-grey overlay whose alpha tracks the storm envelope,
        # so the scene cools as the snow builds and warms back as it
        # fades. Drawn here (after pillars, before the snow + before
        # the bird/coins which render later in the scene) so the
        # background chills while Pip + collectibles stay vivid.
        storm = storm_intensity(self.phase)
        if storm > 0.01:
            a = int(SNOW_TINT_PEAK_A * storm)
            if a > 0:
                wash = pygame.Surface((W, H), pygame.SRCALPHA)
                wash.fill((*SNOW_TINT, a))
                surf.blit(wash, (0, 0))
        # Snow layers — back-to-front for parallax depth:
        # big drift flakes → bulk flakes → driven streaks →
        # turbulence curls.
        for wd in self.wind_drifts:
            wd.draw(surf)
        for du in self.wind_dust:
            du.draw(surf)
        for ws in self.wind_streaks:
            ws.draw(surf)
        for sw_ in self.wind_swirls:
            sw_.draw(surf)
        # Leaves (drawn after wind so they layer on top — they're
        # the largest, most-readable foreground element)
        for lf in self.leaves:
            lf.draw(surf)
        # Lightning flash — additive white-blue pulse
        if self.flash_remaining > 0:
            t = self.flash_remaining / 0.18
            alpha = int(180 * t)
            flash = pygame.Surface((W, H), pygame.SRCALPHA)
            flash.fill((210, 220, 255, alpha))
            surf.blit(flash, (0, 0))

    # ── sandstorm passes (called around the bird in scenes.py) ──────────
    def draw_far(self, surf):
        """Distant haboob wall + dust-devils on the horizon. Drawn
        BEFORE the mountains so the storm sits behind the peaks
        during the long tease. Wall is cached per intensity bucket."""
        s = sand_intensity(self.phase)
        if s <= 0.02:
            self._sand_far_cache = None
            return
        bucket = round(s * 20) / 20.0
        if self._sand_far_cache is None or self._sand_far_cache[0] != bucket:
            self._sand_far_cache = (
                bucket, _render_sand_wall(bucket, "far", hash(("far", bucket)) & 0xffff))
        surf.blit(self._sand_far_cache[1], (0, 0))

    def draw_front(self, surf):
        """Foreground sandstorm: warm-haze visibility veil + mountain
        bury + the engulfing wall + drifting motes. Drawn AFTER the
        bird so the sand veils Pip + the course (Pip behind the
        sand), but before the HUD."""
        s = sand_intensity(self.phase)
        if s <= 0.02:
            self._sand_front_cache = None
            return
        # warm haze cast + visibility veil (faint in the tease,
        # ramping to the peak; right/leading edge heavier).
        haze = pygame.Surface((W, H), pygame.SRCALPHA)
        for xx in range(0, W, 2):
            fx = xx / W
            a = int(s * (70 + fx * 90))
            pygame.draw.rect(haze, (*SAND_HAZE, a), (xx, 0, 2, H))
        surf.blit(haze, (0, 0))
        # mountain bury wash over the lower scene
        if s >= 0.30:
            t = (s - 0.30) / 0.70
            band = pygame.Surface((W, GROUND_Y - (SAND_HORIZON - 24)),
                                  pygame.SRCALPHA)
            band.fill((*SAND_HAZE, int(150 * t)))
            surf.blit(band, (0, SAND_HORIZON - 24))
        # foreground engulfing wall (cached; only meaningful s>0.4)
        if s > 0.40:
            bucket = round(s * 20) / 20.0
            if self._sand_front_cache is None or self._sand_front_cache[0] != bucket:
                self._sand_front_cache = (
                    bucket, _render_sand_wall(bucket, "front",
                                              hash(("front", bucket)) & 0xffff))
            surf.blit(self._sand_front_cache[1], (0, 0))
        else:
            self._sand_front_cache = None
        # drifting motes in front
        for m in self.sand_motes:
            m.draw(surf)
