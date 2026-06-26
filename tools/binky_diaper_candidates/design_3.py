"""PINNED TERRY — the folded terry-cloth triangle, pinned at the hips (design_3).

A classic folded-square cloth nappy: a flat top waist edge across the hips (y53)
folding down to a pointed crotch, with the two hard diagonal fold lines and a
fastening pin that are the heritage tell. The whole cloth sits ABOVE the scaffold
legs — nothing cream below y62 — so the two chubby legs poke out clean beneath a
banded cream nappy at icon size.

Cream cloth only; the pacifier keeps the pink budget except ONE sub-pixel pin
head (<=2px) on the front hip tab. The diagonal folds are held to 2px so they
survive the 40px downscale, and a hard lower seam + powder-shadow underside anchor
the cream's value against navy night.
"""
from __future__ import annotations
import pygame

from tools.binky_diaper_candidates._shared import (
    make_binky_build, _BB_DIAP, _BB_DIAP_HI, _BB_DIAP_SH, _BB_DIAP_LN, _BB_PINK)


def _diaper(surf):
    # Folded-triangle body: flat top waist edge x18-40 at y53, tapering to a
    # crotch point at (30,61) — the hard floor, nothing cream below it so the
    # scaffold legs (y62+) always emerge clean. Drawn as a polygon (not an
    # ellipse) so the pointed underside reads as folded cloth, not a pad. The
    # darker line tone gives a 1px contour; the cream fills inside it.
    pygame.draw.polygon(surf, _BB_DIAP_LN, [(18, 53), (40, 53), (35, 59), (30, 61), (25, 59)])
    pygame.draw.polygon(surf, _BB_DIAP,    [(19, 54), (39, 54), (34, 59), (30, 60), (26, 59)])

    # Rear wrap point — a smaller cream triangle carried back over the rump so
    # the nappy reads as wrapping round behind, not just a front panel.
    pygame.draw.polygon(surf, _BB_DIAP_LN, [(15, 54), (24, 53), (23, 58)])
    pygame.draw.polygon(surf, _BB_DIAP,    [(16, 54), (23, 54), (22, 57)])

    # Powder-shadow along the lower fold edges (y59-61) — the value anchor that
    # keeps the cream point from voiding flat against navy night. Stays at/above
    # y61 so no powder bleeds into the leg zone.
    pygame.draw.line(surf, _BB_DIAP_SH, (25, 59), (30, 61), 2)
    pygame.draw.line(surf, _BB_DIAP_SH, (30, 61), (35, 59), 2)

    # Hard bottom seam — a 1px edge along the cloth's lower fold so the nappy
    # visibly ENDS here, reading as a banded hem the legs drop out beneath.
    pygame.draw.line(surf, _BB_DIAP_LN, (25, 60), (30, 61), 1)
    pygame.draw.line(surf, _BB_DIAP_LN, (30, 61), (35, 60), 1)

    # Diagonal fold lines (the heritage signature) — from the back-left rump and
    # the front hip down to the crotch point. Kept 2px so they stay legible after
    # the 40px downscale rather than softening into the cream.
    pygame.draw.line(surf, _BB_DIAP_LN, (18, 54), (30, 61), 2)
    pygame.draw.line(surf, _BB_DIAP_LN, (40, 54), (30, 61), 2)

    # Lit waist edge — a flat highlight across the top fold, the crisp folded-
    # cloth top line that carries the day read against bright sky.
    pygame.draw.line(surf, _BB_DIAP_HI, (20, 53), (38, 53), 2)

    # Hip pin tabs — small white squares pinching the cloth at each hip. The
    # back tab is plain; the front tab carries the lone pink pin head.
    pygame.draw.rect(surf, _BB_DIAP_LN, (18, 51, 4, 4))
    pygame.draw.rect(surf, _BB_DIAP_HI, (19, 52, 2, 2))
    pygame.draw.rect(surf, _BB_DIAP_LN, (37, 51, 4, 4))
    pygame.draw.rect(surf, _BB_DIAP_HI, (38, 52, 2, 2))
    # The fastening pin head — the single sanctioned cloth-pink, kept sub-pixel
    # so it never competes with the pacifier hero.
    pygame.draw.circle(surf, _BB_PINK, (39, 53), 1)


build = make_binky_build(_diaper)
