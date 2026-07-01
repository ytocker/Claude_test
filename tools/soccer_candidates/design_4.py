"""Soccer v11 Design 4 — THE PENALTY TAKER.

Bold red jersey to contrast with the goalkeeper's lime green and the
striker's white. Black collar separator keeps the red jersey from fusing
into the red macaw head. "7" in white. The hero prop is the soccer ball
positioned at KNEE height — reads as "about to kick" rather than stationary.
White shorts, red socks with white hoop, dark cleats.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

_RED     = (190,  20,  30)
_RED_D   = (130,  10,  18)
_WHITE   = (240, 240, 245)
_BLACK   = ( 20,  20,  28)
_CLEAT   = ( 28,  28,  36)

_PAL = _pal(
    tail=[(200,30,40),(240,95,40),(255,160,55),(255,220,80)],
    tail_line=(170,25,25),
    body_shadow=(130, 10, 18),
    body_main  =(190, 20, 30),
    body_chest =(210, 35, 45),
    body_belly =(155, 12, 22),
    sheen=(255,100,100,50),
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
    # Black separator prevents red jersey from fusing with red macaw head.
    pygame.draw.line(surf, _BLACK, (BCX-17, BCY-13), (BCX+17, BCY-13), 2)

    # White V-collar sits above the black separator — makes it read as kit.
    pygame.draw.line(surf, _WHITE, (BCX-6, BCY-12), (BCX+2, BCY-8), 2)
    pygame.draw.line(surf, _WHITE, (BCX+8, BCY-12), (BCX+2, BCY-8), 2)

    # Oval outline to anchor the red field.
    pygame.draw.ellipse(surf, _RED_D, (BCX-19,BCY-14,38,28), 1)

    # Squad "7" in white — top horizontal bar + angled drop.
    nx, ny = BCX-4, BCY-8
    pygame.draw.line(surf, _WHITE, (nx-4, ny),     (nx+4, ny),     3)
    pygame.draw.line(surf, _WHITE, (nx+4, ny),     (nx-2, ny+10),  3)
    pygame.draw.line(surf, _RED_D, (nx-5, ny-1),   (nx+5, ny-1),   1)  # crisp top edge

    # Hem seam.
    pygame.draw.ellipse(surf, _RED_D, (BCX-9,BCY+5,20,2), 1)

    # White shorts — clean contrast with red jersey.
    pygame.draw.ellipse(surf, _WHITE, (BCX-9,BCY+6,20,9))
    pygame.draw.ellipse(surf, (200,205,215), (BCX-9,BCY+6,20,9), 1)
    _poly(surf, _RED, [(BCX-1,BCY+12),(BCX+3,BCY+12),(BCX+1,BCY+15)])

    # Red socks with white hoop.
    for sx in (27, 35):
        pygame.draw.line(surf, _RED,   (sx, BCY+10), (sx, BCY+17), 4)
        pygame.draw.line(surf, _WHITE, (sx, BCY+11), (sx, BCY+13), 3)

    # Cleats.
    for cx in (23, 31):
        pygame.draw.rect(surf, _CLEAT, (cx, BCY+14, 9, 5), border_radius=2)
        pygame.draw.line(surf, _WHITE, (cx, BCY+18), (cx+8, BCY+18), 1)

    # HERO PROP — soccer ball at knee height, "about to kick" positioning.
    bx, by = BCX-16, BCY+10
    pygame.draw.circle(surf, (235,235,235), (bx, by), 7)
    pygame.draw.circle(surf, (20,20,20),    (bx, by), 7, 1)
    for px, py in [(bx-2,by-4),(bx+4,by-1),(bx+1,by+4),(bx-4,by+1)]:
        pygame.draw.circle(surf, (20,20,20), (px,py), 2)


build = _make_skin(_paint, base_fn=_base)
