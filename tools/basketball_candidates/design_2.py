"""THE ROAD WARRIOR — the basketball candidate (DESIGN 2 of 5).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
roster is untouched.

Concept: the dark AWAY-jersey look. Where the other kits lean bright/home,
this one re-plumages Pip's BODY near-black through the palette system so the
uniform reads as a deep away sweater — the scarlet macaw head still crowns it,
but the torso is jersey black. The #1 identity prop is a BASKETBALL held at
DRIBBLE HEIGHT (thigh level, off the near side), drawn LAST so it reads as the
ball being worked mid-motion, not a static logo. White carries every uniform
tell (armhole piping, blocky squad "7", side stripes) so the kit pops off the
black body, and chrome soles + ankle bumps make the high-tops read at 40px.
"""
import math

import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

BCX, BCY = 32, 52

# Near-black away-jersey re-plumage: the torso goes deep black so the white
# uniform marks (piping / number / stripes) and the warm basketball are the
# highest-value notes. The head keeps the scarlet macaw so Pip is still Pip;
# gold aviators become the road-warrior's tinted shades.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(10, 10, 16),
    body_main=(22, 22, 30),          # deep black jersey
    body_chest=(32, 32, 42),
    body_belly=(14, 14, 20),
    sheen=(80, 80, 120, 40),
    wing_main=(40, 40, 50),          # dark, near-black — reads as the jersey
    wing_dark=(25, 25, 32),
    wing_tip=(55, 55, 68),
    wing_secondary=(70, 70, 88),     # desaturated dark, no gold
    wing_highlight=(90, 92, 110),    # cool-grey, no blue
    head_shadow=(150, 15, 20), head_main=BIRD_RED,
    head_cheek=(255, 130, 130), head_crown=(255, 170, 170),
    lens_frame=(255, 200, 50), lens_body=(20, 20, 30),
    lens_tint=(35, 55, 90, 130), lens_glint=(255, 255, 255),
    beak_main=BIRD_BEAK, beak_dark=BIRD_BEAK_D,
    beak_gloss=(255, 230, 150), foot=BIRD_BEAK_D,
)

# White carries every uniform tell against the black jersey; chrome silvers the
# high-top soles/ankle bumps so the shoes read as more than a dark lump.
_WHITE   = (240, 240, 245)
_BLACK_J = (22, 22, 30)              # jersey black
_CHROME  = (180, 185, 200)          # sneaker chrome / silver
_DARK    = (10, 10, 16)


def _base(angle_deg):
    # Black-jerseyed body, scarlet macaw head, tinted road shades kept on.
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # Thin cool outline around the torso so the dark away jersey separates from a
    # dark night sky instead of dissolving into it.
    pygame.draw.ellipse(surf, (80, 80, 100), (BCX - 19, BCY - 14, 38, 28), 1)

    # Sleeveless tank armholes — one clean white piping line per armhole tracing
    # where the arms pass through the vest, now that the darkened wing lets a
    # single solid line read. The basketball-kit tell that says "singlet".
    pygame.draw.line(surf, _WHITE, (BCX - 18, BCY - 13), (BCX - 12, BCY + 3), 2)
    pygame.draw.line(surf, _WHITE, (BCX + 16, BCY - 13), (BCX + 10, BCY + 3), 2)

    # Squad "7" — large white blocky digit centred on the dark chest, with a
    # near-black drop shadow so it stays crisp against the jersey at 40px.
    nx, ny = BCX + 1, BCY - 4
    pygame.draw.line(surf, _DARK, (nx - 6, ny - 8 + 1), (nx + 6, ny - 8 + 1), 4)
    pygame.draw.line(surf, _DARK, (nx + 6, ny - 8 + 1), (nx - 2, ny + 6 + 1), 4)
    pygame.draw.line(surf, _WHITE, (nx - 6, ny - 8), (nx + 6, ny - 8), 4)
    pygame.draw.line(surf, _WHITE, (nx + 6, ny - 8), (nx - 2, ny + 6), 4)

    # Hem seam under the number so the jersey reads as a garment edge, not paint.
    pygame.draw.line(surf, (50, 50, 65), (BCX - 12, BCY + 5), (BCX + 12, BCY + 5), 1)

    # Baggy black shorts with white side stripes — the second half of the kit.
    pygame.draw.ellipse(surf, _BLACK_J, (BCX - 10, BCY + 5, 22, 12))
    pygame.draw.ellipse(surf, (50, 50, 65), (BCX - 10, BCY + 5, 22, 12), 1)
    pygame.draw.line(surf, _WHITE, (BCX + 10, BCY + 6), (BCX + 10, BCY + 16), 2)
    pygame.draw.line(surf, _WHITE, (BCX - 12, BCY + 6), (BCX - 12, BCY + 16), 2)

    # Black high-tops with a chrome sole slab + ankle bump so the shoes read as
    # sneakers, not black blobs; a chrome lace-line ties each one together.
    for hx in (22, 30):
        pygame.draw.rect(surf, _CHROME, (hx, BCY + 15, 10, 5), border_radius=1)
        pygame.draw.rect(surf, _BLACK_J, (hx, BCY + 11, 10, 5), border_radius=2)
        pygame.draw.ellipse(surf, _BLACK_J, (hx + 1, BCY + 9, 8, 5))
        pygame.draw.line(surf, _CHROME, (hx + 1, BCY + 13), (hx + 8, BCY + 13), 1)
        pygame.draw.line(surf, (220, 222, 235), (hx + 1, BCY + 10), (hx + 8, BCY + 10), 2)

    # BASKETBALL at DRIBBLE HEIGHT — the #1 identity prop, drawn LAST over
    # everything. Sat on the DARK side (against jersey/shorts, not the warm tail)
    # so its bright orange lands on high contrast; bigger + brighter than the
    # buried orange-on-orange it replaced. Bold vertical seam + two side arcs +
    # a specular highlight make it unmistakably a ball at 40px.
    bx, by = BCX + 16, BCY + 12
    pygame.draw.circle(surf, (255, 140, 40), (bx, by), 9)
    pygame.draw.circle(surf, (20, 20, 20), (bx, by), 9, 1)
    pygame.draw.line(surf, (20, 20, 20), (bx, by - 9), (bx, by + 9), 1)
    pygame.draw.arc(surf, (20, 20, 20), (bx - 11, by - 9, 14, 18), 0.3, math.pi - 0.3, 1)
    pygame.draw.arc(surf, (20, 20, 20), (bx - 3, by - 9, 14, 18),
                    math.pi + 0.3, 2 * math.pi - 0.3, 1)
    pygame.draw.circle(surf, (255, 255, 255), (bx - 3, by - 3), 2)


build = _make_skin(_paint, base_fn=_base)
