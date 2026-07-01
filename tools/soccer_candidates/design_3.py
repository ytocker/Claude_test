"""Soccer v11 Design 3 — THE CAPTAIN.

Deep navy jersey with a bold white chest stripe and the #10, a large gold
captain's armband on the near wing, white shorts, navy-and-gold socks,
and a soccer ball at the feet.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

_NAVY    = ( 15,  30,  90)
_NAVY_D  = (  8,  18,  60)
_WHITE   = (235, 235, 240)
_GOLD    = (255, 200,   0)
_GOLD_D  = (180, 140,   0)
_CLEAT   = ( 28,  28,  36)

_PAL = _pal(
    tail=[(200,30,40),(240,95,40),(255,160,55),(255,220,80)],
    tail_line=(170,25,25),
    body_shadow=( 8, 18, 60),
    body_main  =(15, 30, 90),
    body_chest =(22, 45,115),
    body_belly =(10, 22, 70),
    sheen=(80,120,255,50),
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
    # Subtle dark outline so the navy oval doesn't dissolve into the sky.
    pygame.draw.ellipse(surf, _NAVY_D, (BCX-19,BCY-14,38,28), 1)

    # White V-collar — crisp against the dark jersey.
    pygame.draw.line(surf, _WHITE, (BCX-6, BCY-12), (BCX+2, BCY-8), 2)
    pygame.draw.line(surf, _WHITE, (BCX+8, BCY-12), (BCX+2, BCY-8), 2)

    # Bold white chest stripe — the graphic signature across the navy field.
    pygame.draw.line(surf, _WHITE, (BCX-18, BCY-4), (BCX+18, BCY-4), 3)
    pygame.draw.line(surf, (200,205,220), (BCX-18,BCY-5), (BCX+18,BCY-5), 1)

    # Squad "10" in white — left of centre on the stripe.
    pygame.draw.line(surf, _WHITE, (BCX-10, BCY-9), (BCX-10, BCY+2), 3)
    pygame.draw.line(surf, _WHITE, (BCX-12, BCY-9), (BCX-10, BCY-9), 2)
    pygame.draw.ellipse(surf, _WHITE, (BCX-6, BCY-9, 8, 12), 2)

    # CAPTAIN'S ARMBAND — hero prop on the near (right) wing, bold gold.
    ax, ay = BCX+14, BCY-4
    pygame.draw.line(surf, _GOLD_D, (ax-5, ay-5), (ax+5, ay+5), 8)
    pygame.draw.line(surf, _GOLD,   (ax-4, ay-4), (ax+4, ay+4), 6)
    pygame.draw.line(surf, (255,235,100), (ax-4,ay-5), (ax+3,ay+2), 2)
    pygame.draw.line(surf, _NAVY,   (ax-1, ay-2), (ax-1, ay+2), 2)  # "C" mark

    # Hem seam.
    pygame.draw.ellipse(surf, (40,60,130), (BCX-9,BCY+5,20,2), 1)

    # White shorts — contrast with navy jersey.
    pygame.draw.ellipse(surf, _WHITE, (BCX-9,BCY+6,20,9))
    pygame.draw.ellipse(surf, (200,205,215), (BCX-9,BCY+6,20,9), 1)
    _poly(surf, _NAVY, [(BCX-1,BCY+12),(BCX+3,BCY+12),(BCX+1,BCY+15)])

    # Navy socks with gold hoop.
    for sx in (27, 35):
        pygame.draw.line(surf, _NAVY, (sx, BCY+10), (sx, BCY+17), 4)
        pygame.draw.line(surf, _GOLD, (sx, BCY+11), (sx, BCY+13), 3)

    # Cleats with gold sole accent.
    for cx in (23, 31):
        pygame.draw.rect(surf, _CLEAT, (cx, BCY+14, 9, 5), border_radius=2)
        pygame.draw.line(surf, _GOLD_D, (cx, BCY+18), (cx+8, BCY+18), 1)

    # Soccer ball — drawn LAST.
    bx, by = BCX-8, BCY+24
    pygame.draw.circle(surf, (235,235,235), (bx, by), 6)
    pygame.draw.circle(surf, (20,20,20),    (bx, by), 6, 1)
    for px, py in [(bx-2,by-3),(bx+3,by-1),(bx-1,by+3)]:
        pygame.draw.circle(surf, (20,20,20), (px,py), 2)


build = _make_skin(_paint, base_fn=_base)
