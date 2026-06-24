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
    # Lifted ~1px (top y43→y42) with an unbroken _KEY outline so the cranium
    # reads as a distinct lobe (Pip's head) rather than melting into the chest.
    pygame.draw.polygon(surf, _BONE,    [(48, 43), (60, 42), (58, 47), (46, 47)])
    pygame.draw.polygon(surf, _KEY,     [(48, 43), (60, 42), (58, 47), (46, 47)], 1)
    pygame.draw.line(surf, _BONE_SH, (49, 45), (58, 44), 1)   # mandible line

    # ── ONE clean hollow eye-socket — a round HOLE at the original eye spot
    # (50,40), with a darker inner-lower rim so it reads as a socket with a back
    # wall (depth), not a hole punched clean through the skull.
    pygame.draw.circle(surf, _BONE, (50, 40), 5)             # bone orbit ring
    pygame.draw.circle(surf, _KEY,  (50, 40), 4)
    pygame.draw.circle(surf, _VOID, (50, 40), 3)             # the empty socket
    pygame.draw.arc(surf, _BONE_SH, (47, 38, 6, 6),          # inner-lower back wall
                    math.radians(200), math.radians(340), 1)
    pygame.draw.circle(surf, _BONE, (49, 38), 1)             # life glint
    # Nostril dot on the bone beak so the original bill reads skeletal.
    pygame.draw.circle(surf, _VOID, (55, 44), 1)

    # ── Spine — THREE clear vertebra beads only (skull base / mid / tail root);
    # the intermediate beads read as a fat white worm at 40px, so they're cut.
    spine = [(41, 47), (29, 53), (18, 56)]
    pygame.draw.lines(surf, _KEY, False, spine, 3)
    for vx, vy in spine:
        _bead(surf, vx, vy, 2)

    # ── Sternum — a short bone bar that sits clearly ABOVE the spine line, with
    # dark flesh between it and the spine so the two never smear into one bar.
    pygame.draw.line(surf, _KEY,  (37, 49), (31, 57), 4)
    pygame.draw.line(surf, _BONE, (37, 49), (31, 57), 2)

    # ── Ribcage — TWO widened rib rungs only. A _VOID wash under each so they
    # read as bone-on-black and the dark gap of flesh between them survives at
    # 40px (three 4px-apart rungs fused into a mesh).
    for (rx, ry) in ((37, 50), (34, 56)):
        rect = (rx - 15, ry - 7, 16, 15)
        pygame.draw.arc(surf, _VOID, rect, math.radians(10), math.radians(170), 4)
        pygame.draw.arc(surf, _KEY,  rect, math.radians(15), math.radians(165), 3)
        pygame.draw.arc(surf, _BONE, rect, math.radians(20), math.radians(160), 2)

    # ── Tail — a single white tail-feather bone over the original tail fan
    # (x2–23 / y44–62). Fattened to a 3px stroke + r3 tip knob, keylined, because
    # the tail is a primary Pip silhouette anchor that otherwise vanishes at 40px.
    pygame.draw.line(surf, _KEY,  (19, 51), (5, 54), 5)
    pygame.draw.line(surf, _BONE, (19, 51), (6, 54), 3)
    pygame.draw.circle(surf, _KEY,  (6, 54), 4)
    pygame.draw.circle(surf, _BONE, (6, 54), 3)              # feather tip knob

    # ── Legs — ONE clean knee knob per leg, sat on the ankle so each leg reads
    # as a single bone line rather than a beaded ladder.
    for kx in (28, 34):
        pygame.draw.circle(surf, _KEY,  (kx, 66), 3)
        pygame.draw.circle(surf, _BONE, (kx, 66), 2)


build = store_skins._make_skin(_paint, base_fn=_bone_parrot_wing)
