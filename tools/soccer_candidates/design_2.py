"""Soccer v8 Design 2 — BRAZIL (Canarinha).

Inspired by Brazil's iconic canarinha kit: golden-yellow body with deep-green
V-collar and green sleeve-trim band, a circular CBF-style crest badge at the
upper chest, and royal-blue shorts. The palette re-plumages the body oval
gold; the _paint pass adds the green trim and badge. Clean and immediately
readable at 40 px — gold body, green collar, blue shorts.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

_GOLD    = (255, 213,   0)
_GOLD_D  = (200, 160,   0)
_GREEN   = (  0, 175,  65)
_GREEN_D = (  0, 120,  42)
_BLUE    = (  3,  67, 155)
_BLUE_D  = (  1,  45, 110)
_WHITE   = (245, 245, 250)
_SCK     = (245, 245, 250)
_SCK_H   = (  0, 150,  57)
_CLEAT   = ( 28,  28,  36)

_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(200, 160,   0),
    body_main=(255, 213,   0),
    body_chest=(255, 225,  20),
    body_belly=(225, 180,   0),
    sheen=(255, 240, 100, 80),
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
    # Green body-oval border (2 px) gives the jersey a clean green edge trim,
    # reminiscent of the green outline on Brazil's gold shirt.
    pygame.draw.ellipse(surf, _GREEN, (BCX - 19, BCY - 14, 38, 28), 2)

    # Deep green V-collar at the head-body junction.
    pygame.draw.line(surf, _GREEN, (BCX - 6, BCY - 12), (BCX + 2, BCY - 8), 2)
    pygame.draw.line(surf, _GREEN, (BCX + 8, BCY - 12), (BCX + 2, BCY - 8), 2)

    # Green shoulder-trim band across the collar line.
    pygame.draw.line(surf, _GREEN_D, (BCX - 6, BCY - 12), (BCX + 8, BCY - 12), 3)

    # CBF-style circular crest badge on upper chest — enlarged to survive 40px.
    pygame.draw.circle(surf, _GREEN_D, (BCX + 5, BCY - 4), 7)
    pygame.draw.circle(surf, _GREEN, (BCX + 5, BCY - 4), 6)
    pygame.draw.circle(surf, _GOLD, (BCX + 5, BCY - 4), 4)
    pygame.draw.circle(surf, _BLUE, (BCX + 5, BCY - 4), 2)

    # Sleeve seam arcs at wing roots.
    pygame.draw.line(surf, _GREEN_D, (BCX + 8, BCY - 11), (BCX + 17, BCY - 5), 1)
    pygame.draw.line(surf, _GREEN_D, (BCX - 6, BCY - 11), (BCX - 14, BCY - 5), 1)

    # Thin gold hem outline separating jersey from shorts.
    pygame.draw.ellipse(surf, _GOLD_D, (BCX - 9, BCY + 5, 20, 3), 1)

    # Royal-blue shorts.
    pygame.draw.ellipse(surf, _BLUE, (BCX - 9, BCY + 6, 20, 9))
    pygame.draw.ellipse(surf, _BLUE_D, (BCX - 9, BCY + 6, 20, 9), 1)

    # White socks, green club hoop.
    for sx in (27, 35):
        pygame.draw.line(surf, _SCK, (sx, BCY + 11), (sx, BCY + 16), 4)
        pygame.draw.line(surf, _SCK_H, (sx, BCY + 12), (sx, BCY + 14), 3)

    # Near-black cleats.
    for cx in (23, 31):
        pygame.draw.rect(surf, _CLEAT, (cx, BCY + 14, 9, 5), border_radius=1)


build = _make_skin(_paint, base_fn=_base)
