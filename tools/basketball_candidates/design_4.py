"""Basketball v4 Design 4 — THE WARRIOR.

Royal blue + gold. Golden State Warriors palette. Gold "3", gold neckline + hem
trim, white headband with blue midline + knot, white shoes with gold accent.
Polygon drawn over natural parrot (no body recolor).
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from tools.basketball_candidates._shared import draw_basketball_kit

_BLUE   = ( 30,  60, 160)
_BLUE_D = ( 18,  38, 110)
_BLUE_H = ( 60, 100, 210)
_GOLD   = (235, 180,   0)
_GOLD_D = (165, 120,   0)
_WHITE  = (242, 242, 242)
_WHITE_D= (196, 196, 204)

BCX, BCY = 32, 52


def _paint(surf, _a):
    draw_basketball_kit(
        surf, BCX, BCY, HX, HY, CROWN_Y, _poly,
        jersey=_BLUE, jersey_d=_BLUE_D, jersey_h=_BLUE_H,
        trim=_GOLD, trim_d=_GOLD_D,
        num_col=_GOLD, num_d=_BLUE_D, number="3",
        shoe=_WHITE, shoe_d=_WHITE_D, shoe_ac=_GOLD,
        band_accent=_BLUE,
    )


build = _make_skin(_paint)
