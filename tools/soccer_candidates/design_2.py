"""Soccer v11 Design 2 — THE GOALKEEPER.

Bright lime-green jersey — no other sport uses this colour, so it's an
instant goalkeeper tell even at 10px. Oversized keeper gloves on the wing
tips are the hero prop. No ball needed: the gloves ARE the identity.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

_LIME    = ( 50, 200,  80)
_LIME_D  = ( 20, 140,  50)
_GLOVE   = (180, 230,  50)
_GLOVE_D = (120, 170,  20)
_GLOVE_W = (240, 255, 200)
_BLACK   = ( 20,  20,  28)
_WHITE   = (240, 240, 245)
_NUM     = (  0, 100,  30)

_PAL = _pal(
    tail=[(200,30,40),(240,95,40),(255,160,55),(255,220,80)],
    tail_line=(170,25,25),
    body_shadow=( 20,140, 50),
    body_main  =( 50,200, 80),
    body_chest =( 70,220, 95),
    body_belly =( 35,165, 60),
    sheen=(150,255,150,60),
    wing_main=BIRD_WING, wing_dark=BIRD_WING_D, wing_tip=BIRD_TIP,
    wing_secondary=(255,200,60), wing_highlight=(170,210,255),
    head_shadow=(150,15,20), head_main=BIRD_RED,
    head_cheek=(255,130,130), head_crown=(255,170,170),
    lens_frame=(255,200,50), lens_body=(20,20,30),
    lens_tint=(35,55,90,130), lens_glint=(255,255,255),
    beak_main=BIRD_BEAK, beak_dark=BIRD_BEAK_D,
    beak_gloss=(255,230,150), foot=BIRD_BEAK_D,
)

BCX, BCY = 32, 52


def _base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # Dark-green oval outline anchors the bright lime field.
    pygame.draw.ellipse(surf, _LIME_D, (BCX-19,BCY-14,38,28), 1)

    # Black crew collar — separates lime jersey from red macaw head.
    pygame.draw.line(surf, _BLACK, (BCX-8, BCY-13), (BCX+10, BCY-13), 3)
    pygame.draw.line(surf, _BLACK, (BCX-7, BCY-12), (BCX+9,  BCY-12), 2)

    # Jersey number "1" — bold vertical bar in dark green, left chest.
    pygame.draw.line(surf, _NUM, (BCX-6, BCY-8), (BCX-6, BCY+2), 3)
    pygame.draw.line(surf, _NUM, (BCX-8, BCY-8), (BCX-6, BCY-8), 2)

    # Hem seam.
    pygame.draw.ellipse(surf, _LIME_D, (BCX-9,BCY+5,20,2), 1)

    # Black shorts.
    pygame.draw.ellipse(surf, _BLACK, (BCX-9,BCY+6,20,9))
    pygame.draw.ellipse(surf, (40,40,50), (BCX-9,BCY+6,20,9), 1)
    _poly(surf, _WHITE, [(BCX-1,BCY+12),(BCX+3,BCY+12),(BCX+1,BCY+15)])

    # Lime socks with white hoop.
    for sx in (27, 35):
        pygame.draw.line(surf, _LIME,  (sx, BCY+10), (sx, BCY+17), 4)
        pygame.draw.line(surf, _WHITE, (sx, BCY+11), (sx, BCY+13), 3)

    # Cleats.
    for cx in (23, 31):
        pygame.draw.rect(surf, (28,28,36), (cx, BCY+14, 9, 5), border_radius=2)

    # KEEPER GLOVES — hero prop, drawn LAST so they overlay the wing tips.
    # Near (right) glove — large and very visible.
    pygame.draw.rect(surf, _GLOVE_D, (BCX+14, BCY-10, 12, 16), border_radius=3)
    pygame.draw.rect(surf, _GLOVE,   (BCX+15, BCY- 9, 10, 14), border_radius=2)
    pygame.draw.rect(surf, _GLOVE_W, (BCX+16, BCY- 6,  7,  8), border_radius=1)
    for fy in (BCY-4, BCY-1, BCY+2):
        pygame.draw.line(surf, _GLOVE_D, (BCX+16, fy), (BCX+22, fy), 1)
    # Far (left) glove — smaller, partially behind the body.
    pygame.draw.rect(surf, _GLOVE_D, (BCX-25, BCY-8, 10, 13), border_radius=3)
    pygame.draw.rect(surf, _GLOVE,   (BCX-24, BCY-7,  8, 11), border_radius=2)


build = _make_skin(_paint, base_fn=_base)
