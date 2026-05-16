"""Dynamic Wildflower Meadow — large flower-type pool, randomly drawn.

V3 ("Dynamic Meadow") is the headline design: every flower position picks
from a pool of 12 distinct flower types so the meadow never repeats.
V1, V2, V4, V5 keep their single-type identities for comparison against
the original choices.

Each ``draw_ground_vN`` is a drop-in replacement for
``game.draw.draw_ground``.
"""
from __future__ import annotations

import math
import random

import pygame


# ── shared palette ─────────────────────────────────────────────────────────

_GRASS_TOP = (90, 200, 80)
_GRASS_MID = (45, 145, 50)
_GRASS_DK = (25, 90, 35)
_DIRT_TOP = (95, 70, 45)
_DIRT_DEEP = (55, 38, 25)
_ROCK = (140, 130, 115)
_YELLOW_CENTER = (255, 220, 90)
_BLACK = (25, 15, 15)


# ── helpers ────────────────────────────────────────────────────────────────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, delta):
    return (_clamp(c[0] + delta), _clamp(c[1] + delta), _clamp(c[2] + delta))


def _lerp_color(a, b, t):
    return _mix(a, b, t)


def _brightness(c) -> float:
    return min(1.0, (c[0] + c[1] + c[2]) / 510.0)


def _warmth(c) -> float:
    return (c[0] - c[2]) / 255.0


def _vertical_gradient(surf, x0, y0, x1, y1, top, bot):
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / max(1, h - 1)
        c = _lerp_color(top, bot, t)
        pygame.draw.line(surf, c, (x0, y0 + i), (x1 - 1, y0 + i))


