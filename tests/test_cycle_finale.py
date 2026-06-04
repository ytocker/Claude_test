"""
Cycle-finale polish — locked behaviour.

Pins:
  - Treasure chest never lands in `world.powerups_picked` so the
    run-summary chip strip can never show a chest icon.
  - The chest's pickup hitbox tracks the FULL drawn sprite (~100 x 82
    px), not the small 34 px circle a regular power-up uses. Brushing
    the chest's outer corner picks it up.
  - Bunting / balloons / crowd anchor to the flanking real pillars'
    centres (last real before, first real after the 5-phantom band).
"""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
pygame.init()
pygame.display.set_mode((360, 640))

from game.world import World  # noqa: E402
from game.entities import PowerUp  # noqa: E402
from game.config import PIPE_W  # noqa: E402
from game.treasure_box import PICKUP_W, PICKUP_H  # noqa: E402


def _drop_chest(world, bx=180.0, by=320.0):
    chest = PowerUp(bx, by, kind="treasure")
    world.powerups.append(chest)
    return chest


class TreasureNotInSummary(unittest.TestCase):
    def test_powerups_picked_skips_treasure(self):
        w = World()
        chest = _drop_chest(w)
        # Drive the bird onto the chest centre — guaranteed pickup
        # whatever the collision model is.
        w.bird.x, w.bird.y = chest.x, chest.y
        w._check_pickups()
        self.assertTrue(chest.collected, "chest should be picked up")
        self.assertEqual(w.powerups_picked.get("treasure", 0), 0,
                         "treasure must not increment powerups_picked")


class ChestSpriteRectCollision(unittest.TestCase):
    """The chest is 100x82; circle test was ~34 px from centre.
    A horizontal offset of 48 px from centre is past the old circle
    but well inside the new sprite-rect."""

    def test_corner_brush_picks_up(self):
        w = World()
        chest = _drop_chest(w, bx=200.0, by=320.0)
        # 48 px right of chest centre — inside the 50 px half-width,
        # outside the 34 px collision circle.
        w.bird.x = chest.x + 48
        w.bird.y = chest.y
        w._check_pickups()
        self.assertTrue(chest.collected,
                        "corner-brush should pick up the chest under "
                        "the new sprite-rect hitbox")

    def test_far_miss_still_misses(self):
        w = World()
        chest = _drop_chest(w, bx=200.0, by=320.0)
        # Well outside the sprite rect — must not pick up.
        w.bird.x = chest.x + PICKUP_W
        w.bird.y = chest.y + PICKUP_H
        w._check_pickups()
        self.assertFalse(chest.collected,
                         "far miss must not pick up the chest")


class CelebrationSpawnAnchors(unittest.TestCase):
    """Bunting + crowd + balloons spawn at flanking-pillar coords."""

    def _force_finale(self, world):
        # Advance biome wrap so the next pillar carries the finale flag,
        # then call _spawn_pipe enough times to hit phantom #3 (chest
        # drop). Easier path: poke the internal counters directly,
        # matching what world.update would do at the wrap.
        from game.config import (
            CYCLE_FINALE_RUSH_PILLARS, CYCLE_FINALE_BOX_INDEX)
        world._finale_rush_remaining = (
            CYCLE_FINALE_RUSH_PILLARS - CYCLE_FINALE_BOX_INDEX)
        world._finale_box_dropped = False
        # Spawn one pillar — the next call will hit the middle-phantom
        # branch and drop the chest plus all celebration items.
        last_x = world.pipes[-1].x if world.pipes else 800.0
        world._spawn_pipe(last_x + 280.0)

    def test_spawn_creates_bunting_balloon_crowd(self):
        w = World()
        # Need at least one real pillar in the list for the LEFT
        # flanking anchor to be picked up. Spawn 3 normal pillars
        # first so self.pipes has a non-phantom history.
        x = 800.0
        for _ in range(3):
            w._spawn_pipe(x)
            x += 280.0
        last_real = w.pipes[-1]
        last_real_centre_x = last_real.x + PIPE_W * 0.5
        self._force_finale(w)
        self.assertEqual(len(w.celebration_buntings), 1)
        self.assertEqual(len(w.celebration_balloon_clusters), 1)
        self.assertEqual(len(w.celebration_crowds), 1)
        bunting = w.celebration_buntings[-1]
        # Left endpoint sits on the last real pillar's centre.
        self.assertAlmostEqual(bunting.x_left, last_real_centre_x,
                               places=2)
        # Left y on the upper-pipe tip of that pillar.
        expected_y = last_real.gap_y - last_real.gap_h * 0.5
        self.assertAlmostEqual(bunting.y_left, expected_y, places=2)
        # Right endpoint at predicted next-real-pillar x.
        crowd = w.celebration_crowds[-1]
        self.assertEqual(len(crowd.cluster_xs), 5,
                         "crowd should have 5 clusters")
        # One cluster x is the finish line itself.
        chest = next(m for m in w.powerups if m.kind == "treasure")
        finish_x = chest.x
        self.assertIn(finish_x, crowd.cluster_xs,
                      "one cluster must sit exactly on the finish stripe")
        # All clusters fall within the [left, right] span.
        for cx in crowd.cluster_xs:
            self.assertGreaterEqual(cx, bunting.x_left - 0.001)
            self.assertLessEqual(cx, bunting.x_right + 0.001)


if __name__ == "__main__":
    unittest.main()
