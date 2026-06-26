"""Red panda back — DESIGN 2: TAPERED BANDED (R3, final).

R3 fix per art-director C2: crescents were too similar to #1's spots at 40px.
Now each cream mark is drawn as a true cross-band — circles spanning a short
perpendicular arc segment that visibly wraps the tail width rather than just
marking the outer flank — so the banding is legible and distinct from #1.
"""
import math
import pygame

from tools.red_panda_candidates._shared import (
    make, _aaellipse,
    BCX, BCY,
    FUR, FUR_D, FUR_H, RING, SEAM, CREAM, CREAM_W,
)

# Cross-band t-positions along the arc and their width (cream fill radius).
_BANDS_T = (0.18, 0.38, 0.58, 0.78)
_BAND_W  = 5   # cream fill radius (wide enough to span the tail cross-section)


def back(surf, f):
    lift = 1 - f
    tcx, tcy = BCX + 3, BCY + 9
    r     = 23
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

    # Cross-bands: cream circles at 3 radii (inner / centre / outer) so the
    # band genuinely wraps across the tail width rather than being a flank dot.
    for t in _BANDS_T:
        a  = start + span * t
        w  = max(4, int(12 - t * 8))
        for roff in (-int(w * 0.5), 0, int(w * 0.5)):
            rr = r + roff
            px = int(tcx + math.cos(a) * rr)
            py = int(tcy + math.sin(a) * rr)
            pygame.draw.circle(surf, RING,  (px, py), _BAND_W + 1)
            pygame.draw.circle(surf, CREAM, (px, py), _BAND_W)

    # White terminal tip.
    a  = start + span
    tx = int(tcx + math.cos(a) * r)
    ty = int(tcy + math.sin(a) * r)
    pygame.draw.circle(surf, SEAM,   (tx, ty), 6)
    pygame.draw.circle(surf, CREAM_W,(tx, ty), 4)


build = make(back)
