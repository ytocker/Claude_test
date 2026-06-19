"""
Player & retention metrics.

The retention story the old dashboard never told: cohort curves, a
retention triangle, and a new-vs-returning split — plus the engagement
segments and roster it already had. Pure pandas, stateless.

Retention definitions (held constant so tests have known answers):
  • install day  = a device's FIRST played_at UTC date *within the
    fetched frame*. The app feeds a wide (~120d) frame here so the
    install day is real for cohorts at least `max_day` days old.
  • Dn retained  = a cohort device that played again on (install + n).
  • censoring    = a (cohort, offset) is only counted once enough wall
    time has passed (install + offset ≤ today); younger cells are
    omitted rather than counted as 0, so a fresh cohort doesn't drag
    the curve down.

Windowed-telemetry caveat: a device whose true first play predates the
frame looks "new" the day it re-enters. Exact fix needs a server-side
first_seen; out of scope. Surfaced in chart subtitles.
"""
from __future__ import annotations

import pandas as pd

from metrics.common import day_floor_cutoff, in_window, window_cutoff


# ── Shared internals ─────────────────────────────────────────────────────────


def _first_seen(df: pd.DataFrame) -> pd.Series:
    """device_id -> first observed UTC day (floored)."""
    return df.groupby("device_id")["played_at"].min().dt.floor("D")


def _active_device_days(df: pd.DataFrame) -> pd.DataFrame:
    """Distinct (device_id, day) pairs — one row per day a device was active."""
    sub = df[["device_id"]].copy()
    sub["day"] = df["played_at"].dt.floor("D")
    return sub.drop_duplicates()


# ── Headline scalars ─────────────────────────────────────────────────────────


def returning_rate_7d(df: pd.DataFrame) -> float:
    """Fraction of last-7d players with plays on >=2 distinct UTC days.
    Returns 0.0 if there are no players in the window so the metric
    card shows 0% rather than NaN."""
    if df.empty:
        return 0.0
    recent = df[df["played_at"] >= window_cutoff(7)]
    if recent.empty:
        return 0.0
    days_per_player = (
        recent.assign(d=recent["played_at"].dt.date)
              .groupby("device_id")["d"].nunique()
    )
    total = len(days_per_player)
    repeated = int((days_per_player >= 2).sum())
    return repeated / total if total else 0.0


def one_shot_count(df: pd.DataFrame, days: int = 7) -> int:
    """Number of devices in the window with exactly one play. The "bounce"
    signal for a casual game — high values mean the first-run experience
    isn't converting curious clicks into a second attempt. Hyper-casual
    benchmarks expect 60–75% of players to be one-shots."""
    if df.empty:
        return 0
    recent = in_window(df, days)
    if recent.empty:
        return 0
    plays_per_device = recent.groupby("device_id").size()
    return int((plays_per_device == 1).sum())


def active_players(df: pd.DataFrame, days: int = 7) -> int:
    """Distinct devices active in the window — the denominator for the
    one-shot/bounce percentage card."""
    if df.empty:
        return 0
    recent = in_window(df, days)
    return int(recent["device_id"].nunique())


def new_players_today(df: pd.DataFrame) -> int:
    """Devices whose first observed play (within the frame) is today.
    Subject to the windowed-telemetry caveat above."""
    if df.empty:
        return 0
    today = pd.Timestamp.now(tz="UTC").normalize()
    return int((_first_seen(df) == today).sum())


def retention_summary(df: pd.DataFrame) -> dict[str, float]:
    """{'d1': .., 'd7': ..} pooled across eligible cohorts — the two
    headline retention KPIs. 0.0 when no cohort is old enough."""
    curve = retention_curve(df, max_day=7)
    out = {"d1": 0.0, "d7": 0.0}
    for off, key in ((1, "d1"), (7, "d7")):
        row = curve[curve["day_offset"] == off]
        if not row.empty and int(row["cohort_devices"].iloc[0]) > 0:
            out[key] = float(row["retained_frac"].iloc[0])
    return out


# ── Cohort retention ─────────────────────────────────────────────────────────


