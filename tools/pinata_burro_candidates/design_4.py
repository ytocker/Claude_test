"""Burro piñata — CREPE PLUME TAIL variant (design 4).
A wide fan of 5 crepe-paper strips at the rump, arranged in a peacock-style
spread, in festival colours. The boldest tail silhouette.
"""
import math
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared import (
    draw_rope, draw_legs, draw_body, draw_head,
    _make_prebuilt_skin, _phase, _TROT,
    BCX, BCY, PINK, PINK_D, ORANGE, TURQ, CREAM,
)
import pygame


def _draw_tail(surf, cx, cy, bob, sway):
    # Pivot at rump: rear edge of turquoise band
    pivot_x = cx - 17
    pivot_y = cy + 2

    # 5 crepe strips as pointed polygons fanning upper-left to lower-left over a
    # ~90° arc (-155°..-65°). The wider spread + high-contrast alternating colours
    # keep the strips reading as distinct plumes at 40px instead of merging into a
    # single pink wedge. sway rotates the whole fan so it opens/closes in motion.
    fan_rot = sway * 5.0   # degrees: +1 sway → fan rotates +5°
    strips = [
        (-155 + fan_rot, PINK,   14),
        (-132 + fan_rot, CREAM,  13),
        (-110 + fan_rot, ORANGE, 13),
        (-87  + fan_rot, TURQ,   14),
        (-65  + fan_rot, PINK_D, 11),
    ]
    for ang_deg, color, length in strips:
        ang = math.radians(ang_deg)
        tip_x = pivot_x + math.cos(ang) * length
        tip_y = pivot_y + math.sin(ang) * length
        # Strip base width = 3px perpendicular to the strip direction
        perp = math.radians(ang_deg + 90)
        bw = 3   # half-base-width
        base_l = (pivot_x + math.cos(perp)*bw, pivot_y + math.sin(perp)*bw)
        base_r = (pivot_x - math.cos(perp)*bw, pivot_y - math.sin(perp)*bw)
        pts = [base_l, (tip_x, tip_y), base_r]
        pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])
        # CREAM keyline along the strip edges
        pygame.draw.line(surf, CREAM, (int(base_l[0]), int(base_l[1])),
                         (int(tip_x), int(tip_y)), 1)


def build_fn(wing_angle_deg):
    surf = pygame.Surface((64, 84), pygame.SRCALPHA)
    ph = _phase(wing_angle_deg)
    bob = _TROT[ph]["bob"]
    sway = _TROT[ph]["sway"]
    cx, cy = BCX, BCY + bob
    draw_rope(surf, cx, cy)
    draw_legs(surf, cx, cy, sway)
    _draw_tail(surf, cx, cy, bob, sway)   # tail BEFORE body so body overlaps root
    draw_body(surf, cx, cy)
    draw_head(surf, cx, cy)
    return surf


build = _make_prebuilt_skin(build_fn)
