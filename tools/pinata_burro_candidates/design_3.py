"""Burro piñata — RIBBON STREAMER TAIL variant (design 3).
A long curling paper ribbon from the rump in alternating festival colours
(pink → orange → pink), swinging with the trot.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared import (
    draw_rope, draw_legs, draw_body, draw_head,
    _make_prebuilt_skin, _phase, _TROT,
    BCX, BCY, PINK, ORANGE, ORANGE_D, CREAM,
)
import pygame


def _draw_tail(surf, cx, cy, bob, sway):
    # Anchor at rump, trail back then curl — reads as a tail, not a 5th leg.
    # PINK+ORANGE only; turquoise collides with day-sky at 40px.
    # All segments 5px fat + 1px keyline so they survive scale-down.
    p0 = (cx - 15, cy + 1)
    p1 = (cx - 25, cy + 0)

    # Segment 1: PINK rearward trail
    pygame.draw.line(surf, PINK, p0, p1, 5)
    pygame.draw.line(surf, (184, 28, 88), p0, p1, 1)

    # Segment 2: ORANGE, curves gently down
    p2 = (cx - 33, cy + 4)
    pygame.draw.line(surf, ORANGE, p1, p2, 5)
    pygame.draw.line(surf, ORANGE_D, p1, p2, 1)

    # Segment 3: PINK tip, large sway so ribbon whips visibly at 40px
    tip_x = int(cx - 38 + sway * 6)
    tip_y = int(cy + 4 - abs(sway) * 4)
    p3 = (tip_x, tip_y)
    pygame.draw.line(surf, PINK, p2, p3, 5)
    pygame.draw.line(surf, (184, 28, 88), p2, p3, 1)


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
