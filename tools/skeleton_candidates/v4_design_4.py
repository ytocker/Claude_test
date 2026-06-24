"""v4 SKELETON · design_4 — IVORY ANATOMICAL (scratch exploration only).

A warm natural-history museum plate: the original Pip macaw rendered as an aged
real skeleton in bone/ivory/cream, not stark radiograph white. The full anatomy
is fixed in `_v4_xray_base`; this file only changes the bone *material* and adds
naturalist refinement so it reads like a vintage plate of real bone.

The ivory material is sold three ways on TOP of the base skeleton:
  • a warm tan SHADOW side re-struck slightly below/right of every long bone so
    each shaft reads round and lit from the upper-left (the museum-plate cue);
  • a cream HIGHLIGHT skim on the upper-left of those same bones;
  • extra fine DETAIL — countable rib ticks, vertebra knobs with sockets, and a
    LONGER curved overstroke on the dominant beak bone so the hooked mandible is
    unmistakably the hero.

Flesh is kept dark but leans warm-brown (aged-specimen tone) so warm ivory bone
reads against it as old bone, not bright bone on cold flesh.

NOT registered in store_skins.BUILDERS. Production is untouched.
"""
import pygame

from tools.skeleton_candidates import _v4_xray_base as XB
from game.store_skins import COMPOSITE_W, COMPOSITE_H


# ── ivory bone material (lit upper-left) ─────────────────────────────────────
# Warm cream main body, a deeper warm-tan for the shadow side / keyline so the
# bone keeps a soft edge on the pale day sky WITHOUT the cold blue keyline the
# radiograph designs use, and a near-white-cream highlight skim.
BONE_IVORY = (238, 228, 200)        # warm aged ivory — the main material
BONE_CREAM = (252, 246, 226)        # cream highlight on the lit (upper-left) side
BONE_TAN   = (170, 150, 110)        # warm tan shadow side / soft keyline
BONE_DEEP  = (128, 108, 76)         # deepest crevice tone (sockets, mandible gap)
BEAK_IVORY = (244, 234, 206)        # beak a hair brighter — naturally the hero

# Style handed to the shared painter. `sh` is the WARM tan (not a cold keyline)
# so the base anatomy already carries warm roundness; `hi` is cream.
STYLE = dict(
    bone=BONE_IVORY, hi=BONE_CREAM, sh=BONE_TAN,
    w_long=3, w_rib=2, w_fine=2, beak=BEAK_IVORY,
)

# Warm-dark flesh: charcoal pushed FURTHER toward brown (aged specimen) so the
# ivory reads as old bone in a genuinely warm body, and the silhouette survives
# day and night. R2: more red/ochre lean so the "aged body" story actually shows.
_FLESH = XB._pal(
    tail=[(34, 27, 22), (41, 33, 26), (48, 39, 31), (55, 45, 36)],
    tail_line=(22, 17, 13),
    body_shadow=(22, 17, 13),
    body_main=(41, 33, 26),
    body_chest=(50, 40, 31),
    body_belly=(61, 49, 38),
    sheen=None,
    wing_main=(36, 29, 23),
    wing_dark=(23, 18, 14),
    wing_tip=(47, 38, 30),
    wing_secondary=None,
    wing_highlight=None,
    head_shadow=(26, 20, 16),
    head_main=(47, 38, 30),
    head_cheek=(58, 47, 37),
    head_crown=(65, 52, 41),
    lens_frame=(0, 0, 0), lens_body=(0, 0, 0),
    lens_tint=None, lens_glint=None,
    beak_main=(38, 30, 24),
    beak_dark=(24, 19, 14),
    beak_gloss=(51, 41, 32),
    foot=(34, 27, 22),
)


def _flesh_base(angle_deg):
    return XB._build_parrot_with_palette(angle_deg, _FLESH, draw_lenses=False)


# ── naturalist roundness: warm shadow + cream highlight along the long bones ──
# Lit from upper-left: shadow side offsets down-right, highlight skims up-left,
# and a warm-DARK hairline rims the up-left contour so the bone holds its edge on
# bright day sky WITHOUT resorting to a cold blue keyline (R2 #4). Drawn THIN
# over the already-painted ivory bones so they bulge into rounded tubes.
def _round_bone(surf, p0, p1):
    sh = (p0[0] + 1, p0[1] + 1), (p1[0] + 1, p1[1] + 1)   # warm shadow, down-right
    hi = (p0[0] - 1, p0[1] - 1), (p1[0] - 1, p1[1] - 1)   # cream highlight, up-left
    pygame.draw.line(surf, BONE_DEEP, *hi, 1)             # lit-side dark rim first
    pygame.draw.line(surf, BONE_TAN, *sh, 1)
    pygame.draw.line(surf, BONE_CREAM, *hi, 1)            # highlight sits over the rim


def _round_polybone(surf, pts):
    for i in range(len(pts) - 1):
        _round_bone(surf, pts[i], pts[i + 1])


