"""Gameplay & balance metrics — power-up efficacy (with zero-denominator
guards), distributions, economy, and the resurrected skill curve."""
from __future__ import annotations

import pandas as pd

import metrics
from metrics import gameplay as m
from constants import POWERUP_KEYS_ACTIVE

NOW = pd.Timestamp.now(tz="UTC")


def _pu(**kw):
    d = {k: 0 for k in POWERUP_KEYS_ACTIVE}
    d.update(kw)
    return d


def _row(*, id_, device_id="a", days_ago=1, score=50, duration_s=40,
         coins=10, pillars=5, near_misses=1, powerups=None) -> dict:
    return {
        "id": id_, "device_id": device_id,
        "played_at": NOW - pd.Timedelta(days=days_ago, hours=-1),
        "score": score, "duration_s": duration_s, "coins": coins,
        "pillars": pillars, "near_misses": near_misses,
        "powerups": powerups if powerups is not None else _pu(),
        "submit_error": None,
    }


def _frame(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["played_at"] = pd.to_datetime(df["played_at"], utc=True)
    return df


def _empty() -> pd.DataFrame:
    return pd.DataFrame(columns=[
        "id", "device_id", "played_at", "score", "duration_s",
        "coins", "pillars", "near_misses", "powerups", "submit_error",
    ])


def test_score_and_duration_summary():
    df = _frame([_row(id_=i, score=10 * i, duration_s=5 * i) for i in range(1, 11)])
    s = metrics.score_summary(df, days=7)
    assert s["median"] == 55.0
    assert s["max"] == 100.0
    d = metrics.duration_summary(df, days=7)
    assert d["median"] == 27.5
    assert d["max"] == 50.0


def test_coins_per_run():
    df = _frame([_row(id_=1, coins=10), _row(id_=2, coins=20)])
    assert metrics.coins_per_run(df, days=7) == 15.0


def test_powerup_efficacy_positive_for_helpful_powerup():
    # magnet runs score high; non-magnet runs score low.
    rows = [_row(id_=i, score=200, powerups=_pu(magnet=1)) for i in range(5)]
    rows += [_row(id_=10 + i, score=50, powerups=_pu()) for i in range(5)]
    eff = metrics.powerup_efficacy(_frame(rows), days=30).set_index("powerup")
    assert eff.loc["magnet", "n_with"] == 5
    assert eff.loc["magnet", "n_without"] == 5
    assert eff.loc["magnet", "score_lift_pct"] > 0


def test_powerup_efficacy_negative_for_harmful_powerup():
    rows = [_row(id_=i, score=20, duration_s=10, powerups=_pu(grow=1)) for i in range(4)]
    rows += [_row(id_=10 + i, score=120, duration_s=90, powerups=_pu()) for i in range(6)]
    eff = metrics.powerup_efficacy(_frame(rows), days=30).set_index("powerup")
    assert eff.loc["grow", "score_lift_pct"] < 0


def test_powerup_efficacy_omits_never_picked():
    rows = [_row(id_=i, powerups=_pu(magnet=1)) for i in range(3)]
    eff = metrics.powerup_efficacy(_frame(rows), days=30)
    # Only magnet was ever picked → only magnet appears.
    assert set(eff["powerup"]) == {"magnet"}


def test_powerup_efficacy_guards_zero_baseline():
    # Every run picked magnet → no "without" group → lift guarded to 0.
    rows = [_row(id_=i, powerups=_pu(magnet=1)) for i in range(4)]
    eff = metrics.powerup_efficacy(_frame(rows), days=30).set_index("powerup")
    assert eff.loc["magnet", "n_without"] == 0
    assert eff.loc["magnet", "score_lift_pct"] == 0.0


def test_powerup_efficacy_excess_lift_nets_out_exposure():
    # Magnet runs are both higher-scoring AND longer; excess_lift is the
    # score lift in *excess* of the survival lift (the exposure proxy).
    rows = [_row(id_=i, score=200, duration_s=80, powerups=_pu(magnet=1))
            for i in range(6)]
    rows += [_row(id_=10 + i, score=100, duration_s=40, powerups=_pu())
             for i in range(6)]
    eff = m.powerup_efficacy(_frame(rows), days=30).set_index("powerup")
    r = eff.loc["magnet"]
    # score doubled (+100%), duration doubled (+100%) → excess ~0: the
    # score gain is fully explained by more time on screen.
    assert r["score_lift_pct"] == 100.0
    assert r["dur_lift_pct"] == 100.0
    assert abs(r["excess_lift_pct"]) < 1e-9


def test_powerup_efficacy_low_n_flag():
    # 5 magnet runs (< MIN_EFFICACY_N) → flagged low_n; magnet picked in
    # enough to clear it when we add more.
    few = [_row(id_=i, powerups=_pu(magnet=1)) for i in range(5)]
    few += [_row(id_=10 + i, powerups=_pu(triple=1)) for i in range(20)]
    eff = m.powerup_efficacy(_frame(few), days=30).set_index("powerup")
    assert bool(eff.loc["magnet", "low_n"]) is True
    assert bool(eff.loc["triple", "low_n"]) is False


def test_powerup_efficacy_has_excess_and_low_n_columns():
    rows = [_row(id_=i, powerups=_pu(magnet=1)) for i in range(3)]
    rows += [_row(id_=10 + i, powerups=_pu()) for i in range(3)]
    eff = m.powerup_efficacy(_frame(rows), days=30)
    assert {"excess_lift_pct", "low_n"} <= set(eff.columns)


def test_coin_economy_ratio():
    df = _frame([
        _row(id_=1, coins=20, pillars=10),
        _row(id_=2, coins=10, pillars=10),
    ])
    econ = metrics.coin_economy_by_day(df, days=7)
    # Same day: 30 coins / 20 pillars = 1.5.
    assert econ["coins_per_pillar"].iloc[-1] == 1.5


def test_skill_proxy_columns_and_filters_short_runs():
    df = _frame([
        _row(id_=1, duration_s=1, pillars=5),   # <2s → dropped
        _row(id_=2, duration_s=20, pillars=10, near_misses=4),
    ])
    out = metrics.skill_proxy_by_day(df, days=30)
    assert set(out.columns) == {"date", "pillars_per_s", "near_miss_rate"}
    assert len(out) == 1  # only the 20s run survives


def test_gameplay_metrics_on_empty():
    assert metrics.powerup_efficacy(_empty(), days=30).empty
    assert metrics.coin_economy_by_day(_empty(), days=30).empty
    assert metrics.score_summary(_empty()) == {"median": 0.0, "p90": 0.0, "max": 0.0}
    assert metrics.coins_per_run(_empty()) == 0.0
    assert metrics.duration_distribution(_empty()).empty
