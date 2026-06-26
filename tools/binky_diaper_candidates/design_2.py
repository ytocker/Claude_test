"""DESIGN 2 — PUFFY DISPOSABLE: the bulky modern nappy, worn not stuck on.

The make-or-break read is two legs sticking out BELOW a banded cream nappy, so
the cloth is built as an underside BAND that curves from the back rump around
the belly's UNDERSIDE to the front hip — its lowest/widest bulk pooling at the
underside (not centred on the belly face). The bottom edge stops at ~y63 so the
locked base's feet (y65-69) poke out clean beneath it.

Two real diaper tells replace the old gift-box "+" seam: a chunky lit waistband
ribbing the TOP, and powder leg-cuff gathers notching each leg root. Bulk is
sold by puffing the silhouette proud of the belly contour with a pooled powder
shadow under the heaviest point — shape, not lines — so "padded disposable"
survives the 40px shrink. Cream-only; the pacifier keeps the whole pink budget.
"""
from __future__ import annotations
import pygame

from tools.binky_diaper_candidates._shared import (
    make_binky_build, _BB_DIAP, _BB_DIAP_HI, _BB_DIAP_SH, _BB_DIAP_LN)


def _diaper(surf):
    # Painted bulk first, tells (waistband + cuffs) on top so they stay crisp.

    # Pooled powder shadow under the heaviest underside point (~x28,y62): a low,
    # wide arc that reads as the padded mass bulging ~2px proud of the belly
    # contour, and holds the garment's value against the navy night sky. Kept
    # above y63 so it never tints the legs the base draws beneath.
    pygame.draw.ellipse(surf, _BB_DIAP_SH, (16, 55, 26, 8))

    # The cream band itself — a wrapped underside crescent, NOT a belly patch.
    # Top edge flat at the waistband (y53), bottom bulging low and wide at the
    # underside (y62), so the lowest/heaviest bulk pools beneath the belly
    # rather than sitting centred on the belly face.
    pygame.draw.ellipse(surf, _BB_DIAP, (17, 52, 25, 11))   # back-to-front wrap
    pygame.draw.ellipse(surf, _BB_DIAP, (21, 55, 18, 8))    # over-stuffed lobe
    # Flat-top the fill to the band so the waistband — not the ellipse crown —
    # is the cloth's top edge, keeping the powder-blue bib gap open above.
    pygame.draw.rect(surf, _BB_DIAP, (18, 53, 23, 3))

    # (a) WAISTBAND across the top (x18-40, y51-54): chunky 3px with a lit white
    # top edge + one rib line, the brightest cloth edge — it orients the whole
    # garment on day sky and tops the diaper like a real elastic band. Drawn
    # last over the fill so the lit run survives.
    pygame.draw.line(surf, _BB_DIAP,    (18, 54), (40, 54), 1)   # band core
    pygame.draw.line(surf, _BB_DIAP_LN, (18, 53), (40, 53), 1)   # rib line
    pygame.draw.line(surf, _BB_DIAP,    (18, 52), (40, 52), 1)   # band core
    pygame.draw.line(surf, _BB_DIAP_HI, (19, 51), (39, 51), 1)   # lit top edge

    # (b) LEG-CUFF gathers at the bottom corners — the other half of the
    # "diaper not gift-box" signal. Powder scalloped arcs hug each leg root so
    # the hem reads gathered, not a flat box edge; a 1px notch backs each so
    # the tell survives even when the 2px scallop blurs at 40px.
    for lx in (24, 33):
        pygame.draw.arc(surf, _BB_DIAP_SH, (lx, 60, 5, 5), 3.4, 6.1, 2)
        pygame.draw.line(surf, _BB_DIAP_SH, (lx + 1, 62), (lx + 3, 62), 1)
    # Front-hip tape tab anchors the band to the right edge of the wrap.
    pygame.draw.rect(surf, _BB_DIAP_HI, (38, 53, 3, 3))
    pygame.draw.line(surf, _BB_DIAP_LN, (40, 53), (40, 55), 1)


build = make_binky_build(_diaper)
