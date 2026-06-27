"""Burro piñata — DONKEY TUFT TAIL variant (design 2).
Classic short upright donkey tail: a stiff cream stub on the upper rump
ending in a dark fluffy tuft — the anatomical donkey reference.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared import (
    draw_rope, draw_legs, draw_body, draw_head,
    _make_prebuilt_skin, _phase, _TROT,
    BCX, BCY, CREAM, CREAM_D, ORANGE_D,
)
import pygame
from game.parrot import _aaellipse


def _draw_tail(surf, cx, cy, bob, sway):
    rx, ry = cx - 16, cy + 2          # root at upper rump
    # Stub tip sways slightly with trot
    tx = int(cx - 24 + sway * 1.5)
    ty = cy - 6
    # Stiff stub: outer shadow then bright cream
    pygame.draw.line(surf, CREAM_D, (rx, ry), (tx, ty), 5)
    pygame.draw.line(surf, CREAM,   (rx, ry), (tx, ty), 3)
    # Fluffy tuft: overlapping dark-warm circles
    _aaellipse(surf, ORANGE_D, (tx,     ty),     4, 4)
    _aaellipse(surf, ORANGE_D, (tx - 2, ty + 1), 3, 3)
    _aaellipse(surf, ORANGE_D, (tx + 1, ty + 2), 3, 3)
    _aaellipse(surf, CREAM_D,  (tx - 1, ty),     2, 2)  # light tip on tuft


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
