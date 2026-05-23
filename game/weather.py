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


def wind_intensity(phase: float) -> float:
    """Two bumps:
      - Golden-hour calm breeze (phase 0.18, gentle leaf drift, no
        gameplay effect)
      - Predawn HEADWIND event (phase 0.85, peak storm wind that
        pushes Pip leftward + slows the world scroll). Includes a
        ~8-second plateau at peak (phase 0.8375-0.8625) so the
        climax feels sustained rather than instantaneous — the
        smoothstep bump is scaled by 1.045 then clamped at 1.0,
        which flattens the top while keeping the ramps smooth.
    Returned value is clamped 0..1 and serves both as a particle
    spawn multiplier (Weather.update reads it for leaves + wind
    streaks) and as the gameplay-effect scalar (World reads it for
    bird.wind_lean + scroll slowdown)."""
    calm  = _bump(phase, 0.18, 0.10) * 0.35   # ambient golden-hour breeze
    # Storm bump with peak plateau: 1.045× scaling makes the
    # smoothstep saturate at the top across a phase-width 0.025
    # window (= 8 s of cycle), giving the climax visible duration.
    storm = min(1.0, _bump(phase, 0.85, 0.10) * 1.045)
    return max(0.0, min(1.0, calm + storm))


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
    """Mid-ground fast streak racing leftward, used as the primary
    visual cue for the predawn headwind event. Length, speed and
    spawn-rate all scale with wind intensity. Drawn as a TAPERED
    motion-blur trail: multiple short segments along the streak
    length, alphas fading from 0 at the head/tail to peak in the
    middle. The streak's flight path is a gentle sine wobble so
    the trail curves rather than running dead straight — the eye
    reads that as wind, not rain."""
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
    """Background slow drift — long soft semi-transparent streaks
    scrolling at ~1/3 the speed of `_WindStreak` to give parallax
    depth. No bright core, just a wide blurred body. Spawns at
    the gentlest wind threshold so the sky-in-motion feeling
    arrives BEFORE the strong fast streaks."""
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
        return self.x > W + 60 or self.y > GROUND_Y or self.y < -40

    def draw(self, surf):
        # Painted as a tapered horizontal blur: 3 stacked semi-
        # transparent lines of different widths and offsets to
        # approximate a wide soft brush stroke.
        tail_x = self.x - self.len
        tail_y = self.y
        x1, y1 = int(self.x), int(self.y)
        x2, y2 = int(tail_x), int(tail_y)
        ox = min(x1, x2) - 4
        oy = min(y1, y2) - 4
        sw = abs(x2 - x1) + 8
        sh = max(8, abs(y2 - y1) + 8)
        sub = pygame.Surface((sw, sh), pygame.SRCALPHA)
        # 3 stacked widths for a soft falloff
        for w, a_mul in ((4, 0.35), (3, 0.65), (2, 1.00)):
            a = int(self.alpha * a_mul)
            pygame.draw.line(sub, (*self.color, a),
                             (x1 - ox, y1 - oy), (x2 - ox, y2 - oy), w)
        surf.blit(sub, (ox, oy))


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
    """Tiny 1-2 px specks racing leftward fast. Provides the
    'lots of small stuff in the air' textural density that turns
    a few visible streaks into a sky full of wind. Fastest layer
    of the four (parallax foreground)."""
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
        return self.x > W + 10 or self.y > GROUND_Y or self.y < -20

    def draw(self, surf):
        # Tiny dot with a 2-px tail painted as a 1-px line for
        # speed-feel — at 400-600 px/s the eye registers a streak,
        # not a static dot.
        tail = max(2, int(self.size * 1.5))
        x1 = int(self.x);  y1 = int(self.y)
        x2 = x1 - tail;    y2 = y1
        sw = tail + 4
        sh = max(4, self.size + 4)
        sub = pygame.Surface((sw, sh), pygame.SRCALPHA)
        pygame.draw.line(sub, (*self.color, self.alpha),
                         (sw - 2, sh // 2),
                         (sw - 2 - tail, sh // 2), self.size)
        surf.blit(sub, (x1 - sw + 2, y1 - sh // 2))


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

        # Wind leaves
        wind = wind_intensity(phase)
        if wind > 0:
            target = int(wind * 10)
            while len(self.leaves) < target:
                self._spawn_leaf(wind)
            for lf in self.leaves:
                lf.update(dt)
            self.leaves = [lf for lf in self.leaves if not lf.off_screen()]
        else:
            self.leaves = []

        # Wind event — four layered particle types for parallax
        # depth and atmospheric richness. Each layer gates in at a
        # different intensity threshold so the buildup reads as
        # "more types of wind appearing" rather than just denser:
        #   wind > 0.10  drift (slow background) + dust (specks)
        #   wind > 0.15  streaks (mid-ground fast trails)
        #   wind > 0.30  swirls (iconic cartoon-wind cue)

        # Layer A: background slow drift — appears earliest, sets
        # the atmospheric mood before anything else gets dense.
        if wind > 0.10:
            drift_t = (wind - 0.10) / 0.90
            target = int(drift_t * 25)
            while len(self.wind_drifts) < target:
                self._spawn_wind_drift(drift_t, phase)
        for wd in self.wind_drifts:
            wd.update(dt)
        self.wind_drifts = [wd for wd in self.wind_drifts
                             if not wd.off_screen()]

        # Layer D: dust specks — same threshold as drift, very
        # high density at peak (120 specks), provides textural
        # foreground depth.
        if wind > 0.10:
            dust_t = (wind - 0.10) / 0.90
            target = int(dust_t * 120)
            while len(self.wind_dust) < target:
                self._spawn_wind_dust(dust_t, phase)
        for du in self.wind_dust:
            du.update(dt)
        self.wind_dust = [du for du in self.wind_dust
                          if not du.off_screen()]

        # Layer B: mid-ground fast streaks (the visual headline).
        if wind > 0.15:
            streak_t = (wind - 0.15) / 0.85
            target = int(streak_t * 60)
            while len(self.wind_streaks) < target:
                self._spawn_wind_streak(streak_t, phase)
        for ws in self.wind_streaks:
            ws.update(dt)
        self.wind_streaks = [ws for ws in self.wind_streaks
                             if not ws.off_screen()]

        # Layer C: swirls — the iconic cartoon-wind cue, only
        # appears mid-build onward. Lower density (12 at peak) so
        # each swirl reads as a deliberate shape, not visual mush.
        if wind > 0.30:
            swirl_t = (wind - 0.30) / 0.70
            target = int(swirl_t * 12)
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

    def _wind_palette(self, phase):
        """Tint that drifts from cool predawn (0.75) to warm
        sunrise (0.95) across the wind event. Returns one of a
        small palette per call so successive particles vary
        slightly within the current biome moment."""
        # Drift 0.75 → 0.95 mapped to 0..1
        t = max(0.0, min(1.0, (phase - 0.75) / 0.20))
        # Cool slate cyan → warm peach-cream
        cool = (180, 200, 235)
        warm = (220, 215, 200)
        base_r = int(cool[0] + (warm[0] - cool[0]) * t)
        base_g = int(cool[1] + (warm[1] - cool[1]) * t)
        base_b = int(cool[2] + (warm[2] - cool[2]) * t)
        # 4 small variations around the base — saturate/desat for
        # natural per-particle variety
        return random.choice((
            (base_r,           base_g,           base_b),
            (base_r - 10,      base_g - 5,       base_b - 5),
            (min(255, base_r + 15), min(255, base_g + 10), min(255, base_b + 10)),
            (base_r - 5,       base_g + 5,       base_b + 5),
        ))

    def _spawn_wind_streak(self, streak_t, phase):
        """Mid-ground fast streak — TAILWIND direction. Spawns at
        the left edge (or above-left) and races RIGHTWARD across
        the canvas, suggesting wind blowing in the direction of
        Pip's travel. Length, speed, alpha scale with `streak_t`."""
        # 60% spawn at left edge, 40% from above-left (storm
        # blowing in diagonally from upper-left)
        if random.random() < 0.6:
            x = -random.uniform(0, 20)
            y = random.uniform(20, GROUND_Y - 40)
        else:
            x = random.uniform(-20, W * 0.6)
            y = random.uniform(-30, 0)
        vx = (320 + streak_t * 220) + random.uniform(0, 80)
        vy = 30 + random.uniform(-10, 40)
        length = int(12 + streak_t * 18)
        col = self._wind_palette(phase)
        alpha = int(120 + streak_t * 110)
        wobble_amp = random.uniform(1.5, 3.5)
        wobble_freq = random.uniform(8.0, 13.0)
        self.wind_streaks.append(
            _WindStreak(x, y, vx, vy, length, col, alpha,
                        wobble_amp=wobble_amp,
                        wobble_freq=wobble_freq))

    def _spawn_wind_drift(self, drift_t, phase):
        """Background slow drift — long soft RIGHTWARD streaks."""
        x = -random.uniform(0, 30)
        y = random.uniform(10, GROUND_Y - 30)
        vx = (110 + drift_t * 70) + random.uniform(0, 30)
        vy = random.uniform(-5, 15)
        length = int(30 + drift_t * 20)
        col = self._wind_palette(phase)
        alpha = int(50 + drift_t * 50)
        self.wind_drifts.append(
            _WindDrift(x, y, vx, vy, length, col, alpha))

    def _spawn_wind_swirl(self, swirl_t, phase):
        """Iconic cartoon-wind cue — drifts RIGHTWARD with the
        tailwind. Sizes bimodal (small/medium/big feature)."""
        x = -random.uniform(0, 20)
        y = random.uniform(40, GROUND_Y - 60)
        vx = (100 + swirl_t * 80) + random.uniform(0, 30)
        vy = random.uniform(-10, 10)
        size_pick = random.random()
        if size_pick < 0.15:
            size = random.randint(14, 18)
        elif size_pick < 0.45:
            size = random.randint(5, 7)
        else:
            size = random.randint(8, 12)
        col = self._wind_palette(phase)
        alpha = int(140 + swirl_t * 80)
        rot_rate = random.choice((-1.0, 1.0)) * random.uniform(0.8, 1.8)
        life = random.uniform(1.4, 2.2)
        self.wind_swirls.append(
            _WindSwirl(x, y, vx, vy, size, col, alpha,
                        rot_rate, life))

    def _spawn_wind_dust(self, dust_t, phase):
        """Tiny specks racing RIGHTWARD fast — foreground texture."""
        x = -random.uniform(0, 15)
        y = random.uniform(5, GROUND_Y - 10)
        vx = (380 + dust_t * 220) + random.uniform(0, 40)
        vy = random.uniform(-10, 25)
        size = random.choice((1, 1, 2))
        col = self._wind_palette(phase)
        alpha = int(80 + dust_t * 80)
        self.wind_dust.append(
            _WindDust(x, y, vx, vy, size, col, alpha))

    def draw(self, surf):
        # Rain
        for s in self.streaks:
            s.draw(surf)
        # Wind layers — drawn back-to-front for parallax depth:
        # background drift → dust specks → mid streaks → foreground
        # swirls. Same painter's-order rule the rest of the scene
        # already follows.
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
