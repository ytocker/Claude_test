"""Soccer v8 Design 3 — AC MILAN (Rossoneri).

Inspired by AC Milan's classic rossoneri kit: the body oval is split into
three red stripes and two black stripes (five equal bands). Palette base is
milan-red; the _paint pass clips to the body oval and paints two black bands
at fixed x positions. White shorts (Milan's canonical home pairing). Gold
small crest on upper chest.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

_RED     = (200,  30,  30)
_RED_D   = (140,  15,  15)
_BLACK   = ( 10,  10,  12)
_WHITE   = (245, 245, 250)
_WHITE_D = (200, 200, 210)
_GOLD    = (200, 155,  30)
_SHORTS  = (245, 245, 250)
_SHORTS_D = (200, 200, 210)
_SCK     = (245, 245, 250)
_SCK_H   = (200,  30,  30)
_CLEAT   = ( 28,  28,  36)

_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(140,  15,  15),
    body_main=(200,  30,  30),
    body_chest=(215,  45,  45),
    body_belly=(170,  18,  18),
    sheen=(255, 120, 120, 60),
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
    # Rossoneri stripe pattern: clip to body oval, paint two black bands (8 px
    # each) over the red base, creating a red|black|red|black|red sequence
    # across the 38 px body width. ~7–8 px per band.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX - 19, BCY - 14, 38, 28))
    pygame.draw.rect(surf, _BLACK, (BCX - 12, BCY - 14, 8, 28))
    pygame.draw.rect(surf, _BLACK, (BCX +  4, BCY - 14, 8, 28))
    surf.set_clip(clip_prev)
    pygame.draw.ellipse(surf, _RED_D, (BCX - 19, BCY - 14, 38, 28), 1)

    # White crew collar.
    pygame.draw.line(surf, _WHITE, (BCX - 7, BCY - 12), (BCX + 9, BCY - 12), 2)
    pygame.draw.line(surf, _RED_D, (BCX - 7, BCY - 11), (BCX + 9, BCY - 11), 1)

    # Gold crest badge on red upper-chest panel.
    pygame.draw.circle(surf, _RED_D, (BCX + 5, BCY - 5), 4)
    pygame.draw.circle(surf, _GOLD, (BCX + 5, BCY - 5), 3)

    # Sleeve seam arcs.
    pygame.draw.line(surf, _RED_D, (BCX + 8, BCY - 11), (BCX + 17, BCY - 5), 1)
    pygame.draw.line(surf, _RED_D, (BCX - 6, BCY - 11), (BCX - 14, BCY - 5), 1)

    # Thin dark hem line.
    pygame.draw.ellipse(surf, _RED_D, (BCX - 9, BCY + 5, 20, 3), 1)

    # White shorts (Milan's home kit pairing with red/black jersey).
    pygame.draw.ellipse(surf, _SHORTS, (BCX - 9, BCY + 6, 20, 9))
    pygame.draw.ellipse(surf, _SHORTS_D, (BCX - 9, BCY + 6, 20, 9), 1)

    # White socks, red hoop.
    for sx in (27, 35):
        pygame.draw.line(surf, _SCK, (sx, BCY + 11), (sx, BCY + 16), 4)
        pygame.draw.line(surf, _SCK_H, (sx, BCY + 12), (sx, BCY + 14), 3)

    # Near-black cleats.
    for cx in (23, 31):
        pygame.draw.rect(surf, _CLEAT, (cx, BCY + 14, 9, 5), border_radius=1)


build = _make_skin(_paint, base_fn=_base)
