"""Block personalities — the SPATIAL layer of the weekend street.

The day curve says how busy the town is; this module says WHERE. The world x-axis
divides into ~900 px blocks (≈5.6 s of flight), and each block is dealt a
personality — a stall row, a quiet residential stretch, a small square, a green
walk — so different parts of town feel different as Pip advances, the way a real
street has knots and gaps rather than a uniform field. Personalities bias the
scenario roster and multiply the local density; a slow world-x sine breathes on
top so even same-personality stretches vary.

Everything is a PURE function of (block index, run seed, daypart) with a bounded
lookback, so a block's character is stable for its whole traversal (no flicker)
and every run deals the town a new layout.
"""
from __future__ import annotations

import random

BLOCK_PX = 900

# Personalities: (name, density multiplier)
STALL_ROW = "stall_row"
QUIET = "quiet"
SQUARE = "square"
GREEN = "green"
SHOPFRONT = "shopfront"
TEMPLE = "temple"
CROSSING = "crossing"
WORKS = "works"

_DENS_MULT = {
    STALL_ROW: 1.5, QUIET: 0.4, SQUARE: 1.1, GREEN: 0.5,
    SHOPFRONT: 1.0, TEMPLE: 0.7, CROSSING: 1.6, WORKS: 0.35,
}
_LOW = (QUIET, GREEN, WORKS)

# Daypart decks: which personalities a block prefers at each stretch of the day.
# Weights, not gates — every personality can appear anywhere, rarely.
_DAYPARTS = (
    # (phase_end, {personality: weight})
    (0.157, {STALL_ROW: 5, CROSSING: 4, SHOPFRONT: 3, GREEN: 2, QUIET: 1, TEMPLE: 1, WORKS: 1, SQUARE: 1}),   # morning market
    (0.309, {GREEN: 4, QUIET: 4, TEMPLE: 3, WORKS: 2, SHOPFRONT: 2, SQUARE: 1, STALL_ROW: 1, CROSSING: 1}),   # the long middle
    (0.416, {SQUARE: 4, SHOPFRONT: 3, GREEN: 3, STALL_ROW: 2, QUIET: 2, TEMPLE: 2, CROSSING: 1, WORKS: 1}),   # golden stroll
    (0.644, {STALL_ROW: 5, SHOPFRONT: 2, SQUARE: 2, QUIET: 2, GREEN: 2, TEMPLE: 1, CROSSING: 1, WORKS: 1}),   # setup + rain
    (0.785, {STALL_ROW: 5, CROSSING: 4, SQUARE: 3, SHOPFRONT: 2, GREEN: 2, TEMPLE: 1, QUIET: 1, WORKS: 1}),   # night market
    (0.924, {QUIET: 5, WORKS: 3, GREEN: 3, TEMPLE: 2, STALL_ROW: 1, SQUARE: 1, SHOPFRONT: 1, CROSSING: 1}),   # small hours
    (1.001, {SHOPFRONT: 3, STALL_ROW: 3, QUIET: 3, GREEN: 2, WORKS: 2, TEMPLE: 1, SQUARE: 1, CROSSING: 1}),   # first light
)

# Which scenario builders (by function name) each personality prefers. A block
# only REORDERS/FILTERS the daypart roster — it never invents scenes the hour
# doesn't offer, so the temporal story stays authoritative.
_ROSTER_PREF = {
    STALL_ROW: ("_scene_food_grill", "_scene_food_soup", "_scene_food_steamer",
                "_scene_food_tea", "_scene_market", "_scene_dawn_setup", "_scene_vendor"),
    CROSSING: ("_scene_stroll", "_scene_market", "_scene_food_tea", "_scene_vendor"),
    SQUARE: ("_scene_stroll", "_scene_bench", "_scene_campfire"),
    SHOPFRONT: ("_scene_vendor", "_scene_stroll", "_scene_market", "_scene_bench"),
    TEMPLE: ("_scene_quiet", "_scene_pastoral", "_scene_rest", "_scene_vendor"),
    GREEN: ("_scene_pastoral", "_scene_quiet", "_scene_bench", "_scene_rest"),
    QUIET: ("_scene_quiet", "_scene_rest", "_scene_pastoral", "_scene_bench"),
    WORKS: ("_scene_rest", "_scene_sweeper", "_scene_quiet", "_scene_dawn_setup"),
}

