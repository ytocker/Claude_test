"""Burro piñata — DONKEY TUFT TAIL variant (design 2).
Classic short upright donkey tail: a stiff cream stub on the upper rump
ending in a dark fluffy tuft — the anatomical donkey reference.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared import (
    draw_rope, draw_legs, draw_body, draw_head,
    _make_prebuilt_skin, _phase, _TROT,
    BCX, BCY, CREAM, CREAM_D,
)
import pygame
from game.parrot import _aaellipse


def _draw_tail(surf, cx, cy, bob, sway):
    # Anchored high on the hot-pink top band's rear corner so the stub
    # clears the front tassel-leg cluster below it — a low root fuses with
    # the legs at 40px and stops reading as a tail.
    rx, ry = cx - 15, cy - 5
    # Sway swings the TUFT TIP, not the whole stub; the root stays pinned so
    # the switch trails the bob instead of sliding as a rigid stick.
    tip_x = int(cx - 22 + sway * 2)
    tip_y = cy - 11
    # Pale stiff stub — cream against the body edge gives the value contrast
    # a real donkey switch reads by (light rump edge → dark tuft).
    pygame.draw.line(surf, CREAM, (rx, ry), (tip_x, tip_y), 2)
    # Dark charcoal-brown teardrop tuft: taller than wide, not a round pom.
    _aaellipse(surf, (58, 42, 34), (tip_x, tip_y), 4, 6)
    # Cream rim catch-light on the upper-left edge to lift it off the body.
    pygame.draw.circle(surf, (242, 233, 220), (tip_x - 2, tip_y - 3), 1)


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
