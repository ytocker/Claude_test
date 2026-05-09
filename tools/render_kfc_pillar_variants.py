"""KFC powerup pillar transformation — 5 wacky-cartoon design picker.

When the KFC powerup is active in the game, every pillar pair turns into a
hot-dog-style + fried-chicken pillar. This file defines five distinct
candidate designs (no cumulative tier ladder; each variant is a different
concept). The harness `render_kfc_pillar_gameplay.py` patches the live
draw path via `install_variant(n)` and saves a 360x640 frame per variant.

Variants:
  V1 - Dog & Drum Tower    alternating fried drumsticks + hot-dog buns
                           with mustard drizzle + sesame-seed top
  V2 - Mega Frankfurter    one giant sausage-in-bun + ketchup/mustard
                           zigzags + chicken-wing accent at the gap edge
  V3 - KFC Bucket Stack    striped buckets overflowing with chicken
                           pieces + hot-dog flagpole + pennant
  V4 - Corn Dog Crispy     battered corn-dog rod + crispy crumb bumps +
                           honey-mustard drips + wooden stick at gap
  V5 - Crispy Skyscraper   stacked sandwich tower (fillet/bun/cheese/
                           lettuce) + toothpick skewer through gap

Picker only - does NOT modify any `game/` file. `install_variant(n)`
returns a context manager that monkey-patches both
`game.pillar_variants.draw_pillar_pair` AND `game.entities.draw_pillar_pair`
(the import binding in entities.py is what `Pipe.draw` actually calls).
"""
import contextlib
import math
import random

import pygame
import pygame.gfxdraw as gfx

from game import entities as gent
from game import pillar_variants as gpv


# ----- Cartoon palette ------------------------------------------------------

# Hot-dog
BUN_HI    = (252, 226, 178)
BUN_MID   = (232, 192, 130)
BUN_LO    = (188, 142,  78)
BUN_LINE  = (110,  72,  30)
SAUSAGE_HI  = (228, 124,  92)
SAUSAGE_MID = (198,  82,  62)
SAUSAGE_LO  = (146,  46,  36)

# Fried chicken
CRUST_HI  = (250, 212, 118)
CRUST_MID = (224, 162,  62)
CRUST_LO  = (148,  84,  20)
CRUMB     = (255, 232, 168)
BONE      = (248, 240, 210)
BONE_SHA  = (190, 175, 140)

# KFC bucket
KFC_RED   = (212,  34,  34)
KFC_RED_D = (152,  18,  18)
KFC_WHITE = (250, 245, 235)

# Condiments / extras
MUSTARD     = (252, 206,  56)
MUSTARD_HI  = (255, 234, 130)
KETCHUP     = (210,  44,  40)
KETCHUP_HI  = (244,  92,  72)
CHEESE      = (252, 184,  60)
LETTUCE_HI  = (140, 200,  78)
LETTUCE_MID = ( 86, 158,  64)
LETTUCE_LO  = ( 52, 106,  40)
WOOD_HI     = (230, 192, 132)
WOOD_LO     = (162, 116,  62)

OUTLINE = ( 38,  22,  10)
SHADOW  = ( 22,  14,   8)


# ----- Drawing primitives ---------------------------------------------------

def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _drop_shadow(surf, rect, inflate=0):
    """Soft drop-shadow under a shape's bounding rect (chunky cartoon)."""
    sh = pygame.Surface(
        (rect.width + inflate * 2 + 6, rect.height + inflate * 2 + 6),
        pygame.SRCALPHA,
    )
    pygame.draw.ellipse(sh, (*SHADOW, 90), sh.get_rect())
    surf.blit(sh, (rect.x - inflate - 3, rect.bottom - inflate - 1))


def _aa_filled_circle(surf, cx, cy, r, color):
    gfx.filled_circle(surf, cx, cy, r, color)
    gfx.aacircle(surf, cx, cy, r, color)


def _aa_outline_polygon(surf, pts, fill, outline=OUTLINE, ow=2):
    """Filled cartoon polygon with chunky outline."""
    pygame.draw.polygon(surf, fill, pts)
    pygame.draw.polygon(surf, outline, pts, ow)


