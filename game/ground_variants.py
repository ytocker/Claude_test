"""Ground-rendering variants used for design exploration.

Each ``draw_ground_vN`` function is a drop-in replacement for
``game.draw.draw_ground`` — same signature, same scrolling behaviour.
Each variant has its own dominant palette and decoration vocabulary; the
biome ``top_color`` / ``mid_color`` / ``bot_color`` inputs feed a thin
ambient overlay so day/sunset/night still feels right while the theme
identity dominates.
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


def _lerp_color(a, b, t):
    return _mix(a, b, t)


def _brightness(c) -> float:
    return min(1.0, (c[0] + c[1] + c[2]) / 510.0)


def _warmth(c) -> float:
    return (c[0] - c[2]) / 255.0


def _vertical_gradient(surf, x0, y0, x1, y1, top, bot):
    """Fill a vertical band with a linear top→bot gradient."""
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / max(1, h - 1)
        c = _lerp_color(top, bot, t)
        pygame.draw.line(surf, c, (x0, y0 + i), (x1 - 1, y0 + i))


def _ambient_ground_overlay(surf, ground_y, w, h, mid_color):
    """Translucent overlay on the ground band so the theme still responds
    to time-of-day. Darken at night, warm wash at sunset."""
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
    """Yield (sx, k, rng) for deterministic per-step decoration."""
    phase = scroll * speed
    first = int(phase // step) - 1
    last = int((phase + w) // step) + 2
    for k in range(first, last + 1):
        rng = random.Random((k * 2654435761 ^ seed_off) & 0xFFFFFFFF)
        wx = k * step + rng.uniform(-step * 0.25, step * 0.25)
        sx = int(wx - phase)
        if -20 < sx < w + 20:
            yield sx, k, rng


# ──────────────────────────────────────────────────────────────────────────
# V1: Wildflower Meadow
# ──────────────────────────────────────────────────────────────────────────

_V1_GRASS_TOP = (90, 200, 80)
_V1_GRASS_MID = (45, 145, 50)
_V1_GRASS_DK = (25, 90, 35)
_V1_DIRT_TOP = (95, 70, 45)
_V1_DIRT_DEEP = (55, 38, 25)
_V1_FLOWER_RED = (235, 80, 80)
_V1_FLOWER_YELLOW = (255, 220, 90)
_V1_FLOWER_WHITE = (250, 248, 240)
_V1_FLOWER_PINK = (250, 170, 210)
_V1_FLOWER_PURPLE = (190, 130, 230)
_V1_CLOVER = (90, 180, 100)
_V1_DANDELION = (255, 245, 200)
_V1_ROCK = (140, 130, 115)


def _v1_flower(surf, x, y, color):
    """4-petal flower with bright center."""
    pygame.draw.circle(surf, color, (x - 1, y), 1)
    pygame.draw.circle(surf, color, (x + 1, y), 1)
    pygame.draw.circle(surf, color, (x, y - 1), 1)
    pygame.draw.circle(surf, color, (x, y + 1), 1)
    pygame.draw.circle(surf, _V1_FLOWER_YELLOW, (x, y), 1)


def _v1_butterfly(surf, x, y, color):
    """Tiny 2-wing butterfly."""
    pygame.draw.circle(surf, color, (x - 1, y), 2)
    pygame.draw.circle(surf, color, (x + 2, y), 2)
    pygame.draw.line(surf, (40, 30, 30), (x, y - 1), (x, y + 1), 1)


def draw_ground_v1(surf, ground_y, w, h, scroll,
                   top_color=None, mid_color=None, bot_color=None):
    mid_color = mid_color or _V1_GRASS_MID

    grass_h = 22
    _vertical_gradient(surf, 0, ground_y, w, ground_y + grass_h,
                       _V1_GRASS_TOP, _V1_GRASS_MID)
    _vertical_gradient(surf, 0, ground_y + grass_h, w, h,
                       _V1_DIRT_TOP, _V1_DIRT_DEEP)

    # Sparse darker grass tufts spanning the full grass strip
    for sx, k, rng in _scatter(scroll, w, 0.7, 5, 11):
        if 0 <= sx < w:
            tuft_h = rng.randint(3, 9)
            lean = rng.randint(-2, 2)
            base_y = ground_y + rng.randint(0, 4)
            pygame.draw.line(surf, _V1_GRASS_DK,
                             (sx, base_y), (sx + lean, base_y - tuft_h), 1)
            pygame.draw.line(surf, _V1_GRASS_TOP,
                             (sx, base_y), (sx + lean, base_y - tuft_h + 1), 1)

    # Tall hero blades poking above the ground line
    for sx, k, rng in _scatter(scroll, w, 0.7, 11, 23):
        if 0 <= sx < w:
            tuft_h = rng.randint(7, 12)
            base_y = ground_y + rng.randint(0, 2)
            lean = rng.randint(-2, 2)
            pygame.draw.line(surf, _V1_GRASS_DK,
                             (sx, base_y), (sx + lean, base_y - tuft_h), 1)
            pygame.draw.line(surf, _V1_GRASS_TOP,
                             (sx + 1, base_y), (sx + 1 + lean, base_y - tuft_h + 1), 1)

    # Flowers — varied colours, just above the grass line
    flower_palette = [_V1_FLOWER_RED, _V1_FLOWER_YELLOW, _V1_FLOWER_WHITE,
                      _V1_FLOWER_PINK, _V1_FLOWER_PURPLE]
    for sx, k, rng in _scatter(scroll, w, 0.7, 22, 37):
        if 0 <= sx < w:
            col = rng.choice(flower_palette)
            fy = ground_y + rng.randint(-2, 6)
            # short stem
            pygame.draw.line(surf, _V1_GRASS_DK,
                             (sx, fy + 3), (sx, fy), 1)
            _v1_flower(surf, sx, fy, col)

    # Dandelion puffballs
    for sx, k, rng in _scatter(scroll, w, 0.7, 55, 53):
        if 0 <= sx < w and rng.random() < 0.6:
            fy = ground_y + rng.randint(-3, 4)
            pygame.draw.line(surf, _V1_GRASS_DK,
                             (sx, fy + 4), (sx, fy), 1)
            pygame.draw.circle(surf, _V1_DANDELION, (sx, fy), 2)
            pygame.draw.circle(surf, (255, 255, 255), (sx, fy), 1)

    # Small rocks half-buried
    for sx, k, rng in _scatter(scroll, w, 0.7, 70, 67):
        if 0 <= sx < w and rng.random() < 0.55:
            ry = ground_y + 10 + rng.randint(0, 8)
            rw = rng.randint(4, 7)
            pygame.draw.ellipse(surf, _V1_ROCK,
                                (sx - rw // 2, ry, rw, 3))
            pygame.draw.line(surf, _shade(_V1_ROCK, 30),
                             (sx - rw // 2 + 1, ry),
                             (sx + rw // 2 - 2, ry), 1)

    # A butterfly here and there hovering above the ground
    for sx, k, rng in _scatter(scroll, w, 0.7, 130, 91):
        if 0 <= sx < w and rng.random() < 0.5:
            by = ground_y - rng.randint(8, 22)
            col = rng.choice([_V1_FLOWER_YELLOW, _V1_FLOWER_PINK,
                              _V1_FLOWER_PURPLE])
            _v1_butterfly(surf, sx, by, col)

    # Edge highlight
    pygame.draw.line(surf, _shade(_V1_GRASS_TOP, 60),
                     (0, ground_y), (w - 1, ground_y), 1)

    _ambient_ground_overlay(surf, ground_y, w, h, mid_color)


# ──────────────────────────────────────────────────────────────────────────
# V2: Mossy Cobblestone Path
# ──────────────────────────────────────────────────────────────────────────

_V2_STONE_LIGHT = (175, 170, 155)
_V2_STONE_MID = (125, 120, 105)
_V2_STONE_DARK = (75, 70, 60)
_V2_MORTAR = (55, 45, 38)
_V2_MOSS_DK = (50, 100, 55)
_V2_MOSS_LT = (110, 175, 90)
_V2_PUDDLE = (140, 175, 210)
_V2_PUDDLE_HI = (210, 230, 250)
_V2_WEED = (90, 150, 70)
_V2_IVY_DK = (35, 90, 45)


def _v2_cobble(surf, x, y, sw, sh, rng):
    """One rounded stone with light/shadow shading and mortar outline."""
    # Mortar (dark outline)
    pygame.draw.ellipse(surf, _V2_MORTAR,
                        (x - sw // 2 - 1, y - 1, sw + 2, sh + 2))
    base = _mix(_V2_STONE_MID, _V2_STONE_LIGHT, rng.random() * 0.6)
    pygame.draw.ellipse(surf, base,
                        (x - sw // 2, y, sw, sh))
    # Highlight on top-left
    pygame.draw.ellipse(surf, _mix(base, _V2_STONE_LIGHT, 0.6),
                        (x - sw // 2 + 1, y + 1, sw // 2, sh // 2))
    # Shadow on bottom-right
    pygame.draw.ellipse(surf, _shade(base, -30),
                        (x - 1, y + sh // 2, sw // 2 + 1, sh // 2))


def draw_ground_v2(surf, ground_y, w, h, scroll,
                   top_color=None, mid_color=None, bot_color=None):
    mid_color = mid_color or _V2_STONE_MID

    # Dirt base under stones
    _vertical_gradient(surf, 0, ground_y, w, h,
                       _V2_MORTAR, _shade(_V2_MORTAR, -20))

    # Two staggered rows of cobblestones
    rows = [(ground_y + 4, 0), (ground_y + 18, 11)]
    for row_y, stagger in rows:
        for sx, k, rng in _scatter(scroll, w, 0.7, 22, 7 + row_y):
            if -10 <= sx + stagger < w + 10:
                sw = rng.randint(16, 22)
                sh = rng.randint(8, 12)
                _v2_cobble(surf, sx + stagger, row_y, sw, sh, rng)

    # Moss patches in the gaps
    for sx, k, rng in _scatter(scroll, w, 0.7, 16, 19):
        if 0 <= sx < w and rng.random() < 0.7:
            my = ground_y + rng.choice([12, 28]) + rng.randint(-2, 2)
            for _ in range(rng.randint(3, 6)):
                mx = sx + rng.randint(-4, 4)
                col = rng.choice([_V2_MOSS_DK, _V2_MOSS_LT, _V2_MOSS_DK])
                pygame.draw.circle(surf, col, (mx, my + rng.randint(-1, 1)), 1)

    # Puddles between stones — reflect sky-ish color
    for sx, k, rng in _scatter(scroll, w, 0.7, 95, 31):
        if 0 <= sx < w and rng.random() < 0.55:
            pw = rng.randint(8, 14)
            py = ground_y + rng.choice([10, 24])
            pygame.draw.ellipse(surf, _V2_PUDDLE,
                                (sx - pw // 2, py, pw, 3))
            pygame.draw.line(surf, _V2_PUDDLE_HI,
                             (sx - pw // 2 + 1, py),
                             (sx + pw // 2 - 2, py), 1)

    # Weeds sprouting between stones
    for sx, k, rng in _scatter(scroll, w, 0.7, 30, 53):
        if 0 <= sx < w and rng.random() < 0.6:
            wh = rng.randint(4, 8)
            pygame.draw.line(surf, _V2_WEED,
                             (sx, ground_y + 2),
                             (sx - 1, ground_y + 2 - wh), 1)
            pygame.draw.line(surf, _V2_WEED,
                             (sx + 1, ground_y + 2),
                             (sx + 2, ground_y + 2 - wh + 1), 1)

    # Ivy along the top edge — dangling
    for sx, k, rng in _scatter(scroll, w, 0.7, 14, 71):
        if 0 <= sx < w and rng.random() < 0.4:
            for dy in range(rng.randint(2, 6)):
                col = _V2_IVY_DK if dy % 2 == 0 else _V2_MOSS_DK
                pygame.draw.circle(surf, col, (sx, ground_y - dy), 1)

    # Edge highlight (worn stone)
    pygame.draw.line(surf, _shade(_V2_STONE_LIGHT, 20),
                     (0, ground_y - 1), (w - 1, ground_y - 1), 1)

    _ambient_ground_overlay(surf, ground_y, w, h, mid_color)


# ──────────────────────────────────────────────────────────────────────────
# V3: Sandy Beach
# ──────────────────────────────────────────────────────────────────────────

_V3_SAND_LIGHT = (245, 225, 175)
_V3_SAND_MID = (220, 195, 140)
_V3_SAND_DARK = (175, 145, 95)
_V3_WET_SAND = (155, 130, 95)
_V3_SHELL_PINK = (250, 200, 190)
_V3_SHELL_CREAM = (255, 240, 215)
_V3_SHELL_DARK = (170, 110, 90)
_V3_PEBBLE_GRAY = (170, 165, 155)
_V3_PEBBLE_DARK = (115, 110, 100)
_V3_SEAWEED = (90, 140, 95)
_V3_DRIFTWOOD = (130, 100, 75)
_V3_DRIFTWOOD_DK = (85, 60, 40)


def _v3_shell_spiral(surf, x, y):
    pygame.draw.circle(surf, _V3_SHELL_DARK, (x, y), 3)
    pygame.draw.circle(surf, _V3_SHELL_PINK, (x, y), 2)
    pygame.draw.circle(surf, _V3_SHELL_CREAM, (x, y - 1), 1)


def _v3_shell_scallop(surf, x, y):
    pygame.draw.polygon(surf, _V3_SHELL_DARK,
                        [(x - 3, y), (x + 3, y), (x, y - 3)])
    pygame.draw.polygon(surf, _V3_SHELL_PINK,
                        [(x - 2, y), (x + 2, y), (x, y - 2)])
    pygame.draw.line(surf, _V3_SHELL_DARK,
                     (x, y - 2), (x, y), 1)


def _v3_footprint(surf, x, y):
    pygame.draw.ellipse(surf, _V3_WET_SAND, (x, y, 4, 2))
    pygame.draw.circle(surf, _V3_WET_SAND, (x + 1, y - 2), 1)
    pygame.draw.circle(surf, _V3_WET_SAND, (x + 3, y - 2), 1)


def draw_ground_v3(surf, ground_y, w, h, scroll,
                   top_color=None, mid_color=None, bot_color=None):
    mid_color = mid_color or _V3_SAND_MID

    # Wet-sand back stripe (the "shoreline" hint)
    wet_band_h = 5
    pygame.draw.rect(surf, _V3_WET_SAND, (0, ground_y, w, wet_band_h))
    # Foam ripples
    off = int(scroll * 0.4) % 14
    for fx in range(-off, w, 14):
        pygame.draw.line(surf, _V3_SAND_LIGHT,
                         (fx, ground_y), (fx + 6, ground_y), 1)

    # Dry sand below
    _vertical_gradient(surf, 0, ground_y + wet_band_h, w, h,
                       _V3_SAND_LIGHT, _V3_SAND_DARK)

    # Sand grain noise speckles
    rng_speck = random.Random(int(scroll) // 4 + 113)
    for _ in range(60):
        sx = rng_speck.randrange(0, w)
        sy = rng_speck.randrange(ground_y + wet_band_h + 1, h - 1)
        pygame.draw.line(surf, _V3_SAND_DARK, (sx, sy), (sx, sy), 1)

    # Seaweed strands lying on the wet sand
    for sx, k, rng in _scatter(scroll, w, 0.7, 60, 7):
        if 0 <= sx < w and rng.random() < 0.65:
            wy = ground_y + 1
            for j in range(rng.randint(4, 7)):
                wx = sx + j + rng.randint(-1, 1)
                pygame.draw.line(surf, _V3_SEAWEED, (wx, wy), (wx, wy + 1), 1)

    # Pebbles
    for sx, k, rng in _scatter(scroll, w, 0.7, 24, 23):
        if 0 <= sx < w:
            py = ground_y + wet_band_h + rng.randint(2, 30)
            pr = rng.choice([1, 1, 2])
            col = rng.choice([_V3_PEBBLE_GRAY, _V3_PEBBLE_DARK])
            pygame.draw.circle(surf, col, (sx, py), pr)
            if pr == 2:
                pygame.draw.circle(surf, _shade(col, 30), (sx - 1, py - 1), 1)

    # Shells (spiral or scallop)
    for sx, k, rng in _scatter(scroll, w, 0.7, 50, 41):
        if 0 <= sx < w and rng.random() < 0.7:
            sy = ground_y + wet_band_h + rng.randint(4, 28)
            if rng.random() < 0.5:
                _v3_shell_spiral(surf, sx, sy)
            else:
                _v3_shell_scallop(surf, sx, sy)

    # Footprints trail
    for sx, k, rng in _scatter(scroll, w, 0.7, 38, 67):
        if 0 <= sx < w and rng.random() < 0.45:
            fy = ground_y + 12 + (k % 3) * 5
            _v3_footprint(surf, sx, fy)

    # Driftwood — occasional
    for sx, k, rng in _scatter(scroll, w, 0.7, 160, 89):
        if 0 <= sx < w and rng.random() < 0.6:
            dy = ground_y + 18
            dw = rng.randint(14, 22)
            pygame.draw.rect(surf, _V3_DRIFTWOOD_DK,
                             (sx - dw // 2, dy, dw, 3))
            pygame.draw.rect(surf, _V3_DRIFTWOOD,
                             (sx - dw // 2, dy, dw, 2))
            # Bark marks
            for m in range(2, dw - 2, 4):
                pygame.draw.line(surf, _V3_DRIFTWOOD_DK,
                                 (sx - dw // 2 + m, dy),
                                 (sx - dw // 2 + m, dy + 2), 1)

    # Top edge — soft, no harsh line
    pygame.draw.line(surf, _shade(_V3_WET_SAND, 20),
                     (0, ground_y), (w - 1, ground_y), 1)

    _ambient_ground_overlay(surf, ground_y, w, h, mid_color)


# ──────────────────────────────────────────────────────────────────────────
# V4: Snowy Tundra
# ──────────────────────────────────────────────────────────────────────────

_V4_SNOW_TOP = (245, 250, 255)
_V4_SNOW_MID = (215, 225, 240)
_V4_SNOW_SHADE = (175, 195, 220)
_V4_ICE = (180, 220, 240)
_V4_ICE_HI = (240, 250, 255)
_V4_GRASS_BROWN = (160, 125, 80)
_V4_GRASS_BROWN_DK = (90, 65, 40)
_V4_PINECONE_DK = (90, 60, 35)
_V4_PINECONE_LT = (160, 115, 70)
_V4_FOOTPRINT = (170, 185, 210)


def _v4_snowflake(surf, x, y):
    pygame.draw.line(surf, (255, 255, 255), (x - 1, y), (x + 1, y), 1)
    pygame.draw.line(surf, (255, 255, 255), (x, y - 1), (x, y + 1), 1)


def _v4_pinecone(surf, x, y):
    pygame.draw.ellipse(surf, _V4_PINECONE_DK, (x - 2, y - 1, 5, 4))
    pygame.draw.line(surf, _V4_PINECONE_LT, (x - 1, y), (x + 1, y), 1)
    pygame.draw.line(surf, _V4_PINECONE_LT, (x - 1, y + 2), (x + 1, y + 2), 1)


def _v4_footprint(surf, x, y):
    pygame.draw.ellipse(surf, _V4_FOOTPRINT, (x, y, 4, 2))


def draw_ground_v4(surf, ground_y, w, h, scroll,
                   top_color=None, mid_color=None, bot_color=None):
    mid_color = mid_color or _V4_SNOW_MID

    # Snow band with cool-blue undertone
    _vertical_gradient(surf, 0, ground_y, w, ground_y + 14,
                       _V4_SNOW_TOP, _V4_SNOW_MID)
    _vertical_gradient(surf, 0, ground_y + 14, w, h,
                       _V4_SNOW_MID, _V4_SNOW_SHADE)

    # Drifted bumps along the top edge — uneven snow line
    drift_pts = []
    for x in range(0, w + 1, 4):
        sx = x + scroll * 0.7
        wave = int(math.sin(sx * 0.05) * 2 + math.sin(sx * 0.13 + 1.0) * 1)
        drift_pts.append((x, ground_y + wave))
    drift_pts = [(0, ground_y + 4)] + drift_pts + [(w, ground_y + 4)]
    pygame.draw.polygon(surf, _V4_SNOW_TOP, drift_pts)

    # Ice crystal sparkles scattered on the snow
    for sx, k, rng in _scatter(scroll, w, 0.7, 18, 19):
        if 0 <= sx < w and rng.random() < 0.75:
            sy = ground_y + rng.randint(3, 28)
            _v4_snowflake(surf, sx, sy)

    # Brighter ice patches
    for sx, k, rng in _scatter(scroll, w, 0.7, 90, 47):
        if 0 <= sx < w and rng.random() < 0.6:
            iy = ground_y + rng.randint(6, 22)
            iw = rng.randint(8, 14)
            pygame.draw.ellipse(surf, _V4_ICE, (sx - iw // 2, iy, iw, 4))
            pygame.draw.line(surf, _V4_ICE_HI,
                             (sx - iw // 2 + 1, iy + 1),
                             (sx + iw // 2 - 2, iy + 1), 1)

    # Brown grass tufts poking through
    for sx, k, rng in _scatter(scroll, w, 0.7, 26, 31):
        if 0 <= sx < w and rng.random() < 0.6:
            tuft_h = rng.randint(5, 9)
            by = ground_y + rng.randint(0, 4)
            for lean in (-1, 0, 1):
                pygame.draw.line(surf, _V4_GRASS_BROWN_DK,
                                 (sx + lean, by),
                                 (sx + lean, by - tuft_h), 1)
            pygame.draw.line(surf, _V4_GRASS_BROWN,
                             (sx, by), (sx, by - tuft_h + 1), 1)

    # Footprint trail
    for sx, k, rng in _scatter(scroll, w, 0.7, 22, 67):
        if 0 <= sx < w and rng.random() < 0.5:
            fy = ground_y + 8 + (k % 4) * 4
            _v4_footprint(surf, sx, fy)

    # Pinecones — occasional
    for sx, k, rng in _scatter(scroll, w, 0.7, 140, 83):
        if 0 <= sx < w and rng.random() < 0.55:
            cy = ground_y + 20
            _v4_pinecone(surf, sx, cy)

    # Drifting snowflakes in the air just above ground
    air_rng = random.Random(int(scroll) // 5 + 7)
    for _ in range(15):
        fx = air_rng.randrange(0, w)
        fy = air_rng.randrange(ground_y - 30, ground_y - 3)
        _v4_snowflake(surf, fx, fy)

    # Edge highlight
    pygame.draw.line(surf, (255, 255, 255),
                     (0, ground_y - 1), (w - 1, ground_y - 1), 1)

    _ambient_ground_overlay(surf, ground_y, w, h, mid_color)


# ──────────────────────────────────────────────────────────────────────────
# V5: Enchanted Forest Floor
# ──────────────────────────────────────────────────────────────────────────

_V5_LOAM_TOP = (95, 75, 55)
_V5_LOAM_MID = (65, 50, 38)
_V5_LOAM_DEEP = (35, 25, 20)
_V5_LEAF_RED = (200, 80, 60)
_V5_LEAF_ORANGE = (235, 145, 60)
_V5_LEAF_YELLOW = (240, 200, 90)
_V5_LEAF_BROWN = (130, 90, 50)
_V5_MUSH_CAP = (215, 70, 70)
_V5_MUSH_CAP_DK = (155, 40, 40)
_V5_MUSH_STEM = (240, 230, 200)
_V5_FERN = (60, 130, 70)
_V5_FERN_HI = (110, 200, 100)
_V5_GLOW_FLOWER = (180, 230, 255)
_V5_GLOW_FLOWER_HI = (250, 255, 230)
_V5_TWIG = (75, 55, 35)


def _v5_mushroom(surf, x, y):
    """Tiny red-cap mushroom with white spots."""
    pygame.draw.rect(surf, _V5_MUSH_STEM, (x - 1, y - 1, 2, 3))
    pygame.draw.ellipse(surf, _V5_MUSH_CAP_DK, (x - 3, y - 4, 7, 4))
    pygame.draw.ellipse(surf, _V5_MUSH_CAP, (x - 3, y - 4, 7, 3))
    pygame.draw.circle(surf, (255, 255, 255), (x - 1, y - 3), 1)
    pygame.draw.circle(surf, (255, 255, 255), (x + 1, y - 2), 1)


def _v5_fern_frond(surf, x, y, height):
    pygame.draw.line(surf, _V5_FERN, (x, y), (x, y - height), 1)
    for j in range(2, height, 2):
        pygame.draw.line(surf, _V5_FERN,
                         (x, y - j), (x - 2, y - j - 1), 1)
        pygame.draw.line(surf, _V5_FERN,
                         (x, y - j), (x + 2, y - j - 1), 1)
    pygame.draw.circle(surf, _V5_FERN_HI, (x, y - height), 1)


def _v5_leaf(surf, x, y, color):
    pygame.draw.ellipse(surf, _shade(color, -30), (x, y, 4, 2))
    pygame.draw.ellipse(surf, color, (x, y, 3, 2))


def _v5_glow_flower(surf, x, y):
    """Small bioluminescent flower with halo."""
    halo = pygame.Surface((9, 9), pygame.SRCALPHA)
    pygame.draw.circle(halo, (180, 230, 255, 80), (4, 4), 4)
    pygame.draw.circle(halo, (220, 240, 255, 150), (4, 4), 2)
    surf.blit(halo, (x - 4, y - 4))
    pygame.draw.circle(surf, _V5_GLOW_FLOWER_HI, (x, y), 1)


def _v5_firefly(surf, x, y):
    halo = pygame.Surface((9, 9), pygame.SRCALPHA)
    pygame.draw.circle(halo, (255, 240, 130, 90), (4, 4), 4)
    pygame.draw.circle(halo, (255, 250, 200, 220), (4, 4), 1)
    surf.blit(halo, (x - 4, y - 4))


def draw_ground_v5(surf, ground_y, w, h, scroll,
                   top_color=None, mid_color=None, bot_color=None):
    mid_color = mid_color or _V5_LOAM_MID

    # Loam band
    _vertical_gradient(surf, 0, ground_y, w, ground_y + 14,
                       _V5_LOAM_TOP, _V5_LOAM_MID)
    _vertical_gradient(surf, 0, ground_y + 14, w, h,
                       _V5_LOAM_MID, _V5_LOAM_DEEP)

    # Soil noise speckles
    rng_n = random.Random(int(scroll) // 4 + 5)
    for _ in range(50):
        sx = rng_n.randrange(0, w)
        sy = rng_n.randrange(ground_y + 1, h - 1)
        col = rng_n.choice([_V5_LOAM_DEEP, _V5_LEAF_BROWN])
        pygame.draw.line(surf, col, (sx, sy), (sx, sy), 1)

    # Fallen leaves
    leaf_palette = [_V5_LEAF_RED, _V5_LEAF_ORANGE, _V5_LEAF_YELLOW, _V5_LEAF_BROWN]
    for sx, k, rng in _scatter(scroll, w, 0.7, 12, 7):
        if 0 <= sx < w:
            ly = ground_y + rng.randint(3, 30)
            col = rng.choice(leaf_palette)
            _v5_leaf(surf, sx, ly, col)

    # Twigs
    for sx, k, rng in _scatter(scroll, w, 0.7, 60, 31):
        if 0 <= sx < w and rng.random() < 0.6:
            ty = ground_y + rng.randint(10, 30)
            tw = rng.randint(5, 9)
            pygame.draw.line(surf, _V5_TWIG, (sx, ty), (sx + tw, ty + 1), 1)

    # Ferns
    for sx, k, rng in _scatter(scroll, w, 0.7, 36, 53):
        if 0 <= sx < w and rng.random() < 0.6:
            fh = rng.randint(7, 11)
            _v5_fern_frond(surf, sx, ground_y + 2, fh)

    # Mushroom clusters (rings) — 2–3 per cluster
    for sx, k, rng in _scatter(scroll, w, 0.7, 65, 71):
        if 0 <= sx < w:
            for off in (-4, 0, 5):
                if rng.random() < 0.75:
                    my = ground_y + 6 + rng.randint(-2, 4)
                    _v5_mushroom(surf, sx + off, my)

    # Glowing flowers
    for sx, k, rng in _scatter(scroll, w, 0.7, 80, 97):
        if 0 <= sx < w and rng.random() < 0.75:
            gy = ground_y + rng.randint(4, 28)
            _v5_glow_flower(surf, sx, gy)

    # Fireflies hovering above the ground
    fire_rng = random.Random(int(scroll) // 5 + 19)
    glow_layer = pygame.Surface((w, h - ground_y + 40), pygame.SRCALPHA)
    for _ in range(14):
        fx = fire_rng.randrange(0, w)
        fy = fire_rng.randrange(ground_y - 35, ground_y + 5)
        _v5_firefly(glow_layer, fx, fy - (ground_y - 40))
    surf.blit(glow_layer, (0, ground_y - 40))

    # Edge — soft mossy line
    pygame.draw.line(surf, _V5_FERN_HI,
                     (0, ground_y - 1), (w - 1, ground_y - 1), 1)

    _ambient_ground_overlay(surf, ground_y, w, h, mid_color)


# ── dispatcher ─────────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_ground_v1,
    2: draw_ground_v2,
    3: draw_ground_v3,
    4: draw_ground_v4,
    5: draw_ground_v5,
}

VARIANT_NAMES = {
    1: "Wildflower Meadow",
    2: "Mossy Cobblestone Path",
    3: "Sandy Beach",
    4: "Snowy Tundra",
    5: "Enchanted Forest Floor",
}
