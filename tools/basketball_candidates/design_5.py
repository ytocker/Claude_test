"""Basketball v4 Design 5 — THE HEAT.

Near-black + red + white. Miami Heat palette. White "6", white headband with
red midline + knot, black shoes with red accent stripe.
Polygon drawn over natural parrot (no body recolor).
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from tools.basketball_candidates._shared import draw_basketball_kit

_BLACK   = ( 22,  22,  30)
_BLACK_D = ( 10,  10,  16)
_BLACK_H = ( 50,  50,  65)
_RED     = (200,  20,  30)
_RED_D   = (140,  12,  18)
_WHITE   = (242, 242, 242)
_WHITE_D = (196, 196, 204)

BCX, BCY = 32, 52


def _paint(surf, _a):
    draw_basketball_kit(
        surf, BCX, BCY, HX, HY, CROWN_Y, _poly,
        jersey=_BLACK, jersey_d=_BLACK_D, jersey_h=_BLACK_H,
        trim=_WHITE, trim_d=_WHITE_D,
        num_col=_WHITE, num_d=_BLACK_D, number="6",
        shoe=_BLACK, shoe_d=_BLACK_D, shoe_ac=_RED,
        band_accent=_RED,
    )


build = _make_skin(_paint)
