"""WAR PHARAOH — the Khepresh Conqueror (PHARAOH v2_design_4 of 5).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
pharaoh skin is untouched. WAR PHARAOH is a paint-over (Pip's face stays under
the crown).

Concept: the ONLY round/soft crown in the batch + the ONLY weapon prop. The
hero silhouette is the smooth deep-blue Khepresh war-dome — a single bulbous
cap that reads as a soft helmet against every conical pharaoh crown. The crown
is left as a CLEAN blue cap (no boss confetti): the lone gold on it is a
forward-striking uraeus cobra proud of the dome's front edge. A curved gold
khopesh sickle-sword is slung diagonally across the body — keylined dark on
both edges with an exaggerated hook whose tip POKES PAST the back outline
against the sky, so the weapon actually reads as a weapon at 40px.

At 40px the read, in order: (1) a saturated blue ROUND dome (the soft-crown
break, and the brightest/most-saturated shape so it wins the focal fight),
(2) the gold uraeus glinting at the brow, (3) a single curved gold blade laid
across the body with a hooked tip breaking the back outline. Nothing else
competes — no sash, no scale field, no body blue.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Khepresh deep royal blue needs two values so the dome reads as a rounded
# helmet (shadow on the underside) rather than a flat disc at 40px. Blue lives
# ONLY in the crown so it wins the focal fight as the brightest/most-saturated
# shape against the scarlet body.
_WP_BLUE    = (30, 58, 138)        # #1E3A8A khepresh blue
_WP_BLUE_D  = (20, 42, 99)         # #142A63 blue shadow
_WP_BLUE_H  = (54, 92, 184)        # crown top-light so the dome catches the sky
# Gold is the hero accent + the weapon; three values so the curved khopesh keeps
# a bright edge that survives the downscale (a metal curve only reads if it glints).
_WP_GOLD    = (232, 178, 58)       # #E8B23A gold uraeus / khopesh
_WP_GOLD_H  = (244, 214, 122)      # #F4D67A gold highlight (the 40px glint)
_WP_GOLD_D  = (168, 122, 36)       # gold shadow so the blade has a dark edge
# A near-black keyline so the gold blade reads against the WARM body (gold on
# scarlet smears without a hard dark edge — the cutlass uses steel-on-sky, the
# khopesh has no sky behind most of its length so it needs its own keyline).
_WP_KEY     = (28, 18, 10)         # blade keyline / cobra eye
_WP_SANDAL  = (58, 40, 26)         # dark leather sandal at the feet line
_WP_SANDAL_H = (96, 70, 46)


def _khopesh_blade(surf, p0, ctrl, p1, color, width):
    """Quadratic-bezier polyline so the khopesh reads as a CURVED sickle, not a
    straight bar. Sampled coarse — the curve survives downscale, extra points
    don't (same idiom as the pirate cutlass)."""
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
    # ── KHOPESH slung diagonally across the body (painted first so the body
    #    covers the grip root). Unlike a straight cutlass the khopesh is a SICKLE:
    #    the hilt sits low-front at the waist, the shaft rises back, then the
    #    cutting edge HOOKS hard up-and-back so the hooked tip clears the back
    #    outline against the sky — a weapon you can't see isn't a weapon. The
    #    curvature is exaggerated so even ~5-6px downscaled still reads as a hook.
    hilt = (HX - 2, HY + 24)          # grip, low at the waist / near wing
    ktip = (HX - 27, CROWN_Y + 2)     # hook tip, POKING PAST the back outline
    kctrl = (HX - 26, HY + 16)        # control pulls the sickle belly far out
    # Dark keyline on BOTH edges (widest) so the gold curve reads against the
    # warm body along its whole length, not just where sky is behind it.
    _khopesh_blade(surf, hilt, kctrl, ktip, _WP_KEY, 7)
    _khopesh_blade(surf, hilt, kctrl, ktip, _WP_GOLD_D, 5)
    _khopesh_blade(surf, hilt, kctrl, ktip, _WP_GOLD, 4)
    # Bright back-edge glint — the single highest-value line that makes the gold
    # curve read as a blade at 40px. Offset along the spine of the curve.
    _khopesh_blade(surf, (hilt[0] - 1, hilt[1] - 2),
                   (kctrl[0] - 2, kctrl[1] - 2), (ktip[0] + 1, ktip[1] - 1),
                   _WP_GOLD_H, 2)
    # Hooked sickle point — a clear forward-curling barb so the tip reads as the
    # khopesh's signature hook against the sky, keylined dark so it survives.
    hook = [(ktip[0] - 3, ktip[1] - 4), (ktip[0] + 5, ktip[1] - 1),
            (ktip[0] + 1, ktip[1] + 3), (ktip[0] - 2, ktip[1] + 1)]
    _poly(surf, _WP_KEY, [(x - 1, y) for x, y in hook])
    _poly(surf, _WP_GOLD, hook)
    pygame.draw.line(surf, _WP_GOLD_H, (ktip[0] - 2, ktip[1] - 3),
                     (ktip[0] + 3, ktip[1] - 1), 1)
    # Short dark grip stub + a gold pommel bead so the low end reads as the handle.
    pygame.draw.line(surf, _WP_KEY, (hilt[0] + 1, hilt[1]),
                     (hilt[0] + 6, hilt[1] + 6), 4)
    pygame.draw.circle(surf, _WP_GOLD, (hilt[0] + 7, hilt[1] + 7), 2)
    pygame.draw.circle(surf, _WP_GOLD_H, (hilt[0] + 6, hilt[1] + 6), 1)

    # ── ONE GOLD COLLAR ARC across the upper chest — a single thin band with a
    #    dark underline reads as regalia at 40px; the old scale-fleck field read
    #    as a gold cloud. Drawn as a shallow arc following the chest curve, kept
    #    well inside the footprint so it never bulks the body.
    collar = pygame.Rect(HX - 16, HY + 6, 24, 16)
    pygame.draw.arc(surf, _WP_KEY, collar, 3.6, 5.8, 3)      # dark underline
    pygame.draw.arc(surf, _WP_GOLD, collar, 3.6, 5.8, 2)
    pygame.draw.arc(surf, _WP_GOLD_H, (HX - 14, HY + 5, 20, 14), 3.9, 5.4, 1)

    # ── SANDAL RECOLOR at the feet line (~HY+24) — dark leather straps sitting ON
    #    the feet, never below them, so the bird keeps its true size.
    for fx in (28, 34):
        pygame.draw.ellipse(surf, _WP_SANDAL, (fx - 3, HY + 23, 7, 4))
        pygame.draw.line(surf, _WP_SANDAL_H, (fx - 2, HY + 23), (fx + 2, HY + 23), 1)
        pygame.draw.line(surf, _WP_SANDAL, (fx, HY + 21), (fx, HY + 24), 1)  # ankle strap

    # ── THIN GOLD BROW-BAND where the dome meets the head (drawn before the dome
    #    so the dome's lower edge overlaps it cleanly), a hard horizontal gold
    #    line that anchors the face under the crown at 40px. The lone non-cobra
    #    gold on the crown — it seats the soft dome on the head.
    pygame.draw.line(surf, _WP_GOLD, (HX - 12, CROWN_Y + 9), (HX + 12, CROWN_Y + 9), 3)
    pygame.draw.line(surf, _WP_GOLD_H, (HX - 9, CROWN_Y + 8), (HX + 4, CROWN_Y + 8), 1)

    # ── KHEPRESH WAR-DOME (above CROWN_Y) — the hero. A single smooth deep-blue
    #    rounded cap (the only round/soft crown in the batch), tall enough to
    #    dome over the crown but bulbous, NOT a cone. Kept a CLEAN blue cap — no
    #    boss confetti — so the saturated blue reads as the focal shape. A shadow
    #    ellipse underlay gives the dome volume; a top-light arc catches the sky.
    dome = pygame.Rect(HX - 15, CROWN_Y - 11, 30, 26)         # bulbous cap
    pygame.draw.ellipse(surf, _WP_BLUE_D, dome)
    inner = pygame.Rect(HX - 14, CROWN_Y - 11, 28, 23)        # body sits high
    pygame.draw.ellipse(surf, _WP_BLUE, inner)
    pygame.draw.ellipse(surf, _WP_BLUE_H, (HX - 9, CROWN_Y - 10, 16, 8))  # top-light
    # Flatten the dome's bottom into the brow-band so it reads as a seated helmet,
    # not a floating ball.
    _poly(surf, _WP_BLUE_D, [(HX - 14, CROWN_Y + 7), (HX + 14, CROWN_Y + 7),
                             (HX + 13, CROWN_Y + 10), (HX - 13, CROWN_Y + 10)])

    # ── GOLD URAEUS cobra striking forward at the brow — the ONLY gold on the
    #    crown, so it reads as a forward-striking cobra rather than "more gold."
    #    A bright gold head-blob proud of the dome's front edge with a tiny dark
    #    eye; a short reared S-neck connects it to the brow-band. Painted last so
    #    it sits proud of the dome and carries the night read.
    ux, uy = HX + 3, CROWN_Y + 6      # cobra root at the brow-band centre-front
    neck = [(ux, uy), (ux + 1, uy - 4), (ux + 3, uy - 7)]
    pygame.draw.lines(surf, _WP_KEY, False,
                      [(x + 1, y + 1) for x, y in neck], 4)   # cobra shadow
    pygame.draw.lines(surf, _WP_GOLD, False, neck, 3)         # reared S-neck
    # Flared hood + forward-striking head jutting proud of the dome's front edge.
    head = [(ux + 1, uy - 6), (ux + 4, uy - 10), (ux + 9, uy - 8),
            (ux + 8, uy - 4), (ux + 4, uy - 3)]
    _poly(surf, _WP_KEY, [(x + 1, y) for x, y in head])
    _poly(surf, _WP_GOLD, head)
    pygame.draw.circle(surf, _WP_GOLD_H, (ux + 6, uy - 7), 2)   # bright cobra head
    pygame.draw.circle(surf, _WP_KEY, (ux + 7, uy - 8), 1)      # eye dot


build = store_skins._make_skin(_paint)