def _ambient_ground_overlay(surf, ground_y, w, h, mid_color):
    b = _brightness(mid_color)
    band = pygame.Surface((w, h - ground_y), pygame.SRCALPHA)
    if b < 0.6:
        alpha = int(160 * (0.6 - b))
        band.fill((mid_color[0] // 3, mid_color[1] // 3,
                   mid_color[2] // 3, alpha))
    w_amt = _warmth(mid_color)
    if w_amt > 0.05:
        alpha = int(min(85, w_amt * 220))
        warm = pygame.Surface((w, h - ground_y), pygame.SRCALPHA)
        warm.fill((255, 150, 90, alpha))
        band.blit(warm, (0, 0))
    surf.blit(band, (0, ground_y))


def _scatter(scroll, w, speed, step, seed_off):
    phase = scroll * speed
    first = int(phase // step) - 1
    last = int((phase + w) // step) + 2
    for k in range(first, last + 1):
        rng = random.Random((k * 2654435761 ^ seed_off) & 0xFFFFFFFF)
        wx = k * step + rng.uniform(-step * 0.25, step * 0.25)
        sx = int(wx - phase)
        if -20 < sx < w + 20:
            yield sx, k, rng


# ── accent creatures ───────────────────────────────────────────────────────

def _butterfly(surf, x, y, color):
    pygame.draw.circle(surf, color, (x - 1, y), 2)
    pygame.draw.circle(surf, color, (x + 2, y), 2)
    pygame.draw.line(surf, _BLACK, (x, y - 1), (x, y + 1), 1)


def _ladybug(surf, x, y):
    pygame.draw.ellipse(surf, (200, 30, 30), (x - 2, y - 1, 4, 3))
    pygame.draw.circle(surf, _BLACK, (x - 2, y), 1)
    pygame.draw.line(surf, _BLACK, (x, y - 1), (x, y + 1), 1)
    pygame.draw.circle(surf, _BLACK, (x - 1, y), 1)
    pygame.draw.circle(surf, _BLACK, (x + 1, y), 1)


def _bee(surf, x, y):
    pygame.draw.ellipse(surf, (245, 210, 70), (x - 2, y - 1, 4, 3))
    pygame.draw.line(surf, _BLACK, (x - 1, y - 1), (x - 1, y + 1), 1)
    pygame.draw.line(surf, _BLACK, (x + 1, y - 1), (x + 1, y + 1), 1)
    pygame.draw.line(surf, (235, 240, 255), (x - 1, y - 2), (x + 1, y - 2), 1)


# ── flower drawers ─────────────────────────────────────────────────────────
#
# All flowers share signature ``(surf, x, ground_y, rng)``.
# (x, ground_y) is the anchor point on the grass surface; the flower
# decides its own stem length so tall-vs-short variation is built in.
# This shape-variety is the heart of the dynamic-meadow feel.

_TULIP_COLORS = [(225, 65, 70), (240, 200, 70), (250, 130, 180),
                 (180, 100, 220), (245, 130, 60)]


def _f_tulip(surf, x, ground_y, rng):
    col = rng.choice(_TULIP_COLORS)
    base_y = ground_y + rng.randint(0, 4)
    bud_y = base_y - rng.randint(8, 12)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, bud_y + 1), 1)
    pygame.draw.line(surf, _GRASS_TOP, (x + 1, base_y), (x + 1, bud_y + 2), 1)
    pygame.draw.line(surf, _GRASS_DK,
                     (x, base_y - 3), (x + 3, base_y - 6), 1)
    pygame.draw.line(surf, _GRASS_TOP,
                     (x, base_y - 4), (x + 3, base_y - 7), 1)
    pygame.draw.line(surf, _shade(col, -40),
                     (x - 1, bud_y - 1), (x - 1, bud_y + 2), 1)
    pygame.draw.line(surf, col, (x, bud_y - 2), (x, bud_y + 2), 1)
    pygame.draw.line(surf, _shade(col, -40),
                     (x + 1, bud_y - 1), (x + 1, bud_y + 2), 1)
    pygame.draw.line(surf, _mix(col, (255, 255, 255), 0.6),
                     (x, bud_y - 1), (x, bud_y), 1)


def _f_daisy(surf, x, ground_y, rng):
    fy = ground_y + rng.randint(-2, 5)
    pygame.draw.line(surf, _GRASS_DK, (x, fy + 3), (x, fy), 1)
    white = (252, 250, 240)
    pygame.draw.circle(surf, white, (x - 1, fy), 1)
    pygame.draw.circle(surf, white, (x + 1, fy), 1)
    pygame.draw.circle(surf, white, (x, fy - 1), 1)
    pygame.draw.circle(surf, white, (x, fy + 1), 1)
    pygame.draw.circle(surf, white, (x - 1, fy - 1), 1)
    pygame.draw.circle(surf, _YELLOW_CENTER, (x, fy), 1)


def _f_poppy(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    fy = base_y - rng.randint(2, 5)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, fy + 1), 1)
    pygame.draw.circle(surf, (155, 30, 35), (x - 1, fy), 2)
    pygame.draw.circle(surf, (215, 50, 45), (x + 1, fy), 2)
    pygame.draw.circle(surf, (230, 70, 55), (x, fy - 1), 1)
    pygame.draw.circle(surf, _BLACK, (x, fy), 1)


def _f_lavender(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    height = rng.randint(9, 14)
    top_y = base_y - height
    pygame.draw.line(surf, (95, 135, 80), (x, base_y), (x, top_y), 1)
    spike_end = top_y + height // 2
    for sy in range(top_y, spike_end + 1):
        col = (180, 130, 220) if (sy - top_y) % 2 == 0 else (155, 105, 200)
        pygame.draw.circle(surf, col, (x, sy), 1)
        if rng.random() < 0.6:
            pygame.draw.circle(surf, _shade(col, -20), (x - 1, sy), 1)
        if rng.random() < 0.6:
            pygame.draw.circle(surf, _shade(col, -20), (x + 1, sy), 1)
    pygame.draw.circle(surf, (215, 175, 245), (x, top_y - 1), 1)


def _f_sunflower(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    head_y = base_y - rng.randint(10, 14)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, head_y + 2), 2)
    pygame.draw.line(surf, _GRASS_TOP, (x, base_y), (x, head_y + 2), 1)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y - 4), (x + 3, base_y - 6), 1)
    pygame.draw.line(surf, _GRASS_TOP, (x, base_y - 4), (x + 3, base_y - 5), 1)
    petal = (255, 200, 60)
    petal_hi = (255, 240, 130)
    for ang_deg in (0, 45, 90, 135, 180, 225, 270, 315):
        ang = math.radians(ang_deg)
        px = x + int(math.cos(ang) * 3)
        py = head_y + int(math.sin(ang) * 3)
        pygame.draw.circle(surf, petal, (px, py), 1)
    pygame.draw.circle(surf, petal_hi, (x - 2, head_y - 1), 1)
    pygame.draw.circle(surf, (120, 70, 30), (x, head_y), 2)
    pygame.draw.circle(surf, (60, 40, 20), (x, head_y), 1)


def _f_rose(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    bloom_y = base_y - rng.randint(3, 6)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, bloom_y + 1), 1)
    pygame.draw.line(surf, _GRASS_DK,
                     (x - 1, base_y - 2), (x - 3, base_y - 4), 1)
    pygame.draw.line(surf, _GRASS_TOP,
                     (x - 1, base_y - 2), (x - 3, base_y - 3), 1)
    is_pink = rng.random() < 0.5
    outer = (200, 60, 90) if is_pink else (160, 30, 35)
    mid = (240, 130, 170) if is_pink else (215, 50, 45)
    inner = (255, 200, 220) if is_pink else (240, 120, 110)
    pygame.draw.circle(surf, outer, (x, bloom_y), 3)
    pygame.draw.circle(surf, mid, (x, bloom_y), 2)
    pygame.draw.circle(surf, inner, (x, bloom_y - 1), 1)


