"""Soccer v8 Design 5 — JUVENTUS (Bianconeri) — R2 revision.

The R1 half-split (white left / black right) read as damage or glitch at 40px
rather than a football kit. This revision uses alternating black-white vertical
stripes across the full body oval (3 black + 2 white gaps = 5-band pattern),
which is immediately recognisable as the Juventus bianconeri kit and reads as
fabric, not a broken sprite. Palette base stays white; the _paint pass clips to
the oval and paints 3 black bands. Black shorts and black-hooped socks.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

_WHITE   = (242, 242, 245)
_WHITE_D = (195, 195, 205)
_BLACK   = ( 10,  10,  12)
_BLACK_M = ( 25,  25,  28)
_GOLD    = (200, 155,  30)
_SHORTS  = ( 10,  10,  12)
_SHORTS_D = ( 28,  28,  34)
_SCK     = (242, 242, 245)
_SCK_H   = ( 10,  10,  12)
_CLEAT   = ( 10,  10,  12)

_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(195, 195, 205),
    body_main=(242, 242, 245),
    body_chest=(250, 250, 252),
    body_belly=(215, 215, 225),
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

BCX, BCY = 32, 52


def _base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # Bianconeri stripe pattern: white palette base + 3 black vertical bands
    # clipped to the body oval. White|Black|White|Black|White|Black|White =
    # alternating ~5 px bands across the 38 px oval width.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX - 19, BCY - 14, 38, 28))
    for x in (BCX - 14, BCX - 3, BCX + 8):
        pygame.draw.rect(surf, _BLACK, (x, BCY - 14, 5, 28))
    surf.set_clip(clip_prev)
    pygame.draw.ellipse(surf, _BLACK, (BCX - 19, BCY - 14, 38, 28), 1)

    # Black crew collar band.
    pygame.draw.line(surf, _BLACK, (BCX - 7, BCY - 12), (BCX + 9, BCY - 12), 2)

    # Gold crest badge on the first white stripe (left chest).
    pygame.draw.circle(surf, _BLACK_M, (BCX - 8, BCY - 5), 5)
    pygame.draw.circle(surf, _GOLD, (BCX - 8, BCY - 5), 4)

    # Sleeve seam arcs at wing roots.
    pygame.draw.line(surf, _BLACK, (BCX + 8, BCY - 11), (BCX + 17, BCY - 5), 1)
    pygame.draw.line(surf, _WHITE_D, (BCX - 6, BCY - 11), (BCX - 14, BCY - 5), 1)

    # Thin hem outline at jersey bottom.
    pygame.draw.ellipse(surf, _BLACK, (BCX - 9, BCY + 5, 20, 3), 1)

    # Black shorts.
    pygame.draw.ellipse(surf, _SHORTS, (BCX - 9, BCY + 6, 20, 9))
    pygame.draw.ellipse(surf, _SHORTS_D, (BCX - 9, BCY + 6, 20, 9), 1)

    # White socks, black hoop.
    for sx in (27, 35):
        pygame.draw.line(surf, _SCK, (sx, BCY + 11), (sx, BCY + 16), 4)
        pygame.draw.line(surf, _SCK_H, (sx, BCY + 12), (sx, BCY + 14), 3)

    # Black cleats.
    for cx in (23, 31):
        pygame.draw.rect(surf, _CLEAT, (cx, BCY + 14, 9, 5), border_radius=1)


build = _make_skin(_paint, base_fn=_base)
