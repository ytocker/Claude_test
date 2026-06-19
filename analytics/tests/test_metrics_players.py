"""Players & retention metrics — the highest-risk new code. Cohorts are
built at controlled day-offsets from TODAY so D1/D7 have known answers."""
from __future__ import annotations

import pandas as pd

import metrics
from constants import POWERUP_KEYS_ACTIVE

NOW = pd.Timestamp.now(tz="UTC")
TODAY = NOW.normalize()


def _row(*, id_, device_id, days_ago, score=50) -> dict:
    # Pin to mid-day so day-flooring is unambiguous regardless of run time.
    played = TODAY - pd.Timedelta(days=days_ago) + pd.Timedelta(hours=12)
    return {
        "id": id_, "device_id": device_id, "played_at": played,
        "score": score, "duration_s": 40, "coins": 10, "pillars": 5,
        "near_misses": 1, "powerups": {k: 0 for k in POWERUP_KEYS_ACTIVE},
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


# One cohort installed 10 days ago:
#   A: plays day-10 (offset0), day-9 (offset1), day-3 (offset7)
#   B: plays day-10, day-9 (offset1)
#   C: plays day-10 only (one-shot)
# Plus D: installs today (for new_players_today).
def _cohort_frame() -> pd.DataFrame:
    return _frame([
        _row(id_=1, device_id="A", days_ago=10),
        _row(id_=2, device_id="A", days_ago=9),
        _row(id_=3, device_id="A", days_ago=3),
        _row(id_=4, device_id="B", days_ago=10),
        _row(id_=5, device_id="B", days_ago=9),
        _row(id_=6, device_id="C", days_ago=10),
        _row(id_=7, device_id="D", days_ago=0),
    ])


def test_cohort_retention_known_fractions():
    cr = metrics.cohort_retention(_cohort_frame(), max_day=7)
    cohort = TODAY - pd.Timedelta(days=10)
    sub = cr[cr["cohort_date"] == cohort].set_index("day_offset")
    assert int(sub.loc[0, "cohort_size"]) == 3
    assert int(sub.loc[0, "retained"]) == 3      # all 3 played install day
    assert int(sub.loc[1, "retained"]) == 2      # A, B
    assert int(sub.loc[7, "retained"]) == 1      # A only
    assert sub.loc[1, "retained_frac"] == 2 / 3


def test_retention_curve_summary_pooled():
    summ = metrics.retention_summary(_cohort_frame())
    assert summ["d1"] == 2 / 3
    assert summ["d7"] == 1 / 3


def test_cohort_censors_future_offsets():
    # Cohort installed 2 days ago: offsets 3..7 are in the future → omitted.
    df = _frame([
        _row(id_=1, device_id="X", days_ago=2),
        _row(id_=2, device_id="X", days_ago=1),
    ])
    cr = metrics.cohort_retention(df, max_day=7)
    offsets = set(cr["day_offset"])
    assert offsets == {0, 1, 2}


def test_retention_matrix_shape_and_blank_cells():
    mat = metrics.retention_matrix(_cohort_frame(), max_day=7)
    assert list(mat.columns) == list(range(8))
    # Today's cohort has only offset 0 observed; the rest must be NaN.
    today = TODAY
    assert mat.loc[today, 0] == 1.0
    assert pd.isna(mat.loc[today, 1])


def test_new_players_today():
    assert metrics.new_players_today(_cohort_frame()) == 1


def test_new_vs_returning_split():
    nvr = metrics.new_vs_returning_by_day(_cohort_frame(), days=30).set_index("date")
    d10 = TODAY - pd.Timedelta(days=10)
    d9 = TODAY - pd.Timedelta(days=9)
    assert int(nvr.loc[d10, "new"]) == 3        # A, B, C first seen
    assert int(nvr.loc[d10, "returning"]) == 0
    assert int(nvr.loc[d9, "new"]) == 0
    assert int(nvr.loc[d9, "returning"]) == 2   # A, B back


def test_sessions_per_active_day_counts_plays():
    # A has 2 plays on the same day, B has 1.
    df = _frame([
        _row(id_=1, device_id="A", days_ago=1),
        _row(id_=2, device_id="A", days_ago=1),
        _row(id_=3, device_id="B", days_ago=1),
    ])
    s = metrics.sessions_per_active_day(df, days=7)
    assert sorted(s.tolist()) == [1, 2]


def test_retention_on_empty():
    assert metrics.retention_curve(_empty()).empty
    assert metrics.retention_matrix(_empty()).empty
    assert metrics.cohort_retention(_empty()).empty
    assert metrics.retention_summary(_empty()) == {"d1": 0.0, "d7": 0.0}
    assert metrics.new_players_today(_empty()) == 0
