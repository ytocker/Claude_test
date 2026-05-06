"""Sparse ambient background scenes — distant flocks, distant fireworks, etc.

These are RARE punctuating events tied to biome phase (golden hour, night).
Each event has a hard cooldown and a one-at-a-time cap so they enrich the
world without crowding the screen. The intent: a player gets one or two
of these per run, not a constant parade.
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

_FLOCK_COOLDOWN_S = 75.0
_FIREWORKS_COOLDOWN_S = 110.0

# Initial delay before the FIRST event of each kind in a run (avoids
# popping one in the first 5 seconds while the player is still finding
# their flap rhythm).
_FLOCK_INITIAL_DELAY = (15.0, 35.0)
_FIREWORKS_INITIAL_DELAY = (30.0, 60.0)


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


# ── Controller ───────────────────────────────────────────────────────────────

class AmbientScenes:
    """Sparse ambient event director.

    One V-flock max + one fireworks set max active at any time. Each kind
    has a phase window and a cooldown; outside the window the cooldown
    counter pauses (no spawning until phase re-enters the window).
    """

    def __init__(self):
        self.flock: _VFlock | None = None
        self.fireworks: _Fireworks | None = None
        self._flock_cool = random.uniform(*_FLOCK_INITIAL_DELAY)
        self._fireworks_cool = random.uniform(*_FIREWORKS_INITIAL_DELAY)

    @staticmethod
    def _in_window(phase: float, windows) -> bool:
        return any(lo <= phase <= hi for lo, hi in windows)

    def update(self, dt: float, phase: float, palette: dict) -> None:
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

    def draw(self, surf: pygame.Surface) -> None:
        if self.flock is not None:
            self.flock.draw(surf)
        if self.fireworks is not None:
            self.fireworks.draw(surf)
