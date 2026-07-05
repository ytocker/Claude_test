"""Flamingo tail — DESIGN 5: FLUFFY POMPOM. A fuller, plush powder-puff rump
tuft — a base lobe ringed with small rounded bumps for a fluffy texture, sitting
snug against the body so it's maximally attached. The cute/casual take. Scratch
only."""
from game.parrot import _aaellipse
from tools.flamingo_candidates._shared import (
    make, _FLA_BODY, _FLA_BODY_D, _FLA_BODY_H, BCX, BCY,
)


def tail(surf):
    # Plush base mass rooted under the body rump.
    _aaellipse(surf, _FLA_BODY_D, (16, BCY + 5), 10, 8)
    _aaellipse(surf, _FLA_BODY,   (15, BCY + 4), 9, 7)
    # A ring of small bumps around the back-left edge → fluffy powder-puff.
    for bx, by, br in ((8, BCY + 1, 4), (6, BCY + 6, 4), (9, BCY + 10, 4),
                       (14, BCY + 11, 3), (12, BCY - 1, 3)):
        _aaellipse(surf, _FLA_BODY_D, (bx, by), br, br)
        _aaellipse(surf, _FLA_BODY,   (bx - 1, by - 1), br - 1, br - 1)
    # Top sheen so the puff catches light.
    _aaellipse(surf, _FLA_BODY_H, (12, BCY + 1), 4, 2)


build = make(tail)
