"""Five elegant Olympic-LAUREL outer-RING concepts for the achievement medallion.

The victor's leaf-crown, drawn slim. Every concept is a NARROW ring/branch with
SHORT overlapping leaf-sprigs layered along it — the open-top circlet of two
sprigs rising from a base to nearly meet at the top, small refined leaves,
generous negative space, a calm dominant center emblem. This is the ELEGANT
weight (matches ``tools/ring_elegant`` — hairline struck band + big calm navy
face); it is the OPPOSITE of the bulky big-leaf gear-tooth wreath in
``tools/wreath_polish`` / ``tools/badge_rings`` (fame_wreath), which reads as a
thick decorated bezel rather than a graceful leaf crown.

Same approved Fame -> Shame TRADE-OFF as the ring family — Fame is the pristine
GOLD Olympic laurel; Shame is the SAME wreath gently GONE BAD: leaves browned
and wilting, a couple shed (a real gap), a slight droop, the base ribbon
loosened. Restrained, never gory, still readable at 44px. NO diagonal crack.

The five are distinct WITHIN the laurel theme (per ``distinct-design-variants``)
— different leaf shape, density and circlet topology, not one base recolored:

  1) CLASSIC  bay-laurel twin sprigs of small almond leaves + a base ribbon bow.
  2) OLIVE    kotinos: narrower lanceolate leaves in paired nodes + tiny olives.
  3) CIRCLET  a single slender near-continuous ring of tiny leaves (top opening).
  4) MINIMAL  sparse, well-spaced leaves, maximum breathing space (the calmest).
  5) LAYERED  fuller twin sprigs with a subtle double leaf row — lush yet thin.

The CENTER emblem is never redesigned — every composer stamps the live engraved
glyph through ``ai._stamp_glyph`` (``pillar_100`` in Fame, ``goose_egg`` in
Shame). Each Shame wilts in the way that suits its own build (olive drops its
drupes; the circlet browns an arc; etc.).

WRITE-ONLY scratch under ``tools/`` — never bundled; imports ``game`` read-only.
Composers render at the REAL badge geometry (``R = 0.46 * px``); the slim laurel
sits well inside the badge square with generous margin.
"""
from __future__ import annotations

import math
import pygame

import game.achievement_icons as ai
from game.draw import lerp_color

_LIGHT = ai._LIGHT  # share the family's one upper-left light source

# ── shared geometry ───────────────────────────────────────────────────────────
# A big calm navy field with a hairline struck rim; the laurel floats on the
# field as a NARROW leaf circlet (a moat of navy inside and out), never a chunky
# decorated bezel. Leaf tips are held within ~0.44*R of the branch so nothing
# clips the badge square under the real ``R = 0.46*px`` geometry.
_FACE_F   = 0.92    # face radius / R  (near-full -> generous negative space)
_BAND_IN  = 0.88    # metal rim's inner radius / R (visible hairline rim)
_BRANCH_R = 0.74    # the laurel branch's centre radius / R (floats on the field)
_GLYPH_F  = 0.60    # glyph radius / R (the prominent, calm focal point)

# The circlet is open at the TOP so it reads as a crown the way a victor wears it
# (two sprigs rising to nearly meet). Angles are screen space (y-down), 90deg is
# the bottom; the base ribbon sits at the bottom, the opening at the top.
_TOP_GAP  = math.radians(34)    # half-angle of the open top between the sprigs
_BASE_A   = math.radians(90)    # bottom of the ring (where the ribbon ties)


# ── shared palettes ──────────────────────────────────────────────────────────
# Fame gold — the family's warm struck gold; the only fully saturated accent.
_G_HI   = (255, 232, 160)
_G_MID  = (232, 186,  74)
_G_LO   = (150, 102,  22)
_G_EDGE = ( 70,  44,   8)
_G_SPEC = (255, 250, 222)
_FACE_TOP = (44, 32, 92)
_FACE_BOT = (16, 10, 44)
_FACE_REC = (10,  6, 28)
_GLY    = (255, 236, 184)
_GLY_SH = ( 32,  18,  44)

