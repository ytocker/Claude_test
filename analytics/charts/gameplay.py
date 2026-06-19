"""
Gameplay & balance Plotly builders.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from constants import POWERUP_LABELS
from theme import CORAL, GOLD, MUTED, SKY, style


def score_hist(scores: pd.Series) -> go.Figure:
    fig = go.Figure()
    if scores.empty:
        return style(fig, "Score distribution (7d)")
    fig.add_histogram(x=scores, nbinsx=40, marker_color=SKY,
                      hovertemplate="%{x}: %{y} runs<extra></extra>")
    fig.update_layout(yaxis_type="log", yaxis_title="Runs (log)")
    for v, lab, col in ((float(scores.median()), "median", GOLD),
                        (float(scores.quantile(0.9)), "p90", CORAL)):
        fig.add_vline(x=v, line_dash="dash", line_color=col,
                      annotation_text=f"{lab}={int(v)}", annotation_position="top")
    return style(fig, "Score distribution (7d)")


def duration_hist(durations: pd.Series) -> go.Figure:
    """Survival-time histogram. The spike near zero is the rage-quit /
    immediate-death population — worth watching for difficulty spikes."""
    fig = go.Figure()
    if durations.empty:
        return style(fig, "Survival time (7d)")
    fig.add_histogram(x=durations, nbinsx=40, marker_color=SKY,
                      hovertemplate="%{x}s: %{y} runs<extra></extra>")
    fig.update_layout(yaxis_type="log", yaxis_title="Runs (log)", xaxis_title="Seconds alive")
    median = float(durations.median())
    fig.add_vline(x=median, line_dash="dash", line_color=GOLD,
                  annotation_text=f"median={median:.0f}s", annotation_position="top")
    return style(fig, "Survival time (7d)")


def score_quantiles(q_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if q_df.empty:
        return style(fig, "Score percentiles per day")
    for col, color, name in (("median", SKY, "Median"),
                             ("p90", GOLD, "p90"),
                             ("max", CORAL, "Max")):
        fig.add_scatter(x=q_df["date"], y=q_df[col], mode="lines+markers",
                        name=name, line=dict(color=color, width=2))
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
    return style(fig, "Score percentiles per day")


def skill_over_time(skill_df: pd.DataFrame) -> go.Figure:
    """Median pillars/second + near-miss rate per day on twin axes. Rising
    pillars/sec = players getting better (or the game easing); a climbing
    near-miss rate = play getting riskier. (Resurrected from dead code.)"""
    fig = go.Figure()
    if skill_df.empty:
        return style(fig, "Skill over time")
    fig.add_scatter(x=skill_df["date"], y=skill_df["pillars_per_s"],
                    mode="lines+markers", name="Pillars/sec (median)",
                    line=dict(color=SKY, width=2),
                    hovertemplate="%{y:.2f} pillars/s<extra></extra>")
    fig.add_scatter(x=skill_df["date"], y=skill_df["near_miss_rate"],
                    mode="lines+markers", name="Near-miss rate", yaxis="y2",
                    line=dict(color=GOLD, width=2),
                    hovertemplate="%{y:.2f} near-miss/pillar<extra></extra>")
    fig.update_layout(
        yaxis=dict(title="Pillars/sec"),
        yaxis2=dict(title="Near-miss rate", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    return style(fig, "Skill over time")


def powerup_mix(totals: pd.DataFrame) -> go.Figure:
    """Horizontal bar of pickup counts, most-picked at top."""
    fig = go.Figure()
    if totals.empty:
        return style(fig, "Power-up pickups (7d)")
    ordered = totals.sort_values("count", ascending=True)
    labels = [POWERUP_LABELS.get(n, n).title() for n in ordered["name"]]
    fig.add_bar(x=ordered["count"], y=labels, orientation="h", marker_color=SKY,
                hovertemplate="%{y}: %{x} pickups<extra></extra>")
    fig.update_layout(xaxis_title="Pickups")
    return style(fig, "Power-up pickups (7d)")


def powerup_efficacy(eff_df: pd.DataFrame, metric: str = "score") -> go.Figure:
    """Diverging bar of per-power-up score lift (runs that picked it vs
    runs that didn't). Gold = over-performing, coral = under. The marquee
    balance read."""
    fig = go.Figure()
    title = "Power-up efficacy — score lift"
    sub = "Median score with vs without · correlational, not causal"
    if eff_df.empty:
        return style(fig, title, subtitle=sub)
    col = f"{metric}_lift_pct"
    ordered = eff_df.sort_values(col, ascending=True)
    labels = [POWERUP_LABELS.get(n, n).title() for n in ordered["powerup"]]
    colors = [GOLD if v >= 0 else CORAL for v in ordered[col]]
    fig.add_bar(
        x=ordered[col], y=labels, orientation="h", marker_color=colors,
        text=[f"{v:+.0f}%" for v in ordered[col]], textposition="outside",
        customdata=ordered[["n_with", "n_without"]].values,
        hovertemplate="%{y}: %{x:+.0f}% (n=%{customdata[0]} with, "
                      "%{customdata[1]} without)<extra></extra>",
    )
    fig.add_vline(x=0, line_color=MUTED, line_width=1)
    # Outside data labels need horizontal headroom or they clip at the
    # panel edge; pad the range to the largest-magnitude bar.
    span = float(ordered[col].abs().max() or 1)
    fig.update_layout(xaxis_title="Score lift vs runs without it (%)",
                      xaxis_range=[-span * 1.3, span * 1.3])
    fig.update_traces(cliponaxis=False)
    return style(fig, title, subtitle=sub)


def coin_economy(econ_df: pd.DataFrame) -> go.Figure:
    """Coins-per-pillar per day — economy density over time."""
    fig = go.Figure()
    if econ_df.empty:
        return style(fig, "Coin economy")
    fig.add_scatter(x=econ_df["date"], y=econ_df["coins_per_pillar"],
                    mode="lines+markers", line=dict(color=GOLD, width=2),
                    hovertemplate="%{y:.2f} coins/pillar<extra></extra>")
    fig.update_layout(yaxis_title="Coins per pillar")
    return style(fig, "Coin economy", subtitle="Coins collected per pillar passed")


def powerups_per_run(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if df.empty:
        return style(fig, "Power-ups per run (30d)")
    fig.add_scatter(x=df["date"], y=df["per_run"], mode="lines+markers",
                    line=dict(color=GOLD, width=2),
                    hovertemplate="%{y:.2f} / run<extra></extra>")
    return style(fig, "Power-ups per run (30d)")