def _f_bluebell(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    top_y = base_y - rng.randint(6, 10)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, top_y), 1)
    side = 1 if rng.random() < 0.5 else -1
    col = (110, 150, 230)
    col_dk = (75, 110, 195)
    col_hi = (170, 210, 255)
    n_bells = rng.randint(3, 4)
    for i in range(n_bells):
        by = top_y + i * 3
        bx = x + side * (1 + (i % 2))
        pygame.draw.ellipse(surf, col_dk, (bx, by, 3, 3))
        pygame.draw.ellipse(surf, col, (bx, by, 2, 3))
        pygame.draw.line(surf, col_hi, (bx, by), (bx, by), 1)


def _f_daffodil(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    fy = base_y - rng.randint(8, 11)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, fy + 1), 1)
    petal = (255, 248, 175)
    petal_dk = (220, 200, 110)
    pygame.draw.circle(surf, petal_dk, (x - 2, fy), 1)
    pygame.draw.circle(surf, petal_dk, (x + 2, fy), 1)
    pygame.draw.circle(surf, petal, (x - 1, fy - 1), 1)
    pygame.draw.circle(surf, petal, (x + 1, fy - 1), 1)
    pygame.draw.circle(surf, petal, (x - 1, fy + 1), 1)
    pygame.draw.circle(surf, petal, (x + 1, fy + 1), 1)
    pygame.draw.circle(surf, petal, (x, fy - 2), 1)
    pygame.draw.circle(surf, (240, 145, 45), (x, fy), 1)
    pygame.draw.circle(surf, (255, 200, 70), (x, fy), 1)


def _f_iris(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    fy = base_y - rng.randint(7, 10)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, fy + 1), 1)
    # Sword leaf
    pygame.draw.line(surf, _GRASS_DK,
                     (x - 1, base_y), (x - 1, base_y - 5), 1)
    pygame.draw.line(surf, _GRASS_TOP,
                     (x - 1, base_y), (x - 1, base_y - 4), 1)
    col = (150, 90, 215) if rng.random() < 0.5 else (90, 130, 220)
    col_dk = _shade(col, -45)
    col_hi = _mix(col, (255, 255, 255), 0.55)
    # 3 petals: left-up, right-up, down
    pygame.draw.line(surf, col_dk, (x - 1, fy - 2), (x - 1, fy), 1)
    pygame.draw.line(surf, col, (x - 1, fy - 1), (x - 1, fy), 1)
    pygame.draw.line(surf, col_dk, (x + 1, fy - 2), (x + 1, fy), 1)
    pygame.draw.line(surf, col, (x + 1, fy - 1), (x + 1, fy), 1)
    pygame.draw.line(surf, col, (x, fy - 3), (x, fy), 1)
    pygame.draw.circle(surf, col_hi, (x, fy - 2), 1)
    pygame.draw.circle(surf, (255, 220, 90), (x, fy + 1), 1)


def _f_cornflower(surf, x, ground_y, rng):
    fy = ground_y + rng.randint(-2, 5)
    pygame.draw.line(surf, _GRASS_DK, (x, fy + 3), (x, fy), 1)
    col = (90, 130, 220)
    pygame.draw.circle(surf, col, (x - 1, fy), 1)
    pygame.draw.circle(surf, col, (x + 1, fy), 1)
    pygame.draw.circle(surf, col, (x, fy - 1), 1)
    pygame.draw.circle(surf, col, (x, fy + 1), 1)
    pygame.draw.circle(surf, col, (x - 1, fy - 1), 1)
    pygame.draw.circle(surf, col, (x + 1, fy + 1), 1)
    pygame.draw.circle(surf, (50, 80, 160), (x, fy), 1)


def _f_foxglove(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    height = rng.randint(11, 15)
    top_y = base_y - height
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, top_y), 1)
    col = (210, 130, 180) if rng.random() < 0.5 else (170, 110, 220)
    col_dk = _shade(col, -30)
    col_hi = _mix(col, (255, 255, 255), 0.6)
    side = 1 if rng.random() < 0.5 else -1
    for i in range(5):
        by = top_y + 2 + i * 2
        bx = x + side
        pygame.draw.ellipse(surf, col_dk, (bx, by, 3, 2))
        pygame.draw.ellipse(surf, col, (bx, by, 2, 2))
    pygame.draw.circle(surf, col_hi, (x, top_y), 1)


