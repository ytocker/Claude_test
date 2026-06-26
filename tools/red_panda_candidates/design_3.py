"""Red panda back — DESIGN 3: BANDED RINGS (R3, final).

R3 fixes per art-director C2:
- Floor tail width at 9px so the last third doesn't float as a detached object.
- Reduce to 4 bold cream rings (was ~6 narrow ones), each painted as a wide
  arc segment (~25° span) so rings read as rings not zipper-noise at 40px.
- Rings centred at non-uniform positions for a natural feel.
"""
import math
import pygame

from tools.red_panda_candidates._shared import (
    make, _aaellipse,
    BCX, BCY,
    FUR, FUR_D, FUR_H, RING, SEAM, CREAM, CREAM_W,
)

# 4 ring centres as fractions of the arc span.
_RING_T = (0.17, 0.38, 0.60, 0.80)
_RING_HALF_SPAN = math.radians(12)   # ±12° = ~24° total per ring


def back(surf, f):
    lift = 1 - f
    tcx, tcy = BCX + 3, BCY + 9
    r     = 26
    w_max = 9                          # floor width
    start = math.radians(138)
    span  = math.radians(150) + lift * math.radians(16)
    steps = 32

    _aaellipse(surf, SEAM,  (BCX - 4, BCY + 8), 15, 12)
    _aaellipse(surf, FUR_D, (BCX - 4, BCY + 7), 14, 11)
    _aaellipse(surf, FUR,   (BCX - 5, BCY + 6), 13, 10)

    # Shared seam undercoat.
    for i in range(steps + 1):
        t = i / steps
        a = start + span * t
        pygame.draw.circle(surf, SEAM,
                           (int(tcx + math.cos(a) * (r - w_max * 0.55)),
                            int(tcy + math.sin(a) * (r - w_max * 0.55))), w_max)

    # Russet base plume — constant width (floored at 9px, no taper at the tip).
    for i in range(steps + 1):
        t = i / steps
        a = start + span * t
        pygame.draw.circle(surf, FUR,
                           (int(tcx + math.cos(a) * r),
                            int(tcy + math.sin(a) * r)), w_max)
    # Outer shade rim.
    for i in range(steps + 1):
        t = i / steps
        a = start + span * t
        pygame.draw.circle(surf, FUR_D,
                           (int(tcx + math.cos(a) * (r + w_max * 0.5)),
                            int(tcy + math.sin(a) * (r + w_max * 0.5))), max(1, w_max // 2))

    # 4 bold cream ring-bands — each spans ±12° around its centre position.
    ring_steps = 8
    for rt in _RING_T:
        a_cen = start + span * rt
        for i in range(ring_steps + 1):
            da = -_RING_HALF_SPAN + 2 * _RING_HALF_SPAN * (i / ring_steps)
            a  = a_cen + da
            px = int(tcx + math.cos(a) * r)
            py = int(tcy + math.sin(a) * r)
            pygame.draw.circle(surf, RING,  (px, py), 6)
            pygame.draw.circle(surf, CREAM, (px, py), 5)

    # Bright white terminal tip.
    a  = start + span
    tx = int(tcx + math.cos(a) * r)
    ty = int(tcy + math.sin(a) * r)
    pygame.draw.circle(surf, SEAM,   (tx, ty), w_max + 1)
    pygame.draw.circle(surf, CREAM_W,(tx, ty), w_max)


build = make(back)
