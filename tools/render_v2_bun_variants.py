"""V2 Mega Frankfurter - bun-style picker (5 side-bun treatments).

Round 1 V2 enclosed the sausage in a round ellipse bun. Feedback: the
sausage looks great but the bun should sit on the SIDES of the hot dog,
not as a round ellipse around it. This picker keeps the sausage +
mustard zigzag + ketchup dots + chicken-wing accents IDENTICAL to
round-1 V2 and only varies the bun treatment.

Layout (PIPE_W = 58):
  bun-left strip  : 18 px wide (extrudes 4 px outside the pillar)
  sausage central : 30 px wide
  bun-right strip : 18 px wide (extrudes 4 px outside the pillar)

5 bun treatments:
  v2_bun1 Classic Side    smooth golden side strips with rounded
                          corners and outer-edge highlights
  v2_bun2 Soft Cradle     side strips with curved inner edges that
                          gently hug the sausage at top + bottom
  v2_bun3 Brioche Knots   each side is 3-4 stacked plump knot
                          segments + sesame seeds, glossy darker
                          gold (looks torn-and-shared like brioche)
  v2_bun4 Pretzel Salt    same shape as classic but DARK MAHOGANY
                          pretzel glaze + scattered salt-grain dots
  v2_bun5 Sub Roll Cut    cross-section reveal: outer crust +
                          cream-white crumb facing the sausage,
                          like a sub roll sliced lengthwise

Picker only - no game/ files modified. install_variant(key)
context-manager-monkey-patches draw_pillar_pair in BOTH
game.pillar_variants AND game.entities (the import binding in
entities.py is what Pipe.draw actually calls).
"""
import contextlib
import math
import random

import pygame
import pygame.gfxdraw as gfx

from game import entities as gent
from game import pillar_variants as gpv


# ----- Cartoon palette (matches round-1 V2) ---------------------------------

# Bun
BUN_HI    = (252, 226, 178)
BUN_MID   = (232, 192, 130)
BUN_LO    = (188, 142,  78)
BUN_LINE  = (110,  72,  30)
BRIOCHE_HI  = (250, 212, 138)
BRIOCHE_MID = (218, 166,  90)
BRIOCHE_LO  = (158, 110,  46)
PRETZEL_HI  = (172, 110,  56)
PRETZEL_MID = (118,  64,  24)
PRETZEL_LO  = ( 64,  30,  12)
SALT_COLOR  = (252, 248, 240)
CRUMB_HI    = (252, 244, 222)   # interior bread crumb (sub roll cut)
CRUMB_MID   = (232, 218, 184)
CRUMB_LO    = (192, 174, 134)

# Sausage (frankfurter)
SAUSAGE_HI  = (228, 124,  92)
SAUSAGE_MID = (198,  82,  62)
SAUSAGE_LO  = (146,  46,  36)

# Fried chicken (for the wing accents)
CRUST_HI  = (250, 212, 118)
CRUST_MID = (224, 162,  62)
CRUST_LO  = (148,  84,  20)
CRUMB     = (255, 232, 168)
BONE      = (248, 240, 210)

# Condiments
MUSTARD     = (252, 206,  56)
MUSTARD_HI  = (255, 234, 130)
KETCHUP     = (210,  44,  40)
KETCHUP_HI  = (244,  92,  72)

OUTLINE = ( 38,  22,  10)
SHADOW  = ( 22,  14,   8)


# ----- Geometry constants ---------------------------------------------------

BUN_W       = 18    # each side
SAUSAGE_W   = 30
EXTRUDE     = 4     # bun extends this many px outside the pillar bounds
SAUSAGE_PROTRUDE = 8  # sausage pokes past gap-edge


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


def draw_chicken_wing(surf, cx, cy, w, h, *, flip=False):
    """Cartoon fried chicken wing - drumette + wingette + bone tip.
    Identical to the round-1 V2 wing accent."""
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


# ----- Sausage rendering (IDENTICAL across all 5 bun variants) -------------