# Fame leaf gold — lit vs shadowed gold foliage, tinted per-leaf by the light.
_LEAF_HI = (250, 216, 112)
_LEAF_LO = (156, 108,  28)
_LEAF_MR = (120,  82,  18)      # engraved midrib
_OLIVE   = (214, 176,  70)      # a small gold olive drupe
_OLIVE_HI = (255, 240, 190)

# Shame — the SAME wreath gently wilted. The band cools to a muted pewter; the
# leaves go autumn tan/brown (lifted so a thin browned leaf still reads at 44px),
# never a flat grey blob. Restrained warmth is the only "colour", mirroring gold.
_P_HI   = (176, 180, 192)
_P_MID  = (118, 122, 138)
_P_LO   = ( 60,  64,  80)
_P_EDGE = ( 26,  26,  34)
_P_TARN = (120, 108,  86)
_P_TARN2 = ( 84,  76,  62)
_P_FACE_TOP = (52, 54, 74)
_P_FACE_BOT = (28, 30, 48)
_P_FACE_REC = (14, 14, 26)
_P_GLY  = (196, 200, 214)
_P_GLY_SH = (16, 16, 26)

_WILT_HI = (198, 158,  92)      # dry tan leaf, lit (lifted so it reads on navy)
_WILT_LO = (122,  86,  46)      # rotted brown leaf, shadow
_WILT_MR = ( 78,  54,  28)      # dry midrib
_WILT_DEAD = (156, 130,  86)    # grey-brown fully-dead shed leaf
_OLIVE_D = (120, 102,  66)      # shrivelled dull olive


# ── shared low-level helpers ─────────────────────────────────────────────────

def _center(surf, glyph_key, cx, cy, R, gly, gly_sh, sheen=None):
    ai._stamp_glyph(surf, glyph_key, cx, cy, int(R * _GLYPH_F), gly, gly_sh, sheen)


