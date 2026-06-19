"""
Live-ops / overview metrics — the health-and-monitoring numbers.

DAU + plays with day-over-day deltas, data freshness, and the
cheat/rejection signal mined from the submit_error column. Pure pandas,
stateless, so tests drive each function with a fixture frame.

All inputs are assumed already plausibility-filtered (filters.plausible)
with tz-aware UTC played_at.
"""
from __future__ import annotations

import pandas as pd

from filters import today_utc_start
from metrics.common import day_floor_cutoff, in_window


# ── Headline scalars ─────────────────────────────────────────────────────────


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


def plays_window_delta(df: pd.DataFrame, days: int = 7) -> tuple[int, int]:
    """(plays in last `days`, plays in the `days` before that). The second
    value is the comparison base for a period-over-period delta on the
    metric card — the old dashboard showed the current count with no
    trend to read it against."""
    if df.empty:
        return 0, 0
    now = pd.Timestamp.now(tz="UTC")
    cur_start = now - pd.Timedelta(days=days)
    prev_start = now - pd.Timedelta(days=2 * days)
    current = int((df["played_at"] >= cur_start).sum())
    prior = int(((df["played_at"] >= prev_start) & (df["played_at"] < cur_start)).sum())
    return current, prior


def minutes_since_last_play(df: pd.DataFrame) -> float | None:
    """Data-freshness signal: minutes since the most recent play. None on
    an empty frame so the card can render '—' rather than a bogus number."""
    if df.empty:
        return None
    last = df["played_at"].max()
    delta = pd.Timestamp.now(tz="UTC") - last
    return max(0.0, delta.total_seconds() / 60.0)


def rejection_rate(df: pd.DataFrame, days: int = 7) -> float:
    """Share of runs in the window whose top-10 submit was rejected
    (submit_error not null). A spike is the cheat / client-bug signal —
    the column existed in telemetry but was never surfaced before.
    Returns 0.0 on an empty window or when the column is absent."""
    if df.empty or "submit_error" not in df.columns:
        return 0.0
    recent = in_window(df, days)
    if recent.empty:
        return 0.0
    return float(recent["submit_error"].notna().mean())


def rejection_count(df: pd.DataFrame, days: int = 7) -> tuple[int, int]:
    """(rejected runs, total runs) in the window — the explicit
    numerator/denominator behind rejection_rate, so the KPI card can show
    '2 / 64 runs' and the reader can size the noise. 0/0 on empty."""
    if df.empty or "submit_error" not in df.columns:
        return 0, 0
    recent = in_window(df, days)
    total = int(len(recent))
    rejected = int(recent["submit_error"].notna().sum())
    return rejected, total


def rejection_reasons(df: pd.DataFrame, days: int = 7) -> pd.DataFrame:
    """Count of each distinct submit_error reason in the window, the gate
    name normalised to the text before the first ':'. Long frame
    [reason, count] sorted desc. Empty frame when nothing was rejected."""
    cols = ["reason", "count"]
    if df.empty or "submit_error" not in df.columns:
        return pd.DataFrame(columns=cols)
    recent = in_window(df, days)
    errs = recent.loc[recent["submit_error"].notna(), "submit_error"]
    if errs.empty:
        return pd.DataFrame(columns=cols)
    gate = errs.astype(str).str.split(":").str[0].str.strip()
    out = (gate.value_counts()
               .rename_axis("reason")
               .reset_index(name="count"))
    return out


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