def _f_cosmos(surf, x, ground_y, rng):
    fy = ground_y + rng.randint(-2, 5)
    pygame.draw.line(surf, _GRASS_DK, (x, fy + 3), (x, fy), 1)
    col = rng.choice([(250, 170, 210), (255, 230, 235), (240, 130, 170)])
    pygame.draw.circle(surf, col, (x - 1, fy - 1), 1)
    pygame.draw.circle(surf, col, (x + 1, fy - 1), 1)
    pygame.draw.circle(surf, col, (x - 1, fy + 1), 1)
    pygame.draw.circle(surf, col, (x + 1, fy + 1), 1)
    pygame.draw.circle(surf, col, (x, fy - 2), 1)
    pygame.draw.circle(surf, (200, 50, 80), (x, fy), 1)


def _f_marigold(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    fy = base_y - rng.randint(2, 4)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, fy + 1), 1)
    outer = (200, 110, 30) if rng.random() < 0.5 else (235, 165, 50)
    pygame.draw.circle(surf, _shade(outer, -30), (x, fy), 2)
    pygame.draw.circle(surf, outer, (x, fy), 2)
    pygame.draw.circle(surf, (255, 220, 100), (x - 1, fy - 1), 1)
    pygame.draw.circle(surf, (255, 220, 100), (x + 1, fy - 1), 1)
    pygame.draw.circle(surf, (160, 70, 20), (x, fy), 1)


def _f_crocus(surf, x, ground_y, rng):
    fy = ground_y + rng.randint(-1, 3)
    pygame.draw.line(surf, _GRASS_DK, (x, fy + 3), (x, fy), 1)
    col = rng.choice([(170, 100, 220), (240, 240, 250), (255, 200, 90)])
    pygame.draw.line(surf, _shade(col, -30), (x - 1, fy), (x - 1, fy - 1), 1)
    pygame.draw.line(surf, col, (x, fy - 2), (x, fy + 1), 1)
    pygame.draw.line(surf, _shade(col, -30), (x + 1, fy), (x + 1, fy - 1), 1)
    pygame.draw.circle(surf, (255, 230, 100), (x, fy), 1)


def _f_pansy(surf, x, ground_y, rng):
    fy = ground_y + rng.randint(-2, 5)
    pygame.draw.line(surf, _GRASS_DK, (x, fy + 3), (x, fy), 1)
    pygame.draw.circle(surf, (130, 80, 200), (x - 1, fy - 1), 1)
    pygame.draw.circle(surf, (130, 80, 200), (x + 1, fy - 1), 1)
    pygame.draw.circle(surf, (250, 220, 80), (x - 1, fy + 1), 1)
    pygame.draw.circle(surf, (250, 220, 80), (x + 1, fy + 1), 1)
    pygame.draw.circle(surf, _BLACK, (x, fy), 1)


def _f_carnation(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    fy = base_y - rng.randint(3, 5)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, fy + 1), 1)
    col = rng.choice([(245, 130, 170), (245, 70, 100), (255, 240, 230)])
    pygame.draw.circle(surf, _shade(col, -30), (x, fy), 2)
    pygame.draw.circle(surf, col, (x, fy), 2)
    pygame.draw.circle(surf, _mix(col, (255, 255, 255), 0.55),
                       (x - 1, fy - 1), 1)
    pygame.draw.circle(surf, _mix(col, (255, 255, 255), 0.55),
                       (x + 1, fy - 1), 1)


def _f_lily(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    fy = base_y - rng.randint(5, 8)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, fy + 1), 1)
    pygame.draw.line(surf, _GRASS_DK,
                     (x, base_y - 2), (x + 3, base_y - 4), 1)
    white = (250, 248, 240)
    pygame.draw.line(surf, white, (x - 2, fy + 1), (x, fy - 2), 1)
    pygame.draw.line(surf, white, (x + 2, fy + 1), (x, fy - 2), 1)
    pygame.draw.line(surf, white, (x - 2, fy + 1), (x - 1, fy + 2), 1)
    pygame.draw.line(surf, white, (x + 2, fy + 1), (x + 1, fy + 2), 1)
    pygame.draw.circle(surf, (240, 200, 80), (x, fy), 1)


