"""Burro piñata — RIBBON STREAMER TAIL variant (design 3).
A long curling paper ribbon from the rump in alternating festival colours
(pink → orange → turquoise), swinging with the trot.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared import (
    draw_rope, draw_legs, draw_body, draw_head,
    _make_prebuilt_skin, _phase, _TROT,
    BCX, BCY, PINK, ORANGE, TURQ, CREAM,
)
import pygame


def _draw_tail(surf, cx, cy, bob, sway):
    sw = sway * 2.0               # full swing with trot
    # Three ribbon segments, alternating festival colours.
    # Points are offset by sw so the whole ribbon sways.
    p0 = (cx - 16,          cy + 4)
    p1 = (cx - 22 + sw,     cy + 10)
    p2 = (cx - 27 + sw * 0.7, cy + 5)
    p3 = (cx - 25 + sw * 0.5, cy + 13)

    for (a, b, col) in [(p0, p1, PINK), (p1, p2, ORANGE), (p2, p3, TURQ)]:
        pygame.draw.line(surf, col, (int(a[0]), int(a[1])),
                         (int(b[0]), int(b[1])), 3)
    # Bright tip end to read at 40px
    pygame.draw.circle(surf, PINK, (int(p3[0]), int(p3[1])), 2)


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
