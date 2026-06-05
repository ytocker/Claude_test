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

from game.config import (W, H, GROUND_Y,
                         WEATHER_SNOW_ACCUM_RATE, WEATHER_SNOW_MELT_RATE)
from game import audio


# ── Storm anchor: shift the rain + lightning phase window so the
# drizzle's lower edge lands at config.RAIN_START_PILLAR. The shift is
# derived from the same onboarding-ramp dwell math World.update
# interpolates over, so the storm lands at the chosen pillar no matter
# how the ramp constants are tuned. Only the rain/lightning curves use
# this — the snow squall, morning thermal, and calm breeze keep their
# original anchors.

def _phase_for_pillar(pillar: int) -> float:
    """Cumulative biome phase elapsed to reach `pillar`, mirroring what
    the game ACTUALLY does (not the simpler inter-pillar dwell math the
    older plotter used).

    Pillar 1 is special: it's seeded at `W + 60 + SPAWN_GRACE * SCROLL_BASE`
    by `_seed_first_pipes`, then has to scroll all the way to `BIRD_X − PIPE_W`
    before scoring fires. That seeded travel is ~1.14 s longer than a normal
    inter-pillar dwell, and the previous formula didn't account for it —
    so phase-for-pillar was ~0.6 pillars off the real gameplay axis.

    Pillars 2..N then use the inter-pillar dwell `_current_spacing() /
    _current_scroll()`, with `_ramp_t()` computed at `pillars_passed =
    pp_after_previous_score` (which matches the live game). Phase is
    unwrapped — values above 1.0 are possible if `pillar` exceeds one
    biome cycle. Imports live here so a stale weather import never
    touches `game.config`'s heavier module at top-level."""
    from game.config import (
        PLATEAU_PIPES, RAMP_PIPES,
        PIPE_SPACING, PIPE_SPACING_NEWBIE,
        SCROLL_BASE, SCROLL_NEWBIE_BASE,
        SPAWN_GRACE, BIRD_X, PIPE_W, W,
    )
    from game.biome import CYCLE_SECONDS
    if pillar <= 0:
        return 0.0
    # First-pillar seeded travel (plateau scroll).
    seeded_x = W + 60 + int(SPAWN_GRACE * SCROLL_BASE)
    travel = seeded_x - BIRD_X - PIPE_W
    t = travel / SCROLL_NEWBIE_BASE
    # Inter-pillar dwells for pillars 2..pillar.
    for pp in range(1, int(pillar)):
        if pp < PLATEAU_PIPES:
            ramp_t = 0.0
        else:
            denom = max(1, RAMP_PIPES - PLATEAU_PIPES)
            x = min(1.0, (pp - PLATEAU_PIPES) / denom)
            ramp_t = 1.0 - (1.0 - x) ** 2
        spacing = (PIPE_SPACING_NEWBIE
                   + (PIPE_SPACING - PIPE_SPACING_NEWBIE) * ramp_t)
        scroll = (SCROLL_NEWBIE_BASE
                  + (SCROLL_BASE - SCROLL_NEWBIE_BASE) * ramp_t)
        t += spacing / scroll
    return t / CYCLE_SECONDS


# Baseline drizzle-start phase before any shift (the original literal).
_RAIN_DRIZZLE_START_BASE = 0.32
# Baseline snow-squall lower edge before any shift (center 0.85 − width
# 0.10 — the original literal where storm_intensity first goes non-zero).
_SNOW_LOWER_EDGE_BASE = 0.75

# Resolved at import time so all downstream constants are stable.
from game.config import (RAIN_START_PILLAR as _RAIN_START_PILLAR,
                         SNOW_START_PILLAR as _SNOW_START_PILLAR)
_RAIN_PHASE_SHIFT = (_phase_for_pillar(_RAIN_START_PILLAR)
                     - _RAIN_DRIZZLE_START_BASE)
_SNOW_PHASE_SHIFT = (_phase_for_pillar(_SNOW_START_PILLAR)
                     - _SNOW_LOWER_EDGE_BASE)

