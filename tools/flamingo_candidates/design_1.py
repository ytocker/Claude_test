"""Flamingo tail — DESIGN 1: ROUNDED TUFT. A soft cluster of overlapping rounded
plume lobes rooted INSIDE the body rump (so it emerges from under the body, never
a floating shard) and trailing back-and-down. Everything else is the production
flamingo. Scratch only."""
from game.parrot import _aaellipse
from tools.flamingo_candidates._shared import (
    make, _FLA_BODY, _FLA_BODY_D, _FLA_BODY_H, BCX, BCY,
)


def tail(surf):
    # Roots well inside the body (x ~22) so the body overlaps the base; lobes
    # shrink as they trail back-left + slightly down off the rump.
    _aaellipse(surf, _FLA_BODY_D, (20, BCY + 5), 9, 7)     # base shadow lobe
    _aaellipse(surf, _FLA_BODY_D, (12, BCY + 7), 6, 5)
    _aaellipse(surf, _FLA_BODY,   (19, BCY + 4), 8, 6)     # mid mass
    _aaellipse(surf, _FLA_BODY,   (12, BCY + 6), 5, 4)
    _aaellipse(surf, _FLA_BODY_H, (18, BCY + 2), 4, 2)     # top highlight
    _aaellipse(surf, _FLA_BODY_H, (13, BCY + 4), 3, 2)


build = make(tail)
