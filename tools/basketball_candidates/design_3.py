"""Basketball v4 Design 3 — THE CELTIC.

Green + white + gold. Boston Celtics palette. White "3", white headband with
green midline + knot, gold shoe accent stripe.
Polygon drawn over natural parrot (no body recolor).
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from tools.basketball_candidates._shared import draw_basketball_kit

_GREEN   = (  0, 128,  55)
_GREEN_D = (  0,  88,  38)
_GREEN_H = ( 30, 165,  85)
_WHITE   = (242, 242, 242)
_WHITE_D = (196, 196, 204)
_GOLD    = (200, 160,  10)
_GOLD_D  = (140, 110,   5)

BCX, BCY = 32, 52


def _paint(surf, _a):
    draw_basketball_kit(
        surf, BCX, BCY, HX, HY, CROWN_Y, _poly,
        jersey=_GREEN, jersey_d=_GREEN_D, jersey_h=_GREEN_H,
        trim=_WHITE, trim_d=_WHITE_D,
        num_col=_WHITE, num_d=_GREEN_D, number="3",
        shoe=_WHITE, shoe_d=_WHITE_D, shoe_ac=_GOLD,
    )


build = _make_skin(_paint)