def _slim_band(surf, cx, cy, R, hi, mid, lo, spec=None, edge=None,
               light=_LIGHT, spec_span=0.5):
    """A SLIM struck-metal frame from ``R`` in to ``_BAND_IN*R`` under the one
    upper-left light — the same strike geometry as the live family but a fraction
    of its width, so the perimeter reads as a refined bezel, not a chunky bevel."""
    inner = int(R * _BAND_IN)
    for i in range(R, inner, -1):
        t = (R - i) / max(1, R - inner)
        pygame.draw.circle(surf, lerp_color(hi, lo, t * 0.6 + 0.2), (cx, cy), i)
    steps = 56
    band = (R - inner)
    for seg in range(steps):
        a0 = seg / steps * math.tau
        a1 = (seg + 1) / steps * math.tau
        d = (math.cos(a0 - light) + 1) * 0.5
        col = lerp_color(lo, hi, d ** 1.4)
        rect = pygame.Rect(cx - R + band // 3, cy - R + band // 3,
                           (R - band // 3) * 2, (R - band // 3) * 2)
        pygame.draw.arc(surf, col, rect, -a1, -a0, max(2, band - band // 3))
    if spec is not None:
        mid_r = (R + inner) // 2
        hot = pygame.Rect(cx - mid_r, cy - mid_r, mid_r * 2, mid_r * 2)
        pygame.draw.arc(surf, spec, hot, light - spec_span, light + spec_span,
                        max(2, band // 2))
    pygame.draw.circle(surf, mid, (cx, cy), R, max(1, R // 30))
    if edge is not None:
        pygame.draw.circle(surf, edge, (cx, cy), R, max(1, R // 44))


def _finish_center(surf, cx, cy, R, hi, lo, ftop, fbot, frec, gk, gly, gly_sh,
                   sheen=None):
    """Draw the shared large calm center: a thin step keyline, the big recessed
    face, and the live engraved emblem — identical construction across concepts
    so only the laurel carries the trade-off."""
    fr = int(R * _FACE_F)
    ai._draw_step(surf, cx, cy, fr + max(1, R // 22), hi, lo)
    ai._draw_face(surf, cx, cy, fr, ftop, fbot, frec)
    _center(surf, gk, cx, cy, R, gly, gly_sh, sheen)


def _tarnish_creep(surf, cx, cy, R, seed, n=12):
    """A few faint oxide flecks on the pewter band — enough to read 'tarnished',
    never a corroded mess."""
    s = seed
    for i in range(n):
        s = (s * 1103515245 + 12345) & 0x7fffffff
        a = (s / 0x7fffffff) * math.tau
        s = (s * 1103515245 + 12345) & 0x7fffffff
        rad = R * (_BAND_IN + (1.0 - _BAND_IN) * (s / 0x7fffffff))
        px = cx + int(math.cos(a) * rad)
        py = cy + int(math.sin(a) * rad)
        col = _P_TARN if i % 2 else _P_TARN2
        pygame.draw.circle(surf, col, (px, py), max(1, R // 60))


def _leaf(surf, bx, by, ang, ln, wd, fill, edge, R, mr=None):
    """One small almond laurel leaf: a pointed lens swept along ``ang`` from a
    base at (bx, by), with an engraved midrib so it reads as foliage, not a
    spike. Small + refined by design (short ``ln``)."""
    ca, sa = math.cos(ang), math.sin(ang)
    nx, ny = -sa, ca
    pts = []
    for f, w in ((0.0, 0.0), (0.34, wd), (0.66, wd * 0.78), (1.0, 0.0)):
        pts.append((bx + ca * ln * f + nx * w, by + sa * ln * f + ny * w))
    for f, w in ((1.0, 0.0), (0.66, wd * 0.78), (0.34, wd), (0.0, 0.0)):
        pts.append((bx + ca * ln * f - nx * w, by + sa * ln * f - ny * w))
    pygame.draw.polygon(surf, fill, [(int(x), int(y)) for x, y in pts])
    pygame.draw.line(surf, mr if mr is not None else edge, (int(bx), int(by)),
                     (int(bx + ca * ln), int(by + sa * ln)), max(1, R // 64))


def _leaf_col(a, hi, lo):
    """Tint a leaf by its angle to the one upper-left light, like the rim."""
    d = (math.cos(a - _LIGHT) + 1) * 0.5
    return lerp_color(lo, hi, d ** 1.2)


def _ribbon(surf, cx, cy, R, hi, lo, loosened=False):
    """The small ribbon tie where the two sprigs meet at the base of the crown —
    the wreath's classic finishing knot. ``loosened`` lets the tails sag apart so
    the Shame wreath reads as gently coming undone (never torn to shreds)."""
    rc = R * _BRANCH_R
    bx = cx + int(math.cos(_BASE_A) * rc)
    by = cy + int(math.sin(_BASE_A) * rc)
    knot = max(2, R // 22)
    pygame.draw.circle(surf, lerp_color(hi, lo, 0.25), (bx, by), knot)
    pygame.draw.circle(surf, lo, (bx, by), knot, max(1, R // 60))
    # two short tails draping down-out from the knot
    for sgn in (-1, 1):
        spread = 0.42 if loosened else 0.26
        drop = 0.16 if loosened else 0.13
        tip = (bx + int(sgn * R * spread), by + int(R * drop))
        mid = (bx + int(sgn * R * (spread * 0.5)),
               by + int(R * (drop * 0.55 + (0.05 if loosened else 0.0))))
        pygame.draw.lines(surf, lerp_color(hi, lo, 0.35), False,
                          [(bx, by), mid, tip], max(2, R // 40))


# ── per-sprig placement ──────────────────────────────────────────────────────
# All concepts lay leaves along the two flank arcs from the base up toward the
# top gap. ``_sprig_angles`` yields the branch positions for one flank; helpers
# then place leaves tangentially (swept up-and-out along the branch).

def i_even(f, span=6):
    """True on alternate nodes along a sprig (``f`` is the 0..1 node fraction) —
    used to space olive drupes at every other node."""
    return int(round(f * span)) % 2 == 0


def _sprig_angles(n, sgn):
    """``n`` evenly spaced branch angles on one flank, from just off the base
    ribbon up to just short of the top gap. ``sgn`` +1 = RIGHT flank (sweeping
    up through 0deg), -1 = LEFT flank (up through 180deg) — so the two sprigs
    frame the emblem symmetrically and meet, open, at the top."""
    if sgn > 0:
        a_base = _BASE_A - math.radians(6)            # bottom, just right
        a_top = -math.pi / 2 + _TOP_GAP               # just right of straight up
    else:
        a_base = _BASE_A + math.radians(6)            # bottom, just left
        a_top = 3 * math.pi / 2 - _TOP_GAP            # just left of straight up
    for i in range(n):
        f = i / (n - 1)
        yield f, a_base + (a_top - a_base) * f


def _place_leaf(surf, cx, cy, rc, a, sgn, ln, wd, hi, lo, R, mr,
                out_k=0.5, droop=0.0):
    """Place one leaf on the branch at angle ``a`` on flank ``sgn``. Each leaf
    lies back along the branch (tangent swept toward the TOP) with a slight
    radial lift ``out_k`` — the classic overlapping laurel sprig, leaves fanning
    up each flank. ``droop`` bends the tip limply groundward for the wilt."""
    bx = cx + math.cos(a) * rc
    by = cy + math.sin(a) * rc
    # tangent pointing up the branch toward the top + a small outward radial lift
    tx, ty = sgn * math.sin(a), sgn * (-math.cos(a))
    ox, oy = math.cos(a), math.sin(a)
    dx = tx + out_k * ox
    dy = ty + out_k * oy + droop * 0.9                # droop pulls the tip down
    dx -= sgn * droop * 0.25
    ang = math.atan2(dy, dx)
    _leaf(surf, bx, by, ang, ln, wd, _leaf_col(a, hi, lo), lo, R, mr)


def _fallen_leaf(surf, cx, cy, R, fx, fy, fl, fa, col, edge):
    """A single shed leaf resting just inside the lower field — small enough to
    stay a clean silhouette at 44px, close enough not to clip the badge square."""
    _leaf(surf, cx + R * fx, cy + R * fy, fa, R * fl, R * fl * 0.30, col, edge,
          R, _WILT_MR)


# ═══════════════════════════════════════════════════════════════════════════
# 1) CLASSIC — bay-laurel twin sprigs of small almond leaves + a base ribbon bow.
# ═══════════════════════════════════════════════════════════════════════════

def _classic_ring(surf, cx, cy, R, hi, lo, mr, wilt=False):
    rc = R * _BRANCH_R
    n = 10
    for sgn in (-1, 1):
        for f, a in _sprig_angles(n, sgn):
            droop = 0.9 * f if wilt else 0.0
            # a wilted right flank sheds its two lowest leaves (a real gap)
            if wilt and sgn > 0 and f < 0.24:
                continue
            ln = R * (0.30 - 0.06 * f)
            wd = R * (0.105 - 0.020 * f)
            _place_leaf(surf, cx, cy, rc, a, sgn, ln, wd, hi, lo, R, mr,
                        out_k=0.5, droop=droop)


def fame_classic(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _G_HI, _G_MID, _G_LO, spec=_G_SPEC, edge=_G_EDGE)
    _finish_center(surf, cx, cy, R, _G_HI, _G_LO, _FACE_TOP, _FACE_BOT, _FACE_REC,
                   glyph_key, _GLY, _GLY_SH, ai._GLYPH_SHEEN)
    _classic_ring(surf, cx, cy, R, _LEAF_HI, _LEAF_LO, _LEAF_MR)
    _ribbon(surf, cx, cy, R, _G_HI, _G_LO)


def shame_classic(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _P_HI, _P_MID, _P_LO, spec=None, edge=_P_EDGE)
    _tarnish_creep(surf, cx, cy, R, seed=13)
    _finish_center(surf, cx, cy, R, _P_HI, _P_LO, _P_FACE_TOP, _P_FACE_BOT,
                   _P_FACE_REC, glyph_key, _P_GLY, _P_GLY_SH)
    _classic_ring(surf, cx, cy, R, _WILT_HI, _WILT_LO, _WILT_MR, wilt=True)
    _fallen_leaf(surf, cx, cy, R, 0.30, 0.72, 0.17, 2.5, _WILT_DEAD, _WILT_LO)
    _ribbon(surf, cx, cy, R, _P_MID, _P_LO, loosened=True)


# ═══════════════════════════════════════════════════════════════════════════
# 2) OLIVE — kotinos: narrower lanceolate leaves in paired nodes + tiny olives.
# ═══════════════════════════════════════════════════════════════════════════

def _olive_ring(surf, cx, cy, R, hi, lo, mr, olive_col, olive_hi, wilt=False):
    rc = R * _BRANCH_R
    n = 7                                   # paired nodes along each sprig
    for sgn in (-1, 1):
        for f, a in _sprig_angles(n, sgn):
            droop = 0.9 * f if wilt else 0.0
            if wilt and sgn < 0 and f < 0.28:      # left flank sheds low leaves
                continue
            bx = cx + math.cos(a) * rc
            by = cy + math.sin(a) * rc
            # opposite paired leaves at each node — slim lanceolate, both sides,
            # one leaning up-toward-top, one down-toward-base
            ln = R * (0.255 - 0.045 * f)
            wd = R * (0.058 - 0.010 * f)            # narrower than bay laurel
            for ok in (0.75, -0.35):
                _place_leaf(surf, cx, cy, rc, a, sgn, ln, wd, hi, lo, R, mr,
                            out_k=ok, droop=droop)
            # a small olive drupe nestled inboard of each node (the kotinos cue);
            # a wilted sprig has shrivelled/dropped its upper olives
            if 0.12 < f < 0.92 and i_even(f) and not (wilt and f > 0.4):
                orad = max(2, int(R * 0.055))
                ox = bx - math.cos(a) * R * 0.075
                oy = by - math.sin(a) * R * 0.075
                pygame.draw.circle(surf, lo, (int(ox), int(oy)), orad + 1)
                pygame.draw.circle(surf, olive_col, (int(ox), int(oy)), orad)
                pygame.draw.circle(surf, olive_hi,
                                   (int(ox - orad * 0.32), int(oy - orad * 0.32)),
                                   max(1, orad // 2))


def fame_olive(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _G_HI, _G_MID, _G_LO, spec=_G_SPEC, edge=_G_EDGE)
    _finish_center(surf, cx, cy, R, _G_HI, _G_LO, _FACE_TOP, _FACE_BOT, _FACE_REC,
                   glyph_key, _GLY, _GLY_SH, ai._GLYPH_SHEEN)
    _olive_ring(surf, cx, cy, R, _LEAF_HI, _LEAF_LO, _LEAF_MR, _OLIVE, _OLIVE_HI)
    _ribbon(surf, cx, cy, R, _G_HI, _G_LO)


def shame_olive(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _P_HI, _P_MID, _P_LO, spec=None, edge=_P_EDGE)
    _tarnish_creep(surf, cx, cy, R, seed=29)
    _finish_center(surf, cx, cy, R, _P_HI, _P_LO, _P_FACE_TOP, _P_FACE_BOT,
                   _P_FACE_REC, glyph_key, _P_GLY, _P_GLY_SH)
    _olive_ring(surf, cx, cy, R, _WILT_HI, _WILT_LO, _WILT_MR, _OLIVE_D,
                _WILT_DEAD, wilt=True)
    # a shed leaf + a dropped shrivelled olive resting low in the field
    _fallen_leaf(surf, cx, cy, R, -0.30, 0.74, 0.15, 0.7, _WILT_DEAD, _WILT_LO)
    pygame.draw.circle(surf, _OLIVE_D,
                       (cx + int(R * 0.10), cy + int(R * 0.80)), max(2, int(R * 0.03)))
    _ribbon(surf, cx, cy, R, _P_MID, _P_LO, loosened=True)


# ═══════════════════════════════════════════════════════════════════════════
# 3) CIRCLET — a single slender near-continuous ring of tiny leaves (top gap).
#    Kept spaced + midribbed so it never collapses to gear-teeth at 44px.
# ═══════════════════════════════════════════════════════════════════════════

def _circlet_ring(surf, cx, cy, R, hi, lo, mr, wilt=False):
    rc = R * _BRANCH_R
    n = 20                                  # small leaves nearly all the way round
    # sweep the whole ring except a small opening at the very top
    a0 = -math.pi / 2 + _TOP_GAP
    a1 = -math.pi / 2 + math.tau - _TOP_GAP
    # a browned ARC on the lower-right when wilted, with a real shed-leaf gap in it
    brown_lo = math.radians(18)
    brown_hi = math.radians(96)
    for i in range(n):
        f = i / (n - 1)
        a = a0 + (a1 - a0) * f
        an = a % math.tau
        in_brown = wilt and (brown_lo <= an <= brown_hi)
        if wilt and math.radians(46) <= an <= math.radians(70):
            continue                        # two adjacent leaves shed (a gap)
        bx = cx + math.cos(a) * rc
        by = cy + math.sin(a) * rc
        # every leaf lies tangential + lifted outward, all sweeping one way round
        tx, ty = math.sin(a), -math.cos(a)              # CCW tangent
        ox, oy = math.cos(a), math.sin(a)
        droop = 0.8 if in_brown else 0.0
        ang = math.atan2(ty + 0.45 * oy + droop * 0.9, tx + 0.45 * ox)
        ln = R * 0.165
        wd = R * 0.052
        lh, ll = (_WILT_HI, _WILT_LO) if in_brown else (hi, lo)
        _leaf(surf, bx, by, ang, ln, wd, _leaf_col(a, lh, ll), ll, R, mr)


def fame_circlet(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _G_HI, _G_MID, _G_LO, spec=_G_SPEC, edge=_G_EDGE)
    _finish_center(surf, cx, cy, R, _G_HI, _G_LO, _FACE_TOP, _FACE_BOT, _FACE_REC,
                   glyph_key, _GLY, _GLY_SH, ai._GLYPH_SHEEN)
    _circlet_ring(surf, cx, cy, R, _LEAF_HI, _LEAF_LO, _LEAF_MR)


def shame_circlet(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _P_HI, _P_MID, _P_LO, spec=None, edge=_P_EDGE)
    _tarnish_creep(surf, cx, cy, R, seed=47)
    _finish_center(surf, cx, cy, R, _P_HI, _P_LO, _P_FACE_TOP, _P_FACE_BOT,
                   _P_FACE_REC, glyph_key, _P_GLY, _P_GLY_SH)
    _circlet_ring(surf, cx, cy, R, _LEAF_HI, _LEAF_LO, _LEAF_MR, wilt=True)
    _fallen_leaf(surf, cx, cy, R, 0.36, 0.66, 0.14, 2.4, _WILT_DEAD, _WILT_LO)


# ═══════════════════════════════════════════════════════════════════════════
# 4) MINIMAL — sparse, well-spaced leaves, maximum breathing space (calmest).
# ═══════════════════════════════════════════════════════════════════════════

def _minimal_ring(surf, cx, cy, R, hi, lo, mr, wilt=False):
    rc = R * _BRANCH_R
    n = 5                                   # only a few leaves per sprig
    for sgn in (-1, 1):
        for f, a in _sprig_angles(n, sgn):
            droop = 0.9 * f if wilt else 0.0
            if wilt and sgn > 0 and f < 0.30:      # right flank drops its low leaf
                continue
            ln = R * (0.30 - 0.05 * f)             # larger, well-spaced
            wd = R * (0.11 - 0.014 * f)
            _place_leaf(surf, cx, cy, rc, a, sgn, ln, wd, hi, lo, R, mr,
                        out_k=0.5, droop=droop)


def fame_minimal(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _G_HI, _G_MID, _G_LO, spec=_G_SPEC, edge=_G_EDGE)
    _finish_center(surf, cx, cy, R, _G_HI, _G_LO, _FACE_TOP, _FACE_BOT, _FACE_REC,
                   glyph_key, _GLY, _GLY_SH, ai._GLYPH_SHEEN)
    _minimal_ring(surf, cx, cy, R, _LEAF_HI, _LEAF_LO, _LEAF_MR)
    _ribbon(surf, cx, cy, R, _G_HI, _G_LO)


def shame_minimal(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _P_HI, _P_MID, _P_LO, spec=None, edge=_P_EDGE)
    _tarnish_creep(surf, cx, cy, R, seed=61)
    _finish_center(surf, cx, cy, R, _P_HI, _P_LO, _P_FACE_TOP, _P_FACE_BOT,
                   _P_FACE_REC, glyph_key, _P_GLY, _P_GLY_SH)
    _minimal_ring(surf, cx, cy, R, _WILT_HI, _WILT_LO, _WILT_MR, wilt=True)
    _fallen_leaf(surf, cx, cy, R, 0.34, 0.70, 0.18, 2.5, _WILT_DEAD, _WILT_LO)
    _ribbon(surf, cx, cy, R, _P_MID, _P_LO, loosened=True)


# ═══════════════════════════════════════════════════════════════════════════
# 5) LAYERED — fuller twin sprigs with a subtle double leaf row — lush yet thin.
# ═══════════════════════════════════════════════════════════════════════════

def _layered_ring(surf, cx, cy, R, hi, lo, mr, wilt=False):
    rc = R * _BRANCH_R
    n = 11
    for sgn in (-1, 1):
        for f, a in _sprig_angles(n, sgn):
            droop = 0.85 * f if wilt else 0.0
            # outer row — the shed row when wilted (upper flank comes apart)
            shed = wilt and sgn > 0 and 0.30 < f < 0.66
            if not shed:
                ln = R * (0.26 - 0.05 * f)
                wd = R * (0.085 - 0.014 * f)
                _place_leaf(surf, cx, cy, rc + R * 0.03, a, sgn, ln, wd, hi, lo,
                            R, mr, out_k=0.62, droop=droop)
            # inner row — a shorter offset leaf tucked toward the field
            ln2 = R * (0.185 - 0.03 * f)
            wd2 = R * (0.062 - 0.009 * f)
            _place_leaf(surf, cx, cy, rc - R * 0.05, a, sgn, ln2, wd2, hi, lo,
                        R, mr, out_k=0.34, droop=droop * 0.6)


def fame_layered(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _G_HI, _G_MID, _G_LO, spec=_G_SPEC, edge=_G_EDGE)
    _finish_center(surf, cx, cy, R, _G_HI, _G_LO, _FACE_TOP, _FACE_BOT, _FACE_REC,
                   glyph_key, _GLY, _GLY_SH, ai._GLYPH_SHEEN)
    _layered_ring(surf, cx, cy, R, _LEAF_HI, _LEAF_LO, _LEAF_MR)
    _ribbon(surf, cx, cy, R, _G_HI, _G_LO)


def shame_layered(surf, cx, cy, R, glyph_key):
    _slim_band(surf, cx, cy, R, _P_HI, _P_MID, _P_LO, spec=None, edge=_P_EDGE)
    _tarnish_creep(surf, cx, cy, R, seed=83)
    _finish_center(surf, cx, cy, R, _P_HI, _P_LO, _P_FACE_TOP, _P_FACE_BOT,
                   _P_FACE_REC, glyph_key, _P_GLY, _P_GLY_SH)
    _layered_ring(surf, cx, cy, R, _WILT_HI, _WILT_LO, _WILT_MR, wilt=True)
    _fallen_leaf(surf, cx, cy, R, 0.32, 0.72, 0.15, 2.4, _WILT_DEAD, _WILT_LO)
    _ribbon(surf, cx, cy, R, _P_MID, _P_LO, loosened=True)


# Each concept pairs a Fame composer with its gently-wilted Shame twin.
CONCEPTS = [
    ("classic", fame_classic, shame_classic),
    ("olive", fame_olive, shame_olive),
    ("circlet", fame_circlet, shame_circlet),
    ("minimal", fame_minimal, shame_minimal),
    ("layered", fame_layered, shame_layered),
]
