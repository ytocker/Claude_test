"""Basketball v3 Design 3 — THE CELTIC.

Green + white + gold. Classic Boston Celtics style. White number "33",
white headband with green knot, white shorts with green stripe.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP
from tools.basketball_candidates._shared import draw_basketball_kit

_GREEN   = (  0, 130,  60)
_GREEN_D = (  0,  90,  42)
_WHITE   = (245, 245, 248)
_WHITE_D = (180, 185, 198)
_GOLD    = (200, 160,  10)
_GOLD_D  = (140, 110,   5)

_PAL = _pal(
    tail=[(200,30,40),(240,95,40),(255,160,55),(255,220,80)],
    tail_line=(170,25,25),
    body_shadow=(  0,  90, 42),
    body_main  =(  0, 130, 60),
    body_chest =( 10, 150, 70),
    body_belly =(  0, 100, 45),
    sheen=(100,255,150,50),
    wing_main=BIRD_WING, wing_dark=BIRD_WING_D, wing_tip=BIRD_TIP,
    wing_secondary=(100, 200, 130), wing_highlight=(180, 235, 205),
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
        jersey_d=_GREEN_D,
        strap=_WHITE, strap_d=_WHITE_D,
        num_col=_WHITE, num_d=_GREEN_D,
        number="33",
        shorts=_WHITE, shorts_d=_WHITE_D,
        waist=_GOLD,
        band=_WHITE, band_d=_WHITE_D,
        knot=_GREEN,
    )


build = _make_skin(_paint, base_fn=_base)
