"""Mountain variants — 5 wildly different tree-forest themes.

Each variant is a complete self-contained scene with its own hill palette,
tree style, and ambient decoration. They all share the same signature so
they're drop-in replacements for ``game.draw.draw_mountains``.
"""
from __future__ import annotations

import math
import random

import pygame


# ── shared helpers ─────────────────────────────────────────────────────────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, delta):
    return (_clamp(c[0] + delta), _clamp(c[1] + delta), _clamp(c[2] + delta))


def _brightness(c) -> float:
    return min(1.0, (c[0] + c[1] + c[2]) / 510.0)


def _warmth(c) -> float:
    return (c[0] - c[2]) / 255.0


def _ambient_overlay(surf, ground_y, w, near_color):
    """Translucent overlay so the theme still responds to time-of-day."""
    b = _brightness(near_color)
    band = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    if b < 0.6:
        alpha = int(160 * (0.6 - b))
        band.fill((near_color[0] // 3, near_color[1] // 3,
                   near_color[2] // 3, alpha))
    w_amt = _warmth(near_color)
    if w_amt > 0.05:
        alpha = int(min(85, w_amt * 220))
        warm = pygame.Surface((w, ground_y), pygame.SRCALPHA)
        warm.fill((255, 150, 90, alpha))
        band.blit(warm, (0, 0))
    surf.blit(band, (0, 0))


def _hill_polygon(w, ground_y, scroll, speed, base_h, freq_a, amp_a,
                  freq_b, amp_b, phase_a=0.0, phase_b=0.0):
    """Return polygon points + sampled (x, ridge_y) heights for a hill layer."""
    pts = [(0, ground_y)]
    heights: list[tuple[int, int]] = []
    for x in range(0, w + 1, 3):
        sx = x + scroll * speed
        h = int(base_h
                + math.sin(sx * freq_a + phase_a) * amp_a
                + math.sin(sx * freq_b + phase_b) * amp_b)
        pts.append((x, ground_y - h))
        heights.append((x, ground_y - h))
    pts.append((w, ground_y))
    return pts, heights


def _scatter_trees(scroll, w, speed, step, seed_off):
    """Yield (sx, key) for tree positions across the screen, deterministic."""
    phase = scroll * speed
    first = int(phase // step) - 1
    last = int((phase + w) // step) + 2
    for k in range(first, last + 1):
        rng = random.Random((k * 2654435761 ^ seed_off) & 0xFFFFFFFF)
        wx = k * step + rng.uniform(-step * 0.2, step * 0.2)
        sx = int(wx - phase)
        if -30 < sx < w + 30:
            yield sx, k, rng


# ──────────────────────────────────────────────────────────────────────────
# V1: Twisted Bonsai
# ──────────────────────────────────────────────────────────────────────────

_V1_BACK = (170, 195, 195)
_V1_MID = (105, 140, 120)
_V1_NEAR = (70, 105, 85)
_V1_TRUNK = (55, 40, 30)
_V1_FOLIAGE = (60, 130, 70)
_V1_FOLIAGE_DK = (38, 90, 50)
_V1_FOLIAGE_HI = (130, 200, 110)
_V1_LEAF_RED = (215, 80, 70)


def _tree_bonsai(surf, x, y, scale=1.0):
    """Gnarled twisted bonsai with dense foliage cushions."""
    s = scale
    # Twisted trunk: zigzag of 4 points
    p1 = (x, y)
    p2 = (x - int(4 * s), y - int(10 * s))
    p3 = (x + int(3 * s), y - int(18 * s))
    p4 = (x, y - int(23 * s))
    pygame.draw.lines(surf, _V1_TRUNK, False, [p1, p2, p3, p4],
                      max(2, int(2 * s)))
    # Branch reaching right
    branch_end = (x + int(9 * s), y - int(20 * s))
    pygame.draw.line(surf, _V1_TRUNK, p3, branch_end, max(1, int(2 * s)))
    # Branch reaching left
    branch_left = (x - int(7 * s), y - int(22 * s))
    pygame.draw.line(surf, _V1_TRUNK, p3, branch_left, max(1, int(2 * s)))

    # Foliage cushions at branch tips and top
    r = max(3, int(5 * s))
    cushions = [
        (x - int(6 * s), y - int(24 * s)),
        (x, y - int(27 * s)),
        (x + int(5 * s), y - int(25 * s)),
        (x + int(10 * s), y - int(20 * s)),
        (x - int(7 * s), y - int(22 * s)),
    ]
    for cx, cy in cushions:
        pygame.draw.circle(surf, _V1_FOLIAGE_DK, (cx, cy + 1), r + 1)
        pygame.draw.circle(surf, _V1_FOLIAGE, (cx, cy), r)
    # Highlight on top cushion
    pygame.draw.circle(surf, _V1_FOLIAGE_HI, (cushions[1][0] - 1, cushions[1][1] - 1),
                       max(1, int(2 * s)))
    # Red leaf accents
    pygame.draw.circle(surf, _V1_LEAF_RED, cushions[0], max(1, int(2 * s)))
    pygame.draw.circle(surf, _V1_LEAF_RED, (cushions[3][0] - 1, cushions[3][1] + 1),
                       max(1, int(1.5 * s)))


def draw_mountains_v1(surf, scroll, ground_y, w, far_color=None, near_color=None):
    near_color = near_color or (30, 40, 80)

    pts, _ = _hill_polygon(w, ground_y, scroll, 0.06, 95,
                           0.010, 22, 0.027, 10, phase_b=0.8)
    pygame.draw.polygon(surf, _V1_BACK, pts)

    # Distant pagoda silhouette every now and then on mid hills
    pts, mid_h = _hill_polygon(w, ground_y, scroll, 0.15, 70,
                               0.014, 26, 0.033, 12, phase_b=1.4)
    pygame.draw.polygon(surf, _V1_MID, pts)
    for sx, k, rng in _scatter_trees(scroll, w, 0.15, 38, 7):
        if 0 <= sx < w:
            idx = min(len(mid_h) - 1, max(0, sx // 3))
            ridge_y = mid_h[idx][1]
            _tree_bonsai(surf, sx, ridge_y + 4, scale=0.55)
    # Optional small pagoda silhouettes — sparse, deterministic
    for sx, k, rng in _scatter_trees(scroll, w, 0.15, 120, 91):
        if 0 <= sx < w and rng.random() < 0.55:
            idx = min(len(mid_h) - 1, max(0, sx // 3))
            ridge_y = mid_h[idx][1]
            _v1_pagoda_silhouette(surf, sx, ridge_y + 2,
                                  _shade(_V1_MID, -28))

    pts, near_h = _hill_polygon(w, ground_y, scroll, 0.28, 48,
                                0.018, 20, 0.041, 9, phase_b=0.5)
    pygame.draw.polygon(surf, _V1_NEAR, pts)
    for sx, k, rng in _scatter_trees(scroll, w, 0.28, 30, 13):
        if 0 <= sx < w:
            idx = min(len(near_h) - 1, max(0, sx // 3))
            ridge_y = near_h[idx][1]
            _tree_bonsai(surf, sx, ridge_y + 4, scale=1.0)

    # Drifting red leaves in the air
    rng = random.Random(int(scroll) // 7)
    for _ in range(28):
        lx = rng.randrange(0, w)
        ly = rng.randrange(ground_y - 200, ground_y - 30)
        pygame.draw.circle(surf, _V1_LEAF_RED, (lx, ly), 1)
        if rng.random() < 0.5:
            pygame.draw.circle(surf, (240, 140, 110), (lx + 1, ly), 1)

    _ambient_overlay(surf, ground_y, w, near_color)


def _v1_pagoda_silhouette(surf, x, base_y, color):
    """Tiny 3-tier pagoda silhouette as scene accent."""
    pygame.draw.rect(surf, color, (x - 3, base_y - 4, 6, 4))
    pygame.draw.polygon(surf, color,
                        [(x - 5, base_y - 4), (x + 5, base_y - 4), (x, base_y - 8)])
    pygame.draw.rect(surf, color, (x - 2, base_y - 11, 4, 3))
    pygame.draw.polygon(surf, color,
                        [(x - 4, base_y - 11), (x + 4, base_y - 11), (x, base_y - 14)])
    pygame.draw.line(surf, color, (x, base_y - 14), (x, base_y - 17), 1)


# ──────────────────────────────────────────────────────────────────────────
# V2: Autumn Maple
# ──────────────────────────────────────────────────────────────────────────

_V2_BACK = (175, 155, 145)
_V2_MID = (175, 125, 90)
_V2_NEAR = (130, 100, 70)
_V2_TRUNK = (60, 40, 30)
_V2_RED = (220, 75, 50)
_V2_ORANGE = (245, 145, 55)
_V2_YELLOW = (250, 210, 80)
_V2_DARK = (165, 60, 30)


def _tree_autumn(surf, x, y, scale=1.0):
    """Layered red/orange/yellow autumn maple canopy."""
    s = scale
    trunk_h = int(18 * s)
    pygame.draw.line(surf, _V2_TRUNK, (x, y), (x, y - trunk_h),
                     max(2, int(2 * s)))
    # Side branches sketched
    pygame.draw.line(surf, _V2_TRUNK,
                     (x, y - trunk_h + 4),
                     (x - int(6 * s), y - trunk_h - int(2 * s)), 1)
    pygame.draw.line(surf, _V2_TRUNK,
                     (x, y - trunk_h + 2),
                     (x + int(6 * s), y - trunk_h - int(3 * s)), 1)

    r = max(4, int(11 * s))
    cy = y - trunk_h - r // 2
    # Layered colors: dark base → red → orange → yellow center
    pygame.draw.circle(surf, _V2_DARK, (x - r // 3, cy + 1), r)
    pygame.draw.circle(surf, _V2_DARK, (x + r // 3, cy), r)
    pygame.draw.circle(surf, _V2_DARK, (x, cy - r // 2), r - 1)

    pygame.draw.circle(surf, _V2_RED, (x - r // 3, cy), r - 1)
    pygame.draw.circle(surf, _V2_RED, (x + r // 3, cy - 1), r - 2)
    pygame.draw.circle(surf, _V2_ORANGE, (x, cy - r // 3), r - 2)
    pygame.draw.circle(surf, _V2_YELLOW, (x + 1, cy - r // 2 - 1),
                       max(2, r - 4))
    # Scattered leaf dots for texture
    rng = random.Random(int(x * 17 + y))
    for _ in range(6):
        dx = rng.randint(-r, r)
        dy = rng.randint(-r - r // 2, r // 3)
        col = rng.choice([_V2_RED, _V2_ORANGE, _V2_YELLOW])
        pygame.draw.circle(surf, col, (x + dx, cy + dy), max(1, int(1.5 * s)))


def draw_mountains_v2(surf, scroll, ground_y, w, far_color=None, near_color=None):
    near_color = near_color or (30, 40, 80)

    pts, _ = _hill_polygon(w, ground_y, scroll, 0.06, 95,
                           0.010, 22, 0.027, 10, phase_b=0.8)
    pygame.draw.polygon(surf, _V2_BACK, pts)

    pts, mid_h = _hill_polygon(w, ground_y, scroll, 0.15, 70,
                               0.014, 26, 0.033, 12, phase_b=1.4)
    pygame.draw.polygon(surf, _V2_MID, pts)
    for sx, k, rng in _scatter_trees(scroll, w, 0.15, 38, 7):
        if 0 <= sx < w:
            idx = min(len(mid_h) - 1, max(0, sx // 3))
            ridge_y = mid_h[idx][1]
            _tree_autumn(surf, sx, ridge_y + 4, scale=0.55)

    pts, near_h = _hill_polygon(w, ground_y, scroll, 0.28, 48,
                                0.018, 20, 0.041, 9, phase_b=0.5)
    pygame.draw.polygon(surf, _V2_NEAR, pts)
    for sx, k, rng in _scatter_trees(scroll, w, 0.28, 28, 13):
        if 0 <= sx < w:
            idx = min(len(near_h) - 1, max(0, sx // 3))
            ridge_y = near_h[idx][1]
            _tree_autumn(surf, sx, ridge_y + 4, scale=1.0)

    # Falling leaves: small colored dots scattered with random rotation hint
    rng = random.Random(int(scroll) // 5)
    for _ in range(40):
        lx = rng.randrange(0, w)
        ly = rng.randrange(ground_y - 220, ground_y - 20)
        col = rng.choice([_V2_RED, _V2_ORANGE, _V2_YELLOW])
        # Draw as 2-pixel ellipse for a "leaf" feel
        if rng.random() < 0.5:
            pygame.draw.ellipse(surf, col, (lx, ly, 3, 2))
        else:
            pygame.draw.ellipse(surf, col, (lx, ly, 2, 3))

    _ambient_overlay(surf, ground_y, w, near_color)


# ──────────────────────────────────────────────────────────────────────────
# V3: Bioluminescent Alien
# ──────────────────────────────────────────────────────────────────────────

_V3_BACK = (45, 35, 75)
_V3_MID = (60, 40, 95)
_V3_NEAR = (40, 25, 65)
_V3_TRUNK = (22, 18, 35)
_V3_ORBS = [
    (90, 230, 220),   # teal
    (60, 200, 240),   # cyan
    (180, 120, 240),  # violet
    (240, 110, 200),  # magenta
    (140, 250, 160),  # mint
]


def _tree_alien(surf, x, y, scale=1.0):
    """Dark twisted trunk with glowing orb fruits at branch tips."""
    s = scale
    trunk_h = int(22 * s)
    # Trunk (gently curved)
    p1 = (x, y)
    p2 = (x + int(2 * s), y - int(8 * s))
    p3 = (x - int(2 * s), y - int(16 * s))
    p4 = (x, y - trunk_h)
    pygame.draw.lines(surf, _V3_TRUNK, False, [p1, p2, p3, p4],
                      max(2, int(2 * s)))

    branch_y = y - trunk_h
    # Branches splaying out
    branches = [
        (x - int(9 * s), branch_y - int(3 * s)),
        (x - int(5 * s), branch_y - int(10 * s)),
        (x, branch_y - int(12 * s)),
        (x + int(5 * s), branch_y - int(10 * s)),
        (x + int(9 * s), branch_y - int(3 * s)),
    ]
    for bx, by in branches:
        pygame.draw.line(surf, _V3_TRUNK, (x, branch_y), (bx, by),
                         max(1, int(2 * s)))

    # Glowing orbs at branch tips
    rng = random.Random(int(x * 31))
    for bx, by in branches:
        color = _V3_ORBS[rng.randrange(len(_V3_ORBS))]
        # Outer halo
        halo_r = max(6, int(8 * s))
        halo = pygame.Surface((halo_r * 2 + 2, halo_r * 2 + 2),
                              pygame.SRCALPHA)
        pygame.draw.circle(halo, (color[0], color[1], color[2], 60),
                           (halo_r + 1, halo_r + 1), halo_r)
        pygame.draw.circle(halo, (color[0], color[1], color[2], 130),
                           (halo_r + 1, halo_r + 1), halo_r - 2)
        surf.blit(halo, (bx - halo_r - 1, by - halo_r - 1))
        # Bright core
        pygame.draw.circle(surf, color, (bx, by), max(2, int(3 * s)))
        pygame.draw.circle(surf, (255, 255, 255), (bx, by),
                           max(1, int(1 * s)))


def draw_mountains_v3(surf, scroll, ground_y, w, far_color=None, near_color=None):
    near_color = near_color or (30, 40, 80)

    pts, _ = _hill_polygon(w, ground_y, scroll, 0.06, 95,
                           0.010, 22, 0.027, 10, phase_b=0.8)
    pygame.draw.polygon(surf, _V3_BACK, pts)

    pts, mid_h = _hill_polygon(w, ground_y, scroll, 0.15, 70,
                               0.014, 26, 0.033, 12, phase_b=1.4)
    pygame.draw.polygon(surf, _V3_MID, pts)
    for sx, k, rng in _scatter_trees(scroll, w, 0.15, 38, 7):
        if 0 <= sx < w:
            idx = min(len(mid_h) - 1, max(0, sx // 3))
            ridge_y = mid_h[idx][1]
            _tree_alien(surf, sx, ridge_y + 4, scale=0.55)

    pts, near_h = _hill_polygon(w, ground_y, scroll, 0.28, 48,
                                0.018, 20, 0.041, 9, phase_b=0.5)
    pygame.draw.polygon(surf, _V3_NEAR, pts)
    for sx, k, rng in _scatter_trees(scroll, w, 0.28, 28, 13):
        if 0 <= sx < w:
            idx = min(len(near_h) - 1, max(0, sx // 3))
            ridge_y = near_h[idx][1]
            _tree_alien(surf, sx, ridge_y + 4, scale=1.0)

    # Floating glowing particles (spores)
    rng = random.Random(int(scroll) // 5)
    glow_layer = pygame.Surface((w, ground_y), pygame.SRCALPHA)
    for _ in range(45):
        px = rng.randrange(0, w)
        py = rng.randrange(ground_y - 220, ground_y - 20)
        col = rng.choice(_V3_ORBS)
        pygame.draw.circle(glow_layer, (col[0], col[1], col[2], 90), (px, py), 3)
        pygame.draw.circle(glow_layer, (255, 255, 255, 220), (px, py), 1)
    surf.blit(glow_layer, (0, 0))

    _ambient_overlay(surf, ground_y, w, near_color)


# ──────────────────────────────────────────────────────────────────────────
# V4: Dr. Seuss Truffula
# ──────────────────────────────────────────────────────────────────────────

_V4_BACK = (210, 180, 215)
_V4_MID = (200, 145, 175)
_V4_NEAR = (115, 165, 150)
_V4_TRUNK = (80, 55, 90)
_V4_TRUNK_STRIPE = (220, 200, 235)
_V4_PUFFS = [
    (255, 200, 80),   # yellow
    (220, 110, 200),  # magenta
    (140, 220, 230),  # teal
    (255, 140, 90),   # coral
    (180, 230, 130),  # lime
    (130, 160, 250),  # periwinkle
]


def _tree_seuss(surf, x, y, scale=1.0):
    """Wavy striped trunk + stacked multi-colour puff balls (Truffula)."""
    s = scale
    trunk_h = int(30 * s)
    # Wavy trunk (3 segments forming gentle S)
    pts = [
        (x, y),
        (x - int(3 * s), y - int(10 * s)),
        (x + int(3 * s), y - int(20 * s)),
        (x - int(2 * s), y - trunk_h),
    ]
    pygame.draw.lines(surf, _V4_TRUNK, False, pts, max(2, int(2 * s)))
    # Horizontal stripes — sample positions along the polyline
    seg_lens = []
    for i in range(len(pts) - 1):
        seg_lens.append(math.hypot(pts[i + 1][0] - pts[i][0],
                                   pts[i + 1][1] - pts[i][1]))
    total = sum(seg_lens)
    n_stripes = max(4, int(total / 4))
    for i in range(n_stripes):
        u = (i + 0.5) / n_stripes * total
        # Find segment
        acc = 0
        for j, sl in enumerate(seg_lens):
            if acc + sl >= u:
                t = (u - acc) / sl if sl > 0 else 0
                sx = int(pts[j][0] + (pts[j + 1][0] - pts[j][0]) * t)
                sy = int(pts[j][1] + (pts[j + 1][1] - pts[j][1]) * t)
                pygame.draw.line(surf, _V4_TRUNK_STRIPE,
                                 (sx - 1, sy), (sx + 1, sy), 1)
                break
            acc += sl

    # Stacked puff balls at top
    top = pts[-1]
    rng = random.Random(int(x * 53))
    puff_centers = [
        (top[0] - int(2 * s), top[1] - int(2 * s)),
        (top[0] + int(3 * s), top[1] - int(5 * s)),
        (top[0] - int(1 * s), top[1] - int(9 * s)),
    ]
    r = max(3, int(5 * s))
    for cx, cy in puff_centers:
        color = rng.choice(_V4_PUFFS)
        pygame.draw.circle(surf, _shade(color, -40), (cx, cy + 1), r + 1)
        pygame.draw.circle(surf, color, (cx, cy), r)
        pygame.draw.circle(surf, _mix(color, (255, 255, 255), 0.55),
                           (cx - r // 2, cy - r // 2), max(1, int(2 * s)))


def draw_mountains_v4(surf, scroll, ground_y, w, far_color=None, near_color=None):
    near_color = near_color or (30, 40, 80)

    pts, _ = _hill_polygon(w, ground_y, scroll, 0.06, 95,
                           0.010, 22, 0.027, 10, phase_b=0.8)
    pygame.draw.polygon(surf, _V4_BACK, pts)

    pts, mid_h = _hill_polygon(w, ground_y, scroll, 0.15, 70,
                               0.014, 26, 0.033, 12, phase_b=1.4)
    pygame.draw.polygon(surf, _V4_MID, pts)
    for sx, k, rng in _scatter_trees(scroll, w, 0.15, 40, 7):
        if 0 <= sx < w:
            idx = min(len(mid_h) - 1, max(0, sx // 3))
            ridge_y = mid_h[idx][1]
            _tree_seuss(surf, sx, ridge_y + 4, scale=0.55)

    pts, near_h = _hill_polygon(w, ground_y, scroll, 0.28, 48,
                                0.018, 20, 0.041, 9, phase_b=0.5)
    pygame.draw.polygon(surf, _V4_NEAR, pts)
    for sx, k, rng in _scatter_trees(scroll, w, 0.28, 32, 13):
        if 0 <= sx < w:
            idx = min(len(near_h) - 1, max(0, sx // 3))
            ridge_y = near_h[idx][1]
            _tree_seuss(surf, sx, ridge_y + 4, scale=1.0)

    # Floating sparkles / stars
    rng = random.Random(int(scroll) // 6)
    for _ in range(30):
        sx = rng.randrange(0, w)
        sy = rng.randrange(ground_y - 220, ground_y - 30)
        col = rng.choice(_V4_PUFFS)
        # 4-point star
        pygame.draw.line(surf, col, (sx - 2, sy), (sx + 2, sy), 1)
        pygame.draw.line(surf, col, (sx, sy - 2), (sx, sy + 2), 1)
        pygame.draw.circle(surf, (255, 255, 255), (sx, sy), 1)

    _ambient_overlay(surf, ground_y, w, near_color)


# ──────────────────────────────────────────────────────────────────────────
# V5: Tropical Palm Beach
# ──────────────────────────────────────────────────────────────────────────

_V5_BACK = (190, 215, 220)
_V5_MID = (210, 185, 130)
_V5_NEAR = (220, 200, 120)
_V5_PALM_TRUNK = (120, 85, 55)
_V5_PALM_TRUNK_DK = (75, 55, 35)
_V5_FROND = (45, 115, 55)
_V5_FROND_HI = (110, 180, 75)
_V5_COCONUT = (75, 50, 30)


def _tree_palm(surf, x, y, scale=1.0):
    """Palm tree: curved trunk + drooping fronds + 2 coconuts."""
    s = scale
    trunk_h = int(28 * s)
    # Curved trunk via polyline
    pts = [
        (x, y),
        (x + int(2 * s), y - int(10 * s)),
        (x - int(1 * s), y - int(20 * s)),
        (x + int(2 * s), y - trunk_h),
    ]
    pygame.draw.lines(surf, _V5_PALM_TRUNK, False, pts,
                      max(2, int(3 * s)))
    # Trunk segment marks
    for i in range(0, trunk_h, max(4, int(5 * s))):
        # Approximate x along trunk
        t = i / trunk_h
        # Bilinear pick (close enough at this scale)
        bx = int(pts[0][0] + (pts[3][0] - pts[0][0]) * t
                 + math.sin(t * math.pi) * 2 * s)
        sy = y - i
        pygame.draw.line(surf, _V5_PALM_TRUNK_DK,
                         (bx - int(2 * s), sy), (bx + int(2 * s), sy), 1)

    top = pts[-1]
    cx, cy = top
    # 7 fronds drooping outward in different directions
    frond_dirs = [(-1.1, -0.6), (-1.2, 0.0), (-0.9, 0.7),
                  (0.0, 0.9), (0.9, 0.7), (1.2, 0.0), (1.1, -0.6)]
    for dx, dy in frond_dirs:
        length = int(13 * s)
        steps = 7
        prev = (cx, cy)
        for st in range(1, steps + 1):
            t = st / steps
            # Sag for downward fronds
            sag = (t * t) * 5 * s if dy > 0 else 0
            fx = cx + int(dx * length * t)
            fy = cy + int(dy * length * t + sag)
            r = max(1, int((1.5 - t) * 2.5 * s))
            pygame.draw.line(surf, _V5_FROND, prev, (fx, fy),
                             max(1, int(2 * s)))
            pygame.draw.circle(surf, _V5_FROND_HI, (fx, fy), r)
            prev = (fx, fy)

    # Coconuts at the crown base
    pygame.draw.circle(surf, _V5_COCONUT, (cx - int(2 * s), cy + int(2 * s)),
                       max(1, int(2 * s)))
    pygame.draw.circle(surf, _V5_COCONUT, (cx + int(2 * s), cy + int(1 * s)),
                       max(1, int(2 * s)))


def draw_mountains_v5(surf, scroll, ground_y, w, far_color=None, near_color=None):
    near_color = near_color or (30, 40, 80)

    # Back: hazy sea/sky band (very low ridge)
    pts, _ = _hill_polygon(w, ground_y, scroll, 0.06, 70,
                           0.010, 14, 0.027, 6, phase_b=0.8)
    pygame.draw.polygon(surf, _V5_BACK, pts)

    # Mid: tan sand dunes
    pts, mid_h = _hill_polygon(w, ground_y, scroll, 0.15, 55,
                               0.014, 18, 0.033, 8, phase_b=1.4)
    pygame.draw.polygon(surf, _V5_MID, pts)
    for sx, k, rng in _scatter_trees(scroll, w, 0.15, 50, 7):
        if 0 <= sx < w:
            idx = min(len(mid_h) - 1, max(0, sx // 3))
            ridge_y = mid_h[idx][1]
            _tree_palm(surf, sx, ridge_y + 4, scale=0.55)

    # Near: yellow sand beach
    pts, near_h = _hill_polygon(w, ground_y, scroll, 0.28, 40,
                                0.018, 14, 0.041, 6, phase_b=0.5)
    pygame.draw.polygon(surf, _V5_NEAR, pts)
    for sx, k, rng in _scatter_trees(scroll, w, 0.28, 38, 13):
        if 0 <= sx < w:
            idx = min(len(near_h) - 1, max(0, sx // 3))
            ridge_y = near_h[idx][1]
            _tree_palm(surf, sx, ridge_y + 4, scale=1.0)

    # Tiny seabirds (V-shape) in the distance
    rng = random.Random(int(scroll) // 8)
    for _ in range(8):
        bx = rng.randrange(0, w)
        by = rng.randrange(ground_y - 220, ground_y - 120)
        pygame.draw.line(surf, (60, 50, 50), (bx, by), (bx + 3, by - 2), 1)
        pygame.draw.line(surf, (60, 50, 50), (bx + 3, by - 2), (bx + 6, by), 1)

    # Warm sunlit dust motes
    for _ in range(20):
        dx = rng.randrange(0, w)
        dy = rng.randrange(ground_y - 180, ground_y - 30)
        pygame.draw.circle(surf, (255, 240, 180), (dx, dy), 1)

    _ambient_overlay(surf, ground_y, w, near_color)


# ── dispatcher ─────────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_mountains_v1,
    2: draw_mountains_v2,
    3: draw_mountains_v3,
    4: draw_mountains_v4,
    5: draw_mountains_v5,
}

VARIANT_NAMES = {
    1: "Twisted Bonsai",
    2: "Autumn Maple",
    3: "Bioluminescent Alien",
    4: "Dr. Seuss Truffula",
    5: "Tropical Palm Beach",
}
