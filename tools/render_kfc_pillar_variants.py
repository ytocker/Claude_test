"""KFC powerup pillar transformation - round 2: refined V2-V5 with sub-variants.

Round 1 picked V2/V3/V4/V5 (V1 dropped). Round 2 invests more in each design
and offers 3 sub-variants (a/b/c) per design family for final selection. The
4 chosen finals will then be wired into game/pillar_variants.py and picked
randomly per pillar (`seed % 4`) when the KFC powerup is active.

12 sub-variants:

  V2 - Mega Frankfurter (one giant sausage-in-bun pillar)
    V2a Classic Mustard   plump bun, sausage poking out top + bottom,
                          mustard zigzag, sesame top, chicken-wing accent
    V2b Chili Cheese      same body + dripping chili meat sauce + melted
                          american cheese drip + scattered chopped chili
    V2c Bacon Wrapped     diagonal bacon strips spiralling round the
                          sausage + crispy bacon highlights

  V3 - KFC Bucket (red+white striped bucket stack)
    V3a Classic KFC       refined stripes, white "KFC" label band,
                          mixed chicken overflow (drum + nugget + wing)
    V3b Family Feast      taller buckets, gold "FAMILY" label, big
                          overflow piles + chain of pennants on flagpole
    V3c Combo Meal        bucket + adjacent fries box + soda cup with
                          straw clustered around the pillar

  V4 - Corn Dog Crispy (battered rod with stick at gap)
    V4a Classic Golden    refined dimensional crumb bumps + honey-mustard
                          drips + wood-grain stick with red ribbon
    V4b Spicy Red         red-tinted batter + hot-sauce drips + cooling
                          ranch-cream drips + chilli pepper accent
    V4c Sesame Sprinkle   sesame seeds embedded in batter + lighter
                          tan-gold tone + double-stick crossed at gap

  V5 - Crispy Skyscraper (multi-layer sandwich tower)
    V5a Classic Stack     bun-top / fillet / cheese / lettuce / fillet /
                          bun-bot, refined wave-edge fillets, sesame top
    V5b Mega Crunch       adds golden onion-ring layers + crispy bacon
                          strips between layers
    V5c BBQ Pickle        BBQ-sauce drip between layers + green pickle
                          slices + red-onion rings

Picker only - does NOT modify any `game/` file. install_variant(key)
monkey-patches draw_pillar_pair in BOTH game.pillar_variants and
game.entities (the import binding in entities.py is what Pipe.draw
actually calls).
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
KFC_RED     = (212,  34,  34)
KFC_RED_D   = (152,  18,  18)
KFC_WHITE   = (250, 245, 235)
KFC_GOLD    = (242, 196,  72)
KFC_GOLD_D  = (174, 130,  20)

# Condiments / extras
MUSTARD     = (252, 206,  56)
MUSTARD_HI  = (255, 234, 130)
KETCHUP     = (210,  44,  40)
KETCHUP_HI  = (244,  92,  72)
CHILI_LO    = (122,  28,  18)
CHILI_MID   = (172,  52,  30)
CHILI_HI    = (218,  86,  46)
CHEESE      = (252, 184,  60)
CHEESE_HI   = (255, 220, 110)
LETTUCE_HI  = (140, 200,  78)
LETTUCE_MID = ( 86, 158,  64)
LETTUCE_LO  = ( 52, 106,  40)
PICKLE_HI   = (174, 220, 110)
PICKLE_MID  = (106, 162,  62)
PICKLE_LO   = ( 56, 102,  36)
ONION_HI    = (252, 222, 162)
ONION_MID   = (224, 168,  78)
BACON_HI    = (240, 156, 104)
BACON_MID   = (192,  78,  56)
BACON_FAT   = (252, 224, 196)
BBQ_HI      = (164,  72,  32)
BBQ_MID     = (118,  46,  20)
BBQ_LO      = ( 78,  28,  10)
HOT_HI      = (240,  82,  50)
HOT_MID     = (190,  44,  28)
RANCH_HI    = (252, 246, 230)
RANCH_MID   = (220, 212, 184)
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
    gfx.filled_circle(surf, cx, cy, r, color)
    gfx.aacircle(surf, cx, cy, r, color)


def _aa_outline_polygon(surf, pts, fill, outline=OUTLINE, ow=2):
    pygame.draw.polygon(surf, fill, pts)
    pygame.draw.polygon(surf, outline, pts, ow)


def _bumpy_circle(surf, cx, cy, r, color, *, hi=None, lo=None,
                  outline=OUTLINE, jitter=0.2, seed=0):
    """Lumpy filled circle (irregular fried-piece silhouette)."""
    rng = random.Random(seed)
    n = 11
    pts = []
    for i in range(n):
        a = i * 2 * math.pi / n
        rr = r + rng.uniform(-r * jitter, r * jitter)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.92))
    pygame.draw.polygon(surf, outline, pts)
    pygame.draw.polygon(surf, lo or _shade(color, -28),
                        [(p[0], p[1] + 1) for p in pts])
    pygame.draw.polygon(surf, color, [(p[0], p[1]) for p in pts])
    if hi:
        pts_i = [(cx + (x - cx) * 0.55, cy + (y - cy) * 0.55 - 1)
                 for (x, y) in pts]
        pygame.draw.polygon(surf, hi, pts_i)


# ----- Food primitives ------------------------------------------------------

def draw_drumstick(surf, cx, cy, w, h, *, tilt=0, bone_top=True, seed=0):
    """Cartoon fried drumstick. Pear-shape meat blob + bone nub."""
    layer = pygame.Surface((w + 14, h + 14), pygame.SRCALPHA)
    lw, lh = layer.get_size()
    meat_rect = pygame.Rect(7, 9, w, int(h * 0.78))
    pygame.draw.ellipse(layer, OUTLINE, meat_rect.inflate(4, 4))
    pygame.draw.ellipse(layer, CRUST_LO, meat_rect.inflate(2, 2))
    pygame.draw.ellipse(layer, CRUST_MID, meat_rect)
    pygame.draw.ellipse(
        layer, CRUST_HI,
        meat_rect.inflate(-int(w * 0.45), -int(h * 0.45))
                 .move(-int(w * 0.10), -int(h * 0.06)))
    rng = random.Random(seed * 13 + 7)
    for _ in range(9):
        bx = rng.randint(meat_rect.left + 4, meat_rect.right - 4)
        by = rng.randint(meat_rect.top + 4, meat_rect.bottom - 4)
        _aa_filled_circle(layer, bx, by, 1, CRUMB)
    bone_w = max(5, int(w * 0.32))
    bone_h = max(8, int(h * 0.28))
    if bone_top:
        bx = 7 + (w - bone_w) // 2
        by = 0
    else:
        bx = 7 + (w - bone_w) // 2
        by = lh - bone_h - 4
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


def draw_chicken_nugget(surf, cx, cy, r, *, jitter_seed=0):
    _bumpy_circle(surf, cx, cy, r, CRUST_MID, hi=CRUST_HI,
                  lo=CRUST_LO, jitter=0.22, seed=jitter_seed)
    rng = random.Random(jitter_seed * 17)
    for _ in range(3):
        bx = int(cx + rng.uniform(-r * 0.5, r * 0.5))
        by = int(cy + rng.uniform(-r * 0.5, r * 0.5))
        _aa_filled_circle(surf, bx, by, 1, CRUMB)


def draw_chicken_wing(surf, cx, cy, w, h, *, flip=False):
    """Cartoon fried chicken wing: drumette + wingette + bone tip."""
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
    _aa_filled_circle(surf, bone_x + (5 if not flip else 0), cy, 2, BONE)


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


def draw_sesame(surf, rect, n=8, seed=0, band='top'):
    """Tiny ivory tear-drops scattered on the top/bottom of a bun."""
    rng = random.Random(seed * 17 + 91)
    for _ in range(n):
        x = rng.randint(rect.x + 4, rect.right - 4)
        if band == 'top':
            y = rng.randint(rect.y + 3, rect.y + max(4, rect.height // 3))
        else:
            y = rng.randint(rect.bottom - max(4, rect.height // 3),
                            rect.bottom - 3)
        pygame.draw.ellipse(surf, OUTLINE,
                            pygame.Rect(x - 2, y - 1, 4, 3))
        pygame.draw.ellipse(surf, (250, 234, 196),
                            pygame.Rect(x - 1, y - 1, 3, 2))


def draw_bacon_strip(surf, x1, y1, x2, y2, *, w=8):
    """Diagonal bacon strip with fat marbling bands."""
    angle = math.atan2(y2 - y1, x2 - x1)
    nx = -math.sin(angle) * w / 2
    ny = math.cos(angle) * w / 2
    pts = [(x1 - nx, y1 - ny), (x2 - nx, y2 - ny),
           (x2 + nx, y2 + ny), (x1 + nx, y1 + ny)]
    pygame.draw.polygon(surf, OUTLINE, [(p[0], p[1] + 1) for p in pts])
    pygame.draw.polygon(surf, BACON_MID, pts)
    # Fat marbling band along the centre
    cpts = [(x1 - nx * 0.35, y1 - ny * 0.35),
            (x2 - nx * 0.35, y2 - ny * 0.35),
            (x2 + nx * 0.10, y2 + ny * 0.10),
            (x1 + nx * 0.10, y1 + ny * 0.10)]
    pygame.draw.polygon(surf, BACON_FAT, cpts)
    pygame.draw.polygon(surf, BACON_HI,
                        [(p[0] - nx * 0.20, p[1] - ny * 0.20) for p in cpts[:2]] +
                        [(p[0] - nx * 0.30, p[1] - ny * 0.30) for p in cpts[2:]])


def draw_pickle_slice(surf, cx, cy, r):
    pygame.draw.circle(surf, OUTLINE, (cx, cy + 1), r + 1)
    pygame.draw.circle(surf, PICKLE_LO, (cx, cy), r)
    pygame.draw.circle(surf, PICKLE_MID, (cx - 1, cy - 1), max(2, r - 2))
    # Inner seed dots
    rng = random.Random(cx * 7 + cy)
    for _ in range(3):
        sx = cx + rng.randint(-r // 2, r // 2)
        sy = cy + rng.randint(-r // 2, r // 2)
        _aa_filled_circle(surf, sx, sy, 1, PICKLE_HI)


def draw_onion_ring(surf, cx, cy, r):
    pygame.draw.circle(surf, OUTLINE, (cx, cy + 1), r + 1)
    pygame.draw.circle(surf, CRUST_LO, (cx, cy), r)
    pygame.draw.circle(surf, CRUST_MID, (cx, cy), r)
    inner_r = max(2, r // 2)
    pygame.draw.circle(surf, OUTLINE, (cx, cy), inner_r + 1)
    pygame.draw.circle(surf, ONION_MID, (cx, cy), inner_r)
    pygame.draw.circle(surf, ONION_HI, (cx - 1, cy - 1), max(1, inner_r - 1))
    # Crispy bumps on outer ring
    rng = random.Random(cx * 31 + cy * 11)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi)
        rr = r - 2
        bx = int(cx + math.cos(a) * rr)
        by = int(cy + math.sin(a) * rr)
        _aa_filled_circle(surf, bx, by, 1, CRUMB)


def draw_pennant(surf, x1, y1, length, *, color=KFC_RED, tail_up=True):
    pen_h = 8
    sign = -1 if tail_up else 1
    pts = [(x1, y1),
           (x1 + length, y1 + sign * pen_h // 2),
           (x1, y1 + sign * pen_h)]
    pygame.draw.polygon(surf, OUTLINE, [(p[0] + 1, p[1] + 1) for p in pts])
    pygame.draw.polygon(surf, color, pts)


def draw_fries_box(surf, rect, *, n_fries=8, seed=0):
    """Red-and-white fries box with golden fries poking out the top."""
    x, y, w, h = rect
    box_top_w = w
    box_bot_w = max(8, int(w * 0.78))
    poly = [(x, y + h * 0.30),
            (x + box_top_w, y + h * 0.30),
            (x + (box_top_w - box_bot_w) // 2 + box_bot_w, y + h),
            (x + (box_top_w - box_bot_w) // 2, y + h)]
    pygame.draw.polygon(surf, OUTLINE, [(p[0], p[1] + 1) for p in poly])
    pygame.draw.polygon(surf, KFC_WHITE, poly)
    # Stripes
    for i in range(3):
        u0 = (i + 0.20) / 3
        u1 = (i + 0.55) / 3
        pygame.draw.polygon(
            surf, KFC_RED,
            [(poly[0][0] + (poly[1][0] - poly[0][0]) * u0, poly[0][1]),
             (poly[0][0] + (poly[1][0] - poly[0][0]) * u1, poly[0][1]),
             (poly[3][0] + (poly[2][0] - poly[3][0]) * u1, poly[2][1]),
             (poly[3][0] + (poly[2][0] - poly[3][0]) * u0, poly[2][1])])
    pygame.draw.polygon(surf, OUTLINE, poly, 2)
    # Fries poking out
    rng = random.Random(seed)
    for i in range(n_fries):
        u = (i + 0.5) / n_fries
        fx = int(x + 4 + u * (w - 8))
        fy = int(y + h * 0.30 - 4 - rng.randint(0, 16))
        fy_top = fy - rng.randint(10, 24)
        pygame.draw.line(surf, OUTLINE, (fx, fy + 1), (fx, fy_top + 1), 5)
        pygame.draw.line(surf, CRUST_LO, (fx, fy), (fx, fy_top), 4)
        pygame.draw.line(surf, MUSTARD, (fx - 1, fy_top + 2),
                         (fx - 1, fy_top + 6), 1)


def draw_drink_cup(surf, rect):
    """Red soda cup with white lid + striped straw."""
    x, y, w, h = rect
    cup = [(x + 2, y + h * 0.18),
           (x + w - 2, y + h * 0.18),
           (x + w - 5, y + h),
           (x + 5, y + h)]
    pygame.draw.polygon(surf, OUTLINE, [(p[0], p[1] + 1) for p in cup])
    pygame.draw.polygon(surf, KFC_RED, cup)
    # Vertical white stripe (KFC swoosh hint)
    swoosh = [(x + w * 0.32, y + h * 0.24),
              (x + w * 0.62, y + h * 0.24),
              (x + w * 0.50, y + h * 0.92),
              (x + w * 0.30, y + h * 0.92)]
    pygame.draw.polygon(surf, KFC_WHITE, swoosh)
    # Lid
    lid = pygame.Rect(int(x), int(y + h * 0.10), int(w), int(h * 0.18))
    pygame.draw.rect(surf, OUTLINE, lid.inflate(2, 2), border_radius=4)
    pygame.draw.rect(surf, KFC_WHITE, lid, border_radius=3)
    # Straw
    straw = pygame.Rect(int(x + w * 0.55), int(y - h * 0.18),
                        4, int(h * 0.32))
    pygame.draw.rect(surf, OUTLINE, straw.inflate(2, 0), border_radius=2)
    pygame.draw.rect(surf, KFC_RED, straw, border_radius=2)
    # Straw stripe
    for sy in range(straw.y + 2, straw.bottom - 2, 5):
        pygame.draw.line(surf, KFC_WHITE, (straw.x, sy), (straw.right, sy), 2)


# ============================================================================
# V2 - Mega Frankfurter (refined base + 3 sub-variants)
# ============================================================================

def _draw_frank_body(surf, rect, *, gap_side):
    """Plump bun + sausage poking through; sausage caps emerge at the gap.

    gap_side='bottom' (top pillar): sausage cap at rect.bottom.
    gap_side='top'    (bot pillar): sausage cap at rect.y.
    Returns the inner sausage rect for further decoration.
    """
    x, y, w, h = rect
    bun = pygame.Rect(x - 4, y, w + 8, h)
    # Bun lobe shape: rounded
    radius = max(12, w // 2 + 8)
    pygame.draw.rect(surf, OUTLINE, bun.inflate(4, 4), border_radius=radius)
    pygame.draw.rect(surf, BUN_LO, bun.inflate(2, 2), border_radius=radius)
    pygame.draw.rect(surf, BUN_MID, bun, border_radius=radius)
    # Lit-side highlight
    hl = pygame.Rect(bun.x + 5, bun.y + 6,
                     max(4, bun.width // 3), max(4, bun.height - 14))
    pygame.draw.rect(surf, BUN_HI, hl, border_radius=radius // 2)
    # Sausage tube poking through the bun from end to end
    # The sausage extends slightly OUT of the bun on the gap end.
    sx = bun.x + 8
    sw = bun.width - 16
    sausage_extend = 8
    if gap_side == 'bottom':
        sy = bun.y + 14
        sh_ = bun.height - 14 + sausage_extend
    else:
        sy = bun.y - sausage_extend
        sh_ = bun.height - 14 + sausage_extend
        if sy < 0:
            sh_ -= -sy
            sy = 0
    s = pygame.Rect(sx, sy, sw, sh_)
    radius_s = sw // 2 + 2
    pygame.draw.rect(surf, OUTLINE, s.inflate(4, 4), border_radius=radius_s)
    pygame.draw.rect(surf, SAUSAGE_LO, s.inflate(2, 2), border_radius=radius_s)
    pygame.draw.rect(surf, SAUSAGE_MID, s, border_radius=radius_s)
    # Sausage lit highlight
    pygame.draw.rect(surf, SAUSAGE_HI,
                     pygame.Rect(s.x + 3, s.y + 4, max(2, s.width // 3),
                                 max(2, s.height - 14)),
                     border_radius=s.width // 4)
    return s, bun


def draw_kfc_v2a(surf, top_rect, bot_rect, palette, seed):
    """V2a Classic Mustard - mustard zigzag + sesame top + chicken wing."""
    s_top, b_top = _draw_frank_body(surf, top_rect, gap_side='bottom')
    s_bot, b_bot = _draw_frank_body(surf, bot_rect, gap_side='top')
    # Mustard zigzag along sausage length
    for s in (s_top, s_bot):
        n = max(6, s.height // 12)
        amp = max(3, s.width // 4)
        cx = s.centerx
        pts = [(cx + (amp if i % 2 == 0 else -amp),
                s.y + 6 + i * (s.height - 12) // max(1, n - 1))
               for i in range(n)]
        pygame.draw.lines(surf, _shade(MUSTARD, -40), False, pts, 5)
        pygame.draw.lines(surf, MUSTARD, False, pts, 3)
        pygame.draw.lines(surf, MUSTARD_HI, False, pts, 1)
    # Sesame on the top of the bun (visible end of top pillar)
    draw_sesame(surf, b_top, n=12, seed=seed, band='top')
    # Chicken wing accent at gap edges
    draw_chicken_wing(surf, bot_rect.centerx + 14, bot_rect.top + 12,
                      48, 32, flip=False)
    draw_chicken_wing(surf, top_rect.centerx - 14, top_rect.bottom - 12,
                      40, 26, flip=True)


def draw_kfc_v2b(surf, top_rect, bot_rect, palette, seed):
    """V2b Chili Cheese - chili meat sauce dripping + cheese melt."""
    s_top, b_top = _draw_frank_body(surf, top_rect, gap_side='bottom')
    s_bot, b_bot = _draw_frank_body(surf, bot_rect, gap_side='top')
    rng = random.Random(seed)
    for s in (s_top, s_bot):
        # Lumpy chili meat strip running down the sausage
        chili_w = s.width - 4
        chili = pygame.Rect(s.centerx - chili_w // 2, s.y + 4,
                            chili_w, s.height - 12)
        pygame.draw.rect(surf, _shade(CHILI_LO, -10), chili.inflate(2, 2),
                         border_radius=4)
        pygame.draw.rect(surf, CHILI_MID, chili, border_radius=4)
        # Chili meat lumps
        for i in range(max(8, chili.height // 6)):
            cx = rng.randint(chili.left + 2, chili.right - 2)
            cy = rng.randint(chili.top + 3, chili.bottom - 3)
            r = rng.randint(2, 4)
            _aa_filled_circle(surf, cx, cy, r, CHILI_HI)
        # Tiny chopped jalapenos
        for i in range(5):
            jx = rng.randint(chili.left + 1, chili.right - 1)
            jy = rng.randint(chili.top + 2, chili.bottom - 2)
            pygame.draw.line(surf, LETTUCE_MID, (jx, jy), (jx + 2, jy), 2)
            pygame.draw.line(surf, LETTUCE_HI, (jx, jy), (jx + 1, jy), 1)
        # Drippy melted cheese cascading off the chili (3 thick drips)
        for i in range(3):
            dx = chili.left + 6 + i * (chili.width - 12) // 2
            dy = chili.bottom - 4
            dl = 18 + (i % 2) * 6
            draw_drip(surf, dx, dy, dl, color=CHEESE, hi=CHEESE_HI, width=5)
    # Sesame on the visible end-bun
    draw_sesame(surf, b_top, n=10, seed=seed, band='top')


def draw_kfc_v2c(surf, top_rect, bot_rect, palette, seed):
    """V2c Bacon Wrapped - diagonal bacon strips spiralling round sausage."""
    s_top, b_top = _draw_frank_body(surf, top_rect, gap_side='bottom')
    s_bot, b_bot = _draw_frank_body(surf, bot_rect, gap_side='top')
    for s in (s_top, s_bot):
        # Spiral diagonal bacon strips at fixed pitch
        strip_w = 10
        spacing = 16
        pitch = 12  # diagonal lean
        n = max(2, s.height // spacing + 2)
        for i in range(n):
            y0 = s.y + i * spacing - 8
            y1 = y0 + spacing + 4
            # Strip from left to right with diagonal lean
            draw_bacon_strip(surf, s.left, y0,
                             s.right, y0 + pitch, w=strip_w)
        # Mustard squiggle running over the bacon
        n_m = max(5, s.height // 14)
        amp = max(3, s.width // 4)
        cx = s.centerx
        pts = [(cx + (amp if i % 2 == 0 else -amp),
                s.y + 8 + i * (s.height - 14) // max(1, n_m - 1))
               for i in range(n_m)]
        pygame.draw.lines(surf, _shade(MUSTARD, -40), False, pts, 4)
        pygame.draw.lines(surf, MUSTARD, False, pts, 2)
    draw_sesame(surf, b_top, n=10, seed=seed, band='top')


# ============================================================================
# V3 - KFC Bucket (refined base + 3 sub-variants)
# ============================================================================

def _draw_bucket(surf, rect, *, label_text="KFC", label_color=KFC_RED,
                 label_bg=KFC_WHITE, n_stripes=4, seed=0,
                 draw_label=True):
    """Single bucket. Returns (rim_rect, label_band_rect). The label band
    rect is returned so callers can choose to draw the text upright AFTER
    flipping the whole layer (top-pillar buckets)."""
    x, y, w, h = rect
    top_w = w
    bot_w = max(8, int(w * 0.74))
    tl = (x, y + 4)
    tr = (x + top_w, y + 4)
    br = (x + (top_w - bot_w) // 2 + bot_w, y + h)
    bl = (x + (top_w - bot_w) // 2, y + h)
    poly = [tl, tr, br, bl]
    # Drop shadow
    pygame.draw.polygon(surf, (*SHADOW, 60), [(px, py + 2) for (px, py) in poly])
    pygame.draw.polygon(surf, OUTLINE, [(px, py + 1) for (px, py) in poly])
    pygame.draw.polygon(surf, KFC_WHITE, poly)
    # Stripes (trapezoidal)
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
    # Curved bottom (perspective hint)
    bottom_band = pygame.Rect(int(bl[0]) - 2, int(br[1]) - 4,
                              int(br[0] - bl[0]) + 4, 6)
    pygame.draw.ellipse(surf, OUTLINE, bottom_band.inflate(2, 2))
    pygame.draw.ellipse(surf, KFC_RED_D, bottom_band)
    # Outline
    pygame.draw.polygon(surf, OUTLINE, poly, 2)
    # Top rim band
    rim = pygame.Rect(tl[0] - 2, tl[1] - 4, top_w + 4, 8)
    pygame.draw.rect(surf, OUTLINE, rim.inflate(2, 2), border_radius=4)
    pygame.draw.rect(surf, KFC_RED_D, rim, border_radius=4)
    pygame.draw.rect(surf, KFC_RED, rim.inflate(-4, -3), border_radius=3)
    # Label band placement (white box). The TEXT is drawn here only when
    # `draw_label=True`; for flipped top-pillar buckets, the caller draws
    # the text upright in world coords AFTER the flip.
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


def _draw_chicken_overflow(surf, rim, seed=0, mix='basic'):
    """Pile of fried chicken pieces overflowing the rim of a bucket.

    mix='basic'  - mostly nuggets
    mix='varied' - drumstick + wing + nugget
    mix='heavy'  - 5+ pieces, varied
    """
    rng = random.Random(seed)
    pieces = []
    if mix == 'basic':
        pieces = [('nug', rim.left + rim.width * u, rim.top - 2)
                  for u in (0.20, 0.50, 0.80)]
    elif mix == 'varied':
        pieces = [
            ('drum', rim.left + 6, rim.top - 3, -22),
            ('nug',  rim.centerx + 1, rim.top - 5, 0),
            ('wing', rim.right - 8, rim.top - 4, 12),
        ]
    else:  # heavy
        pieces = [
            ('drum', rim.left + 6, rim.top - 5, -25),
            ('drum', rim.right - 10, rim.top - 6, 18),
            ('wing', rim.centerx - 8, rim.top - 9, -10),
            ('nug',  rim.centerx + 9, rim.top - 4, 0),
            ('nug',  rim.centerx,    rim.top - 12, 0),
        ]
    for kind, *args in pieces:
        if kind == 'nug':
            cx, cy = args[0], args[1]
            draw_chicken_nugget(surf, int(cx), int(cy), 7,
                                jitter_seed=seed * 11 + int(cx))
        elif kind == 'drum':
            cx, cy, tilt = args
            draw_drumstick(surf, int(cx), int(cy), 18, 22,
                           tilt=tilt, bone_top=False, seed=seed + int(cx))
        elif kind == 'wing':
            cx, cy, _ = args + (0,) if len(args) == 2 else args
            draw_chicken_wing(surf, int(cx), int(cy), 22, 16,
                              flip=(cx > rim.centerx))


def _stack_buckets(surf, rect, *, gap_side, label, label_color,
                   bucket_h=64, mix='varied', seed=0):
    """Stack buckets in a top or bottom pillar rect. Top pillar's gap-side
    bucket is flipped (rim faces gap). Text labels are drawn upright in
    world coords after the flip so they don't appear mirrored."""
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
            layer = pygame.Surface((rb.width, rb.height + 14),
                                   pygame.SRCALPHA)
            inner_rect = pygame.Rect(0, 4, rb.width, rb.height - 4)
            local_rim, local_label = _draw_bucket(
                layer, inner_rect, label_text=label,
                label_color=label_color, seed=seed + i, draw_label=False)
            layer = pygame.transform.flip(layer, False, True)
            surf.blit(layer, rb.topleft)
            # Compute world coords of rim + label (flipping mirrors y).
            lh = layer.get_height()
            real_rim = pygame.Rect(
                rb.x + local_rim.x,
                rb.y + (lh - local_rim.bottom),
                local_rim.width, local_rim.height)
            real_label = pygame.Rect(
                rb.x + local_label.x,
                rb.y + (lh - local_label.bottom),
                local_label.width, local_label.height)
            rims.append((real_rim, real_label))
        else:
            inner_rect = pygame.Rect(rb.x, rb.y, rb.width, rb.height)
            rim, label_band = _draw_bucket(
                surf, inner_rect, label_text=label,
                label_color=label_color, seed=seed + i, draw_label=True)
            rims.append((rim, label_band))

    # Draw upright text on flipped top-pillar buckets (label drawn last so
    # it appears in world space, not mirrored).
    if gap_side == 'bottom':
        try:
            font = pygame.font.SysFont(None, 14, bold=True)
            txt = font.render(label, True, label_color)
            for _rim, lb in rims:
                surf.blit(txt, (lb.centerx - txt.get_width() // 2,
                                  lb.centery - txt.get_height() // 2))
        except Exception:
            pass

    # Overflow pile only on the bucket nearest to the gap.
    if rims:
        gap_rim = rims[-1][0]
        _draw_chicken_overflow(surf, gap_rim, seed=seed + 17, mix=mix)


def _draw_pennant_chain(surf, base_x, base_y, length, *, n=3,
                        color=KFC_RED, alt=KFC_GOLD):
    """Vertical flagpole + multiple pennants tied along it."""
    # Pole
    pole = pygame.Rect(base_x - 2, base_y - length, 4, length)
    pygame.draw.rect(surf, OUTLINE, pole.inflate(2, 0), border_radius=2)
    pygame.draw.rect(surf, BUN_LO, pole, border_radius=2)
    # Pennants
    for i in range(n):
        py = base_y - length + 4 + i * (length - 8) // max(1, n - 1)
        c = color if i % 2 == 0 else alt
        draw_pennant(surf, base_x, py, 14 + (i % 2) * 4, color=c,
                     tail_up=False)


def draw_kfc_v3a(surf, top_rect, bot_rect, palette, seed):
    """V3a Classic KFC - red+white stripes, clean KFC label, varied chicken."""
    _stack_buckets(surf, bot_rect, gap_side='top',
                   label="KFC", label_color=KFC_RED, mix='varied', seed=seed)
    _stack_buckets(surf, top_rect, gap_side='bottom',
                   label="KFC", label_color=KFC_RED, mix='varied',
                   seed=seed + 100)
    # Single hot-dog flagpole + 1 pennant on top of bot pillar
    pole_x = bot_rect.centerx
    pole_top = bot_rect.top - 4
    pole_h = 26
    pole = pygame.Rect(pole_x - 4, pole_top - pole_h, 8, pole_h)
    pygame.draw.rect(surf, OUTLINE, pole.inflate(2, 0), border_radius=3)
    pygame.draw.rect(surf, BUN_LO, pole, border_radius=3)
    pygame.draw.rect(surf, SAUSAGE_MID, pole.inflate(-3, -2), border_radius=2)
    # Single pennant
    draw_pennant(surf, pole_x + 4, pole_top - pole_h + 4, 18, color=KFC_RED,
                 tail_up=False)


def draw_kfc_v3b(surf, top_rect, bot_rect, palette, seed):
    """V3b Family Feast - taller buckets, gold FAMILY label, big overflow."""
    _stack_buckets(surf, bot_rect, gap_side='top',
                   label="FAMILY", label_color=KFC_RED_D,
                   bucket_h=80, mix='heavy', seed=seed)
    _stack_buckets(surf, top_rect, gap_side='bottom',
                   label="FAMILY", label_color=KFC_RED_D,
                   bucket_h=80, mix='heavy', seed=seed + 200)
    # Multi-pennant chain on a flagpole
    _draw_pennant_chain(surf, bot_rect.centerx, bot_rect.top - 2,
                        length=42, n=3,
                        color=KFC_RED, alt=KFC_GOLD)


def draw_kfc_v3c(surf, top_rect, bot_rect, palette, seed):
    """V3c Combo Meal - bucket + side fries box + soda cup with straw."""
    # Slimmer central bucket so we have room for sides
    inner_top = pygame.Rect(top_rect.x + 6, top_rect.y, top_rect.width - 12,
                            top_rect.height)
    inner_bot = pygame.Rect(bot_rect.x + 6, bot_rect.y, bot_rect.width - 12,
                            bot_rect.height)
    _stack_buckets(surf, inner_bot, gap_side='top',
                   label="COMBO", label_color=KFC_RED,
                   bucket_h=70, mix='basic', seed=seed)
    _stack_buckets(surf, inner_top, gap_side='bottom',
                   label="COMBO", label_color=KFC_RED,
                   bucket_h=70, mix='basic', seed=seed + 300)
    # Fries box clinging to the side near the gap
    fries_rect = pygame.Rect(bot_rect.centerx - 14, bot_rect.top + 8,
                             28, 36)
    draw_fries_box(surf, fries_rect, n_fries=7, seed=seed)
    # Drink cup at the OTHER pillar's gap edge
    cup_rect = pygame.Rect(top_rect.centerx - 12, top_rect.bottom - 38,
                           24, 36)
    draw_drink_cup(surf, cup_rect)


# ============================================================================
# V4 - Corn Dog Crispy (refined base + 3 sub-variants)
# ============================================================================

def _draw_corndog_body(surf, rect, *, batter_lo, batter_mid, batter_hi,
                      crumb_color=CRUMB, sesame=False, seed=0):
    """Refined corn-dog rod with dimensional crumb bumps."""
    x, y, w, h = rect
    rod = pygame.Rect(x - 1, y, w + 2, h)
    radius = max(8, w // 2 + 2)
    # Drop shadow
    pygame.draw.rect(surf, (*SHADOW, 60),
                     rod.inflate(6, 6).move(2, 2), border_radius=radius)
    pygame.draw.rect(surf, OUTLINE, rod.inflate(4, 4), border_radius=radius)
    pygame.draw.rect(surf, batter_lo, rod.inflate(2, 2), border_radius=radius)
    pygame.draw.rect(surf, batter_mid, rod, border_radius=radius)
    # Lit-side gradient
    hl = pygame.Rect(rod.x + 4, rod.y + 4,
                     max(3, rod.width // 3), rod.height - 8)
    pygame.draw.rect(surf, batter_hi, hl, border_radius=radius // 2)
    # Dimensional crumb bumps: each has a shadow + highlight pair
    rng = random.Random(seed * 19 + 7)
    n = max(28, h // 5)
    for _ in range(n):
        bx = rng.randint(rod.x + 3, rod.right - 3)
        by = rng.randint(rod.y + 4, rod.bottom - 4)
        r = rng.randint(2, 4)
        _aa_filled_circle(surf, bx + 1, by + 1, r, _shade(batter_lo, -10))
        _aa_filled_circle(surf, bx, by, r, _shade(batter_mid, +18))
        _aa_filled_circle(surf, bx - 1, by - 1, max(1, r - 2), crumb_color)
    # Sesame seeds embedded (only if sesame variant)
    if sesame:
        for _ in range(max(8, h // 20)):
            sx = rng.randint(rod.x + 4, rod.right - 4)
            sy = rng.randint(rod.y + 6, rod.bottom - 6)
            pygame.draw.ellipse(surf, OUTLINE,
                                pygame.Rect(sx - 2, sy - 1, 4, 3))
            pygame.draw.ellipse(surf, (250, 234, 196),
                                pygame.Rect(sx - 1, sy - 1, 3, 2))
    return rod


def _draw_wood_stick(surf, cx, top_y, length, *, ribbon_color=None):
    stick_w = 10
    stick = pygame.Rect(cx - stick_w // 2, top_y, stick_w, length)
    pygame.draw.rect(surf, OUTLINE, stick.inflate(2, 2), border_radius=4)
    pygame.draw.rect(surf, WOOD_LO, stick, border_radius=4)
    pygame.draw.rect(surf, WOOD_HI,
                     pygame.Rect(stick.x + 2, stick.y + 2, 3, stick.height - 4),
                     border_radius=2)
    # Wood-grain striations
    for i in range(2):
        pygame.draw.line(surf, _shade(WOOD_LO, -40),
                         (stick.x + 2, stick.y + 6 + i * 8),
                         (stick.right - 2, stick.y + 6 + i * 8), 1)
    # Optional red ribbon tied at the top
    if ribbon_color is not None:
        rib_y = stick.y + 4
        rib = pygame.Rect(stick.x - 2, rib_y, stick_w + 4, 5)
        pygame.draw.rect(surf, OUTLINE, rib.inflate(2, 2), border_radius=2)
        pygame.draw.rect(surf, ribbon_color, rib, border_radius=2)
        # Bow tails
        pts1 = [(stick.x - 2, rib_y + 2), (stick.x - 8, rib_y - 2),
                (stick.x - 6, rib_y + 6)]
        pts2 = [(stick.right + 2, rib_y + 2), (stick.right + 8, rib_y - 2),
                (stick.right + 6, rib_y + 6)]
        pygame.draw.polygon(surf, OUTLINE, [(p[0], p[1] + 1) for p in pts1])
        pygame.draw.polygon(surf, ribbon_color, pts1)
        pygame.draw.polygon(surf, OUTLINE, [(p[0], p[1] + 1) for p in pts2])
        pygame.draw.polygon(surf, ribbon_color, pts2)


def draw_kfc_v4a(surf, top_rect, bot_rect, palette, seed):
    """V4a Classic Golden - rich golden batter, honey-mustard drips."""
    _draw_corndog_body(surf, top_rect, batter_lo=CRUST_LO,
                       batter_mid=CRUST_MID, batter_hi=CRUST_HI,
                       seed=seed)
    _draw_corndog_body(surf, bot_rect, batter_lo=CRUST_LO,
                       batter_mid=CRUST_MID, batter_hi=CRUST_HI,
                       seed=seed + 1)
    # Honey-mustard drips along an edge (couple per pillar)
    for rect in (top_rect, bot_rect):
        for i, dx in enumerate((rect.x + 4, rect.right - 6)):
            dy = rect.y + 16 + i * 22
            if dy + 24 < rect.bottom:
                draw_drip(surf, dx, dy, 22 + i * 2,
                          color=(244, 178, 60), hi=(255, 222, 130), width=4)
    # Wooden stick at the gap
    _draw_wood_stick(surf, top_rect.centerx, top_rect.bottom - 2, 26,
                     ribbon_color=RIBBON_HI)
    _draw_wood_stick(surf, bot_rect.centerx, bot_rect.top - 26, 26,
                     ribbon_color=RIBBON_HI)


def draw_kfc_v4b(surf, top_rect, bot_rect, palette, seed):
    """V4b Spicy Red - red-tinted batter + hot-sauce + ranch cooling drips."""
    spicy_lo  = (148,  44,  16)
    spicy_mid = (212,  92,  40)
    spicy_hi  = (244, 162,  88)
    _draw_corndog_body(surf, top_rect, batter_lo=spicy_lo,
                       batter_mid=spicy_mid, batter_hi=spicy_hi,
                       seed=seed)
    _draw_corndog_body(surf, bot_rect, batter_lo=spicy_lo,
                       batter_mid=spicy_mid, batter_hi=spicy_hi,
                       seed=seed + 1)
    # Hot sauce drips (red) on one side, ranch (cream) on the other
    for rect in (top_rect, bot_rect):
        draw_drip(surf, rect.x + 4, rect.y + 18, 24,
                  color=HOT_MID, hi=HOT_HI, width=5)
        draw_drip(surf, rect.right - 6, rect.y + 36, 22,
                  color=RANCH_MID, hi=RANCH_HI, width=4)
        draw_drip(surf, rect.x + 4, rect.y + 60, 18,
                  color=HOT_MID, hi=HOT_HI, width=4)
    # Tiny chilli pepper accent at the gap
    for cx, cy in ((bot_rect.centerx - 14, bot_rect.top + 6),
                   (top_rect.centerx + 14, top_rect.bottom - 6)):
        # Chilli body
        pygame.draw.ellipse(surf, OUTLINE,
                            pygame.Rect(cx - 8, cy - 3, 16, 8))
        pygame.draw.ellipse(surf, HOT_MID,
                            pygame.Rect(cx - 7, cy - 2, 14, 6))
        pygame.draw.ellipse(surf, HOT_HI,
                            pygame.Rect(cx - 5, cy - 2, 8, 3))
        # Stem
        pygame.draw.line(surf, LETTUCE_LO, (cx - 6, cy - 3), (cx - 9, cy - 6), 2)
        pygame.draw.line(surf, LETTUCE_HI, (cx - 6, cy - 3), (cx - 8, cy - 5), 1)
    # Wooden stick at the gap
    _draw_wood_stick(surf, top_rect.centerx, top_rect.bottom - 2, 26,
                     ribbon_color=HOT_MID)
    _draw_wood_stick(surf, bot_rect.centerx, bot_rect.top - 26, 26,
                     ribbon_color=HOT_MID)


def draw_kfc_v4c(surf, top_rect, bot_rect, palette, seed):
    """V4c Sesame Sprinkle - lighter tan batter + sesame seeds + double sticks."""
    light_lo  = (170, 116,  44)
    light_mid = (240, 196,  98)
    light_hi  = (255, 232, 158)
    _draw_corndog_body(surf, top_rect, batter_lo=light_lo,
                       batter_mid=light_mid, batter_hi=light_hi,
                       sesame=True, seed=seed)
    _draw_corndog_body(surf, bot_rect, batter_lo=light_lo,
                       batter_mid=light_mid, batter_hi=light_hi,
                       sesame=True, seed=seed + 1)
    # Honey-mustard drips
    for rect in (top_rect, bot_rect):
        for i in range(2):
            dx = rect.x + 4 + i * (rect.width - 8)
            dy = rect.y + 24 + i * 20
            if dy + 22 < rect.bottom:
                draw_drip(surf, dx, dy, 20,
                          color=(244, 196, 80), hi=(255, 232, 130), width=4)
    # Crossed double sticks at the gap
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


# ============================================================================
# V5 - Crispy Skyscraper (refined base + 3 sub-variants)
# ============================================================================

LAYER_BUN_TOP   = 'bun_top'
LAYER_BUN_BOT   = 'bun_bot'
LAYER_FILLET    = 'fillet'
LAYER_CHEESE    = 'cheese'
LAYER_LETTUCE   = 'lettuce'
LAYER_BACON     = 'bacon'
LAYER_ONION     = 'onion'
LAYER_PICKLE    = 'pickle'
LAYER_BBQ       = 'bbq'

LAYER_HEIGHTS = {
    LAYER_BUN_TOP:  30,
    LAYER_BUN_BOT:  20,
    LAYER_FILLET:   28,
    LAYER_CHEESE:   12,
    LAYER_LETTUCE:  14,
    LAYER_BACON:    10,
    LAYER_ONION:    16,
    LAYER_PICKLE:   12,
    LAYER_BBQ:       6,
}


def _draw_layer(surf, rect, kind, *, seed=0):
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
        hl = pygame.Rect(r.x + 4, r.y + 3, r.width - 8,
                         max(3, int(h * 0.40)))
        pygame.draw.rect(surf, BUN_HI, hl, border_radius=int(hl.height * 0.8))
        draw_sesame(surf, r, n=8, seed=seed + y, band='top')
    elif kind == LAYER_BUN_BOT:
        r = pygame.Rect(x - 2, y, w + 4, h)
        pygame.draw.rect(surf, OUTLINE, r.inflate(4, 4),
                         border_radius=int(h * 0.6))
        pygame.draw.rect(surf, BUN_LO, r.inflate(2, 2),
                         border_radius=int(h * 0.6))
        pygame.draw.rect(surf, BUN_MID, r, border_radius=int(h * 0.6))
    elif kind == LAYER_FILLET:
        r = pygame.Rect(x - 6, y, w + 12, h)
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
        pygame.draw.polygon(surf, CRUST_LO, [(p[0], p[1] + 1) for p in pts])
        pygame.draw.polygon(surf, CRUST_MID, [(p[0], p[1] + 2) for p in pts])
        rng = random.Random(seed + y * 7)
        for _ in range(int(r.width * h / 18)):
            bx = rng.randint(r.x + 4, r.right - 4)
            by = rng.randint(r.y + 2, r.bottom - 2)
            _aa_filled_circle(surf, bx, by, 1, CRUMB)
        hl = pygame.Rect(r.x + 6, r.y + 2, r.width - 12, max(2, h // 3))
        pygame.draw.rect(surf, CRUST_HI, hl, border_radius=h // 4)
    elif kind == LAYER_CHEESE:
        r = pygame.Rect(x - 6, y, w + 12, h)
        pygame.draw.rect(surf, OUTLINE, r.inflate(4, 4), border_radius=4)
        pygame.draw.rect(surf, _shade(CHEESE, -30), r.inflate(2, 2),
                         border_radius=3)
        pygame.draw.rect(surf, CHEESE, r, border_radius=3)
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
        pygame.draw.rect(surf, LETTUCE_LO, r, border_radius=3)
        n_bumps = max(5, r.width // 7)
        for i in range(n_bumps):
            bx = int(r.x + (i + 0.5) * r.width / n_bumps)
            for by, rr in ((r.y, 4), (r.bottom, 3)):
                _aa_filled_circle(surf, bx, by, rr, OUTLINE)
                _aa_filled_circle(surf, bx, by, max(1, rr - 1), LETTUCE_MID)
                _aa_filled_circle(surf, bx - 1, by - 1, max(1, rr - 2),
                                  LETTUCE_HI)
    elif kind == LAYER_BACON:
        r = pygame.Rect(x - 4, y, w + 8, h)
        pygame.draw.rect(surf, OUTLINE, r.inflate(2, 2), border_radius=2)
        pygame.draw.rect(surf, BACON_MID, r, border_radius=2)
        # Marbling stripe
        m = pygame.Rect(r.x, r.centery - 1, r.width, 2)
        pygame.draw.rect(surf, BACON_FAT, m)
        pygame.draw.rect(surf, BACON_HI,
                         pygame.Rect(r.x + 2, r.y + 1, r.width - 4, 2))
        # Wavy bottom edge bumps
        for i, sx in enumerate(range(r.x + 4, r.right - 4, 8)):
            _aa_filled_circle(surf, sx, r.bottom, 2, OUTLINE)
            _aa_filled_circle(surf, sx, r.bottom, 1, BACON_HI)
    elif kind == LAYER_ONION:
        r = pygame.Rect(x - 6, y, w + 12, h)
        # Two onion rings side by side
        ring_r = max(4, h // 2)
        for sx in (r.x + ring_r + 2, r.right - ring_r - 2):
            draw_onion_ring(surf, sx, r.centery, ring_r)
    elif kind == LAYER_PICKLE:
        r = pygame.Rect(x - 6, y, w + 12, h)
        pickle_r = max(4, h // 2)
        for sx in (r.x + pickle_r + 2, r.centerx, r.right - pickle_r - 2):
            draw_pickle_slice(surf, sx, r.centery, pickle_r)
    elif kind == LAYER_BBQ:
        r = pygame.Rect(x - 8, y, w + 16, h)
        pygame.draw.rect(surf, OUTLINE, r.inflate(2, 2), border_radius=3)
        pygame.draw.rect(surf, BBQ_LO, r.inflate(0, 0), border_radius=3)
        pygame.draw.rect(surf, BBQ_MID,
                         pygame.Rect(r.x + 2, r.y + 1, r.width - 4, max(1, h - 2)),
                         border_radius=2)
        pygame.draw.rect(surf, BBQ_HI,
                         pygame.Rect(r.x + 4, r.y + 1, max(2, r.width // 4), 1))
        # Drippy tongues at edges
        for sx in (r.x + 8, r.right - 12):
            pts = [(sx, r.bottom), (sx + 4, r.bottom + 6), (sx + 8, r.bottom)]
            pygame.draw.polygon(surf, OUTLINE,
                                [(p[0], p[1] + 1) for p in pts])
            pygame.draw.polygon(surf, BBQ_MID, pts)


def _stack_layers(surf, rect, sequence, gap_side='bottom', seed=0):
    x, y, w, h = rect
    if gap_side == 'top':
        seq = list(reversed(sequence))
    else:
        seq = list(sequence)
    cy = y
    i = 0
    while cy < y + h:
        kind = seq[i % len(seq)]
        lh = LAYER_HEIGHTS[kind]
        r = pygame.Rect(x, cy, w, min(lh, y + h - cy))
        _draw_layer(surf, r, kind, seed=seed)
        cy += lh
        i += 1


def _draw_skewer(surf, rect, *, top_color=KFC_RED):
    pick_x = rect.centerx
    pick_top = rect.top - 18
    pick_bot = rect.top + min(rect.height - 4, 90)
    pygame.draw.line(surf, OUTLINE, (pick_x, pick_top), (pick_x, pick_bot), 4)
    pygame.draw.line(surf, WOOD_HI, (pick_x, pick_top + 1),
                     (pick_x, pick_bot - 1), 2)
    frill = [(pick_x - 7, pick_top - 2),
             (pick_x + 7, pick_top - 6),
             (pick_x, pick_top + 2)]
    pygame.draw.polygon(surf, OUTLINE, [(p[0], p[1] + 1) for p in frill])
    pygame.draw.polygon(surf, top_color, frill)


def draw_kfc_v5a(surf, top_rect, bot_rect, palette, seed):
    """V5a Classic Stack - bun/fillet/cheese/lettuce/fillet/bun."""
    seq = [LAYER_BUN_TOP, LAYER_FILLET, LAYER_CHEESE, LAYER_LETTUCE,
           LAYER_FILLET, LAYER_BUN_BOT]
    _stack_layers(surf, top_rect, seq, gap_side='bottom', seed=seed)
    _stack_layers(surf, bot_rect, seq, gap_side='top', seed=seed)
    _draw_skewer(surf, bot_rect)


def draw_kfc_v5b(surf, top_rect, bot_rect, palette, seed):
    """V5b Mega Crunch - adds onion-ring + bacon between layers."""
    seq = [LAYER_BUN_TOP, LAYER_FILLET, LAYER_BACON, LAYER_CHEESE,
           LAYER_ONION, LAYER_LETTUCE, LAYER_FILLET, LAYER_BUN_BOT]
    _stack_layers(surf, top_rect, seq, gap_side='bottom', seed=seed)
    _stack_layers(surf, bot_rect, seq, gap_side='top', seed=seed)
    _draw_skewer(surf, bot_rect, top_color=KFC_GOLD)


def draw_kfc_v5c(surf, top_rect, bot_rect, palette, seed):
    """V5c BBQ Pickle - BBQ-sauce drip + green pickle slices."""
    seq = [LAYER_BUN_TOP, LAYER_FILLET, LAYER_BBQ, LAYER_PICKLE,
           LAYER_CHEESE, LAYER_FILLET, LAYER_BUN_BOT]
    _stack_layers(surf, top_rect, seq, gap_side='bottom', seed=seed)
    _stack_layers(surf, bot_rect, seq, gap_side='top', seed=seed)
    _draw_skewer(surf, bot_rect, top_color=BBQ_HI)


# ----- Variant registry -----------------------------------------------------

KFC_VARIANTS = {
    'v2a': ("V2a Classic Mustard",  draw_kfc_v2a),
    'v2b': ("V2b Chili Cheese",     draw_kfc_v2b),
    'v2c': ("V2c Bacon Wrapped",    draw_kfc_v2c),
    'v3a': ("V3a Classic KFC",      draw_kfc_v3a),
    'v3b': ("V3b Family Feast",     draw_kfc_v3b),
    'v3c': ("V3c Combo Meal",       draw_kfc_v3c),
    'v4a': ("V4a Classic Golden",   draw_kfc_v4a),
    'v4b': ("V4b Spicy Red",        draw_kfc_v4b),
    'v4c': ("V4c Sesame Sprinkle",  draw_kfc_v4c),
    'v5a': ("V5a Classic Stack",    draw_kfc_v5a),
    'v5b': ("V5b Mega Crunch",      draw_kfc_v5b),
    'v5c': ("V5c BBQ Pickle",       draw_kfc_v5c),
}

# Per-design family grouping for the harness's per-family compare strips.
FAMILIES = {
    'v2': ("V2 - Mega Frankfurter", ['v2a', 'v2b', 'v2c']),
    'v3': ("V3 - KFC Bucket",       ['v3a', 'v3b', 'v3c']),
    'v4': ("V4 - Corn Dog Crispy",  ['v4a', 'v4b', 'v4c']),
    'v5': ("V5 - Crispy Skyscraper",['v5a', 'v5b', 'v5c']),
}


@contextlib.contextmanager
def install_variant(key: str):
    """Monkey-patch draw_pillar_pair so every pillar in the rendered scene
    uses the chosen KFC sub-variant. `Pipe.draw` looks up `draw_pillar_pair`
    in entities.py's OWN namespace (because of `from game.pillar_variants
    import draw_pillar_pair`), so we patch BOTH locations.
    """
    if key not in KFC_VARIANTS:
        raise ValueError(f"unknown KFC variant {key!r}; valid: "
                         f"{sorted(KFC_VARIANTS)}")
    _, fn = KFC_VARIANTS[key]
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