def _f_hyacinth(surf, x, ground_y, rng):
    """Dense vertical pyramid cluster — 3 dots wide, distinct from lavender."""
    base_y = ground_y + rng.randint(0, 4)
    height = rng.randint(9, 13)
    top_y = base_y - height
    pygame.draw.line(surf, (95, 135, 80), (x, base_y), (x, top_y), 1)
    col = rng.choice([(170, 130, 220), (235, 130, 210), (130, 100, 230)])
    col_dk = _shade(col, -30)
    # Pyramid: narrow at top, wider toward bottom
    for i, sy in enumerate(range(top_y, top_y + height // 2 + 2)):
        wd = 1 if i == 0 else 2
        for off in range(-wd, wd + 1):
            shade = col_dk if (off + i) % 2 == 0 else col
            pygame.draw.circle(surf, shade, (x + off, sy), 1)


def _f_tiger_lily(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    fy = base_y - rng.randint(6, 9)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, fy + 1), 1)
    pygame.draw.line(surf, (255, 130, 30), (x - 2, fy), (x, fy - 2), 1)
    pygame.draw.line(surf, (255, 130, 30), (x + 2, fy), (x, fy - 2), 1)
    pygame.draw.line(surf, (235, 100, 40), (x - 2, fy + 1), (x - 1, fy + 2), 1)
    pygame.draw.line(surf, (235, 100, 40), (x + 2, fy + 1), (x + 1, fy + 2), 1)
    pygame.draw.circle(surf, (90, 30, 20), (x - 1, fy - 1), 1)
    pygame.draw.circle(surf, (90, 30, 20), (x + 1, fy), 1)
    pygame.draw.circle(surf, (255, 100, 60), (x, fy), 1)


def _f_buttercup(surf, x, ground_y, rng):
    """Cheery low yellow cup — bigger center than the V1 mixed yellow."""
    fy = ground_y + rng.randint(-1, 4)
    pygame.draw.line(surf, _GRASS_DK, (x, fy + 3), (x, fy), 1)
    petal = (240, 200, 50)
    pygame.draw.circle(surf, petal, (x - 1, fy - 1), 1)
    pygame.draw.circle(surf, petal, (x + 1, fy - 1), 1)
    pygame.draw.circle(surf, petal, (x - 1, fy + 1), 1)
    pygame.draw.circle(surf, petal, (x + 1, fy + 1), 1)
    pygame.draw.circle(surf, petal, (x, fy - 2), 1)
    pygame.draw.circle(surf, (255, 245, 130), (x, fy), 2)
    pygame.draw.circle(surf, (255, 200, 60), (x, fy), 1)


def _f_forget_me_not(surf, x, ground_y, rng):
    """Tiny cluster of small blue 5-petal flowers."""
    fy = ground_y + rng.randint(-2, 5)
    pygame.draw.line(surf, _GRASS_DK, (x, fy + 3), (x, fy), 1)
    blue = (140, 180, 230)
    yellow = (255, 230, 100)
    # 3 small flowers in a cluster
    for cx, cy in ((x - 1, fy - 1), (x + 1, fy), (x, fy + 1)):
        for off in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            pygame.draw.circle(surf, blue, (cx + off[0], cy + off[1]), 1)
        pygame.draw.circle(surf, yellow, (cx, cy), 1)


def _f_violet(surf, x, ground_y, rng):
    """Low wild violet — 5-petal purple with bright center."""
    fy = ground_y + rng.randint(0, 4)
    pygame.draw.line(surf, _GRASS_DK, (x, fy + 3), (x, fy), 1)
    col = (130, 80, 180)
    col_hi = (180, 130, 220)
    pygame.draw.circle(surf, col, (x - 1, fy - 1), 1)
    pygame.draw.circle(surf, col, (x + 1, fy - 1), 1)
    pygame.draw.circle(surf, col_hi, (x, fy + 1), 1)
    pygame.draw.circle(surf, col, (x - 1, fy + 1), 1)
    pygame.draw.circle(surf, col, (x + 1, fy + 1), 1)
    pygame.draw.circle(surf, (250, 240, 230), (x, fy), 1)


def _f_black_eyed_susan(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    fy = base_y - rng.randint(3, 6)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, fy + 1), 1)
    petal = (255, 200, 60)
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                   (-1, -1), (1, 1), (1, -1), (-1, 1)):
        pygame.draw.circle(surf, petal, (x + dx, fy + dy), 1)
    pygame.draw.circle(surf, (60, 35, 15), (x, fy), 1)


def _f_aster(surf, x, ground_y, rng):
    """Thin-petal radial star, smaller than gerbera."""
    fy = ground_y + rng.randint(-2, 5)
    pygame.draw.line(surf, _GRASS_DK, (x, fy + 3), (x, fy), 1)
    col = rng.choice([(180, 110, 200), (235, 130, 200), (130, 90, 200),
                      (115, 165, 220)])
    pygame.draw.line(surf, col, (x - 2, fy), (x + 2, fy), 1)
    pygame.draw.line(surf, col, (x, fy - 2), (x, fy + 2), 1)
    pygame.draw.line(surf, col, (x - 1, fy - 1), (x + 1, fy + 1), 1)
    pygame.draw.line(surf, col, (x + 1, fy - 1), (x - 1, fy + 1), 1)
    pygame.draw.circle(surf, (255, 220, 90), (x, fy), 1)


