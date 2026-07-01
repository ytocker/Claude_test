"""Burro piñata — RIBBON STREAMER TAIL variant (design 3).
A long curling paper ribbon from the rump in alternating festival colours
(pink → orange → turquoise), swinging with the trot.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared import (
    draw_rope, draw_legs, draw_body, draw_head,
    _make_prebuilt_skin, _phase, _TROT,
    BCX, BCY, PINK, ORANGE, TURQ, ORANGE_D, TURQ_D, CREAM,
)
import pygame


def _draw_tail(surf, cx, cy, bob, sway):
    # Anchor at rump, trail BACK then curl — reads as a tail, not a 5th leg.
    # Leading PINK carries the highest contrast on any sky phase; the tip
    # alone sways so the anchor stays visually planted to the rump.
    # Segment 1: horizontal rearward trail (PINK, 3px wide)
    p0 = (cx - 15, cy + 1)
    p1 = (cx - 25, cy + 0)   # trail back ~10px first
    pygame.draw.line(surf, PINK, p0, p1, 3)
    pygame.draw.line(surf, (184, 28, 88), p0, p1, 1)  # dark keyline

    # Segment 2: ORANGE, gently curves down
    p2 = (cx - 32, cy + 4)
    pygame.draw.line(surf, ORANGE, p1, p2, 3)
    pygame.draw.line(surf, ORANGE_D, p1, p2, 1)

    # Segment 3: TURQ tip, animated — only this segment sways
    tip_x = int(cx - 37 + sway * 3)
    tip_y = int(cy + 2 - abs(sway) * 2)   # rises on the out-frames
    p3 = (tip_x, tip_y)
    pygame.draw.line(surf, TURQ, p2, p3, 3)
    pygame.draw.line(surf, TURQ_D, p2, p3, 1)


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
