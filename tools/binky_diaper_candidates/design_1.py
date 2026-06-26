"""SNUG CLOTH — the trim, contour-hugging worn nappy (design_1).

The shipped diaper sat at cy~64, down among the leg roots, so it read as a tub
BINKY sits in. This take instead wraps a close-fitting cloth band round the
rump + lower belly (y53-62) following the belly ellipse, leaving a powder-blue
gap to the bib above and the bare legs poking through clean below at y65.

Cream cloth only — the pacifier keeps the entire pink budget. Powder-shadow
underside + an `#ABA282` seam keep the shape from voiding flat against the navy
night sky; the lit white waistband carries the day top read.
"""
from __future__ import annotations
import pygame

from tools.binky_diaper_candidates._shared import (
    make_binky_build, _BB_DIAP, _BB_DIAP_HI, _BB_DIAP_SH, _BB_DIAP_LN)


def _diaper(surf):
    # Band hugs the lower belly between waist (y53) and crotch (y62); the rear
    # wrap reaches back-left over the rump. Everything stays above the legs
    # (y65+) so they read as poking *through* the cuffs, not sitting in a tub.

    # Rear wrap — cream lobe sweeping the rump back-left, tucked snug so it has
    # no droop or overhang that would creep toward the legs. Pulled a touch
    # further onto the rump so the "wrapped round the back" read is unmistakable.
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (13, 51, 16, 11))
    pygame.draw.ellipse(surf, _BB_DIAP,    (14, 52, 14, 8))
    pygame.draw.arc(surf, _BB_DIAP_SH, (14, 55, 14, 8), 3.3, 6.0, 1)

    # Main band — a flattened cream lobe following the belly contour across the
    # underside; wide at the hips, hugging tight so it never bulges past y63.
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (17, 53, 24, 11))
    pygame.draw.ellipse(surf, _BB_DIAP,    (18, 53, 22, 9))

    # Crotch gusset — a narrow cream tongue dipping between the leg roots, the
    # part that visually separates the two legs. Kept to y64 max so legs clear.
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (27, 58, 8, 7))
    pygame.draw.ellipse(surf, _BB_DIAP,    (28, 58, 6, 5))

    # Underside powder-shadow arc — the value anchor that keeps the cream lobe
    # from voiding into navy night; reads as the cloth curving under the belly.
    pygame.draw.arc(surf, _BB_DIAP_SH, (18, 56, 22, 9), 3.55, 5.87, 2)

    # Waistband — a thin lit band along the top edge following the belly curve,
    # giving the crisp "fastened cloth" top line that carries the day read.
    pygame.draw.arc(surf, _BB_DIAP_HI, (16, 51, 24, 7), 3.40, 6.05, 2)
    # Seam just under the waistband — the second night-value tell.
    pygame.draw.arc(surf, _BB_DIAP_LN, (18, 53, 22, 6), 3.45, 5.97, 1)

    # Centred crotch fold line — one short seam down the gusset, selling the
    # folded cloth between the legs.
    pygame.draw.line(surf, _BB_DIAP_LN, (31, 59), (31, 63), 1)

    # Leg-cuff shades — short powder arcs hugging each leg root so the legs read
    # as emerging *through* the nappy rather than from under a slab.
    pygame.draw.arc(surf, _BB_DIAP_SH, (24, 61, 6, 6), 3.3, 6.1, 2)
    pygame.draw.arc(surf, _BB_DIAP_SH, (33, 61, 6, 6), 3.3, 6.1, 2)


build = make_binky_build(_diaper)
