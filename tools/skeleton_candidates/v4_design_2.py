"""v4 SKELETON · design_2 — BOLD CARTOON BONE (scratch exploration only).

The "instantly legible" sibling: thick chunky PURE WHITE bones with crisp
dark keylines, in the Day-of-the-Dead / Saturday-morning-cartoon register.
No glow, no gradient — clean graphic white-on-dark that pops on the bright
day sky AND the night navy. Anatomy is fixed in `_v4_xray_base`; this file
only fattens the stroke widths and post-thickens the dominant beak bone so
it reads as the hero at 40px.

NOT registered in store_skins.BUILDERS. Production is untouched.
"""
import pygame

from tools.skeleton_candidates import _v4_xray_base as XB


# Fat shafts + a hard near-black keyline so every bone separates on day sky.
# Pure-white beak fill makes the dominant beak bone the brightest mass.
STYLE = dict(
    bone=(250, 252, 255), hi=(255, 255, 255), sh=(12, 13, 22),
    w_long=5, w_rib=4, w_fine=4, beak=(255, 255, 255),
)

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


def _flesh_base(angle_deg):
    return XB._build_parrot_with_palette(angle_deg, _FLESH, draw_lenses=False)


def _beak_post(surf):
    """Fatten the dominant beak bone into a big chunky TRIANGULAR hero bone.

    Drawn AFTER paint_skeleton so it sits on top: a bold double-keylined
    white wedge with a clean dark commissure line and hollow nostril — the
    single most salient mass on the bird at any size."""
    bone = STYLE["bone"]
    key = STYLE["sh"]
    # Triangular upper mandible, wider/heavier than the base hooked outline,
    # ending in a downward raptor hook. Forward-projecting like the original.
    upper = [(53, 36), (68, 41), (69, 47), (63, 48), (57, 45), (53, 42)]
    lower = [(54, 45), (64, 47), (63, 50), (54, 48)]
    # Two-step keyline (fat dark, then white) for the bold cartoon separation.
    pygame.draw.polygon(surf, key, [(x - 2, y + 2) for x, y in upper])
    pygame.draw.polygon(surf, key, [(x - 2, y + 2) for x, y in lower])
    pygame.draw.polygon(surf, bone, upper)
    pygame.draw.polygon(surf, bone, lower)
    pygame.draw.polygon(surf, key, upper, 2)
    pygame.draw.polygon(surf, key, lower, 2)
    pygame.draw.line(surf, key, (54, 45), (64, 46), 2)        # commissure
    pygame.draw.circle(surf, (8, 9, 16), (58, 41), 2)         # hollow nostril
    pygame.draw.line(surf, (255, 255, 255), (54, 38), (66, 43), 1)  # culmen tick


def _paint(surf, angle):
    XB.paint_skeleton(surf, angle, style=STYLE)
    _beak_post(surf)


def _make():
    from game import store_skins
    return store_skins._make_skin(_paint, base_fn=_flesh_base)


build = _make()
