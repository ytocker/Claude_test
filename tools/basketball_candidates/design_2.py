"""Basketball v3 Design 2 — THE BULL.

Red + black. Classic Chicago Bulls home style. White number "23",
white headband with red knot, black shorts.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP
from tools.basketball_candidates._shared import draw_basketball_kit

_RED    = (200,  20,  30)
_RED_D  = (140,  12,  18)
_BLACK  = ( 22,  22,  30)
_BLACK_D= ( 10,  10,  16)
_WHITE  = (245, 245, 248)
_WHITE_D= (180, 182, 195)

_PAL = _pal(
    tail=[(200,30,40),(240,95,40),(255,160,55),(255,220,80)],
    tail_line=(170,25,25),
    body_shadow=(140, 12, 18),
    body_main  =(200, 20, 30),
    body_chest =(220, 30, 42),
    body_belly =(160, 14, 22),
    sheen=(255,100,100,50),
    wing_main=BIRD_WING, wing_dark=BIRD_WING_D, wing_tip=BIRD_TIP,
    wing_secondary=(180, 40, 50), wing_highlight=(220,100,110),
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
    draw_basketball_kit(
        surf, BCX, BCY, HX, CROWN_Y, _poly,
        jersey_d=_RED_D,
        strap=_WHITE, strap_d=_WHITE_D,
        num_col=_WHITE, num_d=_RED_D,
        number="3",
        shorts=_BLACK, shorts_d=_BLACK_D,
        waist=_WHITE,
        band=_WHITE, band_d=_WHITE_D,
        knot=_RED,
    )


build = _make_skin(_paint, base_fn=_base)
