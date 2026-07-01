"""Soccer v8 Design 4 — NETHERLANDS (Oranje).

Inspired by the Dutch national team's iconic oranje kit: bold deep-orange body
with navy V-collar, navy sleeve cuffs, and a stylised Dutch lion crest on the
upper chest. The body oval is re-plumaged via palette to vivid orange; the
_paint pass adds the navy trim. Navy shorts. At 40 px the read is a brilliant
orange bird in a navy-collared football shirt — unmistakably the Dutch kit.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

_ORA    = (225,  88,   0)
_ORA_D  = (170,  60,   0)
_NAVY   = (  0,  22,  68)   # true navy (KNVB blue)
_NAVY_D = (  0,  12,  40)
_GOLD   = (240, 180,  20)
_SCK    = (225,  88,   0)
_SCK_H  = (  0,  30,  80)
_CLEAT  = ( 28,  28,  36)

_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(170,  60,   0),
    body_main=(225,  88,   0),
    body_chest=(240, 105,  15),
    body_belly=(195,  72,   0),
    sheen=(255, 160, 80, 80),
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
    # Navy body-oval border — gives the orange jersey a crisp dark edge.
    pygame.draw.ellipse(surf, _NAVY, (BCX - 19, BCY - 14, 38, 28), 2)

    # Navy collar band — a solid 4px band across the neck separates the orange
    # body from the macaw-red head so the two reds don't muddy each other.
    pygame.draw.line(surf, _NAVY_D, (BCX - 8, BCY - 13), (BCX + 10, BCY - 13), 4)
    pygame.draw.line(surf, _NAVY, (BCX - 8, BCY - 12), (BCX + 10, BCY - 12), 4)

    # Navy V-collar: two lines meeting at a point just below the collar band.
    pygame.draw.line(surf, _NAVY, (BCX - 5, BCY - 10), (BCX + 2, BCY - 7), 2)
    pygame.draw.line(surf, _NAVY, (BCX + 7, BCY - 10), (BCX + 2, BCY - 7), 2)

    # Stylised crest — a small gold shield on the orange upper chest.
    _poly(surf, _NAVY, [(BCX + 3, BCY - 9), (BCX + 7, BCY - 9),
                        (BCX + 7, BCY - 4), (BCX + 5, BCY - 2), (BCX + 3, BCY - 4)])
    _poly(surf, _GOLD, [(BCX + 4, BCY - 8), (BCX + 6, BCY - 8),
                        (BCX + 6, BCY - 4), (BCX + 5, BCY - 3), (BCX + 4, BCY - 4)])

    # Navy sleeve-seam lines at wing roots to read as cuff trim.
    pygame.draw.line(surf, _NAVY, (BCX + 8, BCY - 11), (BCX + 17, BCY - 5), 2)
    pygame.draw.line(surf, _NAVY, (BCX - 6, BCY - 11), (BCX - 14, BCY - 5), 2)

    # Thin navy hem line at jersey bottom.
    pygame.draw.ellipse(surf, _NAVY, (BCX - 9, BCY + 5, 20, 3), 1)

    # Navy shorts.
    pygame.draw.ellipse(surf, _NAVY, (BCX - 9, BCY + 6, 20, 9))
    pygame.draw.ellipse(surf, _NAVY_D, (BCX - 9, BCY + 6, 20, 9), 1)

    # Orange socks with navy hoop.
    for sx in (27, 35):
        pygame.draw.line(surf, _SCK, (sx, BCY + 11), (sx, BCY + 16), 4)
        pygame.draw.line(surf, _SCK_H, (sx, BCY + 12), (sx, BCY + 14), 3)

    # Near-black cleats.
    for cx in (23, 31):
        pygame.draw.rect(surf, _CLEAT, (cx, BCY + 14, 9, 5), border_radius=1)


build = _make_skin(_paint, base_fn=_base)
