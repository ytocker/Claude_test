"""Basketball v3 Design 4 — THE WARRIOR.

Royal blue + gold. Golden State Warriors style. Gold number "30",
gold headband with blue knot, blue shorts.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP
from tools.basketball_candidates._shared import draw_basketball_kit

_BLUE   = ( 30,  60, 160)
_BLUE_D = ( 18,  38, 110)
_GOLD   = (235, 180,   0)
_GOLD_D = (165, 120,   0)
_WHITE  = (245, 245, 248)

_PAL = _pal(
    tail=[(200,30,40),(240,95,40),(255,160,55),(255,220,80)],
    tail_line=(170,25,25),
    body_shadow=( 18, 38, 110),
    body_main  =( 30, 60, 160),
    body_chest =( 42, 76, 185),
    body_belly =( 20, 44, 125),
    sheen=(100,130,255,50),
    wing_main=BIRD_WING, wing_dark=BIRD_WING_D, wing_tip=BIRD_TIP,
    wing_secondary=(200,160,  0), wing_highlight=(235,210,120),
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
        jersey_d=_BLUE_D,
        strap=_GOLD, strap_d=_GOLD_D,
        num_col=_GOLD, num_d=_BLUE_D,
        number="30",
        shorts=_BLUE, shorts_d=_BLUE_D,
        waist=_GOLD,
        band=_GOLD, band_d=_GOLD_D,
        knot=_BLUE,
    )


build = _make_skin(_paint, base_fn=_base)
