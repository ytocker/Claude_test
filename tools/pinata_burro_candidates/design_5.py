"""Burro piñata — STAR SPIKE TAIL variant (design 5).
A short rigid cream spike from the rump ending in a shimmering 5-pointed
festival star — a direct nod to the traditional 7-cone piñata star form.
"""
import math
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared import (
    draw_rope, draw_legs, draw_body, draw_head,
    _make_prebuilt_skin, _phase, _TROT,
    BCX, BCY, CREAM, CREAM_D, PINK, ORANGE, TURQ,
)
import pygame


_STAR_COLORS = (PINK, ORANGE, TURQ, PINK)   # cycles per trot phase → shimmer


def _star(surf, cx, cy, r_out, r_in, color):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(-90 + i * 36)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])


def _draw_tail(surf, cx, cy, bob, sway, ph):
    rx, ry = cx - 16, cy + 2
    tx = int(cx - 23 + sway * 1.5)
    ty = cy - 4
    # Cream spike stub
    pygame.draw.line(surf, CREAM_D, (rx, ry), (tx, ty), 4)
    pygame.draw.line(surf, CREAM,   (rx, ry), (tx, ty), 2)
    # Festival star at tip — colour cycles per phase for a shimmer
    _star(surf, tx, ty, 5, 2, _STAR_COLORS[ph % 4])


def build_fn(wing_angle_deg):
    surf = pygame.Surface((64, 84), pygame.SRCALPHA)
    ph = _phase(wing_angle_deg)
    bob = _TROT[ph]["bob"]
    sway = _TROT[ph]["sway"]
    cx, cy = BCX, BCY + bob
    draw_rope(surf, cx, cy)
    draw_legs(surf, cx, cy, sway)
    _draw_tail(surf, cx, cy, bob, sway, ph)   # tail BEFORE body so body overlaps root
    draw_body(surf, cx, cy)
    draw_head(surf, cx, cy)
    return surf


build = _make_prebuilt_skin(build_fn)