# Module-level rain + lightning phase constants. Each is the original
# literal + _RAIN_PHASE_SHIFT where applicable; widths stay the same.
RAIN_DRIZZLE_START   = _RAIN_DRIZZLE_START_BASE + _RAIN_PHASE_SHIFT
RAIN_DRIZZLE_PEAK    = 0.42 + _RAIN_PHASE_SHIFT
RAIN_DRIZZLE_END     = 0.50 + _RAIN_PHASE_SHIFT
RAIN_STORM_PEAK      = 0.50 + _RAIN_PHASE_SHIFT
RAIN_STORM_WIDTH     = 0.08
RAIN_COLOR_T_START   = 0.35 + _RAIN_PHASE_SHIFT
RAIN_COLOR_T_RANGE   = 0.20
LIGHTNING_PHASE_MIN  = 0.49 + _RAIN_PHASE_SHIFT
LIGHTNING_PHASE_MAX  = 0.58 + _RAIN_PHASE_SHIFT
# Phase at which the rain block fully clears (storm peak + its half-width).
# A run opens here so play begins exactly as the rain ends — see
# World.__init__.
RAIN_END             = RAIN_STORM_PEAK + RAIN_STORM_WIDTH

# Snow squall (shifted by config.SNOW_START_PILLAR).
SNOW_STORM_CENTER    = 0.85 + _SNOW_PHASE_SHIFT
SNOW_STORM_WIDTH     = 0.13


# ── phase → intensity curves ────────────────────────────────────────────────

def _bump(phase: float, center: float, width: float) -> float:
    """Smooth bump peaking at `center` and fading over ±width. Returns 0..1."""
    d = abs(((phase - center + 0.5) % 1.0) - 0.5)
    if d >= width:
        return 0.0
    t = 1.0 - d / width
    return t * t * (3 - 2 * t)  # smoothstep


def _skew_bump(phase: float, start: float, peak: float, end: float) -> float:
    """Asymmetric bump: 0 outside [start, end], a smoothstep RISE from start→peak
    and a smoothstep FALL from peak→end. A long rise + short fall gives a long
    buildup and a short fade. Returns 0..1."""
    if phase <= start or phase >= end:
        return 0.0
    if phase <= peak:
        u = (phase - start) / (peak - start)
    else:
        u = (end - phase) / (end - peak)
    return u * u * (3 - 2 * u)


def rain_intensity(phase: float) -> float:
    """Drizzle build → dusk thunderstorm peak → fade. The entire block
    is anchored to `config.RAIN_START_PILLAR` via `_RAIN_PHASE_SHIFT`
    above — the drizzle's lower edge lands at that pillar's biome
    phase, then the original shape (long buildup + storm peak + short
    fade) plays out from there."""
    a = _skew_bump(phase, RAIN_DRIZZLE_START, RAIN_DRIZZLE_PEAK,
                   RAIN_DRIZZLE_END) * 0.35
    b = _bump(phase, RAIN_STORM_PEAK, RAIN_STORM_WIDTH) * 1.00
    return max(0.0, min(1.0, a + b))


def rain_color(phase: float):
    """Always blue/grey-dominant raindrops, shifting only slightly with the
    sky — a faintly warm-lit blue at the early drizzle, a deeper slate-blue
    at the storm peak. Anchors to the shifted rain block via
    `RAIN_COLOR_T_START` so the warm→cool crossfade always lines up with
    the storm peak no matter where `RAIN_START_PILLAR` puts it."""
    warm = (180, 192, 220)   # early-drizzle lit, still clearly blue-dominant
    cool = (135, 162, 212)   # cool slate-blue at the storm peak
    t_cool = min(1.0, max(0.0,
                          (phase - RAIN_COLOR_T_START) / RAIN_COLOR_T_RANGE))
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
    """The predawn SNOW SQUALL event — the single bump that drives the
    snow visuals, the cold atmospheric wash, AND the tailwind gameplay
    (Pip's forward push + scroll boost). The center is anchored to
    `config.SNOW_START_PILLAR` via `_SNOW_PHASE_SHIFT` above. A short
    plateau at the peak keeps the climax sustained: the smoothstep
    bump is scaled 1.045 then clamped at 1.0, flattening the top
    while the ramps stay smooth. 0 everywhere outside the snow
    window, so the golden-hour breeze (`calm_breeze`) never triggers
    snow."""
    return min(1.0, _bump(phase, SNOW_STORM_CENTER, SNOW_STORM_WIDTH)
               * 1.045)


