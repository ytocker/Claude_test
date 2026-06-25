"""SWASHBUCKLER — the armed-for-a-fight pirate candidate (DESIGN 3 of 5).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_pirate`` is untouched.

Concept: keep the pirate IDENTITY (slate tricorn + bright-gold brim + white
skull cockade + eyepatch) but bristle it with steel. The hero silhouette-break
is a CUTLASS slung diagonally BEHIND the body — a curved steel blade whose tip
and brass guard overshoot the tail/back outline so the weapon reads against
open sky no matter how the body fills. The lower body is kept deliberately
sparse — body + ONE clean baldric buckle + the cutlass hilt, three things not
seven — so the blade stays the hero and nothing collapses into mud at 40px. A
tiny cheek scar finishes the fighter's face.

At 40px the read, in order of value: (1) a pirate-shaped bird, (2) the gold brim
+ white skull popping at the crown, (3) a curved steel blade behind the bird
with a hard highlight edge so it survives the downscale, and (4) a single warm
brass buckle on a raised-value baldric strap crossing the chest. Every steel
object carries a bright highlight edge because steel only reads as a blade if it
glints.
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
_LEATHER  = (62, 42, 26)           # #3E2A1A belt leather
_LEATHER_H = (96, 68, 44)          # raised baldric body — reads on dark-blue lower body
_LEATHER_HH = (132, 100, 66)       # baldric top-edge glint so the strap reads as a line

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
    # Shorter, stubbier hanger — tip pulled IN toward the body and down so the
    # blade is ~a third shorter, yet still overshoots the back/tail outline.
    btip = (HX - 22, CROWN_Y - 2)     # blade tip, still past the back outline
    bctrl = (HX - 19, HY + 6)         # control keeps the curved-sabre belly
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

    # Simplified hilt where the blade meets the body — let the BLADE be the hero,
    # so this is just a bright brass guard-cross + ONE short grip stub. A crowded
    # D-guard + wrapped grip + pommel collapsed into mud at 40px; three clean marks
    # (cross / stub / glint) read as "hilt" without competing with the cutlass.
    gx, gy = hilt
    # Bright brass guard-cross — the warm anchor that says "this end is the handle".
    pygame.draw.line(surf, _BRASS_D, (gx - 5, gy - 4), (gx + 5, gy + 4), 4)
    pygame.draw.line(surf, _BRASS, (gx - 5, gy - 4), (gx + 5, gy + 4), 2)
    pygame.draw.line(surf, _BRASS_H, (gx - 4, gy - 4), (gx + 1, gy), 1)
    # ONE short grip stub below the cross; pommel kept ≥2px and pushed clear of the
    # body edge so it reads as a separate dot, not a smear on the silhouette.
    pygame.draw.line(surf, _WOOD, (gx + 4, gy + 3), (gx + 8, gy + 9), 4)
    pygame.draw.circle(surf, _BRASS, (gx + 9, gy + 11), 2)   # pommel cap

    # ── LEATHER BALDRIC across the chest (over the body). Raised TWO value steps so
    #    the diagonal strap survives against the dark-blue lower body at 40px — a
    #    dark strap on a dark body just vanished. Body centre ~(32, 52); the strap
    #    runs shoulder-to-hip diagonally.
    s0 = (HX - 4, HY + 10)            # up at the near shoulder
    s1 = (HX - 26, HY + 26)           # down toward the off hip
    pygame.draw.line(surf, _LEATHER_H, s0, s1, 6)
    pygame.draw.line(surf, _LEATHER_HH, (s0[0] - 1, s0[1] + 1), (s1[0] - 1, s1[1] + 1), 1)
    # ONE clean brass buckle — shrunk ~25% (≈8px), dark leather window dropped for a
    # 1px brass cross + a brightened top glint so it reads as a glint of metal, not a
    # black hole punched in the body.
    bkx, bky = (HX - 14), (HY + 18)
    pygame.draw.rect(surf, _BRASS_D, (bkx - 4, bky - 4, 8, 8), border_radius=2)
    pygame.draw.rect(surf, _BRASS, (bkx - 3, bky - 3, 6, 6), border_radius=2)
    pygame.draw.line(surf, _BRASS_D, (bkx, bky - 3), (bkx, bky + 3), 1)   # brass cross
    pygame.draw.line(surf, _BRASS_D, (bkx - 3, bky), (bkx + 3, bky), 1)
    pygame.draw.line(surf, _BRASS_H, (bkx - 3, bky - 3), (bkx + 2, bky - 3), 2)

    # ── CLASSIC WOODEN PEG LEG over the NEAR foot. The base foot is only ~2px so
    #    the peg is drawn chunkier (3-4px) to survive downscale, and pokes below the
    #    body to break the lower silhouette. Far foot is left as a normal foot.
    px, ptop, pbot = 26, 65, 78
    pygame.draw.line(surf, _LEATHER, (px - 1, ptop), (px - 1, pbot), 1)   # shadow side
    pygame.draw.line(surf, _WOOD, (px, ptop), (px, pbot - 1), 4)          # peg body
    pygame.draw.line(surf, _WOOD, (px, pbot - 1), (px, pbot), 2)          # whittled tip
    pygame.draw.line(surf, _LEATHER_H, (px + 1, ptop + 1), (px + 1, pbot - 2), 1)  # glint
    pygame.draw.line(surf, _LEATHER, (px - 2, ptop), (px + 2, ptop), 2)   # ferrule at body

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
    # Big white skull cockade dead-centre-front. Eyes pulled tighter together and
    # the jaw shortened a touch so the hero read isn't a wide-eyed surprised face.
    sx, sy = HX, cy + 1
    pygame.draw.circle(surf, _PIR_SKULL, (sx, sy), 4)
    pygame.draw.polygon(surf, _PIR_SKULL, [(sx - 2, sy + 2), (sx + 2, sy + 2),
                                           (sx + 1, sy + 4), (sx - 1, sy + 4)])
    pygame.draw.circle(surf, (40, 30, 40), (sx - 1, sy - 1), 1)
    pygame.draw.circle(surf, (40, 30, 40), (sx + 1, sy - 1), 1)


build = store_skins._make_skin(_paint)
