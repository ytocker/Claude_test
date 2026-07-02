"""THE LAKER DUNKER — basketball candidate DESIGN 4 of 5, purple-body rebuild.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
roster is untouched.

Why the purple-body take: the other basketball candidates lean on white or
orange kits, so this one claims the single most iconic hoops silhouette — the
purple-and-gold Lakers look — by recolouring Pip's whole torso Lakers purple via
_pal and reserving GOLD for every uniform structure a fan reads instantly: a
sleeveless gold-piped tank, a bold gold "24" on the chest, gold-striped baggy
shorts, and white-and-gold high-tops. The #1 identity prop is the basketball
raised to WING level in a dunk pose — drawn last so nothing overlaps it, so the
read is not just "athlete" but "the dunk". Pip's scarlet macaw head/beak/eye stay
in the open so it still reads as a parrot wearing a uniform.
"""
import math

import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D,
                       BIRD_TIP)

# Lakers-purple body: the jersey IS the body, so the palette recolours the whole
# torso purple and keeps the scarlet macaw head/beak so it still reads as Pip.
# The gold + light-blue wing accents echo the trim without stealing the read.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(60, 12, 95),
    body_main=(90, 20, 140),         # Lakers purple
    body_chest=(110, 28, 165),
    body_belly=(70, 14, 110),
    sheen=(180, 100, 255, 50),
    wing_main=BIRD_WING, wing_dark=BIRD_WING_D, wing_tip=BIRD_TIP,
    wing_secondary=(255, 200, 60), wing_highlight=(170, 210, 255),
    head_shadow=(150, 15, 20), head_main=BIRD_RED,
    head_cheek=(255, 130, 130), head_crown=(255, 170, 170),
    lens_frame=(255, 200, 50), lens_body=(20, 20, 30),
    lens_tint=(35, 55, 90, 130), lens_glint=(255, 255, 255),
    beak_main=BIRD_BEAK, beak_dark=BIRD_BEAK_D,
    beak_gloss=(255, 230, 150), foot=BIRD_BEAK_D,
)

# Gold is the accent value carried against the purple jersey body; a two-value
# gold keeps trim and numerals reading round at the 40px downscale.
_PURPLE   = (90, 20, 140)
_PURPLE_D = (60, 12, 95)
_GOLD     = (240, 180, 0)
_GOLD_D   = (180, 130, 0)
_WHITE    = (245, 245, 248)


def _base(angle_deg):
    """Purple-jersey Pip body — the Lakers recolour that _paint lands the gold
    accents on top of."""
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # Thin dark oval outline so the purple jersey keeps a crisp edge against a
    # bright day sky.
    pygame.draw.ellipse(surf, _PURPLE_D, (BCX - 19, BCY - 14, 38, 28), 1)

    # SLEEVELESS TANK — gold armhole piping on both shoulders (a two-value line
    # so the strap reads round), plus a gold collar neckline. No sleeves is the
    # basketball-vs-soccer tell.
    pygame.draw.line(surf, _GOLD_D, (BCX - 15, BCY - 13), (BCX - 11, BCY + 4), 3)
    pygame.draw.line(surf, _GOLD,   (BCX - 14, BCY - 13), (BCX - 10, BCY + 4), 2)
    pygame.draw.line(surf, _GOLD_D, (BCX + 13, BCY - 13), (BCX + 9, BCY + 4), 3)
    pygame.draw.line(surf, _GOLD,   (BCX + 12, BCY - 13), (BCX + 8, BCY + 4), 2)
    pygame.draw.line(surf, _GOLD,   (BCX - 6, BCY - 13), (BCX + 4, BCY - 13), 2)

    # "24" in gold on the purple chest — the retired-jersey read. Bold strokes so
    # the numerals survive the downscale instead of collapsing to noise.
    nx, ny = BCX - 5, BCY - 3
    pygame.draw.line(surf, _GOLD_D, (nx - 4, ny - 7), (nx + 3, ny - 7), 4)   # shadow
    pygame.draw.line(surf, _GOLD, (nx - 4, ny - 8), (nx + 3, ny - 8), 3)     # top bar
    pygame.draw.line(surf, _GOLD, (nx + 3, ny - 8), (nx - 3, ny), 3)         # diagonal
    pygame.draw.line(surf, _GOLD, (nx - 4, ny), (nx + 3, ny), 3)             # mid bar
    pygame.draw.line(surf, _GOLD, (nx - 4, ny), (nx - 4, ny + 6), 3)         # left drop
    pygame.draw.line(surf, _GOLD, (nx - 4, ny + 6), (nx + 3, ny + 6), 3)     # bottom
    nx2 = nx + 10
    pygame.draw.line(surf, _GOLD, (nx2 - 3, ny - 8), (nx2 - 3, ny), 3)       # left stem
    pygame.draw.line(surf, _GOLD, (nx2 - 3, ny), (nx2 + 3, ny), 3)           # cross bar
    pygame.draw.line(surf, _GOLD, (nx2 + 3, ny - 8), (nx2 + 3, ny + 6), 3)   # right stem

    # Hem seam separating tank from shorts.
    pygame.draw.line(surf, _GOLD_D, (BCX - 12, BCY + 5), (BCX + 11, BCY + 5), 1)

    # Purple baggy shorts with a gold side stripe down each leg.
    pygame.draw.ellipse(surf, _PURPLE, (BCX - 10, BCY + 5, 22, 12))
    pygame.draw.ellipse(surf, _PURPLE_D, (BCX - 10, BCY + 5, 22, 12), 1)
    pygame.draw.line(surf, _GOLD, (BCX + 10, BCY + 6), (BCX + 10, BCY + 16), 2)
    pygame.draw.line(surf, _GOLD, (BCX - 12, BCY + 6), (BCX - 12, BCY + 16), 2)

    # White + gold high-top sneakers with a purple tongue — chunky ankle collars
    # so the shoe shape survives the downscale.
    for hx in (22, 30):
        pygame.draw.rect(surf, (200, 200, 200), (hx, BCY + 15, 10, 4), border_radius=1)
        pygame.draw.rect(surf, _WHITE, (hx, BCY + 11, 10, 5), border_radius=2)
        pygame.draw.ellipse(surf, _WHITE, (hx + 1, BCY + 9, 8, 5))
        pygame.draw.line(surf, _GOLD, (hx + 1, BCY + 13), (hx + 8, BCY + 13), 1)
        pygame.draw.line(surf, _PURPLE, (hx + 4, BCY + 9), (hx + 4, BCY + 12), 2)

    # BASKETBALL raised to DUNK HEIGHT — drawn LAST so nothing overlaps it. The
    # ball rides up beside the near wing so the pose reads "the dunk", the single
    # loudest hoops signal, and the seam arcs give it round volume at 40px.
    bx, by = BCX + 14, BCY - 6
    pygame.draw.circle(surf, (230, 115, 30), (bx, by), 7)
    pygame.draw.circle(surf, (20, 20, 20), (bx, by), 7, 1)
    pygame.draw.line(surf, (20, 20, 20), (bx, by - 7), (bx, by + 7), 1)
    pygame.draw.arc(surf, (20, 20, 20), (bx - 9, by - 7, 12, 14), 0.3, math.pi - 0.3, 1)
    pygame.draw.arc(surf, (20, 20, 20), (bx - 3, by - 7, 12, 14), math.pi + 0.3, 2 * math.pi - 0.3, 1)


build = _make_skin(_paint, base_fn=_base)
