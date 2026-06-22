"""Unit tests for the Arcade content/logic (crystal ball, vending, Beakon).
Pure functions with an injected RNG — deterministic, no pygame.
"""
import random

from game import arcade
from game.store_data import _default_stats


def _stats(**kw):
    s = _default_stats()
    s.update(kw)
    return s


def test_crystal_prediction_shape():
    rng = random.Random(0)
    for _ in range(200):
        p = arcade.crystal_prediction(_stats(death_pillar_histogram=[0, 1, 3, 2]), rng)
        assert set(p) == {"text", "kind", "predicted_pillar"}
        assert p["kind"] in ("real", "meta", "nonsense")
        assert isinstance(p["text"], str) and p["text"]
        assert p["predicted_pillar"] is None or isinstance(p["predicted_pillar"], int)
        # Real-tip flavor never commits a falsifiable number.
        if p["kind"] in ("real", "nonsense"):
            assert p["predicted_pillar"] is None


def test_grade_prophecy():
    assert arcade.grade_prophecy(None, 5) is None
    assert arcade.grade_prophecy(7, 8) is True   # within +-1
    assert arcade.grade_prophecy(7, 7) is True
    assert arcade.grade_prophecy(7, 10) is False


def test_vend_covers_all_kinds_and_pays_out():
    rng = random.Random(1)
    kinds = set()
    for _ in range(5000):
        out = arcade.vend(rng)
        kinds.add(out["kind"])
        assert out["coins_back"] >= 0
        assert out["name"] and out["id"]
        if out["kind"] == "jackpot":
            assert out["coins_back"] == arcade.JACKPOT_COINS
        if out["kind"] == "out_of_order":
            assert out["coins_back"] == 0
    # Over 5000 rolls every outcome kind should appear, incl. the rare ones.
    assert {"trinket", "charm", "jackpot", "change",
            "out_of_order", "moth", "gerald"} <= kinds


def test_beakon_refund_only_for_addicts():
    rng = random.Random(2)
    for _ in range(100):
        tip = arcade.beakon_tip(rng, visit_count=1)
        assert tip["refund"] is False
    saw_refund = any(
        arcade.beakon_tip(rng, visit_count=50)["refund"] for _ in range(100))
    assert saw_refund


def test_beakon_tip_shape():
    rng = random.Random(3)
    for _ in range(200):
        tip = arcade.beakon_tip(rng, visit_count=3)
        assert set(tip) == {"text", "kind", "refund"}
        assert tip["kind"] in ("real", "meta", "nonsense", "refund")
        assert tip["text"]
