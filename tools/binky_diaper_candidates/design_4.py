"""DESIGN 4 — SAGGY LOAD: the comedy heavy nappy.

Reads as a worn low-rise nappy whose rear rump lobe droops down-and-back for a
cute "heavy/full" baby read. The front waistband stays HIGH and snug across the
hip/belly (y53-55) while a cream pouch sags behind, biased back-LEFT (x14-22) so
the heaviness is asymmetric — an off-balance rump sag, never a tub Pip sits in.

The lobe now hard-caps at y61: the scaffold draws chubby legs over the cloth at
x28 & x35 (y62 down), so the cloth must END above them. A 1px `#ABA282` seam runs
the lobe's lower edge at y61 to read that hard end, a `#C9D9DE` shadow pool under
the heaviest point (~18,60) sells "full", and the `#ABA282` sag crease + powder
underside hold the cream's value on navy night while the lit white front
waistband carries the day top read.
"""
from __future__ import annotations
import pygame

from tools.binky_diaper_candidates._shared import (
    make_binky_build, _BB_DIAP, _BB_DIAP_HI, _BB_DIAP_SH, _BB_DIAP_LN)


def _diaper(surf):
    # Build back-to-front: the heavy rear pouch first (so the front waistband
    # reads crisp over it). Every cream/powder pixel stays at y61 or above so the
    # scaffold legs (x28 & x35, y62 down) poke out clean below an ended hem.

    # Powder underside first — a shadowed base that gives the lobe navy-night
    # hold and reads as the under-curve of the heavy sag. Kept up at y52-61.
    pygame.draw.ellipse(surf, _BB_DIAP_SH, (13, 52, 16, 9))

    # Drooping rear lobe — a cream pouch sagging down-and-back over the rump,
    # mass biased back-LEFT (x14-22) for the asymmetric comedy "full" read. Its
    # rounded bottom rounds out at y61, well left of the leg column (x28-35).
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (13, 51, 15, 10))
    pygame.draw.ellipse(surf, _BB_DIAP,    (14, 51, 13, 9))
    # A second lower-left bulge exaggerates the heavy sag; its lowest cream pixel
    # bottoms at y61 (the hard cap) and never reaches past x22 toward the legs.
    pygame.draw.ellipse(surf, _BB_DIAP,    (14, 55, 9, 6))

    # Deep-shadow pool under the heaviest point — the value anchor that sells
    # "full" and keeps the sagging lobe from voiding flat against navy night.
    pygame.draw.ellipse(surf, _BB_DIAP_SH, (16, 57, 7, 4))
    pygame.draw.arc(surf, _BB_DIAP_SH, (15, 56, 10, 5), 3.5, 6.05, 2)

    # Hard bottom seam — a 1px `#ABA282` edge riding the lobe's lower curve at
    # ~y61 so the cloth visibly ENDS above the legs (the hard cap made legible).
    pygame.draw.arc(surf, _BB_DIAP_LN, (13, 56, 13, 6), 3.45, 6.0, 1)

    # Front waistband — a snug lit band across the front hip/belly that stays
    # HIGH (y53-55) while the rear sags, so the silhouette reads off-balance
    # (the whole point) rather than uniformly low like the old tub.
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (24, 53, 18, 6))
    pygame.draw.ellipse(surf, _BB_DIAP,    (24, 53, 17, 5))
    pygame.draw.arc(surf, _BB_DIAP_HI, (24, 52, 17, 5), 3.35, 6.05, 2)
    # Seam just under the waistband — second night-value tell up front.
    pygame.draw.arc(surf, _BB_DIAP_LN, (24, 54, 17, 4), 3.5, 6.0, 1)

    # Sag crease — one curved `#ABA282` fold riding across the droop where the
    # heavy cloth bunches (x16-24, y58); the read that says "sagging", not "round".
    pygame.draw.arc(surf, _BB_DIAP_LN, (15, 54, 11, 7), 3.45, 5.95, 1)

    # Crotch fold — a short cream gusset dipping between the waistband and lobe,
    # tying the high front to the low rear. Kept up at y59 so the leg tops stay
    # clear and the legs read as poking *through* below it.
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (26, 55, 7, 5))
    pygame.draw.ellipse(surf, _BB_DIAP,    (26, 55, 6, 4))


build = make_binky_build(_diaper)
