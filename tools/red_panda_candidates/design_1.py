"""Red panda back — DESIGN 1: TAPERED PLUME (R3, final).

R3 fixes per art-director C2:
- Cream spots staggered off the mechanical vertical column: top spot rides the
  outer curl (r+1), middle pair offset inward (r-2), root spot stays on-arc.
- Tail pulled in 3px (r 26→23) so outer wisps clear the UI safe area.
"""
import math
import pygame

from tools.red_panda_candidates._shared import (
    make, _aaellipse,
    BCX, BCY,
    FUR, FUR_D, FUR_H, RING, SEAM, CREAM, CREAM_W,
)


def back(surf, f):
    lift = 1 - f
    tcx, tcy = BCX + 3, BCY + 9
    r     = 23                         # pulled in 3px from R2's 26
    start = math.radians(138)
    span  = math.radians(150) + lift * math.radians(16)
    steps = 32

    _aaellipse(surf, SEAM,  (BCX - 4, BCY + 8), 15, 12)
    _aaellipse(surf, FUR_D, (BCX - 4, BCY + 7), 14, 11)
    _aaellipse(surf, FUR,   (BCX - 5, BCY + 6), 13, 10)

    # Outer fur-break wisps.
    for i in range(0, steps, 2):
        t  = i / steps
        a  = start + span * t
        w  = max(4, int(12 - t * 8))
        ro = r + w * 0.7 + 4
        for da in (-0.18, 0.0, 0.18):
            pygame.draw.circle(surf, FUR_D,
                               (int(tcx + math.cos(a + da) * ro),
                                int(tcy + math.sin(a + da) * ro)), 3)

    # Inner fur-break wisps.
    for i in range(0, steps, 3):
        t  = i / steps
        a  = start + span * t
        w  = max(4, int(12 - t * 8))
        ri = r - w * 0.6 - 2
        for da in (-0.12, 0.0, 0.12):
            pygame.draw.circle(surf, FUR_D,
                               (int(tcx + math.cos(a + da) * ri),
                                int(tcy + math.sin(a + da) * ri)), 2)

    # Main tapered plume.
    for i in range(steps + 1):
        t  = i / steps
        a  = start + span * t
        w  = max(4, int(12 - t * 8))
        pygame.draw.circle(surf, FUR,
                           (int(tcx + math.cos(a) * r),
                            int(tcy + math.sin(a) * r)), w)

    # 5 cream spots — STAGGERED so they don't form a mechanical column at 40px.
    # (t, radius-offset) pairs: top spot rides the outer curl, pairs offset inward.
    _SPOT_OFFSETS = (
        (0.14, +1),   # near root  — slightly outer
        (0.32, -2),   # lower-mid  — inward
        (0.50,  0),   # mid
        (0.68, -2),   # upper-mid  — inward
        (0.84, +1),   # near tip   — slightly outer
    )
    for t, roff in _SPOT_OFFSETS:
        a  = start + span * t
        w  = max(4, int(12 - t * 8))
        sr = max(2, int(w * 0.62))
        rr = r + roff
        px = int(tcx + math.cos(a) * rr)
        py = int(tcy + math.sin(a) * rr)
        pygame.draw.circle(surf, RING,  (px, py), sr + 1)
        pygame.draw.circle(surf, CREAM, (px, py), sr)

    # Sharpened terminal tip.
    a  = start + span
    tx = int(tcx + math.cos(a) * r)
    ty = int(tcy + math.sin(a) * r)
    pygame.draw.circle(surf, SEAM,   (tx, ty), 6)
    pygame.draw.circle(surf, CREAM_W,(tx, ty), 4)


build = make(back)
