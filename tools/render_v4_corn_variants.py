"""V4 Corn Dog Crispy - 5 batter/topping treatments (picker).

Round-1 V4 was a single golden-batter rod with crispy bumps + honey-
mustard drips + wooden stick at the gap. This picker explores 5
distinct batter / texture / topping directions while keeping the basic
silhouette (corn-dog rod + stick at gap) consistent.

5 variants:
  v4_corn1 Classic Golden  rich golden batter, dense round crispy
                           bumps, honey-mustard drips, single stick
                           with red ribbon at the gap
  v4_corn2 Spicy Buffalo   red-orange tinted batter, hot-sauce drips
                           + cooling ranch-cream drips, chilli pepper
                           accent at gap, red-ribbon stick
  v4_corn3 Sesame Crusted  lighter tan-gold batter with sesame seeds
                           embedded throughout, double crossed sticks
                           at the gap, subtle drips
  v4_corn4 Cheesy Beer     amber beer-batter rod, melted-cheese drips
                           with green chive sprinkles, waffle-pattern
                           cross-hatch bumps for a denser fried look
  v4_corn5 Pretzel Wrap    dark mahogany pretzel-style crust + salt
                           grain dots + mustard squiggle running the
                           length, faint twisted-pretzel scoring lines

Picker only - no game/ files modified.
"""
import contextlib
import math
import random

import pygame
import pygame.gfxdraw as gfx

from game import entities as gent
from game import pillar_variants as gpv


# ----- Cartoon palette ------------------------------------------------------

# Standard fried crust
CRUST_HI  = (250, 212, 118)
CRUST_MID = (224, 162,  62)
CRUST_LO  = (148,  84,  20)
CRUMB     = (255, 232, 168)

# Spicy buffalo
SPICY_HI  = (244, 162,  88)
SPICY_MID = (212,  92,  40)
SPICY_LO  = (148,  44,  16)
HOT_HI    = (240,  82,  50)
HOT_MID   = (190,  44,  28)
RANCH_HI  = (252, 246, 230)
RANCH_MID = (220, 212, 184)

# Sesame light
SESAME_HI  = (255, 232, 158)
SESAME_MID = (240, 196,  98)
SESAME_LO  = (170, 116,  44)

# Beer batter (amber)
BEER_HI   = (252, 222, 140)
BEER_MID  = (222, 178,  68)
BEER_LO   = (158, 108,  40)
CHEESE    = (252, 184,  60)
CHEESE_HI = (255, 220, 110)
CHIVE_HI  = (160, 220,  90)
CHIVE_MID = ( 86, 168,  56)

# Pretzel
PRETZEL_HI  = (172, 110,  56)
PRETZEL_MID = (118,  64,  24)
PRETZEL_LO  = ( 64,  30,  12)
SALT_COLOR  = (252, 248, 240)

# Condiments
MUSTARD     = (252, 206,  56)
MUSTARD_HI  = (255, 234, 130)
HONEY_MID   = (244, 178,  60)
HONEY_HI    = (255, 222, 130)
LETTUCE_HI  = (140, 200,  78)
LETTUCE_LO  = ( 52, 106,  40)

# Stick / ribbon
WOOD_HI     = (230, 192, 132)
WOOD_LO     = (162, 116,  62)
RIBBON_HI   = (232,  80,  64)
RIBBON_LO   = (162,  32,  28)

OUTLINE = ( 38,  22,  10)
SHADOW  = ( 22,  14,   8)


# ----- Utility primitives ---------------------------------------------------

def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _aa_filled_circle(surf, cx, cy, r, color):
    cx, cy, r = int(cx), int(cy), int(r)
    if r < 1:
        return
    gfx.filled_circle(surf, cx, cy, r, color)
    gfx.aacircle(surf, cx, cy, r, color)


def draw_drip(surf, x, y, length, *, color, hi=None, width=4):
    """Vertical drip with rounded blob at the bottom."""
    pygame.draw.line(surf, OUTLINE, (x, y), (x, y + length), width + 2)
    pygame.draw.line(surf, _shade(color, -40), (x, y), (x, y + length), width)
    pygame.draw.line(surf, color, (x - 1, y), (x - 1, y + length - 2),
                     max(1, width - 2))
    _aa_filled_circle(surf, x, y + length, max(3, width), OUTLINE)
    _aa_filled_circle(surf, x, y + length, max(2, width - 1), color)
    if hi is not None:
        _aa_filled_circle(surf, x - 1, y + length - 1, max(1, width - 3), hi)


