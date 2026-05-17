"""
Pure pandas aggregations — one function per KPI.

Kept stateless and side-effect-free so tests can drive each function
with a fixture frame and compare against hand-computed expected values.
Streamlit/Plotly imports live in charts.py and app.py; this module is
plot-library-agnostic.

All inputs are assumed to be already plausibility-filtered (see
filters.plausible). Date columns are assumed tz-aware UTC.
"""
from __future__ import annotations

import pandas as pd

from constants import POWERUP_KEYS_ACTIVE
from filters import today_utc_start


# ── Headline KPI scalars ─────────────────────────────────────────────────────


def dau_today(df: pd.DataFrame) -> int:
    """Distinct device_ids that played since UTC midnight."""
    if df.empty:
        return 0
    return int(df[df["played_at"] >= today_utc_start()]["device_id"].nunique())


def plays_today(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    return int((df["played_at"] >= today_utc_start()).sum())


def dau_yesterday(df: pd.DataFrame) -> int:
    """For the delta indicator on the 'DAU today' metric card."""
    if df.empty:
        return 0
    start = today_utc_start()
    yest = start - pd.Timedelta(days=1)
    mask = (df["played_at"] >= yest) & (df["played_at"] < start)
    return int(df[mask]["device_id"].nunique())


def plays_yesterday(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    start = today_utc_start()
    yest = start - pd.Timedelta(days=1)
    mask = (df["played_at"] >= yest) & (df["played_at"] < start)
    return int(mask.sum())


def returning_rate_7d(df: pd.DataFrame) -> float:
    """Fraction of last-7d players with plays on >=2 distinct UTC days.
    Returns 0.0 if there are no players in the window so the metric
    card shows 0% rather than NaN."""
    if df.empty:
        return 0.0
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=7)
    recent = df[df["played_at"] >= cutoff]
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
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)
    recent = df[df["played_at"] >= cutoff]
    if recent.empty:
        return 0
    plays_per_device = recent.groupby("device_id").size()
    return int((plays_per_device == 1).sum())


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
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)
    recent = df[df["played_at"] >= cutoff]
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


# ── Time series ──────────────────────────────────────────────────────────────


def by_day(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """One row per UTC day with plays + unique players + avg duration.
    Fills missing days with zeros so the chart x-axis is continuous."""
    end = pd.Timestamp.now(tz="UTC").normalize()
    full_idx = pd.date_range(end=end, periods=days, freq="D", tz="UTC")
    if df.empty:
        return pd.DataFrame({
            "date": full_idx, "plays": 0, "uniques": 0, "avg_duration_s": 0.0,
        })
    sub = df.copy()
    sub["date"] = sub["played_at"].dt.floor("D")
    grouped = sub.groupby("date").agg(
        plays=("id", "count"),
        uniques=("device_id", "nunique"),
        avg_duration_s=("duration_s", "mean"),
    )
    grouped = grouped.reindex(full_idx, fill_value=0)
    grouped["avg_duration_s"] = grouped["avg_duration_s"].astype(float).fillna(0.0)
    return grouped.reset_index().rename(columns={"index": "date"})


def hourly_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """Weekday (0=Mon) × hour-of-day play counts, in UTC. Returns a wide
    frame: rows = weekday, columns = hour 0..23. Filled to a complete
    7×24 grid so the heatmap renders even with sparse data."""
    grid = pd.DataFrame(0, index=range(7), columns=range(24))
    if df.empty:
        return grid
    weekday = df["played_at"].dt.weekday
    hour = df["played_at"].dt.hour
    counts = pd.crosstab(weekday, hour)
    counts = counts.reindex(index=range(7), columns=range(24), fill_value=0)
    return counts


# ── Score & skill ────────────────────────────────────────────────────────────


def score_distribution(df: pd.DataFrame, days: int = 7) -> pd.Series:
    """Scores from the last `days` days for a histogram."""
    if df.empty:
        return pd.Series([], dtype=int)
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)
    return df[df["played_at"] >= cutoff]["score"].astype(int)


