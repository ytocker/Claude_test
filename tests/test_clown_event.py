"""
Clown event — locked behaviour.

Pins:
  - The event fires once per biome day, when the phase crosses the clown
    anchor (CLOWN_EVENT_PHASE = the phase of CLOWN_START_PILLAR), and re-arms
    on the cycle wrap so it recurs every day.
  - The reserved slot is always CLOWN_SLOT_PILLARS wide regardless of the
    rolled gauntlet length N: the first N pillars are warren towers
    (is_staff, at the fused CLOWN_WARREN_SPACING), the remaining N..slot are
    regular gameplay, and coin rush is suppressed across the whole slot — so
    downstream pillar numbering stays deterministic.
"""
import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
pygame.init()
pygame.display.set_mode((360, 640))

from game.world import World, CLOWN_EVENT_PHASE  # noqa: E402
from game.clown_routes import build_clown_route  # noqa: E402
from game.config import (  # noqa: E402
    CLOWN_SLOT_PILLARS, CLOWN_WARREN_SPACING, CLOWN_ROLL_MIN, CLOWN_ROLL_MAX)
from game.biome import CYCLE_SECONDS  # noqa: E402


class SlotReservation(unittest.TestCase):
    def _lay_slot(self, n):
        w = World()
        w._clown_route = build_clown_route(n, random.Random(0))
        w._clown_slot_remaining = CLOWN_SLOT_PILLARS
        rows = []  # (is_staff, is_rush, spacing-for-this-pillar)
        x = 500.0
        for _ in range(CLOWN_SLOT_PILLARS):
            sp = w._next_spacing()
            w._spawn_pipe(x)
            p = w.pipes[-1]
            rows.append((getattr(p, "is_staff", False),
                         getattr(p, "is_rush", False), sp))
            x += sp
        return w, rows

    def test_short_roll_fills_to_slot_width(self):
        n = 14
        w, rows = self._lay_slot(n)
        staff = [s for s, _, _ in rows]
        self.assertEqual(staff, [True] * n + [False] * (CLOWN_SLOT_PILLARS - n),
                         "first N pillars warren, the rest regular fill")
        self.assertEqual(sum(staff), n)
        self.assertEqual(w._clown_slot_remaining, 0, "slot fully consumed")

    def test_warren_uses_fused_spacing(self):
        n = 12
        _w, rows = self._lay_slot(n)
        self.assertTrue(all(sp == CLOWN_WARREN_SPACING for _, _, sp in rows[:n]),
                        "warren pillars sit at the fused spacing")
        self.assertTrue(all(sp != CLOWN_WARREN_SPACING for _, _, sp in rows[n:]),
                        "regular-fill pillars use the normal spacing")

    def test_coin_rush_suppressed_in_slot(self):
        _w, rows = self._lay_slot(CLOWN_ROLL_MAX)
        self.assertFalse(any(r for _, r, _ in rows),
                         "no coin rush anywhere inside the clown slot")

    def test_full_roll_is_all_warren(self):
        n = CLOWN_ROLL_MAX
        _w, rows = self._lay_slot(n)
        self.assertTrue(all(s for s, _, _ in rows),
                        "a max roll fills the slot entirely with warren towers")


class Trigger(unittest.TestCase):
    def _arm_just_before_anchor(self, w):
        w.ready_t = 0.0
        w.bird.alive = True
        w.game_over = False
        w._clown_fired_this_cycle = False
        w._clown_slot_remaining = 0
        # Park phase a hair before the anchor; push biome_time a hair past it so
        # the crossing fires inside this update tick.
        w._last_biome_phase = CLOWN_EVENT_PHASE - 0.005
        w.biome_time = (CLOWN_EVENT_PHASE + 0.002) * CYCLE_SECONDS

    def test_fires_once_at_anchor(self):
        w = World()
        self._arm_just_before_anchor(w)
        w.update(1 / 60.0)
        self.assertEqual(w._clown_slot_remaining, CLOWN_SLOT_PILLARS,
                         "crossing the clown anchor reserves the full slot")
        self.assertTrue(w._clown_fired_this_cycle)
        self.assertGreaterEqual(len(w._clown_route), CLOWN_ROLL_MIN)
        self.assertLessEqual(len(w._clown_route), CLOWN_ROLL_MAX)

    def test_does_not_refire_same_day(self):
        w = World()
        self._arm_just_before_anchor(w)
        w.update(1 / 60.0)
        # Drain the slot, then keep advancing within the same day: must not
        # re-arm until a cycle wrap re-sets the flag.
        w._clown_slot_remaining = 0
        w._last_biome_phase = CLOWN_EVENT_PHASE - 0.005
        w.biome_time = (CLOWN_EVENT_PHASE + 0.002) * CYCLE_SECONDS
        w.update(1 / 60.0)
        self.assertEqual(w._clown_slot_remaining, 0,
                         "clown must not re-fire twice in one day")


if __name__ == "__main__":
    unittest.main()
