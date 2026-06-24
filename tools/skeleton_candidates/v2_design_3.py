"""v2_design_3 — CALAVERA-MACAW: Día de Muertos sugar-skull parrot skeleton.

The corrected ``_v2_anatomy`` parrot skeleton (hooked bone beak + long tail) in
near-white bone, painted as a festive calavera: cyan-ringed eye sockets, a
a teardrop marigold petal crown spiking off the cranium, a low magenta forehead
heart, and a curling marigold scroll on the big hooked beak. Bone stays the value
anchor; the paint is the third read, never drowning the skeleton. Scratch only.
"""
import math

import pygame

from game.store_skins import _make_prebuilt_skin, _poly
from tools.skeleton_candidates import _v2_anatomy as A


P = A.Pal(
    bone=(255, 252, 239), bone_sh=(214, 210, 198), bone_deep=(120, 116, 104),
    body=(26, 22, 34), body_deep=(15, 12, 22), keyline=(44, 38, 52),
    socket=(20, 16, 28), glint=(255, 255, 255),
)

_MARIGOLD, _MARI_D = (255, 150, 28), (214, 110, 12)
_MARI_HI = (255, 198, 96)
_CYAN, _CYAN_D = (24, 206, 224), (16, 150, 168)
_MAGENTA = (236, 46, 136)


def _petal(surf, cx, cy, ang, length, color, color_d):
    """A marigold crown petal as a teardrop pointing along ``ang``. A dark sliver
    is laid first by the caller so adjacent petals separate into spikes; kept
    >=2px wide so it survives the 40px downscale."""
    tx = cx + math.cos(ang) * length
    ty = cy + math.sin(ang) * length
    px, py = -math.sin(ang), math.cos(ang)
    wid = max(2.0, length * 0.42)
    base_l = (cx + px * wid * 0.5, cy + py * wid * 0.5)
    base_r = (cx - px * wid * 0.5, cy - py * wid * 0.5)
    mid_l = (cx + math.cos(ang) * length * 0.55 + px * wid,
             cy + math.sin(ang) * length * 0.55 + py * wid)
    mid_r = (cx + math.cos(ang) * length * 0.55 - px * wid,
             cy + math.sin(ang) * length * 0.55 - py * wid)
    _poly(surf, color, [base_l, mid_l, (tx, ty), mid_r, base_r])
    pygame.draw.line(surf, color_d, base_l, (tx, ty), 1)         # centre vein


def _paint(surf, angle_deg, P):
    # ── Marigold petal crown — the SILHOUETTE tell. Discrete teardrop petals
    # fanned across the top of the cranium, each rooted on a dark sliver so the
    # crown spikes upward as separate points instead of one orange blob. Magenta
    # alternates in for the festive two-tone, but marigold dominates the read.
    crx, cry = 46, 9
    petal_cols = ((_MARIGOLD, _MARI_D), (_MAGENTA, _MARI_D), (_MARIGOLD, _MARI_D),
                  (_MARI_HI, _MARI_D), (_MARIGOLD, _MARI_D), (_MAGENTA, _MARI_D),
                  (_MARIGOLD, _MARI_D))
    n = len(petal_cols)
    for k in range(n):
        a = math.radians(-156 + k * (132.0 / (n - 1)))
        col, cold = petal_cols[k]
        rx = crx + math.cos(a) * 2
        ry = cry + math.sin(a) * 2
        pygame.draw.line(surf, P.body_deep, (crx, cry), (rx, ry), 3)  # dark root
        _petal(surf, crx, cry, a, 7, col, cold)
    pygame.draw.circle(surf, _MARI_D, (crx, cry), 2)            # dark crown hub
    pygame.draw.circle(surf, _MARIGOLD, (crx, cry), 1)

    # ── Cyan socket ring — the best-surviving calavera tell at 40px. A bold 1px
    # loop plus six bead-dots around the anatomy's eye socket (~45,16); a dark
    # backing keeps the cyan crisp on bright bone, never mushing into the bone.
    ex, ey = 45, 16
    pygame.draw.circle(surf, P.body_deep, (ex, ey), 5, 1)      # dark backing
    pygame.draw.circle(surf, _CYAN, (ex, ey), 4, 1)
    for p in range(6):
        a = p * (math.pi / 3.0) + math.radians(15)
        bx = ex + int(round(math.cos(a) * 5))
        by = ey + int(round(math.sin(a) * 5))
        pygame.draw.circle(surf, _CYAN, (bx, by), 1)

    # ── Magenta forehead heart — small and set LOW, between the brow and crown,
    # so it never merges with the crown's magenta above it.
    hx, hy = 45, 12
    pygame.draw.circle(surf, _MAGENTA, (hx - 1, hy), 1)
    pygame.draw.circle(surf, _MAGENTA, (hx + 1, hy), 1)
    _poly(surf, _MAGENTA, [(hx - 2, hy + 1), (hx + 2, hy + 1), (hx, hy + 3)])

    # ── Marigold beak scroll — a curling filigree painted ON the big hooked
    # upper mandible. Two short curve-strokes + bead dots follow the beak's
    # forward bulge, decorating it WITHOUT flooding the bone so the hook read
    # (the parrot tell) survives. A cyan tip-bead caps it like a flower core.
    pygame.draw.lines(surf, _MARIGOLD, False, [(52, 13), (56, 14), (59, 17)], 2)
    pygame.draw.line(surf, _MARI_D, (53, 16), (57, 19), 1)     # under-curl
    pygame.draw.circle(surf, _MAGENTA, (54, 13), 1)            # scroll bead
    pygame.draw.circle(surf, _CYAN, (60, 18), 1)               # tip flower core

    # ── Two tiny accents framing the jaw grin — keep the colour off the ribs/
    # tail entirely so skull->ribs->wing->tail still parses as bone structure.
    pygame.draw.circle(surf, _CYAN, (42, 23), 1)
    pygame.draw.circle(surf, _MAGENTA, (49, 24), 1)


def _build(wing_angle_deg):
    return A.build_skeleton(wing_angle_deg, P, post=_paint)


build = _make_prebuilt_skin(_build)
