"""PINNED TERRY — the folded terry-cloth triangle, pinned at the hips (design_3).

The shipped diaper sat at cy~64, down among the leg roots, so it read as a tub
BINKY sits in. This take wraps a classic folded-square terry nappy: a flat top
waist edge across the hips (y53) tapering to a pointed crotch (y63), with the
folded-cloth's signature diagonal fold lines and a fastening pin at the hip.
Everything stays above the legs (y65+) so they poke out clean at the base
corners.

Cream cloth only — the pacifier keeps the pink budget, except ONE sub-pixel pin
head (<=2px) on the front hip tab, the heritage detail this concept turns on.
The diagonal fold lines are kept hard (>=2px) so they survive the 40px
downscale; the powder-shadow underside + seam hold the cream's value on navy.
"""
from __future__ import annotations
import pygame

from tools.binky_diaper_candidates._shared import (
    make_binky_build, _BB_DIAP, _BB_DIAP_HI, _BB_DIAP_SH, _BB_DIAP_LN, _BB_PINK)


def _diaper(surf):
    # Folded-triangle body: flat top waist edge x18-40 at y53 tapering to a
    # crotch point near (30,63). Drawn as a filled polygon (not an ellipse) so
    # the pointed underside reads as folded cloth, not a rounded pad. The outer
    # line tone gives a 1px contour all round; the cream fills inside it.
    body_pts = [(18, 54), (40, 54), (37, 60), (30, 63), (24, 60)]
    pygame.draw.polygon(surf, _BB_DIAP_LN, body_pts)
    pygame.draw.polygon(surf, _BB_DIAP,
                        [(19, 54), (39, 54), (36, 60), (30, 62), (25, 60)])

    # Rear wrap point — a smaller cream triangle carried back over the rump so
    # the nappy reads as wrapping round behind, not just a front panel.
    pygame.draw.polygon(surf, _BB_DIAP_LN, [(15, 54), (24, 53), (23, 59)])
    pygame.draw.polygon(surf, _BB_DIAP,    [(16, 54), (23, 54), (22, 58)])

    # Underside powder-shadow along the lower fold edges (y61-63) — the value
    # anchor that keeps the cream point from voiding flat against navy night.
    pygame.draw.line(surf, _BB_DIAP_SH, (25, 61), (30, 63), 2)
    pygame.draw.line(surf, _BB_DIAP_SH, (30, 63), (36, 60), 2)

    # Diagonal fold lines (the heritage signature) — from the back-left rump and
    # front hip down to the crotch point. Kept to 2px so they stay legible after
    # the 40px downscale rather than softening into the cream.
    pygame.draw.line(surf, _BB_DIAP_LN, (18, 54), (30, 63), 2)
    pygame.draw.line(surf, _BB_DIAP_LN, (40, 54), (30, 63), 2)

    # Lit waist edge — a flat highlight across the top fold, the crisp folded-
    # cloth top line that carries the day read against bright sky.
    pygame.draw.line(surf, _BB_DIAP_HI, (20, 53), (38, 53), 2)

    # Hip pin tabs — small white squares pinching the cloth at each hip. The
    # back tab is plain; the front tab carries the lone pink pin head.
    pygame.draw.rect(surf, _BB_DIAP_LN, (18, 52, 4, 4))
    pygame.draw.rect(surf, _BB_DIAP_HI, (19, 53, 2, 2))
    pygame.draw.rect(surf, _BB_DIAP_LN, (37, 52, 4, 4))
    pygame.draw.rect(surf, _BB_DIAP_HI, (38, 53, 2, 2))
    # The fastening pin head — the single sanctioned cloth-pink, kept sub-pixel
    # so it never competes with the pacifier hero.
    pygame.draw.circle(surf, _BB_PINK, (39, 54), 1)

    # Leg-gap cuff shades — powder arcs framing the wide base corners where the
    # legs emerge, so the legs read as poking *through* the nappy, not under a
    # slab. Sits at the (26,63)/(35,63) corners called out in the spec.
    pygame.draw.arc(surf, _BB_DIAP_SH, (23, 60, 7, 6), 3.4, 6.0, 2)
    pygame.draw.arc(surf, _BB_DIAP_SH, (33, 60, 7, 6), 3.4, 6.0, 2)


build = make_binky_build(_diaper)
