"""Sakura mountain variants — 5 tree-style options.

The sakura scene (rolling hills + drifting petals + distant blossoms) is
identical across all five variants; only the foreground tree rendering
function changes. This lets the user compare tree styles fairly.

Each ``draw_mountains_vN`` is a drop-in replacement for
``game.draw.draw_mountains``.
"""
from __future__ import annotations

import math
import random

import pygame


# ── shared palette ─────────────────────────────────────────────────────────

_BACK = (210, 180, 205)
_MID = (200, 140, 165)
_NEAR_GRASS = (135, 170, 110)
_TRUNK = (75, 50, 40)
_BLOSSOM = (255, 180, 205)
_BLOSSOM_HI = (255, 230, 235)
_BLOSSOM_DARK = (220, 130, 170)


# ── shared helpers ─────────────────────────────────────────────────────────

def _clamp(c):
    return max(0, min(255, int(c)))


def _brightness(c) -> float:
    return min(1.0, (c[0] + c[1] + c[2]) / 510.0)


def _warmth(c) -> float:
    return (c[0] - c[2]) / 255.0


def _ambient_overlay(surf, ground_y, w, near_color):
    """Darken at night, warm wash at sunset — preserves theme identity."""
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


def _draw_trunk(surf, base_x, base_y, height, thickness=2):
    pygame.draw.line(surf, _TRUNK,
                     (base_x, base_y),
                     (base_x, base_y - height), thickness)


# ── tree-style helpers (one per variant) ───────────────────────────────────

