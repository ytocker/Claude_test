"""SWASHBUCKLER — the armed-for-a-fight pirate candidate (DESIGN 3 of 5).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_pirate`` is untouched.

Concept: keep the pirate IDENTITY (slate tricorn + bright-gold brim + white
skull cockade + eyepatch) but bristle it with steel. The hero silhouette-break
is a CUTLASS slung diagonally BEHIND the body — a curved steel blade whose tip
and brass guard overshoot the tail/back outline so the weapon reads against
open sky no matter how the body fills. Layered density: a leather baldric with
a big square brass buckle across the chest, and a flintlock pistol grip + curved
butt tucked at the waist near the near wing. A tiny cheek scar finishes the
fighter's face.

At 40px the read, in order of value: (1) a pirate-shaped bird, (2) the gold brim
+ white skull popping at the crown, (3) a curved steel blade behind the bird
with a hard highlight edge so it survives the downscale, and (4) the brass
buckle + pistol butt as warm metal on the body. Every steel object carries a
bright highlight edge because steel only reads as a blade if it glints.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Steel needs a bright edge or it dissolves into the sky at 40px — three values
# (shadow / body / highlight) per blade so the curve still reads after downscale.
_STEEL    = (199, 208, 218)        # #C7D0DA blade body
_STEEL_D  = (124, 135, 148)        # #7C8794 blade shadow
_STEEL_H  = (240, 245, 250)        # bright glint edge (the read at 40px)
_BRASS    = (217, 164, 65)         # #D9A441 guard / buckle
_BRASS_D  = (150, 110, 40)
_BRASS_H  = (255, 233, 168)        # #FFE9A8 buckle highlight
_WOOD     = (90, 58, 34)           # #5A3A22 grip wood
_WOOD_H   = (132, 92, 56)
_LEATHER  = (62, 42, 26)           # #3E2A1A belt leather
_LEATHER_H = (96, 68, 44)

# Pirate identity — same family as the production _paint_pirate so the read
# stays unmistakably "pirate" while the steel is layered around it.
_PIR_FELT   = (74, 78, 96)
_PIR_FELT_D = (48, 52, 70)
_PIR_FELT_H = (120, 126, 150)
_PIR_TRIM   = (255, 205, 70)
_PIR_TRIM_H = (255, 240, 160)
_PIR_GOLD   = (255, 205, 70)
_PIR_SKULL  = (244, 246, 240)
_SCAR       = (150, 60, 60)


def _curved_blade(surf, p0, ctrl, p1, color, width):
    """A quadratic-bezier polyline so the cutlass reads as a CURVED sabre, not a
    straight bar. Sampled coarse (curves survive downscale; extra points don't)."""
    pts = []
    for i in range(9):
        t = i / 8.0
        mt = 1 - t
        x = mt * mt * p0[0] + 2 * mt * t * ctrl[0] + t * t * p1[0]
        y = mt * mt * p0[1] + 2 * mt * t * ctrl[1] + t * t * p1[1]
        pts.append((x, y))
    pygame.draw.lines(surf, color, False, pts, width)
    return pts


def _paint(surf, _a):
    # ── CUTLASS slung diagonally BEHIND the body (painted first so it reads as
    #    behind the bird — only the parts that overshoot the silhouette survive
    #    where the body would otherwise cover them). Hilt sits low-front near the
    #    near wing/waist; the curved blade sweeps up-and-back past the tail so the
    #    tip + guard break the outline against the sky. Three steel values give
    #    the curve a bright highlight edge that reads at 40px.
    hilt = (HX - 2, HY + 24)          # brass guard, at the waist (near wing)
    btip = (HX - 33, CROWN_Y - 6)     # blade tip, up past the tail/back outline
    bctrl = (HX - 28, HY + 8)         # control pulls the belly of the curve down-left
    # Shadow underlay (widest) so the bright blade has a dark edge against sky.
    _curved_blade(surf, hilt, bctrl, btip, _STEEL_D, 6)
    _curved_blade(surf, hilt, bctrl, btip, _STEEL, 4)
    # Bright back-edge of the blade — the single highest-value glint that makes
    # steel read as a weapon at 40px. Offset toward the spine of the curve.
    hi0 = (hilt[0] - 2, hilt[1] - 2)
    hictrl = (bctrl[0] - 3, bctrl[1] - 3)
    hi1 = (btip[0] + 1, btip[1] - 1)
    _curved_blade(surf, hi0, hictrl, hi1, _STEEL_H, 2)
    # Sharp steel tip cap so the point overshoots cleanly.
    _poly(surf, _STEEL_H, [(btip[0] - 1, btip[1] - 3), (btip[0] + 4, btip[1] + 1),
                           (btip[0] - 2, btip[1] + 2)])

    # Brass D-guard + grip at the hilt — warm metal anchoring the low end of the
    # diagonal so the weapon reads as carried, not floating.
    gx, gy = hilt
    pygame.draw.line(surf, _BRASS_D, (gx - 5, gy - 5), (gx + 5, gy + 5), 5)
    pygame.draw.line(surf, _BRASS, (gx - 5, gy - 5), (gx + 5, gy + 5), 3)
    pygame.draw.line(surf, _BRASS_H, (gx - 4, gy - 5), (gx + 2, gy - 1), 1)
    # Curved knuckle-bow of the D-guard sweeping below the grip.
    pygame.draw.arc(surf, _BRASS, (gx - 2, gy - 1, 12, 13),
                    math.radians(40), math.radians(200), 3)
    # Wrapped wooden grip below the guard.
    pygame.draw.line(surf, _WOOD, (gx + 3, gy + 4), (gx + 9, gy + 12), 5)
    pygame.draw.line(surf, _WOOD_H, (gx + 4, gy + 5), (gx + 8, gy + 11), 1)
    pygame.draw.circle(surf, _BRASS, (gx + 10, gy + 13), 2)   # pommel cap

    # ── LEATHER BALDRIC across the chest (over the body) with a big square brass
    #    buckle. Body centre ~(32, 52); the strap runs shoulder-to-hip diagonally.
    s0 = (HX - 4, HY + 10)            # up at the near shoulder
    s1 = (HX - 26, HY + 26)           # down toward the off hip
    pygame.draw.line(surf, _LEATHER, s0, s1, 6)
    pygame.draw.line(surf, _LEATHER_H, (s0[0] - 1, s0[1] + 1), (s1[0] - 1, s1[1] + 1), 1)
    # Big square brass buckle centred on the strap — warm metal on the body.
    bkx, bky = (HX - 14), (HY + 18)
    pygame.draw.rect(surf, _BRASS_D, (bkx - 5, bky - 5, 11, 11), border_radius=2)
    pygame.draw.rect(surf, _BRASS, (bkx - 4, bky - 4, 9, 9), border_radius=2)
    pygame.draw.rect(surf, _LEATHER, (bkx - 2, bky - 2, 5, 5))      # buckle window
    pygame.draw.line(surf, _BRASS_H, (bkx - 4, bky - 4), (bkx + 4, bky - 4), 2)

    # ── FLINTLOCK pistol tucked at the waist near the near wing — a curved wooden
    #    butt + a hint of brass barrel/lock poking up so the body bristles with a
    #    second weapon. Sits forward of the baldric so both read.
    pgx, pgy = HX + 7, HY + 20
    # Curved wooden grip/butt.
    _poly(surf, _WOOD, [(pgx, pgy - 2), (pgx + 7, pgy + 2), (pgx + 6, pgy + 9),
                        (pgx + 1, pgy + 8), (pgx - 1, pgy + 3)])
    pygame.draw.line(surf, _WOOD_H, (pgx + 1, pgy), (pgx + 4, pgy + 7), 1)
    # Brass butt-cap + a short barrel/lock hint angled up out of the belt.
    pygame.draw.circle(surf, _BRASS, (pgx + 5, pgy + 8), 2)
    pygame.draw.line(surf, _STEEL_D, (pgx + 1, pgy - 1), (pgx - 4, pgy - 7), 4)
    pygame.draw.line(surf, _STEEL, (pgx + 1, pgy - 1), (pgx - 4, pgy - 7), 2)
    pygame.draw.line(surf, _STEEL_H, (pgx, pgy - 2), (pgx - 4, pgy - 7), 1)
    pygame.draw.circle(surf, _BRASS, (pgx, pgy + 1), 2)            # lock plate

    # ── PIRATE IDENTITY (the anchor read) — earring, eyepatch, tricorn, gold
    #    brim, skull cockade. Same family as production so it stays "pirate".
    # Gold hoop earring under the head.
    pygame.draw.circle(surf, _PIR_GOLD, (HX - 8, HY + 10), 3, 2)
    pygame.draw.circle(surf, _PIR_TRIM_H, (HX - 9, HY + 9), 1)

    # Eyepatch over the NEAR (right) eye + a strap up over the crown.
    pygame.draw.line(surf, _PIR_FELT_D, (HX + 11, HY - 2), (HX - 6, CROWN_Y), 2)
    pygame.draw.ellipse(surf, _PIR_FELT_D, (HX + 6, HY - 5, 9, 9))
    pygame.draw.ellipse(surf, _PIR_FELT, (HX + 7, HY - 4, 7, 7))

    # Tiny cheek scar hint just below the patched eye — the fighter's face.
    pygame.draw.line(surf, _SCAR, (HX + 9, HY + 5), (HX + 11, HY + 9), 2)
    pygame.draw.line(surf, _PIR_SKULL, (HX + 9, HY + 5), (HX + 10, HY + 7), 1)

    # Tricorn lifted a row higher so the brim breaks the crown outline.
    cy = CROWN_Y - 3
    brim = [(HX - 17, cy + 5), (HX - 5, cy - 7), (HX + 4, cy - 8),
            (HX + 16, cy + 4), (HX + 6, cy + 9), (HX - 6, cy + 9)]
    pygame.draw.polygon(surf, _PIR_FELT_D, brim)
    inner = [(HX - 14, cy + 4), (HX - 4, cy - 5), (HX + 3, cy - 6),
             (HX + 13, cy + 3), (HX + 5, cy + 7), (HX - 5, cy + 7)]
    pygame.draw.polygon(surf, _PIR_FELT, inner)
    pygame.draw.polygon(surf, _PIR_FELT_H, [(HX - 4, cy - 5), (HX + 3, cy - 6),
                                            (HX + 2, cy - 2), (HX - 3, cy - 2)])
    # One continuous bright gold band tracing the whole brim edge — the read.
    band = [(HX - 15, cy + 4), (HX - 4, cy - 5), (HX + 3, cy - 6), (HX + 14, cy + 3)]
    pygame.draw.lines(surf, _PIR_TRIM, False, band, 2)
    pygame.draw.lines(surf, _PIR_TRIM_H, False,
                      [(HX - 13, cy + 3), (HX - 4, cy - 6), (HX + 3, cy - 7)], 1)
    # Big white skull cockade dead-centre-front.
    sx, sy = HX, cy + 1
    pygame.draw.circle(surf, _PIR_SKULL, (sx, sy), 4)
    pygame.draw.polygon(surf, _PIR_SKULL, [(sx - 3, sy + 2), (sx + 3, sy + 2),
                                           (sx + 1, sy + 5), (sx - 1, sy + 5)])
    pygame.draw.circle(surf, (40, 30, 40), (sx - 2, sy - 1), 1)
    pygame.draw.circle(surf, (40, 30, 40), (sx + 2, sy - 1), 1)


build = store_skins._make_skin(_paint)