def _f_zinnia(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    fy = base_y - rng.randint(2, 5)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, fy + 1), 1)
    outer = rng.choice([(245, 100, 70), (245, 130, 60), (235, 165, 50),
                        (255, 200, 60), (240, 100, 130)])
    mid = _mix(outer, (255, 255, 255), 0.45)
    pygame.draw.circle(surf, _shade(outer, -30), (x, fy), 3)
    pygame.draw.circle(surf, outer, (x, fy), 2)
    pygame.draw.circle(surf, mid, (x, fy - 1), 1)
    pygame.draw.circle(surf, (255, 220, 90), (x, fy), 1)


def _f_chrysanthemum(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    fy = base_y - rng.randint(3, 5)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, fy + 1), 1)
    col = rng.choice([(245, 140, 50), (240, 220, 90),
                      (240, 100, 130), (240, 240, 230)])
    pygame.draw.circle(surf, _shade(col, -30), (x, fy), 2)
    pygame.draw.circle(surf, col, (x, fy), 2)
    for ox, oy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        pygame.draw.circle(surf, col, (x + ox, fy + oy), 1)
    pygame.draw.circle(surf, _mix(col, (255, 255, 255), 0.6),
                       (x - 1, fy - 1), 1)


def _f_snapdragon(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    height = rng.randint(10, 14)
    top_y = base_y - height
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, top_y), 1)
    col = rng.choice([(245, 130, 100), (250, 200, 120), (240, 240, 230),
                      (235, 110, 170)])
    col_dk = _shade(col, -30)
    for i in range(4):
        by = top_y + 2 + i * 3
        bx = x + (1 if i % 2 == 0 else -1)
        pygame.draw.ellipse(surf, col_dk, (bx - 1, by - 1, 3, 3))
        pygame.draw.ellipse(surf, col, (bx - 1, by - 1, 3, 2))
        pygame.draw.line(surf, col_dk, (bx, by + 1), (bx, by + 1), 1)


def _f_ranunculus(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    fy = base_y - rng.randint(3, 5)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, fy + 1), 1)
    col = rng.choice([(245, 220, 90), (250, 175, 200), (245, 100, 100),
                      (255, 180, 60)])
    pygame.draw.circle(surf, _shade(col, -45), (x, fy), 2)
    pygame.draw.circle(surf, _shade(col, -20), (x, fy), 2)
    pygame.draw.circle(surf, col, (x, fy - 1), 1)
    pygame.draw.circle(surf, _mix(col, (255, 255, 255), 0.7),
                       (x - 1, fy - 1), 1)


def _f_gerbera(surf, x, ground_y, rng):
    """Bold large radial daisy — 8 petals."""
    base_y = ground_y + rng.randint(0, 4)
    fy = base_y - rng.randint(4, 7)
    pygame.draw.line(surf, _GRASS_DK, (x, base_y), (x, fy + 1), 1)
    col = rng.choice([(245, 80, 80), (255, 165, 60), (235, 95, 160),
                      (255, 230, 100), (245, 130, 60)])
    for ang_deg in (0, 45, 90, 135, 180, 225, 270, 315):
        ang = math.radians(ang_deg)
        px = x + int(math.cos(ang) * 2)
        py = fy + int(math.sin(ang) * 2)
        pygame.draw.circle(surf, col, (px, py), 1)
    pygame.draw.circle(surf, (60, 35, 25), (x, fy), 1)


def _f_larkspur(surf, x, ground_y, rng):
    base_y = ground_y + rng.randint(0, 4)
    height = rng.randint(11, 15)
    top_y = base_y - height
    pygame.draw.line(surf, (95, 135, 80), (x, base_y), (x, top_y), 1)
    col = rng.choice([(90, 130, 220), (140, 90, 200), (110, 160, 230)])
    col_dk = _shade(col, -30)
    for i in range(4):
        by = top_y + 1 + i * 3
        pygame.draw.circle(surf, col_dk, (x, by), 1)
        pygame.draw.circle(surf, col, (x - 1, by), 1)
        pygame.draw.circle(surf, col, (x + 1, by), 1)
        pygame.draw.circle(surf, col, (x, by - 1), 1)


