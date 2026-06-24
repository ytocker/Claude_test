"""v3_design_1 · CLEAN — a faithful skeleton of the ORIGINAL Pip macaw, iconic.

Rooted in the v2 BONEWHITE look (bright white bone on a near-black flesh body)
but reshaped to the REAL parrot: the silhouette, the ORIGINAL beak, and the
ORIGINAL tail location all come from `_bone_parrot` (the recoloured
`_build_parrot_with_palette`). This paint adds only the BOLD, iconic skeletal
reads so it stays crisp at 40px: a white cranium + one hollow eye-socket, a few
strong rib rungs, a clear vertebral spine, simple wing finger-bones + leg bones,
and a single white tail-feather bone over the original tail fan.

Paint is in COMPOSITE space (original sprite coords + PARROT_DY=20): head centre
(47,41), body centre (32,52), original beak ~(55,41)(61,44)(58,48)(52,46),
original tail fan ≈ x2–23 / y44–62. Scratch only — never registered in BUILDERS.
"""
import math
import pygame

from game import store_skins
from game.parrot import _aaellipse
from tools.skeleton_candidates._v3_bone_base import _bone_parrot

_BONE    = (255, 255, 255)
_BONE_SH = (228, 231, 238)
_KEY     = (58, 61, 71)            # cool keyline so white reads on the day sky
_VOID    = (13, 14, 19)            # socket / gape hollow


def _paint(surf, wing_angle_deg):
    # ── Skull — a bright white cranium over the dark head (head centre 47,41).
    _aaellipse(surf, _KEY,     (47, 40), 11, 10)
    _aaellipse(surf, _BONE,    (47, 40), 10, 9)
    _aaellipse(surf, _BONE_SH, (47, 44), 8, 4)            # jaw/cheek shelf
    # One hollow eye-socket at the original eye spot (sprite 50,20 → 50,40).
    pygame.draw.circle(surf, _KEY,  (50, 40), 4)
    pygame.draw.circle(surf, _VOID, (50, 40), 3)
    pygame.draw.circle(surf, (255, 255, 255), (52, 38), 1)   # life glint
    # Bone keyline tracing the original beak so it reads skeletal (it is already
    # bone-coloured from the base; this crisps its top edge + a nostril dot).
    pygame.draw.circle(surf, _VOID, (54, 43), 1)             # nostril

    # ── Spine — a vertebra-bead column from the skull base to the tail root.
    spine = [(41, 46), (35, 49), (29, 52), (23, 54), (18, 55)]
    pygame.draw.lines(surf, _KEY, False, spine, 3)
    for vx, vy in spine:
        pygame.draw.circle(surf, _BONE, (vx, vy), 2)

    # ── Ribcage — three bold paired rib rungs off the sternum on the chest.
    pygame.draw.line(surf, _KEY,  (37, 48), (28, 60), 4)
    pygame.draw.line(surf, _BONE, (37, 48), (28, 60), 2)     # sternum
    for i, ty in enumerate((51, 55, 59)):
        sx = 34 - i * 3
        pygame.draw.arc(surf, _BONE, (sx - 12, ty - 5, 13, 12),
                        math.radians(20), math.radians(150), 2)
        pygame.draw.arc(surf, _BONE_SH, (sx - 1, ty - 5, 13, 12),
                        math.radians(30), math.radians(160), 2)

    # ── One white tail-feather bone over the original tail fan (x2–23 / y44–62).
    pygame.draw.line(surf, _KEY,  (19, 50), (5, 53), 3)
    pygame.draw.line(surf, _BONE, (19, 50), (5, 53), 1)

    # ── Legs — knob knees on the original bone leg lines (feet 26,69 / 36,69).
    for kx in (28, 34):
        pygame.draw.circle(surf, _BONE, (kx, 65), 2)


build = store_skins._make_skin(_paint, base_fn=_bone_parrot)
