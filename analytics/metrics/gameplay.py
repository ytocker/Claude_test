"""
Gameplay & balance metrics — difficulty, skill, power-up balance, economy.

Answers the questions the old dashboard couldn't: how hard is the game
right now (score & survival distributions), is skill drifting over time,
and — the marquee addition — does each power-up actually help (efficacy),
not just how often it's picked. Pure pandas, stateless.
"""
from __future__ import annotations

import pandas as pd

from constants import POWERUP_KEYS_ACTIVE
from metrics.common import day_floor_cutoff, in_window


# ── Score & survival summaries ───────────────────────────────────────────────


def score_distribution(df: pd.DataFrame, days: int = 7) -> pd.Series:
    """Scores from the last `days` days for a histogram."""
    if df.empty:
        return pd.Series([], dtype=int)
    return in_window(df, days)["score"].astype(int)


def duration_distribution(df: pd.DataFrame, days: int = 7) -> pd.Series:
    """Survival times (seconds) from the last `days` days for a histogram.
    A spike near zero is the immediate-flame-out / rage-quit signal."""
    if df.empty:
        return pd.Series([], dtype=int)
    return in_window(df, days)["duration_s"].astype(int)


def _summary(series: pd.Series) -> dict[str, float]:
    if series.empty:
        return {"median": 0.0, "p90": 0.0, "max": 0.0}
    return {
        "median": float(series.median()),
        "p90": float(series.quantile(0.9)),
        "max": float(series.max()),
    }


def score_summary(df: pd.DataFrame, days: int = 7) -> dict[str, float]:
    """median / p90 / max score over the window for the KPI cards."""
    return _summary(score_distribution(df, days))


def duration_summary(df: pd.DataFrame, days: int = 7) -> dict[str, float]:
    """median / p90 / max survival seconds over the window."""
    return _summary(duration_distribution(df, days))


def coins_per_run(df: pd.DataFrame, days: int = 7) -> float:
    """Mean coins collected per run — the economy's top-line throughput."""
    if df.empty:
        return 0.0
    recent = in_window(df, days)
    if recent.empty:
        return 0.0
    return float(recent["coins"].mean())


def score_quantiles_by_day(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Median / p90 / max score per UTC day. Empty days are dropped (the
    chart will simply not draw a point there)."""
    if df.empty:
        return pd.DataFrame(columns=["date", "median", "p90", "max"])
    sub = df.copy()
    sub["date"] = sub["played_at"].dt.floor("D")
    sub = sub[sub["date"] >= day_floor_cutoff(days)]
    if sub.empty:
        return pd.DataFrame(columns=["date", "median", "p90", "max"])
    out = sub.groupby("date")["score"].agg(
        median="median",
        p90=lambda s: float(s.quantile(0.9)),
        max="max",
    ).reset_index()
    return out


def skill_proxy_by_day(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Median pillars-per-second + near-miss rate by day. Filters out
    trivially-short runs (<2s) so a wave of immediate flame-outs doesn't
    dominate the skill curve. (Previously computed but never rendered —
    now wired into the gameplay tab.)"""
    if df.empty:
        return pd.DataFrame(columns=["date", "pillars_per_s", "near_miss_rate"])
    sub = df[df["duration_s"] >= 2].copy()
    if sub.empty:
        return pd.DataFrame(columns=["date", "pillars_per_s", "near_miss_rate"])
    sub["date"] = sub["played_at"].dt.floor("D")
    sub["pps"] = sub["pillars"] / sub["duration_s"].clip(lower=1)
    sub = sub[sub["date"] >= day_floor_cutoff(days)]
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


def coin_economy_by_day(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Coins-per-pillar per UTC day — economy density, robust to how long
    runs last. A drift up/down flags a coin-spawn or rush-rate regression.
    Columns: [date, coins, pillars, coins_per_pillar]."""
    cols = ["date", "coins", "pillars", "coins_per_pillar"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    sub = df.copy()
    sub["date"] = sub["played_at"].dt.floor("D")
    sub = sub[sub["date"] >= day_floor_cutoff(days)]
    if sub.empty:
        return pd.DataFrame(columns=cols)
    g = sub.groupby("date").agg(coins=("coins", "sum"), pillars=("pillars", "sum")).reset_index()
    g["coins_per_pillar"] = g["coins"] / g["pillars"].where(g["pillars"] > 0, 1)
    return g[cols]


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
    sub = in_window(df, days)
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
    sub["total_pu"] = sub["powerups"].apply(_total_powerups)
    sub["date"] = sub["played_at"].dt.floor("D")
    sub = sub[sub["date"] >= day_floor_cutoff(days)]
    if sub.empty:
        return pd.DataFrame(columns=["date", "per_run"])
    out = sub.groupby("date")["total_pu"].mean().reset_index().rename(
        columns={"total_pu": "per_run"}
    )
    return out


def powerup_efficacy(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """For each active power-up, compare runs that picked it ≥1× against
    runs that didn't, on median score and median survival. `lift` is the
    percentage difference (with vs without).

    Correlational, not causal — a power-up may be picked *because* a run
    is already going well (longer runs see more spawns). The chart says
    so. Still the fastest read on whether a power-up is pulling its
    weight or is dead weight / overpowered.

    Columns: [powerup, n_with, n_without, score_with, score_without,
    score_lift_pct, dur_with, dur_without, dur_lift_pct]. Power-ups never
    picked in the window are omitted (no signal)."""
    cols = ["powerup", "n_with", "n_without",
            "score_with", "score_without", "score_lift_pct",
            "dur_with", "dur_without", "dur_lift_pct"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    sub = in_window(df, days).copy()
    if sub.empty:
        return pd.DataFrame(columns=cols)
    rows = []
    for k in POWERUP_KEYS_ACTIVE:
        picked = sub["powerups"].apply(
            lambda d, key=k: isinstance(d, dict) and int(d.get(key, 0) or 0) > 0
        )
        n_with = int(picked.sum())
        n_without = int((~picked).sum())
        if n_with == 0:
            continue  # never picked in window → nothing to compare
        with_grp = sub[picked]
        without_grp = sub[~picked]
        score_with = float(with_grp["score"].median())
        dur_with = float(with_grp["duration_s"].median())
        score_without = float(without_grp["score"].median()) if n_without else float("nan")
        dur_without = float(without_grp["duration_s"].median()) if n_without else float("nan")
        rows.append({
            "powerup": k,
            "n_with": n_with,
            "n_without": n_without,
            "score_with": score_with,
            "score_without": score_without,
            "score_lift_pct": _lift(score_with, score_without),
            "dur_with": dur_with,
            "dur_without": dur_without,
            "dur_lift_pct": _lift(dur_with, dur_without),
        })
    return pd.DataFrame(rows, columns=cols)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _total_powerups(d) -> int:
    if not isinstance(d, dict):
        return 0
    return sum(int(d.get(k, 0) or 0) for k in POWERUP_KEYS_ACTIVE)


def _lift(with_val: float, without_val: float) -> float:
    """Percentage lift of `with` over `without`, guarding the zero/NaN
    baseline (returns 0.0 — undefined lift reads as 'no signal')."""
    if without_val is None or pd.isna(without_val) or without_val == 0:
        return 0.0
    return (with_val - without_val) / without_val * 100.0
