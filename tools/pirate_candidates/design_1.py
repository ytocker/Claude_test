"""CAPTAIN'S COMMAND — the pirate promoted to a dressed-up ship's captain.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_pirate`` is untouched.

The brief: keep the pirate IDENTITY (tricorn + white skull cockade + gold) but
pile on naval finery so the costume reads as formal RANK, not a deckhand. The
coat / epaulette / jabot are painted as OVERLAYS on the scarlet macaw base
(default ``_build_frame``) so Pip's identity survives — the wine coat sits as
turned-back panels framing the chest rather than replacing the whole body, so
the scarlet still breathes between the lapels.

At 40px in motion the read, in order of value, is: (1) the broad navy-slate
TRICORN — a three-cornered brim (asymmetric front-dipped point + a single low
back corner, NOT two mirrored Napoleon horns) lifted off the crown with a gold
lace band tracing the OUTER edge and a second lace rope set INSIDE the brim,
(2) the white skull cockade dead-centre as the anchor (thin 1px gold ring, not a
filled disc, so the bone reads), (3) the gold bullion epaulette + gold coat-cuff
breaking the back / wing outline so the silhouette reads WIDER and "dressed",
and (4) the slim tapered lace jabot tucked under the beak + the wine coat panels
with a gold-button row as the close-up density. The coat is a cooler, darker
desaturated burgundy with a near-black-wine separating LINE against the scarlet
body so the lapel edge survives even when the fills merge. Every object is mass +
one bright accent so the stack holds when it shrinks; nothing rides near-black on
the navy store card — the felt is mid-value slate and the coat lifts off both the
scarlet body and the dark card.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Deeper navy-slate felt than the original (still mid-value so it lifts off the
# scarlet head AND the dark store card). The double lace band carries the read.
_FELT    = (46, 51, 70)            # #2E3346
_FELT_D  = (30, 34, 50)
_FELT_H  = (78, 84, 108)
_LACE    = (255, 205, 70)          # #FFCD46 gold lace
_LACE_H  = (255, 240, 160)         # #FFF0A0 gold highlight
_SKULL   = (244, 246, 240)         # #F4F6F0 lace-white skull + jabot
_SKULL_D = (196, 200, 196)
# Captain's coat — a COOLER, darker desaturated burgundy-plum so it sits a clear
# value step BELOW the scarlet body (no mud-merge), and still lifts off the navy
# card. _COAT_S is a near-black wine used as a hard separating line at the lapel
# edge so the coat reads even when its fill bleeds into the scarlet.
_COAT    = (104, 38, 54)           # #682636 desaturated burgundy-plum
_COAT_D  = (66, 22, 36)            # #421624 coat shadow / fold
_COAT_S  = (38, 12, 22)            # #260C16 near-black wine separating line
_COAT_H  = (146, 60, 78)           # lifted lapel edge highlight
_DARKEYE = (28, 22, 30)


def _paint(surf, _a):
    # ── captain's coat: turned-back wine panels framing the chest, drawn FIRST
    #    so the scarlet body and the gold buttons sit on top. Body centre is
    #    ~(32, 52) in composite space; the two lapels open in a V from the
    #    shoulders down so the scarlet chest still shows between them — the coat
    #    DRESSES the bird, it doesn't repaint it.
    bcx, bcy = 32, 52
    # Near (right) front panel — one clean wine WEDGE. Its bottom point is pulled
    # UP so the wine stops SHORT of the blue tail block instead of fighting it; the
    # lower body now reads scarlet → one wine lapel → gold buttons, nothing else.
    # Drawn shadow-first so the fill sits inside a dark frame.
    near = [(bcx + 18, bcy - 9), (bcx + 21, bcy + 2),
            (bcx + 14, bcy + 11), (bcx + 6, bcy + 9),
            (bcx + 4, bcy + 1), (bcx + 7, bcy - 5), (bcx + 11, bcy - 7)]
    _poly(surf, _COAT_D, near)
    near_in = [(bcx + 17, bcy - 7), (bcx + 19, bcy + 2),
               (bcx + 13, bcy + 9), (bcx + 7, bcy + 7),
               (bcx + 6, bcy + 1), (bcx + 8, bcy - 3), (bcx + 11, bcy - 5)]
    _poly(surf, _COAT, near_in)
    # Far (left) panel — narrower, peeking past the near wing so the coat wraps.
    far = [(bcx - 16, bcy - 6), (bcx - 9, bcy - 8),
           (bcx - 6, bcy + 4), (bcx - 12, bcy + 10), (bcx - 17, bcy + 2)]
    _poly(surf, _COAT_D, far)
    _poly(surf, _COAT, [(bcx - 14, bcy - 4), (bcx - 9, bcy - 6),
                        (bcx - 7, bcy + 3), (bcx - 12, bcy + 8),
                        (bcx - 15, bcy + 1)])
    # HARD near-black-wine separating line where the near lapel meets the scarlet
    # body — this is the edge that survives even if the coat fill bleeds into the
    # body, so the lapel always reads as a distinct cloth panel, not mud.
    pygame.draw.lines(surf, _COAT_S, False,
                      [(bcx + 11, bcy - 7), (bcx + 7, bcy - 1),
                       (bcx + 5, bcy + 3), (bcx + 6, bcy + 9)], 2)
    # Lifted lapel edge on the near panel so the coat catches light, not mud.
    pygame.draw.lines(surf, _COAT_H, False,
                      [(bcx + 12, bcy - 5), (bcx + 18, bcy + 1),
                       (bcx + 14, bcy + 9)], 1)

    # Gold-button placket down the lapel — TWO studs with wide vertical spacing so
    # each reads as a DISTINCT gold point at 40px (three blurred into one gold smear
    # against the epaulette on the night read). Each on a dark backing pip so the
    # gold survives downscale against the coat.
    for k, by in enumerate((bcy - 2, bcy + 5)):
        pygame.draw.circle(surf, _COAT_S, (bcx + 9, by), 3)
        pygame.draw.circle(surf, _LACE, (bcx + 9, by), 2)
        pygame.draw.circle(surf, _LACE_H, (bcx + 8, by - 1), 1)

    # ── slim white lace jabot tucked DIRECTLY under the beak base so it connects
    #    to the head (not a floating sail). Just TWO tiers now, pulled ~2px tighter
    #    under the beak, and the lowest tier is painted in _SKULL_D (off-white) so
    #    ONLY the skull cockade holds the brightest white crown. Its left edge is
    #    broken by the coat wine so it isn't a clean white rectangle against sky.
    jx, jy = HX + 4, HY + 3         # pulled ~2px tighter under the beak base
    # Coat-wine wedge biting the left side of the ruffle so the white edge breaks.
    _poly(surf, _COAT_D, [(jx - 4, jy + 1), (jx - 1, jy + 2),
                          (jx - 2, jy + 7), (jx - 5, jy + 5)])
    _poly(surf, _SKULL_D, [(jx - 3, jy), (jx + 4, jy),
                           (jx + 1, jy + 9), (jx - 2, jy + 8)])
    # Top tier the brighter lace-white; lower tier off-white so it yields the
    # brightest-white crown to the skull cockade above.
    for t, (w, dy, col) in enumerate(((3, 0, _SKULL), (2, 4, _SKULL_D))):
        cy = jy + dy
        ww = w - t
        _poly(surf, col, [(jx - ww, cy), (jx + ww + 1, cy), (jx, cy + 5)])
        pygame.draw.line(surf, _SKULL_D, (jx - ww + 1, cy + 2), (jx, cy + 4), 1)
        pygame.draw.line(surf, _SKULL_D, (jx, cy + 4), (jx + ww, cy + 2), 1)

    # ── gold BULLION epaulette pushed HIGHER onto the far shoulder so it clearly
    #    breaks the back silhouette against the sky — the "rank" read no other
    #    pirate has. ONE clean gold pad + a single bright top highlight + ONE row
    #    of fat 2px fringe dots, so it reads as a crisp shape, not an ambiguous
    #    lump, even at 40px.
    epx, epy = HX - 17, HY + 5
    _poly(surf, _COAT_S, [(epx - 6, epy - 4), (epx + 5, epy - 5),
                          (epx + 6, epy + 3), (epx - 5, epy + 3)])
    _poly(surf, _LACE, [(epx - 5, epy - 3), (epx + 4, epy - 4),
                        (epx + 5, epy + 2), (epx - 4, epy + 2)])
    # Single bright highlight across the top of the pad.
    pygame.draw.line(surf, _LACE_H, (epx - 4, epy - 3), (epx + 4, epy - 3), 1)
    # ONE row of fat fringe dots hanging off the back edge into sky.
    for fx in range(-5, 6, 3):
        pygame.draw.circle(surf, _LACE, (epx + fx, epy + 6), 2)
    pygame.draw.circle(surf, _LACE_H, (epx - 5, epy + 6), 1)

    # ── gold hoop earring (keep the buccaneer note under the head).
    pygame.draw.circle(surf, _LACE, (HX - 8, HY + 11), 3, 2)
    pygame.draw.circle(surf, _LACE_H, (HX - 9, HY + 10), 1)

    # ── richer TRICORN: built on the ORIGINAL three-cornered brim read (which the
    #    R1 double-outline broke into a Napoleon bicorn). A tricorn has a
    #    front-dipped point and TWO low side corners that fold up — NOT two tall
    #    mirrored horns. The brim is asymmetric: the near (right) front dips into a
    #    point, the back-left corner is a single low fold. Side apexes sit ~3-4px
    #    LOWER than R1 and the crown is rounded so it never silhouettes as horns.
    cy = CROWN_Y - 3
    brim = [(HX - 17, cy + 6), (HX - 6, cy - 2), (HX - 1, cy + 1),
            (HX + 5, cy - 3), (HX + 16, cy + 5),
            (HX + 6, cy + 10), (HX - 6, cy + 10)]
    _poly(surf, _FELT_D, brim)
    inner = [(HX - 14, cy + 5), (HX - 5, cy + 0), (HX - 1, cy + 2),
             (HX + 4, cy - 1), (HX + 13, cy + 4),
             (HX + 5, cy + 8), (HX - 5, cy + 8)]
    _poly(surf, _FELT, inner)
    # Rounded felt crown so the dark felt doesn't read as a flat void OR a horn.
    pygame.draw.circle(surf, _FELT, (HX - 1, cy + 1), 6)
    _poly(surf, _FELT_H, [(HX - 4, cy - 2), (HX + 2, cy - 3),
                          (HX + 1, cy + 1), (HX - 3, cy + 1)])
    # OUTER gold lace tracing the three-cornered brim edge — the primary read.
    outer = [(HX - 15, cy + 5), (HX - 5, cy - 1), (HX - 1, cy + 1),
             (HX + 4, cy - 2), (HX + 14, cy + 4)]
    pygame.draw.lines(surf, _LACE, False, outer, 2)
    pygame.draw.lines(surf, _LACE_H, False,
                      [(HX - 13, cy + 4), (HX - 5, cy - 1), (HX - 1, cy + 1)], 1)
    # SECOND lace rope set INSIDE the brim (a band wrapping the crown base), NOT a
    # second outer horn — this is the "double lace" finery without the bicorn.
    pygame.draw.lines(surf, _LACE, False,
                      [(HX - 11, cy + 7), (HX - 1, cy + 4), (HX + 10, cy + 6)], 2)

    # ── white skull cockade dead-centre-front — the ANCHOR. A THIN 1px gold ring
    #    (not a filled disc that ate the bone at 40px) so the white skull stays the
    #    2nd-brightest, most-central shape; two 2px dark eye sockets with +1px
    #    spacing so two distinct dark eyes survive downscale.
    sx, sy = HX, cy + 2
    pygame.draw.circle(surf, _SKULL, (sx, sy), 4)             # bone
    pygame.draw.circle(surf, _LACE, (sx, sy), 5, 1)           # thin 1px gold ring
    _poly(surf, _SKULL, [(sx - 3, sy + 2), (sx + 3, sy + 2),
                         (sx + 1, sy + 5), (sx - 1, sy + 5)])  # jaw
    pygame.draw.circle(surf, _DARKEYE, (sx - 3, sy - 1), 2)   # +1px wider spacing
    pygame.draw.circle(surf, _DARKEYE, (sx + 3, sy - 1), 2)


build = store_skins._make_skin(_paint)
