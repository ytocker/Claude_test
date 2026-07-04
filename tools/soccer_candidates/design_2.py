"""Soccer v11 Design 2 — THE GOALKEEPER.

Bright lime-green keeper field — no other sport uses this colour, so it's
an instant goalkeeper tell even at 10px. The torso AND near wing are lime,
so they fuse into one continuous jersey. A single oversized keeper glove
at the leading wingtip is the hero prop: no ball needed, the glove IS the
identity.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D,
)

_LIME    = ( 50, 200,  80)
_LIME_D  = ( 20, 140,  50)
_GLOVE_W = (248, 250, 245)   # near-white palm — max contrast against lime
_GLOVE_S = (205, 212, 200)   # palm shadow / seam
_BAND    = ( 26,  26,  34)   # chunky dark wristband
_BLACK   = ( 20,  20,  28)
_WHITE   = (245, 246, 250)

_PAL = _pal(
    tail=[(200,30,40),(240,95,40),(255,160,55),(255,220,80)],
    tail_line=(170,25,25),
    body_shadow=( 20,140, 50),
    body_main  =( 50,200, 80),
    body_chest =( 70,220, 95),
    body_belly =( 35,165, 60),
    sheen=(150,255,150,60),
    # Near wing recoloured lime so torso + wing read as one keeper field.
    wing_main=_LIME, wing_dark=_LIME_D,
    wing_secondary=(80,220,100), wing_tip=(30,170,60),
    wing_highlight=(150,255,170),
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
    # Dark-lime oval outline anchors the bright keeper field.
    pygame.draw.ellipse(surf, _LIME_D, (BCX-19,BCY-14,38,28), 1)

    # Black crew collar — separates lime jersey from red macaw head.
    pygame.draw.line(surf, _BLACK, (BCX-8, BCY-13), (BCX+10, BCY-13), 3)
    pygame.draw.line(surf, _BLACK, (BCX-7, BCY-12), (BCX+9,  BCY-12), 2)

    # Bold white "1" centred on the lime chest — serif feet so a lone
    # vertical bar still reads as a number at 40px.
    pygame.draw.line(surf, _WHITE, (BCX, BCY-8), (BCX, BCY+3), 3)
    pygame.draw.line(surf, _WHITE, (BCX-3, BCY-7), (BCX, BCY-8), 3)  # flag
    pygame.draw.line(surf, _WHITE, (BCX-3, BCY-8), (BCX+3, BCY-8), 2)  # top serif
    pygame.draw.line(surf, _WHITE, (BCX-3, BCY+3), (BCX+3, BCY+3), 2)  # foot serif

    # Black shorts block — single separator under the jersey.
    pygame.draw.ellipse(surf, _BLACK, (BCX-9,BCY+5,20,10))
    pygame.draw.ellipse(surf, (44,44,54), (BCX-9,BCY+5,20,10), 1)

    # HERO KEEPER GLOVE — single, oversized, leading (right) wingtip in a
    # raised "save" pose. Drawn LAST so it overlays the lime wing.
    gx, gy = BCX+13, BCY-13
    pygame.draw.rect(surf, _BLACK,   (gx-1, gy-1, 16, 22), border_radius=5)
    pygame.draw.rect(surf, _GLOVE_W, (gx,   gy,   14, 20), border_radius=4)
    # Palm shadow + finger grooves for a padded goalkeeper look.
    pygame.draw.rect(surf, _GLOVE_S, (gx+1, gy+9, 12,  6), border_radius=2)
    for fx in (gx+3, gx+7, gx+11):
        pygame.draw.line(surf, _GLOVE_S, (fx, gy+1), (fx, gy+8), 1)
    # Chunky dark wristband cuffs the glove at the wing.
    pygame.draw.rect(surf, _BAND,  (gx-1, gy+16, 16, 6), border_radius=2)
    pygame.draw.line(surf, (70,70,84), (gx, gy+18), (gx+13, gy+18), 1)


build = _make_skin(_paint, base_fn=_base)
