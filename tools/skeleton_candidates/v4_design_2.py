"""v4 SKELETON · design_2 — BOLD CARTOON BONE (scratch exploration only).

The "instantly legible" sibling: thick chunky PURE WHITE bones with crisp
dark keylines, in the Day-of-the-Dead / Saturday-morning-cartoon register.
No glow, no gradient — clean graphic white-on-dark that pops on the bright
day sky AND the night navy.

The black "back" mass is now a HOODED OPEN-FRONT CLOAK (shared cloak base):
a cowl wraps the back of the skull, the drape flares to a tattered hem, and
the open chest V keeps the ribcage + spine + dominant beak as the hero. To
stay in the BOLD register the cloth is flat near-black with ONE crisp,
clearly-lighter cool-steel keyline on the hood rim + hem — a bold clean
shape, not fussy folds — that survives the 40px downscale.

R2 is all about NEGATIVE SPACE: at 40px the white bones flood-filled into a
blob, so this pass forces dark flesh BETWEEN bones — thin fill bones (ribs,
keel) so 4 distinct rib arcs survive, a hard dark gap at the skull/beak
hinge so the beak reads as its own projecting wedge, an enlarged pure-dark
eye-socket so the thumbnail keeps one skull eye-hole, and a single clean
forward beak wedge with the hook below the jawline (no sub-pixel ticks).

NOT registered in store_skins.BUILDERS. Production is untouched.
"""
import pygame

from tools.skeleton_candidates import _v4_xray_base as XB


# Structural bones stay fat (spine/legs/skull = w_long); FILL bones (ribs,
# keel) are thinned so dark flesh survives between them at thumbnail size.
STYLE = dict(
    bone=(250, 252, 255), hi=(255, 255, 255), sh=(12, 13, 22),
    w_long=5, w_rib=2, w_fine=4, beak=(255, 255, 255),
)

# Pure-dark flesh tone used to CARVE negative space back between bones.
_VOID = (8, 9, 16)

# Darker flesh than the base default — sinks the body so chunky white bone
# carries the entire read at thumbnail size.
_FLESH = XB._pal(
    tail=[(14, 15, 26), (18, 20, 32), (22, 24, 38), (26, 28, 44)],
    tail_line=(8, 9, 16),
    body_shadow=(8, 9, 16),
    body_main=(18, 20, 32),
    body_chest=(22, 24, 38),
    body_belly=(28, 31, 48),
    sheen=None,
    wing_main=(15, 17, 28),
    wing_dark=(9, 10, 18),
    wing_tip=(21, 23, 36),
    wing_secondary=None,
    wing_highlight=None,
    head_shadow=(11, 12, 20),
    head_main=(21, 23, 36),
    head_cheek=(27, 30, 46),
    head_crown=(30, 33, 50),
    lens_frame=(0, 0, 0), lens_body=(0, 0, 0),
    lens_tint=None, lens_glint=None,
    beak_main=(17, 18, 30),
    beak_dark=(9, 10, 18),
    beak_gloss=(24, 26, 40),
    foot=(14, 15, 26),
)


# BOLD keyline for the cloak: one crisp, clearly-lighter cool-steel edge so the
# hood + tattered hem read as a single bold clean shape against the near-black
# cloth — same graphic register as the thick high-contrast bones (no fussy
# folds, just a hard rim that survives the 40px downscale on day AND night).
_CLOAK_EDGE = (176, 184, 214)


def _flesh_base(angle_deg):
    # Shared cloak shape on YOUR near-black cloth, then re-strike the hood-rim
    # and tattered-hem keylines one step thicker so the cloak reads as a single
    # bold graphic shape — matching the chunky high-contrast bones, not the
    # base's hairline default rim.
    surf = XB.cloak_base(angle_deg, _FLESH, edge=_CLOAK_EDGE)
    pygame.draw.lines(surf, _CLOAK_EDGE, False, XB._HOOD_RIM, 2)
    pygame.draw.lines(surf, _CLOAK_EDGE, False, XB._HEM_EDGE, 2)
    return surf


def _rib_gaps(surf):
    """Carve pure-dark slots BETWEEN the white rib arcs so 4 distinct ribs
    survive instead of flooding into one chest blob — ribs are the #1
    'this is a skeleton' cue. Slots sit between adjacent _RIB_ROOTS, angled
    to follow the ribcage curve down toward the keel."""
    for x0 in (35, 30, 25, 21):          # between the four rib arcs
        pygame.draw.line(surf, _VOID, (x0, XB.DY + 27), (x0 - 5, XB.DY + 40), 2)


def _eye_socket(surf):
    """Re-stamp an enlarged pure-dark eye-hole so even the 40px thumbnail
    keeps one skull eye — the dot that sells 'skull'. Skull centre (HX,HY)."""
    cx, cy = XB.HX + 2, XB.HY - 1
    pygame.draw.circle(surf, STYLE["bone"], (cx, cy), 6, 2)   # bone rim
    pygame.draw.circle(surf, _VOID, (cx, cy), 5)              # hollow socket


def _beak_post(surf):
    """The DOMINANT beak bone: one big clean forward-projecting triangular
    wedge, hook tip clearly below the jawline, anchored to the skull at a
    single bone knuckle and framed top + bottom by pure-dark flesh so it
    detaches cleanly. No commissure/culmen ticks — they read as a gaping
    mouth at 1x; the dark frame does the separation."""
    bone = STYLE["bone"]
    key = STYLE["sh"]
    # Dark frame ABOVE and BELOW the beak root so its edges touch void, not
    # the white skull — this is what makes it read as its own bone at 40px.
    pygame.draw.line(surf, _VOID, (55, 35), (66, 39), 2)     # over the culmen
    pygame.draw.line(surf, _VOID, (55, 47), (62, 50), 2)     # under the jaw
    # Big triangular wedge: broad root at the skull hinge → long taper to a
    # hook that drops below the lower jaw. The biggest, most-salient bone.
    wedge = [(56, 38), (72, 44), (70, 50), (63, 49), (59, 46), (56, 44)]
    pygame.draw.polygon(surf, key, [(x, y + 1) for x, y in wedge])  # drop keyline
    pygame.draw.polygon(surf, bone, wedge)
    pygame.draw.polygon(surf, key, wedge, 2)                 # crisp dark outline
    knob = XB.knob
    knob(surf, bone, (56, 41), 2)                            # skull/beak knuckle
    pygame.draw.circle(surf, _VOID, (60, 42), 1)            # nostril


def _paint(surf, angle):
    XB.paint_skeleton(surf, angle, style=STYLE)
    # Carve the negative space the base's white fill destroyed.
    _rib_gaps(surf)
    _eye_socket(surf)
    _beak_post(surf)


def _make():
    from game import store_skins
    return store_skins._make_skin(_paint, base_fn=_flesh_base)


build = _make()
