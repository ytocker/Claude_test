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

# Warm-dark flesh: charcoal pushed toward brown (aged specimen) so the ivory
# reads as old bone in a warm body, and the silhouette survives day and night.
_FLESH = XB._pal(
    tail=[(28, 24, 22), (34, 29, 26), (40, 35, 31), (46, 40, 36)],
    tail_line=(18, 15, 13),
    body_shadow=(18, 15, 13),
    body_main=(34, 29, 26),
    body_chest=(42, 36, 32),
    body_belly=(52, 45, 39),
    sheen=None,
    wing_main=(30, 25, 23),
    wing_dark=(19, 16, 14),
    wing_tip=(40, 34, 30),
    wing_secondary=None,
    wing_highlight=None,
    head_shadow=(22, 18, 16),
    head_main=(40, 34, 30),
    head_cheek=(50, 43, 38),
    head_crown=(56, 48, 42),
    lens_frame=(0, 0, 0), lens_body=(0, 0, 0),
    lens_tint=None, lens_glint=None,
    beak_main=(32, 27, 24),
    beak_dark=(20, 16, 14),
    beak_gloss=(44, 37, 33),
    foot=(28, 24, 22),
)


def _flesh_base(angle_deg):
    return XB._build_parrot_with_palette(angle_deg, _FLESH, draw_lenses=False)


# ── naturalist roundness: warm shadow + cream highlight along the long bones ──
# Lit from upper-left, so the shadow side sits offset down-right of the shaft and
# the highlight skims up-left. Drawn THIN over the already-painted ivory bones so
# they bulge into rounded tubes the way a real bone plate is shaded.
def _round_bone(surf, p0, p1):
    sh = (p0[0] + 1, p0[1] + 1), (p1[0] + 1, p1[1] + 1)   # shadow offset down-right
    hi = (p0[0] - 1, p0[1] - 1), (p1[0] - 1, p1[1] - 1)   # highlight up-left
    pygame.draw.line(surf, BONE_TAN, *sh, 1)
    pygame.draw.line(surf, BONE_CREAM, *hi, 1)


def _round_polybone(surf, pts):
    for i in range(len(pts) - 1):
        _round_bone(surf, pts[i], pts[i + 1])


def _naturalist_pass(surf):
    """Add the museum-plate roundness + countable detail on top of the base
    anatomy. Nothing here MOVES a bone — it only shades and detail-ticks the
    fixed skeleton so it reads as real specimen bone."""
    DY = XB.DY

    # Spine + keel get rounded; each vertebra a cream-lit knob over a warm socket.
    _round_polybone(surf, XB._SPINE)
    _round_polybone(surf, XB._KEEL)
    for v in XB._SPINE:
        XB.knob(surf, BONE_TAN, (v[0] + 1, v[1] + 1), 2)      # socket shadow
        XB.knob(surf, BONE_IVORY, v, 2)
        XB.knob(surf, BONE_CREAM, (v[0] - 1, v[1] - 1), 1)    # lit crown of knob

    # Ribs: round each, then add a fine cross-tick at mid-rib so they read as
    # COUNTABLE individual ribs (the natural-history-plate giveaway).
    for r0 in XB._RIB_ROOTS:
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

    # Skull: warm-shade the lower-right arc, cream-skim the cranium dome, and
    # deepen the eye-socket rim into a real hollow orbit.
    pygame.draw.arc(surf, BONE_TAN, pygame.Rect(XB.HX - 11, XB.HY - 11, 23, 23),
                    -1.9, 0.6, 1)
    pygame.draw.circle(surf, BONE_CREAM, (XB.HX - 2, XB.HY - 5), 4, 1)
    pygame.draw.circle(surf, BONE_DEEP, (XB.HX + 3, XB.HY - 1), 3)
    pygame.draw.circle(surf, BONE_CREAM, (XB.HX + 1, XB.HY - 3), 4, 1)  # orbit rim hi


def _beak_hero(surf):
    """The dominant beak bone, re-stated LONGER and more curved than the base so
    the hooked upper mandible is unmistakably the signature bone. Warm-shaded
    underside + cream culmen sell it as one solid, aged, round ivory beak."""
    # A longer, more deeply hooked upper mandible than the base footprint, still
    # hinged at the skull (~54,38) and projecting forward to a downturned tip.
    upper = [(54, 36), (62, 39), (68, 43), (69, 49), (64, 50),
             (60, 46), (56, 43), (54, 41)]
    lower = [(55, 45), (64, 47), (63, 51), (55, 48)]

    pygame.draw.polygon(surf, BONE_TAN, [(p[0], p[1] + 1) for p in upper])  # warm underside
    pygame.draw.polygon(surf, BEAK_IVORY, upper)
    pygame.draw.polygon(surf, BONE_TAN, [(p[0], p[1] + 1) for p in lower])
    pygame.draw.polygon(surf, BEAK_IVORY, lower)

    # Culmen (top ridge) cream gloss — the longer overstroke that makes the hook
    # read as the hero; mandible gap deepened; hollow nostril.
    pygame.draw.lines(surf, BONE_CREAM, False,
                      [(54, 38), (60, 39), (66, 43), (68, 47)], 1)
    pygame.draw.line(surf, BONE_DEEP, (55, 45), (64, 47), 1)   # mandible gap
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
