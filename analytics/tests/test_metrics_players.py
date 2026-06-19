"""Players & retention metrics — the highest-risk new code. Cohorts are
built at controlled day-offsets from TODAY so D1/D7 have known answers."""
from __future__ import annotations

import pandas as pd

from metrics import players as m
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
    cr = m.cohort_retention(_cohort_frame(), max_day=7)
    cohort = TODAY - pd.Timedelta(days=10)
    sub = cr[cr["cohort_date"] == cohort].set_index("day_offset")
    assert int(sub.loc[0, "cohort_size"]) == 3
    assert int(sub.loc[0, "retained"]) == 3      # all 3 played install day
    assert int(sub.loc[1, "retained"]) == 2      # A, B
    assert int(sub.loc[7, "retained"]) == 1      # A only
    assert sub.loc[1, "retained_frac"] == 2 / 3


def test_retention_curve_summary_pooled():
    # Summary uses the UNBOUNDED curve. On this frame exact and unbounded
    # agree at D1/D7 (no device skips then returns within the cohort window
    # below offset 7), so the historical headline values still hold:
    #   D1 = devices reaching offset ≥1 = {A, B} = 2/3
    #   D7 = devices reaching offset ≥7 = {A}    = 1/3
    summ = m.retention_summary(_cohort_frame())
    assert summ["d1"] == 2 / 3
    assert summ["d7"] == 1 / 3


def test_retention_curve_unbounded_is_monotone():
    # A is active at offsets {0,1,7} — it skips offsets 2..6. Exact-day
    # retention therefore dips to 0 at D2..D6 then springs back to 1 at D7
    # (non-monotone). Unbounded keeps A alive the whole way (max offset 7),
    # so the curve is monotone non-increasing and never bumps back up.
    df = _cohort_frame()
    exact = m.retention_curve(df, max_day=7, mode="exact")
    unb = m.retention_curve(df, max_day=7, mode="unbounded")

    ex = exact.set_index("day_offset")["retained"]
    assert ex.loc[1] == 2 and ex.loc[2] == 0 and ex.loc[7] == 1  # the bump

    fr = unb["retained_frac"].tolist()
    assert fr == sorted(fr, reverse=True)          # monotone non-increasing
    un = unb.set_index("day_offset")["retained"]
    assert un.loc[0] == 3                          # D0 must be 100%
    assert un.loc[1] == 2                           # A, B reach ≥1
    assert un.loc[3] == 1 and un.loc[6] == 1        # only A survives the gap
    assert un.loc[7] == 1


def test_retention_curve_d0_is_full_population():
    for mode in ("unbounded", "exact"):
        curve = m.retention_curve(_cohort_frame(), max_day=7, mode=mode)
        d0 = curve[curve["day_offset"] == 0].iloc[0]
        assert d0["retained_frac"] == 1.0
        assert int(d0["retained"]) == int(d0["cohort_devices"]) == 3


def test_retention_curve_rejects_bad_mode():
    import pytest
    with pytest.raises(ValueError):
        m.retention_curve(_cohort_frame(), max_day=7, mode="rolling-7")


def test_settled_cohort_size_excludes_unsettled():
    # A/B/C install 10d ago (settled at max_day=7); D installs today
    # (unsettled). So n=3.
    assert m.settled_cohort_size(_cohort_frame(), max_day=7) == 3
    assert m.settled_cohort_size(_empty(), max_day=7) == 0


def test_cohort_censors_future_offsets():
    # Cohort installed 2 days ago: offsets 3..7 are in the future → omitted.
    df = _frame([
        _row(id_=1, device_id="X", days_ago=2),
        _row(id_=2, device_id="X", days_ago=1),
    ])
    cr = m.cohort_retention(df, max_day=7)
    offsets = set(cr["day_offset"])
    assert offsets == {0, 1, 2}


def test_retention_matrix_shape_and_blank_cells():
    mat = m.retention_matrix(_cohort_frame(), max_day=7)
    assert list(mat.columns) == list(range(8))
    # Today's cohort has only offset 0 observed; the rest must be NaN.
    today = TODAY
    assert mat.loc[today, 0] == 1.0
    assert pd.isna(mat.loc[today, 1])


def test_new_players_today():
    assert m.new_players_today(_cohort_frame()) == 1


def test_new_vs_returning_split():
    nvr = m.new_vs_returning_by_day(_cohort_frame(), days=30).set_index("date")
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
    s = m.sessions_per_active_day(df, days=7)
    assert sorted(s.tolist()) == [1, 2]


def test_retention_on_empty():
    assert m.retention_curve(_empty()).empty
    assert m.retention_matrix(_empty()).empty
    assert m.cohort_retention(_empty()).empty
    assert m.retention_summary(_empty()) == {"d1": 0.0, "d7": 0.0}
    assert m.new_players_today(_empty()) == 0