def score_quantiles_by_day(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Median / p90 / max score per UTC day. Empty days are dropped (the
    chart will simply not draw a point there)."""
    if df.empty:
        return pd.DataFrame(columns=["date", "median", "p90", "max"])
    sub = df.copy()
    sub["date"] = sub["played_at"].dt.floor("D")
    cutoff = pd.Timestamp.now(tz="UTC").normalize() - pd.Timedelta(days=days)
    sub = sub[sub["date"] >= cutoff]
    if sub.empty:
        return pd.DataFrame(columns=["date", "median", "p90", "max"])
    out = sub.groupby("date")["score"].agg(
        median="median",
        p90=lambda s: float(s.quantile(0.9)),
        max="max",
    ).reset_index()
    return out


def skill_proxy_by_day(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Median pillars-per-second by day. Filters out trivially-short
    runs (<2s) so a wave of immediate flame-outs doesn't dominate the
    skill curve."""
    if df.empty:
        return pd.DataFrame(columns=["date", "pillars_per_s", "near_miss_rate"])
    sub = df[df["duration_s"] >= 2].copy()
    if sub.empty:
        return pd.DataFrame(columns=["date", "pillars_per_s", "near_miss_rate"])
    sub["date"] = sub["played_at"].dt.floor("D")
    sub["pps"] = sub["pillars"] / sub["duration_s"].clip(lower=1)
    cutoff = pd.Timestamp.now(tz="UTC").normalize() - pd.Timedelta(days=days)
    sub = sub[sub["date"] >= cutoff]
    if sub.empty:
        return pd.DataFrame(columns=["date", "pillars_per_s", "near_miss_rate"])
    grouped = sub.groupby("date").apply(
        lambda g: pd.Series({
            "pillars_per_s": float(g["pps"].median()),
            "near_miss_rate": float(g["near_misses"].sum() / max(g["pillars"].sum(), 1)),
        }),
        include_groups=False,
    ).reset_index()
    return grouped


# ── Power-ups ────────────────────────────────────────────────────────────────


def powerup_totals(df: pd.DataFrame, days: int = 7) -> pd.DataFrame:
    """Sum each active power-up key across the last `days` days. Returns
    a long frame (name, count) ready for a horizontal bar chart.

    Reverse is excluded because it's disabled in the game and would
    contribute zero noise. Surprise is included; it counts the pickup
    of a Surprise Box, not the rerolled outcome (the rerolled outcome
    increments its own key)."""
    if df.empty:
        return pd.DataFrame({"name": list(POWERUP_KEYS_ACTIVE),
                             "count": [0] * len(POWERUP_KEYS_ACTIVE)})
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)
    sub = df[df["played_at"] >= cutoff]
    totals = {k: 0 for k in POWERUP_KEYS_ACTIVE}
    for entry in sub["powerups"]:
        if not isinstance(entry, dict):
            continue
        for k in POWERUP_KEYS_ACTIVE:
            totals[k] += int(entry.get(k, 0) or 0)
    return pd.DataFrame({"name": list(totals.keys()), "count": list(totals.values())})


def powerups_per_run_by_day(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Avg total power-ups picked per run, per day. Useful for spotting
    spawn-rate regressions."""
    if df.empty:
        return pd.DataFrame(columns=["date", "per_run"])
    sub = df.copy()
    sub["total_pu"] = sub["powerups"].apply(
        lambda d: sum(int(d.get(k, 0) or 0) for k in POWERUP_KEYS_ACTIVE)
        if isinstance(d, dict) else 0
    )
    sub["date"] = sub["played_at"].dt.floor("D")
    cutoff = pd.Timestamp.now(tz="UTC").normalize() - pd.Timedelta(days=days)
    sub = sub[sub["date"] >= cutoff]
    if sub.empty:
        return pd.DataFrame(columns=["date", "per_run"])
    out = sub.groupby("date")["total_pu"].mean().reset_index().rename(
        columns={"total_pu": "per_run"}
    )
    return out


# ── Player roster ────────────────────────────────────────────────────────────


def roster(df: pd.DataFrame, days: int = 30, top_n: int = 50) -> pd.DataFrame:
    """One row per active player in the last `days` days. Sorted by
    plays desc, capped at top_n. Used by the bottom table in app.py;
    nickname + color are joined on at render time so this stays
    library-free."""
    if df.empty:
        return pd.DataFrame(columns=[
            "device_id", "plays", "days_active",
            "best_score", "avg_duration_s", "last_seen",
        ])
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)
    sub = df[df["played_at"] >= cutoff].copy()
    if sub.empty:
        return pd.DataFrame(columns=[
            "device_id", "plays", "days_active",
            "best_score", "avg_duration_s", "last_seen",
        ])
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
