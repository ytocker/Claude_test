"""v2_design_3 — CALAVERA-MACAW: Día de Muertos sugar-skull parrot skeleton.

The corrected ``_v2_anatomy`` parrot skeleton (hooked bone beak + long tail) in
near-white bone, painted as a festive calavera: cyan-ringed eye sockets, a
marigold petal crown spiking off the cranium, a magenta forehead heart, and a
marigold scroll on the beak. Bone stays the value anchor; the paint is the third
read, never drowning the skeleton. Scratch only.
"""
import pygame

from game.store_skins import _make_prebuilt_skin, _poly
from tools.skeleton_candidates import _v2_anatomy as A


P = A.Pal(
    bone=(255, 252, 239), bone_sh=(214, 210, 198), bone_deep=(120, 116, 104),
    body=(26, 22, 34), body_deep=(15, 12, 22), keyline=(44, 38, 52),
    socket=(20, 16, 28), glint=(255, 255, 255),
)

_MARIGOLD, _MARI_D = (255, 150, 28), (214, 110, 12)
_CYAN = (22, 200, 216)
_MAGENTA = (236, 46, 136)


def _paint(surf, angle_deg, P):
    # Marigold petal crown — discrete points spiking up off the cranium.
    for px, py in ((40, 5), (44, 3), (48, 3), (52, 5)):
        _poly(surf, _MARIGOLD, [(px, py), (px - 2, py + 4), (px + 2, py + 4)])
        pygame.draw.circle(surf, _MARI_D, (px, py + 4), 1)
    pygame.draw.circle(surf, _MARIGOLD, (46, 7), 2)              # crown centre bud
    # Cyan socket rings — the best-surviving calavera tell at 40px.
    pygame.draw.circle(surf, _CYAN, (45, 16), 4, 1)
    for a in range(0, 360, 60):
        import math
        rx = 45 + int(5 * math.cos(math.radians(a)))
        ry = 16 + int(5 * math.sin(math.radians(a)))
        pygame.draw.circle(surf, _CYAN, (rx, ry), 1)
    # Magenta forehead heart, set low between brow and crown.
    pygame.draw.circle(surf, _MAGENTA, (44, 11), 1)
    pygame.draw.circle(surf, _MAGENTA, (47, 11), 1)
    _poly(surf, _MAGENTA, [(43, 12), (48, 12), (45, 15)])
    # Marigold scroll line along the upper beak (painted bill).
    pygame.draw.line(surf, _MARIGOLD, (52, 14), (59, 19), 2)
    pygame.draw.circle(surf, _CYAN, (59, 20), 1)
    # Two cyan cheek-dots framing the grin.
    pygame.draw.circle(surf, _CYAN, (42, 23), 1)
    pygame.draw.circle(surf, _MAGENTA, (49, 24), 1)


def _build(wing_angle_deg):
    return A.build_skeleton(wing_angle_deg, P, post=_paint)


build = _make_prebuilt_skin(_build)
