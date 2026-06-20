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
        # Crossing the anchor now sends in the cinematic controller; the slot is
        # NOT reserved until the die is rolled (see Pickup tests).
        self.assertIsNotNone(w.clown_event, "crossing the anchor spawns the clown")
        self.assertTrue(w._clown_fired_this_cycle)
        self.assertEqual(w._clown_slot_remaining, 0,
                         "slot is reserved on the die roll, not at the trigger")

    def test_does_not_refire_same_day(self):
        w = World()
        self._arm_just_before_anchor(w)
        w.update(1 / 60.0)
        first = w.clown_event
        # Clear it and keep advancing within the same day: must not re-arm until a
        # cycle wrap re-sets the flag.
        w.clown_event = None
        w._last_biome_phase = CLOWN_EVENT_PHASE - 0.005
        w.biome_time = (CLOWN_EVENT_PHASE + 0.002) * CYCLE_SECONDS
        w.update(1 / 60.0)
        self.assertIsNotNone(first)
        self.assertIsNone(w.clown_event, "clown must not re-fire twice in one day")


class Pickup(unittest.TestCase):
    """The die roll reserves the gauntlet and feeds N to the slot."""

    def _roll(self, ghost=False):
        from game.clown_event import ClownEvent
        w = World()
        ev = ClownEvent()
        w.clown_event = ev
        # Force the outcome deterministically, then run the collect→reveal path.
        ev.collected = True
        ev.ghost_run = ghost
        ev.roll = 10 if ghost else 18
        ev.spin_t = 0.0
        ev.phase = "rolling"
        ev._reveal(w)
        return w, ev

    def test_roll_reserves_slot(self):
        w, ev = self._roll()
        self.assertEqual(w._clown_slot_remaining, CLOWN_SLOT_PILLARS)
        self.assertEqual(len(w._clown_route), 18, "route length == rolled N")
        self.assertGreater(ev.die_pop_t, 0.0, "reveal banner armed")

    def test_ghost_sets_bird_ghost(self):
        w, ev = self._roll(ghost=True)
        self.assertTrue(ev.ghost_run)
        self.assertGreater(w.ghost_timer, 0.0, "GHOST roll phases Pip through")
        self.assertEqual(w.ghost_timer_total, w.ghost_timer)
        self.assertEqual(len(w._clown_route), 10, "ghost rolls the minimum")

    def test_auto_grab_on_pass(self):
        from game.clown_event import ClownEvent
        w = World()
        ev = ClownEvent()
        # Park the die well left of Pip so the auto-grab fires this tick.
        ev.dice_x = w.bird.x - 100
        ev.update(w, 1 / 60.0)
        self.assertTrue(ev.collected, "a die that drifts past Pip auto-grabs")
        self.assertEqual(ev.phase, "rolling")


class WeatherWidthInvariance(unittest.TestCase):
    """Rain/snow event DURATIONS must stay fixed in wall-clock seconds (and so
    in pillars) regardless of how long the biome day is — extending the cycle to
    absorb the clown event must NOT stretch the storms. Their shape offsets are
    scaled by (original cycle / current cycle); these products must equal the
    original 320 s-cycle phase widths × 320."""

    def test_rain_durations_are_cycle_invariant(self):
        import game.weather as w
        from game.biome import CYCLE_SECONDS as cyc
        drizzle = (w.RAIN_DRIZZLE_END - w.RAIN_DRIZZLE_START) * cyc
        self.assertAlmostEqual(drizzle, 0.18 * 320.0, places=4)
        self.assertAlmostEqual(w.RAIN_STORM_WIDTH * cyc, 0.08 * 320.0, places=4)

    def test_snow_duration_is_cycle_invariant(self):
        import game.weather as w
        from game.biome import CYCLE_SECONDS as cyc
        self.assertAlmostEqual(w.SNOW_STORM_WIDTH * cyc, 0.13 * 320.0, places=4)


if __name__ == "__main__":
    unittest.main()
