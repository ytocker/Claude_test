"""FOLD-OVER FRONT — a structured nappy BAND with a turned-down waistband (design_5).

The earlier take sat the cloth as a flat front slab that swallowed the legs.
This wraps a NAPPY BAND round the rump + lower belly (y52-61): an enlarged rear
lobe carries the cloth around behind the body, the underside connects back-lobe
to front-panel as one continuous band, and a hard horizontal seam under the
turned-down front waistband stays the architectural tell at 40px. The cloth ENDS
at a hard bottom edge ~y61 so the scaffold's chubby legs read as poking out
below — nothing cream descends past y61.

Cream cloth only — the pacifier keeps the entire pink budget. The `#ABA282`
seam plus `#C9D9DE` powder-shadow underside hold value against navy; the lit
`#FFFFFF` panel top carries the bright-day read.
"""
from __future__ import annotations
import pygame

from tools.binky_diaper_candidates._shared import (
    make_binky_build, _BB_DIAP, _BB_DIAP_HI, _BB_DIAP_SH, _BB_DIAP_LN)


def _diaper(surf):
    # The whole nappy is a BAND capped at y61 so the scaffold legs (y62+) clear.

    # Rear wrap — an enlarged rump lobe back-left so the cloth visibly turns the
    # corner behind the body rather than reading as a front-only panel.
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (13, 52, 13, 9))
    pygame.draw.ellipse(surf, _BB_DIAP,    (14, 53, 11, 7))
    # A powder shadow seam along the rump's lower-back edge sells the wrap — the
    # eye reads cloth continuing around behind the body, not a flat slab.
    pygame.draw.line(surf, _BB_DIAP_SH, (15, 59), (24, 59), 2)

    # Underside band — the cream that connects the rear lobe to the front panel
    # across the belly's underside, so back + front read as ONE continuous band.
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (22, 55, 18, 6))
    pygame.draw.ellipse(surf, _BB_DIAP,    (23, 56, 16, 4))

    # Fold-over front panel — the signature flap turned down across the front
    # belly, narrowed ~2px from before so a powder-blue belly gap stays visible
    # above it. Drawn as a filled rect so the seam is a crisp horizontal line.
    pygame.draw.rect(surf, _BB_DIAP, (25, 53, 15, 4))
    # Panel top — lit white waistband edge carrying the bright-day top read.
    pygame.draw.line(surf, _BB_DIAP_HI, (26, 53), (39, 53), 1)
    # Panel bottom — the crisp turned-down seam, the architectural 40px tell.
    pygame.draw.line(surf, _BB_DIAP_LN, (25, 57), (40, 57), 2)

    # Tape strip — a short vertical closure tick above the seam (not a crosshair),
    # the detail that says "fastened nappy" rather than "folded towel".
    pygame.draw.line(surf, _BB_DIAP_LN, (32, 53), (32, 56), 2)

    # Hard bottom edge — the cloth visibly ENDS here, above the legs, so the band
    # reads as a nappy hem rather than dissolving into the body.
    pygame.draw.line(surf, _BB_DIAP_LN, (24, 61), (39, 61), 2)
    # Powder-shadow underside just inside the hem — the navy value-hold anchor,
    # the cloth curving under the belly. Stays above y62 so legs read clean.
    pygame.draw.line(surf, _BB_DIAP_SH, (25, 60), (38, 60), 1)


build = make_binky_build(_diaper)
