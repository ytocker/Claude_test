"""
Players & retention Plotly builders.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from theme import CORAL, GOLD, GRID, MUTED, SKY, SKY_SOFT, style

_CAVEAT = "Install = first play seen in window; trailing cohorts are censored, not zero"
_MODE_NOTE = {
    "unbounded": "Unbounded: active on day n or any later day (monotone leak curve)",
    "exact": "Exact day-n only — bumpy on small N; a late return lifts a single point",
}


def retention_curve(curve_df: pd.DataFrame, mode: str = "unbounded") -> go.Figure:
    """Pooled D0..Dn retention curve with retained-% labels. The single
    most important shape on the tab — how fast the game leaks players.
    `mode` only changes the subtitle wording; the maths lives in the
    metric. N (the settled denominator) rides the subtitle so the small-N
    noise floor is explicit."""
    fig = go.Figure()
    note = _MODE_NOTE.get(mode, _MODE_NOTE["unbounded"])
    if curve_df.empty:
        return style(fig, "Retention curve (D0–D7)", subtitle=note)
    n = int(curve_df["cohort_devices"].iloc[0])
    pct = curve_df["retained_frac"] * 100
    fig.add_scatter(
        x=curve_df["day_offset"], y=pct, mode="lines+markers+text",
        line=dict(color=SKY, width=3), marker=dict(size=8, color=SKY),
        text=[f"{p:.0f}%" for p in pct], textposition="top center",
        textfont=dict(color=MUTED, size=11),
        customdata=curve_df["retained"],
        hovertemplate="D%{x}: %{y:.1f}% (%{customdata} of "
                      + f"{n})<extra></extra>",
    )
    fig.update_layout(
        xaxis=dict(title="Days since first play", dtick=1),
        yaxis=dict(title="Retained", ticksuffix="%", range=[0, 115]),
    )
    subtitle = f"{note} · n={n} settled installs"
    return style(fig, "Retention curve (D0–D7)", subtitle=subtitle)


def retention_matrix(matrix_df: pd.DataFrame, sizes=None) -> go.Figure:
    """Cohort × day-offset retention triangle. Censored cells stay blank.
    Row labels carry the cohort size (n=…) when `sizes` (a cohort_date →
    size mapping) is supplied, so a vivid-looking 100% row that is really
    one device can't masquerade as a trend."""
    fig = go.Figure()
    if matrix_df.empty:
        return style(fig, "Retention by cohort", subtitle=_CAVEAT)
    z = (matrix_df * 100).values

    def _label(d):
        base = d.strftime("%b %d") if hasattr(d, "strftime") else str(d)
        if sizes is not None and d in sizes:
            return f"{base} · n={int(sizes[d])}"
        return base

    y = [_label(d) for d in matrix_df.index]
    fig.add_trace(go.Heatmap(
        z=z, x=[f"D{c}" for c in matrix_df.columns], y=y,
        colorscale="Blues", zmin=0, zmax=100,
        hovertemplate="%{y} · %{x}: %{z:.0f}%<extra></extra>",
        colorbar=dict(title="%"),
    ))
    fig.update_yaxes(autorange="reversed")
    return style(fig, "Retention by cohort",
                 subtitle=_CAVEAT + " · row n = cohort size")


def new_vs_returning(nvr_df: pd.DataFrame, days: int = 30) -> go.Figure:
    """Stacked daily new vs returning active players. Healthy growth is a
    rising returning base, not just churn-and-replace acquisition."""
    fig = go.Figure()
    if nvr_df.empty:
        return style(fig, f"New vs returning players ({days}d)")
    fig.add_bar(
        x=nvr_df["date"], y=nvr_df["returning"], name="Returning",
        marker_color=SKY, hovertemplate="%{y} returning<extra></extra>",
    )
    fig.add_bar(
        x=nvr_df["date"], y=nvr_df["new"], name="New",
        marker_color=GOLD, hovertemplate="%{y} new<extra></extra>",
    )
    fig.update_layout(
        barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        yaxis_title="Active players",
    )
    return style(fig, f"New vs returning players ({days}d)")


def sessions_histogram(sessions: pd.Series, days: int = 30) -> go.Figure:
    """Distribution of plays-per-active-day. A wall at 1 = single-run
    sessions; a long tail = bingeing."""
    fig = go.Figure()
    if sessions.empty:
        return style(fig, f"Session depth ({days}d)")
    fig.add_histogram(
        x=sessions, marker_color=SKY,
        xbins=dict(start=0.5, size=1),
        hovertemplate="%{x} plays/day: %{y} sessions<extra></extra>",
    )
    median = float(sessions.median())
    fig.add_vline(x=median, line_dash="dash", line_color=GOLD,
                  annotation_text=f"median={median:.0f}",
                  annotation_position="top")
    fig.update_layout(xaxis_title="Plays in a single day", yaxis_title="Device-days")
    return style(fig, f"Session depth ({days}d)",
                 subtitle="Plays per device per active day")


def engagement_segments(seg_df: pd.DataFrame, days: int) -> go.Figure:
    """Horizontal bar of player counts per play-count bucket. The 1-play
    bar is drawn in gold so the bounce segment pops."""
    fig = go.Figure()
    if seg_df.empty:
        return style(fig, f"Players by engagement ({days}d)")
    colors = [GOLD if seg == "1 play" else SKY for seg in seg_df["segment"]]
    fig.add_bar(
        x=seg_df["players"], y=seg_df["segment"], orientation="h",
        marker_color=colors, text=seg_df["players"], textposition="outside",
        hovertemplate="%{y}: %{x} players<extra></extra>",
    )
    total = int(seg_df["players"].sum())
    one_shot = int(seg_df.loc[seg_df["segment"] == "1 play", "players"].sum())
    subtitle = (
        f"{one_shot}/{total} players ({one_shot / total * 100:.0f}%) played only once"
        if total else "no players in window"
    )
    span = float(seg_df["players"].max() or 1)
    fig.update_layout(xaxis_title="Players", yaxis=dict(autorange="reversed"),
                      xaxis_range=[0, span * 1.18])
    fig.update_traces(cliponaxis=False)
    return style(fig, f"Players by engagement ({days}d)", subtitle=subtitle)
