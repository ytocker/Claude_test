"""Unit tests for the persistent Profile-stats accumulator (store_data).

These cover record_run's aggregation, the death-context counters, and that an
older save (missing the whole ``stats`` block) upgrades silently via _coerce.
Pure data — no pygame, no network.
"""
import json
from types import SimpleNamespace

import pytest

from game import store_data


def _fake_run(**kw):
    base = dict(
        score=0, pillars_passed=0, time_alive=0.0, coin_count=0,
        coins_spawned=0, flap_count=0, near_misses=0,
        powerups_picked={}, max_flaps_per_sec=0, death_powerups=[],
    )
    base.update(kw)
    return SimpleNamespace(**base)


@pytest.fixture()
def fresh_store(tmp_path, monkeypatch):
    monkeypatch.setattr(store_data, "STORE_FILE", str(tmp_path / "store.json"))
    monkeypatch.setattr(store_data, "_IS_BROWSER", False)
    store_data._reset_for_test()
    yield store_data
    store_data._reset_for_test()


def test_record_run_accumulates_lifetime_and_bests(fresh_store):
    fresh_store.record_run(_fake_run(
        score=42, pillars_passed=9, time_alive=15.0, coin_count=8,
        coins_spawned=12, flap_count=30, near_misses=3,
        powerups_picked={"magnet": 1, "ghost": 2}, max_flaps_per_sec=7))
    fresh_store.record_run(_fake_run(
        score=20, pillars_passed=14, time_alive=11.0, coin_count=5,
        coins_spawned=5, flap_count=22, near_misses=1,
        powerups_picked={"magnet": 1}, max_flaps_per_sec=9))

    s = fresh_store.all_stats()
    assert s["runs_played"] == 2
    assert s["total_pillars"] == 23
    assert s["total_coins_earned"] == 13
    assert s["total_powerups"] == 4
    assert s["powerups_by_kind"] == {"magnet": 2, "ghost": 2}
    # coins_ignored only counts the first run's 4 un-grabbed coins.
    assert s["coins_ignored"] == 4
    # Bests are per-run maxima, not sums.
    assert s["best_score"] == 42
    assert s["best_pillars"] == 14
    assert s["best_time_s"] == 15.0
    assert s["max_flaps_per_sec"] == 9


def test_death_context_counters(fresh_store):
    # A scoreless, instant, pillar-one washout with a wasted Ghost.
    fresh_store.record_run(_fake_run(
        score=0, pillars_passed=0, time_alive=1.2, death_powerups=["ghost"]))
    s = fresh_store.all_stats()
    assert s["scoreless_deaths"] == 1
    assert s["pillar1_deaths"] == 1
    assert s["sub3s_deaths"] == 1
    assert s["deaths_with_powerup"] == {"ghost": 1}
    assert s["death_pillar_histogram"][0] == 1
    # No dignified run yet, so the board has no anchor date.
    assert s["last_dignified_date"] == ""


def test_same_pillar_streak(fresh_store):
    for _ in range(3):
        fresh_store.record_run(_fake_run(score=5, pillars_passed=12, time_alive=8.0))
    fresh_store.record_run(_fake_run(score=9, pillars_passed=20, time_alive=9.0))
    s = fresh_store.all_stats()
    assert s["last_death_pillar"] == 20
    assert s["same_pillar_streak"] == 1  # reset when the death pillar changed
    assert s["death_pillar_histogram"][12] == 3


def test_histogram_caps(fresh_store):
    fresh_store.record_run(_fake_run(score=999, pillars_passed=500, time_alive=90.0))
    s = fresh_store.all_stats()
    assert len(s["death_pillar_histogram"]) == store_data._HIST_CAP + 1
    assert s["death_pillar_histogram"][store_data._HIST_CAP] == 1


def test_dignified_run_sets_date(fresh_store):
    fresh_store.record_run(_fake_run(score=30, pillars_passed=10, time_alive=12.0))
    assert fresh_store.all_stats()["last_dignified_date"] != ""


def test_old_save_without_stats_upgrades(fresh_store, tmp_path):
    # A pre-stats save: wallet + owned only, no "stats" key at all.
    legacy = {"version": 1, "wallet": 250, "owned": []}
    with open(fresh_store.STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(legacy, f)
    fresh_store._reset_for_test()
    fresh_store.load()
    assert fresh_store.balance() == 250
    s = fresh_store.all_stats()
    assert s["runs_played"] == 0
    assert s["best_score"] == 0
    # And recording still works on the upgraded state.
    fresh_store.record_run(_fake_run(score=7, pillars_passed=4, time_alive=6.0))
    assert fresh_store.all_stats()["runs_played"] == 1
