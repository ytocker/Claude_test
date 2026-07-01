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


# 5 strips: (angle_from_pos_x in degrees, color, length)
_PLUME = [
    (-150, PINK,   13),
    (-125, ORANGE, 14),
    (-100, CREAM,  12),
    (-75,  TURQ,   14),
    (-50,  PINK_D, 12),
]


def _strip(surf, rx, ry, angle_deg, length, color):
    """Slim pointed strip from root (rx,ry) at angle, tapering to a point."""
    a = math.radians(angle_deg)
    tx = rx + math.cos(a) * length
    ty = ry + math.sin(a) * length
    # Perpendicular for base width
    px = -math.sin(a) * 2.0
    py =  math.cos(a) * 2.0
    pts = [
        (int(rx + px), int(ry + py)),
        (int(rx - px), int(ry - py)),
        (int(tx), int(ty)),
    ]
    pygame.draw.polygon(surf, color, pts)


def _draw_tail(surf, cx, cy, bob, sway):
    rx, ry = cx - 16, cy + 2
    sway_deg = sway * 3.0    # whole fan pivots slightly with trot
    for angle_deg, color, length in _PLUME:
        _strip(surf, rx, ry, angle_deg + sway_deg, length, color)


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
