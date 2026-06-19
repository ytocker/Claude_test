"""
Achievements engine unit tests.

Run with: ``python -m pytest tests/``.

Exercises the end-of-run evaluator: correct unlocks fire from a finished run's
stats, lifetime counters accumulate across runs, derived stats (distinct
power-ups, lottery jackpot from the proof ledger) resolve, and a repeat of an
identical run yields no *new* unlocks. Persistence I/O is stubbed so the tests
never touch disk or a browser bridge.
"""
import unittest

from game import achievements as ach
from game.config import RAIN_START_PILLAR


class _FakeProof:
    def __init__(self, events):
        self._events = list(events)

    def events_tuple(self):
        return list(self._events)


class _FakeWorld:
    """Minimal stand-in exposing the attributes evaluate_run reads."""

    def __init__(self, **kw):
        self.score = kw.get("score", 0)
        self.coin_count = kw.get("coin_count", 0)
        self.pillars_passed = kw.get("pillars_passed", 0)
        self.time_alive = kw.get("time_alive", 0.0)
        self.near_misses = kw.get("near_misses", 0)
        self.flap_count = kw.get("flap_count", 0)
        self.cycles_completed = kw.get("cycles_completed", 0)
        self.powerups_picked = dict(ach._blank()["life"]["powerups_seen"])  # empty-ish
        self.powerups_picked = kw.get("powerups_picked", {})
        self._proof = _FakeProof(kw.get("events", []))


class TestAchievements(unittest.TestCase):

    def setUp(self):
        # Stub persistence so nothing hits disk / the browser bridge.
        self._orig_save = ach.save
        ach.save = lambda store=None: None
        ach.reset_cache()

    def tearDown(self):
        ach.save = self._orig_save
        ach.reset_cache()

    def test_first_flight_and_basic_thresholds(self):
        store = ach._blank()
        w = _FakeWorld(pillars_passed=30, score=120, coin_count=26)
        newly = ach.evaluate_run(w, store)
        self.assertIn("first_flight", newly)
        self.assertIn("pillar_25", newly)
        self.assertIn("score_100", newly)
        self.assertIn("coin_25_run", newly)
        # Not reached this run.
        self.assertNotIn("pillar_50", newly)
        self.assertNotIn("score_500", newly)

    def test_no_rerun_duplicates(self):
        store = ach._blank()
        w = _FakeWorld(pillars_passed=30)
        first = ach.evaluate_run(w, store)
        self.assertIn("first_flight", first)
        # Same run again — already-unlocked ids must not re-fire.
        second = ach.evaluate_run(_FakeWorld(pillars_passed=30), store)
        self.assertEqual(second, [])

    def test_lifetime_accumulation_unlocks(self):
        store = ach._blank()
        # 500 lifetime coins via ten 50-coin runs; coins_500_life unlocks on
        # the run that crosses the threshold, not before.
        unlocked_on = None
        for i in range(10):
            newly = ach.evaluate_run(_FakeWorld(coin_count=50), store)
            if "coins_500_life" in newly:
                unlocked_on = i
        self.assertEqual(store["life"]["total_coins"], 500)
        self.assertEqual(store["life"]["total_runs"], 10)
        self.assertEqual(unlocked_on, 9)

    def test_distinct_powerups_run_and_life(self):
        store = ach._blank()
        w = _FakeWorld(powerups_picked={"triple": 1, "magnet": 2,
                                        "slowmo": 1, "ghost": 1})
        newly = ach.evaluate_run(w, store)
        self.assertIn("first_powerup", newly)
        self.assertIn("powerup_sampler", newly)   # 4 distinct in the run
        # magnet_life counts magnet + megamagnet; only 2 so far.
        self.assertNotIn("magnet_life", newly)

    def test_hidden_secret_from_pickup(self):
        store = ach._blank()
        w = _FakeWorld(powerups_picked={"genie": 1, "poison": 1})
        newly = ach.evaluate_run(w, store)
        self.assertIn("made_a_wish", newly)
        self.assertIn("poisoned", newly)
        self.assertTrue(ach.BY_ID["made_a_wish"].hidden)

    def test_lottery_jackpot_from_events(self):
        store = ach._blank()
        jackpot = ach._JACKPOT_DELTA
        w = _FakeWorld(events=[(1.0, jackpot, "lottery")])
        newly = ach.evaluate_run(w, store)
        self.assertIn("jackpot", newly)
        # A losing lottery roll must not count.
        store2 = ach._blank()
        w2 = _FakeWorld(events=[(1.0, -10, "lottery")])
        self.assertNotIn("jackpot", ach.evaluate_run(w2, store2))

    def test_weather_biome_threshold(self):
        store = ach._blank()
        w = _FakeWorld(pillars_passed=RAIN_START_PILLAR)
        self.assertIn("storm_rider", ach.evaluate_run(w, store))

    def test_registry_ids_unique(self):
        ids = [a.id for a in ach.ACHIEVEMENTS]
        self.assertEqual(len(ids), len(set(ids)))
        # Every achievement belongs to a known category bucket.
        for a in ach.ACHIEVEMENTS:
            self.assertIn(a, ach.BY_CAT[a.category])


if __name__ == "__main__":
    unittest.main()
