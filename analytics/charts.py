"""
Plotly figure builders — one function per chart.

Each function takes pre-aggregated data and returns a go.Figure with
consistent styling (transparent background, sky-blue accent, small
margins). Layout decisions are centralised in _style() so the dashboard
has one visual identity across every panel.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from constants import POWERUP_LABELS

SKY = "#4DA3FF"
SKY_SOFT = "rgba(77, 163, 255, 0.35)"
GOLD = "#F4C95D"
INK = "#0F1B2D"

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=40, b=10),
    font=dict(family="system-ui, sans-serif"),
    hoverlabel=dict(bgcolor="white"),
)


def _style(fig: go.Figure, title: str | None = None, height: int = 320) -> go.Figure:
    fig.update_layout(**_LAYOUT, height=height,
                      title=dict(text=title, x=0.0, xanchor="left",
                                 font=dict(size=15)) if title else None)
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(120,120,120,0.18)", zeroline=False)
    return fig


# ── Engagement ───────────────────────────────────────────────────────────────


def plays_and_uniques(by_day_df: pd.DataFrame) -> go.Figure:
    """Plays per day as bars + unique players as a line (secondary y).
    Adds a 7-day rolling mean of plays as a thinner trace so trend is
    readable through day-to-day noise."""
    fig = go.Figure()
    if by_day_df.empty:
        return _style(fig, "Plays & unique players (30d)")
    fig.add_bar(
        x=by_day_df["date"], y=by_day_df["plays"],
        name="Plays", marker_color=SKY_SOFT, hovertemplate="%{y} plays<extra></extra>",
    )
    rolling = by_day_df["plays"].rolling(7, min_periods=1).mean()
    fig.add_scatter(
        x=by_day_df["date"], y=rolling, name="Plays (7d avg)",
        mode="lines", line=dict(color=SKY, width=2),
        hovertemplate="%{y:.1f} (7d avg)<extra></extra>",
    )
    fig.add_scatter(
        x=by_day_df["date"], y=by_day_df["uniques"], name="Unique players",
        mode="lines+markers", line=dict(color=GOLD, width=2), yaxis="y2",
        hovertemplate="%{y} unique<extra></extra>",
    )
    fig.update_layout(
        yaxis=dict(title="Plays"),
        yaxis2=dict(title="Unique players", overlaying="y", side="right",
                    showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    return _style(fig, "Plays & unique players (30d)")


def avg_duration(by_day_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if by_day_df.empty:
        return _style(fig, "Avg session duration (s)")
    fig.add_scatter(
        x=by_day_df["date"], y=by_day_df["avg_duration_s"],
        mode="lines+markers", line=dict(color=SKY, width=2),
        hovertemplate="%{y:.1f}s<extra></extra>",
    )
    return _style(fig, "Avg session duration (s)")


def hourly_heatmap(grid: pd.DataFrame) -> go.Figure:
    """Weekday × hour-of-day heatmap. Rows are reordered Mon..Sun for
    reading-direction convention; hover shows the count."""
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    z = grid.values
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=[f"{h:02d}" for h in grid.columns],
        y=weekdays,
        colorscale="Blues",
        hovertemplate="%{y} %{x}:00 — %{z} plays<extra></extra>",
        colorbar=dict(title="Plays"),
    ))
    fig.update_yaxes(autorange="reversed")
    return _style(fig, "When people play (UTC, weekday × hour)")


# ── Score & skill ────────────────────────────────────────────────────────────


def score_hist(scores: pd.Series) -> go.Figure:
    fig = go.Figure()
    if scores.empty:
        return _style(fig, "Score distribution (7d)")
    fig.add_histogram(
        x=scores, nbinsx=40, marker_color=SKY,
        hovertemplate="%{x}: %{y} runs<extra></extra>",
    )
    fig.update_layout(yaxis_type="log", yaxis_title="Runs (log)")
    median = float(scores.median())
    p90 = float(scores.quantile(0.9))
    for v, lab, col in [(median, "median", GOLD), (p90, "p90", "#FF8E5C")]:
        fig.add_vline(x=v, line_dash="dash", line_color=col,
                      annotation_text=f"{lab}={int(v)}",
                      annotation_position="top")
    return _style(fig, "Score distribution (7d)")


def score_quantiles(q_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if q_df.empty:
        return _style(fig, "Score percentiles per day")
    for col, color, name in [("median", SKY, "Median"),
                              ("p90", GOLD, "p90"),
                              ("max", "#FF8E5C", "Max")]:
        fig.add_scatter(
            x=q_df["date"], y=q_df[col], mode="lines+markers",
            name=name, line=dict(color=color, width=2),
        )
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom",
                                  y=1.02, x=0))
    return _style(fig, "Score percentiles per day")


# ── Power-ups ────────────────────────────────────────────────────────────────


def powerup_mix(totals: pd.DataFrame) -> go.Figure:
    """Horizontal bar of pickup counts. Sorted desc so the most-picked
    is at the top — the eye drops naturally."""
    fig = go.Figure()
    if totals.empty:
        return _style(fig, "Power-up pickups (7d)")
    ordered = totals.sort_values("count", ascending=True)
    labels = [POWERUP_LABELS.get(n, n).title() for n in ordered["name"]]
    fig.add_bar(
        x=ordered["count"], y=labels, orientation="h",
        marker_color=SKY,
        hovertemplate="%{y}: %{x} pickups<extra></extra>",
    )
    fig.update_layout(xaxis_title="Pickups")
    return _style(fig, "Power-up pickups (7d)")


def powerups_per_run(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if df.empty:
        return _style(fig, "Power-ups per run (30d)")
    fig.add_scatter(
        x=df["date"], y=df["per_run"], mode="lines+markers",
        line=dict(color=GOLD, width=2),
        hovertemplate="%{y:.2f} / run<extra></extra>",
    )
    return _style(fig, "Power-ups per run (30d)")
