"""Bespoke per-achievement center-glyph drawers, one module per category.

Each module defines `_glyph_<id>(surf, cx, cy, r, col)` drawers in the engraved
relief idiom of ``achievement_icons`` plus a ``GLYPHS`` dict keyed by the
achievement id. They are aggregated here and merged into
``achievement_icons._GLYPHS`` at import so every achievement renders its own
emblem. ``MYSTERY_KEYS`` are the amethyst secret tier — their ids route through
the ``_HIDDEN_KEYS`` amethyst path.
"""
from game.emblems import (
    flight_log, riches, power_player, stormchaser,
    skater, mysteries, blooper_reel, lifetime_lows,
)

_MODULES = (flight_log, riches, power_player, stormchaser,
            skater, mysteries, blooper_reel, lifetime_lows)

EMBLEM_GLYPHS: dict = {}
for _m in _MODULES:
    EMBLEM_GLYPHS.update(_m.GLYPHS)

# Placeholder aliases: new Hall-of-Fame ids reuse a fitting existing glyph until
# bespoke emblems are drawn in a later design pass. Each guarded so a renamed
# source glyph can't KeyError the whole roster.
_ALIASES = {
    "sky_legend": "pillar_100",
    "quad_digits": "score_500",
    "weeklong_bender": "day_three",
    "purist": "frequent_flyer",
    "millionaire": "midas",
    "power_overwhelming": "power_addict",
    "overachiever": "power_hungry",
    "kitchen_sink": "powerup_sampler",
    "overloaded": "powerup_collector",
    "bullet_time": "marathon",
    "ghost_rider": "denial",
    "regifted": "jackpot",
    "endless": "marathon",
    "read_fine_print": "treasure_hunter",
    "morbid_curiosity": "poisoned",
    "are_you_still_there": "marathon",
    "after_hours": "day_complete",
    "early_bird": "day_complete",
    "leap_of_faith": "day_three",
    "auld_lang_syne": "jackpot",
    "lucky_sevens": "jackpot",
    "palindrome": "score_100",
    "the_completionist": "trick_legend",
    "many_happy_returns": "day_three",
    "creature_of_habit": "day_complete",
    "the_grind": "flap_life",
    "never_say_die": "iron_wings",
}
for _new, _src in _ALIASES.items():
    if _src in EMBLEM_GLYPHS:
        EMBLEM_GLYPHS[_new] = EMBLEM_GLYPHS[_src]

MYSTERY_KEYS = frozenset(mysteries.GLYPHS)
