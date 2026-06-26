"""Flamingo tail — DESIGN 4: UPSWEPT WISPS. A solid base lobe at the rump (the
connector) from which three thin wisps curl UP-and-back, like a flamingo's
perked tail. The base lobe keeps the wisps growing from a connected mass rather
than floating. Scratch only."""
import pygame

from game.parrot import _aaellipse
from tools.flamingo_candidates._shared import (
    make, _FLA_BODY, _FLA_BODY_D, _FLA_BODY_H, BCX, BCY,
)


def tail(surf):
    # Fuller solid connecting base lobe under the body rump so the wisps grow
    # from a clear tail mass (not whiskers off the body).
    _aaellipse(surf, _FLA_BODY_D, (19, BCY + 4), 9, 7)
    _aaellipse(surf, _FLA_BODY,   (18, BCY + 3), 8, 6)
    _aaellipse(surf, _FLA_BODY_H, (16, BCY + 1), 3, 2)
    # Three THICK upswept plumes rooted IN the lobe, curling up + back together
    # (a tighter sweep so they read as a perked tail, not stray whiskers).
    for (rx, ry, mx, my, tx, ty) in (
        (16, BCY - 1, 10, BCY - 4, 5, BCY - 4),
        (17, BCY + 1, 10, BCY - 1, 4, BCY),
        (18, BCY + 3, 11, BCY + 2, 5, BCY + 3),
    ):
        pygame.draw.lines(surf, _FLA_BODY_D, False,
                          [(rx, ry), (mx, my), (tx, ty)], 3)
        pygame.draw.line(surf, _FLA_BODY_H, (rx, ry), (mx, my), 1)


build = make(tail)
