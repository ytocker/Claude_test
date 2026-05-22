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
    """Fast horizontal-ish streak racing leftward, used as the
    visual cue for the predawn headwind event. Length, speed and
    spawn-rate all scale with wind intensity — at low wind the
    streaks are few + short + slow; at peak they're dense + long
    + fast. Cool slate-cyan colour blends with the predawn sky."""
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
        return self.x < -30 or self.y > GROUND_Y or self.y < -20

    def draw(self, surf):
        # The streak is drawn AWAY FROM its current motion (so it
        # trails behind itself, leftward). Two-stroke render: a
        # thicker semi-transparent body + a brighter 1-px core.
        dx = -self.vx * 0.012   # tail extends opposite the motion
        dy = -self.vy * 0.012
        body_col = (*self.color, self.alpha)
        core_col = (255, 255, 255, min(255, self.alpha + 60))
        # Use SRCALPHA scratch so alpha actually blends
        x1 = int(self.x); y1 = int(self.y)
        x2 = int(self.x - dx); y2 = int(self.y - dy)
        # 2-px wide body
        sub = pygame.Surface(
            (abs(x2 - x1) + 4, abs(y2 - y1) + 4),
            pygame.SRCALPHA,
        )
        ox = min(x1, x2) - 2
        oy = min(y1, y2) - 2
        pygame.draw.line(sub, body_col,
                         (x1 - ox, y1 - oy), (x2 - ox, y2 - oy), 2)
        pygame.draw.line(sub, core_col,
                         (x1 - ox, y1 - oy), (x2 - ox, y2 - oy), 1)
        surf.blit(sub, (ox, oy))


# ── main Weather controller ────────────────────────────────────────────────

class Weather:
    def __init__(self):
        self.streaks: list[_Streak] = []
        self.leaves: list[_Leaf] = []
        # Wind streaks — only spawn at meaningful wind intensity
        # (predawn HEADWIND event, phase ~0.85). At the small
        # golden-hour breeze intensity these stay at 0.
        self.wind_streaks: list[_WindStreak] = []
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

        # Wind streaks — visible cue for the headwind event. Gate
        # at wind > 0.15 so the small golden-hour calm breeze
        # (peak ~0.35) shows leaves only, while the predawn storm
        # bump (peak ~1.00) gets the dramatic horizontal streaks
        # too. Streak count + speed both scale with wind so the
        # buildup→peak→fade reads clearly.
        if wind > 0.15:
            # Map wind 0.15..1.00 → streak_t 0..1 so streaks ramp
            # in from zero at the gate rather than appearing at
            # full density immediately.
            streak_t = (wind - 0.15) / 0.85
            target = int(streak_t * 60)
            while len(self.wind_streaks) < target:
                self._spawn_wind_streak(streak_t, phase)
            for ws in self.wind_streaks:
                ws.update(dt)
            self.wind_streaks = [ws for ws in self.wind_streaks
                                 if not ws.off_screen()]
        else:
            # Quickly drain any lingering streaks when wind drops
            # below the gate (cycle continues to scroll them off
            # via their own velocity each frame).
            for ws in self.wind_streaks:
                ws.update(dt)
            self.wind_streaks = [ws for ws in self.wind_streaks
                                 if not ws.off_screen()]

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

    def _spawn_wind_streak(self, streak_t, phase):
        """One fast leftward streak. Origin: right edge (or above
        the canvas, so streaks also enter from the top-right at an
        angle). Velocity, length, alpha all scale with `streak_t`
        (already pre-mapped 0..1 from the wind intensity gate so
        the buildup reads smoothly)."""
        # 60% spawn at right edge, 40% from above-right (so the
        # storm looks like it's blowing in from upper-right)
        if random.random() < 0.6:
            x = W + random.uniform(0, 20)
            y = random.uniform(20, GROUND_Y - 40)
        else:
            x = random.uniform(W * 0.4, W + 20)
            y = random.uniform(-30, 0)
        # Leftward + slight downward
        vx = -(320 + streak_t * 220) - random.uniform(0, 80)
        vy = 30 + random.uniform(-10, 40)
        length = int(8 + streak_t * 14)
        # Cool slate-cyan, slightly varied per streak
        col = random.choice((
            (190, 210, 235),
            (170, 200, 230),
            (210, 220, 240),
            (200, 215, 245),
        ))
        alpha = int(120 + streak_t * 110)
        self.wind_streaks.append(
            _WindStreak(x, y, vx, vy, length, col, alpha))

    def draw(self, surf):
        # Rain
        for s in self.streaks:
            s.draw(surf)
        # Wind streaks (drawn after rain so they layer on top of
        # the drizzle when both happen to overlap, though normally
        # they don't — different cycle phases)
        for ws in self.wind_streaks:
            ws.draw(surf)
        # Leaves
        for lf in self.leaves:
            lf.draw(surf)
        # Lightning flash — additive white-blue pulse
        if self.flash_remaining > 0:
            t = self.flash_remaining / 0.18
            alpha = int(180 * t)
            flash = pygame.Surface((W, H), pygame.SRCALPHA)
            flash.fill((210, 220, 255, alpha))
            surf.blit(flash, (0, 0))