def wind_intensity(phase: float) -> float:
    """Combined curve (calm breeze + storm) kept for any caller
    that wants the union. Snow visuals + gameplay use
    storm_intensity directly; leaves use calm_breeze."""
    return max(0.0, min(1.0, calm_breeze(phase) + storm_intensity(phase)))


def thermal_intensity(phase: float) -> float:
    """Morning thermals — warm rising air that scatters sinter rocks and
    spawns ground geysers giving Pip a continuous updraft. Asymmetric on
    purpose: a LONG buildup (~50→96s) and a SHORT fade (~96→112s). The curve
    is a pure scheduling signal (peak 1.0) read against two thresholds:
    rocks appear just above 0 (so they lead the event in sparse and thicken),
    while geysers only spawn above GEYSER_SPAWN_THRESHOLD — so the rocks-only
    opening and rocks-only fade tail both fall out of this one signal. Geyser
    count and each geyser's duty-cycle also scale off it. Held off the opening
    (0 before ~50s) so the player feels the base game first; 0 outside the
    window. Cycle = 320s, so 50/96/112s → phases 0.15625/0.30/0.35."""
    return _skew_bump(phase, 50.0 / 320.0, 96.0 / 320.0, 112.0 / 320.0)


# Cold wash colour for the snow squall. The wash starts as a deep
# blue-grey (cooling the scene so flakes pop) and trends toward a soft,
# cool snowy white at the storm peak — a MODERATE wash (peak alpha ~half)
# that reads as weather rather than a screen-filling whiteout.
SNOW_TINT = (74, 96, 130)
SNOW_TINT_WHITE = (205, 218, 235)
SNOW_TINT_PEAK_A = 128
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


# ── particle: a single rain streak ──────────────────────────────────────────

