"""Basketball v4 Design 1 — THE LAKER.

Purple + gold + white. Los Angeles Lakers palette. White "8", white headband
with purple midline + knot, gold shoe accent. Closest to the approved original.
Polygon drawn over natural parrot (no body recolor) so plumage shows at armholes.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from tools.basketball_candidates._shared import draw_basketball_kit

_PURPLE   = (106,  45, 168)
_PURPLE_D = ( 74,  28, 122)
_PURPLE_H = (140,  80, 206)
_GOLD     = (235, 180,   0)
_GOLD_D   = (165, 120,   0)
_WHITE    = (242, 242, 242)
_WHITE_D  = (196, 196, 204)

BCX, BCY = 32, 52


def _paint(surf, _a):
    draw_basketball_kit(
        surf, BCX, BCY, HX, HY, CROWN_Y, _poly,
        jersey=_PURPLE, jersey_d=_PURPLE_D, jersey_h=_PURPLE_H,
        trim=_WHITE, trim_d=_WHITE_D,
        num_col=_WHITE, num_d=_PURPLE_D, number="8",
        shoe=_WHITE, shoe_d=_WHITE_D, shoe_ac=_GOLD,
    )


build = _make_skin(_paint)