def _naturalist_pass(surf):
    """Add the museum-plate roundness + countable detail on top of the base
    anatomy. Nothing here MOVES a bone — it only shades and detail-ticks the
    fixed skeleton so it reads as real specimen bone, and stays calm at 40px."""
    DY = XB.DY

    # Spine: round the shaft, then a single ivory knob with one cream tick on
    # ALTERNATING vertebrae only — enough to read "segmented" without beading
    # into a blur at scale (R2 #5).
    _round_polybone(surf, XB._SPINE)
    for i, v in enumerate(XB._SPINE):
        XB.knob(surf, BONE_IVORY, v, 2)
        if i % 2 == 0:
            XB.knob(surf, BONE_CREAM, (v[0] - 1, v[1] - 1), 1)

    # Keel/sternum: darkened a half-step toward tan so the bright ivory ribs read
    # as a CAGE over a recessed sternum instead of fusing into one bright bar
    # (R2 #3). Re-struck in tan over the base ivory keel.
    XB.polybone(surf, BONE_TAN, XB._KEEL, 2)

    # Ribs: drop to 3 (more air between them) and round each with a single fine
    # cross-tick, so "countable" survives the downscale (R2 #3).
    for r0 in (XB._RIB_ROOTS[0], XB._RIB_ROOTS[1], XB._RIB_ROOTS[3]):
        pts = XB._rib_curve(r0)
        _round_polybone(surf, pts)
        mid = pts[len(pts) // 2]
        pygame.draw.line(surf, BONE_CREAM,
                         (mid[0] - 1, mid[1] - 1), (mid[0] + 1, mid[1] - 1), 1)

    # Pelvis + leg long-bones rounded; knees get a small bright epiphysis knob.
    pelvis = (22, 33 + DY)
    XB.knob(surf, BONE_CREAM, (pelvis[0] - 1, pelvis[1] - 1), 1)
    for hipx, foot, splay in ((25, (26, 49 + DY), -3), (30, (36, 49 + DY), 3)):
        knee = (hipx + splay, 45 + DY)
        _round_bone(surf, pelvis, knee)
        _round_bone(surf, knee, foot)
        XB.knob(surf, BONE_TAN, (knee[0] + 1, knee[1] + 1), 1)
        XB.knob(surf, BONE_CREAM, knee, 1)

    # Skull: a CALM anchor for the beak. One clean cream cranium curve on the lit
    # dome, one warm-dark hollow orbit with a single cream rim — nothing more, so
    # the head doesn't compete with the hero beak at 40px (R2 #2).
    pygame.draw.line(surf, BONE_DEEP, (XB.HX - 8, XB.HY - 3),
                     (XB.HX - 3, XB.HY - 8), 1)            # lit-side dark rim
    pygame.draw.arc(surf, BONE_CREAM, pygame.Rect(XB.HX - 9, XB.HY - 9, 16, 14),
                    0.5, 2.4, 2)                           # one clean cranium curve
    pygame.draw.circle(surf, BONE_DEEP, (XB.HX + 3, XB.HY - 1), 3)  # hollow orbit
    pygame.draw.circle(surf, BONE_CREAM, (XB.HX + 3, XB.HY - 1), 3, 1)  # single rim


def _beak_hero(surf):
    """The dominant beak bone — the HERO. R2: pushed ~20-25% further forward, on
    a slightly fatter shaft, kept the brightest fill on the whole bird, so it is
    the longest/brightest/cleanest single bone even at 40px. The skull is now a
    calm anchor it projects off of."""
    # Upper mandible hinges at the skull (~53,36) and projects to a downturned
    # raptor hook further forward than R1 (tip ~72 vs ~69) on a fatter body.
    upper = [(53, 35), (62, 38), (69, 42), (72, 47), (71, 52), (65, 52),
             (61, 47), (57, 44), (54, 41), (53, 38)]
    lower = [(55, 45), (66, 47), (65, 52), (55, 49)]

    pygame.draw.polygon(surf, BONE_TAN, [(p[0], p[1] + 1) for p in upper])  # warm underside
    pygame.draw.polygon(surf, BEAK_IVORY, upper)
    pygame.draw.polygon(surf, BONE_TAN, [(p[0], p[1] + 1) for p in lower])
    pygame.draw.polygon(surf, BEAK_IVORY, lower)

    # Culmen (top ridge) cream gloss — a long bright overstroke running the full
    # forward length so the hook is unmistakably the brightest cleanest bone;
    # warm-dark lit-side rim under it holds the edge on bright sky.
    pygame.draw.lines(surf, BONE_DEEP, False,
                      [(53, 37), (61, 38), (68, 42), (71, 47)], 1)
    pygame.draw.lines(surf, BONE_CREAM, False,
                      [(53, 36), (61, 37), (68, 41), (71, 46)], 1)
    pygame.draw.line(surf, BONE_DEEP, (55, 45), (66, 47), 1)   # mandible gap
    pygame.draw.circle(surf, BONE_DEEP, (58, 41), 1)           # nostril fossa


def _paint(surf, angle):
    """Paint the warm ivory skeleton: lay the full fixed anatomy, then add the
    naturalist roundness/detail and the longer hero beak bone on top."""
    XB.paint_skeleton(surf, angle, style=STYLE)
    _naturalist_pass(surf)
    _beak_hero(surf)


def _make():
    from game import store_skins
    return store_skins._make_skin(_paint, base_fn=_flesh_base)


build = _make()
