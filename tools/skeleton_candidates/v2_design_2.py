"""v2_design_2 — PIRATE-MACAW: the DEADMAN'S FLAG pirate on correct anatomy.

Keeps the v1 pirate gear — red bandana wrapping the cranium, a black eyepatch
over the socket, a gold hoop earring, and a steel cutlass slung across the back
breaking the silhouette — but rebuilt on the ``_v2_anatomy`` parrot skeleton so
the hooked bone beak and the long bony tail now read as a macaw. Bone is the
bright value anchor; the gear is the theme layer. Scratch only.
"""
import pygame

from game.store_skins import _make_prebuilt_skin, _poly
from tools.skeleton_candidates import _v2_anatomy as A


# Warm-ivory bone so the gear colours sit naturally on it.
P = A.Pal(
    bone=(244, 239, 224), bone_sh=(196, 188, 166), bone_deep=(150, 142, 122),
    body=(26, 20, 16), body_deep=(14, 10, 8), keyline=(40, 30, 24),
    socket=(8, 6, 5), glint=(255, 250, 235), rib=(96, 80, 64),
)

_RED, _RED_D, _RED_H = (200, 32, 43), (150, 22, 32), (236, 92, 96)
_BLACK, _BLACK_H = (26, 20, 16), (54, 46, 40)
_GOLD, _GOLD_H = (232, 178, 58), (255, 224, 140)
_STEEL, _STEEL_D, _STEEL_H = (185, 192, 201), (120, 128, 138), (228, 233, 238)


def _cutlass(surf, angle_deg, P):
    # Steel blade slung across the back, drawn behind the bones; gold crossguard
    # low by the hip, curved tip breaking the outline high past the shoulder.
    guard, butt, tip = (18, 40), (10, 47), (3, 8)
    pygame.draw.line(surf, _STEEL_D, butt, guard, 4)
    pygame.draw.line(surf, _STEEL, butt, guard, 2)
    pygame.draw.circle(surf, _GOLD, butt, 3)
    gx, gy = guard
    pygame.draw.line(surf, _GOLD, (gx - 4, gy + 4), (gx + 4, gy - 4), 4)
    spine = [(gx - 1, gy - 4), (15, 28), (12, 16), (9, 10), tip]
    pygame.draw.lines(surf, _STEEL_D, False, [(x + 1, y) for x, y in spine], 3)
    pygame.draw.lines(surf, _STEEL, False, spine, 2)
    pygame.draw.lines(surf, _STEEL_H, False, spine[:-1], 1)
    pygame.draw.line(surf, _STEEL, tip, (tip[0] + 4, tip[1] - 2), 2)
    pygame.draw.circle(surf, (255, 255, 255), tip, 1)


def _gear(surf, angle_deg, P):
    # Eyepatch over the socket — a black oval distinct from the round hollow.
    pygame.draw.line(surf, _BLACK, (38, 9), (43, 19), 2)        # strap
    A._aaellipse(surf, P.bone_sh, (41, 14), 5, 4)
    A._aaellipse(surf, _BLACK, (41, 14), 4, 3)
    A._aaellipse(surf, _BLACK_H, (40, 13), 2, 1)
    # Gold hoop earring at the jaw.
    pygame.draw.circle(surf, _GOLD, (43, 26), 2)
    pygame.draw.circle(surf, _GOLD_H, (42, 25), 1)
    # Red bandana wrapping the cranium (brow-hugging, knot-tail trailing back).
    band = [(37, 12), (55, 12), (54, 8), (38, 9)]
    _poly(surf, _RED, band)
    pygame.draw.line(surf, _RED_H, (41, 10), (52, 10), 2)
    _poly(surf, _RED, [(37, 9), (42, 8), (43, 13), (38, 14)])     # knot
    _poly(surf, _RED, [(38, 10), (31, 8), (30, 12), (38, 14)])    # tail back
    _poly(surf, _RED_D, [(38, 14), (30, 12), (34, 11)])
    pygame.draw.circle(surf, P.bone, (35, 12), 1)                 # one low dot
    # A bold X crossbones below the sternum (Jolly-Roger tell), dark-on-bone.
    for (ax, ay), (bx, by) in (((23, 40), (33, 46)), ((23, 46), (33, 40))):
        pygame.draw.line(surf, P.rib, (ax, ay), (bx, by), 3)
        for ex, ey in ((ax, ay), (bx, by)):
            pygame.draw.circle(surf, P.bone, (ex, ey), 2)
            pygame.draw.circle(surf, P.rib, (ex, ey), 2, 1)


def _build(wing_angle_deg):
    return A.build_skeleton(wing_angle_deg, P, pre=_cutlass, post=_gear,
                            draw_socket=True)


build = _make_prebuilt_skin(_build)
