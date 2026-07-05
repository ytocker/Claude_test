"""Flamingo tail — DESIGN 3: SLEEK SWEPT. One smooth continuous wedge that flows
off the rump as a single shape merged with the body (wide at the body, tapering
to a soft point), with a highlight along the top edge. Minimal + elegant, clearly
part of the body. Scratch only."""
import pygame

from game.parrot import _aaellipse
from tools.flamingo_candidates._shared import (
    make, _FLA_BODY, _FLA_BODY_D, _FLA_BODY_H, BCX, BCY,
)


def tail(surf):
    # A single swept wedge: wide where it meets the body (x ~23, full rump
    # height) tapering to a soft tip at the back-left, so the silhouette reads as
    # one continuous body-plus-tail mass.
    pygame.draw.polygon(surf, _FLA_BODY_D, [
        (23, BCY - 2), (3, BCY + 4), (4, BCY + 9), (23, BCY + 9)])
    pygame.draw.polygon(surf, _FLA_BODY, [
        (22, BCY), (6, BCY + 5), (7, BCY + 8), (22, BCY + 8)])
    # Soft rounded tip + a top-edge highlight to sell the sweep.
    _aaellipse(surf, _FLA_BODY, (6, BCY + 5), 3, 3)
    pygame.draw.line(surf, _FLA_BODY_H, (21, BCY), (6, BCY + 4), 1)


build = make(tail)
