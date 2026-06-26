"""DESIGN 5 — THE ULTRA FAN (Soccer / Football — supporter, v2).

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted as a match-day terrace fan rather than a player: the SET's
only NON-player. The read is carried by KNITWEAR + a club SCARF, not an athletic
kit. The hero is a gold club SCARF looped once at the neck with two staggered
fringed tails draped down the chest (drawn LAST, in front of everything), under
a full bobble HAT on the crown.

v2 fix: the jersey is anchored on the HEAD anchors (HX,HY) using the proven
baseball jersey polygon (tools/sports_candidates/design_4.py) so the torso sits
where the bird's body actually is — jersey top y=HY+8 (=49), hem y=HY+23 (=64).
Nothing from the jersey rises above y=49. The crown wears a full rounded bobble
HAT dome (NOT a flat headband) with a pompom standing proud on top.

The supporter speaks two stripe languages on purpose: the replica TOP is white
HOOPS on red, while the chunky SCARF is solid GOLD. Red shirt vs gold scarf is
what splits the chest into two clean reads at 40px.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Club red + gold. Three values per material keep the knit reading round, not
# flat, after the 40px downscale.
_RED      = (204, 34, 34)        # #CC2222 club red — jersey field, hat, socks
_RED_D    = (132, 20, 20)        # deep red shadow / linework
_RED_H    = (236, 92, 78)        # red highlight (hat sheen)
_WHITE    = (244, 244, 248)      # #F4F4F8 jersey hoops / hat rim / pompom
_WHITE_D  = (176, 178, 192)      # cool white shade
_GOLD     = (232, 178, 58)       # #E8B23A scarf face (the hero gold)
_GOLD_H   = (255, 218, 120)      # gold glint
_GOLD_D   = (150, 108, 24)       # gold shadow so the scarf reads as draped fabric
_NAVY     = (28, 34, 68)         # #1C2244 shorts / sock pillars / boots
_NAVY_H   = (74, 84, 132)        # navy rim glint
_DARK     = (26, 26, 34)         # near-black boot body


def _paint(surf, _a):
    # --- WHITE-hooped club JERSEY over the torso (HX,HY anchors) -----------------
    # Proven baseball jersey footprint, recoloured: red field + horizontal white
    # hoops. Jersey top sits at HY+8 (y=49), hem at HY+23 (y=64) — nothing rises
    # above y=49, so it never balloons up into the macaw's chin/cheek.
    jersey = [(HX - 13, HY + 8), (HX - 14, HY + 18), (HX - 10, HY + 23),
              (HX + 8, HY + 23), (HX + 11, HY + 18), (HX + 9, HY + 8)]
    _poly(surf, _RED, jersey)
    # Three bold WHITE hoops, each 3px tall, evenly spaced from HY+10..HY+21.
    # Clipped to the jersey footprint so the bars never leak past the cloth edge.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(HX - 14, HY + 8, 26, 16))
    for sy in (HY + 10, HY + 15, HY + 20):
        pygame.draw.rect(surf, _WHITE, (HX - 14, sy, 26, 3))
        pygame.draw.line(surf, _WHITE_D, (HX - 14, sy + 3), (HX + 12, sy + 3), 1)
    surf.set_clip(clip_prev)
    # Off-side shade so the jersey reads as a rounded torso, not a flat card.
    _poly(surf, _RED_D, [(HX + 5, HY + 9), (HX + 11, HY + 18),
                         (HX + 8, HY + 23), (HX + 6, HY + 22)])
    pygame.draw.polygon(surf, _RED_D, jersey, 1)

    # --- Dark SHORTS band under the jersey hem (HY+23..26) -----------------------
    pygame.draw.rect(surf, _NAVY, (HX - 11, HY + 23, 20, 4), border_radius=1)
    pygame.draw.line(surf, _NAVY_H, (HX - 10, HY + 23), (HX + 7, HY + 23), 1)

    # --- SOCKS — two navy pillars (HY+13..HY+24) with a single white hoop -------
    for sx in (HX - 9, HX + 3):
        pygame.draw.rect(surf, _NAVY, (sx, HY + 13, 5, 11), border_radius=1)
        pygame.draw.line(surf, _NAVY_H, (sx, HY + 14), (sx, HY + 23), 1)
        pygame.draw.line(surf, _WHITE, (sx, HY + 15), (sx + 4, HY + 15), 2)

    # --- BOOTS at the feet line (HY+24..27) with a sole tick --------------------
    for fx in (HX - 11, HX + 1):
        pygame.draw.rect(surf, _DARK, (fx, HY + 24, 9, 3), border_radius=2)
        pygame.draw.line(surf, _NAVY_H, (fx + 1, HY + 24), (fx + 7, HY + 24), 1)
        # Sole tick under the boot — the football-boot read.
        pygame.draw.line(surf, _DARK, (fx, HY + 27), (fx + 8, HY + 27), 1)

    # --- BOBBLE HAT on the crown (FULL rounded dome — NOT a band) ----------------
    # A full rounded cap covering the crown with a white rim line, and a pompom
    # standing proud on its very top. This is a hat shape, not a horizontal band.
    pygame.draw.ellipse(surf, _RED_D, (HX - 13, CROWN_Y - 9, 26, 19))   # rim halo
    pygame.draw.ellipse(surf, _RED, (HX - 12, CROWN_Y - 8, 24, 18))
    pygame.draw.ellipse(surf, _RED_H, (HX - 8, CROWN_Y - 6, 11, 6))      # dome sheen
    # White rim line hugging the cap's lower edge so the hat separates from crown.
    pygame.draw.arc(surf, _WHITE, (HX - 12, CROWN_Y - 8, 24, 18),
                    3.34, 6.08, 2)
    # Pompom standing on the very top — white ball with a dark ring.
    pygame.draw.circle(surf, _RED_D, (HX, CROWN_Y - 8), 5)
    pygame.draw.circle(surf, _WHITE, (HX, CROWN_Y - 8), 4)
    pygame.draw.circle(surf, _WHITE_D, (HX + 1, CROWN_Y - 6), 1)

    # --- SCARF (THE HERO — drawn LAST so it drapes in FRONT of everything) -------
    # A gold club scarf looped once at the neck, with two staggered hanging tails.
    # Gold shadow + bright gold face on every shape so the knit reads as fabric
    # draped over the shirt, not a flat sticker. Loop sits at HY+5..11.
    loop = [(HX - 13, HY + 5), (HX + 12, HY + 5), (HX + 12, HY + 11),
            (HX + 3, HY + 11), (HX, HY + 9), (HX - 3, HY + 11), (HX - 12, HY + 11)]
    _poly(surf, _GOLD_D, loop)
    loop_in = [(HX - 11, HY + 6), (HX + 10, HY + 6), (HX + 10, HY + 10),
               (HX + 3, HY + 10), (HX, HY + 8), (HX - 3, HY + 10), (HX - 10, HY + 10)]
    _poly(surf, _GOLD, loop_in)
    pygame.draw.line(surf, _GOLD_H, (HX - 10, HY + 6), (HX + 9, HY + 6), 1)
    pygame.draw.polygon(surf, _GOLD_D, loop, 1)

    def _tail(x0, y0, x1, y1, w):
        # A gold knit strap draped down the chest: a dark gold underlay for
        # thickness, a bright gold face, and a notched fringe at the hanging end.
        half = w // 2
        pygame.draw.line(surf, _GOLD_D, (x0, y0), (x1, y1), w)
        pygame.draw.line(surf, _GOLD, (x0, y0), (x1, y1), max(2, w - 2))
        pygame.draw.line(surf, _GOLD_H, (x0 - half + 1, y0), (x1 - half + 1, y1), 1)
        # Fringe-tick ends — two short gold teeth past the hem so it frays.
        for fx in (x1 - half, x1, x1 + half):
            pygame.draw.line(surf, _GOLD_D, (fx, y1), (fx, y1 + 2), 1)
        pygame.draw.line(surf, _GOLD, (x1 - half, y1 + 1), (x1 + half, y1 + 1), 1)

    # Near tail — longer, drops to ~HY+24, 5px wide. Far tail — shorter (2px
    # above), ~HY+22, 4px wide. Staggered length reads them as two streamers.
    _tail(HX + 2, HY + 10, HX + 4, HY + 24, 5)
    _tail(HX - 6, HY + 10, HX - 10, HY + 22, 4)


build = store_skins._make_skin(_paint)
