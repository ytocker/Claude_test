"""Burro piñata — TASSEL TAIL variant (design 1).
Adds a pendant festival tassel at the rump matching the leg-tassel vocabulary:
cream stub + fat ORANGE knot + fanned strands. Sways with the trot animation.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared import (
    draw_rope, draw_legs, draw_body, draw_head,
    _make_prebuilt_skin, _phase, _TROT,
    BCX, BCY, CREAM, CREAM_D, ORANGE, HOOF,
)
import pygame
from game.parrot import _aaellipse


def _draw_tail(surf, cx, cy, bob, sway):
    # Root at rear-left body edge, mid-height
    rx = int(cx - 16 + sway * 2)   # sways with trot
    ry = cy + 3
    # Cream stub
    kx, ky = rx - 3, ry + 6        # knot position (slightly left+down from root)
    pygame.draw.line(surf, CREAM_D, (rx, ry), (kx, ky), 4)
    pygame.draw.line(surf, CREAM,   (rx, ry), (kx, ky), 2)
    # Fat tassel knot
    _aaellipse(surf, ORANGE, (kx, ky + 2), 5, 5)
    pygame.draw.circle(surf, CREAM, (kx, ky + 2), 1)   # keyline
    # Fanned strands below knot
    for dx in (-3, -1, 0, 1, 3):
        pygame.draw.line(surf, ORANGE, (kx, ky + 2),
                         (kx + dx, ky + 9), 1)


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
