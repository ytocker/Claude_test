"""Red panda back — DESIGN 5: FLUFFY RUMP (R3, final).

R3 fix per art-director C2: was reading as generic "hamster" with no species
signature. Added a short ringed tail nub (2 cream rings, one russet segment)
protruding from the rump lobe at the upper-left, so the rump reads as a
red-panda rump with its ringed tail poking out — not just a fluffy blob.
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

    # Fluffy rump lobe — core concept unchanged.
    rx, ry = BCX - 5, BCY + 6
    _aaellipse(surf, SEAM,  (rx,     ry + 2), 17, 14)
    _aaellipse(surf, FUR_D, (rx,     ry + 1), 16, 13)
    _aaellipse(surf, FUR,   (rx - 1, ry),     15, 12)
    _aaellipse(surf, FUR_H, (rx - 4, ry - 3),  5,  3)

    # Fur-break wisps around the rump outline (no clean ellipse read).
    for a_deg in (90, 115, 140, 165, 195, 220, 250):
        a  = math.radians(a_deg)
        rr = 15 + 3
        pygame.draw.circle(surf, FUR_D,
                           (int(rx - 1 + math.cos(a) * rr),
                            int(ry     + math.sin(a) * rr)), 3)
        pygame.draw.circle(surf, FUR,
                           (int(rx - 1 + math.cos(a) * (rr - 2)),
                            int(ry     + math.sin(a) * (rr - 2))), 2)

    # Short ringed tail nub protruding upper-left from the rump — the species
    # signature that makes this unmistakably a red panda, not a hamster.
    # Nub pivot sits at the upper-left edge of the rump lobe.
    nub_cx = rx - 12
    nub_cy = ry - 8
    nub_r  = 10
    nub_w  = 7
    nub_start = math.radians(220)
    nub_span  = math.radians(90) + lift * math.radians(8)
    nub_steps = 12

    # Russet nub base.
    for i in range(nub_steps + 1):
        t = i / nub_steps
        a = nub_start + nub_span * t
        pygame.draw.circle(surf, FUR,
                           (int(nub_cx + math.cos(a) * nub_r),
                            int(nub_cy + math.sin(a) * nub_r)), nub_w)

    # 2 cream rings on the nub so it reads as red-panda tail.
    for t in (0.25, 0.72):
        a  = nub_start + nub_span * t
        px = int(nub_cx + math.cos(a) * nub_r)
        py = int(nub_cy + math.sin(a) * nub_r)
        pygame.draw.circle(surf, RING,  (px, py), 5)
        pygame.draw.circle(surf, CREAM, (px, py), 4)

    # Cream tip of the nub.
    a  = nub_start + nub_span
    tx = int(nub_cx + math.cos(a) * nub_r)
    ty = int(nub_cy + math.sin(a) * nub_r)
    pygame.draw.circle(surf, SEAM,   (tx, ty), nub_w + 1)
    pygame.draw.circle(surf, CREAM_W,(tx, ty), nub_w - 1)

    # Longer tail arc (r=24) attached behind the rump.
    tcx, tcy = BCX + 1, BCY + 11
    r     = 24
    w     = 9
    start = math.radians(140)
    span  = math.radians(144) + lift * math.radians(14)
    steps = 28

    for i in range(steps + 1):
        t = i / steps
        a = start + span * t
        pygame.draw.circle(surf, SEAM,
                           (int(tcx + math.cos(a) * (r - w * 0.55)),
                            int(tcy + math.sin(a) * (r - w * 0.55))), w)
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

    for k in range(4):
        t  = (k + 0.65) / 4.6
        a  = start + span * t
        px = int(tcx + math.cos(a) * r)
        py = int(tcy + math.sin(a) * r)
        pygame.draw.circle(surf, RING,  (px, py), 6)
        pygame.draw.circle(surf, CREAM, (px, py), 5)

    a  = start + span
    tx = int(tcx + math.cos(a) * r)
    ty = int(tcy + math.sin(a) * r)
    pygame.draw.circle(surf, SEAM,   (tx, ty), w + 1)
    pygame.draw.circle(surf, CREAM_W,(tx, ty), w)


build = make(back)