class _Streak:
    __slots__ = ("x", "y", "vx", "vy", "len", "color", "intensity")

    def __init__(self, x, y, vx, vy, length, color, intensity):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.len = length
        self.color = color
        self.intensity = intensity

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def off_screen(self):
        return self.y > GROUND_Y or self.x < -8 or self.x > W + 8

    def draw(self, surf):
        dx = self.vx / max(1.0, abs(self.vy)) * self.len
        dy = self.len
        hx, hy = int(self.x), int(self.y)
        # Light drizzle reads as a clean thin streak; the dramatic 2px-line +
        # bright teardrop head only kicks in at the heavy thunderstorm peak.
        width = 2 if self.intensity >= 0.5 else 1
        pygame.draw.line(surf, self.color, (hx, hy),
                         (int(self.x - dx), int(self.y - dy)), width)
        if self.intensity >= 0.7:
            c = self.color
            head = (min(255, c[0] + 42), min(255, c[1] + 36),
                    min(255, c[2] + 26))
            pygame.draw.circle(surf, head, (hx, hy), 2)


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

        # Accumulated snow squall cover (0..1) — the single source of truth for
        # both the screen whiteout and Pip's burial (read in world). Persists
        # across frames so the wash builds and holds rather than tracking the
        # raw storm envelope symmetrically.
        self.snow_cover: float = 0.0

        # Lightning state: countdown to next strike, and flash envelope 0..1.
        self.flash_remaining: float = 0.0
        self.next_strike: float = random.uniform(4.0, 9.0)

    def update(self, dt, phase):
        self.phase = phase

        # Snow squall cover on Pip — a UNIFORM (constant-rate) build the whole
        # time it's actively snowing, so the max lands near the END of the squall
        # rather than at its peak, then a FASTER defrost once the storm is over.
        # Gated on storm_intensity (exactly 0 outside the window) so there is no
        # phase-wrap math: accumulate while it snows, melt only once it stops.
        wi = storm_intensity(phase)
        if wi > 0.0:
            self.snow_cover = min(1.0, self.snow_cover + WEATHER_SNOW_ACCUM_RATE * dt)
        else:
            self.snow_cover = max(0.0, self.snow_cover - WEATHER_SNOW_MELT_RATE * dt)

        # Rain
        intensity = rain_intensity(phase)
        if intensity > 0:
            color = rain_color(phase)
            target = int(80 + intensity * 170)   # heavier downpour for the storm climax
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
            target = int(drift_t * 40)
            while len(self.wind_drifts) < target:
                self._spawn_wind_drift(drift_t, phase)
        for wd in self.wind_drifts:
            wd.update(dt)
        self.wind_drifts = [wd for wd in self.wind_drifts
                             if not wd.off_screen()]

        # Bulk snowflakes — dense at peak (the body of the squall).
        if storm > 0.10:
            dust_t = (storm - 0.10) / 0.90
            target = int(dust_t * 260)
            while len(self.wind_dust) < target:
                self._spawn_wind_dust(dust_t, phase)
        for du in self.wind_dust:
            du.update(dt)
        self.wind_dust = [du for du in self.wind_dust
                          if not du.off_screen()]

        # Driven-snow streaks (the wind-blown headline).
        if storm > 0.15:
            streak_t = (storm - 0.15) / 0.85
            target = int(streak_t * 90)
            while len(self.wind_streaks) < target:
                self._spawn_wind_streak(streak_t, phase)
        for ws in self.wind_streaks:
            ws.update(dt)
        self.wind_streaks = [ws for ws in self.wind_streaks
                             if not ws.off_screen()]

        # Turbulence curls — small white eddies, peak only.
        if storm > 0.30:
            swirl_t = (storm - 0.30) / 0.70
            target = int(swirl_t * 14)
            while len(self.wind_swirls) < target:
                self._spawn_wind_swirl(swirl_t, phase)
        for sw_ in self.wind_swirls:
            sw_.update(dt)
        self.wind_swirls = [sw_ for sw_ in self.wind_swirls
                             if not sw_.off_screen()]

        # Full-screen lightning flash — fires a few times spread across the
        # dusk THUNDERSTORM, gated to open only once the rain is heavy (near
        # the peak) so the earlier light drizzle stays flash-free. The long
        # interval lands ~3 flashes over the storm; the storm-jolt strike on
        # Pip adds its own flash near the peak. Gate tracks the shifted rain
        # block via the module-level LIGHTNING_PHASE_* constants so moving
        # RAIN_START_PILLAR also moves the lightning window in lockstep.
        storming = LIGHTNING_PHASE_MIN <= phase <= LIGHTNING_PHASE_MAX
        if storming:
            self.next_strike -= dt
            if self.next_strike <= 0 and self.flash_remaining <= 0:
                self.flash_remaining = 0.18
                self.next_strike = random.uniform(22.0, 34.0)
                audio.play_thunder()
        else:
            self.next_strike = max(self.next_strike, random.uniform(8.0, 16.0))
        if self.flash_remaining > 0:
            self.flash_remaining = max(0.0, self.flash_remaining - dt)

    def _spawn_streak(self, intensity, color):
        # Spawn across the WHOLE field (not just above the top edge): a
        # top-only seed leaves the lower screen bare on the first frames and
        # under the gentle slant, so a full-field respawn keeps coverage even.
        x = random.uniform(-20, W + 20)
        y = random.uniform(-30, GROUND_Y)
        vx = -60 - intensity * 60            # GENTLE slant (not the steep V2 wind)
        vy = 420 + intensity * 220
        length = 12 + int(intensity * 18)
        self.streaks.append(_Streak(x, y, vx, vy, length, color, intensity))

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
        # Atmospheric wash for the snow squall — a full-screen overlay whose
        # alpha AND colour track storm_intensity, so the scene cools+whitens on
        # the rise, peaks WITH the storm, and clears exactly when the snowstorm
        # ends (no lingering hold). Colour trends from the cool blue-grey toward
        # a soft snowy white at the peak — a moderate wash that reads as weather,
        # not a blinding whiteout. Drawn here (after pillars, before the snow +
        # before the bird/coins which render later) so the background cools while
        # Pip + collectibles stay readable on top.
        wash_t = storm_intensity(self.phase)
        if wash_t > 0.01:
            a = int(SNOW_TINT_PEAK_A * wash_t)
            if a > 0:
                col = (int(SNOW_TINT[0] + (SNOW_TINT_WHITE[0] - SNOW_TINT[0]) * wash_t),
                       int(SNOW_TINT[1] + (SNOW_TINT_WHITE[1] - SNOW_TINT[1]) * wash_t),
                       int(SNOW_TINT[2] + (SNOW_TINT_WHITE[2] - SNOW_TINT[2]) * wash_t))
                wash = pygame.Surface((W, H), pygame.SRCALPHA)
                wash.fill((*col, a))
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
