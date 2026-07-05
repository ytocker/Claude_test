"""Basketball v4 Design 2 — THE BULL.

Red + white + black. Chicago Bulls palette. White "3", white headband with
red midline + knot, white shoes with red accent stripe.
Polygon drawn over natural parrot (no body recolor).
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from tools.basketball_candidates._shared import draw_basketball_kit

_RED    = (200,  20,  30)
_RED_D  = (140,  12,  18)
_RED_H  = (220,  55,  65)
_WHITE  = (242, 242, 242)
_WHITE_D= (196, 196, 204)

BCX, BCY = 32, 52


def _paint(surf, _a):
    draw_basketball_kit(
        surf, BCX, BCY, HX, HY, CROWN_Y, _poly,
        jersey=_RED, jersey_d=_RED_D, jersey_h=_RED_H,
        trim=_WHITE, trim_d=_WHITE_D,
        num_col=_WHITE, num_d=_RED_D, number="3",
        shoe=_WHITE, shoe_d=_WHITE_D, shoe_ac=_RED,
    )


build = _make_skin(_paint)
