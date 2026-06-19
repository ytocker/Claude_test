"""
Overview / live-ops Plotly builders. Each takes pre-aggregated data and
returns a styled go.Figure (theme.style centralises the look).
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from theme import CORAL, GOLD, GRID, MUTED, SKY, SKY_SOFT, style


def plays_and_uniques(by_day_df: pd.DataFrame, days: int = 30) -> go.Figure:
    """Plays per day as bars + a centred-trend smoothing line + unique
    players on a secondary axis. The smoothing line is a 7-day *display*
    smoother (min_periods=1, fills in from day 1) — distinct from the
    anomaly band's 14-day trailing baseline λ; labelled "smoothing" not
    "avg" so the two 7-day-ish lines on the tab aren't conflated."""
    fig = go.Figure()
    if by_day_df.empty:
        return style(fig, f"Plays & unique players ({days}d)")
    fig.add_bar(
        x=by_day_df["date"], y=by_day_df["plays"],
        name="Plays", marker_color=SKY_SOFT, hovertemplate="%{y} plays<extra></extra>",
    )
    rolling = by_day_df["plays"].rolling(7, min_periods=1).mean()
    fig.add_scatter(
        x=by_day_df["date"], y=rolling, name="Plays (7d smoothing)",
        mode="lines", line=dict(color=SKY, width=2),
        hovertemplate="%{y:.1f} (7d smoothing)<extra></extra>",
    )
    fig.add_scatter(
        x=by_day_df["date"], y=by_day_df["uniques"], name="Unique players",
        mode="lines+markers", line=dict(color=GOLD, width=2), yaxis="y2",
        hovertemplate="%{y} unique<extra></extra>",
    )
    # Tint each axis title to its series colour so the line→axis mapping
    # is readable without tracing the legend: SKY = Plays (left),
    # GOLD = Unique players (right).
    fig.update_layout(
        yaxis=dict(title=dict(text="Plays", font=dict(color=SKY))),
        yaxis2=dict(title=dict(text="Unique players", font=dict(color=GOLD)),
                    overlaying="y", side="right", showgrid=False,
                    tickfont=dict(color=GOLD)),
        # Below the plot so it never sits over the title bar.
        legend=dict(orientation="h", yanchor="top", y=-0.16, x=0),
    )
    return style(fig, f"Plays & unique players ({days}d)")


def plays_anomaly_band(band_df: pd.DataFrame, days: int = 30) -> go.Figure:
    """Daily plays against a *trailing* **Poisson** band (λ ± 2√λ). The
    band is drawn only past the 14-day warm-up; warm-up days carry no
    band, so the reader isn't shown a fabricated 'normal range' on thin
    history. Anomalous days (Poisson z beyond ±2 — a spike *or* a drop)
    are haloed coral; in-band gold; warm-up muted."""
    fig = go.Figure()
    if band_df.empty:
        return style(fig, f"Daily volume vs expected range ({days}d)")

    # Band only over the warmed-up tail; NaNs on warm-up days leave a gap
    # rather than a fake band collapsing to the point.
    fig.add_scatter(
        x=band_df["date"], y=band_df["hi"], mode="lines",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
        connectgaps=False,
    )
    fig.add_scatter(
        x=band_df["date"], y=band_df["lo"], mode="lines", fill="tonexty",
        fillcolor=SKY_SOFT, line=dict(width=0), name="Expected range (λ ± 2√λ)",
        hoverinfo="skip", connectgaps=False,
    )
    fig.add_scatter(
        x=band_df["date"], y=band_df["mean"], mode="lines",
        line=dict(color=SKY, width=1, dash="dot"), name="14d baseline λ (trailing)",
        hovertemplate="%{y:.1f} expected (λ)<extra></extra>", connectgaps=False,
    )

    warmup = band_df["warmup"].to_numpy()
    outlier = band_df["outlier"].to_numpy()

    # Faint marker over the warm-up region so the gap reads as "no band
    # yet" rather than missing data. Annotation anchored on the warm-up
    # midpoint when there is one.
    warm_dates = band_df.loc[band_df["warmup"], "date"]
    if not warm_dates.empty:
        mid = warm_dates.iloc[len(warm_dates) // 2]
        ymax = float(band_df["plays"].max() or 1)
        fig.add_annotation(
            x=mid, y=ymax, yanchor="top", showarrow=False,
            text="warm-up<br>(no band yet)",
            font=dict(size=10, color=MUTED), align="center", opacity=0.9,
        )

    # In-band plays: gold dots, drawn first so the coral halos sit on top.
    normal_mask = ~warmup & ~outlier
    fig.add_scatter(
        x=band_df.loc[normal_mask, "date"], y=band_df.loc[normal_mask, "plays"],
        mode="markers", marker=dict(color=GOLD, size=7), name="Plays (in range)",
        hovertemplate="%{y} plays (normal)<extra></extra>",
    )
    # Warm-up plays: muted, no band judged.
    fig.add_scatter(
        x=band_df.loc[warmup, "date"], y=band_df.loc[warmup, "plays"],
        mode="markers", marker=dict(color=MUTED, size=6), showlegend=False,
        hovertemplate="%{y} plays (warm-up)<extra></extra>",
    )
    # Outliers: large coral marker with a halo ring so they're
    # unmistakable against the gold in-band dots.
    fig.add_scatter(
        x=band_df.loc[outlier, "date"], y=band_df.loc[outlier, "plays"],
        mode="markers", name="Anomalous day",
        marker=dict(color=CORAL, size=14, symbol="circle",
                    line=dict(color="#FFE2D2", width=3)),
        hovertemplate="%{y} plays (anomalous)<extra></extra>",
    )
    n_out = int(outlier.sum())
    sub = (f"{n_out} day(s) outside the expected Poisson range (λ ± 2√λ)"
           if n_out else "No days outside the expected Poisson range (λ ± 2√λ)")
    # Legend sits below the plot so it never collides with the subtitle.
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.18, x=0),
        yaxis_title="Plays",
    )
    return style(fig, f"Daily volume vs expected range ({days}d)", subtitle=sub)


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
    # Framed as the companion to the freshness / "alive" check: a quiet
    # dashboard right now is only worth an alert if *this* weekday-hour
    # cell is usually busy. Reads as health context, not a planning grid.
    return style(fig, "Quiet now? Compare to the usual weekly rhythm",
                 subtitle="Plays by UTC weekday × hour — is the current "
                          "silence expected for this slot?")
