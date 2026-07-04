"""Soccer v11 Design 4 — THE PENALTY TAKER.

A real filled kit: darker red body field with a brighter chest, white
shoulder yoke + side seams so the jersey reads as tailored fabric rather
than bare plumage. A dark V-collar separates the red head from the red
jersey. Blocky white "7" squad number. Grey shorts with a red waistband
keep the pure-white soccer ball popping off them. The hero prop is the
soccer ball at KNEE height — reads as "about to kick", drawn last so
nothing overlaps it.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

_RED       = (190,  20,  30)
_RED_D     = (130,  10,  18)
_WHITE     = (240, 240, 245)
_BLACK     = ( 20,  20,  28)
_COLLAR    = ( 30,  30,  38)
_SHORTS    = (195, 198, 210)
_SHORTS_SH = (160, 164, 180)
_WAISTBAND = (120,  12,  20)
_CLEAT     = ( 28,  28,  36)

_PAL = _pal(
    tail=[(200,30,40),(240,95,40),(255,160,55),(255,220,80)],
    tail_line=(170,25,25),
    body_shadow=(120, 8, 16),
    body_main  =(160, 18, 28),
    body_chest =(210, 40, 50),
    body_belly =(150, 12, 22),
    sheen=(255,100,100,50),
    wing_main=BIRD_WING, wing_dark=BIRD_WING_D, wing_tip=BIRD_TIP,
    wing_secondary=(255,200,60), wing_highlight=(130,160,200),
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
    # Dark filled V-collar — a clear separator so the red jersey can't fuse
    # into the red macaw head sitting right above it.
    _poly(surf, _COLLAR, [
        (BCX-9, BCY-14), (BCX+9, BCY-14),
        (BCX+3, BCY-8),  (BCX-3, BCY-8),
    ])
    pygame.draw.line(surf, _BLACK, (BCX-17, BCY-13), (BCX+17, BCY-13), 4)

    # White shoulder yoke across the top of the torso — visible kit tailoring.
    pygame.draw.line(surf, _WHITE, (BCX-14, BCY-10), (BCX+14, BCY-10), 2)
    # White side seams down the flanks of the red field.
    pygame.draw.line(surf, _WHITE, (BCX-17, BCY-12), (BCX-17, BCY+5), 2)
    pygame.draw.line(surf, _WHITE, (BCX+17, BCY-12), (BCX+17, BCY+5), 2)

    # Blocky white "7" — one thick top bar + one angled drop, dark shadow
    # underneath for contrast against the red field.
    sx, sy = BCX+2, BCY-4
    pygame.draw.line(surf, _RED_D, (sx-6, sy-8+1), (sx+6, sy-8+1), 4)  # shadow
    pygame.draw.line(surf, _RED_D, (sx+6, sy-8+1), (sx-2, sy+6+1), 4)
    pygame.draw.line(surf, _WHITE, (sx-6, sy-8), (sx+6, sy-8), 4)      # top bar
    pygame.draw.line(surf, _WHITE, (sx+6, sy-8), (sx-2, sy+6), 4)      # diagonal

    # Hem seam.
    pygame.draw.ellipse(surf, _RED_D, (BCX-9,BCY+5,20,2), 1)

    # Grey shorts — muted enough that the pure-white ball pops off them.
    pygame.draw.ellipse(surf, _SHORTS, (BCX-9,BCY+6,20,9))
    pygame.draw.ellipse(surf, _SHORTS_SH, (BCX-9,BCY+6,20,9), 1)
    # Red waistband so the shorts read as shorts, not a blob.
    pygame.draw.line(surf, _WAISTBAND, (BCX-8, BCY+6), (BCX+10, BCY+6), 2)
    _poly(surf, _SHORTS_SH, [(BCX-1,BCY+12),(BCX+3,BCY+12),(BCX+1,BCY+15)])

    # Red socks with white hoop.
    for skx in (27, 35):
        pygame.draw.line(surf, _RED,   (skx, BCY+10), (skx, BCY+17), 4)
        pygame.draw.line(surf, _WHITE, (skx, BCY+11), (skx, BCY+13), 3)

    # Cleats.
    for cx in (23, 31):
        pygame.draw.rect(surf, _CLEAT, (cx, BCY+14, 9, 5), border_radius=2)
        pygame.draw.line(surf, _WHITE, (cx, BCY+18), (cx+8, BCY+18), 1)

    # HERO PROP — soccer ball at knee height, drawn LAST so nothing clips it.
    bx, by = BCX-16, BCY+10
    pygame.draw.circle(surf, (235,235,235), (bx, by), 7)
    pygame.draw.circle(surf, (20,20,20),    (bx, by), 7, 1)
    for px, py in [(bx-2,by-4),(bx+4,by-1),(bx+1,by+4),(bx-4,by+1)]:
        pygame.draw.circle(surf, (20,20,20), (px,py), 2)


build = _make_skin(_paint, base_fn=_base)
