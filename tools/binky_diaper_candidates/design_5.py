"""FOLD-OVER FRONT — the structured nappy with a turned-down waistband (design_5).

The shipped diaper sat at cy~64, down among the leg roots, so it read as a tub
BINKY sits in. This take wraps a structured nappy round the rump + lower belly
(y52-63) and folds the front waistband down into a panel, so a crisp horizontal
seam cuts across the belly — the architectural tell that survives the 40px
downscale on both day and navy night.

Cream cloth only — the pacifier keeps the entire pink budget. The hard `#ABA282`
seam under the turned-down panel plus the `#C9D9DE` powder-shadow underside hold
the shape's value against navy; the lit `#FFFFFF` panel top carries the day read.
"""
from __future__ import annotations
import pygame

from tools.binky_diaper_candidates._shared import (
    make_binky_build, _BB_DIAP, _BB_DIAP_HI, _BB_DIAP_SH, _BB_DIAP_LN)


def _diaper(surf):
    # Everything sits above the legs (y65+) so they read as poking out below,
    # never as the bird sitting inside a tub.

    # Rear wrap — a plain smooth cream lobe round the rump back-left; the panel
    # detail is all up front, so the back stays quiet and uncluttered.
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (15, 52, 12, 10))
    pygame.draw.ellipse(surf, _BB_DIAP,    (16, 53, 10, 8))

    # Lower body — the cream that shows BELOW the turned-down panel, wrapping
    # the underside between the leg roots; capped at y63 so the legs clear.
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (25, 56, 14, 8))
    pygame.draw.ellipse(surf, _BB_DIAP,    (26, 57, 12, 6))

    # Fold-over front panel — the signature. A flap turned down across the front
    # belly with a flat top and a hard bottom edge; drawn as a filled rect so the
    # seam stays a crisp horizontal line rather than a soft elliptical curve.
    pygame.draw.rect(surf, _BB_DIAP, (24, 52, 18, 6))

    # Panel top — lit white waistband edge that carries the bright-day top read.
    pygame.draw.line(surf, _BB_DIAP_HI, (25, 53), (41, 53), 2)

    # Panel bottom — the crisp turned-down seam, the architectural 40px tell.
    # Kept a hard 2px so it doesn't dissolve when the sprite shrinks to game size.
    pygame.draw.line(surf, _BB_DIAP_LN, (24, 58), (42, 58), 2)
    # A thread of powder-shadow just under the seam reads as the panel's free
    # edge casting onto the cloth below, and anchors value on navy night.
    pygame.draw.line(surf, _BB_DIAP_SH, (25, 59), (41, 59), 1)

    # Tape strip — a short vertical closure stripe centred on the panel, the
    # detail that says "fastened nappy" rather than "folded towel".
    pygame.draw.line(surf, _BB_DIAP_LN, (32, 54), (32, 57), 2)

    # Crotch seam — a centred fold down the lower body, separating the legs.
    pygame.draw.line(surf, _BB_DIAP_LN, (32, 59), (32, 63), 1)

    # Underside powder-shadow arc — the cloth curving under the belly; the main
    # value anchor that keeps the lower lobe from voiding flat into navy.
    pygame.draw.arc(surf, _BB_DIAP_SH, (25, 59, 14, 6), 3.45, 5.97, 2)

    # Leg-cuff shades — short powder arcs hugging each leg root so the legs read
    # as emerging *through* the nappy rather than from beneath a slab.
    pygame.draw.arc(surf, _BB_DIAP_SH, (24, 61, 6, 6), 3.3, 6.1, 2)
    pygame.draw.arc(surf, _BB_DIAP_SH, (33, 61, 6, 6), 3.3, 6.1, 2)


build = make_binky_build(_diaper)
