"""v3_design_2 · X-RAY — a faithful skeleton of the ORIGINAL Pip macaw, full.

Same faithful base as the CLEAN take (`_bone_parrot` = the recoloured original
parrot, so silhouette + ORIGINAL beak + ORIGINAL tail location are exact), but the
paint shows the FULL anatomy "through" the dark flesh: a white cranium + hollow
socket, a complete vertebral column, a full ribcage (every rib), wing phalanges
fanning along the wing, leg bones with knees + claw feet, and tail-feather bones
across the original tail fan. Denser than CLEAN — must still pass the 40px read,
white bone staying the brightest element.

Paint is in COMPOSITE space (original sprite coords + PARROT_DY=20). Scratch only
— never registered in BUILDERS.
"""
import math
import pygame

from game import store_skins
from game.parrot import _aaellipse
from tools.skeleton_candidates._v3_bone_base import _bone_parrot

_BONE    = (255, 255, 255)
_BONE_SH = (224, 228, 236)
_KEY     = (58, 61, 71)
_VOID    = (13, 14, 19)


def _paint(surf, wing_angle_deg):
    # ── Skull — white cranium + hollow socket (head centre 47,41).
    _aaellipse(surf, _KEY,     (47, 40), 11, 10)
    _aaellipse(surf, _BONE,    (47, 40), 10, 9)
    _aaellipse(surf, _BONE_SH, (47, 44), 8, 4)
    pygame.draw.circle(surf, _KEY,  (50, 40), 4)
    pygame.draw.circle(surf, _VOID, (50, 40), 3)
    pygame.draw.circle(surf, (255, 255, 255), (52, 38), 1)
    pygame.draw.circle(surf, _VOID, (54, 43), 1)             # nostril
    # cranial suture line
    pygame.draw.line(surf, _BONE_SH, (43, 35), (50, 35), 1)

    # ── Full vertebral column — dense bead spine skull-base → tail root.
    spine = [(41, 46), (37, 48), (33, 50), (29, 52), (25, 53), (21, 54), (18, 55)]
    pygame.draw.lines(surf, _KEY, False, spine, 3)
    pygame.draw.lines(surf, _BONE, False, spine, 1)
    for vx, vy in spine:
        pygame.draw.circle(surf, _BONE, (vx, vy), 2)
        pygame.draw.circle(surf, _BONE_SH, (vx, vy), 2, 1)

    # ── Full ribcage — sternum + five paired ribs wrapping the chest/belly.
    pygame.draw.line(surf, _KEY,  (38, 47), (27, 61), 4)
    pygame.draw.line(surf, _BONE, (38, 47), (27, 61), 2)
    for i, ty in enumerate((49, 52, 55, 58, 61)):
        sx = 35 - i * 2
        pygame.draw.arc(surf, _BONE, (sx - 13, ty - 5, 14, 12),
                        math.radians(18), math.radians(155), 2)
        pygame.draw.arc(surf, _BONE_SH, (sx - 1, ty - 5, 14, 12),
                        math.radians(25), math.radians(162), 2)

    # ── Wing phalanges — finger-bones fanning along the wing mass (static
    #    overlay; reads as wing-bone at 40px even as the base wing flaps).
    wrist = (30, 49)
    for tip in ((44, 44), (47, 50), (40, 58)):
        pygame.draw.line(surf, _KEY,  wrist, tip, 3)
        pygame.draw.line(surf, _BONE, wrist, tip, 1)
        pygame.draw.circle(surf, _BONE, tip, 1)
    pygame.draw.circle(surf, _BONE, wrist, 2)

    # ── Tail-feather bones across the original tail fan (x2–23 / y44–62).
    for (x0, y0), (x1, y1) in (((20, 49), (5, 50)), ((20, 52), (4, 55)),
                               ((19, 55), (7, 60))):
        pygame.draw.line(surf, _KEY,  (x0, y0), (x1, y1), 3)
        pygame.draw.line(surf, _BONE, (x0, y0), (x1, y1), 1)

    # ── Legs — full bones: knob knees + 2-claw bone feet on the original lines.
    for kx, fx in ((28, 26), (34, 36)):
        pygame.draw.circle(surf, _BONE, (kx, 65), 2)
        for dx in (-2, 1):
            pygame.draw.line(surf, _BONE_SH, (fx, 69), (fx + dx, 72), 2)


build = store_skins._make_skin(_paint, base_fn=_bone_parrot)