def _draw_sausage_segment(surf, rect, *, gap_side, seed):
    """Vertical sausage centered horizontally inside the pillar rect.

    Sausage protrudes SAUSAGE_PROTRUDE px past the gap edge. Mustard
    zigzag runs the full length, ketchup dots accent every other zigzag
    point. (Matches round-1 V2 condiment treatment.)
    """
    x, y, w, h = rect
    sx = x + (w - SAUSAGE_W) // 2
    if gap_side == 'bottom':         # top pillar
        sy = y
        sh = h + SAUSAGE_PROTRUDE
    else:                             # bot pillar
        sy = max(0, y - SAUSAGE_PROTRUDE)
        sh = h + (y - sy)
    s = pygame.Rect(sx, sy, SAUSAGE_W, sh)
    radius_s = SAUSAGE_W // 2 + 2
    pygame.draw.rect(surf, OUTLINE, s.inflate(4, 4), border_radius=radius_s)
    pygame.draw.rect(surf, SAUSAGE_LO, s.inflate(2, 2), border_radius=radius_s)
    pygame.draw.rect(surf, SAUSAGE_MID, s, border_radius=radius_s)
    # Lit-side highlight on the sausage
    pygame.draw.rect(surf, SAUSAGE_HI,
                     pygame.Rect(s.x + 4, s.y + 4, max(2, SAUSAGE_W // 3),
                                 max(2, sh - 14)),
                     border_radius=SAUSAGE_W // 4)
    # Mustard zigzag
    n = max(6, sh // 12)
    amp = max(3, SAUSAGE_W // 4)
    cx = s.centerx
    pts_m = [(cx + (amp if i % 2 == 0 else -amp),
              s.y + 8 + i * (sh - 16) // max(1, n - 1))
             for i in range(n)]
    pygame.draw.lines(surf, _shade(MUSTARD, -40), False, pts_m, 5)
    pygame.draw.lines(surf, MUSTARD, False, pts_m, 3)
    pygame.draw.lines(surf, MUSTARD_HI, False, pts_m, 1)
    # Ketchup dotted accents (every other zigzag point)
    for i in range(0, n, 2):
        bx, by = pts_m[i]
        _aa_filled_circle(surf, int(bx), int(by), 2, KETCHUP)
        _aa_filled_circle(surf, int(bx), int(by), 1, KETCHUP_HI)


def _draw_chicken_wing_accents(surf, top_rect, bot_rect):
    """The fried-chicken-wing accents at the gap edges.
    IDENTICAL to round-1 V2."""
    draw_chicken_wing(surf, bot_rect.centerx + 6, bot_rect.top + 14,
                      46, 30, flip=False)
    draw_chicken_wing(surf, top_rect.centerx - 8, top_rect.bottom - 14,
                      36, 24, flip=True)


# ============================================================================
# 5 bun treatments
# ============================================================================

def _bun_anchor(rect):
    """Returns (left_outer_x, left_inner_x, right_inner_x, right_outer_x).

    Buns extrude EXTRUDE px outside the pillar rect on each side.
    """
    x = rect.x
    w = rect.width
    return (x - EXTRUDE,           # left bun outer edge
            x - EXTRUDE + BUN_W,   # left bun inner edge
            x + w + EXTRUDE - BUN_W,
            x + w + EXTRUDE)


# ----- v2_bun1 Classic Side -------------------------------------------------

def _draw_bun_classic(surf, rect, *, hi=BUN_HI, mid=BUN_MID, lo=BUN_LO):
    x_lo, x_li, x_ri, x_ro = _bun_anchor(rect)
    radius = BUN_W // 2 + 2
    for outer_x in (x_lo, x_ri):
        bun = pygame.Rect(outer_x, rect.y, BUN_W, rect.height)
        pygame.draw.rect(surf, OUTLINE, bun.inflate(4, 4), border_radius=radius)
        pygame.draw.rect(surf, lo, bun.inflate(2, 2), border_radius=radius)
        pygame.draw.rect(surf, mid, bun, border_radius=radius)
        # Lit-side highlight: longer strip on the outer side
        is_left = (outer_x == x_lo)
        hl_x = bun.x + 3 if is_left else bun.right - 6
        hl = pygame.Rect(hl_x, bun.y + 6, 3, bun.height - 12)
        pygame.draw.rect(surf, hi, hl, border_radius=2)


def draw_v2_bun1(surf, top_rect, bot_rect, palette, seed):
    """V2-bun1 Classic Side - smooth golden side strips. No gap-edge
    decorations: just bun + sausage + mustard zigzag + ketchup dots."""
    _draw_bun_classic(surf, top_rect)
    _draw_bun_classic(surf, bot_rect)
    _draw_sausage_segment(surf, top_rect, gap_side='bottom', seed=seed)
    _draw_sausage_segment(surf, bot_rect, gap_side='top', seed=seed)


# ----- v2_bun2 Soft Cradle --------------------------------------------------

def _draw_bun_cradle(surf, rect):
    """Side strips with curved INNER edges that 'hug' the sausage at top
    + bottom (concave inner curve at each end of the strip)."""
    x_lo, x_li, x_ri, x_ro = _bun_anchor(rect)
    y_top = rect.y
    y_bot = rect.bottom
    cradle = max(8, rect.height // 12)   # how far the curve reaches in
    # Build polygon for each side (left + right)
    for is_left in (True, False):
        if is_left:
            outer = x_lo
            inner = x_li
        else:
            outer = x_ro
            inner = x_ri
        # Polygon traced clockwise from top-outer corner.
        # Inner edge curves inward (toward sausage) at top and bottom.
        # Use ~7 segments for the curved inner edge.
        pts = [(outer, y_top + 4), (outer, y_bot - 4)]
        # Bottom curve back to inner edge
        n_curve = 5
        for i in range(n_curve + 1):
            u = i / n_curve
            curve_x = inner - cradle * math.sin(u * math.pi / 2) * (1 if is_left else -1)
            curve_y = y_bot - 4 - cradle * (1 - math.cos(u * math.pi / 2))
            pts.append((curve_x, curve_y))
        # Inner edge straight up
        pts.append((inner, y_bot - 4 - cradle))
        pts.append((inner, y_top + 4 + cradle))
        # Top curve back to outer edge
        for i in range(n_curve + 1):
            u = i / n_curve
            curve_x = inner - cradle * math.cos(u * math.pi / 2) * (1 if is_left else -1)
            curve_y = y_top + 4 + cradle - cradle * math.sin(u * math.pi / 2)
            pts.append((curve_x, curve_y))
        pygame.draw.polygon(surf, OUTLINE, [(p[0], p[1] + 1) for p in pts])
        pygame.draw.polygon(surf, BUN_LO, [(p[0], p[1]) for p in pts])
        # Inner highlight - shrink polygon slightly toward outer edge
        pygame.draw.polygon(surf, BUN_MID,
                            [((p[0] - outer) * 0.96 + outer,
                              (p[1] - rect.centery) * 0.98 + rect.centery)
                             for p in pts])
        # Lit highlight strip along the outer side
        hl_x = outer + 3 if is_left else outer - 6
        pygame.draw.rect(surf, BUN_HI,
                         pygame.Rect(hl_x, y_top + 12, 3, rect.height - 24),
                         border_radius=2)


def draw_v2_bun2(surf, top_rect, bot_rect, palette, seed):
    """V2-bun2 Soft Cradle - curved-inner side strips."""
    _draw_bun_cradle(surf, top_rect)
    _draw_bun_cradle(surf, bot_rect)
    _draw_sausage_segment(surf, top_rect, gap_side='bottom', seed=seed)
    _draw_sausage_segment(surf, bot_rect, gap_side='top', seed=seed)
    _draw_chicken_wing_accents(surf, top_rect, bot_rect)


# ----- v2_bun3 Brioche Knots ------------------------------------------------

def _draw_bun_brioche(surf, rect, *, seed=0):
    """Each side is a stack of plump knot segments with sesame seeds."""
    x_lo, x_li, x_ri, x_ro = _bun_anchor(rect)
    knot_h = 32
    n = max(2, rect.height // knot_h)
    rng = random.Random(seed)
    for is_left in (True, False):
        outer_x = x_lo if is_left else x_ri
        for i in range(n):
            ky = rect.y + i * knot_h
            kh = min(knot_h - 4, rect.bottom - ky - 2)
            if kh < 12:
                continue
            knot = pygame.Rect(outer_x - 1, ky, BUN_W + 2, kh)
            radius = min(knot.width, knot.height) // 2 + 2
            pygame.draw.rect(surf, OUTLINE, knot.inflate(3, 3),
                             border_radius=radius)
            pygame.draw.rect(surf, BRIOCHE_LO, knot.inflate(1, 1),
                             border_radius=radius)
            pygame.draw.rect(surf, BRIOCHE_MID, knot, border_radius=radius)
            # Glossy highlight on top half
            hl = pygame.Rect(knot.x + 3, knot.y + 3,
                             knot.width - 6, max(2, knot.height // 3))
            pygame.draw.rect(surf, BRIOCHE_HI, hl, border_radius=hl.height)
            # Sesame seeds (3 per knot, scattered on outer surface)
            for _ in range(3):
                sx = rng.randint(knot.x + 3, knot.right - 3)
                sy = rng.randint(knot.y + 4, knot.bottom - 4)
                pygame.draw.ellipse(surf, OUTLINE,
                                    pygame.Rect(sx - 2, sy - 1, 4, 3))
                pygame.draw.ellipse(surf, (250, 234, 196),
                                    pygame.Rect(sx - 1, sy - 1, 3, 2))


def draw_v2_bun3(surf, top_rect, bot_rect, palette, seed):
    """V2-bun3 Brioche Knots - plump segmented side knots + sesame."""
    _draw_bun_brioche(surf, top_rect, seed=seed)
    _draw_bun_brioche(surf, bot_rect, seed=seed + 1)
    _draw_sausage_segment(surf, top_rect, gap_side='bottom', seed=seed)
    _draw_sausage_segment(surf, bot_rect, gap_side='top', seed=seed)
    _draw_chicken_wing_accents(surf, top_rect, bot_rect)


# ----- v2_bun4 Pretzel Salt -------------------------------------------------

def _draw_bun_pretzel(surf, rect, *, seed=0):
    """Same shape as classic but pretzel-dark mahogany glaze + salt grains."""
    _draw_bun_classic(surf, rect, hi=PRETZEL_HI, mid=PRETZEL_MID, lo=PRETZEL_LO)
    # Salt grains scattered on each side
    rng = random.Random(seed * 7 + 23)
    x_lo, x_li, x_ri, x_ro = _bun_anchor(rect)
    for outer_x in (x_lo, x_ri):
        for _ in range(max(8, rect.height // 14)):
            sx = rng.randint(outer_x + 2, outer_x + BUN_W - 2)
            sy = rng.randint(rect.y + 4, rect.bottom - 4)
            _aa_filled_circle(surf, sx + 1, sy + 1, 2, OUTLINE)
            _aa_filled_circle(surf, sx, sy, 2, SALT_COLOR)
            _aa_filled_circle(surf, sx - 1, sy - 1, 1, (255, 255, 255))
    # Hint of subtle "twist" on the surface (faint diagonal scoring lines)
    for outer_x in (x_lo, x_ri):
        for j in range(0, rect.height, 22):
            y0 = rect.y + j
            pygame.draw.line(surf, _shade(PRETZEL_LO, -10),
                             (outer_x + 2, y0),
                             (outer_x + BUN_W - 2, y0 + 6), 1)


def draw_v2_bun4(surf, top_rect, bot_rect, palette, seed):
    """V2-bun4 Pretzel Salt - dark pretzel glaze + salt crystals."""
    _draw_bun_pretzel(surf, top_rect, seed=seed)
    _draw_bun_pretzel(surf, bot_rect, seed=seed + 1)
    _draw_sausage_segment(surf, top_rect, gap_side='bottom', seed=seed)
    _draw_sausage_segment(surf, bot_rect, gap_side='top', seed=seed)
    _draw_chicken_wing_accents(surf, top_rect, bot_rect)


# ----- v2_bun5 Sub Roll Cut -------------------------------------------------

def _draw_bun_subroll(surf, rect):
    """Cross-section reveal: outer crust + cream-white crumb facing the
    sausage. Looks like a sub-roll sliced lengthwise to cradle the sausage."""
    x_lo, x_li, x_ri, x_ro = _bun_anchor(rect)
    crust_w = 9    # outer crust thickness
    crumb_w = BUN_W - crust_w  # interior crumb visible to the inside
    radius_outer = crust_w + 2
    for is_left in (True, False):
        if is_left:
            outer_x = x_lo
            crust_rect = pygame.Rect(outer_x, rect.y, crust_w, rect.height)
            crumb_rect = pygame.Rect(outer_x + crust_w, rect.y, crumb_w,
                                     rect.height)
        else:
            outer_x = x_ri
            crust_rect = pygame.Rect(outer_x + crumb_w, rect.y, crust_w,
                                     rect.height)
            crumb_rect = pygame.Rect(outer_x, rect.y, crumb_w, rect.height)
        # Whole bun outline
        whole = pygame.Rect(outer_x, rect.y, BUN_W, rect.height)
        pygame.draw.rect(surf, OUTLINE, whole.inflate(4, 4),
                         border_radius=radius_outer)
        # Crumb (interior, cream-white)
        pygame.draw.rect(surf, CRUMB_LO, crumb_rect.inflate(2, 2),
                         border_radius=4)
        pygame.draw.rect(surf, CRUMB_MID, crumb_rect, border_radius=4)
        # Crumb texture: tiny ivory dots
        rng = random.Random(rect.y * 7 + crumb_rect.x)
        for _ in range(crumb_rect.height // 6):
            cx = rng.randint(crumb_rect.left + 2, crumb_rect.right - 2)
            cy = rng.randint(crumb_rect.top + 2, crumb_rect.bottom - 2)
            _aa_filled_circle(surf, cx, cy, 1, CRUMB_HI)
        # Crust (outer, golden brown)
        pygame.draw.rect(surf, BUN_LO, crust_rect.inflate(2, 2),
                         border_radius=radius_outer)
        pygame.draw.rect(surf, BUN_MID, crust_rect, border_radius=radius_outer)
        # Crust highlight (lit edge)
        hl_x = crust_rect.x + 2 if is_left else crust_rect.right - 4
        hl = pygame.Rect(hl_x, crust_rect.y + 6, 3, crust_rect.height - 12)
        pygame.draw.rect(surf, BUN_HI, hl, border_radius=2)
        # Clear divide line between crust and crumb
        if is_left:
            div_x = crust_rect.right
        else:
            div_x = crust_rect.left
        pygame.draw.line(surf, _shade(BUN_LO, -20),
                         (div_x, crust_rect.y + 4),
                         (div_x, crust_rect.bottom - 4), 1)


def draw_v2_bun5(surf, top_rect, bot_rect, palette, seed):
    """V2-bun5 Sub Roll Cut - cross-section bun with crust + crumb visible."""
    _draw_bun_subroll(surf, top_rect)
    _draw_bun_subroll(surf, bot_rect)
    _draw_sausage_segment(surf, top_rect, gap_side='bottom', seed=seed)
    _draw_sausage_segment(surf, bot_rect, gap_side='top', seed=seed)
    _draw_chicken_wing_accents(surf, top_rect, bot_rect)


# ----- Variant registry -----------------------------------------------------

V2_BUN_VARIANTS = {
    'v2_bun1': ("V2-bun1 Classic Side",  draw_v2_bun1),
    'v2_bun2': ("V2-bun2 Soft Cradle",   draw_v2_bun2),
    'v2_bun3': ("V2-bun3 Brioche Knots", draw_v2_bun3),
    'v2_bun4': ("V2-bun4 Pretzel Salt",  draw_v2_bun4),
    'v2_bun5': ("V2-bun5 Sub Roll Cut",  draw_v2_bun5),
}


@contextlib.contextmanager
def install_variant(key: str):
    """Monkey-patch draw_pillar_pair so every pillar in the rendered scene
    uses the chosen V2 bun treatment. Patches BOTH game.pillar_variants
    AND game.entities (the import binding in entities.py is what
    Pipe.draw actually calls)."""
    if key not in V2_BUN_VARIANTS:
        raise ValueError(f"unknown V2 bun variant {key!r}; valid: "
                         f"{sorted(V2_BUN_VARIANTS)}")
    _, fn = V2_BUN_VARIANTS[key]
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
