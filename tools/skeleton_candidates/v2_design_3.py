"""v2_design_3 — CALAVERA-MACAW: Día de Muertos sugar-skull parrot skeleton.

The corrected ``_v2_anatomy`` parrot skeleton (hooked bone beak + long tail) in
near-white bone, painted as a festive calavera: cyan-ringed eye sockets, a
teardrop marigold petal crown spiking off the cranium, a magenta cheek heart,
and a single marigold stroke high on the upper mandible. The hooked beak tip and
the dark gape stay PURE BONE so the parrot down-hook reads as bone; the paint is
the third read, never drowning the skeleton. Scratch only.
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
    # Span pulled UP (was -156..-24): the leftmost petals were tipping over the
    # cyan socket in the flap frames; -144..-30 keeps every petal above the
    # cranium so the crown->socket->beak read order is protected.
    for k in range(n):
        a = math.radians(-144 + k * (114.0 / (n - 1)))
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

    # ── Magenta cheek heart — relocated DOWN onto the jaw front (the crown
    # version vanished into the crown at 40px). A clean 2px solid heart with
    # bone around it, set on the cheek so it reads as a distinct calavera mark.
    hx, hy = 46, 20
    pygame.draw.circle(surf, _MAGENTA, (hx - 1, hy), 1)
    pygame.draw.circle(surf, _MAGENTA, (hx + 1, hy), 1)
    _poly(surf, _MAGENTA, [(hx - 2, hy), (hx + 2, hy), (hx, hy + 3)])

    # ── Marigold beak stroke — ONE short stroke high on the UPPER mandible only.
    # The down-hook tip (lower beak) and the dark gape stay PURE BONE so the
    # parrot hook reads as bone; the scroll is demoted to a single 1px filigree.
    pygame.draw.line(surf, _MARIGOLD, (53, 12), (56, 13), 1)

    # ── Two tiny accents framing the jaw grin — keep the colour off the ribs/
    # tail entirely so skull->ribs->wing->tail still parses as bone structure.
    pygame.draw.circle(surf, _CYAN, (42, 23), 1)
    pygame.draw.circle(surf, _MAGENTA, (49, 24), 1)


def _build(wing_angle_deg):
    return A.build_skeleton(wing_angle_deg, P, post=_paint)


build = _make_prebuilt_skin(_build)
