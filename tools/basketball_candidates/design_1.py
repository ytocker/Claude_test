"""THE NBA HOME — basketball candidate DESIGN 1 of 5, white-body rebuild.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
roster is untouched.

Why the white-body take: an all-orange tank read as a soccer jersey. An NBA
HOME uniform is WHITE — so this build recolours Pip's whole body to a white
jersey via _pal, and reserves orange for the accent structures a hoops kit owns
and soccer never does: sleeveless shoulder straps over a bare-shoulder cut, a
single bold jersey number, baggy side-striped shorts, chunky ankle-collar high-tops,
and — the #1 identity prop — an orange basketball tucked at the feet, drawn
last so nothing overlaps it. Pip's scarlet macaw head/beak/eye stay in the open
above the white jersey, so it still reads as a parrot wearing a uniform.
"""
import math

import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D,
                       BIRD_TIP)

# White NBA-home body: the jersey IS the body, so the palette recolours the
# whole torso off-white and keeps the scarlet macaw head/beak so it still reads
# as Pip. A cool grey shadow keeps the white from turning muddy.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(185, 188, 205),
    body_main=(245, 245, 248),       # white jersey
    body_chest=(252, 252, 255),
    body_belly=(215, 218, 230),
    sheen=(255, 255, 255, 100),
    wing_main=BIRD_WING, wing_dark=BIRD_WING_D, wing_tip=BIRD_TIP,
    wing_secondary=(255, 200, 60), wing_highlight=(170, 210, 255),
    head_shadow=(150, 15, 20), head_main=BIRD_RED,
    head_cheek=(255, 130, 130), head_crown=(255, 170, 170),
    lens_frame=(255, 200, 50), lens_body=(20, 20, 30),
    lens_tint=(35, 55, 90, 130), lens_glint=(255, 255, 255),
    beak_main=BIRD_BEAK, beak_dark=BIRD_BEAK_D,
    beak_gloss=(255, 230, 150), foot=BIRD_BEAK_D,
)

# Court palette — orange is the accent value against the white jersey body.
_ORANGE   = (210, 85, 20)            # NBA jersey orange
_ORANGE_D = (150, 55, 10)            # dark orange (strap depth / trim)
_WHITE    = (245, 245, 248)
_BLACK    = (20, 20, 28)
_SOLE     = (160, 162, 170)          # rubber sole grey


def _base(angle_deg):
    """White-jersey Pip body — the NBA-home uniform recolour that _paint lands
    the orange accents on top of."""
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # ── Dark oval outline (2px) so the white jersey holds against a bright day
    #    sky instead of dissolving into the clouds.
    pygame.draw.ellipse(surf, (155, 158, 175), (BCX - 19, BCY - 14, 38, 28), 2)

    # ── SLEEVELESS TANK straps — two thick orange strips framing the white
    #    chest, running collar-to-armpit so the bare-shoulder tank silhouette
    #    registers. NO SLEEVES is the basketball-vs-soccer tell.
    pygame.draw.line(surf, _ORANGE, (BCX - 14, BCY - 13), (BCX - 10, BCY + 4), 4)
    pygame.draw.line(surf, _ORANGE, (BCX + 12, BCY - 13), (BCX + 8, BCY + 4), 4)
    # Dark strap edges for depth.
    pygame.draw.line(surf, _ORANGE_D, (BCX - 16, BCY - 13), (BCX - 12, BCY + 4), 1)
    pygame.draw.line(surf, _ORANGE_D, (BCX + 14, BCY - 13), (BCX + 10, BCY + 4), 1)

    # ── JERSEY NUMBER "3" — one bold digit reads at 40px where two collapse.
    #    Drawn straight on the white jersey (two horizontal bars + a right
    #    vertical connecting them) with a dark drop-shadow for lift.
    for dx, dy, col in ((1, 1, _ORANGE_D), (0, 0, _ORANGE)):
        nx, ny = BCX + 2 + dx, BCY + dy
        pygame.draw.line(surf, col, (nx - 5, ny - 6), (nx + 4, ny - 6), 4)
        pygame.draw.line(surf, col, (nx - 5, ny), (nx + 4, ny), 4)
        pygame.draw.line(surf, col, (nx - 5, ny + 6), (nx + 4, ny + 6), 4)
        pygame.draw.line(surf, col, (nx + 4, ny - 6), (nx + 4, ny + 6), 4)

    # ── Tank HEM seam.
    pygame.draw.line(surf, _ORANGE_D, (BCX - 10, BCY + 5), (BCX + 8, BCY + 5), 1)

    # ── BAGGY SHORTS — a distinct light-grey value from the white jersey so the
    #    two garments don't blur into one blob; longer than a soccer kit's, with
    #    orange side stripes.
    pygame.draw.ellipse(surf, (210, 212, 222), (BCX - 10, BCY + 5, 22, 12))
    pygame.draw.ellipse(surf, (175, 178, 192), (BCX - 10, BCY + 5, 22, 12), 1)
    pygame.draw.line(surf, _ORANGE, (BCX + 10, BCY + 6), (BCX + 10, BCY + 16), 2)
    pygame.draw.line(surf, _ORANGE, (BCX - 12, BCY + 6), (BCX - 12, BCY + 16), 2)

    # ── HIGH-TOP SNEAKERS — chunkier than cleats, with an ankle collar bump
    #    above a thick rubber sole. A sneaker, never a cleat.
    for hx in (22, 30):
        pygame.draw.rect(surf, _SOLE, (hx, BCY + 15, 10, 4), border_radius=1)
        pygame.draw.rect(surf, _WHITE, (hx, BCY + 11, 10, 5), border_radius=2)
        pygame.draw.ellipse(surf, _WHITE, (hx + 1, BCY + 9, 8, 5))
        pygame.draw.line(surf, _ORANGE, (hx + 1, BCY + 13), (hx + 8, BCY + 13), 1)

    # ── BASKETBALL — the #1 identity prop, drawn LAST so nothing overlaps it
    #    and sized/placed to clear the feet fully below the body. Hot-orange
    #    sphere (reads distinctly from the white jersey) with the classic
    #    vertical seam + two curved side seams and a white specular dot.
    bx, by = BCX - 10, BCY + 26
    pygame.draw.circle(surf, (255, 140, 40), (bx, by), 9)
    pygame.draw.circle(surf, (20, 20, 20), (bx, by), 9, 1)
    pygame.draw.line(surf, (20, 20, 20), (bx, by - 9), (bx, by + 9), 1)
    pygame.draw.arc(surf, (20, 20, 20), (bx - 12, by - 9, 15, 18), 0.3, math.pi - 0.3, 1)
    pygame.draw.arc(surf, (20, 20, 20), (bx - 3, by - 9, 15, 18), math.pi + 0.3, 2 * math.pi - 0.3, 1)
    pygame.draw.circle(surf, (255, 255, 255), (bx - 3, by - 3), 2)


build = store_skins._make_skin(_paint, base_fn=_base)
