"""DESIGN 2 — PUFFY DISPOSABLE: the bulky modern nappy.

Reads as a worn padded disposable on the rump + lower belly: a raised ribbed
waistband, a fat cream lobe bulging past the belly contour, and scalloped
leg-cuff gathers around each leg opening. The leg openings stay above the leg
roots (y65) so the legs poke out below — never a tub Pip sits in.

The leg-cuff ruffle is the diaper tell, so it is kept hard (>=2px) and shaded
in powder so it survives the 40px shrink. The cream lobe always carries a
powder underside arc + seam so it holds value against the navy night sky;
the lit white waistband carries the day read.
"""
from __future__ import annotations
import pygame

from tools.binky_diaper_candidates._shared import (
    make_binky_build, _BB_DIAP, _BB_DIAP_HI, _BB_DIAP_SH, _BB_DIAP_LN)


def _diaper(surf):
    # Padded body first, then the band/cuffs on top, so the cuff ruffles and
    # the lit waistband read crisp over the fill.

    # Deep underside shadow sells the bulk; sits low (y60-63) and slightly wide
    # so the silhouette puffs past the belly contour without reaching the legs.
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (15, 54, 28, 10))
    pygame.draw.ellipse(surf, _BB_DIAP_SH, (16, 56, 26, 8))

    # Fat rounded cream lobe — the bulging padded body, x16-42 / y54-63.
    pygame.draw.ellipse(surf, _BB_DIAP, (16, 54, 26, 8))
    pygame.draw.ellipse(surf, _BB_DIAP, (18, 56, 22, 7))

    # Chunky raised ribbed waistband (x17-41, y51-54): line stack reads as a
    # 3px band even after the shrink. Powder base, cream core, lit white top.
    pygame.draw.line(surf, _BB_DIAP_LN, (17, 53), (41, 53), 4)
    pygame.draw.line(surf, _BB_DIAP, (17, 52), (41, 52), 3)
    pygame.draw.line(surf, _BB_DIAP_HI, (18, 51), (40, 51), 1)
    # Stretchy-tape ribbing ticks.
    for tx in (23, 29, 35):
        pygame.draw.line(surf, _BB_DIAP_LN, (tx, 51), (tx, 53), 1)

    # Front resealable tape tab at the hip (x38-41, y55-57), one darker edge.
    pygame.draw.rect(surf, _BB_DIAP_HI, (38, 55, 3, 3))
    pygame.draw.line(surf, _BB_DIAP_LN, (41, 55), (41, 57), 1)

    # Leg-cuff gathers — the signature tell. Scalloped powder arcs around each
    # leg opening, kept hard at 2px so they survive 40px. Openings sit at y63-65,
    # above the leg roots, so legs emerge below.
    for ox in (24, 33):
        # back-to-front pair of 2px scallop bumps per opening
        pygame.draw.arc(surf, _BB_DIAP_SH,
                        (ox, 61, 4, 5), 3.5, 6.0, 2)
        pygame.draw.arc(surf, _BB_DIAP_SH,
                        (ox + 2, 61, 4, 5), 3.5, 6.0, 2)
        # powder shade tucked under each opening so the leg reads as poking out
        pygame.draw.line(surf, _BB_DIAP_SH, (ox + 1, 64), (ox + 4, 64), 1)

    # Centre crotch seam keeps the lobe from voiding to a flat blob on navy.
    pygame.draw.line(surf, _BB_DIAP_LN, (29, 56), (29, 62), 1)
    pygame.draw.line(surf, _BB_DIAP_SH, (28, 57), (28, 61), 1)


build = make_binky_build(_diaper)