def draw_drumstick(surf, cx, cy, w, h, *, tilt=0, bone_top=True):
    """Cartoon fried drumstick. Tear-drop-ish meat blob + bone nub.

    `bone_top=True`: bone protrudes upward (used in upright stacks).
    `tilt` rotates the whole stick in degrees.
    """
    layer = pygame.Surface((w + 14, h + 14), pygame.SRCALPHA)
    lw, lh = layer.get_size()
    # Meat blob: fat oval w/ slight pear bulge
    meat_rect = pygame.Rect(7, 9, w, int(h * 0.78))
    pygame.draw.ellipse(layer, OUTLINE, meat_rect.inflate(4, 4))
    pygame.draw.ellipse(layer, CRUST_LO, meat_rect.inflate(2, 2))
    pygame.draw.ellipse(layer, CRUST_MID, meat_rect)
    pygame.draw.ellipse(layer, CRUST_HI, meat_rect.inflate(-int(w * 0.45), -int(h * 0.45))
                        .move(-int(w * 0.10), -int(h * 0.06)))
    # Crispy crumb dots
    rng = random.Random(int(cx * 13 + cy * 7))
    for _ in range(7):
        bx = rng.randint(meat_rect.left + 4, meat_rect.right - 4)
        by = rng.randint(meat_rect.top + 4, meat_rect.bottom - 4)
        _aa_filled_circle(layer, bx, by, 1, CRUMB)
    # Bone nub (cylinder + cap)
    bone_w = max(5, int(w * 0.32))
    bone_h = max(8, int(h * 0.28))
    if bone_top:
        bx = 7 + (w - bone_w) // 2
        by = 0
        bone_rect = pygame.Rect(bx, by, bone_w, bone_h)
        pygame.draw.rect(layer, OUTLINE, bone_rect.inflate(4, 2), border_radius=4)
        pygame.draw.rect(layer, BONE_SHA, bone_rect.inflate(2, 0), border_radius=3)
        pygame.draw.rect(layer, BONE, bone_rect.inflate(-2, -1), border_radius=3)
        # rounded knob
        _aa_filled_circle(layer, bone_rect.centerx - bone_w // 4,
                          bone_rect.top + 1, max(2, bone_w // 3), BONE)
        _aa_filled_circle(layer, bone_rect.centerx + bone_w // 4,
                          bone_rect.top + 1, max(2, bone_w // 3), BONE)
    else:
        bx = 7 + (w - bone_w) // 2
        by = lh - bone_h - 4
        bone_rect = pygame.Rect(bx, by, bone_w, bone_h)
        pygame.draw.rect(layer, OUTLINE, bone_rect.inflate(4, 2), border_radius=4)
        pygame.draw.rect(layer, BONE_SHA, bone_rect.inflate(2, 0), border_radius=3)
        pygame.draw.rect(layer, BONE, bone_rect.inflate(-2, -1), border_radius=3)
        _aa_filled_circle(layer, bone_rect.centerx - bone_w // 4,
                          bone_rect.bottom - 1, max(2, bone_w // 3), BONE)
        _aa_filled_circle(layer, bone_rect.centerx + bone_w // 4,
                          bone_rect.bottom - 1, max(2, bone_w // 3), BONE)
    if tilt:
        layer = pygame.transform.rotate(layer, tilt)
    rect = layer.get_rect(center=(cx, cy))
    surf.blit(layer, rect.topleft)


def draw_hot_dog_bun(surf, rect, *, sausage=True, mustard=True, ketchup=False,
                     condiment_phase=0.0):
    """Plump hot-dog bun (rect-shaped) with optional sausage + condiments.

    `rect` is the full bun outer rect.
    """
    r = rect
    # Drop shadow
    sh = pygame.Surface((r.width + 8, r.height + 8), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (*SHADOW, 60),
                        pygame.Rect(0, 0, r.width + 8, r.height + 8))
    surf.blit(sh, (r.x - 4, r.bottom - r.height // 3))
    # Bottom-bun shadow lobe
    pygame.draw.rect(surf, OUTLINE, r.inflate(4, 4), border_radius=int(r.height * 0.55))
    pygame.draw.rect(surf, BUN_LO, r.inflate(2, 2), border_radius=int(r.height * 0.55))
    pygame.draw.rect(surf, BUN_MID, r, border_radius=int(r.height * 0.55))
    # Highlight
    hl = pygame.Rect(r.x + 4, r.y + 3, r.width - 8, max(3, int(r.height * 0.30)))
    pygame.draw.rect(surf, BUN_HI, hl, border_radius=int(hl.height * 0.8))
    # Centre split (where sausage sits)
    split_h = max(8, int(r.height * 0.50))
    split = pygame.Rect(r.x + 4, r.y + (r.height - split_h) // 2,
                        r.width - 8, split_h)
    pygame.draw.rect(surf, BUN_LINE, split.inflate(0, 0),
                     border_radius=int(split.height * 0.45))
    pygame.draw.rect(surf, _shade(SAUSAGE_LO, -10),
                     split.inflate(-2, -2),
                     border_radius=int(split.height * 0.40))
    if sausage:
        sw, sh_ = split.width - 6, split.height - 4
        s = pygame.Rect(split.x + 3, split.y + 2, sw, sh_)
        pygame.draw.rect(surf, SAUSAGE_LO, s.inflate(2, 2),
                         border_radius=int(sh_ * 0.45))
        pygame.draw.rect(surf, SAUSAGE_MID, s, border_radius=int(sh_ * 0.45))
        # Sausage highlight
        hl2 = pygame.Rect(s.x + 3, s.y + 1, s.width - 6, max(2, sh_ // 3))
        pygame.draw.rect(surf, SAUSAGE_HI, hl2,
                         border_radius=int(hl2.height * 0.8))
        # Mustard zigzag
        if mustard:
            n = max(4, s.width // 8)
            xs = [s.x + 4 + i * (s.width - 8) / max(1, n - 1) for i in range(n)]
            ys = [s.centery + (-2 if i % 2 == 0 else 2) for i in range(n)]
            pts = list(zip([int(x) for x in xs], ys))
            pygame.draw.lines(surf, _shade(MUSTARD, -40), False, pts, 4)
            pygame.draw.lines(surf, MUSTARD, False, pts, 3)
            pygame.draw.lines(surf, MUSTARD_HI, False, pts, 1)
        if ketchup:
            n = max(3, s.width // 10)
            xs = [s.x + 6 + i * (s.width - 12) / max(1, n - 1) for i in range(n)]
            ys = [s.centery + (3 if i % 2 == 0 else -3) for i in range(n)]
            pts = list(zip([int(x) for x in xs], ys))
            pygame.draw.lines(surf, _shade(KETCHUP, -40), False, pts, 4)
            pygame.draw.lines(surf, KETCHUP, False, pts, 3)


def draw_sesame(surf, rect, n=8, seed=0):
    """Tiny ivory tear-drops scattered on the top half of the bun."""
    rng = random.Random(seed * 17 + 91)
    for _ in range(n):
        x = rng.randint(rect.x + 4, rect.right - 4)
        y = rng.randint(rect.y + 3, rect.y + rect.height // 3)
        pygame.draw.ellipse(surf, OUTLINE,
                            pygame.Rect(x - 2, y - 1, 4, 3))
        pygame.draw.ellipse(surf, (250, 234, 196),
                            pygame.Rect(x - 1, y - 1, 3, 2))


def draw_chicken_nugget(surf, cx, cy, r, *, jitter_seed=0):
    """Chunky lumpy fried-chicken nugget."""
    rng = random.Random(jitter_seed)
    pts = []
    n = 9
    for i in range(n):
        a = i * 2 * math.pi / n
        rr = r + rng.uniform(-1.4, 1.6)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.85))
    _aa_outline_polygon(surf, pts, CRUST_MID, OUTLINE, 2)
    # Inner highlight
    pts_i = [(cx + (x - cx) * 0.65, cy + (y - cy) * 0.65 - 1)
             for (x, y) in pts]
    pygame.draw.polygon(surf, CRUST_HI, pts_i)
    # Crumb dots
    for _ in range(3):
        bx = int(cx + rng.uniform(-r * 0.6, r * 0.6))
        by = int(cy + rng.uniform(-r * 0.6, r * 0.6))
        _aa_filled_circle(surf, bx, by, 1, CRUMB)


def draw_chicken_wing(surf, cx, cy, w, h, *, flip=False):
    """Cartoon fried chicken wing (drumette + wingette)."""
    # Drumette big lobe
    big = pygame.Rect(cx - w // 2, cy - h // 2, int(w * 0.65), int(h * 0.85))
    pygame.draw.ellipse(surf, OUTLINE, big.inflate(4, 4))
    pygame.draw.ellipse(surf, CRUST_LO, big.inflate(2, 2))
    pygame.draw.ellipse(surf, CRUST_MID, big)
    pygame.draw.ellipse(surf, CRUST_HI, big.inflate(-int(w * 0.30), -int(h * 0.40)))
    # Wingette
    sm = pygame.Rect(cx + (1 if not flip else -1) * int(w * 0.08),
                     cy - int(h * 0.10),
                     int(w * 0.55), int(h * 0.55))
    if flip:
        sm.x = cx - int(w * 0.08) - sm.width
    pygame.draw.ellipse(surf, OUTLINE, sm.inflate(4, 4))
    pygame.draw.ellipse(surf, CRUST_LO, sm.inflate(2, 2))
    pygame.draw.ellipse(surf, CRUST_MID, sm)
    pygame.draw.ellipse(surf, CRUST_HI, sm.inflate(-int(w * 0.30), -int(h * 0.36))
                        .move(-2, -1))
    # Bone tip
    bone_x = sm.right + 2 if not flip else sm.left - 5
    pygame.draw.rect(surf, OUTLINE,
                     pygame.Rect(bone_x - 1, cy - 2, 6, 5), border_radius=2)
    pygame.draw.rect(surf, BONE,
                     pygame.Rect(bone_x, cy - 1, 4, 3), border_radius=2)


def draw_mustard_drip(surf, x, y, length, *, color=MUSTARD,
                      hi=MUSTARD_HI, width=4):
    """Vertical mustard/cheese drip with a fat blob at the bottom."""
    # Trail
    pygame.draw.line(surf, OUTLINE, (x, y), (x, y + length), width + 2)
    pygame.draw.line(surf, _shade(color, -40), (x, y), (x, y + length), width)
    pygame.draw.line(surf, color, (x - 1, y), (x - 1, y + length - 2), max(1, width - 2))
    # Blob
    _aa_filled_circle(surf, x, y + length, max(3, width), OUTLINE)
    _aa_filled_circle(surf, x, y + length, max(2, width - 1), color)
    _aa_filled_circle(surf, x - 1, y + length - 1, max(1, width - 3), hi)


# ----- V1: Dog & Drum Tower -------------------------------------------------

def draw_kfc_v1(surf, top_rect, bot_rect, palette, seed):
    """Alternating fried drumsticks + hot-dog buns stacked vertically.

    Top pillar: stack ends with a sesame-bun cap at the gap.
    Bottom pillar: stack starts with a sesame-bun cap at the gap.
    Mustard drips run down the side of the buns.
    """
    rng = random.Random(seed * 5 + 11)

    def _stack(rect, cap_at='top'):
        # cap_at='top' means the sesame bun is at rect.top (gap-side for top
        # pillar).  cap_at='bot' means the sesame bun is at rect.bottom.
        x, y, w, h = rect
        if h < 30:
            return
        # Slab heights: bun, drum, bun, drum ...
        slabs = []
        cur = 0
        kinds = ['bun', 'drum']
        i = 0
        while cur < h - 10:
            kind = kinds[i % 2]
            sh = 36 if kind == 'bun' else 50
            slabs.append((kind, cur, min(sh, h - cur)))
            cur += sh
            i += 1
        # Reorder if cap_at='bot' so the bun sits at the bottom
        if cap_at == 'bot':
            slabs = list(reversed([(k, h - (s + sh), sh) for (k, s, sh) in slabs]))
        for kind, sy, sh in slabs:
            r = pygame.Rect(x, y + sy, w, sh)
            if r.height < 10:
                continue
            if kind == 'bun':
                draw_hot_dog_bun(surf, r.inflate(2, -2), sausage=False,
                                 mustard=False)
                # Sesame on the cap
                if (cap_at == 'top' and sy == 0) or \
                   (cap_at == 'bot' and sy + sh >= h - 1):
                    draw_sesame(surf, r, n=10, seed=seed + sy)
            else:  # drum
                tilt = rng.choice([-12, -6, 6, 12])
                draw_drumstick(surf, r.centerx, r.centery,
                               w + 14, sh + 4, tilt=tilt,
                               bone_top=(cap_at == 'top'))
        # Mustard drip down the right edge
        drip_y = y + 6 if cap_at == 'top' else y + h - 22
        draw_mustard_drip(surf, x + w - 6, drip_y, 18, width=4)

    _stack(top_rect, cap_at='top')   # cap is the gap-facing bun (bottom of top pillar)
    _stack(bot_rect, cap_at='bot')   # cap is the gap-facing bun (top of bot pillar)


# ----- V2: Mega Frankfurter -------------------------------------------------

def draw_kfc_v2(surf, top_rect, bot_rect, palette, seed):
    """One giant sausage-in-bun pillar with bold ketchup+mustard zigzags.
    A chunky fried chicken wing accents the gap edge of the bottom pillar."""

    def _frank(rect, gap_side='bottom'):
        x, y, w, h = rect
        if h < 14:
            return
        bun = pygame.Rect(x - 2, y, w + 4, h)
        # Bun outline + fill
        radius = max(10, w // 2 + 4)
        pygame.draw.rect(surf, OUTLINE, bun.inflate(4, 4), border_radius=radius)
        pygame.draw.rect(surf, BUN_LO, bun.inflate(2, 2), border_radius=radius)
        pygame.draw.rect(surf, BUN_MID, bun, border_radius=radius)
        # Highlight strip
        hl = pygame.Rect(bun.x + 5, bun.y + 6, max(4, bun.width - 26), max(4, bun.height - 12))
        pygame.draw.rect(surf, BUN_HI, hl, border_radius=radius // 2)
        # Sausage tube
        s_inset_x = 8
        s_inset_y = 14
        s = pygame.Rect(bun.x + s_inset_x, bun.y + s_inset_y,
                        bun.width - s_inset_x * 2, bun.height - s_inset_y * 2)
        if s.height < 8:
            s = pygame.Rect(bun.x + 6, bun.y + 6, bun.width - 12, bun.height - 12)
        pygame.draw.rect(surf, OUTLINE, s.inflate(4, 4), border_radius=s.width // 2 + 2)
        pygame.draw.rect(surf, SAUSAGE_LO, s.inflate(2, 2),
                         border_radius=s.width // 2 + 2)
        pygame.draw.rect(surf, SAUSAGE_MID, s, border_radius=s.width // 2)
        pygame.draw.rect(surf, SAUSAGE_HI,
                         pygame.Rect(s.x + 4, s.y + 4, max(2, s.width // 3),
                                     max(2, s.height - 12)),
                         border_radius=s.width // 4)
        # Long mustard squiggle running the length of the sausage
        n = max(6, s.height // 12)
        cx = s.centerx
        amp = max(3, s.width // 4)
        pts_m = [(cx + (amp if i % 2 == 0 else -amp),
                  s.y + 8 + i * (s.height - 16) // max(1, n - 1))
                 for i in range(n)]
        pygame.draw.lines(surf, _shade(MUSTARD, -40), False, pts_m, 5)
        pygame.draw.lines(surf, MUSTARD, False, pts_m, 3)
        # Ketchup dotted accents
        for i in range(0, n, 2):
            bx, by = pts_m[i]
            _aa_filled_circle(surf, bx, by, 2, KETCHUP)
            _aa_filled_circle(surf, bx, by, 1, KETCHUP_HI)
        # End-cap of bun (rounded, so it reads as a hot dog end)
        if gap_side == 'bottom':
            cap_rect = pygame.Rect(bun.x - 2, bun.bottom - 14, bun.width + 4, 18)
        else:
            cap_rect = pygame.Rect(bun.x - 2, bun.y - 4, bun.width + 4, 18)
        pygame.draw.rect(surf, OUTLINE, cap_rect.inflate(4, 4), border_radius=radius)
        pygame.draw.rect(surf, BUN_LO, cap_rect.inflate(2, 2), border_radius=radius)
        pygame.draw.rect(surf, BUN_MID, cap_rect, border_radius=radius)

    _frank(top_rect, gap_side='bottom')
    _frank(bot_rect, gap_side='top')

    # Chicken wing accent at the gap edge of the bottom pillar
    wcx = bot_rect.centerx + 6
    wcy = bot_rect.top + 14
    draw_chicken_wing(surf, wcx, wcy, 46, 30, flip=False)
    # Smaller wing accent dangling under top pillar
    draw_chicken_wing(surf, top_rect.centerx - 8, top_rect.bottom - 14,
                      36, 24, flip=True)


# ----- V3: KFC Bucket Stack -------------------------------------------------

def _draw_bucket(surf, rect, *, overflow_chicken=True, seed=0):
    """Red+white striped fried-chicken bucket (trapezoid, wide at top)."""
    x, y, w, h = rect
    top_w = w
    bot_w = max(8, int(w * 0.74))
    # Trapezoid points
    tl = (x, y + 4)
    tr = (x + top_w, y + 4)
    br = (x + (top_w - bot_w) // 2 + bot_w, y + h)
    bl = (x + (top_w - bot_w) // 2, y + h)
    poly = [tl, tr, br, bl]
    # Outline / base white fill
    pygame.draw.polygon(surf, OUTLINE, [(px, py + 1) for (px, py) in poly])
    pygame.draw.polygon(surf, KFC_WHITE, poly)
    # Vertical red stripes (4 of them)
    n_stripes = 4
    for i in range(n_stripes):
        u0 = (i + 0.10) / n_stripes
        u1 = (i + 0.55) / n_stripes
        # Stripe is also a trapezoid (each x interpolated from tl..tr)
        sx0_top = tl[0] + (tr[0] - tl[0]) * u0
        sx1_top = tl[0] + (tr[0] - tl[0]) * u1
        sx0_bot = bl[0] + (br[0] - bl[0]) * u0
        sx1_bot = bl[0] + (br[0] - bl[0]) * u1
        pygame.draw.polygon(
            surf, KFC_RED,
            [(sx0_top, tl[1]), (sx1_top, tl[1]),
             (sx1_bot, br[1]), (sx0_bot, br[1])])
    # Re-stroke outline + a top rim band
    pygame.draw.polygon(surf, OUTLINE, poly, 2)
    rim = pygame.Rect(tl[0] - 2, tl[1] - 4, top_w + 4, 8)
    pygame.draw.rect(surf, OUTLINE, rim.inflate(2, 2), border_radius=4)
    pygame.draw.rect(surf, KFC_RED_D, rim, border_radius=4)
    pygame.draw.rect(surf, KFC_RED,
                     rim.inflate(-4, -3), border_radius=3)
    # KFC text band on the white area: simple "KFC" lettering
    label_y = (tl[1] + br[1]) // 2 - 5
    label_x = (tl[0] + tr[0]) // 2 - 9
    font_band = pygame.Rect(label_x - 2, label_y - 2, 22, 12)
    pygame.draw.rect(surf, KFC_WHITE, font_band, border_radius=2)
    try:
        font = pygame.font.SysFont(None, 14, bold=True)
        txt = font.render("KFC", True, KFC_RED)
        surf.blit(txt, (font_band.centerx - txt.get_width() // 2,
                         font_band.centery - txt.get_height() // 2))
    except Exception:
        pygame.draw.line(surf, KFC_RED, (font_band.x + 2, font_band.centery),
                         (font_band.right - 2, font_band.centery), 2)
    # Overflowing chicken pieces along the rim
    if overflow_chicken:
        rng = random.Random(seed)
        n = 3
        for i in range(n):
            cx = int(tl[0] + (tr[0] - tl[0]) * (0.20 + i * 0.30))
            cy = int(tl[1] - 3 + rng.randint(-2, 2))
            r = 7 + rng.randint(0, 2)
            draw_chicken_nugget(surf, cx, cy, r, jitter_seed=seed + i * 13)


def draw_kfc_v3(surf, top_rect, bot_rect, palette, seed):
    """Stacked KFC buckets with overflowing chicken pieces.
    Bottom pillar: 2-3 buckets stacked + a hot-dog flagpole on top.
    Top pillar: inverted bucket(s) hanging from the ceiling."""
    rng = random.Random(seed * 7 + 23)

    # Bottom pillar: stack buckets from ground up
    bx, by, bw, bh = bot_rect
    bucket_h = 64
    n = max(1, bh // bucket_h)
    for i in range(n):
        r = pygame.Rect(bx - 4, by + bh - (i + 1) * bucket_h, bw + 8, bucket_h - 4)
        if r.bottom > by + bh:
            r.height -= r.bottom - (by + bh)
        if r.top < by:
            r.height -= by - r.top
            r.top = by
        if r.height < 18:
            continue
        _draw_bucket(surf, r, overflow_chicken=(i == n - 1), seed=seed + i)

    # Hot-dog flagpole on top of the stack (rises into the gap area)
    pole_x = bot_rect.centerx
    pole_top = bot_rect.top - 4
    # Pole (bun + sausage horizontal-as-flagpole)
    pole_h = 26
    pole = pygame.Rect(pole_x - 4, pole_top - pole_h, 8, pole_h)
    pygame.draw.rect(surf, OUTLINE, pole.inflate(2, 0), border_radius=3)
    pygame.draw.rect(surf, BUN_LO, pole, border_radius=3)
    pygame.draw.rect(surf, SAUSAGE_MID, pole.inflate(-3, -2), border_radius=2)
    # Pennant
    pen = [(pole_x + 4, pole_top - pole_h + 2),
           (pole_x + 22, pole_top - pole_h + 7),
           (pole_x + 4, pole_top - pole_h + 12)]
    pygame.draw.polygon(surf, OUTLINE, [(p[0] + 1, p[1] + 1) for p in pen])
    pygame.draw.polygon(surf, KFC_RED, pen)
    pygame.draw.line(surf, KFC_WHITE,
                     (pole_x + 8, pole_top - pole_h + 7),
                     (pole_x + 14, pole_top - pole_h + 7), 1)

    # Top pillar: inverted (upside-down) buckets hanging
    tx, ty, tw, th = top_rect
    n_top = max(1, th // bucket_h)
    for i in range(n_top):
        r = pygame.Rect(tx - 4, ty + i * bucket_h, tw + 8, bucket_h - 4)
        if r.bottom > ty + th:
            r.height -= r.bottom - (ty + th)
        if r.height < 18:
            continue
        # Draw flipped (chicken at bottom = gap side)
        layer = pygame.Surface((r.width, r.height + 12), pygame.SRCALPHA)
        _draw_bucket(layer, layer.get_rect().inflate(0, -10).move(0, 4),
                     overflow_chicken=(i == n_top - 1), seed=seed + 100 + i)
        layer = pygame.transform.flip(layer, False, True)
        surf.blit(layer, r.topleft)


# ----- V4: Corn Dog Crispy --------------------------------------------------

def draw_kfc_v4(surf, top_rect, bot_rect, palette, seed):
    """A giant corn dog: fried-batter rod with crispy bumps + wooden stick
    protruding through the gap. Honey-mustard drips down the sides."""

    def _corndog(rect, stick_at='top'):
        x, y, w, h = rect
        # Rod body: rounded rectangle
        rod = pygame.Rect(x - 1, y, w + 2, h)
        radius = max(8, w // 2 + 2)
        pygame.draw.rect(surf, OUTLINE, rod.inflate(4, 4), border_radius=radius)
        pygame.draw.rect(surf, CRUST_LO, rod.inflate(2, 2), border_radius=radius)
        pygame.draw.rect(surf, CRUST_MID, rod, border_radius=radius)
        # Lit side highlight
        hl = pygame.Rect(rod.x + 4, rod.y + 4, max(3, rod.width // 3), rod.height - 8)
        pygame.draw.rect(surf, CRUST_HI, hl, border_radius=radius // 2)
        # Crispy bumps: dense scatter across the surface
        rng = random.Random(seed * 19 + (1 if stick_at == 'top' else 2))
        bumps = max(28, h // 6)
        for _ in range(bumps):
            bx = rng.randint(rod.x + 3, rod.right - 3)
            by = rng.randint(rod.y + 4, rod.bottom - 4)
            r = rng.randint(2, 4)
            _aa_filled_circle(surf, bx + 1, by + 1, r, _shade(CRUST_LO, -10))
            _aa_filled_circle(surf, bx, by, r, _shade(CRUST_MID, +18))
            _aa_filled_circle(surf, bx - 1, by - 1, max(1, r - 2), CRUMB)
        # Honey-mustard glaze drips along an edge
        for i in range(3):
            dx = rod.x + 6 + i * (rod.width - 12) // 2
            dy = rod.y + 8 + i * 18
            if dy + 24 < rod.bottom:
                draw_mustard_drip(surf, dx, dy, 22, color=(244, 178, 60),
                                  hi=(255, 222, 130), width=4)
        # Wooden stick protruding from the gap end
        stick_w = 10
        stick_l = 28
        if stick_at == 'top':
            sx = rod.centerx - stick_w // 2
            sy = rod.bottom - 2
        else:
            sx = rod.centerx - stick_w // 2
            sy = rod.y - stick_l + 2
        stick = pygame.Rect(sx, sy, stick_w, stick_l)
        pygame.draw.rect(surf, OUTLINE, stick.inflate(2, 2), border_radius=4)
        pygame.draw.rect(surf, WOOD_LO, stick.inflate(0, 0), border_radius=4)
        pygame.draw.rect(surf, WOOD_HI,
                         pygame.Rect(stick.x + 2, stick.y + 2, 3, stick.height - 4),
                         border_radius=2)
        # Wood grain
        for i in range(2):
            pygame.draw.line(surf, _shade(WOOD_LO, -30),
                             (stick.x + 2, stick.y + 6 + i * 8),
                             (stick.right - 2, stick.y + 6 + i * 8), 1)

    # Top pillar: stick points DOWN into the gap
    _corndog(top_rect, stick_at='top')
    # Bottom pillar: stick points UP into the gap
    _corndog(bot_rect, stick_at='bot')


# ----- V5: Crispy Skyscraper ------------------------------------------------

def draw_kfc_v5(surf, top_rect, bot_rect, palette, seed):
    """Multilayer fast-food sandwich tower with a toothpick skewer through
    the centre. Layers cycle: bun_top -> fillet -> cheese -> lettuce ->
    fillet -> bun_bot ..."""

    LAYER_BUN_TOP   = 'bun_top'
    LAYER_BUN_BOT   = 'bun_bot'
    LAYER_FILLET    = 'fillet'
    LAYER_CHEESE    = 'cheese'
    LAYER_LETTUCE   = 'lettuce'

    HEIGHTS = {
        LAYER_BUN_TOP:  30,
        LAYER_BUN_BOT:  20,
        LAYER_FILLET:   28,
        LAYER_CHEESE:   12,
        LAYER_LETTUCE:  14,
    }
    SEQ = [LAYER_BUN_TOP, LAYER_FILLET, LAYER_CHEESE,
           LAYER_LETTUCE, LAYER_FILLET, LAYER_BUN_BOT]

    def _draw_layer(rect, kind):
        x, y, w, h = rect
        if h < 4:
            return
        if kind == LAYER_BUN_TOP:
            r = pygame.Rect(x - 2, y, w + 4, h)
            pygame.draw.rect(surf, OUTLINE, r.inflate(4, 4),
                             border_radius=int(h * 0.7))
            pygame.draw.rect(surf, BUN_LO, r.inflate(2, 2),
                             border_radius=int(h * 0.7))
            pygame.draw.rect(surf, BUN_MID, r, border_radius=int(h * 0.7))
            hl = pygame.Rect(r.x + 4, r.y + 3, r.width - 8, max(3, int(h * 0.40)))
            pygame.draw.rect(surf, BUN_HI, hl, border_radius=int(hl.height * 0.8))
            draw_sesame(surf, r, n=8, seed=seed + y)
        elif kind == LAYER_BUN_BOT:
            r = pygame.Rect(x - 2, y, w + 4, h)
            pygame.draw.rect(surf, OUTLINE, r.inflate(4, 4),
                             border_radius=int(h * 0.6))
            pygame.draw.rect(surf, BUN_LO, r.inflate(2, 2),
                             border_radius=int(h * 0.6))
            pygame.draw.rect(surf, BUN_MID, r, border_radius=int(h * 0.6))
        elif kind == LAYER_FILLET:
            r = pygame.Rect(x - 6, y, w + 12, h)
            # Wavy outer outline
            pts = []
            n = 12
            for i in range(n + 1):
                u = i / n
                wave = math.sin(u * math.pi * 3 + seed) * 2
                pts.append((r.x + u * r.width, r.y + wave))
            for i in range(n + 1):
                u = (n - i) / n
                wave = math.sin(u * math.pi * 3 + seed + 1) * 2
                pts.append((r.x + u * r.width, r.bottom - wave))
            pygame.draw.polygon(surf, OUTLINE, pts)
            pygame.draw.polygon(surf, CRUST_LO,
                                [(p[0], p[1] + 1) for p in pts])
            pygame.draw.polygon(surf, CRUST_MID,
                                [(p[0], p[1] + 2) for p in pts])
            # Crumb dots scatter
            rng = random.Random(seed + y * 7)
            for _ in range(int(r.width * h / 18)):
                bx = rng.randint(r.x + 4, r.right - 4)
                by = rng.randint(r.y + 2, r.bottom - 2)
                _aa_filled_circle(surf, bx, by, 1, CRUMB)
            # Highlight band on top
            hl = pygame.Rect(r.x + 6, r.y + 2, r.width - 12, max(2, h // 3))
            pygame.draw.rect(surf, CRUST_HI, hl, border_radius=h // 4)
        elif kind == LAYER_CHEESE:
            r = pygame.Rect(x - 6, y, w + 12, h)
            pygame.draw.rect(surf, OUTLINE, r.inflate(4, 4), border_radius=4)
            pygame.draw.rect(surf, _shade(CHEESE, -30), r.inflate(2, 2),
                             border_radius=3)
            pygame.draw.rect(surf, CHEESE, r, border_radius=3)
            # Drippy cheese tongues at the edges
            for sx in (r.x + 8, r.right - 12):
                drop_h = 6
                pts = [(sx, r.bottom),
                       (sx + 4, r.bottom + drop_h),
                       (sx + 8, r.bottom)]
                pygame.draw.polygon(surf, OUTLINE,
                                    [(p[0], p[1] + 1) for p in pts])
                pygame.draw.polygon(surf, CHEESE, pts)
        elif kind == LAYER_LETTUCE:
            r = pygame.Rect(x - 8, y - 2, w + 16, h + 4)
            pygame.draw.rect(surf, OUTLINE, r.inflate(2, 2), border_radius=3)
            pygame.draw.rect(surf, LETTUCE_LO, r.inflate(0, 0), border_radius=3)
            # Frilly upper edge - little bumps
            n_bumps = max(5, r.width // 7)
            for i in range(n_bumps):
                bx = int(r.x + (i + 0.5) * r.width / n_bumps)
                by = r.y
                _aa_filled_circle(surf, bx, by, 4, OUTLINE)
                _aa_filled_circle(surf, bx, by, 3, LETTUCE_MID)
                _aa_filled_circle(surf, bx - 1, by - 1, 2, LETTUCE_HI)
            # Frilly lower edge
            for i in range(n_bumps):
                bx = int(r.x + (i + 0.5) * r.width / n_bumps)
                by = r.bottom
                _aa_filled_circle(surf, bx, by, 3, OUTLINE)
                _aa_filled_circle(surf, bx, by, 2, LETTUCE_MID)

    def _stack(rect, gap_side='bottom'):
        x, y, w, h = rect
        # Build sequence top->down (or reverse for bot pillar)
        if gap_side == 'bottom':
            seq = SEQ[:]  # top pillar: bun_top at the very top
        else:
            seq = list(reversed(SEQ))  # bot pillar: bun_top at the bottom (closest to ground)
        cy = y
        i = 0
        while cy < y + h:
            kind = seq[i % len(seq)]
            lh = HEIGHTS[kind]
            r = pygame.Rect(x, cy, w, min(lh, y + h - cy))
            _draw_layer(r, kind)
            cy += lh
            i += 1

    _stack(top_rect, gap_side='bottom')
    _stack(bot_rect, gap_side='top')

    # Toothpick skewer running through the centre of the bottom pillar
    pick_x = bot_rect.centerx
    pick_top = bot_rect.top - 18
    pick_bot = bot_rect.top + min(bot_rect.height - 4, 90)
    pygame.draw.line(surf, OUTLINE, (pick_x, pick_top),
                     (pick_x, pick_bot), 4)
    pygame.draw.line(surf, WOOD_HI, (pick_x, pick_top + 1),
                     (pick_x, pick_bot - 1), 2)
    # Decorative cellophane frill at the top of the toothpick
    frill = [(pick_x - 7, pick_top - 2),
             (pick_x + 7, pick_top - 6),
             (pick_x, pick_top + 2)]
    pygame.draw.polygon(surf, OUTLINE, [(p[0], p[1] + 1) for p in frill])
    pygame.draw.polygon(surf, KFC_RED, frill)


# ----- Variant registry -----------------------------------------------------

KFC_VARIANTS = {
    1: ("V1 - Dog & Drum Tower",  draw_kfc_v1),
    2: ("V2 - Mega Frankfurter",  draw_kfc_v2),
    3: ("V3 - KFC Bucket Stack",  draw_kfc_v3),
    4: ("V4 - Corn Dog Crispy",   draw_kfc_v4),
    5: ("V5 - Crispy Skyscraper", draw_kfc_v5),
}


@contextlib.contextmanager
def install_variant(n: int):
    """Monkey-patch the live draw_pillar_pair entrypoint to route every pillar
    in the rendered scene to the chosen KFC variant. `Pipe.draw` looks up
    `draw_pillar_pair` in its OWN module namespace (because of the
    `from game.pillar_variants import draw_pillar_pair` at top of
    entities.py), so we patch BOTH locations to be safe.
    """
    if n not in KFC_VARIANTS:
        raise ValueError(f"unknown KFC variant {n}; valid: {sorted(KFC_VARIANTS)}")
    _, fn = KFC_VARIANTS[n]
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