# Full 30-flower pool — V3 picks one at every position so the meadow
# never repeats. Ordered roughly small → tall for readability only.
_FLOWER_POOL = [
    # short-stem rounds
    _f_daisy, _f_poppy, _f_cornflower, _f_cosmos, _f_pansy,
    _f_violet, _f_forget_me_not, _f_buttercup, _f_aster, _f_crocus,
    # mid pom / layered
    _f_marigold, _f_carnation, _f_chrysanthemum, _f_ranunculus,
    _f_zinnia, _f_rose, _f_gerbera, _f_black_eyed_susan,
    # tall single bloom
    _f_tulip, _f_daffodil, _f_iris, _f_lily, _f_tiger_lily,
    # tall spike / cluster
    _f_lavender, _f_foxglove, _f_hyacinth, _f_snapdragon,
    _f_larkspur, _f_bluebell, _f_sunflower,
]
assert len(_FLOWER_POOL) == 30


# Single-style flower function (V1, V2, V4, V5).
_V1_PALETTE = [(235, 80, 80), (255, 220, 90), (250, 248, 240),
               (250, 170, 210), (190, 130, 230)]


def _f_mixed(surf, x, ground_y, rng):
    col = rng.choice(_V1_PALETTE)
    fy = ground_y + rng.randint(-2, 6)
    pygame.draw.line(surf, _GRASS_DK, (x, fy + 3), (x, fy), 1)
    pygame.draw.circle(surf, col, (x - 1, fy), 1)
    pygame.draw.circle(surf, col, (x + 1, fy), 1)
    pygame.draw.circle(surf, col, (x, fy - 1), 1)
    pygame.draw.circle(surf, col, (x, fy + 1), 1)
    pygame.draw.circle(surf, _YELLOW_CENTER, (x, fy), 1)


# ── shared meadow scene ────────────────────────────────────────────────────

