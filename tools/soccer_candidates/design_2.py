"""DESIGN 2 — THE GOALKEEPER (Soccer / Football).

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted as a goalkeeper: the read is carried by two OVERSIZED
padded keeper GLOVES on both wing-hands — big rounded mitts with finger ridges
and a wrist strap, drawn LAST so they sit proud in front of the body and break
the silhouette. They are the design's signature, the furthest read from a
basketball tank. Backing them up: a lurid high-vis NEON-GREEN keeper jersey
(deliberately off-team) with a dark shoulder yoke + long sleeves, short shorts,
short socks + cleats at the feet, and a soft short-brim cap at the crown.

The kit is painted OVER the scarlet body (the head stays the macaw so Pip still
reads as a parrot). The footprint law: the gloves may break the OUTLINE as held
props, but nothing balloons the torso or drops below the feet line — socks +
cleats sit on the feet line (~HY+15..27).

Headless render: tools/soccer_candidates/render_design_2.py.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# High-vis NEON green is the deliberate "keeper is a different colour" tell;
# three jersey values so the long sleeves + yoke separate after the downscale.
_GK_HV     = (25, 195, 125)         # #19C37D high-vis green jersey
_GK_HV_D   = (16, 120, 78)          # jersey shadow / sleeve seam
_GK_HV_H   = (96, 232, 168)         # jersey highlight / sleeve top
_GK_YOKE   = (14, 26, 20)           # #0E1A14 dark shoulder yoke / gloves trim
_GK_YOKE_H = (40, 60, 50)           # yoke edge sheen

# Three glove values so the padding reads round at 40px (the hero shapes).
_GK_GLOVE   = (244, 244, 248)       # #F4F4F8 white glove body
_GK_GLOVE_D = (176, 182, 196)       # glove core shadow (rounds the padding)
_GK_GLOVE_H = (255, 255, 255)       # glove crown highlight

_GK_CAP    = (27, 42, 107)          # #1B2A6B cap navy
_GK_CAP_H  = (60, 84, 168)          # cap crown highlight
_GK_CAP_D  = (16, 26, 70)           # cap brim shadow

_GK_CLEAT   = (35, 37, 46)          # #23252E cleat boot
_GK_CLEAT_H = (78, 84, 102)         # cleat upper highlight
_GK_SOCK    = (14, 26, 20)          # short sock (matches yoke/trim)
_GK_SOCK_H  = (40, 60, 50)


# Body centre in composite space (parrot body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52


def _glove(surf, cx, cy, flip):
    """One oversized padded keeper mitt centred on a wing-hand. `flip` is +1 for
    the near (right) hand, -1 for the far (left) hand, so the cuff/strap and the
    light always fall the same way on both. Built fill→shade→ridges→outline→
    highlight so the padding reads ROUND at 40px and stays the hero shape."""
    f = flip
    # Padded mitt body — a tall rounded shape, slightly wider at the palm and
    # tapering to the fingertips. Drawn as a filled polygon so it can break the
    # body outline cleanly without ballooning the torso. The body-facing inner
    # edge is pulled in 1px (toward the torso centre) to reveal more neon chest
    # at 40px: near glove (f>0) bodies on its LEFT edge, far glove on its RIGHT.
    il = 1 if f > 0 else 0              # near glove: tuck the left edge in
    ir = 1 if f < 0 else 0             # far glove: tuck the right edge in
    mitt = [(cx - 8 + il, cy - 1), (cx - 7, cy - 8), (cx - 2, cy - 11),
            (cx + 4, cy - 11), (cx + 8, cy - 7), (cx + 9 - ir, cy + 2),
            (cx + 7, cy + 8), (cx + 1, cy + 10), (cx - 5, cy + 9),
            (cx - 8 + il, cy + 4)]
    pygame.draw.polygon(surf, _GK_GLOVE, mitt)
    # Core shadow on the cuff side rounds the padding (3-value read).
    pygame.draw.ellipse(surf, _GK_GLOVE_D,
                        (cx - 7 if f > 0 else cx - 2, cy - 3, 9, 12))
    pygame.draw.polygon(surf, _GK_GLOVE, mitt)  # restore body over the shade pool
    pygame.draw.ellipse(surf, _GK_GLOVE_D,
                        (cx + (2 * f) - 4, cy + 1, 8, 8))  # palm-heel shadow

    # Finger ridges — TWO bold near-black grooves up the back of the mitt at
    # wide ~5px spacing so the "padded glove" read holds at 40px. Fewer/deeper
    # grooves survive the downscale where three thin mid-grey lines turn to mud.
    for i in range(2):
        gx = cx - 2 + i * 5
        pygame.draw.line(surf, _GK_YOKE, (gx, cy - 10), (gx, cy + 2), 2)
        pygame.draw.circle(surf, _GK_GLOVE_H, (gx + 1, cy - 9), 1)
    # Thumb pad bulging off the palm side.
    pygame.draw.circle(surf, _GK_GLOVE, (cx - 7 * f, cy + 2), 4)
    pygame.draw.circle(surf, _GK_GLOVE_D, (cx - 7 * f, cy + 2), 4, 1)

    # Dark wrist STRAP across the cuff (keeper trim) — the kit tell that locks
    # the white shape to "glove" rather than "snowball".
    pygame.draw.line(surf, _GK_YOKE, (cx - 8, cy + 7), (cx + 8, cy + 5), 4)
    pygame.draw.line(surf, _GK_YOKE_H, (cx - 7, cy + 6), (cx + 6, cy + 4), 1)

    # Crisp contour holds the mitt shape against the body and the sky.
    pygame.draw.polygon(surf, _GK_GLOVE_D, mitt, 1)
    # Top-light highlight so the padding crowns toward the light.
    pygame.draw.line(surf, _GK_GLOVE_H, (cx - 4, cy - 9), (cx + 3, cy - 9), 2)
    pygame.draw.circle(surf, _GK_GLOVE_H, (cx + 1, cy - 6), 1)


def _paint(surf, _a):
    # --- High-vis NEON keeper JERSEY over the torso -----------------------------
    # A clean jersey block clipped to the chest in lurid high-vis green so it
    # reads as the deliberately off-team keeper kit. Kept inside the body
    # footprint (shoulders ~BCY-12, hem ~BCY+11) so it never balloons the bird.
    jersey = [(BCX - 15, BCY - 9), (BCX - 16, BCY - 1), (BCX - 14, BCY + 11),
              (BCX + 13, BCY + 11), (BCX + 15, BCY - 1), (BCX + 13, BCY - 9),
              (BCX + 4, BCY - 12), (BCX - 6, BCY - 12)]
    _poly(surf, _GK_HV, jersey)
    # Lower-torso shadow gives the jersey a rounded body before the yoke goes on.
    pygame.draw.ellipse(surf, _GK_HV_D, (BCX - 12, BCY + 1, 24, 11))
    _poly(surf, _GK_HV, [(BCX - 14, BCY - 6), (BCX + 13, BCY - 6),
                         (BCX + 12, BCY + 4), (BCX - 13, BCY + 4)])

    # --- Long SLEEVES down the wing roots (keeper kit is long-sleeve) -----------
    # High-vis sleeves cap the wing roots so the kit reads as worn, with a dark
    # cuff at each wrist where the glove strap meets the sleeve.
    for sx, sgn in ((BCX - 14, -1), (BCX + 13, 1)):
        sleeve = [(sx, BCY - 9), (sx + 3 * sgn, BCY - 7), (sx + 5 * sgn, BCY + 2),
                  (sx + 3 * sgn, BCY + 6), (sx - 1 * sgn, BCY + 5),
                  (sx - 2 * sgn, BCY - 4)]
        _poly(surf, _GK_HV, sleeve)
        pygame.draw.line(surf, _GK_HV_H, (sx, BCY - 8),
                         (sx + 4 * sgn, BCY - 1), 1)               # sleeve top light
        pygame.draw.line(surf, _GK_HV_D, (sx + 2 * sgn, BCY + 1),
                         (sx + 4 * sgn, BCY + 5), 1)               # sleeve underside
        pygame.draw.line(surf, _GK_YOKE, (sx + 1 * sgn, BCY + 4),
                         (sx + 5 * sgn, BCY + 3), 3)               # dark wrist cuff

    # --- Dark shoulder YOKE (the keeper-kit contrast panel) ---------------------
    # A near-black yoke across both shoulders and the collar — the high-contrast
    # band that, with the neon below it, reads unmistakably as a keeper shirt and
    # not a plain green tank.
    # Lower edge dropped 1px (deeper dark band) so the dark-over-neon keeper
    # stack still reads after the 40px downscale.
    yoke = [(BCX - 14, BCY - 8), (BCX - 6, BCY - 12), (BCX + 4, BCY - 12),
            (BCX + 13, BCY - 8), (BCX + 9, BCY - 4), (BCX + 2, BCY - 6),
            (BCX - 4, BCY - 6), (BCX - 11, BCY - 4)]
    _poly(surf, _GK_YOKE, yoke)
    pygame.draw.line(surf, _GK_YOKE_H, (BCX - 12, BCY - 7),
                     (BCX - 5, BCY - 10), 1)
    pygame.draw.line(surf, _GK_YOKE_H, (BCX + 11, BCY - 7),
                     (BCX + 4, BCY - 10), 1)
    # Crew collar notch in high-vis so the neckline reads.
    _poly(surf, _GK_HV_H, [(BCX - 4, BCY - 11), (BCX + 3, BCY - 11),
                           (BCX + 2, BCY - 8), (BCX - 3, BCY - 8)])

    # Re-edge the jersey so panels don't leak past the cloth contour.
    pygame.draw.polygon(surf, _GK_HV_D, jersey, 1)

    # --- Short SHORTS hem + short SOCKS + cleats at the feet line ----------------
    # Short shorts hem in dark trim, then short socks + cleats hugging the feet
    # line. Everything sits ON the feet line (~HY+15..27), nothing drops below
    # it, so the bird keeps its true size.
    pygame.draw.line(surf, _GK_YOKE, (BCX - 12, BCY + 11), (BCX + 11, BCY + 11), 3)
    pygame.draw.line(surf, _GK_YOKE_H, (BCX - 10, BCY + 10), (BCX + 8, BCY + 10), 1)
    for fx in (28, 35):
        # Short sock — a stubby dark cuff (keeper socks aren't the tall outfield
        # knee-highs, so the lower silhouette stays distinct from the Striker).
        pygame.draw.line(surf, _GK_SOCK, (fx, HY + 18), (fx, HY + 22), 5)
        pygame.draw.line(surf, _GK_SOCK_H, (fx - 1, HY + 19), (fx - 1, HY + 21), 1)
        # Cleat boot — a single fat dark chunk + one highlight stripe. The tiny
        # stud ticks were sub-pixel noise at 40px, so they're dropped.
        pygame.draw.line(surf, _GK_CLEAT, (fx - 3, HY + 24), (fx + 2, HY + 24), 5)
        pygame.draw.line(surf, _GK_CLEAT_H, (fx - 2, HY + 22), (fx + 1, HY + 22), 1)

    # --- Soft short-brim CAP at the crown (keeps the macaw reading) -------------
    # A low soft cap with a short brim — a goalkeeper tell that adds little bulk,
    # so Pip's macaw head stays recognizable. Navy crown + a short forward brim.
    cy = CROWN_Y - 1
    cap = [(HX - 11, cy + 4), (HX - 6, cy - 3), (HX + 2, cy - 5),
           (HX + 10, cy - 1), (HX + 12, cy + 4), (HX + 2, cy + 3),
           (HX - 5, cy + 4)]
    _poly(surf, _GK_CAP, cap)
    pygame.draw.polygon(surf, _GK_CAP_D, cap, 1)
    # Crown highlight + a short forward brim catching the light.
    pygame.draw.line(surf, _GK_CAP_H, (HX - 5, cy - 2), (HX + 4, cy - 4), 2)
    # Brim filled in the darker shadow value (not the crown navy) so it breaks
    # hard from the dome and reads as a separate brim, not one navy blob.
    brim = [(HX - 12, cy + 4), (HX - 18, cy + 7), (HX - 16, cy + 9),
            (HX - 8, cy + 6)]
    _poly(surf, _GK_CAP_D, brim)
    pygame.draw.polygon(surf, _GK_CAP_D, brim, 1)
    # 1px lighter underedge separates the brim silhouette from the sky/body.
    pygame.draw.line(surf, _GK_CAP_H, (HX - 17, cy + 8), (HX - 9, cy + 6), 1)

    # --- Oversized keeper GLOVES on BOTH wing-hands (THE hero, drawn LAST) -------
    # The signature shapes: big padded mitts sitting proud in front of the body,
    # breaking the silhouette so the read screams GOALKEEPER from across the
    # pitch. Far hand first, near hand last, so the near glove reads frontmost.
    # Far hand pushed out + down so its rounded crown clears the scarlet tail
    # wedge and both mitts read as a matched PAIR against the body.
    _glove(surf, BCX - 18, BCY - 1, flip=-1)   # far (left) hand
    _glove(surf, BCX + 18, BCY - 2, flip=1)    # near (right) hand


build = store_skins._make_skin(_paint)
