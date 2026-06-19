"""
Gameplay & balance Plotly builders.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from constants import POWERUP_LABELS
from theme import CORAL, GOLD, MUTED, SKY, style


def score_hist(scores: pd.Series) -> go.Figure:
    """Score distribution over the last 7 days, log-y.

    The x-axis is clipped to a robust upper bound rather than the raw max:
    a single near-ceiling whale/cheat run (the fixture has a 42k one)
    otherwise stretches the axis to 40k and squashes the entire 9–250-point
    playing population into one bar. The clip is built from p90/p95 — the
    *upper* quantiles still poisoned by a lone extreme value (p99 here is
    already 16k off one row) are deliberately avoided. Runs above the clip
    are counted in an annotation so nothing is hidden, just kept from
    dictating the scale. The vlines (median, p90) sit in opposite top
    corners so their labels never overlap."""
    fig = go.Figure()
    if scores.empty:
        return style(fig, "Score distribution (7d)")
    median = float(scores.median())
    p90 = float(scores.quantile(0.9))
    p95 = float(scores.quantile(0.95))
    # Right edge from low quantiles only (immune to a single whale): show
    # a little headroom past p95 / p90 for the genuine skilled tail. Pad 5%.
    clip = max(p95 * 1.5, p90 * 2.5, median * 2.0)
    n_over = int((scores > clip).sum())
    visible = scores[scores <= clip]
    fig.add_histogram(x=visible, nbinsx=40, marker_color=SKY,
                      hovertemplate="%{x}: %{y} runs<extra></extra>")
    fig.update_layout(yaxis_type="log", yaxis_title="Runs (log)",
                      xaxis_title="Score", xaxis_range=[0, clip * 1.05])
    fig.add_vline(x=median, line_dash="dash", line_color=GOLD,
                  annotation_text=f"median {int(median)}",
                  annotation_position="top left")
    fig.add_vline(x=p90, line_dash="dash", line_color=CORAL,
                  annotation_text=f"p90 {int(p90)}",
                  annotation_position="top right")
    if n_over:
        fig.add_annotation(x=1, y=1, xref="paper", yref="paper",
                           xanchor="right", yanchor="bottom", showarrow=False,
                           font=dict(size=10, color=MUTED),
                           text=f"+{n_over} run(s) above {int(clip):,} not shown")
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
    """Median + p90 score per day — the difficulty band the team tunes
    against. Two deliberate readability choices for the fat-tailed score
    distribution:
      • `max` is NOT drawn — a single near-ceiling run is a whale/cheater,
        not a tuning signal.
      • y-axis is log. On a low-volume day one extreme run can still drag
        p90 into the tens of thousands (the fixture's 42k run pins one
        6-run day's p90 to ~21k); on a linear axis that flattens every
        normal day into one flat line. Log keeps the ~200-point daily
        band legible while the spike stays visible — and honest."""
    sub = "Daily difficulty band · log-y · max omitted (whale/cheater, not signal)"
    fig = go.Figure()
    if q_df.empty:
        return style(fig, "Score percentiles per day", subtitle=sub)
    for col, color, name in (("median", SKY, "Median"),
                             ("p90", GOLD, "p90 (skilled ceiling)")):
        fig.add_scatter(
            x=q_df["date"], y=q_df[col], mode="lines+markers",
            name=name, line=dict(color=color, width=2),
            hovertemplate="%{x|%b %d}: %{y:,.0f} pts<extra>" + name + "</extra>")
    # Legend below the plot — a top legend collides with the subtitle.
    fig.update_layout(yaxis_type="log", yaxis_title="Score (log)",
                      legend=dict(orientation="h", yanchor="top", y=-0.18, x=0))
    return style(fig, "Score percentiles per day", subtitle=sub)


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
    """Horizontal bar of pickup counts, most-picked at top. Window-agnostic
    title — the tab drives the window off the global control, so a baked-in
    '(7d)' would lie when the user widens it."""
    fig = go.Figure()
    if totals.empty:
        return style(fig, "Power-up pickups")
    ordered = totals.sort_values("count", ascending=True)
    labels = [POWERUP_LABELS.get(n, n) for n in ordered["name"]]
    fig.add_bar(x=ordered["count"], y=labels, orientation="h", marker_color=SKY,
                hovertemplate="%{y}: %{x} pickups<extra></extra>")
    fig.update_layout(xaxis_title="Pickups")
    return style(fig, "Power-up pickups", subtitle="Total picks over the selected window")


def powerup_efficacy(eff_df: pd.DataFrame) -> go.Figure:
    """Per-power-up diverging bars of BOTH score lift and survival lift
    (runs that picked it vs runs that didn't), paired so they read against
    each other. The gap between the two is the honesty payload: when score
    lift sits well *above* duration lift the power-up is adding points per
    second alive (real value); when the two track together the score bump
    is mostly just more time on screen (exposure, the known confound).
    Low-sample power-ups (n_with < MIN_EFFICACY_N) are greyed so a noisy
    three-run bar isn't mistaken for a balance verdict. The marquee read."""
    fig = go.Figure()
    title = "Power-up efficacy — score vs survival lift"
    sub = ("Median with vs without · gap = value beyond time on screen · "
           "correlational, not causal")
    if eff_df.empty:
        return style(fig, title, subtitle=sub)
    # Sort by the exposure-adjusted excess so the genuinely over/under-
    # performing power-ups land at the extremes, not the most-exposed.
    ordered = eff_df.sort_values("excess_lift_pct", ascending=True)
    labels = [POWERUP_LABELS.get(n, n) for n in ordered["powerup"]]

    def _series(col, color, name):
        # Grey out low-n bars regardless of sign; full accent otherwise.
        bar_colors = [MUTED if low else color for low in ordered["low_n"]]
        fig.add_bar(
            x=ordered[col], y=labels, orientation="h", name=name,
            marker_color=bar_colors,
            text=[f"{v:+.0f}%" + ("*" if low else "")
                  for v, low in zip(ordered[col], ordered["low_n"])],
            textposition="outside", textfont=dict(size=10),
            customdata=ordered[["n_with", "n_without", "excess_lift_pct"]].values,
            hovertemplate="%{y} — " + name + ": %{x:+.0f}%<br>"
                          "excess vs survival: %{customdata[2]:+.0f}%<br>"
                          "n=%{customdata[0]} with, %{customdata[1]} without"
                          "<extra></extra>",
        )

    _series("score_lift_pct", GOLD, "Score lift")
    _series("dur_lift_pct", SKY, "Survival lift")
    fig.add_vline(x=0, line_color=MUTED, line_width=1)
    # Outside data labels need horizontal headroom or they clip; pad to the
    # largest-magnitude bar across BOTH series.
    span = float(max(ordered["score_lift_pct"].abs().max(),
                     ordered["dur_lift_pct"].abs().max(), 1))
    fig.update_layout(
        barmode="group", bargap=0.25, bargroupgap=0.05,
        xaxis_title="Lift vs runs without it (%)  ·  * = small sample",
        xaxis_range=[-span * 1.35, span * 1.35],
        # Legend below the plot: a top legend collides with the subtitle on
        # this full-width panel.
        legend=dict(orientation="h", yanchor="top", y=-0.28, x=0),
    )
    fig.update_traces(cliponaxis=False)
    return style(fig, title, subtitle=sub)


def coin_economy(econ_df: pd.DataFrame) -> go.Figure:
    """Coins-per-pillar per day — economy density over time. A drift flags
    a coin-spawn or rush-rate regression independent of how long runs run."""
    fig = go.Figure()
    if econ_df.empty:
        return style(fig, "Coin economy")
    fig.add_scatter(x=econ_df["date"], y=econ_df["coins_per_pillar"],
                    mode="lines+markers", line=dict(color=GOLD, width=2),
                    hovertemplate="%{x|%b %d}: %{y:.2f} coins/pillar<extra></extra>")
    # Anchor the y-axis at zero. Plotly's autoscale zooms to the data's
    # ±2% jitter and dramatises a flat economy into a sawtooth — exactly
    # the "don't sell noise as a trend" trap. A zero floor shows the
    # series for what it is: steady, with a headroom band for a real
    # regression to actually look like one.
    top = float(econ_df["coins_per_pillar"].max())
    fig.update_layout(yaxis_title="Coins per pillar",
                      yaxis_range=[0, top * 1.25])
    return style(fig, "Coin economy", subtitle="Coins collected per pillar passed")


def powerups_per_run(df: pd.DataFrame) -> go.Figure:
    """Avg power-ups picked per run, per day — a spawn-rate regression
    watch. Retained as a builder for the KPI/diagnostic surface; the tab
    leads with the per-run KPI card instead of a near-flat line to stay
    under the ≤8-visual budget. Kept so charts.__init__ stays stable."""
    fig = go.Figure()
    if df.empty:
        return style(fig, "Power-ups per run (30d)")
    fig.add_scatter(x=df["date"], y=df["per_run"], mode="lines+markers",
                    line=dict(color=GOLD, width=2),
                    hovertemplate="%{y:.2f} / run<extra></extra>")
    return style(fig, "Power-ups per run (30d)")
