"""THE SARCOPHAGUS KING — the living golden death-mask (v2 DESIGN 5 of 5).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_pharaoh`` is untouched.

Concept (RE-ROLL): the funerary golden death-mask becomes a LIVING coffin lid.
Unlike the rejected realistic golden-nemes, the face itself is the hero — a
FLAT, GRAPHIC gold mask, not a soft portrait. The head is painted over as a
smooth gold face-plane framed by a nemes headcloth of bold alternating
GOLD + LAPIS stripes; big calm lapis-rimmed almond eyes and a single divine
beard bar read it as a solid gold shield at 40px. The lower body is painted as
a COFFIN-LID inlay panel (gold centre band flanked by thin lapis stripes) with
flat crossed-arms holding a mini crook + flail — all kept inside the base bird
footprint so the hitbox never lies.

The critical risk is gold-on-gold going fussy/muddy, so the rule throughout is
FLAT + GRAPHIC: loud lapis stripes carry the value separation, eyes are big and
simple, no tiny filigree. At 40px the read, in order of value: (1) a solid gold
mask shield of a face, (2) the gold+lapis striped nemes lappets framing it,
(3) the big lapis-rimmed eyes + beard bar, (4) the lapis-striped coffin-lid body
panel with the crossed crook+flail. On night the gold face glows and the lapis
stripes anchor the value — pure treasure read.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Mask gold needs three values so the flat face-plane still reads as metal (a
# single flat gold dissolves into "yellow blob"); lapis is the loud value
# separator that keeps the whole thing from going gold-on-gold mud, and the
# turquoise is the one cool inlay accent in the broad collar.
_SK_GOLD    = (232, 178, 58)        # #E8B23A mask gold
_SK_GOLD_D  = (200, 144, 42)        # #C8902A gold shadow
_SK_GOLD_H  = (244, 214, 122)       # #F4D67A gold highlight
_SK_LAPIS   = (31, 58, 147)         # #1F3A93 lapis blue
_SK_LAPIS_D = (20, 38, 102)         # lapis shadow keeps a stripe a stripe at 40px
_SK_TURQ    = (31, 163, 154)        # #1FA39A turquoise inlay
_SK_URAEUS  = (200, 50, 50)         # uraeus / vulture red accent
_SK_VOID    = (16, 16, 24)          # almond eye + brow void (the dark anchor)
_SK_RIM     = (140, 102, 30)        # darker-gold rim on the mask's outer cheek edge


def _paint(surf, _a):
    cy = CROWN_Y

    # ── NEMES LAPPETS — striped cloth falling beside the head. Drawn first so the
    #    gold face-plane laps over their inner edge → the lappets frame the mask.
    #    Bold WIDE alternating gold/lapis stripes (3px) so the value separation
    #    survives downscale instead of turning to 1px noise.
    for sgn, x0 in ((-1, HX - 14), (1, HX + 8)):
        lappet = [(x0, cy + 2), (x0 + 6, cy + 2),
                  (x0 + 7, HY + 17), (x0 - 1, HY + 17)]
        _poly(surf, _SK_GOLD, lappet)
        for i in range(3):
            lx = x0 + i * 2 + 1
            col = _SK_LAPIS if i % 2 == 0 else _SK_GOLD_D
            pygame.draw.line(surf, col, (lx, cy + 3), (lx, HY + 16), 2)
        pygame.draw.polygon(surf, _SK_GOLD_D, lappet, 1)

    # ── FLAT GOLD DEATH-MASK FACE — the hero. A smooth gold face-plane painted
    #    over Pip's head: a broad-cheeked rounded shield. Three flat gold values
    #    only (no gradient noise) so it reads as a solid metal mask, not a soft
    #    portrait. A dark-gold rim on the outer cheek edge gives the shield its
    #    contour without the house outline doing all the work.
    face = [(HX - 11, cy + 4), (HX - 12, HY + 2), (HX - 8, HY + 12),
            (HX, HY + 16), (HX + 9, HY + 13), (HX + 14, HY + 3),
            (HX + 13, cy + 3), (HX, cy + 1)]
    _poly(surf, _SK_RIM, [(x + 1, y) for x, y in face])
    _poly(surf, _SK_GOLD_D, face)
    inner = [(HX - 9, cy + 5), (HX - 10, HY + 2), (HX - 6, HY + 10),
             (HX, HY + 13), (HX + 7, HY + 11), (HX + 11, HY + 3),
             (HX + 10, cy + 4), (HX, cy + 3)]
    _poly(surf, _SK_GOLD, inner)
    # One soft top-cheek highlight band so the flat plane catches light as metal.
    _poly(surf, _SK_GOLD_H, [(HX - 7, cy + 6), (HX + 6, cy + 5),
                             (HX + 4, cy + 9), (HX - 6, cy + 10)])

    # ── EYES — big calm lapis-rimmed almonds, drawn LARGE and simple so they are
    #    the second read after the gold shield. Almond outline (lapis) + dark
    #    pupil; a single cosmetic flick line off each outer corner (Egyptian kohl)
    #    kept to one bold stroke, not filigree.
    for sgn, ex in ((-1, HX - 4), (1, HX + 8)):
        ey = HY + 1
        almond = [(ex - 4, ey), (ex, ey - 3), (ex + 4, ey),
                  (ex, ey + 3)]
        _poly(surf, _SK_LAPIS, almond)
        pygame.draw.circle(surf, _SK_VOID, (ex, ey), 2)
        pygame.draw.circle(surf, _SK_GOLD_H, (ex - 1, ey - 1), 1)   # life glint
        # kohl flick to the outer corner — one stroke.
        pygame.draw.line(surf, _SK_LAPIS, (ex + sgn * 4, ey),
                         (ex + sgn * 7, ey - 1), 2)
    # Straight gold nose ridge between the eyes — a single flat highlight bar.
    pygame.draw.line(surf, _SK_GOLD_H, (HX + 2, HY + 2), (HX + 2, HY + 8), 2)
    pygame.draw.line(surf, _SK_GOLD_D, (HX + 4, HY + 3), (HX + 4, HY + 8), 1)

    # ── DIVINE BEARD BAR — a single long straight gold bar under the chin, lapis
    #    banded so it reads as the plaited royal beard, kept INSIDE the silhouette
    #    (never below the feet line). The vertical tell that says "death-mask".
    bx = HX + 1
    _poly(surf, _SK_GOLD_D, [(bx - 4, HY + 13), (bx + 4, HY + 13),
                             (bx + 3, HY + 23), (bx - 3, HY + 23)])
    _poly(surf, _SK_GOLD, [(bx - 3, HY + 13), (bx + 3, HY + 13),
                           (bx + 2, HY + 22), (bx - 2, HY + 22)])
    for byb in (HY + 16, HY + 19):
        pygame.draw.line(surf, _SK_LAPIS, (bx - 3, byb), (bx + 3, byb), 1)
    pygame.draw.line(surf, _SK_GOLD_H, (bx - 2, HY + 14), (bx - 2, HY + 21), 1)

    # ── NEMES CREST over the crown — the headcloth cap rising to a low peak, with
    #    bold WIDE alternating gold + lapis stripes radiating over it. The ONLY
    #    element allowed above CROWN_Y. A front lapis headband seats it.
    pygame.draw.ellipse(surf, _SK_GOLD_D, (HX - 14, cy - 6, 29, 18))
    pygame.draw.ellipse(surf, _SK_GOLD, (HX - 13, cy - 6, 27, 15))
    # Low peak in the centre so the crest breaks the crown outline as a soft point.
    _poly(surf, _SK_GOLD_D, [(HX - 5, cy - 4), (HX + 5, cy - 4), (HX, cy - 11)])
    _poly(surf, _SK_GOLD, [(HX - 4, cy - 4), (HX + 4, cy - 4), (HX, cy - 10)])
    for i in range(-3, 4):
        x = HX + i * 4
        col = _SK_LAPIS if i % 2 == 0 else _SK_GOLD_D
        pygame.draw.line(surf, col, (x, cy - 5), (x, cy + 6), 3)
    # Front headband — a clean lapis bar under the stripes.
    pygame.draw.line(surf, _SK_LAPIS_D, (HX - 13, cy + 5), (HX + 14, cy + 4), 4)
    pygame.draw.line(surf, _SK_LAPIS, (HX - 13, cy + 4), (HX + 14, cy + 3), 2)
    pygame.draw.line(surf, _SK_GOLD_H, (HX - 6, cy + 1), (HX + 4, cy), 1)

    # ── URAEUS + VULTURE BROW BAND — kept to TWO clean bumps (cobra + vulture),
    #    NOT fussy. Gold bumps with a single red accent each, riding the low peak.
    for sgn, ux in ((-1, HX - 4), (1, HX + 4)):
        pygame.draw.circle(surf, _SK_GOLD_D, (ux, cy - 6), 3)
        pygame.draw.circle(surf, _SK_GOLD, (ux, cy - 6), 2)
        pygame.draw.circle(surf, _SK_URAEUS, (ux, cy - 6), 1)
    pygame.draw.circle(surf, _SK_GOLD_H, (HX, cy - 9), 1)

    # ── BROAD COLLAR — a wide inlaid pectoral of concentric band arcs under the
    #    chin. Kept to 3 THIN arcs (lapis / gold / turquoise) so it stays a flat
    #    inlay inside the body footprint and never reads as added body mass.
    ccx, ccy = HX - 2, HY + 13
    for r, col in ((13, _SK_LAPIS), (11, _SK_GOLD), (9, _SK_TURQ)):
        pygame.draw.arc(surf, col, (ccx - r, ccy - r + 6, r * 2, r * 2),
                        3.5, 6.0, 2)

    # ── COFFIN-LID BODY PANEL — the lower body painted over as a sarcophagus
    #    inlay: a vertical GOLD centre band flanked by thin LAPIS stripes. Kept
    #    strictly inside the base bird footprint (no balloon, nothing below feet).
    BCX, BCY = 32, 52
    _poly(surf, _SK_GOLD_D, [(BCX - 5, BCY - 6), (BCX + 5, BCY - 6),
                             (BCX + 4, BCY + 13), (BCX - 4, BCY + 13)])
    _poly(surf, _SK_GOLD, [(BCX - 4, BCY - 6), (BCX + 4, BCY - 6),
                           (BCX + 3, BCY + 12), (BCX - 3, BCY + 12)])
    pygame.draw.line(surf, _SK_GOLD_H, (BCX - 1, BCY - 5), (BCX - 1, BCY + 11), 1)
    # Thin lapis inlay stripes flanking the gold band — the sarcophagus tell.
    for sgn in (-1, 1):
        sx = BCX + sgn * 7
        pygame.draw.line(surf, _SK_LAPIS_D, (sx, BCY - 5), (sx - sgn, BCY + 11), 3)
        pygame.draw.line(surf, _SK_LAPIS, (sx, BCY - 5), (sx - sgn, BCY + 11), 1)

    # ── CROSSED ARMS holding mini CROOK + FLAIL — painted FLAT across the upper
    #    chest as the death-mask's signature pose (gold mask art, not 3D staffs).
    #    Two short gold bars cross in an X over the coffin panel, with a tiny
    #    crook curl and flail tip, all inside the silhouette.
    # Crook arm (\) with a hooked top.
    pygame.draw.line(surf, _SK_GOLD_D, (BCX - 9, BCY - 4), (BCX + 7, BCY + 9), 4)
    pygame.draw.line(surf, _SK_GOLD, (BCX - 9, BCY - 4), (BCX + 7, BCY + 9), 2)
    pygame.draw.arc(surf, _SK_GOLD, (BCX - 12, BCY - 7, 7, 7), 0.4, 3.0, 2)
    # Flail arm (/) with a tiny three-tail tip.
    pygame.draw.line(surf, _SK_GOLD_D, (BCX + 9, BCY - 4), (BCX - 7, BCY + 9), 4)
    pygame.draw.line(surf, _SK_GOLD, (BCX + 9, BCY - 4), (BCX - 7, BCY + 9), 2)
    for tx in (-2, 0, 2):
        pygame.draw.line(surf, _SK_GOLD, (BCX + 9, BCY - 4),
                         (BCX + 9 + tx, BCY - 8), 1)
    pygame.draw.circle(surf, _SK_LAPIS, (BCX + 9, BCY - 4), 1)   # flail bead
    pygame.draw.circle(surf, _SK_LAPIS, (BCX - 9, BCY - 4), 1)   # crook bead
    # Bright crossing knot where the two arms meet — the flat-art focal dot.
    pygame.draw.circle(surf, _SK_GOLD_H, (BCX, BCY + 3), 2)
    pygame.draw.circle(surf, _SK_LAPIS, (BCX, BCY + 3), 1)

    # ── FEET — gold-banded recolor at the feet line, ON it (~y65), never below.
    for fx in (28, 34):
        pygame.draw.line(surf, _SK_GOLD_D, (fx - 3, 65), (fx + 3, 65), 3)
        pygame.draw.line(surf, _SK_GOLD, (fx - 3, 64), (fx + 3, 64), 2)
        pygame.draw.line(surf, _SK_LAPIS, (fx - 2, 66), (fx + 2, 66), 1)


build = store_skins._make_skin(_paint)