def cohort_retention(df: pd.DataFrame, max_day: int = 7) -> pd.DataFrame:
    """Per-cohort retention, long form. One row per (cohort_date,
    day_offset) with the cohort size, retained-device count, and fraction.
    Censored cells (install + offset in the future) are omitted."""
    cols = ["cohort_date", "day_offset", "cohort_size", "retained", "retained_frac"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    first = _first_seen(df)
    active = _active_device_days(df).merge(
        first.rename("cohort_date"), left_on="device_id", right_index=True,
    )
    active["day_offset"] = (active["day"] - active["cohort_date"]).dt.days
    sizes = first.value_counts()  # cohort_date -> size
    today = pd.Timestamp.now(tz="UTC").normalize()
    rows = []
    for cohort_date, size in sizes.items():
        for off in range(0, max_day + 1):
            if cohort_date + pd.Timedelta(days=off) > today:
                continue  # censored — not enough wall time yet
            retained = int(active[
                (active["cohort_date"] == cohort_date)
                & (active["day_offset"] == off)
            ]["device_id"].nunique())
            rows.append({
                "cohort_date": cohort_date,
                "day_offset": off,
                "cohort_size": int(size),
                "retained": retained,
                "retained_frac": retained / int(size),
            })
    return pd.DataFrame(rows, columns=cols)


def retention_curve(df: pd.DataFrame, max_day: int = 7) -> pd.DataFrame:
    """Single pooled D0..Dn curve over a CONSISTENT denominator: only
    cohorts old enough to be fully observed through `max_day`
    (install ≤ today − max_day) are counted, and every offset divides by
    that same device set. Pooling per-offset-eligible cohorts instead
    (different denominators per point) produces a misleading non-monotone
    curve; fixing the population is the honest read. Columns:
    [day_offset, cohort_devices, retained, retained_frac]."""
    cols = ["day_offset", "cohort_devices", "retained", "retained_frac"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    first = _first_seen(df)
    today = pd.Timestamp.now(tz="UTC").normalize()
    settled = first[first <= today - pd.Timedelta(days=max_day)]
    total = len(settled)
    if total == 0:
        return pd.DataFrame(columns=cols)
    sub = df[df["device_id"].isin(set(settled.index))]
    active = _active_device_days(sub).merge(
        settled.rename("cohort_date"), left_on="device_id", right_index=True,
    )
    active["day_offset"] = (active["day"] - active["cohort_date"]).dt.days
    rows = []
    for off in range(0, max_day + 1):
        retained = int(active[active["day_offset"] == off]["device_id"].nunique())
        rows.append({
            "day_offset": off,
            "cohort_devices": total,
            "retained": retained,
            "retained_frac": retained / total,
        })
    return pd.DataFrame(rows, columns=cols)


def retention_matrix(df: pd.DataFrame, max_day: int = 7) -> pd.DataFrame:
    """Wide cohort × day-offset matrix of retained_frac — the classic
    retention triangle. Rows = cohort_date, cols = 0..max_day. Censored
    cells are NaN so the heatmap leaves them blank."""
    cr = cohort_retention(df, max_day=max_day)
    if cr.empty:
        return pd.DataFrame()
    mat = cr.pivot(index="cohort_date", columns="day_offset", values="retained_frac")
    return mat.reindex(columns=range(0, max_day + 1))


def new_vs_returning_by_day(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Per UTC day: count of NEW devices (first-ever-seen that day) vs
    RETURNING (seen before). Continuous day index, zero-filled. Columns:
    [date, new, returning]."""
    end = pd.Timestamp.now(tz="UTC").normalize()
    full_idx = pd.date_range(end=end, periods=days, freq="D", tz="UTC")
    if df.empty:
        return pd.DataFrame({"date": full_idx, "new": 0, "returning": 0})
    first = _first_seen(df)
    dd = _active_device_days(df).merge(
        first.rename("first_day"), left_on="device_id", right_index=True,
    )
    dd["is_new"] = dd["day"] == dd["first_day"]
    dd = dd[dd["day"] >= day_floor_cutoff(days)]
    g = dd.groupby("day")["is_new"].agg(new="sum", total="count")
    g["returning"] = g["total"] - g["new"]
    g = g.reindex(full_idx, fill_value=0)
    out = g.reset_index().rename(columns={"index": "date"})
    return out[["date", "new", "returning"]].astype({"new": int, "returning": int})


def sessions_per_active_day(df: pd.DataFrame, days: int = 30) -> pd.Series:
    """Plays-per-active-day for every (device, day) in the window — the
    raw material for a session-depth histogram. A long right tail means a
    few players binge; a wall at 1 means most sessions are single runs."""
    if df.empty:
        return pd.Series([], dtype=int, name="plays")
    sub = in_window(df, days).copy()
    if sub.empty:
        return pd.Series([], dtype=int, name="plays")
    sub["day"] = sub["played_at"].dt.floor("D")
    return sub.groupby(["device_id", "day"]).size().reset_index(name="plays")["plays"]


# ── Engagement segments + roster ─────────────────────────────────────────────


def engagement_segments(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Count of players in each play-count bucket: 1 / 2–5 / 6–20 / 21+.
    Returned as a long frame with stable ordering so the bar chart
    renders the segments top-to-bottom in increasing engagement."""
    buckets = [
        ("1 play",     1, 1),
        ("2–5 plays",  2, 5),
        ("6–20 plays", 6, 20),
        ("21+ plays",  21, 10**9),
    ]
    empty = pd.DataFrame({
        "segment": [b[0] for b in buckets],
        "players": [0] * len(buckets),
    })
    if df.empty:
        return empty
    recent = in_window(df, days)
    if recent.empty:
        return empty
    plays_per_device = recent.groupby("device_id").size()
    rows = []
    for label, lo, hi in buckets:
        rows.append({
            "segment": label,
            "players": int(((plays_per_device >= lo) & (plays_per_device <= hi)).sum()),
        })
    return pd.DataFrame(rows)


def roster(df: pd.DataFrame, days: int = 30, top_n: int = 50) -> pd.DataFrame:
    """One row per active player in the last `days` days. Sorted by
    plays desc, capped at top_n. Used by the bottom table in app.py;
    nickname + color are joined on at render time so this stays
    library-free."""
    empty_cols = [
        "device_id", "plays", "days_active",
        "best_score", "avg_duration_s", "last_seen",
    ]
    if df.empty:
        return pd.DataFrame(columns=empty_cols)
    sub = in_window(df, days).copy()
    if sub.empty:
        return pd.DataFrame(columns=empty_cols)
    sub["day"] = sub["played_at"].dt.date
    grouped = sub.groupby("device_id").agg(
        plays=("id", "count"),
        days_active=("day", "nunique"),
        best_score=("score", "max"),
        avg_duration_s=("duration_s", "mean"),
        last_seen=("played_at", "max"),
    ).reset_index()
    # Single-play devices are kept — they're the bounce signal for the
    # game's first-run experience and previously got hidden, which made
    # the dashboard pretend they didn't exist. Sort by plays desc, then
    # by last_seen desc so the most recent one-shots still appear near
    # the top when there's a tie.
    return (
        grouped.sort_values(["plays", "last_seen"], ascending=[False, False])
               .head(top_n)
               .reset_index(drop=True)
    )
