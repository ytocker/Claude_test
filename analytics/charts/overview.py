"""
Overview / live-ops Plotly builders. Each takes pre-aggregated data and
returns a styled go.Figure (theme.style centralises the look).
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from theme import CORAL, GOLD, GRID, MUTED, SKY, SKY_SOFT, style


def plays_and_uniques(by_day_df: pd.DataFrame, days: int = 30) -> go.Figure:
    """Plays per day as bars + a 7-day rolling mean + unique players on a
    secondary axis. Trend is readable through day-to-day noise."""
    fig = go.Figure()
    if by_day_df.empty:
        return style(fig, f"Plays & unique players ({days}d)")
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
        # Below the plot so it never sits over the title bar.
        legend=dict(orientation="h", yanchor="top", y=-0.16, x=0),
    )
    return style(fig, f"Plays & unique players ({days}d)")


def plays_anomaly_band(band_df: pd.DataFrame, days: int = 30) -> go.Figure:
    """Daily plays against a *trailing* rolling mean ± 2σ band. The band
    is drawn only where there's a full 7-day warm-up; warm-up days show
    a faint connecting line for the plays but no band, so the reader
    isn't shown a fabricated 'normal range' on thin history. Days outside
    the band are coral; in-band gold; warm-up muted."""
    fig = go.Figure()
    if band_df.empty:
        return style(fig, f"Daily volume vs normal band ({days}d)")

    # Band only over the warmed-up tail; NaNs on warm-up days leave a gap
    # rather than a fake band collapsing to the point.
    fig.add_scatter(
        x=band_df["date"], y=band_df["hi"], mode="lines",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
        connectgaps=False,
    )
    fig.add_scatter(
        x=band_df["date"], y=band_df["lo"], mode="lines", fill="tonexty",
        fillcolor=SKY_SOFT, line=dict(width=0), name="Normal range (±2σ)",
        hoverinfo="skip", connectgaps=False,
    )
    fig.add_scatter(
        x=band_df["date"], y=band_df["mean"], mode="lines",
        line=dict(color=SKY, width=1, dash="dot"), name="7d mean (trailing)",
        hovertemplate="%{y:.1f} mean<extra></extra>", connectgaps=False,
    )

    warmup = band_df["warmup"].to_numpy()
    outlier = band_df["outlier"].to_numpy()
    colors = [MUTED if w else (CORAL if o else GOLD)
              for w, o in zip(warmup, outlier)]
    fig.add_scatter(
        x=band_df["date"], y=band_df["plays"], mode="markers",
        marker=dict(color=colors, size=7), name="Plays",
        customdata=[("warm-up" if w else "outlier" if o else "normal")
                    for w, o in zip(warmup, outlier)],
        hovertemplate="%{y} plays (%{customdata})<extra></extra>",
    )
    n_out = int(outlier.sum())
    sub = (f"{n_out} day(s) outside the trailing ±2σ range"
           if n_out else "No days outside the trailing ±2σ range")
    # Legend sits below the plot so it never collides with the subtitle.
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.18, x=0),
        yaxis_title="Plays",
    )
    return style(fig, f"Daily volume vs normal band ({days}d)", subtitle=sub)


def rejection_reasons(reasons_df: pd.DataFrame, days: int = 7) -> go.Figure:
    """Horizontal bar of rejected-submit reasons. Empty (no rejections) is
    a good state — render a clean empty frame, not an error."""
    fig = go.Figure()
    if reasons_df.empty:
        fig.add_annotation(text="No rejected submits in window 🎉",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           showarrow=False, font=dict(color=GRID))
        return style(fig, f"Rejected submits by reason ({days}d)")
    ordered = reasons_df.sort_values("count", ascending=True)
    fig.add_bar(
        x=ordered["count"], y=ordered["reason"], orientation="h",
        marker_color=CORAL, text=ordered["count"], textposition="outside",
        cliponaxis=False, hovertemplate="%{y}: %{x}<extra></extra>",
    )
    # Counts are integers — force integer ticks so a 1-vs-1 read doesn't
    # show fractional 0.2/0.4 gridlines, and pad the axis for the labels.
    top = int(ordered["count"].max())
    fig.update_layout(
        xaxis=dict(title="Rejected runs", dtick=1, range=[0, top + 1]),
    )
    return style(fig, f"Rejected submits by reason ({days}d)",
                 subtitle="The plausibility gate that dropped each run")


def avg_duration(by_day_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if by_day_df.empty:
        return style(fig, "Avg session duration (s)")
    fig.add_scatter(
        x=by_day_df["date"], y=by_day_df["avg_duration_s"],
        mode="lines+markers", line=dict(color=SKY, width=2),
        hovertemplate="%{y:.1f}s<extra></extra>",
    )
    return style(fig, "Avg session duration (s)")


def hourly_heatmap(grid: pd.DataFrame) -> go.Figure:
    """Weekday × hour-of-day heatmap. Rows Mon..Sun for reading order."""
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    fig = go.Figure(data=go.Heatmap(
        z=grid.values,
        x=[f"{h:02d}" for h in grid.columns],
        y=weekdays,
        colorscale="Blues",
        hovertemplate="%{y} %{x}:00 — %{z} plays<extra></extra>",
        colorbar=dict(title="Plays"),
    ))
    fig.update_yaxes(autorange="reversed")
    return style(fig, "When people play (UTC, weekday × hour)")
