"""v3_design_1 · CLEAN — a faithful skeleton of the ORIGINAL Pip macaw, iconic.

Rooted in the v2 BONEWHITE look (bright white bone on a near-black flesh body)
but reshaped to the REAL parrot: the silhouette, the ORIGINAL beak, and the
ORIGINAL tail location all come from `_bone_parrot` (the recoloured
`_build_parrot_with_palette`). This paint adds only the BOLD, iconic skeletal
reads so it stays crisp at 40px: a white cranium dome over the dark head, ONE
clean hollow eye-socket, a clear vertebral spine bead column, a FEW strong rib
rungs off a sternum, a bone leg knee/foot, and a single tail-feather bone over
the original tail fan. The wing gets a BONE leading-edge by retinting the base
palette's `wing_highlight` to bone, so the flapping wing carries a bone line
that rotates with it (no static painted wing-bone to drift).

Paint is in COMPOSITE space (original sprite coords + PARROT_DY=20): head centre
(47,41), crown top y31, body centre (32,52), original eye-socket spot (50,40),
original beak ~(55,41)(61,44)(58,48)(52,46), original tail fan ≈ x2–23 / y44–62,
original feet (26,69)/(36,69). Scratch only — never registered in BUILDERS.
"""
import math
import pygame

from game import store_skins
from game.parrot import _aaellipse
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from tools.skeleton_candidates._v3_bone_base import P_BONE

_BONE    = (255, 255, 255)         # brightest element on day AND night
_BONE_SH = (214, 218, 228)         # cool bone shade for inner form
_KEY     = (58, 61, 71)            # cool keyline so white never washes out
_VOID    = (10, 11, 16)            # socket / nostril hollow


# A per-design body palette: identical dark flesh to the shared base, but with a
# bone-white wing leading-edge. The base draws that highlight line on the wing
# polygon, so it rotates with the 4-frame flap — a clean wing-bone read that can
# never drift out of the silhouette like a statically painted one would.
_P = dict(P_BONE)
_P["wing_highlight"] = _BONE


def _bone_parrot_wing(angle_deg):
    return _build_parrot_with_palette(angle_deg, _P, draw_lenses=False)


def _bead(surf, x, y, r):
    """A keylined white vertebra bead — reads as bone on any sky."""
    pygame.draw.circle(surf, _KEY,  (x, y), r + 1)
    pygame.draw.circle(surf, _BONE, (x, y), r)


def _paint(surf, wing_angle_deg):
    # ── Skull — a bright white cranium DOME over the dark head (centre 47,41),
    # set high and forward so it connects naturally toward the bone beak.
    _aaellipse(surf, _KEY,     (47, 39), 11, 10)
    _aaellipse(surf, _BONE,    (47, 39), 10, 9)
    _aaellipse(surf, _BONE_SH, (45, 35),  6, 4)            # crown form light
    # Jaw/cheek shelf carrying the skull down to meet the original bone beak.
    pygame.draw.polygon(surf, _BONE,    [(48, 44), (60, 43), (58, 47), (46, 47)])
    pygame.draw.polygon(surf, _KEY,     [(48, 44), (60, 43), (58, 47), (46, 47)], 1)
    pygame.draw.line(surf, _BONE_SH, (49, 45), (58, 44), 1)   # mandible line

    # ── ONE clean hollow eye-socket — a round/teardrop HOLE at the original eye
    # spot (50,40). Keyline ring → void fill → a single life-glint on the rim.
    pygame.draw.circle(surf, _BONE, (50, 40), 5)             # bone orbit ring
    pygame.draw.circle(surf, _KEY,  (50, 40), 4)
    pygame.draw.circle(surf, _VOID, (50, 40), 3)             # the empty socket
    pygame.draw.line(surf, _VOID, (50, 43), (52, 44), 1)     # teardrop duct
    pygame.draw.circle(surf, _BONE, (49, 38), 1)             # life glint
    # Nostril dot on the bone beak so the original bill reads skeletal.
    pygame.draw.circle(surf, _VOID, (55, 44), 1)

    # ── Spine — one clear vertebra-bead column, skull base → tail root.
    spine = [(41, 47), (35, 50), (29, 53), (23, 55), (18, 56)]
    pygame.draw.lines(surf, _KEY, False, spine, 3)
    for vx, vy in spine:
        _bead(surf, vx, vy, 2)

    # ── Ribcage — a clean sternum + THREE bold, well-spaced rib rungs on the
    # chest. Each rib is a keylined white arc so it pops; spaced so it never
    # turns into a busy mesh at 40px.
    pygame.draw.line(surf, _KEY,  (38, 48), (29, 61), 4)
    pygame.draw.line(surf, _BONE, (38, 48), (29, 61), 2)     # sternum bar
    for i, (rx, ry) in enumerate(((37, 50), (35, 54), (33, 58))):
        rect = (rx - 13, ry - 6, 14, 13)
        pygame.draw.arc(surf, _KEY,  rect, math.radians(15), math.radians(165), 3)
        pygame.draw.arc(surf, _BONE, rect, math.radians(20), math.radians(160), 2)

    # ── Tail — a single white tail-feather bone over the original tail fan
    # (x2–23 / y44–62), keylined so it reads on bright sky.
    pygame.draw.line(surf, _KEY,  (19, 51), (5, 54), 4)
    pygame.draw.line(surf, _BONE, (19, 51), (6, 54), 2)
    pygame.draw.circle(surf, _BONE, (6, 54), 2)              # feather tip knob

    # ── Legs — knob knees on the original bone leg lines (feet 26,69 / 36,69).
    for kx in (28, 34):
        pygame.draw.circle(surf, _KEY,  (kx, 65), 3)
        pygame.draw.circle(surf, _BONE, (kx, 65), 2)


build = store_skins._make_skin(_paint, base_fn=_bone_parrot_wing)