# ----- Corn-dog body --------------------------------------------------------

def _draw_rod_body(surf, rect, *, batter_lo, batter_mid, batter_hi,
                   flat_top=False):
    """Rod-shaped batter body. Returns the rod rect for further decoration.

    `flat_top=True` squares off the top corners so the top pillar visually
    connects to the ceiling instead of appearing to float just below it."""
    x, y, w, h = rect
    rod = pygame.Rect(x - 1, y, w + 2, h)
    radius = max(8, w // 2 + 2)
    if flat_top:
        rad_kwargs = dict(border_top_left_radius=0,
                          border_top_right_radius=0,
                          border_bottom_left_radius=radius,
                          border_bottom_right_radius=radius)
    else:
        rad_kwargs = dict(border_radius=radius)
    # Drop shadow
    pygame.draw.rect(surf, (*SHADOW, 60),
                     rod.inflate(6, 6).move(2, 2), **rad_kwargs)
    pygame.draw.rect(surf, OUTLINE, rod.inflate(4, 4), **rad_kwargs)
    pygame.draw.rect(surf, batter_lo, rod.inflate(2, 2), **rad_kwargs)
    pygame.draw.rect(surf, batter_mid, rod, **rad_kwargs)
    # Lit-side highlight (left third) - always rounded, lives inside the rod
    hl = pygame.Rect(rod.x + 4, rod.y + 4,
                     max(3, rod.width // 3), rod.height - 8)
    pygame.draw.rect(surf, batter_hi, hl, border_radius=radius // 2)
    return rod


def _scatter_round_bumps(surf, rod, *, lo, mid, hi=CRUMB, density=5, seed=0):
    """Dense scatter of round crispy bumps with shadow + highlight pairs."""
    rng = random.Random(seed * 19 + 7)
    n = max(28, rod.height // density)
    for _ in range(n):
        bx = rng.randint(rod.x + 3, rod.right - 3)
        by = rng.randint(rod.y + 4, rod.bottom - 4)
        r = rng.randint(2, 4)
        _aa_filled_circle(surf, bx + 1, by + 1, r, _shade(lo, -10))
        _aa_filled_circle(surf, bx, by, r, _shade(mid, +18))
        _aa_filled_circle(surf, bx - 1, by - 1, max(1, r - 2), hi)


def _scatter_sesame(surf, rod, n, *, seed=0):
    """Tiny ivory tear-drop sesame seeds scattered inside the rod outline."""
    rng = random.Random(seed * 31 + 13)
    for _ in range(n):
        sx = rng.randint(rod.x + 3, rod.right - 3)
        sy = rng.randint(rod.y + 4, rod.bottom - 4)
        pygame.draw.ellipse(surf, OUTLINE,
                            pygame.Rect(sx - 2, sy - 1, 4, 3))
        pygame.draw.ellipse(surf, (250, 234, 196),
                            pygame.Rect(sx - 1, sy - 1, 3, 2))


def _scatter_salt_grains(surf, rod, n, *, seed=0):
    rng = random.Random(seed * 41 + 19)
    for _ in range(n):
        sx = rng.randint(rod.x + 3, rod.right - 3)
        sy = rng.randint(rod.y + 4, rod.bottom - 4)
        _aa_filled_circle(surf, sx + 1, sy + 1, 2, OUTLINE)
        _aa_filled_circle(surf, sx, sy, 2, SALT_COLOR)
        _aa_filled_circle(surf, sx - 1, sy - 1, 1, (255, 255, 255))


def _scatter_chive_dots(surf, rod, n, *, seed=0):
    """Tiny green chive flakes sprinkled across the rod."""
    rng = random.Random(seed * 53 + 7)
    for _ in range(n):
        sx = rng.randint(rod.x + 4, rod.right - 4)
        sy = rng.randint(rod.y + 4, rod.bottom - 4)
        # 2-pixel chive sliver
        pygame.draw.line(surf, OUTLINE, (sx, sy), (sx + 2, sy), 2)
        pygame.draw.line(surf, CHIVE_MID, (sx, sy), (sx + 2, sy), 1)
        _aa_filled_circle(surf, sx + 1, sy - 1, 1, CHIVE_HI)


def _waffle_pattern_bumps(surf, rod, *, lo, mid, hi=CRUMB, seed=0):
    """Cross-hatch / waffle-pattern bumps - small squares in a grid."""
    rng = random.Random(seed * 23 + 11)
    step_x = 6
    step_y = 7
    for gy in range(rod.y + 6, rod.bottom - 4, step_y):
        offset_x = (gy // step_y) % 2 * (step_x // 2)
        for gx in range(rod.x + 4 + offset_x, rod.right - 4, step_x):
            jx = rng.randint(-1, 1)
            jy = rng.randint(-1, 1)
            sq = pygame.Rect(gx + jx, gy + jy, 3, 3)
            pygame.draw.rect(surf, _shade(lo, -10), sq.inflate(2, 2))
            pygame.draw.rect(surf, _shade(mid, +18), sq)
            _aa_filled_circle(surf, sq.x, sq.y, 1, hi)


def _twisted_scoring(surf, rod, *, color, n_lines=None):
    """Subtle pretzel-twist diagonal scoring lines on the surface."""
    if n_lines is None:
        n_lines = max(3, rod.height // 18)
    for i in range(n_lines):
        y0 = rod.y + 4 + i * (rod.height - 8) // max(1, n_lines - 1)
        pygame.draw.line(surf, color,
                         (rod.x + 3, y0),
                         (rod.right - 3, y0 + 6), 1)


def _draw_wood_stick(surf, cx, top_y, length, *, ribbon_color=None):
    """Wooden stick poking into the gap. Optional red ribbon tied at top."""
    stick_w = 10
    stick = pygame.Rect(cx - stick_w // 2, top_y, stick_w, length)
    pygame.draw.rect(surf, OUTLINE, stick.inflate(2, 2), border_radius=4)
    pygame.draw.rect(surf, WOOD_LO, stick, border_radius=4)
    pygame.draw.rect(surf, WOOD_HI,
                     pygame.Rect(stick.x + 2, stick.y + 2, 3, stick.height - 4),
                     border_radius=2)
    for i in range(2):
        pygame.draw.line(surf, _shade(WOOD_LO, -40),
                         (stick.x + 2, stick.y + 6 + i * 8),
                         (stick.right - 2, stick.y + 6 + i * 8), 1)
    if ribbon_color is not None:
        rib_y = stick.y + 4
        rib = pygame.Rect(stick.x - 2, rib_y, stick_w + 4, 5)
        pygame.draw.rect(surf, OUTLINE, rib.inflate(2, 2), border_radius=2)
        pygame.draw.rect(surf, ribbon_color, rib, border_radius=2)
        for sgn, anchor_x in ((-1, stick.x), (+1, stick.right)):
            tail_pts = [
                (anchor_x + sgn * 0, rib_y + 2),
                (anchor_x + sgn * 7, rib_y - 2),
                (anchor_x + sgn * 5, rib_y + 6),
            ]
            pygame.draw.polygon(surf, OUTLINE,
                                [(p[0], p[1] + 1) for p in tail_pts])
            pygame.draw.polygon(surf, ribbon_color, tail_pts)


def _draw_chili_pepper(surf, cx, cy):
    pygame.draw.ellipse(surf, OUTLINE,
                        pygame.Rect(cx - 8, cy - 3, 16, 8))
    pygame.draw.ellipse(surf, HOT_MID,
                        pygame.Rect(cx - 7, cy - 2, 14, 6))
    pygame.draw.ellipse(surf, HOT_HI,
                        pygame.Rect(cx - 5, cy - 2, 8, 3))
    pygame.draw.line(surf, LETTUCE_LO, (cx - 6, cy - 3), (cx - 9, cy - 6), 2)
    pygame.draw.line(surf, CHIVE_HI, (cx - 6, cy - 3), (cx - 8, cy - 5), 1)


# ============================================================================
# 5 corn-dog variants
# ============================================================================

def draw_v4_corn1(surf, top_rect, bot_rect, palette, seed):
    """V4-corn1 Classic Golden - rich golden batter + honey-mustard drips.
    Plain wooden skewer at the gap (no ribbon). Top pillar's rod has a
    flat top edge so it visually connects to the ceiling."""
    for r, side in ((top_rect, 'top'), (bot_rect, 'bot')):
        rod = _draw_rod_body(surf, r, batter_lo=CRUST_LO,
                             batter_mid=CRUST_MID, batter_hi=CRUST_HI,
                             flat_top=(side == 'top'))
        _scatter_round_bumps(surf, rod, lo=CRUST_LO, mid=CRUST_MID,
                             hi=CRUMB, seed=seed + (1 if side == 'top' else 2))
        # Honey-mustard drips (3 staggered)
        for i, dx in enumerate((rod.x + 4, rod.right - 6, rod.centerx + 4)):
            dy = rod.y + 18 + i * 22
            if dy + 22 < rod.bottom:
                draw_drip(surf, dx, dy, 22 + (i % 2) * 4,
                          color=HONEY_MID, hi=HONEY_HI, width=4)
    _draw_wood_stick(surf, top_rect.centerx, top_rect.bottom - 2, 26,
                     ribbon_color=None)
    _draw_wood_stick(surf, bot_rect.centerx, bot_rect.top - 26, 26,
                     ribbon_color=None)


def draw_v4_corn2(surf, top_rect, bot_rect, palette, seed):
    """V4-corn2 Spicy Buffalo - red-tinted batter + hot sauce + ranch."""
    for r, side in ((top_rect, 'top'), (bot_rect, 'bot')):
        rod = _draw_rod_body(surf, r, batter_lo=SPICY_LO,
                             batter_mid=SPICY_MID, batter_hi=SPICY_HI)
        _scatter_round_bumps(surf, rod, lo=SPICY_LO, mid=SPICY_MID,
                             hi=CRUMB, seed=seed + (1 if side == 'top' else 2))
        # Hot sauce drips (one side) + ranch drips (other side)
        draw_drip(surf, rod.x + 4,    rod.y + 22, 24,
                  color=HOT_MID, hi=HOT_HI, width=5)
        draw_drip(surf, rod.right - 6, rod.y + 40, 22,
                  color=RANCH_MID, hi=RANCH_HI, width=4)
        draw_drip(surf, rod.x + 4,    rod.y + 64, 18,
                  color=HOT_MID, hi=HOT_HI, width=4)
    # Tiny chilli pepper accent at each gap edge
    _draw_chili_pepper(surf, bot_rect.centerx - 14, bot_rect.top + 6)
    _draw_chili_pepper(surf, top_rect.centerx + 14, top_rect.bottom - 6)
    _draw_wood_stick(surf, top_rect.centerx, top_rect.bottom - 2, 26,
                     ribbon_color=HOT_MID)
    _draw_wood_stick(surf, bot_rect.centerx, bot_rect.top - 26, 26,
                     ribbon_color=HOT_MID)


def draw_v4_corn3(surf, top_rect, bot_rect, palette, seed):
    """V4-corn3 Sesame Crusted - light tan + sesame seeds + double sticks."""
    for r, side in ((top_rect, 'top'), (bot_rect, 'bot')):
        rod = _draw_rod_body(surf, r, batter_lo=SESAME_LO,
                             batter_mid=SESAME_MID, batter_hi=SESAME_HI)
        _scatter_round_bumps(surf, rod, lo=SESAME_LO, mid=SESAME_MID,
                             hi=CRUMB,
                             seed=seed + (1 if side == 'top' else 2))
        _scatter_sesame(surf, rod, n=max(10, rod.height // 12),
                        seed=seed + (3 if side == 'top' else 5))
        # Subtle honey-mustard drip
        draw_drip(surf, rod.x + 4, rod.y + 24, 18,
                  color=HONEY_MID, hi=HONEY_HI, width=3)
        draw_drip(surf, rod.right - 6, rod.y + 50, 16,
                  color=HONEY_MID, hi=HONEY_HI, width=3)
    # Double crossed sticks at each gap end
    cx_t = top_rect.centerx
    _draw_wood_stick(surf, cx_t - 4, top_rect.bottom - 2, 24,
                     ribbon_color=RIBBON_HI)
    _draw_wood_stick(surf, cx_t + 4, top_rect.bottom + 2, 22,
                     ribbon_color=None)
    cx_b = bot_rect.centerx
    _draw_wood_stick(surf, cx_b - 4, bot_rect.top - 24, 24,
                     ribbon_color=RIBBON_HI)
    _draw_wood_stick(surf, cx_b + 4, bot_rect.top - 22, 22,
                     ribbon_color=None)


def draw_v4_corn4(surf, top_rect, bot_rect, palette, seed):
    """V4-corn4 Cheesy Beer - amber batter + cheese drips + chive sprinkles."""
    for r, side in ((top_rect, 'top'), (bot_rect, 'bot')):
        rod = _draw_rod_body(surf, r, batter_lo=BEER_LO,
                             batter_mid=BEER_MID, batter_hi=BEER_HI)
        # Waffle-pattern bumps (denser, more textured than round bumps)
        _waffle_pattern_bumps(surf, rod, lo=BEER_LO, mid=BEER_MID, hi=CRUMB,
                              seed=seed + (1 if side == 'top' else 2))
        # Chive sprinkles
        _scatter_chive_dots(surf, rod, n=max(8, rod.height // 14),
                            seed=seed + (7 if side == 'top' else 11))
        # Cheese drips (thicker, fewer)
        draw_drip(surf, rod.x + 5, rod.y + 26, 24,
                  color=CHEESE, hi=CHEESE_HI, width=5)
        draw_drip(surf, rod.right - 7, rod.y + 50, 22,
                  color=CHEESE, hi=CHEESE_HI, width=5)
    _draw_wood_stick(surf, top_rect.centerx, top_rect.bottom - 2, 26,
                     ribbon_color=CHIVE_MID)
    _draw_wood_stick(surf, bot_rect.centerx, bot_rect.top - 26, 26,
                     ribbon_color=CHIVE_MID)


def draw_v4_corn5(surf, top_rect, bot_rect, palette, seed):
    """V4-corn5 Pretzel Wrap - dark mahogany pretzel crust + salt + mustard."""
    for r, side in ((top_rect, 'top'), (bot_rect, 'bot')):
        rod = _draw_rod_body(surf, r, batter_lo=PRETZEL_LO,
                             batter_mid=PRETZEL_MID, batter_hi=PRETZEL_HI)
        # Twisted scoring lines (subtle pretzel twist)
        _twisted_scoring(surf, rod, color=_shade(PRETZEL_LO, -10))
        # Salt grain dots
        _scatter_salt_grains(surf, rod, n=max(12, rod.height // 10),
                             seed=seed + (1 if side == 'top' else 2))
        # Mustard squiggle running the length
        n_pts = max(6, rod.height // 14)
        amp = max(3, rod.width // 4)
        cx = rod.centerx
        pts = [(cx + (amp if i % 2 == 0 else -amp),
                rod.y + 8 + i * (rod.height - 16) // max(1, n_pts - 1))
               for i in range(n_pts)]
        pygame.draw.lines(surf, _shade(MUSTARD, -40), False, pts, 5)
        pygame.draw.lines(surf, MUSTARD, False, pts, 3)
        pygame.draw.lines(surf, MUSTARD_HI, False, pts, 1)
    _draw_wood_stick(surf, top_rect.centerx, top_rect.bottom - 2, 26,
                     ribbon_color=MUSTARD)
    _draw_wood_stick(surf, bot_rect.centerx, bot_rect.top - 26, 26,
                     ribbon_color=MUSTARD)


# ----- Variant registry -----------------------------------------------------

V4_CORN_VARIANTS = {
    'v4_corn1': ("V4-corn1 Classic Golden",  draw_v4_corn1),
    'v4_corn2': ("V4-corn2 Spicy Buffalo",   draw_v4_corn2),
    'v4_corn3': ("V4-corn3 Sesame Crusted",  draw_v4_corn3),
    'v4_corn4': ("V4-corn4 Cheesy Beer",     draw_v4_corn4),
    'v4_corn5': ("V4-corn5 Pretzel Wrap",    draw_v4_corn5),
}


@contextlib.contextmanager
def install_variant(key: str):
    """Monkey-patch draw_pillar_pair so every pillar uses the chosen V4
    corn-dog variant. Patches BOTH game.pillar_variants AND game.entities
    (the import binding in entities.py is what Pipe.draw actually calls)."""
    if key not in V4_CORN_VARIANTS:
        raise ValueError(f"unknown V4 corn variant {key!r}; valid: "
                         f"{sorted(V4_CORN_VARIANTS)}")
    _, fn = V4_CORN_VARIANTS[key]
    saved = []

    def _patch(module, attr, replacement):
        saved.append((module, attr, getattr(module, attr)))
        setattr(module, attr, replacement)

    _patch(gpv,  'draw_pillar_pair', fn)
    _patch(gent, 'draw_pillar_pair', fn)
    try:
        yield
    finally:
        for module, attr, orig in reversed(saved):
            setattr(module, attr, orig)
