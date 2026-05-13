"""5-design picker for KFC-mode fries-mountains.

When the KFC powerup is active the existing background mountain
silhouettes get swapped for piles of French fries. This script renders
5 visually distinct candidates as full 360x640 gameplay frames so the
user can pick one to integrate into game/draw.py.

The 3 parallax layers (back / far / near) keep the same sine-stacked
horizon shape and scroll multipliers (0.06 / 0.15 / 0.28) that the
existing draw_mountains() uses - the depth feel is preserved; only
the silhouette content changes from "stone slabs" to "fries".

Run from the repo root:

    PYTHONPATH=. python tools/render_kfc_mountains_picker.py

Output:
    docs/kfc_powerup/fries_mountains/
        v1.png       Classic Spilled Fries
        v2.png       Fries Box Skyline
        v3.png       Curly Fry Spirals
        v4.png       Waffle-Cut Stacks
        v5.png       Loaded Cheesy Fries
        compare.png  5-column strip with labels
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H, GAP_START, GROUND_Y, KFC_GAP_BOOST
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_cloud, draw_ground,
)
from game.entities import Pipe
from game.pillar_kfc import (
    OUTLINE, KFC_RED, KFC_RED_D, KFC_WHITE,
    CRUST_HI, CRUST_MID, CRUST_LO, CRUMB,
)


# --- Palette extensions for fries ------------------------------------------

FRY_LIGHT     = (252, 220, 130)
FRY_GOLD      = (244, 192,  82)
FRY_DEEP      = (200, 140,  40)
FRY_DARK      = (138,  84,  18)
SALT          = (252, 248, 240)
CHEESE        = (252, 184,  60)
CHEESE_HI     = (255, 220, 110)
KETCHUP       = (216,  44,  40)


# --- Layer shading: back -> far -> near (less saturated -> full) -----------

def _layer_shade(color, layer):
    """Tint a colour for the 3 parallax layers.
    layer=0 (back): heavily faded toward sky
    layer=1 (far):  lightly faded
    layer=2 (near): unchanged
    """
    if layer == 0:
        # 50/50 blend with a sky-ish blue-violet (pulls hue cool + lighter)
        mix = (180, 160, 200)
        return tuple(int((color[i] + mix[i]) / 2) for i in range(3))
    if layer == 1:
        mix = (210, 180, 200)
        return tuple(int(color[i] * 0.72 + mix[i] * 0.28) for i in range(3))
    return color


def _outline_for_layer(layer):
    """Darker -> dimmer outline per depth layer."""
    if layer == 0:
        return (90, 70, 90)
    if layer == 1:
        return (60, 36, 18)
    return OUTLINE


# --- Sine-horizon helper (mirrors draw_mountains) --------------------------

def horizon_y(x, scroll, ground_y, layer):
    """y-coordinate of the silhouette top at x for the given parallax layer.

    layer 0 = back (highest), 1 = far, 2 = near (lowest). Matches the
    sine stack used by game.draw.draw_mountains so depth + scroll feel
    are unchanged.
    """
    if layer == 0:
        bx = x + scroll * 0.06
        h = 105 + math.sin(bx * 0.008) * 32 + math.sin(bx * 0.023 + 2.1) * 14
    elif layer == 1:
        fx = x + scroll * 0.15
        h = 80 + math.sin(fx * 0.012) * 42 + math.sin(fx * 0.031) * 22
    else:
        nx = x + scroll * 0.019 * 14   # near layer step factor
        h = 55 + math.sin(nx * 0.019 + 1.4) * 34 + math.sin(nx * 0.047 + 0.7) * 16
    return int(ground_y - h)


def horizon_points(scroll, ground_y, w, layer, step=2):
    """Return a list of (x, y) along the silhouette top of `layer`."""
    return [(x, horizon_y(x, scroll, ground_y, layer))
            for x in range(0, w + 1, step)]


# --- Single-fry sprite ----------------------------------------------------

def draw_fry(surf, cx, cy, length, *, tilt_deg=0,
              light=FRY_LIGHT, gold=FRY_GOLD, deep=FRY_DEEP,
              outline=OUTLINE, salt_dots=0, seed=0):
    """A golden fry stick: rounded rectangle, dark outline, lit-side
    highlight stripe + optional salt sprinkles.

    Supersampled 3x: everything is drawn on an oversized canvas at 3x
    the target dimensions (so curves + rotations stay smooth), then
    smoothscaled DOWN to target. The downscale acts as a low-pass
    filter against the aliased edges of pygame.draw primitives.
    """
    SS = 3
    fw = max(4, length // 7)
    big_len = length * SS
    big_fw = fw * SS
    layer = pygame.Surface((big_len + 18, big_fw + 18), pygame.SRCALPHA)
    rect = pygame.Rect(9, 9, big_len, big_fw)
    radius = big_fw // 2 + SS
    pygame.draw.rect(layer, outline, rect.inflate(2 * SS, 2 * SS),
                     border_radius=radius)
    pygame.draw.rect(layer, deep, rect.inflate(SS, SS),
                     border_radius=radius)
    pygame.draw.rect(layer, gold, rect, border_radius=radius)
    # Lit-side highlight along the top
    hl = pygame.Rect(rect.x + 2 * SS, rect.y + SS, rect.width - 4 * SS,
                     max(SS, big_fw // 3))
    pygame.draw.rect(layer, light, hl,
                     border_radius=max(SS, big_fw // 3))
    # Salt dots
    if salt_dots:
        rng = random.Random(seed)
        for _ in range(salt_dots):
            sx = rng.randint(rect.left + 2 * SS, rect.right - 2 * SS)
            sy = rng.randint(rect.top + SS, rect.bottom - SS)
            pygame.draw.circle(layer, SALT, (sx, sy), SS)
    if tilt_deg:
        layer = pygame.transform.rotate(layer, tilt_deg)
    # Smoothscale back down to 1x (the supersample pass acts as AA)
    target_w = max(1, layer.get_width() // SS)
    target_h = max(1, layer.get_height() // SS)
    layer = pygame.transform.smoothscale(layer, (target_w, target_h))
    rect = layer.get_rect(center=(cx, cy))
    surf.blit(layer, rect.topleft)


# --- Curly fry --------------------------------------------------------------

def draw_curly_fry(surf, cx, cy, *, radius=14, turns=2.2, color=FRY_GOLD,
                    deep=FRY_DEEP, outline=OUTLINE, light=FRY_LIGHT,
                    tilt_deg=0):
    """Spring-shaped fry curl. Drawn as a polyline along a spiral."""
    size = radius * 2 + 12
    layer = pygame.Surface((size, size), pygame.SRCALPHA)
    cx_l, cy_l = size // 2, size // 2
    n = max(24, int(turns * 18))
    pts = []
    for i in range(n):
        u = i / max(1, n - 1)
        a = u * turns * 2 * math.pi
        r = radius * (0.45 + 0.55 * u)   # spiral outward
        x = cx_l + math.cos(a) * r
        y = cy_l + math.sin(a) * r * 0.55   # vertical flatten -> coil look
        pts.append((x, y))
    if len(pts) >= 2:
        # Outline stroke (chunky)
        pygame.draw.lines(layer, outline, False, pts, 7)
        # Deep amber underbelly
        pygame.draw.lines(layer, deep, False, pts, 5)
        # Gold main body
        pygame.draw.lines(layer, color, False, pts, 4)
        # Lit-side highlight - render along the upper half of the curl
        hi_pts = [(p[0], p[1] - 1) for p in pts]
        pygame.draw.lines(layer, light, False, hi_pts, 1)
    if tilt_deg:
        layer = pygame.transform.rotate(layer, tilt_deg)
    rect = layer.get_rect(center=(cx, cy))
    surf.blit(layer, rect.topleft)


# --- Waffle fry -------------------------------------------------------------

def draw_waffle_fry(surf, cx, cy, *, size=18, color=FRY_GOLD,
                     deep=FRY_DEEP, outline=OUTLINE, light=FRY_LIGHT,
                     tilt_deg=0):
    """Square waffle fry with criss-cross cuts."""
    layer = pygame.Surface((size + 8, size + 8), pygame.SRCALPHA)
    rect = pygame.Rect(4, 4, size, size)
    pygame.draw.rect(layer, outline, rect.inflate(2, 2), border_radius=3)
    pygame.draw.rect(layer, deep, rect.inflate(1, 1), border_radius=3)
    pygame.draw.rect(layer, color, rect, border_radius=2)
    # Highlight on upper-left
    hl = pygame.Rect(rect.x + 1, rect.y + 1, max(2, size // 2),
                     max(2, size // 2))
    pygame.draw.rect(layer, light, hl, border_radius=2)
    # Criss-cross grid (the waffle holes)
    n = 3
    step = size / (n + 1)
    for i in range(1, n + 1):
        # Horizontal cuts
        y = int(rect.y + step * i)
        pygame.draw.line(layer, deep, (rect.x + 2, y), (rect.right - 2, y), 2)
        pygame.draw.line(layer, outline, (rect.x + 2, y), (rect.right - 2, y), 1)
        # Vertical cuts
        x = int(rect.x + step * i)
        pygame.draw.line(layer, deep, (x, rect.y + 2), (x, rect.bottom - 2), 2)
        pygame.draw.line(layer, outline, (x, rect.y + 2), (x, rect.bottom - 2), 1)
    if tilt_deg:
        layer = pygame.transform.rotate(layer, tilt_deg)
    rect = layer.get_rect(center=(cx, cy))
    surf.blit(layer, rect.topleft)


# --- Fries carton (McD-style) ----------------------------------------------

def draw_fry_carton(surf, base_x, base_y, w_top, h, *, stripe_color=KFC_RED,
                     stripe_count=5, outline=OUTLINE, layer_idx=2):
    """Trapezoid fries carton with red+white stripes, fries poking out
    of the top. `base_x, base_y` is the BOTTOM-CENTRE of the carton.
    Returns the rim_y (top of carton where fries emerge)."""
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
    # Top rim band
    rim_band = pygame.Rect(tl[0] - 2, rim_y - 4, w_top + 4, 7)
    pygame.draw.rect(surf, outline, rim_band.inflate(2, 2), border_radius=3)
    pygame.draw.rect(surf, _layer_shade(KFC_RED_D, layer_idx),
                      rim_band, border_radius=3)
    pygame.draw.rect(surf, red, rim_band.inflate(-4, -3), border_radius=2)
    return rim_y


# ===========================================================================
# Variant draw functions
# ===========================================================================
#
# Each variant takes (surf, scroll, ground_y, w) and renders all 3 parallax
# layers in painter order (back -> far -> near).
# ===========================================================================


# ---- V1: Classic Spilled Fries --------------------------------------------

def _v1_pile_layer(surf, scroll, ground_y, w, layer):
    """Dense scatter of straight fry sticks filling the ENTIRE layer
    silhouette - draw many short fries at random positions inside the
    silhouette polygon so the pile reads as fries all the way through,
    not a mountain with fries painted on top.
    """
    fry_light = _layer_shade(FRY_LIGHT, layer)
    fry_gold = _layer_shade(FRY_GOLD, layer)
    fry_deep = _layer_shade(FRY_DEEP, layer)
    outline = _outline_for_layer(layer)
    rng = random.Random(layer * 1337)
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
    # Paint from BOTTOM to TOP (high y first, low y last) so fries
    # higher in the pile draw on top - gives the natural overlap
    # look you get when fries are heaped.
    fries.sort(key=lambda f: -f[0])
    for (y, x, L, tilt) in fries:
        draw_fry(surf, x, y, L,
                  tilt_deg=tilt,
                  light=fry_light, gold=fry_gold, deep=fry_deep,
                  outline=outline, salt_dots=salt_dots,
                  seed=x * 7 + y * 11 + layer)


def draw_fries_v1(surf, scroll, ground_y, w):
    for layer in (0, 1, 2):
        _v1_pile_layer(surf, scroll, ground_y, w, layer)


# ---- V2: Fries Box Skyline ------------------------------------------------

def _v2_carton_layer(surf, scroll, ground_y, w, layer):
    """Row of fries cartons with varied heights along the horizon, fries
    poking out the top."""
    # Compute pillar positions: 1 carton every N px, each height
    # tracking the sine horizon so the row reads as a depth silhouette
    spacing = (60, 50, 44)[layer]
    carton_w_range = ((34, 50), (38, 56), (42, 64))[layer]
    fry_count_range = ((4, 6), (5, 8), (6, 10))[layer]
    rng = random.Random(layer * 99 + 7)
    outline = _outline_for_layer(layer)
    fry_light = _layer_shade(FRY_LIGHT, layer)
    fry_gold = _layer_shade(FRY_GOLD, layer)
    fry_deep = _layer_shade(FRY_DEEP, layer)
    # Sort by x first
    x = -spacing // 2
    while x < w + spacing // 2:
        # Carton height tied to the layer's sine - taller in sine peaks
        hy = horizon_y(x, scroll, ground_y, layer)
        carton_h = ground_y - hy + rng.randint(-6, 6)
        carton_h = max(40, carton_h)
        c_w = rng.randint(*carton_w_range)
        rim_y = draw_fry_carton(surf, x, ground_y, c_w, carton_h,
                                  layer_idx=layer)
        # Fries poking out the top
        n_fries = rng.randint(*fry_count_range)
        fry_max_len = (16, 22, 30)[layer]
        for _ in range(n_fries):
            off = rng.uniform(-c_w / 2 + 4, c_w / 2 - 4)
            tilt = rng.uniform(-30, 30)
            L = rng.randint(fry_max_len - 6, fry_max_len)
            draw_fry(surf, int(x + off), rim_y - L // 2 + 2, L,
                      tilt_deg=tilt + 90,   # vertical
                      light=fry_light, gold=fry_gold, deep=fry_deep,
                      outline=outline, salt_dots=0)
        x += spacing + rng.randint(-8, 8)


def draw_fries_v2(surf, scroll, ground_y, w):
    for layer in (0, 1, 2):
        _v2_carton_layer(surf, scroll, ground_y, w, layer)


# ---- V3: Curly Fry Spirals -------------------------------------------------

def _v3_curly_layer(surf, scroll, ground_y, w, layer):
    """Dense scatter of curly fries filling the silhouette interior so
    the whole pile reads as overlapping spirals."""
    light = _layer_shade(FRY_LIGHT, layer)
    gold = _layer_shade(FRY_GOLD, layer)
    deep = _layer_shade(FRY_DEEP, layer)
    outline = _outline_for_layer(layer)
    rng = random.Random(layer * 311 + 11)
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
        draw_curly_fry(
            surf, x, y, radius=r, turns=turns,
            color=gold, deep=deep, outline=outline, light=light,
            tilt_deg=tilt)


def draw_fries_v3(surf, scroll, ground_y, w):
    for layer in (0, 1, 2):
        _v3_curly_layer(surf, scroll, ground_y, w, layer)


# ---- V4: Waffle-Cut Stacks ------------------------------------------------

def _v4_waffle_layer(surf, scroll, ground_y, w, layer):
    """Stacked rows of waffle fries filling the silhouette - dense
    grid with row offset so the pile reads as bricks of waffle, not
    just a row along the top."""
    light = _layer_shade(FRY_LIGHT, layer)
    gold = _layer_shade(FRY_GOLD, layer)
    deep = _layer_shade(FRY_DEEP, layer)
    outline = _outline_for_layer(layer)
    size = (10, 14, 18)[layer]
    cols_spacing = size - 1   # tighter packing for overlap feel
    rng = random.Random(layer * 73 + 17)
    # Walk rows from ground up; for each row, scan all x columns and
    # place a waffle wherever the horizon allows.
    y = ground_y - size // 2
    row_idx = 0
    while True:
        # Earliest possible horizon (anywhere on the surf at this row)
        # - keep going as long as the row still intersects some part of
        # the silhouette.
        offset = (cols_spacing // 2) if (row_idx % 2 == 1) else 0
        any_placed = False
        for x in range(-cols_spacing + offset, w + cols_spacing,
                        cols_spacing):
            hy = horizon_y(x, scroll, ground_y, layer)
            if y < hy + size // 2:
                continue   # this x column doesn't reach this row
            tilt = rng.choice((-4, 0, 0, 4))
            draw_waffle_fry(surf, x + rng.randint(-1, 1), y,
                             size=size, color=gold, deep=deep,
                             outline=outline, light=light,
                             tilt_deg=tilt)
            any_placed = True
        if not any_placed:
            break
        y -= size + 1
        row_idx += 1


def draw_fries_v4(surf, scroll, ground_y, w):
    for layer in (0, 1, 2):
        _v4_waffle_layer(surf, scroll, ground_y, w, layer)


# ---- V5: Loaded Cheesy Fries ----------------------------------------------

def _v5_loaded_layer(surf, scroll, ground_y, w, layer):
    """V1 dense fries pile + cheese drips + ketchup zigzag + crumb
    sprinkles painted ON TOP of the near layer."""
    _v1_pile_layer(surf, scroll, ground_y, w, layer)
    if layer != 2:
        return   # only the near layer gets toppings (back/far stay clean)
    rng = random.Random(123)
    cheese = _layer_shade(CHEESE, layer)
    cheese_hi = _layer_shade(CHEESE_HI, layer)
    ketchup = _layer_shade(KETCHUP, layer)
    outline = _outline_for_layer(layer)
    # Cheese drips - cascading wide tongues from horizon down a bit
    n_cheese = 8
    for i in range(n_cheese):
        x = int((i + 0.5) * (w / n_cheese)) + rng.randint(-12, 12)
        hy = horizon_y(x, scroll, ground_y, layer)
        # Tongue shape (wider top, narrower drip below)
        drip_h = rng.randint(14, 30)
        tongue = [
            (x - 12, hy - 2),
            (x + 12, hy - 2),
            (x + 8,  hy + drip_h - 4),
            (x + 4,  hy + drip_h + 2),
            (x - 4,  hy + drip_h + 2),
            (x - 8,  hy + drip_h - 4),
        ]
        pygame.draw.polygon(surf, outline,
                            [(p[0], p[1] + 1) for p in tongue])
        pygame.draw.polygon(surf, cheese, tongue)
        # Tongue highlight along the top edge
        pygame.draw.polygon(surf, cheese_hi,
                            [(x - 10, hy), (x + 10, hy),
                             (x + 6, hy + 4), (x - 6, hy + 4)])
    # Ketchup zigzags - thin red streak across the upper edge
    pts = []
    for x in range(0, w + 20, 20):
        hy = horizon_y(x, scroll, ground_y, layer)
        zig = -4 if (x // 20) % 2 == 0 else 4
        pts.append((x, hy - 8 + zig))
    if len(pts) >= 2:
        pygame.draw.lines(surf, outline, False, pts, 5)
        pygame.draw.lines(surf, ketchup, False, pts, 3)
    # Crumb / salt sprinkles dotted along the upper edge
    for x in range(0, w, 5):
        if rng.random() < 0.5:
            hy = horizon_y(x, scroll, ground_y, layer)
            pygame.draw.circle(surf, outline,
                                (x, hy - 6 + rng.randint(-3, 3)), 2)
            pygame.draw.circle(surf, CRUMB,
                                (x, hy - 6 + rng.randint(-3, 3)), 1)


def draw_fries_v5(surf, scroll, ground_y, w):
    for layer in (0, 1, 2):
        _v5_loaded_layer(surf, scroll, ground_y, w, layer)


# ===========================================================================
# Harness: render each variant onto a full gameplay frame
# ===========================================================================

def draw_bg_with_fries(surf, fries_fn, *, scroll=0.0, phase=0.62):
    """Sky -> clouds -> FRIES-mountains -> ground. Replaces the call to
    draw_mountains() with the picker variant."""
    buckets = _biome.PHASE_BUCKETS
    pal = _biome.palette_for_phase(phase)
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal, int(phase * buckets))
    surf.blit(sky, (0, 0))
    # Clouds
    for i, (bx, by, sc, var) in enumerate(
            ((20, 90, 0.9, 0), (180, 140, 1.1, 2), (60, 220, 0.8, 3),
             (230, 60, 0.7, 1), (320, 180, 0.9, 4))):
        draw_cloud(surf, bx, by + math.sin(1.2 + i) * 3, sc, variant=var)
    # FRIES instead of mountains
    fries_fn(surf, scroll, GROUND_Y, W)
    # Ground
    draw_ground(surf, GROUND_Y, W, H, scroll,
                pal['ground_top'], pal['ground_mid'], (60, 40, 25))
    return pal


def render_gameplay_frame(surf, fries_fn):
    pal = draw_bg_with_fries(surf, fries_fn)
    # Add 3 KFC-themed pipes in the foreground for context. Use the
    # bucket variant since it's the most distinct KFC pillar look.
    from game import pillar_kfc as kfc
    pillars = []
    gap_h = int(GAP_START * KFC_GAP_BOOST)
    for x, gap_y, seed in [(35, 300, 0), (150, 360, 1), (265, 290, 2)]:
        p = Pipe(float(x), float(gap_y), float(gap_h))
        p.seed = seed
        p.is_kfc = True
        pillars.append(p)
    for p in pillars:
        kfc.draw_pillar_pair_kfc(surf, p.top_rect, p.bot_rect, pal, p.seed)


# ===========================================================================
# Variant registry + main
# ===========================================================================

VARIANTS = (
    ("v1", "V1 Classic Spilled Fries",  draw_fries_v1),
    ("v2", "V2 Fries Box Skyline",       draw_fries_v2),
    ("v3", "V3 Curly Fry Spirals",       draw_fries_v3),
    ("v4", "V4 Waffle-Cut Stacks",       draw_fries_v4),
    ("v5", "V5 Loaded Cheesy Fries",     draw_fries_v5),
)


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((W, H))
    out_dir = os.path.join("docs", "kfc_powerup", "fries_mountains")
    os.makedirs(out_dir, exist_ok=True)

    frames = {}
    for key, label, fn in VARIANTS:
        screen.fill((0, 0, 0))
        render_gameplay_frame(screen, fn)
        frames[key] = screen.copy()
        out_path = os.path.join(out_dir, f"{key}.png")
        pygame.image.save(screen, out_path)
        print(f"saved {out_path}  ({label})")

    # 5-column compare strip
    GAP, LABEL_H, PAD = 14, 30, 18
    cell_w, cell_h = W, H
    canvas_w = cell_w * len(VARIANTS) + GAP * (len(VARIANTS) - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((230, 232, 235))
    label_font = pygame.font.SysFont(None, 22, bold=True)
    for i, (key, label, _) in enumerate(VARIANTS):
        x = PAD + i * (cell_w + GAP)
        y = PAD
        pygame.draw.rect(canvas, (60, 70, 100),
                         pygame.Rect(x - 1, y - 1, cell_w + 2, cell_h + 2),
                         width=1)
        canvas.blit(frames[key], (x, y))
        lbl = label_font.render(label, True, (30, 35, 55))
        canvas.blit(lbl, (x + (cell_w - lbl.get_width()) // 2,
                          y + cell_h + 8))
    out_path = os.path.join(out_dir, "compare.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  {canvas.get_size()}")


if __name__ == "__main__":
    sys.exit(main() or 0)