def _meadow_scene(surf, ground_y, w, h, scroll, mid_color,
                  flower_pool, accent_kind, flower_step=18):
    """Render grass + blades + flowers + rocks + creatures. ``flower_pool``
    is a list; each flower position picks one entry. Smaller
    ``flower_step`` = denser meadow.
    """
    grass_h = 22
    _vertical_gradient(surf, 0, ground_y, w, ground_y + grass_h,
                       _GRASS_TOP, _GRASS_MID)
    _vertical_gradient(surf, 0, ground_y + grass_h, w, h,
                       _DIRT_TOP, _DIRT_DEEP)

    # Sparse darker grass tufts
    for sx, k, rng in _scatter(scroll, w, 0.7, 5, 11):
        if 0 <= sx < w:
            tuft_h = rng.randint(3, 9)
            lean = rng.randint(-2, 2)
            base_y = ground_y + rng.randint(0, 4)
            pygame.draw.line(surf, _GRASS_DK,
                             (sx, base_y), (sx + lean, base_y - tuft_h), 1)
            pygame.draw.line(surf, _GRASS_TOP,
                             (sx, base_y), (sx + lean, base_y - tuft_h + 1), 1)

    # Tall hero blades
    for sx, k, rng in _scatter(scroll, w, 0.7, 11, 23):
        if 0 <= sx < w:
            tuft_h = rng.randint(7, 12)
            base_y = ground_y + rng.randint(0, 2)
            lean = rng.randint(-2, 2)
            pygame.draw.line(surf, _GRASS_DK,
                             (sx, base_y), (sx + lean, base_y - tuft_h), 1)
            pygame.draw.line(surf, _GRASS_TOP,
                             (sx + 1, base_y), (sx + 1 + lean, base_y - tuft_h + 1), 1)

    # Flowers — random pick from the pool
    for sx, k, rng in _scatter(scroll, w, 0.7, flower_step, 37):
        if 0 <= sx < w:
            flower_fn = rng.choice(flower_pool)
            flower_fn(surf, sx, ground_y, rng)

    # Dandelion puffballs
    for sx, k, rng in _scatter(scroll, w, 0.7, 55, 53):
        if 0 <= sx < w and rng.random() < 0.55:
            fy = ground_y + rng.randint(-3, 4)
            pygame.draw.line(surf, _GRASS_DK,
                             (sx, fy + 4), (sx, fy), 1)
            pygame.draw.circle(surf, (255, 245, 200), (sx, fy), 2)
            pygame.draw.circle(surf, (255, 255, 255), (sx, fy), 1)

    # Half-buried rocks
    for sx, k, rng in _scatter(scroll, w, 0.7, 70, 67):
        if 0 <= sx < w and rng.random() < 0.55:
            ry = ground_y + 10 + rng.randint(0, 8)
            rw = rng.randint(4, 7)
            pygame.draw.ellipse(surf, _ROCK,
                                (sx - rw // 2, ry, rw, 3))
            pygame.draw.line(surf, _shade(_ROCK, 30),
                             (sx - rw // 2 + 1, ry),
                             (sx + rw // 2 - 2, ry), 1)

    # Accent creatures
    if accent_kind == "butterfly":
        for sx, k, rng in _scatter(scroll, w, 0.7, 130, 91):
            if 0 <= sx < w and rng.random() < 0.5:
                by = ground_y - rng.randint(8, 22)
                col = rng.choice([(255, 220, 90), (250, 170, 210),
                                  (190, 130, 230)])
                _butterfly(surf, sx, by, col)
    elif accent_kind == "ladybug":
        for sx, k, rng in _scatter(scroll, w, 0.7, 65, 113):
            if 0 <= sx < w and rng.random() < 0.55:
                ly = ground_y + rng.randint(2, 28)
                _ladybug(surf, sx, ly)
    elif accent_kind == "bee":
        for sx, k, rng in _scatter(scroll, w, 0.7, 60, 131):
            if 0 <= sx < w and rng.random() < 0.55:
                by = ground_y - rng.randint(2, 18)
                _bee(surf, sx, by)
    elif accent_kind == "garden_mix":
        # Headline V3: bees + butterflies + the occasional ladybug, so
        # the meadow looks alive without one creature dominating.
        for sx, k, rng in _scatter(scroll, w, 0.7, 95, 91):
            if 0 <= sx < w and rng.random() < 0.55:
                by = ground_y - rng.randint(8, 22)
                col = rng.choice([(255, 220, 90), (250, 170, 210),
                                  (190, 130, 230)])
                _butterfly(surf, sx, by, col)
        for sx, k, rng in _scatter(scroll, w, 0.7, 110, 131):
            if 0 <= sx < w and rng.random() < 0.45:
                by = ground_y - rng.randint(4, 18)
                _bee(surf, sx, by)
        for sx, k, rng in _scatter(scroll, w, 0.7, 140, 113):
            if 0 <= sx < w and rng.random() < 0.45:
                ly = ground_y + rng.randint(2, 26)
                _ladybug(surf, sx, ly)

    # Edge highlight
    pygame.draw.line(surf, _shade(_GRASS_TOP, 60),
                     (0, ground_y), (w - 1, ground_y), 1)

    _ambient_ground_overlay(surf, ground_y, w, h, mid_color)


# ── public variant entry points ────────────────────────────────────────────

def draw_ground_v1(surf, ground_y, w, h, scroll,
                   top_color=None, mid_color=None, bot_color=None):
    """V1 — Mixed Wildflowers (original)."""
    _meadow_scene(surf, ground_y, w, h, scroll,
                  mid_color or _GRASS_MID,
                  [_f_mixed], "butterfly", flower_step=22)


def draw_ground_v2(surf, ground_y, w, h, scroll,
                   top_color=None, mid_color=None, bot_color=None):
    """V2 — Daisy Lawn."""
    _meadow_scene(surf, ground_y, w, h, scroll,
                  mid_color or _GRASS_MID,
                  [_f_daisy], "butterfly", flower_step=22)


def draw_ground_v3(surf, ground_y, w, h, scroll,
                   top_color=None, mid_color=None, bot_color=None):
    """V3 — Dynamic Meadow: 12-flower pool, every position picks randomly."""
    _meadow_scene(surf, ground_y, w, h, scroll,
                  mid_color or _GRASS_MID,
                  _FLOWER_POOL, "garden_mix", flower_step=16)


def draw_ground_v4(surf, ground_y, w, h, scroll,
                   top_color=None, mid_color=None, bot_color=None):
    """V4 — Poppy Field."""
    _meadow_scene(surf, ground_y, w, h, scroll,
                  mid_color or _GRASS_MID,
                  [_f_poppy], "ladybug", flower_step=22)


def draw_ground_v5(surf, ground_y, w, h, scroll,
                   top_color=None, mid_color=None, bot_color=None):
    """V5 — Lavender Spikes."""
    _meadow_scene(surf, ground_y, w, h, scroll,
                  mid_color or _GRASS_MID,
                  [_f_lavender], "bee", flower_step=22)


# ── dispatcher ─────────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_ground_v1,
    2: draw_ground_v2,
    3: draw_ground_v3,
    4: draw_ground_v4,
    5: draw_ground_v5,
}

VARIANT_NAMES = {
    1: "Mixed Wildflowers (original)",
    2: "Daisy Lawn",
    3: "Dynamic Meadow (30-flower pool)",
    4: "Poppy Field",
    5: "Lavender Spikes",
}