_run_seed = 0x5EED
_phi = 0.0     # the breathing sine's per-run phase


def reset_run():
    global _run_seed, _phi
    _run_seed = random.getrandbits(32) or 0x5EED
    _phi = random.uniform(0.0, 6.28318)


def _mix(h):
    h &= 0xFFFFFFFF
    h ^= h >> 15
    h = (h * 0x2C1B3C6D) & 0xFFFFFFFF
    h ^= h >> 12
    h = (h * 0x297A2D39) & 0xFFFFFFFF
    return h ^ (h >> 15)


def _deck_for(phase):
    p = phase % 1.0
    for end, deck in _DAYPARTS:
        if p < end:
            return deck
    return _DAYPARTS[-1][1]


# The distinctive (high-density) personalities are parity-partitioned: even
# blocks draw their highs from one set, odd blocks from the other, so two
# adjacent blocks can never repeat a distinctive character — by construction,
# with no lookback fixups. Lows are unrestricted (two quiet stretches back to
# back just read as a longer quiet stretch, which real streets have).
_HIGH_EVEN = (STALL_ROW, SQUARE, TEMPLE)
_HIGH_ODD = (CROSSING, SHOPFRONT)


def _raw(b, phase):
    """Daypart-weighted personality roll for block b within its parity set."""
    deck = _deck_for(phase)
    allowed = _LOW + (_HIGH_EVEN if (b % 2 == 0) else _HIGH_ODD)
    items = [(pers, wt) for pers, wt in deck.items() if pers in allowed]
    h = _mix((b * 0x9E3779B1) ^ _run_seed)
    x = (h & 0xFFFF) / 65535.0 * sum(wt for _, wt in items)
    acc = 0.0
    for pers, wt in items:
        acc += wt
        if x < acc:
            return pers
    return QUIET


def _pre(b, phase):
    """Raw roll with the breathing guarantee: exactly one block per 4-window is
    grid-forced to a low-density personality (at a hashed offset within the
    window), so even the market peak keeps its gaps — without the over-forcing a
    lookback rule produces."""
    if (b % 4) == (_mix(((b // 4) * 0xB5297A4D) ^ _run_seed) % 4):
        return _LOW[_mix((b * 0xC2B2AE35) ^ _run_seed) % len(_LOW)]
    return _raw(b, phase)


def personality(b, phase):
    """Block b's personality, with the layout rules applied via bounded lookback
    (pure — no chained state): a guaranteed low-density stretch in every 4-block
    window, no repeat within 2 blocks, and no crossing beside a square or
    another crossing."""
    me = _pre(b, phase)
    # A crowd knot beside a performer square over-packs the frame — demote it.
    if me == CROSSING and SQUARE in (_pre(b - 1, phase), _pre(b + 1, phase)):
        me = SHOPFRONT
    return me


def block_at(world_x):
    return int(world_x // BLOCK_PX)


def density_mult(world_x, phase):
    """The block's density multiplier × the slow breathing sine (period 1730 px,
    near-coprime with the block and scenario lattices, per-run phase) — knots
    and gaps that never phase-lock into a rhythm."""
    import math
    pers = personality(block_at(world_x), phase)
    breathe = 1.0 + 0.28 * math.sin(world_x * (6.28318 / 1730.0) + _phi)
    return _DENS_MULT[pers] * breathe


def filter_roster(world_x, phase, roster):
    """Reorder/filter the hour's roster to the block's taste. Falls back to the
    full roster when the intersection is empty, so a block can never silence an
    hour entirely."""
    pers = personality(block_at(world_x), phase)
    pref = _ROSTER_PREF.get(pers, ())
    liked = [fn for fn in roster if fn.__name__ in pref]
    return tuple(liked) if liked else roster


def is_square(world_x, phase):
    return personality(block_at(world_x), phase) == SQUARE
