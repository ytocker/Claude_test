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
# The face-shield rim is the cheek/jaw seal — darker than _GOLD_D so the gold
# plane reads as a closed mask even when the house outline drops out at 40px.
_SK_RIM     = (112, 80, 22)         # deep-gold cheek/jaw rim


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
    # Rim offset down+out, then a 2px restate on the lower cheeks/jaw only, so
    # the face-shield seals as its own closed shape under the house outline.
    _poly(surf, _SK_RIM, [(x + 1, y + 1) for x, y in face])
    pygame.draw.lines(surf, _SK_RIM, False,
                      [(HX - 12, HY + 2), (HX - 8, HY + 12), (HX, HY + 16),
                       (HX + 9, HY + 13), (HX + 14, HY + 3)], 2)
    _poly(surf, _SK_GOLD_D, face)
    inner = [(HX - 9, cy + 5), (HX - 10, HY + 2), (HX - 6, HY + 10),
             (HX, HY + 13), (HX + 7, HY + 11), (HX + 11, HY + 3),
             (HX + 10, cy + 4), (HX, cy + 3)]
    _poly(surf, _SK_GOLD, inner)
    # One soft top-cheek highlight band so the flat plane catches light as metal.
    _poly(surf, _SK_GOLD_H, [(HX - 7, cy + 6), (HX + 6, cy + 5),
                             (HX + 4, cy + 9), (HX - 6, cy + 10)])

    # ── EYES — the #2 read after the gold shield, and where "death-mask" lives.
    #    Enlarged ~40% and spaced wider, each almond is a continuous DARK VOID
    #    interior — dark-on-gold is the contrast that carries (lapis-on-gold
    #    would just echo the nemes stripes above and vanish). A thin gold-
    #    highlight inner line separates the void from the surrounding gold so it
    #    pops off the plane rather than melting into the nemes blue.
    for sgn, ex in ((-1, HX - 6), (1, HX + 10)):
        ey = HY + 1
        almond = [(ex - 6, ey), (ex - 1, ey - 5), (ex + 5, ey - 4),
                  (ex + 5, ey + 1), (ex, ey + 4)]
        almond = [(x, y) for x, y in
                  ([(ex - 6, ey), (ex - 1, ey - 4), (ex + 6, ey),
                    (ex - 1, ey + 4)] if sgn < 0 else
                   [(ex + 6, ey), (ex + 1, ey - 4), (ex - 6, ey),
                    (ex + 1, ey + 4)])]
        # Void fill is the dominant value; a deep-gold rim seats the almond.
        _poly(surf, _SK_RIM, [(x, y + 1) for x, y in almond])
        _poly(surf, _SK_VOID, almond)
        pygame.draw.polygon(surf, _SK_GOLD_H, almond, 1)   # gold-highlight inner line
        pygame.draw.circle(surf, _SK_GOLD_H, (ex - sgn, ey - 1), 1)  # life glint

    # ── DIVINE BEARD BAR — a single long straight gold bar under the chin, lapis
    #    banded so it reads as the plaited royal beard, kept INSIDE the silhouette
    #    (never below the feet line). The vertical tell that says "death-mask".
    bx = HX + 1
    # A dark void halo first, so the beard reads as a distinct vertical against
    # the body instead of merging with the collar/coffin gold beside it.
    _poly(surf, _SK_VOID, [(bx - 6, HY + 13), (bx + 6, HY + 13),
                           (bx + 5, HY + 24), (bx - 5, HY + 24)])
    _poly(surf, _SK_GOLD_D, [(bx - 5, HY + 13), (bx + 5, HY + 13),
                             (bx + 4, HY + 23), (bx - 4, HY + 23)])
    _poly(surf, _SK_GOLD, [(bx - 4, HY + 13), (bx + 4, HY + 13),
                           (bx + 3, HY + 22), (bx - 3, HY + 22)])
    for byb in (HY + 16, HY + 19):
        pygame.draw.line(surf, _SK_LAPIS, (bx - 4, byb), (bx + 4, byb), 2)
    pygame.draw.line(surf, _SK_GOLD_H, (bx - 3, HY + 14), (bx - 3, HY + 21), 1)

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

    # ── URAEUS — ONE central cobra head at the brow peak. Two symmetric red dots
    #    read as misplaced eyes at 40px, so commit to a single bigger cobra bump
    #    (hood + flared base) with one red glint — the rearing-cobra silhouette.
    _poly(surf, _SK_GOLD_D, [(HX - 3, cy - 4), (HX + 3, cy - 4),
                             (HX + 2, cy - 9), (HX - 2, cy - 9)])
    pygame.draw.circle(surf, _SK_GOLD_D, (HX, cy - 10), 3)
    pygame.draw.circle(surf, _SK_GOLD, (HX, cy - 10), 2)
    pygame.draw.circle(surf, _SK_URAEUS, (HX, cy - 10), 1)

    # ── BROAD COLLAR — pulled DOWN + OUT so it clears a dark gap around the beard
    #    and the beard reads as its own vertical. Two THIN arcs only (lapis / gold)
    #    so it stays a flat inlay inside the body footprint, never added mass.
    ccx, ccy = HX - 2, HY + 16
    for r, col in ((14, _SK_LAPIS), (12, _SK_GOLD)):
        pygame.draw.arc(surf, col, (ccx - r, ccy - r + 6, r * 2, r * 2),
                        3.7, 5.8, 2)

    # ── CROSSED CROOK + FLAIL X — the ONE lower-body tell. The coffin-lid stripes
    #    are dropped: a clean bold gold X (echoing the death-mask crossed-arms
    #    pose) reads at 40px where a striped-panel-plus-decorated-X became blue/
    #    gold noise. No crook curl, no flail filigree — just two thick gold bars
    #    crossing, each capped with a single lapis bead, over a void seat so the X
    #    pops off the body rather than blending into the gold.
    BCX, BCY = 32, 52
    a, b = (BCX - 10, BCY - 7), (BCX + 8, BCY + 10)     # crook arm (\)
    c, d = (BCX + 10, BCY - 7), (BCX - 8, BCY + 10)     # flail arm (/)
    for p, q in ((a, b), (c, d)):
        pygame.draw.line(surf, _SK_VOID, p, q, 6)        # dark seat = figure/ground
    for p, q in ((a, b), (c, d)):
        pygame.draw.line(surf, _SK_GOLD_D, p, q, 5)
        pygame.draw.line(surf, _SK_GOLD, p, q, 3)
        pygame.draw.line(surf, _SK_GOLD_H, p, q, 1)
    for bead in (a, c):                                  # two lapis beads, no more
        pygame.draw.circle(surf, _SK_LAPIS_D, bead, 3)
        pygame.draw.circle(surf, _SK_LAPIS, bead, 2)
    # Bright crossing knot where the arms meet — the flat-art focal dot.
    pygame.draw.circle(surf, _SK_GOLD_H, (BCX, BCY + 2), 2)

    # ── FEET — gold-banded recolor at the feet line, ON it (~y65), never below.
    for fx in (28, 34):
        pygame.draw.line(surf, _SK_GOLD_D, (fx - 3, 65), (fx + 3, 65), 3)
        pygame.draw.line(surf, _SK_GOLD, (fx - 3, 64), (fx + 3, 64), 2)
        pygame.draw.line(surf, _SK_LAPIS, (fx - 2, 66), (fx + 2, 66), 1)


build = store_skins._make_skin(_paint)
