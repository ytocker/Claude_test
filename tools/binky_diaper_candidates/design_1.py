"""SNUG CLOTH — the trim, contour-hugging worn nappy (design_1).

A close-fitting cloth band wraps the rump (back-left) round the underside to the
front hip. It rides high and STOPS at a hard seam by y61 so the chubby legs the
scaffold paints below (y62+) read as clearly poking out beneath the nappy — no
"tub he sits in". Wide at the hips, trim across the belly, worn not bulky.

Cream cloth only — the pacifier keeps the entire pink budget. The lit `#FFFFFF`
waistband + one rib carry the day top read; a powder-shadow underside arc and a
hard `#ABA282` bottom seam hold the value (and the cloth-ends-here line) against
the navy night sky. Nothing cream or powder dips below y62.
"""
from __future__ import annotations
import pygame

from tools.binky_diaper_candidates._shared import (
    make_binky_build, _BB_DIAP, _BB_DIAP_HI, _BB_DIAP_SH, _BB_DIAP_LN)

# Powder underside arc tint — kept inside the cloth (above y62) so it never
# bleeds onto the scaffold legs; this is the cloth curving under, not a cuff.
_BB_DIAP_PWD = (201, 217, 222)


def _diaper(surf):
    # The whole band lives between the waist (~y52) and a HARD bottom cap (y61);
    # the scaffold legs render at y62+, so every cream/powder pixel stays above
    # them and the eye reads "cloth STOPS here, legs START there".

    # Rear wrap — a cream lobe sweeping the rump back-left so the "wrapped round
    # the back" read is unmistakable; tucked snug with no droop toward the legs.
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (13, 50, 16, 10))
    pygame.draw.ellipse(surf, _BB_DIAP,    (14, 51, 14, 7))
    pygame.draw.arc(surf, _BB_DIAP_SH, (14, 53, 14, 7), 3.3, 6.0, 1)

    # Main band — a flattened cream lobe hugging the belly contour across the
    # underside; wide at the hips, riding high so its bottom never passes y61.
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (17, 51, 24, 10))
    pygame.draw.ellipse(surf, _BB_DIAP,    (18, 51, 22, 8))

    # Underside powder-shadow arc (y59-61) — the value anchor that keeps the
    # cream from voiding into navy night and reads as the cloth curving under.
    # Held to y61 max so it stays clear of the legs.
    pygame.draw.arc(surf, _BB_DIAP_PWD, (18, 54, 22, 7), 3.45, 5.95, 2)

    # Waistband — a lit `#FFFFFF` top arc following the belly curve for the crisp
    # "fastened cloth" day line, with one `#ABA282` rib just under it.
    pygame.draw.arc(surf, _BB_DIAP_HI, (16, 49, 24, 7), 3.38, 6.05, 2)
    pygame.draw.arc(surf, _BB_DIAP_LN, (17, 51, 22, 6), 3.42, 5.98, 1)

    # Hard bottom seam — a 1px `#ABA282` line along the cloth's lowest edge (~y61)
    # so the cloth visibly ENDS; the scaffold legs begin below it at y62.
    pygame.draw.arc(surf, _BB_DIAP_LN, (18, 55, 22, 6), 3.55, 5.85, 1)

    # Centred fold line — one short seam between the leg roots, selling the
    # folded cloth; kept above y61 so it stops where the legs begin.
    pygame.draw.line(surf, _BB_DIAP_LN, (31, 56), (31, 60), 1)


build = make_binky_build(_diaper)
