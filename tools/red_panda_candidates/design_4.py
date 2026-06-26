"""Red panda back — DESIGN 4: DROOP TAIL (R3, final).

R3 fix per art-director C2: the down-tail had a "hole" at 40px — body and
tail read as separate blobs. Closed by: (1) a connecting bridge mass painted
between the rump and the tail root; (2) the tail tip arc curled partially back
UP after the J-bottom so the silhouette rejoins the body outline.
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
    tcx, tcy = BCX - 10, BCY + 12
    r     = 17
    w     = 9
    start = math.radians(350)
    span  = math.radians(185) + lift * math.radians(8)   # extended slightly
    steps = 30

    # Fluffy rump anchor.
    _aaellipse(surf, SEAM,  (BCX - 5, BCY + 6), 14, 11)
    _aaellipse(surf, FUR_D, (BCX - 5, BCY + 5), 13, 10)
    _aaellipse(surf, FUR,   (BCX - 6, BCY + 4), 12,  9)

    # Connecting bridge: fills the gap between rump and tail root so they read
    # as one continuous mass rather than two separate blobs at 40px.
    bridge_cx = int(tcx + math.cos(start) * r)
    bridge_cy = int(tcy + math.sin(start) * r)
    for bx, by in ((bridge_cx - 2, bridge_cy + 2), (bridge_cx, bridge_cy + 4)):
        pygame.draw.circle(surf, FUR_D, (bx, by), w)
        pygame.draw.circle(surf, FUR,   (bx, by - 1), w - 2)

    # Dark outer outline (value-separation fix from R2).
    for i in range(steps + 1):
        t = i / steps
        a = start + span * t
        ro = r + w * 0.7
        pygame.draw.circle(surf, SEAM,
                           (int(tcx + math.cos(a) * ro),
                            int(tcy + math.sin(a) * ro)), max(1, w // 2 + 1))

    # Inner seam undercoat.
    for i in range(steps + 1):
        t = i / steps
        a = start + span * t
        pygame.draw.circle(surf, SEAM,
                           (int(tcx + math.cos(a) * (r - w * 0.55)),
                            int(tcy + math.sin(a) * (r - w * 0.55))), w)

    # Main russet plume.
    for i in range(steps + 1):
        t = i / steps
        a = start + span * t
        pygame.draw.circle(surf, FUR,
                           (int(tcx + math.cos(a) * r),
                            int(tcy + math.sin(a) * r)), w)
    for i in range(steps + 1):
        t = i / steps
        a = start + span * t
        pygame.draw.circle(surf, FUR_D,
                           (int(tcx + math.cos(a) * (r + w * 0.5)),
                            int(tcy + math.sin(a) * (r + w * 0.5))), max(1, w // 2))

    # 3 cream spots — small fills so russet dominates.
    for k in range(3):
        t  = (k + 0.8) / 3.8
        a  = start + span * t
        px = int(tcx + math.cos(a) * r)
        py = int(tcy + math.sin(a) * r)
        pygame.draw.circle(surf, RING,  (px, py), 5)
        pygame.draw.circle(surf, CREAM, (px, py), 3)

    # Bright tip — the arc now curls back slightly (span extended) so the tip
    # points more inward, rejoining the body silhouette.
    a  = start + span
    tx = int(tcx + math.cos(a) * r)
    ty = int(tcy + math.sin(a) * r)
    pygame.draw.circle(surf, SEAM,   (tx, ty), w + 1)
    pygame.draw.circle(surf, CREAM_W,(tx, ty), w - 2)


build = make(back)
