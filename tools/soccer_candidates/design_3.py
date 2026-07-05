"""Soccer v11 Design 3 — THE CAPTAIN.

Deep navy jersey with a hard white torso outline and a bold white chest
stripe, a gold captain's armband set on the navy upper arm, white shorts,
navy-and-gold socks, and a soccer ball at the feet.
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
    # Neutral blue secondary so the jersey's only gold is the captain's mark.
    wing_secondary=(120,160,200), wing_highlight=(170,210,255),
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
    # Hard white torso outline traces the navy jersey so it separates cleanly
    # from the blue macaw wing behind it — the kit reads as a worn garment,
    # not a recolour of the body.
    torso = (BCX-19, BCY-14, 38, 28)
    pygame.draw.ellipse(surf, _WHITE, torso, 2)

    # White V-collar — crisp against the dark jersey.
    pygame.draw.line(surf, _WHITE, (BCX-6, BCY-12), (BCX+2, BCY-8), 2)
    pygame.draw.line(surf, _WHITE, (BCX+8, BCY-12), (BCX+2, BCY-8), 2)

    # Bold white chest stripe — the lone graphic signature across the navy
    # field (no number, which would smear into the stripe at this scale).
    pygame.draw.line(surf, _WHITE, (BCX-18, BCY-4), (BCX+18, BCY-4), 3)
    pygame.draw.line(surf, (200,205,220), (BCX-18,BCY-5), (BCX+18,BCY-5), 1)

    # CAPTAIN'S ARMBAND — a short horizontal gold bar band on the navy upper
    # arm, framed above and below by navy so it never blends into the wing.
    ax0, ax1, ay = BCX+8, BCX+16, BCY-6
    pygame.draw.line(surf, _NAVY_D, (ax0, ay-2), (ax1, ay-2), 1)
    pygame.draw.line(surf, _GOLD,   (ax0, ay),   (ax1, ay),   3)
    pygame.draw.line(surf, (255,235,100), (ax0, ay-1), (ax1-2, ay-1), 1)
    pygame.draw.line(surf, _NAVY_D, (ax0, ay+2), (ax1, ay+2), 1)
    pygame.draw.line(surf, _NAVY,   (ax0+3, ay-1), (ax0+3, ay+1), 1)  # "C" mark

    # Hem seam.
    pygame.draw.ellipse(surf, (40,60,130), (BCX-9,BCY+5,20,2), 1)

    # White shorts — contrast with navy jersey.
    pygame.draw.ellipse(surf, _WHITE, (BCX-9,BCY+6,20,9))
    pygame.draw.ellipse(surf, (200,205,215), (BCX-9,BCY+6,20,9), 1)
    _poly(surf, _NAVY, [(BCX-1,BCY+12),(BCX+3,BCY+12),(BCX+1,BCY+15)])

    # Navy socks with a single gold hoop — the only other gold on the kit.
    for sx in (27, 35):
        pygame.draw.line(surf, _NAVY, (sx, BCY+10), (sx, BCY+17), 4)
        pygame.draw.line(surf, _GOLD, (sx, BCY+11), (sx, BCY+13), 3)

    # Cleats — matte, no gold sole so the armband stays the eye's gold anchor.
    for cx in (23, 31):
        pygame.draw.rect(surf, _CLEAT, (cx, BCY+14, 9, 5), border_radius=2)

    # Soccer ball — drawn LAST, the clearest soccer signal.
    bx, by = BCX-8, BCY+24
    pygame.draw.circle(surf, (235,235,235), (bx, by), 6)
    pygame.draw.circle(surf, (20,20,20),    (bx, by), 6, 1)
    for px, py in [(bx-2,by-3),(bx+3,by-1),(bx-1,by+3)]:
        pygame.draw.circle(surf, (20,20,20), (px,py), 2)


build = _make_skin(_paint, base_fn=_base)
