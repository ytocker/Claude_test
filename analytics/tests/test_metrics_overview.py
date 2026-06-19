"""Overview / live-ops metrics — driven by NOW-relative frames so the
assertions are stable whenever the suite runs."""
from __future__ import annotations

import pandas as pd

import metrics
from constants import POWERUP_KEYS_ACTIVE

NOW = pd.Timestamp.now(tz="UTC")


def _row(*, id_, device_id, offset, score=50, duration_s=40, coins=10,
         pillars=5, near_misses=1, powerups=None, submit_error=None) -> dict:
    return {
        "id": id_, "device_id": device_id, "played_at": NOW - offset,
        "score": score, "duration_s": duration_s, "coins": coins,
        "pillars": pillars, "near_misses": near_misses,
        "powerups": powerups or {k: 0 for k in POWERUP_KEYS_ACTIVE},
        "submit_error": submit_error,
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


def test_plays_window_delta_splits_current_and_prior():
    rows = [
        _row(id_=1, device_id="a", offset=pd.Timedelta(days=1)),   # current 7d
        _row(id_=2, device_id="b", offset=pd.Timedelta(days=3)),   # current 7d
        _row(id_=3, device_id="c", offset=pd.Timedelta(days=9)),   # prior 7d
        _row(id_=4, device_id="d", offset=pd.Timedelta(days=20)),  # neither
    ]
    cur, prev = metrics.plays_window_delta(_frame(rows), days=7)
    assert cur == 2
    assert prev == 1


def test_plays_window_delta_empty():
    assert metrics.plays_window_delta(_empty(), days=7) == (0, 0)


def test_minutes_since_last_play_none_on_empty():
    assert metrics.minutes_since_last_play(_empty()) is None


def test_minutes_since_last_play_recent():
    df = _frame([_row(id_=1, device_id="a", offset=pd.Timedelta(minutes=30))])
    m = metrics.minutes_since_last_play(df)
    assert 25 <= m <= 35


def test_rejection_rate_counts_non_null_submit_error():
    rows = [
        _row(id_=1, device_id="a", offset=pd.Timedelta(hours=1)),
        _row(id_=2, device_id="b", offset=pd.Timedelta(hours=2), submit_error="chain: x"),
        _row(id_=3, device_id="c", offset=pd.Timedelta(hours=3), submit_error="score: y"),
        _row(id_=4, device_id="d", offset=pd.Timedelta(hours=4)),
    ]
    assert metrics.rejection_rate(_frame(rows), days=7) == 0.5


def test_rejection_rate_graceful_without_column():
    df = _frame([_row(id_=1, device_id="a", offset=pd.Timedelta(hours=1))]).drop(
        columns=["submit_error"])
    assert metrics.rejection_rate(df, days=7) == 0.0


def test_rejection_rate_empty():
    assert metrics.rejection_rate(_empty(), days=7) == 0.0


def test_rejection_reasons_groups_by_gate_name():
    rows = [
        _row(id_=1, device_id="a", offset=pd.Timedelta(hours=1),
             submit_error="score: exceeds MAX_PLAUSIBLE_SCORE"),
        _row(id_=2, device_id="b", offset=pd.Timedelta(hours=2),
             submit_error="score: something else"),
        _row(id_=3, device_id="c", offset=pd.Timedelta(hours=3),
             submit_error="chain: hash mismatch"),
        _row(id_=4, device_id="d", offset=pd.Timedelta(hours=4)),
    ]
    out = metrics.rejection_reasons(_frame(rows), days=7)
    counts = dict(zip(out["reason"], out["count"]))
    assert counts["score"] == 2
    assert counts["chain"] == 1


def test_rejection_reasons_empty_when_no_rejections():
    rows = [_row(id_=1, device_id="a", offset=pd.Timedelta(hours=1))]
    assert metrics.rejection_reasons(_frame(rows), days=7).empty


def test_daily_plays_with_band_has_bounds_and_length():
    rows = [_row(id_=i, device_id="a", offset=pd.Timedelta(days=i % 10))
            for i in range(30)]
    band = metrics.daily_plays_with_band(_frame(rows), days=14)
    assert len(band) == 14
    assert set(band.columns) == {"date", "plays", "mean", "lo", "hi"}
    assert (band["lo"] <= band["hi"]).all()
    assert (band["lo"] >= 0).all()