def daily_plays_with_band(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Daily plays plus a *trailing* rolling mean ± 2·std anomaly band.

    Two correctness choices over the naive version:

    * The band is trailing (`closed='left'`): each day is judged against
      the 7 days *before* it, never against itself. A self-inclusive
      window pulls the mean toward an outlier and shrinks σ, which masks
      the very spike we want to flag.
    * It needs a full 7-day warm-up (`min_periods=7`). A band fitted on
      2–3 points has a meaningless σ — it would either collapse to the
      point (never an outlier) or fire on noise. Warm-up days carry NaN
      band columns and a `warmup=True` flag so the chart can grey them
      out rather than drawing a fake band.

    Columns: [date, plays, mean, lo, hi, warmup, outlier]."""
    base = by_day(df, days=days)
    roll = base["plays"].rolling(7, min_periods=7, closed="left")
    mean = roll.mean()
    std = roll.std()
    base["mean"] = mean
    base["lo"] = (mean - 2 * std).clip(lower=0)
    base["hi"] = mean + 2 * std
    base["warmup"] = mean.isna()
    base["outlier"] = (
        ~base["warmup"]
        & ((base["plays"] > base["hi"]) | (base["plays"] < base["lo"]))
    )
    return base[["date", "plays", "mean", "lo", "hi", "warmup", "outlier"]]


def health_status(df: pd.DataFrame) -> dict:
    """Single glance-and-go verdict for the top of the tab — alive,
    growing, clean — collapsed to one of OK / WATCH / ALERT plus the
    human-readable reasons that drove it.

    The three checks mirror the tab's purpose, each kept honest about
    small N:

    * alive   — minutes since the last play vs the data's own recent
                cadence (median gap over the last 7d), not a hard wall:
                a quiet indie game with naturally long gaps shouldn't
                read as 'down'. ALERT only when silence runs to 3× the
                typical gap (min 6h floor so a single fast burst can't
                set a 2-minute expectation).
    * growing — 7d plays vs the prior 7d; only a *drop* is a concern,
                and only flagged WATCH (volume dips aren't an outage).
    * clean   — rejection rate over 7d, but gated on an absolute count
                so 1 rejected run in a tiny window can't trip an ALERT.

    Returns {level, reasons: [str], alive, growing, clean} where the
    three sub-dicts each carry their own level so the UI can colour
    per-check. Empty frame → ALERT 'no data'."""
    if df.empty:
        return {
            "level": "ALERT",
            "reasons": ["No plays in the loaded window"],
            "alive": {"level": "ALERT", "detail": "no data"},
            "growing": {"level": "ALERT", "detail": "no data"},
            "clean": {"level": "ALERT", "detail": "no data"},
        }

    # ── alive: freshness relative to the game's own cadence ──
    fresh_min = minutes_since_last_play(df) or 0.0
    recent = in_window(df, 7).sort_values("played_at")
    gaps = recent["played_at"].diff().dropna()
    typical_min = (
        float(gaps.median().total_seconds() / 60.0) if len(gaps) >= 3 else 360.0
    )
    expect_min = max(typical_min, 360.0)  # 6h floor — see docstring
    if fresh_min > 3 * expect_min:
        alive = {"level": "ALERT",
                 "detail": f"silent {_fmt_dur(fresh_min)} (typical gap "
                           f"{_fmt_dur(expect_min)})"}
    elif fresh_min > 1.5 * expect_min:
        alive = {"level": "WATCH",
                 "detail": f"last play {_fmt_dur(fresh_min)} ago"}
    else:
        alive = {"level": "OK", "detail": f"last play {_fmt_dur(fresh_min)} ago"}

    # ── growing: 7d vs prior 7d, drop-only ──
    cur, prev = plays_window_delta(df, days=7)
    if prev == 0:
        growing = {"level": "OK", "detail": f"{cur} plays / 7d (no prior week)"}
    else:
        pct = (cur - prev) / prev
        if pct <= -0.30:
            growing = {"level": "WATCH",
                       "detail": f"plays {pct*100:+.0f}% vs prior 7d "
                                 f"({cur} vs {prev})"}
        else:
            growing = {"level": "OK",
                       "detail": f"plays {pct*100:+.0f}% vs prior 7d "
                                 f"({cur} vs {prev})"}

    # ── clean: rejection rate, gated on absolute count ──
    rej = rejection_rate(df, days=7)
    rej_n = int(in_window(df, 7)["submit_error"].notna().sum()) \
        if "submit_error" in df.columns else 0
    if rej_n >= 3 and rej > 0.10:
        clean = {"level": "ALERT",
                 "detail": f"{rej*100:.0f}% rejected ({rej_n} runs / 7d)"}
    elif rej_n >= 3 and rej > 0.05:
        clean = {"level": "WATCH",
                 "detail": f"{rej*100:.0f}% rejected ({rej_n} runs / 7d)"}
    else:
        clean = {"level": "OK",
                 "detail": f"{rej*100:.1f}% rejected ({rej_n} runs / 7d)"}

    rank = {"OK": 0, "WATCH": 1, "ALERT": 2}
    checks = {"alive": alive, "growing": growing, "clean": clean}
    level = max(checks.values(), key=lambda c: rank[c["level"]])["level"]
    reasons = [c["detail"] for c in checks.values() if c["level"] != "OK"]
    if not reasons:
        reasons = ["Alive, growing, and clean"]
    return {"level": level, "reasons": reasons, **checks}


def _fmt_dur(minutes: float) -> str:
    """Compact human duration for status detail lines."""
    if minutes < 90:
        return f"{minutes:.0f} min"
    hours = minutes / 60.0
    if hours < 36:
        return f"{hours:.1f} h"
    return f"{hours / 24:.1f} d"


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
