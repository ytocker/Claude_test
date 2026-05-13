"""KFC powerup fries-mountains: 3 variants randomly picked per activation.

When the KFC powerup is active, the background mountain silhouettes
get swapped for piles of French fries. The variant pool below holds
the 3 picked designs - one is chosen at random per `_activate_kfc`
call (see World.kfc_mountain_variant) and used for the duration of
that powerup window.

Variants:
    0  Classic Spilled Fries  dense scatter of golden fry sticks at
                              varied tilts filling the silhouette
    1  Fries Box Skyline      red+white striped fries cartons with
                              fries poking out the top, varied heights
    2  Curly Fry Spirals      dense scatter of spring-shaped curls
                              filling the silhouette

All variants keep the existing 3-layer parallax shape + scroll
multipliers (back x0.06 / far x0.15 / near x0.28) from
game.draw.draw_mountains so the depth feel is preserved - only the
silhouette content changes.
"""
import math
import random

import pygame

from game.pillar_kfc import (
    OUTLINE, KFC_RED, KFC_RED_D, KFC_WHITE,
    CRUST_HI, CRUST_MID, CRUST_LO, CRUMB,
)


# --- Palette extensions for fries -----------------------------------------

FRY_LIGHT = (252, 220, 130)
FRY_GOLD  = (244, 192,  82)
FRY_DEEP  = (200, 140,  40)
FRY_DARK  = (138,  84,  18)
SALT      = (252, 248, 240)


def _layer_shade(color, layer):
    """Tint a colour for the 3 parallax layers.
    layer=0 (back): heavily faded toward sky
    layer=1 (far):  lightly faded
    layer=2 (near): unchanged
    """
    if layer == 0:
        mix = (180, 160, 200)
        return tuple(int((color[i] + mix[i]) / 2) for i in range(3))
    if layer == 1:
        mix = (210, 180, 200)
        return tuple(int(color[i] * 0.72 + mix[i] * 0.28) for i in range(3))
    return color


def _outline_for_layer(layer):
    if layer == 0:
        return (90, 70, 90)
    if layer == 1:
        return (60, 36, 18)
    return OUTLINE


# --- Horizon shape (mirrors draw_mountains) -------------------------------

def horizon_y(x, scroll, ground_y, layer):
    """y-coordinate of the silhouette top at x for the given parallax
    layer. Matches the sine stack used by game.draw.draw_mountains."""
    if layer == 0:
        bx = x + scroll * 0.06
        h = 105 + math.sin(bx * 0.008) * 32 + math.sin(bx * 0.023 + 2.1) * 14
    elif layer == 1:
        fx = x + scroll * 0.15
        h = 80 + math.sin(fx * 0.012) * 42 + math.sin(fx * 0.031) * 22
    else:
        nx = x + scroll * 0.019 * 14
        h = 55 + math.sin(nx * 0.019 + 1.4) * 34 + math.sin(nx * 0.047 + 0.7) * 16
    return int(ground_y - h)


# --- Single-fry sprite ----------------------------------------------------

