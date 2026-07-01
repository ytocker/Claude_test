"""Burro piñata — TASSEL TAIL variant (design 1).
Adds a pendant festival tassel at the rump matching the leg-tassel vocabulary:
cream stub + fat PINK knot + fanned strands. Only the strand TIPS sway so the
tail reads as a pendulum, not a shape that pops in and out of frame.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared import (
    draw_rope, draw_legs, draw_body, draw_head,
    _make_prebuilt_skin, _phase, _TROT,
    BCX, BCY, CREAM, CREAM_D, PINK, PINK_D, HOOF,
)
import pygame
from game.parrot import _aaellipse


def _draw_tail(surf, cx, cy, bob, sway):
    # Anchored stub + knot stay put in every frame; only the fanned strand tips
    # swing, so the tassel sways like a pendulum instead of popping in and out.
    ax, ay = cx - 16, cy + 2                 # rump anchor (fixed)
    kx, ky = cx - 24, cy + 5                 # knot centre at stub end (fixed)
    # Cream stub, rearward-and-down from the rump
    pygame.draw.line(surf, CREAM_D, (ax, ay), (kx, ky), 3)
    pygame.draw.line(surf, CREAM,   (ax, ay), (kx, ky), 1)
    # Fat pink tassel knot with a darker core + top-left highlight
    _aaellipse(surf, PINK, (kx, ky), 4, 4)
    pygame.draw.circle(surf, PINK_D, (kx, ky), 1)         # core
    pygame.draw.circle(surf, CREAM, (kx - 1, ky - 1), 1)  # highlight
    # Fanned strands: five spread ~40° below-and-back; only the tips sway.
    tip_dx = sway * 2
    for base_dx in (-3, -2, -1, 0, 1):
        tx = int(kx + base_dx + tip_dx)
        ty = ky + 7
        pygame.draw.line(surf, PINK, (kx, ky + 2), (tx, ty), 1)


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
