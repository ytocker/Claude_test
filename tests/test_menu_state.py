"""Menu lifecycle guards — the bird you see on the menu must be clean and correct.

The World is never rebuilt on the way back from a run and the menu's idle tick
touches no bird flag, so before ``App._enter_menu`` existed the menu inherited
whatever the last run left behind: a dead Pip still cross-fading to the death
palette, a last-life bandage, an unexpired KFC/ghost skin. It also never picked
up a loadout equipped in the store, because the only other cosmetics sync runs
at run start — so a fresh launch always showed the default macaw no matter what
the player owned.

These tests pin the three properties that keep that fixed, plus the related
menu-idle guarantee that the menu no longer drives a finished run's spawner.

Run with: ``python -m pytest tests/``.
"""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((360, 640))

from game import store_data
from game.scenes import App, STATE_MENU


class TestEnterMenuResetsRunState(unittest.TestCase):
    """A finished run must not leak its bird into the menu."""

    def test_dead_and_damaged_state_is_cleared(self):
        app = App()
        b = app.world.bird
        # Simulate the tail of a bad run: dead, bandaged, mid-power-up.
        b.alive = False
        b.death_fade_t = 0.8
        b.on_last_life = True
        b.on_first_hit = True
        b.kfc_active = True
        b.ghost_active = True
        b.grow_active = True

        app._enter_menu()

        nb = app.world.bird
        self.assertEqual(app.state, STATE_MENU)
        self.assertTrue(nb.alive, "menu bird must be alive")
        self.assertEqual(nb.death_fade_t, 0.0,
                         "death cross-fade would draw a dead Pip on the menu")
        self.assertFalse(nb.on_last_life, "last-life bandage leaked to the menu")
        self.assertFalse(nb.on_first_hit, "first-hit bandage leaked to the menu")
        for flag in ("kfc_active", "ghost_active", "grow_active"):
            self.assertFalse(getattr(nb, flag), f"{flag} leaked to the menu")


class TestEnterMenuAppliesLoadout(unittest.TestCase):
    """The menu must show what the player actually owns."""

    def test_equipped_skin_and_parcel_are_applied(self):
        app = App()
        orig = store_data.equipped
        store_data.equipped = lambda slot: {"skin": "skin_zombie",
                                            "parcel": "parcel_gift"}.get(slot)
        try:
            app._enter_menu()
        finally:
            store_data.equipped = orig
        self.assertEqual(app.world.bird.equipped_skin, "skin_zombie")
        self.assertEqual(app.world.bird.equipped_parcel, "parcel_gift")

    def test_falls_back_to_base_when_nothing_equipped(self):
        app = App()
        orig = store_data.equipped
        store_data.equipped = lambda slot: None
        try:
            app._enter_menu()
        finally:
            store_data.equipped = orig
        self.assertEqual(app.world.bird.equipped_skin, "skin_base")
        self.assertEqual(app.world.bird.equipped_parcel, "parcel_base")


class TestEnterMenuIsCheapOnRepeat(unittest.TestCase):
    """rebuild_skin_combos re-bakes 28 composites and drops the shared rotation
    cache, so an unguarded call on every menu entry would cost ~23ms natively
    and far more on WASM. It must only fire when the loadout actually changed."""

    def test_no_rebuild_when_skin_is_unchanged(self):
        from game.entities import Bird

        calls = []
        orig = Bird.rebuild_skin_combos

        def counted(self):
            calls.append(self.equipped_skin)
            return orig(self)

        Bird.rebuild_skin_combos = counted
        try:
            app = App()
            app._enter_menu()
            first = len(calls)
            app._enter_menu()
            app._enter_menu()
        finally:
            Bird.rebuild_skin_combos = orig

        self.assertEqual(first, 1, "first menu entry should build combos once")
        self.assertEqual(len(calls), 1,
                         "repeat menu entries must not rebuild an unchanged skin")


class TestMenuIdleDoesNotDriveTheSpawner(unittest.TestCase):
    """The menu branch returns before pipes/coins/power-ups are drawn, and every
    path into play builds a fresh World — so spawning here was invisible, and it
    kept advancing a finished run's clown/finale machinery from the menu."""

    def test_idle_tick_spawns_nothing(self):
        app = App()
        app._enter_menu()
        w = app.world
        before = (len(w.pipes), len(w.coins), len(w.powerups),
                  getattr(w, "coins_spawned", 0))
        for _ in range(60 * 120):          # two minutes of idling
            w.world_idle_tick(1 / 60)
        after = (len(w.pipes), len(w.coins), len(w.powerups),
                 getattr(w, "coins_spawned", 0))
        self.assertEqual(before, after,
                         "menu idle must not spawn or cull gameplay objects")
        self.assertIsNone(getattr(w, "clown_event", None),
                          "a ClownEvent must never be constructed on the menu")

    def test_idle_tick_still_animates_what_the_menu_draws(self):
        app = App()
        app._enter_menu()
        w = app.world
        t0, s0, y0 = w.biome_time, w.bg_scroll, w.bird.y
        for _ in range(30):
            w.world_idle_tick(1 / 60)
        self.assertGreater(w.biome_time, t0, "biome clock drives the menu sky")
        self.assertGreater(w.bg_scroll, s0, "scroll drives parallax and the bob")
        self.assertNotEqual(w.bird.y, y0, "the menu bird should still bob")


if __name__ == "__main__":
    unittest.main()
