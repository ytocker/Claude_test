"""Live play-scene foreground facade — the buff sandstone sidewalk that replaces
the grass meadow ground.

Stage 1 ships the floor + embedded surface detail. Later stages add the
promenade props/characters and the near/front activity lane through this same
facade. All procedural; safe on native + web.
"""
from __future__ import annotations

from game.config import W, H, GROUND_Y
from game import foreground_floor as _floor
from game import foreground_detail as _detail
from game import foreground_promenade as _promenade


def draw_foreground_floor(surf, scroll, pal):
    """Paint the buff running-bond sidewalk + its embedded surface detail into
    the ~45px play-floor band (y=GROUND_Y..H), world-anchored to `scroll`."""
    _floor.fg_swatch_buff_running_bond(surf, W, GROUND_Y, H, scroll, pal)
    _detail.add_embedded_detail("buff", surf, W, GROUND_Y, H, scroll, pal)


def draw_promenade(surf, scroll, pal, phase, t):
    """Draw the promenade props + living cast on the sidewalk, crossfading
    between day→night beats by the live biome `phase`."""
    _promenade.draw_promenade(surf, scroll, pal, phase, t)