def draw_fry(surf, cx, cy, length, *, tilt_deg=0,
              light=FRY_LIGHT, gold=FRY_GOLD, deep=FRY_DEEP,
              outline=OUTLINE, salt_dots=0, seed=0):
    """A golden fry stick. Supersampled 3x then smoothscaled down for
    sharp rounded ends + clean rotation."""
    SS = 3
    fw = max(4, length // 7)
    big_len = length * SS
    big_fw = fw * SS
    layer = pygame.Surface((big_len + 18, big_fw + 18), pygame.SRCALPHA)
    rect = pygame.Rect(9, 9, big_len, big_fw)
    radius = big_fw // 2 + SS
    pygame.draw.rect(layer, outline, rect.inflate(2 * SS, 2 * SS),
                     border_radius=radius)
    pygame.draw.rect(layer, deep, rect.inflate(SS, SS), border_radius=radius)
    pygame.draw.rect(layer, gold, rect, border_radius=radius)
    hl = pygame.Rect(rect.x + 2 * SS, rect.y + SS, rect.width - 4 * SS,
                     max(SS, big_fw // 3))
    pygame.draw.rect(layer, light, hl, border_radius=max(SS, big_fw // 3))
    if salt_dots:
        rng = random.Random(seed)
        for _ in range(salt_dots):
            sx = rng.randint(rect.left + 2 * SS, rect.right - 2 * SS)
            sy = rng.randint(rect.top + SS, rect.bottom - SS)
            pygame.draw.circle(layer, SALT, (sx, sy), SS)
    if tilt_deg:
        layer = pygame.transform.rotate(layer, tilt_deg)
    target_w = max(1, layer.get_width() // SS)
    target_h = max(1, layer.get_height() // SS)
    layer = pygame.transform.smoothscale(layer, (target_w, target_h))
    rect = layer.get_rect(center=(cx, cy))
    surf.blit(layer, rect.topleft)


# --- Curly fry sprite -----------------------------------------------------

def draw_curly_fry(surf, cx, cy, *, radius=14, turns=2.2, color=FRY_GOLD,
                    deep=FRY_DEEP, outline=OUTLINE, light=FRY_LIGHT,
                    tilt_deg=0):
    """Spring-shaped fry curl drawn as a polyline along a spiral."""
    size = radius * 2 + 12
    layer = pygame.Surface((size, size), pygame.SRCALPHA)
    cx_l, cy_l = size // 2, size // 2
    n = max(24, int(turns * 18))
    pts = []
    for i in range(n):
        u = i / max(1, n - 1)
        a = u * turns * 2 * math.pi
        r = radius * (0.45 + 0.55 * u)
        x = cx_l + math.cos(a) * r
        y = cy_l + math.sin(a) * r * 0.55
        pts.append((x, y))
    if len(pts) >= 2:
        pygame.draw.lines(layer, outline, False, pts, 7)
        pygame.draw.lines(layer, deep, False, pts, 5)
        pygame.draw.lines(layer, color, False, pts, 4)
        hi_pts = [(p[0], p[1] - 1) for p in pts]
        pygame.draw.lines(layer, light, False, hi_pts, 1)
    if tilt_deg:
        layer = pygame.transform.rotate(layer, tilt_deg)
    rect = layer.get_rect(center=(cx, cy))
    surf.blit(layer, rect.topleft)


# --- Fries carton (McD-style) ---------------------------------------------

def draw_fry_carton(surf, base_x, base_y, w_top, h, *,
                     stripe_color=KFC_RED, stripe_count=5,
                     outline=OUTLINE, layer_idx=2):
    """Trapezoid fries carton with red+white stripes. base_x/base_y is
    the BOTTOM-CENTRE; returns rim_y so the caller can stack fries
    on top."""
    bot_w = max(int(w_top * 0.75), 16)
    rim_y = base_y - h
    tl = (base_x - w_top // 2, rim_y)
    tr = (base_x + w_top // 2, rim_y)
    br = (base_x + bot_w // 2, base_y)
    bl = (base_x - bot_w // 2, base_y)
    poly = [tl, tr, br, bl]
    pygame.draw.polygon(surf, outline,
                        [(p[0], p[1] + 1) for p in poly])
    white = _layer_shade(KFC_WHITE, layer_idx)
    pygame.draw.polygon(surf, white, poly)
    red = _layer_shade(stripe_color, layer_idx)
    for i in range(stripe_count):
        u0 = (i + 0.10) / stripe_count
        u1 = (i + 0.58) / stripe_count
        sx0_top = tl[0] + (tr[0] - tl[0]) * u0
        sx1_top = tl[0] + (tr[0] - tl[0]) * u1
        sx0_bot = bl[0] + (br[0] - bl[0]) * u0
        sx1_bot = bl[0] + (br[0] - bl[0]) * u1
        pygame.draw.polygon(
            surf, red,
            [(sx0_top, tl[1]), (sx1_top, tl[1]),
             (sx1_bot, br[1]), (sx0_bot, br[1])])
    pygame.draw.polygon(surf, outline, poly, 2)
    rim_band = pygame.Rect(tl[0] - 2, rim_y - 4, w_top + 4, 7)
    pygame.draw.rect(surf, outline, rim_band.inflate(2, 2), border_radius=3)
    pygame.draw.rect(surf, _layer_shade(KFC_RED_D, layer_idx),
                      rim_band, border_radius=3)
    pygame.draw.rect(surf, red, rim_band.inflate(-4, -3), border_radius=2)
    return rim_y


# ============================================================================
# Variant 0: Classic Spilled Fries
# ============================================================================

def _classic_layer(surf, scroll, ground_y, w, layer):
    fry_light = _layer_shade(FRY_LIGHT, layer)
    fry_gold = _layer_shade(FRY_GOLD, layer)
    fry_deep = _layer_shade(FRY_DEEP, layer)
    outline = _outline_for_layer(layer)
    rng = random.Random(int(scroll) * 17 + layer * 1337)
    n_fries = (300, 450, 700)[layer]
    length_range = ((8, 14), (12, 22), (16, 30))[layer]
    salt_dots = (0, 1, 2)[layer]
    fries = []
    for _ in range(n_fries):
        x = rng.randint(-12, w + 12)
        hy = horizon_y(x, scroll, ground_y, layer)
        if hy >= ground_y:
            continue
        y = rng.randint(hy, ground_y - 1)
        tilt = rng.uniform(-85, 85)
        L = rng.randint(*length_range)
        fries.append((y, x, L, tilt))
    fries.sort(key=lambda f: -f[0])
    for (y, x, L, tilt) in fries:
        draw_fry(surf, x, y, L, tilt_deg=tilt,
                  light=fry_light, gold=fry_gold, deep=fry_deep,
                  outline=outline, salt_dots=salt_dots,
                  seed=x * 7 + y * 11 + layer)


def draw_fries_classic(surf, scroll, ground_y, w):
    for layer in (0, 1, 2):
        _classic_layer(surf, scroll, ground_y, w, layer)


# ============================================================================
# Variant 1: Fries Box Skyline
# ============================================================================

def _boxes_layer(surf, scroll, ground_y, w, layer):
    spacing = (60, 50, 44)[layer]
    carton_w_range = ((34, 50), (38, 56), (42, 64))[layer]
    fry_count_range = ((4, 6), (5, 8), (6, 10))[layer]
    rng = random.Random(int(scroll) * 17 + layer * 99 + 7)
    outline = _outline_for_layer(layer)
    fry_light = _layer_shade(FRY_LIGHT, layer)
    fry_gold = _layer_shade(FRY_GOLD, layer)
    fry_deep = _layer_shade(FRY_DEEP, layer)
    x = -spacing // 2
    while x < w + spacing // 2:
        hy = horizon_y(x, scroll, ground_y, layer)
        carton_h = ground_y - hy + rng.randint(-6, 6)
        carton_h = max(40, carton_h)
        c_w = rng.randint(*carton_w_range)
        rim_y = draw_fry_carton(surf, x, ground_y, c_w, carton_h,
                                  layer_idx=layer)
        n_fries = rng.randint(*fry_count_range)
        fry_max_len = (16, 22, 30)[layer]
        for _ in range(n_fries):
            off = rng.uniform(-c_w / 2 + 4, c_w / 2 - 4)
            tilt = rng.uniform(-30, 30)
            L = rng.randint(fry_max_len - 6, fry_max_len)
            draw_fry(surf, int(x + off), rim_y - L // 2 + 2, L,
                      tilt_deg=tilt + 90,
                      light=fry_light, gold=fry_gold, deep=fry_deep,
                      outline=outline, salt_dots=0)
        x += spacing + rng.randint(-8, 8)


def draw_fries_boxes(surf, scroll, ground_y, w):
    for layer in (0, 1, 2):
        _boxes_layer(surf, scroll, ground_y, w, layer)


# ============================================================================
# Variant 2: Curly Fry Spirals
# ============================================================================

def _curly_layer(surf, scroll, ground_y, w, layer):
    light = _layer_shade(FRY_LIGHT, layer)
    gold = _layer_shade(FRY_GOLD, layer)
    deep = _layer_shade(FRY_DEEP, layer)
    outline = _outline_for_layer(layer)
    rng = random.Random(int(scroll) * 17 + layer * 311 + 11)
    n_curls = (160, 240, 360)[layer]
    radius_range = ((4, 8), (6, 11), (9, 14))[layer]
    curls = []
    for _ in range(n_curls):
        x = rng.randint(-12, w + 12)
        hy = horizon_y(x, scroll, ground_y, layer)
        if hy >= ground_y:
            continue
        y = rng.randint(hy, ground_y - 1)
        r = rng.randint(*radius_range)
        tilt = rng.uniform(-45, 45)
        turns = rng.uniform(1.6, 2.6)
        curls.append((y, x, r, tilt, turns))
    curls.sort(key=lambda c: -c[0])
    for (y, x, r, tilt, turns) in curls:
        draw_curly_fry(surf, x, y, radius=r, turns=turns,
                        color=gold, deep=deep, outline=outline,
                        light=light, tilt_deg=tilt)


def draw_fries_curly(surf, scroll, ground_y, w):
    for layer in (0, 1, 2):
        _curly_layer(surf, scroll, ground_y, w, layer)


# ============================================================================
# Dispatcher
# ============================================================================

KFC_MOUNTAIN_DRAWERS = (
    draw_fries_classic,
    draw_fries_boxes,
    draw_fries_curly,
)


def draw_kfc_mountains(surf, scroll, ground_y, w, variant_idx):
    """Route to one of the 3 fries-mountain variants. `variant_idx` is
    stable for the duration of a single KFC powerup activation (set
    on _activate_kfc in World)."""
    KFC_MOUNTAIN_DRAWERS[variant_idx % len(KFC_MOUNTAIN_DRAWERS)](
        surf, scroll, ground_y, w)
