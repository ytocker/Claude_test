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
tricorn lifted off the crown with a DOUBLE bright-gold lace band, (2) the white
skull cockade dead-centre as the anchor, (3) the gold bullion epaulette + gold
coat-cuff breaking the back / wing outline so the silhouette reads WIDER and
"dressed", and (4) the wine coat panels with a gold-button row + the white lace
jabot under the beak as the close-up density. Every object is mass + one bright
accent so the stack holds when it shrinks; nothing rides near-black on the navy
store card — the felt is mid-value slate and the coat is a saturated wine, both
of which lift off both the scarlet body and the dark card.
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
# Captain's coat — saturated wine so the panels read as cloth (not body) and
# still lift off the navy card; the shadow tone seats the turn-back folds.
_COAT    = (122, 31, 40)           # #7A1F28 wine
_COAT_D  = (81, 16, 25)            # #511019 coat shadow
_COAT_H  = (162, 56, 66)           # lifted lapel edge
_DARKEYE = (40, 30, 40)


def _paint(surf, _a):
    # ── captain's coat: turned-back wine panels framing the chest, drawn FIRST
    #    so the scarlet body and the gold buttons sit on top. Body centre is
    #    ~(32, 52) in composite space; the two lapels open in a V from the
    #    shoulders down so the scarlet chest still shows between them — the coat
    #    DRESSES the bird, it doesn't repaint it.
    bcx, bcy = 32, 52
    # Near (right) front panel — the larger sweep down the belly.
    near = [(bcx + 17, bcy - 9), (bcx + 19, bcy + 2),
            (bcx + 12, bcy + 12), (bcx + 4, bcy + 13),
            (bcx + 6, bcy + 2), (bcx + 10, bcy - 6)]
    _poly(surf, _COAT_D, near)
    near_in = [(bcx + 16, bcy - 7), (bcx + 17, bcy + 1),
               (bcx + 11, bcy + 10), (bcx + 5, bcy + 11),
               (bcx + 7, bcy + 2), (bcx + 10, bcy - 4)]
    _poly(surf, _COAT, near_in)
    # Far (left) panel — narrower, peeking past the near wing so the coat wraps.
    far = [(bcx - 16, bcy - 6), (bcx - 9, bcy - 8),
           (bcx - 6, bcy + 4), (bcx - 12, bcy + 10), (bcx - 17, bcy + 2)]
    _poly(surf, _COAT_D, far)
    _poly(surf, _COAT, [(bcx - 14, bcy - 4), (bcx - 9, bcy - 6),
                        (bcx - 7, bcy + 3), (bcx - 12, bcy + 8),
                        (bcx - 15, bcy + 1)])
    # Lifted lapel edge on the near panel so the coat catches light, not mud.
    pygame.draw.lines(surf, _COAT_H, False,
                      [(bcx + 10, bcy - 5), (bcx + 16, bcy - 1),
                       (bcx + 12, bcy + 9)], 1)

    # Gold-button row down the centre placket between the lapels — three studs,
    # each a 2px gold dot with a highlight pip so the row reads as a line.
    for k, by in enumerate((bcy - 4, bcy + 1, bcy + 6)):
        pygame.draw.circle(surf, _LACE, (bcx + 8, by), 2)
        pygame.draw.circle(surf, _LACE_H, (bcx + 7, by - 1), 1)

    # ── turned-back gold CUFF at the near wing — a bright band that widens the
    #    wing outline so the bird reads "dressed" even in silhouette. Sits at the
    #    wing root over the lower body; gold so it pops on both biomes.
    wcx, wcy = 44, 50
    cuff = [(wcx - 6, wcy + 1), (wcx + 6, wcy - 4),
            (wcx + 8, wcy + 1), (wcx - 4, wcy + 6)]
    _poly(surf, _COAT_D, cuff)
    pygame.draw.line(surf, _LACE, (wcx - 5, wcy + 1), (wcx + 6, wcy - 3), 3)
    pygame.draw.line(surf, _LACE_H, (wcx - 4, wcy), (wcx + 4, wcy - 3), 1)

    # ── white lace cravat / jabot tucked under the beak, cascading down to the
    #    coat — a stack of three ruffled tiers so it reads as fabric, not a bib.
    jx, jy = HX + 10, HY + 7        # just under the beak base
    _poly(surf, _SKULL_D, [(jx - 5, jy), (jx + 5, jy),
                           (jx + 3, jy + 12), (jx - 4, jy + 11)])
    for t, (w, dy) in enumerate(((5, 0), (4, 4), (3, 8))):
        cy = jy + dy
        _poly(surf, _SKULL, [(jx - w, cy), (jx + w, cy),
                             (jx + w - 1, cy + 4), (jx, cy + 5),
                             (jx - w + 1, cy + 4)])
        pygame.draw.line(surf, _SKULL_D, (jx - w + 1, cy + 3), (jx, cy + 4), 1)
        pygame.draw.line(surf, _SKULL_D, (jx, cy + 4), (jx + w - 1, cy + 3), 1)

    # ── gold BULLION epaulette breaking the back / shoulder outline (drawn over
    #    the far shoulder so it pushes past the back silhouette — the "rank" read
    #    that no other pirate has). A gold pad with a fringe of bullion strands.
    epx, epy = HX - 16, HY + 9
    _poly(surf, _COAT_D, [(epx - 5, epy - 4), (epx + 5, epy - 5),
                          (epx + 6, epy + 2), (epx - 4, epy + 3)])
    _poly(surf, _LACE, [(epx - 4, epy - 3), (epx + 4, epy - 4),
                        (epx + 5, epy + 1), (epx - 3, epy + 2)])
    pygame.draw.line(surf, _LACE_H, (epx - 3, epy - 3), (epx + 4, epy - 3), 1)
    # Bullion fringe — short gold strands hanging off the back edge into sky.
    for fx in range(-4, 6, 2):
        pygame.draw.line(surf, _LACE, (epx + fx, epy + 2),
                         (epx + fx - 1, epy + 7), 2)
        pygame.draw.circle(surf, _LACE_H, (epx + fx - 1, epy + 7), 1)

    # ── gold hoop earring (keep the buccaneer note under the head).
    pygame.draw.circle(surf, _LACE, (HX - 8, HY + 11), 3, 2)
    pygame.draw.circle(surf, _LACE_H, (HX - 9, HY + 10), 1)

    # ── richer tricorn: deeper navy-slate felt lifted a row off the crown so the
    #    brim breaks the outline, with a DOUBLE gold lace band tracing the edge.
    cy = CROWN_Y - 3
    brim = [(HX - 18, cy + 5), (HX - 5, cy - 8), (HX + 5, cy - 9),
            (HX + 17, cy + 4), (HX + 6, cy + 10), (HX - 6, cy + 10)]
    _poly(surf, _FELT_D, brim)
    inner = [(HX - 15, cy + 4), (HX - 4, cy - 6), (HX + 3, cy - 7),
             (HX + 14, cy + 3), (HX + 5, cy + 8), (HX - 5, cy + 8)]
    _poly(surf, _FELT, inner)
    # Felt crown highlight so the dark felt doesn't read as a flat void.
    _poly(surf, _FELT_H, [(HX - 4, cy - 6), (HX + 3, cy - 7),
                          (HX + 2, cy - 3), (HX - 3, cy - 3)])
    # DOUBLE gold lace band: an outer brim trace + an inner parallel rope.
    outer = [(HX - 16, cy + 4), (HX - 4, cy - 6), (HX + 3, cy - 7),
             (HX + 15, cy + 3)]
    pygame.draw.lines(surf, _LACE, False, outer, 2)
    innerband = [(HX - 13, cy + 6), (HX - 4, cy - 3), (HX + 3, cy - 4),
                 (HX + 12, cy + 5)]
    pygame.draw.lines(surf, _LACE, False, innerband, 2)
    pygame.draw.lines(surf, _LACE_H, False,
                      [(HX - 13, cy + 3), (HX - 4, cy - 7), (HX + 3, cy - 8)], 1)

    # ── white skull cockade dead-centre-front, re-trimmed with a tiny gold edge
    #    so it reads as a jewelled badge, not a plain bone — the anchor pop.
    sx, sy = HX, cy + 1
    pygame.draw.circle(surf, _LACE, (sx, sy), 5)         # gold rim
    pygame.draw.circle(surf, _SKULL, (sx, sy), 4)        # bone
    _poly(surf, _SKULL, [(sx - 3, sy + 2), (sx + 3, sy + 2),
                         (sx + 1, sy + 5), (sx - 1, sy + 5)])  # jaw
    pygame.draw.circle(surf, _DARKEYE, (sx - 2, sy - 1), 1)
    pygame.draw.circle(surf, _DARKEYE, (sx + 2, sy - 1), 1)


build = store_skins._make_skin(_paint)
