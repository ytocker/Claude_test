"""DESIGN 4 — SAGGY LOAD: the comedy heavy nappy.

Reads as a worn low-rise nappy that droops at the back rump for a cute
"heavy/full" baby read. The front waistband stays HIGH and snug across the
hip/belly (y53-55) while a cream pouch sags down-and-back behind, bulging
lowest at (18,63). The droop sits back-LEFT of the legs, so its rounded
bottom stays clear of the leg roots (y65) and the legs still poke through
clean — the asymmetric rump sag is the charm, never a tub Pip sits in.

A `#C9D9DE` deep-shadow pool under the heaviest point sells "full", and the
`#ABA282` sag crease + powder underside hold the cream's value on navy night;
the lit white front waistband carries the day top read.
"""
from __future__ import annotations
import pygame

from tools.binky_diaper_candidates._shared import (
    make_binky_build, _BB_DIAP, _BB_DIAP_HI, _BB_DIAP_SH, _BB_DIAP_LN)


def _diaper(surf):
    # Build back-to-front: the heavy rear pouch first (so the front waistband
    # and crotch gusset read crisp over it), with the lowest bulge kept at y64
    # and pulled back-LEFT of the leg column (x26-36) so legs stay visible.

    # Drooping rear lobe — a cream pouch sagging down-and-back over the rump.
    # The off-centre, rounder lower-left mass is the comedy "full" silhouette;
    # its bottom rounds at y64 (1px above the leg roots) and sits left of x26
    # so it never crowds the legs. Powder base reads as the shadowed underbelly.
    pygame.draw.ellipse(surf, _BB_DIAP_SH, (13, 55, 16, 10))
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (14, 54, 14, 10))
    pygame.draw.ellipse(surf, _BB_DIAP,    (14, 54, 13, 9))
    # A second lower bulge tucked down-left exaggerates the heavy sag without
    # reaching the legs — the heaviest point pools at (18,63).
    pygame.draw.ellipse(surf, _BB_DIAP,    (15, 58, 9, 6))

    # Deep-shadow pool under the heaviest point — the value anchor that sells
    # "full" and keeps the sagging lobe from voiding flat against navy night.
    pygame.draw.ellipse(surf, _BB_DIAP_SH, (16, 60, 7, 4))
    pygame.draw.arc(surf, _BB_DIAP_SH, (14, 59, 11, 6), 3.5, 6.05, 2)

    # Front waistband — a snug lit band across the front hip/belly that stays
    # HIGH (y53-55) while the rear sags, so the silhouette reads off-balance
    # (the whole point) rather than uniformly low like the old tub.
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (24, 53, 18, 7))
    pygame.draw.ellipse(surf, _BB_DIAP,    (24, 53, 17, 6))
    pygame.draw.arc(surf, _BB_DIAP_HI, (24, 52, 17, 6), 3.35, 6.05, 2)
    # Seam just under the waistband — second night-value tell up front.
    pygame.draw.arc(surf, _BB_DIAP_LN, (24, 54, 17, 5), 3.5, 6.0, 1)

    # Sag crease — one curved `#ABA282` fold riding across the droop where the
    # heavy cloth bunches; the read that says "sagging", not just "round".
    pygame.draw.arc(surf, _BB_DIAP_LN, (15, 56, 11, 8), 3.45, 5.95, 1)

    # Crotch fold — a short cream gusset dipping between the leg roots, tying
    # the high front to the low rear. Kept to y64 max so the legs clear below.
    pygame.draw.ellipse(surf, _BB_DIAP_LN, (28, 59, 7, 6))
    pygame.draw.ellipse(surf, _BB_DIAP,    (28, 59, 6, 5))
    pygame.draw.line(surf, _BB_DIAP_LN, (31, 60), (31, 63), 1)

    # Leg-cuff shades — short powder arcs hugging each leg root so the legs
    # read as poking *through* the nappy, framing the gap below the sag.
    pygame.draw.arc(surf, _BB_DIAP_SH, (25, 61, 6, 6), 3.3, 6.1, 2)
    pygame.draw.arc(surf, _BB_DIAP_SH, (33, 61, 6, 6), 3.3, 6.1, 2)


build = make_binky_build(_diaper)