def _tree_pompom(surf, base_x, base_y, scale=1.0):
    """V1 — round 3-bubble canopy (current style)."""
    trunk_h = int(18 * scale)
    r = int(14 * scale)
    _draw_trunk(surf, base_x, base_y, trunk_h, max(1, int(2 * scale)))
    # Side branches
    pygame.draw.line(surf, _TRUNK,
                     (base_x, base_y - trunk_h + 4),
                     (base_x - 5, base_y - trunk_h - 2), 1)
    pygame.draw.line(surf, _TRUNK,
                     (base_x, base_y - trunk_h + 2),
                     (base_x + 5, base_y - trunk_h - 4), 1)
    cy = base_y - trunk_h - 4
    for dx, dy in ((-r // 2, 1), (r // 2, 1), (0, -r // 3)):
        pygame.draw.circle(surf, _BLOSSOM_DARK, (base_x + dx, cy + dy), r)
    for dx, dy in ((-r // 2, 0), (r // 2, 0), (0, -r // 3 - 1)):
        pygame.draw.circle(surf, _BLOSSOM, (base_x + dx, cy + dy), r - 2)
    pygame.draw.circle(surf, _BLOSSOM_HI,
                       (base_x - r // 2 - 2, cy - 4), max(2, r // 3))
    pygame.draw.circle(surf, _BLOSSOM_HI,
                       (base_x + r // 4, cy - r // 3 - 3), max(2, r // 4))


def _tree_umbrella(surf, base_x, base_y, scale=1.0):
    """V2 — wide flat parasol canopy (Japanese-maple-style)."""
    trunk_h = int(22 * scale)
    canopy_w = int(34 * scale)
    canopy_h = int(9 * scale)
    _draw_trunk(surf, base_x, base_y, trunk_h, max(2, int(2 * scale)))
    cy = base_y - trunk_h
    # Dark outline + main canopy ellipse
    pygame.draw.ellipse(surf, _BLOSSOM_DARK,
                        (base_x - canopy_w // 2 - 1, cy - canopy_h - 1,
                         canopy_w + 2, canopy_h * 2 + 2))
    pygame.draw.ellipse(surf, _BLOSSOM,
                        (base_x - canopy_w // 2, cy - canopy_h,
                         canopy_w, canopy_h * 2))
    # Highlight band on the upper-left
    pygame.draw.ellipse(surf, _BLOSSOM_HI,
                        (base_x - canopy_w // 3, cy - canopy_h + 1,
                         canopy_w // 2, max(2, canopy_h - 1)))
    # Hanging blossom drips below
    for dx in (-canopy_w // 3, 0, canopy_w // 3):
        pygame.draw.circle(surf, _BLOSSOM_DARK,
                           (base_x + dx, cy + canopy_h + 2), 3)
        pygame.draw.circle(surf, _BLOSSOM,
                           (base_x + dx, cy + canopy_h + 1), 2)


def _tree_weeping(surf, base_x, base_y, scale=1.0):
    """V3 — weeping willow with drooping blossom strands."""
    trunk_h = int(24 * scale)
    crown_w = int(22 * scale)
    crown_h = int(6 * scale)
    _draw_trunk(surf, base_x, base_y, trunk_h, max(2, int(2 * scale)))
    crown_y = base_y - trunk_h
    # Small flat crown (the canopy from which strands hang)
    pygame.draw.ellipse(surf, _BLOSSOM_DARK,
                        (base_x - crown_w // 2 - 1, crown_y - crown_h - 1,
                         crown_w + 2, crown_h * 2 + 2))
    pygame.draw.ellipse(surf, _BLOSSOM,
                        (base_x - crown_w // 2, crown_y - crown_h,
                         crown_w, crown_h * 2))
    pygame.draw.ellipse(surf, _BLOSSOM_HI,
                        (base_x - crown_w // 4, crown_y - crown_h + 1,
                         crown_w // 3, max(2, crown_h - 1)))
    # Drooping strands — denser in the middle, shorter at the edges
    step = max(2, int(3 * scale))
    for off in range(-crown_w // 2 + 1, crown_w // 2, step):
        # Strand length tapers toward the outside (parabolic).
        edge_dist = abs(off) / max(1, crown_w // 2)
        strand_len = int((4 + (1.0 - edge_dist) * 18) * scale)
        sx = base_x + off
        sy0 = crown_y + crown_h - 1
        sy1 = sy0 + strand_len
        pygame.draw.line(surf, _BLOSSOM_DARK, (sx, sy0), (sx, sy1), 1)
        # Tiny blossom dots along the strand
        for sy in range(sy0 + 2, sy1, max(2, int(3 * scale))):
            pygame.draw.circle(surf, _BLOSSOM, (sx, sy), 1)
        # Brighter tip blossom at the bottom
        pygame.draw.circle(surf, _BLOSSOM_HI, (sx, sy1), 1)


def _tree_pagoda(surf, base_x, base_y, scale=1.0):
    """V4 — 3-tier stacked horizontal blossom layers (pagoda silhouette)."""
    trunk_h = int(24 * scale)
    _draw_trunk(surf, base_x, base_y, trunk_h, max(2, int(2 * scale)))
    cy = base_y - trunk_h
    tier_gap = int(7 * scale)
    widths = [int(28 * scale), int(22 * scale), int(14 * scale)]
    heights = [int(6 * scale), int(5 * scale), int(4 * scale)]
    for i, (tw, th) in enumerate(zip(widths, heights)):
        ty = cy - i * tier_gap
        # Dark base
        pygame.draw.ellipse(surf, _BLOSSOM_DARK,
                            (base_x - tw // 2 - 1, ty - th - 1,
                             tw + 2, th * 2 + 2))
        # Main blossom
        pygame.draw.ellipse(surf, _BLOSSOM,
                            (base_x - tw // 2, ty - th,
                             tw, th * 2))
        # Highlight
        pygame.draw.ellipse(surf, _BLOSSOM_HI,
                            (base_x - tw // 3, ty - th + 1,
                             max(2, tw // 3), max(1, th - 1)))
    # Top finial tuft
    top_y = cy - len(widths) * tier_gap
    pygame.draw.circle(surf, _BLOSSOM_DARK, (base_x, top_y), max(2, int(3 * scale)))
    pygame.draw.circle(surf, _BLOSSOM, (base_x, top_y), max(1, int(2 * scale)))


def _tree_heart(surf, base_x, base_y, scale=1.0):
    """V5 — heart-shaped canopy (two top lobes + V point)."""
    trunk_h = int(18 * scale)
    r = max(4, int(9 * scale))
    _draw_trunk(surf, base_x, base_y, trunk_h, max(2, int(2 * scale)))
    cy = base_y - trunk_h - r // 2

    # Build the heart silhouette as polygon + circles so the darker
    # outline reads cleanly at small sizes.
    # Dark base — two slightly larger lobes + bottom triangle
    pygame.draw.circle(surf, _BLOSSOM_DARK,
                       (base_x - r // 2, cy - r // 4), r)
    pygame.draw.circle(surf, _BLOSSOM_DARK,
                       (base_x + r // 2, cy - r // 4), r)
    pygame.draw.polygon(surf, _BLOSSOM_DARK,
                        [(base_x - r, cy - r // 4 + 1),
                         (base_x + r, cy - r // 4 + 1),
                         (base_x, cy + r + 1)])
    # Bright fill
    pygame.draw.circle(surf, _BLOSSOM,
                       (base_x - r // 2, cy - r // 4), r - 1)
    pygame.draw.circle(surf, _BLOSSOM,
                       (base_x + r // 2, cy - r // 4), r - 1)
    pygame.draw.polygon(surf, _BLOSSOM,
                        [(base_x - r + 1, cy - r // 4),
                         (base_x + r - 1, cy - r // 4),
                         (base_x, cy + r - 1)])
    # Highlight on one lobe
    pygame.draw.circle(surf, _BLOSSOM_HI,
                       (base_x - r // 2 - 1, cy - r // 2),
                       max(1, r // 3))


TREE_STYLES = {
    1: _tree_pompom,
    2: _tree_umbrella,
    3: _tree_weeping,
    4: _tree_pagoda,
    5: _tree_heart,
}


# ── sakura base scene (shared) ─────────────────────────────────────────────

def _sakura_scene(surf, scroll, ground_y, w, far_color, near_color, tree_fn):
    """Render the hills + petals; place trees using ``tree_fn`` on the
    mid and near layers."""
    # BACK
    pts = [(0, ground_y)]
    for x in range(0, w + 1, 3):
        sx = x + scroll * 0.06
        h = int(95 + math.sin(sx * 0.010) * 22 + math.sin(sx * 0.027 + 0.8) * 10)
        pts.append((x, ground_y - h))
    pts.append((w, ground_y))
    pygame.draw.polygon(surf, _BACK, pts)

    # Distant blossom dots
    rng = random.Random(int(scroll) // 4 + 11)
    for _ in range(45):
        sx = rng.randrange(0, w)
        sy = ground_y - rng.randint(35, 100)
        pygame.draw.circle(surf, _BLOSSOM, (sx, sy), 1)

    # MID
    pts = [(0, ground_y)]
    mid_heights = []
    for x in range(0, w + 1, 3):
        sx = x + scroll * 0.15
        h = int(70 + math.sin(sx * 0.014) * 26 + math.sin(sx * 0.033 + 1.4) * 12)
        pts.append((x, ground_y - h))
        mid_heights.append((x, ground_y - h))
    pts.append((w, ground_y))
    pygame.draw.polygon(surf, _MID, pts)

    # Distant trees on mid layer (smaller scale)
    mid_step = 38
    mid_phase = scroll * 0.15
    first = int(mid_phase // mid_step) - 1
    last = int((mid_phase + w) // mid_step) + 2
    for k in range(first, last + 1):
        rng = random.Random((k * 1103515245 + 12345) & 0xFFFFFFFF)
        wx = k * mid_step + rng.uniform(-10, 10)
        sx = int(wx - mid_phase)
        if 0 <= sx < w:
            idx = min(len(mid_heights) - 1, max(0, sx // 3))
            ridge_y = mid_heights[idx][1]
            tree_fn(surf, sx, ridge_y + 4, scale=0.55)

    # NEAR — green hills
    pts = [(0, ground_y)]
    near_heights = []
    for x in range(0, w + 1, 3):
        sx = x + scroll * 0.28
        h = int(48 + math.sin(sx * 0.018) * 20 + math.sin(sx * 0.041 + 0.5) * 9)
        pts.append((x, ground_y - h))
        near_heights.append((x, ground_y - h))
    pts.append((w, ground_y))
    pygame.draw.polygon(surf, _NEAR_GRASS, pts)

    # Hero trees on near layer
    near_step = 28
    near_phase = scroll * 0.28
    first = int(near_phase // near_step) - 1
    last = int((near_phase + w) // near_step) + 2
    for k in range(first, last + 1):
        rng = random.Random((k * 2654435761 + 7) & 0xFFFFFFFF)
        wx = k * near_step + rng.uniform(-6, 6)
        sx = int(wx - near_phase)
        if 0 <= sx < w:
            idx = min(len(near_heights) - 1, max(0, sx // 3))
            ridge_y = near_heights[idx][1]
            tree_fn(surf, sx, ridge_y + 4, scale=1.0)

    # Drifting petals in the air
    rng = random.Random(int(scroll) // 7)
    for _ in range(35):
        px = rng.randrange(0, w)
        py = rng.randrange(ground_y - 200, ground_y - 30)
        pygame.draw.ellipse(surf, _BLOSSOM, (px, py, 4, 2))
        if rng.random() < 0.4:
            pygame.draw.ellipse(surf, _BLOSSOM_HI, (px, py, 2, 1))

    _ambient_overlay(surf, ground_y, w, near_color)


# ── public variant entry points ────────────────────────────────────────────

def draw_mountains_v1(surf, scroll, ground_y, w, far_color=None, near_color=None):
    _sakura_scene(surf, scroll, ground_y, w,
                  far_color or (50, 60, 110),
                  near_color or (30, 40, 80),
                  _tree_pompom)


def draw_mountains_v2(surf, scroll, ground_y, w, far_color=None, near_color=None):
    _sakura_scene(surf, scroll, ground_y, w,
                  far_color or (50, 60, 110),
                  near_color or (30, 40, 80),
                  _tree_umbrella)


def draw_mountains_v3(surf, scroll, ground_y, w, far_color=None, near_color=None):
    _sakura_scene(surf, scroll, ground_y, w,
                  far_color or (50, 60, 110),
                  near_color or (30, 40, 80),
                  _tree_weeping)


def draw_mountains_v4(surf, scroll, ground_y, w, far_color=None, near_color=None):
    _sakura_scene(surf, scroll, ground_y, w,
                  far_color or (50, 60, 110),
                  near_color or (30, 40, 80),
                  _tree_pagoda)


def draw_mountains_v5(surf, scroll, ground_y, w, far_color=None, near_color=None):
    _sakura_scene(surf, scroll, ground_y, w,
                  far_color or (50, 60, 110),
                  near_color or (30, 40, 80),
                  _tree_heart)


VARIANTS = {
    1: draw_mountains_v1,
    2: draw_mountains_v2,
    3: draw_mountains_v3,
    4: draw_mountains_v4,
    5: draw_mountains_v5,
}

VARIANT_NAMES = {
    1: "Sakura Pom-pom (original)",
    2: "Sakura Umbrella",
    3: "Sakura Weeping willow",
    4: "Sakura Tiered pagoda",
    5: "Sakura Heart canopy",
}
