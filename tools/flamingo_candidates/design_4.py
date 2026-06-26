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
    # Solid connecting base lobe under the body rump.
    _aaellipse(surf, _FLA_BODY_D, (20, BCY + 4), 8, 6)
    _aaellipse(surf, _FLA_BODY,   (19, BCY + 3), 7, 5)
    # Three upswept wisps rooted IN the lobe, curling up + back.
    for (rx, ry, mx, my, tx, ty) in (
        (18, BCY,     11, BCY - 4, 4, BCY - 5),
        (19, BCY + 1, 12, BCY - 2, 5, BCY - 1),
        (19, BCY + 3, 12, BCY + 2, 4, BCY + 4),
    ):
        pygame.draw.lines(surf, _FLA_BODY_D, False,
                          [(rx, ry), (mx, my), (tx, ty)], 2)
        pygame.draw.line(surf, _FLA_BODY_H, (rx, ry), (mx, my), 1)


build = make(tail)
