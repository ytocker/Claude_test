"""V3 KFC Bucket Stack - flag-planted-in-bucket picker (5 variants).

Round-1 V3 had a hot-dog flagpole with a single pennant sticking up FROM
the top bucket. Feedback: put the flags directly IN the top bucket
(planted in the chicken pile) and add more crispy items.

All 5 variants share:
  - 3 vertically stacked KFC buckets per pillar (red+white striped)
  - Top pillar uses inverted hanging buckets (rim faces gap)
  - The gap-facing bucket of the BOTTOM pillar gets:
      * a heavier chicken/crispy overflow pile
      * flags planted directly in the pile (no separate flagpole)
  - Top pillar inverted buckets have chicken overflow only (no flags)

Variants differ in flag style + crispy mix:
  v3_stack1 Mini Flag      one small red pennant on toothpick + drumstick
                           + wing + nuggets + popcorn chicken
  v3_stack2 Trio Flags     three fanned-out pennants (red/gold/red) +
                           drumsticks + nuggets + crispy fries
  v3_stack3 KFC Banner     one prominent rectangular "KFC" banner +
                           drumsticks + wing + onion rings + nuggets
  v3_stack4 Crossed Flags  two pennants forming an X + heavy popcorn
                           chicken pile + crispy tenders
  v3_stack5 Five Flags     five tiny toothpick flags across the rim +
                           max overflow: drumsticks + wings + nuggets
                           + tenders + popcorn

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

CRUST_HI  = (250, 212, 118)
CRUST_MID = (224, 162,  62)
CRUST_LO  = (148,  84,  20)
CRUMB     = (255, 232, 168)
BONE      = (248, 240, 210)
BONE_SHA  = (190, 175, 140)

KFC_RED     = (212,  34,  34)
KFC_RED_D   = (152,  18,  18)
KFC_WHITE   = (250, 245, 235)
KFC_GOLD    = (242, 196,  72)

ONION_HI    = (252, 222, 162)
ONION_MID   = (224, 168,  78)

WOOD_HI     = (230, 192, 132)
WOOD_LO     = (162, 116,  62)

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


# ----- Crispy item primitives -----------------------------------------------

def draw_drumstick(surf, cx, cy, w, h, *, tilt=0, bone_top=True, seed=0):
    """Cartoon fried drumstick."""
    layer = pygame.Surface((w + 14, h + 14), pygame.SRCALPHA)
    lh = layer.get_height()
    meat_rect = pygame.Rect(7, 9, w, int(h * 0.78))
    pygame.draw.ellipse(layer, OUTLINE, meat_rect.inflate(4, 4))
    pygame.draw.ellipse(layer, CRUST_LO, meat_rect.inflate(2, 2))
    pygame.draw.ellipse(layer, CRUST_MID, meat_rect)
    pygame.draw.ellipse(layer, CRUST_HI,
                        meat_rect.inflate(-int(w * 0.45), -int(h * 0.45))
                                 .move(-int(w * 0.10), -int(h * 0.06)))
    rng = random.Random(seed * 13 + 7)
    for _ in range(8):
        bx = rng.randint(meat_rect.left + 4, meat_rect.right - 4)
        by = rng.randint(meat_rect.top + 4, meat_rect.bottom - 4)
        _aa_filled_circle(layer, bx, by, 1, CRUMB)
    bone_w = max(5, int(w * 0.32))
    bone_h = max(8, int(h * 0.28))
    if bone_top:
        bx, by = 7 + (w - bone_w) // 2, 0
    else:
        bx, by = 7 + (w - bone_w) // 2, lh - bone_h - 4
    bone_rect = pygame.Rect(bx, by, bone_w, bone_h)
    pygame.draw.rect(layer, OUTLINE, bone_rect.inflate(4, 2), border_radius=4)
    pygame.draw.rect(layer, BONE_SHA, bone_rect.inflate(2, 0), border_radius=3)
    pygame.draw.rect(layer, BONE, bone_rect.inflate(-2, -1), border_radius=3)
    knob_y = bone_rect.top + 1 if bone_top else bone_rect.bottom - 1
    _aa_filled_circle(layer, bone_rect.centerx - bone_w // 4, knob_y,
                      max(2, bone_w // 3), BONE)
    _aa_filled_circle(layer, bone_rect.centerx + bone_w // 4, knob_y,
                      max(2, bone_w // 3), BONE)
    if tilt:
        layer = pygame.transform.rotate(layer, tilt)
    rect = layer.get_rect(center=(cx, cy))
    surf.blit(layer, rect.topleft)


def draw_chicken_wing(surf, cx, cy, w, h, *, flip=False):
    """Cartoon fried chicken wing - drumette + wingette + bone tip."""
    big = pygame.Rect(cx - w // 2, cy - h // 2, int(w * 0.65), int(h * 0.85))
    pygame.draw.ellipse(surf, OUTLINE, big.inflate(4, 4))
    pygame.draw.ellipse(surf, CRUST_LO, big.inflate(2, 2))
    pygame.draw.ellipse(surf, CRUST_MID, big)
    pygame.draw.ellipse(surf, CRUST_HI,
                        big.inflate(-int(w * 0.30), -int(h * 0.40)))
    sm = pygame.Rect(0, 0, int(w * 0.55), int(h * 0.55))
    if flip:
        sm.topright = (cx - int(w * 0.08), cy - int(h * 0.10))
    else:
        sm.topleft = (cx + int(w * 0.08), cy - int(h * 0.10))
    pygame.draw.ellipse(surf, OUTLINE, sm.inflate(4, 4))
    pygame.draw.ellipse(surf, CRUST_LO, sm.inflate(2, 2))
    pygame.draw.ellipse(surf, CRUST_MID, sm)
    pygame.draw.ellipse(surf, CRUST_HI,
                        sm.inflate(-int(w * 0.30), -int(h * 0.36)).move(-2, -1))
    bone_x = sm.right + 2 if not flip else sm.left - 6
    pygame.draw.rect(surf, OUTLINE,
                     pygame.Rect(bone_x - 1, cy - 2, 7, 5),
                     border_radius=2)
    pygame.draw.rect(surf, BONE,
                     pygame.Rect(bone_x, cy - 1, 5, 3),
                     border_radius=2)


def draw_chicken_nugget(surf, cx, cy, r, *, jitter_seed=0):
    """Lumpy fried-chicken nugget."""
    rng = random.Random(jitter_seed)
    pts = []
    n = 9
    for i in range(n):
        a = i * 2 * math.pi / n
        rr = r + rng.uniform(-1.4, 1.6)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.85))
    pygame.draw.polygon(surf, OUTLINE, pts)
    pygame.draw.polygon(surf, CRUST_LO, [(p[0], p[1] + 1) for p in pts])
    pygame.draw.polygon(surf, CRUST_MID, [(p[0], p[1]) for p in pts])
    pts_i = [(cx + (x - cx) * 0.55, cy + (y - cy) * 0.55 - 1)
             for (x, y) in pts]
    pygame.draw.polygon(surf, CRUST_HI, pts_i)
    for _ in range(3):
        bx = int(cx + rng.uniform(-r * 0.6, r * 0.6))
        by = int(cy + rng.uniform(-r * 0.6, r * 0.6))
        _aa_filled_circle(surf, bx, by, 1, CRUMB)


def draw_popcorn(surf, cx, cy, r=4, *, jitter_seed=0):
    """Tiny popcorn-chicken bite."""
    rng = random.Random(jitter_seed)
    pts = []
    n = 7
    for i in range(n):
        a = i * 2 * math.pi / n
        rr = r + rng.uniform(-0.8, 1.0)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.9))
    pygame.draw.polygon(surf, OUTLINE, pts)
    pygame.draw.polygon(surf, CRUST_MID, [(p[0], p[1]) for p in pts])
    pts_i = [(cx + (x - cx) * 0.55, cy + (y - cy) * 0.55 - 1)
             for (x, y) in pts]
    pygame.draw.polygon(surf, CRUST_HI, pts_i)


def draw_fry(surf, cx, cy, w, h, *, tilt=0):
    """Crispy french fry - rounded golden stick."""
    layer = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
    fry_rect = pygame.Rect(4, 4, w, h)
    pygame.draw.rect(layer, OUTLINE, fry_rect.inflate(2, 2),
                     border_radius=2)
    pygame.draw.rect(layer, CRUST_LO, fry_rect.inflate(1, 1),
                     border_radius=2)
    pygame.draw.rect(layer, CRUST_MID, fry_rect, border_radius=2)
    # Lit-side highlight stripe
    pygame.draw.rect(layer, CRUST_HI,
                     pygame.Rect(fry_rect.x + 1, fry_rect.y + 1,
                                 max(1, w // 3), h - 2),
                     border_radius=1)
    if tilt:
        layer = pygame.transform.rotate(layer, tilt)
    rect = layer.get_rect(center=(cx, cy))
    surf.blit(layer, rect.topleft)


def draw_onion_ring(surf, cx, cy, r):
    pygame.draw.circle(surf, OUTLINE, (cx, cy + 1), r + 1)
    pygame.draw.circle(surf, CRUST_LO, (cx, cy), r)
    pygame.draw.circle(surf, CRUST_MID, (cx, cy), r)
    inner = max(2, r // 2)
    pygame.draw.circle(surf, OUTLINE, (cx, cy), inner + 1)
    pygame.draw.circle(surf, ONION_MID, (cx, cy), inner)
    pygame.draw.circle(surf, ONION_HI, (cx - 1, cy - 1), max(1, inner - 1))
    rng = random.Random(cx * 31 + cy * 11)
    for _ in range(5):
        a = rng.uniform(0, 2 * math.pi)
        rr = r - 2
        bx = int(cx + math.cos(a) * rr)
        by = int(cy + math.sin(a) * rr)
        _aa_filled_circle(surf, bx, by, 1, CRUMB)


def draw_tender(surf, cx, cy, w, h, *, tilt=0):
    """Crispy chicken tender - elongated nugget."""
    layer = pygame.Surface((w + 10, h + 10), pygame.SRCALPHA)
    rect = pygame.Rect(5, 5, w, h)
    radius = h // 2
    pygame.draw.rect(layer, OUTLINE, rect.inflate(4, 4), border_radius=radius)
    pygame.draw.rect(layer, CRUST_LO, rect.inflate(2, 2), border_radius=radius)
    pygame.draw.rect(layer, CRUST_MID, rect, border_radius=radius)
    pygame.draw.rect(layer, CRUST_HI,
                     pygame.Rect(rect.x + 3, rect.y + 2, w - 6,
                                 max(2, h // 3)),
                     border_radius=radius // 2)
    rng = random.Random(cx * 7 + cy)
    for _ in range(4):
        bx = rng.randint(rect.left + 3, rect.right - 3)
        by = rng.randint(rect.top + 2, rect.bottom - 2)
        _aa_filled_circle(layer, bx, by, 1, CRUMB)
    if tilt:
        layer = pygame.transform.rotate(layer, tilt)
    out = layer.get_rect(center=(cx, cy))
    surf.blit(layer, out.topleft)


# ----- Bucket primitive -----------------------------------------------------

def _draw_bucket(surf, rect, *, label_text="KFC", label_color=KFC_RED,
                 label_bg=KFC_WHITE, n_stripes=4, draw_label=True):
    """Single red+white-striped bucket trapezoid. Returns (rim_rect,
    label_band_rect) so callers can draw the upright text after flipping."""
    x, y, w, h = rect
    top_w = w
    bot_w = max(8, int(w * 0.74))
    tl = (x, y + 4)
    tr = (x + top_w, y + 4)
    br = (x + (top_w - bot_w) // 2 + bot_w, y + h)
    bl = (x + (top_w - bot_w) // 2, y + h)
    poly = [tl, tr, br, bl]
    pygame.draw.polygon(surf, OUTLINE, [(px, py + 1) for (px, py) in poly])
    pygame.draw.polygon(surf, KFC_WHITE, poly)
    for i in range(n_stripes):
        u0 = (i + 0.10) / n_stripes
        u1 = (i + 0.55) / n_stripes
        sx0_top = tl[0] + (tr[0] - tl[0]) * u0
        sx1_top = tl[0] + (tr[0] - tl[0]) * u1
        sx0_bot = bl[0] + (br[0] - bl[0]) * u0
        sx1_bot = bl[0] + (br[0] - bl[0]) * u1
        pygame.draw.polygon(
            surf, KFC_RED,
            [(sx0_top, tl[1]), (sx1_top, tl[1]),
             (sx1_bot, br[1]), (sx0_bot, br[1])])
    pygame.draw.polygon(surf, OUTLINE, poly, 2)
    rim = pygame.Rect(tl[0] - 2, tl[1] - 4, top_w + 4, 8)
    pygame.draw.rect(surf, OUTLINE, rim.inflate(2, 2), border_radius=4)
    pygame.draw.rect(surf, KFC_RED_D, rim, border_radius=4)
    pygame.draw.rect(surf, KFC_RED, rim.inflate(-4, -3), border_radius=3)
    label_y = (tl[1] + br[1]) // 2 - 6
    label_w = max(20, top_w - 16)
    label_x = (tl[0] + tr[0]) // 2 - label_w // 2
    font_band = pygame.Rect(label_x, label_y, label_w, 14)
    pygame.draw.rect(surf, OUTLINE, font_band.inflate(2, 2), border_radius=3)
    pygame.draw.rect(surf, label_bg, font_band, border_radius=3)
    if draw_label:
        try:
            font = pygame.font.SysFont(None, 14, bold=True)
            txt = font.render(label_text, True, label_color)
            surf.blit(txt, (font_band.centerx - txt.get_width() // 2,
                            font_band.centery - txt.get_height() // 2))
        except Exception:
            pass
    return rim, font_band


# ----- Flag primitives ------------------------------------------------------

def draw_pennant_in_pile(surf, base_x, base_y, *, length=18, height=10,
                        color=KFC_RED, tilt=0):
    """Triangular pennant on a thin toothpick stuck into the chicken pile.
    base_(x,y) is where the toothpick enters the pile (bottom of stick)."""
    stick_h = 16
    # Toothpick (thin wood)
    layer = pygame.Surface((length + 8, stick_h + height + 8),
                           pygame.SRCALPHA)
    sx = 4
    sy_bot = stick_h + height + 4
    sy_top = sy_bot - stick_h
    pygame.draw.line(layer, OUTLINE, (sx, sy_top - 1), (sx, sy_bot + 1), 4)
    pygame.draw.line(layer, WOOD_LO, (sx, sy_top), (sx, sy_bot), 2)
    pygame.draw.line(layer, WOOD_HI, (sx, sy_top + 1), (sx, sy_bot - 1), 1)
    # Triangular pennant attached to top of toothpick
    pen = [(sx, sy_top + 1),
           (sx + length, sy_top + height // 2 + 1),
           (sx, sy_top + height + 1)]
    pygame.draw.polygon(layer, OUTLINE, [(p[0] + 1, p[1] + 1) for p in pen])
    pygame.draw.polygon(layer, color, pen)
    # Tiny accent stripe
    pygame.draw.line(layer, KFC_WHITE,
                     (sx + 3, sy_top + height // 2 + 1),
                     (sx + length // 2, sy_top + height // 2 + 1), 1)
    if tilt:
        layer = pygame.transform.rotate(layer, tilt)
    out = layer.get_rect(midbottom=(base_x, base_y))
    surf.blit(layer, out.topleft)


def draw_banner_flag(surf, base_x, base_y, *, w=22, h=14, text="KFC",
                     color=KFC_RED):
    """Bigger rectangular banner with text on a toothpick."""
    stick_h = 18
    layer = pygame.Surface((w + 8, stick_h + h + 8), pygame.SRCALPHA)
    sx = 4
    sy_bot = stick_h + h + 4
    sy_top = sy_bot - stick_h
    pygame.draw.line(layer, OUTLINE, (sx, sy_top - 1), (sx, sy_bot + 1), 5)
    pygame.draw.line(layer, WOOD_LO, (sx, sy_top), (sx, sy_bot), 3)
    pygame.draw.line(layer, WOOD_HI, (sx, sy_top + 1), (sx, sy_bot - 1), 1)
    banner = pygame.Rect(sx, sy_top - h // 2, w, h)
    pygame.draw.rect(layer, OUTLINE, banner.inflate(2, 2), border_radius=2)
    pygame.draw.rect(layer, _shade(color, -30), banner.inflate(0, 0),
                     border_radius=2)
    pygame.draw.rect(layer, color, banner.inflate(-2, -2), border_radius=2)
    try:
        font = pygame.font.SysFont(None, 13, bold=True)
        txt = font.render(text, True, KFC_WHITE)
        layer.blit(txt, (banner.centerx - txt.get_width() // 2,
                         banner.centery - txt.get_height() // 2))
    except Exception:
        pass
    out = layer.get_rect(midbottom=(base_x, base_y))
    surf.blit(layer, out.topleft)


# ----- Chicken pile generators (size + style varies by variant) -------------

def _draw_chicken_pile_v1(surf, rim, seed):
    """Variant 1 mix: drumstick + wing + 3 nuggets + 2 popcorn."""
    cx = rim.centerx
    base_y = rim.top - 2
    draw_drumstick(surf, cx - 12, base_y - 6, 18, 22,
                   tilt=-22, bone_top=False, seed=seed)
    draw_chicken_wing(surf, cx + 10, base_y - 4, 22, 16, flip=False)
    for i, ux in enumerate((-6, 4, 14)):
        draw_chicken_nugget(surf, cx + ux + (i * 2 - 4),
                            base_y - 12 + (i % 2) * 4, 6,
                            jitter_seed=seed + i * 13)
    draw_popcorn(surf, cx - 4, base_y - 16, jitter_seed=seed + 7)
    draw_popcorn(surf, cx + 8, base_y - 18, jitter_seed=seed + 11)


def _draw_chicken_pile_v2(surf, rim, seed):
    """Variant 2 mix: 2 drumsticks + 4 nuggets + 2 fries."""
    cx = rim.centerx
    base_y = rim.top - 2
    draw_drumstick(surf, cx - 14, base_y - 6, 16, 20,
                   tilt=-30, bone_top=False, seed=seed)
    draw_drumstick(surf, cx + 12, base_y - 6, 16, 20,
                   tilt=22, bone_top=False, seed=seed + 5)
    for i, ux in enumerate((-8, 0, 8)):
        draw_chicken_nugget(surf, cx + ux,
                            base_y - 14 + (i % 2) * 3, 6,
                            jitter_seed=seed + i * 11)
    draw_chicken_nugget(surf, cx - 2, base_y - 22, 5,
                        jitter_seed=seed + 23)
    draw_fry(surf, cx - 18, base_y - 14, 4, 16, tilt=18)
    draw_fry(surf, cx + 18, base_y - 14, 4, 16, tilt=-18)


def _draw_chicken_pile_v3(surf, rim, seed):
    """Variant 3 mix: 2 drumsticks + 1 wing + 2 onion rings + 2 nuggets."""
    cx = rim.centerx
    base_y = rim.top - 2
    draw_drumstick(surf, cx - 13, base_y - 7, 17, 21,
                   tilt=-26, bone_top=False, seed=seed)
    draw_drumstick(surf, cx + 13, base_y - 7, 17, 21,
                   tilt=26, bone_top=False, seed=seed + 9)
    draw_chicken_wing(surf, cx, base_y - 12, 22, 16, flip=False)
    draw_onion_ring(surf, cx - 6, base_y - 18, 6)
    draw_onion_ring(surf, cx + 8, base_y - 20, 6)
    draw_chicken_nugget(surf, cx - 14, base_y - 16, 5,
                        jitter_seed=seed + 33)
    draw_chicken_nugget(surf, cx + 16, base_y - 14, 5,
                        jitter_seed=seed + 41)


def _draw_chicken_pile_v4(surf, rim, seed):
    """Variant 4 mix: heavy popcorn chicken pile + 2 tenders."""
    cx = rim.centerx
    base_y = rim.top - 2
    rng = random.Random(seed * 19)
    # 2 tenders flanking
    draw_tender(surf, cx - 14, base_y - 5, 16, 8, tilt=-16)
    draw_tender(surf, cx + 14, base_y - 5, 16, 8, tilt=16)
    # Popcorn chicken pile (dense)
    for i in range(10):
        u = (i + 0.5) / 10
        px = int(cx + (u - 0.5) * (rim.width - 12)
                 + rng.randint(-3, 3))
        py = int(base_y - 8 - rng.randint(0, 18))
        r = rng.randint(3, 5)
        draw_popcorn(surf, px, py, r=r, jitter_seed=seed + i * 7)


def _draw_chicken_pile_v5(surf, rim, seed):
    """Variant 5 mix: max overflow - drumsticks + wings + nuggets +
    tenders + popcorn (the kitchen sink)."""
    cx = rim.centerx
    base_y = rim.top - 2
    rng = random.Random(seed * 23)
    # 2 drumsticks
    draw_drumstick(surf, cx - 16, base_y - 6, 16, 20,
                   tilt=-30, bone_top=False, seed=seed)
    draw_drumstick(surf, cx + 16, base_y - 6, 16, 20,
                   tilt=30, bone_top=False, seed=seed + 7)
    # 2 wings
    draw_chicken_wing(surf, cx - 6, base_y - 14, 20, 14, flip=True)
    draw_chicken_wing(surf, cx + 8, base_y - 16, 20, 14, flip=False)
    # 4 nuggets
    for i, ux in enumerate((-8, 0, 8, 16)):
        draw_chicken_nugget(surf, cx + ux,
                            base_y - 22 - (i % 2) * 4, 5,
                            jitter_seed=seed + i * 19)
    # 1 tender on top
    draw_tender(surf, cx, base_y - 30, 14, 7, tilt=10)
    # 5 popcorn pieces sprinkled
    for i in range(5):
        px = int(cx - 12 + i * 6 + rng.randint(-2, 2))
        py = int(base_y - 28 - rng.randint(0, 8))
        draw_popcorn(surf, px, py, r=3,
                     jitter_seed=seed + 100 + i * 11)


# ----- Flag arrangement per variant -----------------------------------------

def _flags_v1(surf, rim):
    """Single mini pennant slightly off-centre."""
    draw_pennant_in_pile(surf, rim.centerx + 4, rim.top - 16,
                         length=16, color=KFC_RED, tilt=0)


def _flags_v2(surf, rim):
    """Three pennants fanned out (red / gold / red)."""
    draw_pennant_in_pile(surf, rim.centerx - 10, rim.top - 22,
                         length=12, color=KFC_RED, tilt=18)
    draw_pennant_in_pile(surf, rim.centerx,      rim.top - 28,
                         length=14, color=KFC_GOLD, tilt=0)
    draw_pennant_in_pile(surf, rim.centerx + 10, rim.top - 22,
                         length=12, color=KFC_RED, tilt=-18)


def _flags_v3(surf, rim):
    """Single wide rectangular 'KFC' banner."""
    draw_banner_flag(surf, rim.centerx, rim.top - 26,
                     w=24, h=14, text="KFC", color=KFC_RED)


def _flags_v4(surf, rim):
    """Two pennants tilted toward each other forming an X."""
    draw_pennant_in_pile(surf, rim.centerx - 8, rim.top - 20,
                         length=18, color=KFC_RED, tilt=-25)
    draw_pennant_in_pile(surf, rim.centerx + 8, rim.top - 20,
                         length=18, color=KFC_GOLD, tilt=25)


def _flags_v5(surf, rim):
    """Five tiny toothpick flags spread across the rim."""
    colors = [KFC_RED, KFC_GOLD, KFC_RED, KFC_GOLD, KFC_RED]
    n = 5
    for i, c in enumerate(colors):
        u = (i + 0.5) / n
        bx = int(rim.left + 4 + u * (rim.width - 8))
        # Alternating heights
        by = rim.top - 16 - (3 if i % 2 == 0 else 0)
        draw_pennant_in_pile(surf, bx, by, length=10, color=c,
                             tilt=(-10 if i % 2 == 0 else 10))


VARIANT_PILES = (_draw_chicken_pile_v1, _draw_chicken_pile_v2,
                 _draw_chicken_pile_v3, _draw_chicken_pile_v4,
                 _draw_chicken_pile_v5)

VARIANT_FLAGS = (_flags_v1, _flags_v2, _flags_v3, _flags_v4, _flags_v5)


# ----- Stack rendering ------------------------------------------------------

def _stack_buckets(surf, rect, *, gap_side, label="KFC",
                   bucket_h=64, seed=0, pile_fn=None, flag_fn=None):
    """Stack buckets in the rect. The gap-facing bucket gets the chicken
    pile (and flag arrangement, if flag_fn is provided)."""
    x, y, w, h = rect
    n = max(1, h // bucket_h)
    rims = []
    for i in range(n):
        if gap_side == 'top':
            rb = pygame.Rect(x - 4, y + h - (i + 1) * bucket_h,
                             w + 8, bucket_h - 4)
        else:
            rb = pygame.Rect(x - 4, y + i * bucket_h, w + 8, bucket_h - 4)
        if rb.bottom > y + h:
            rb.height -= rb.bottom - (y + h)
        if rb.top < y:
            rb.height -= y - rb.top
            rb.top = y
        if rb.height < 18:
            continue
        if gap_side == 'bottom':
            # Top pillar: flip vertically so rim points DOWN at gap
            layer = pygame.Surface((rb.width, rb.height + 14),
                                   pygame.SRCALPHA)
            inner_rect = pygame.Rect(0, 4, rb.width, rb.height - 4)
            local_rim, local_label = _draw_bucket(
                layer, inner_rect, label_text=label, draw_label=False)
            layer = pygame.transform.flip(layer, False, True)
            surf.blit(layer, rb.topleft)
            lh = layer.get_height()
            real_rim = pygame.Rect(rb.x + local_rim.x,
                                   rb.y + (lh - local_rim.bottom),
                                   local_rim.width, local_rim.height)
            real_label = pygame.Rect(rb.x + local_label.x,
                                     rb.y + (lh - local_label.bottom),
                                     local_label.width, local_label.height)
            rims.append((real_rim, real_label))
        else:
            rim, label_band = _draw_bucket(
                surf, pygame.Rect(rb.x, rb.y, rb.width, rb.height),
                label_text=label)
            rims.append((rim, label_band))

    # Draw upright text on flipped top-pillar buckets
    if gap_side == 'bottom':
        try:
            font = pygame.font.SysFont(None, 14, bold=True)
            txt = font.render(label, True, KFC_RED)
            for _rim, lb in rims:
                surf.blit(txt, (lb.centerx - txt.get_width() // 2,
                                  lb.centery - txt.get_height() // 2))
        except Exception:
            pass

    # Pile + flags only on gap-facing bucket
    if rims and pile_fn is not None:
        gap_rim = rims[-1][0]
        pile_fn(surf, gap_rim, seed)
        if flag_fn is not None and gap_side == 'top':
            # Flags only on bottom pillar's top bucket (upright, not flipped)
            flag_fn(surf, gap_rim)


def _make_v3_stack_drawer(idx):
    """Build a draw_v3_stackN function bound to the index's pile + flag fn."""
    pile_fn = VARIANT_PILES[idx - 1]
    flag_fn = VARIANT_FLAGS[idx - 1]

    def _draw(surf, top_rect, bot_rect, palette, seed):
        # Top pillar: hanging buckets w/ chicken overflow only (no flag)
        _stack_buckets(surf, top_rect, gap_side='bottom',
                       bucket_h=64, seed=seed + 100, pile_fn=pile_fn)
        # Bottom pillar: stacked buckets, top bucket gets pile + flags
        _stack_buckets(surf, bot_rect, gap_side='top',
                       bucket_h=64, seed=seed,
                       pile_fn=pile_fn, flag_fn=flag_fn)
    return _draw


draw_v3_stack1 = _make_v3_stack_drawer(1)
draw_v3_stack2 = _make_v3_stack_drawer(2)
draw_v3_stack3 = _make_v3_stack_drawer(3)
draw_v3_stack4 = _make_v3_stack_drawer(4)
draw_v3_stack5 = _make_v3_stack_drawer(5)


V3_STACK_VARIANTS = {
    'v3_stack1': ("V3-stack1 Mini Flag",     draw_v3_stack1),
    'v3_stack2': ("V3-stack2 Trio Flags",    draw_v3_stack2),
    'v3_stack3': ("V3-stack3 KFC Banner",    draw_v3_stack3),
    'v3_stack4': ("V3-stack4 Crossed Flags", draw_v3_stack4),
    'v3_stack5': ("V3-stack5 Five Flags",    draw_v3_stack5),
}


@contextlib.contextmanager
def install_variant(key: str):
    """Monkey-patch draw_pillar_pair so every pillar uses the chosen V3
    stack variant."""
    if key not in V3_STACK_VARIANTS:
        raise ValueError(f"unknown V3 stack variant {key!r}; valid: "
                         f"{sorted(V3_STACK_VARIANTS)}")
    _, fn = V3_STACK_VARIANTS[key]
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
