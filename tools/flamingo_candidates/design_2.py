"""Flamingo tail — DESIGN 2: LAYERED FEATHERS. Three tapered feather strokes
fanning back off the rump (one up, one straight, one down), each rooted under the
body with overlapping bases + a pale rib, so they read as real plumage attached
to the body. Scratch only."""
import pygame

from game.parrot import _aaellipse
from tools.flamingo_candidates._shared import (
    make, _FLA_BODY, _FLA_BODY_D, _FLA_BODY_H, BCX, BCY,
)


def _feather(surf, root, tip, w, col, hi):
    rx, ry = root
    tx, ty = tip
    pygame.draw.polygon(surf, col, [(rx, ry - w), (tx, ty), (rx, ry + w)])
    pygame.draw.line(surf, hi, (rx, ry), (tx, ty), 1)


def tail(surf):
    # A solid connecting base under the body rump first, so no feather floats.
    _aaellipse(surf, _FLA_BODY_D, (20, BCY + 5), 9, 7)
    # Three FAT feathers in a TIGHT back-swept fan (not a wide spiky splay) so
    # they read as overlapping plumage, rooted at x~21 under the body edge.
    _feather(surf, (21, BCY + 2), (5, BCY - 1), 4, _FLA_BODY_D, _FLA_BODY_H)
    _feather(surf, (21, BCY + 5), (3, BCY + 5), 4, _FLA_BODY, _FLA_BODY_H)
    _feather(surf, (21, BCY + 8), (6, BCY + 10), 4, _FLA_BODY_D, _FLA_BODY_H)
    # Mid lobe over the roots to merge them into the body.
    _aaellipse(surf, _FLA_BODY, (19, BCY + 4), 7, 5)


build = make(tail)
