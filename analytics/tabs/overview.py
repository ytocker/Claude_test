"""
Tab 1 — Overview / Live-ops.

Glance-and-go health: is the game alive (freshness), growing (DAU/plays
with deltas), and clean (cheat/rejection rate)? The numbers a solo
operator checks first, in F-pattern order.
"""
from __future__ import annotations

# Import this tab's own submodules directly so the tab is self-contained —
# new metrics/charts can be added to metrics/overview.py + charts/overview.py
# and used here without touching the shared package __init__.
from charts import overview as c
from metrics import overview as m


def _delta(cur: int, prev: int, label: str) -> str | None:
    return f"{cur - prev:+d} {label}" if (prev or cur) else None


def render(df, window: int) -> None:
    import streamlit as st

    st.markdown("#### Health at a glance")

    dau_t, dau_y = m.dau_today(df), m.dau_yesterday(df)
    plays_t, plays_y = m.plays_today(df), m.plays_yesterday(df)
    cur7, prev7 = m.plays_window_delta(df, days=7)
    fresh = m.minutes_since_last_play(df)
    rej = m.rejection_rate(df, days=7)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Players today (DAU)", f"{dau_t:,}",
              delta=_delta(dau_t, dau_y, "vs yest"))
    k2.metric("Plays today", f"{plays_t:,}",
              delta=_delta(plays_t, plays_y, "vs yest"))
    k3.metric("Plays (7d)", f"{cur7:,}",
              delta=_delta(cur7, prev7, "vs prior 7d"))
    if fresh is None:
        k4.metric("Last play", "—")
    elif fresh < 90:
        k4.metric("Last play", f"{fresh:.0f} min ago")
    else:
        k4.metric("Last play", f"{fresh / 60:.1f} h ago",
                  delta="stale" if fresh > 24 * 60 else None, delta_color="inverse")
    k5.metric("Rejected submits (7d)", f"{rej * 100:.1f}%",
              delta="elevated" if rej > 0.05 else None, delta_color="inverse",
              help="Share of runs whose leaderboard submit failed a "
                   "plausibility gate — the cheat / client-bug signal.")

    st.divider()

    left, right = st.columns([3, 2])
    with left:
        st.plotly_chart(
            c.plays_and_uniques(m.by_day(df, days=window), days=window),
            use_container_width=True,
        )
    with right:
        st.plotly_chart(
            c.rejection_reasons(m.rejection_reasons(df, days=window), days=window),
            use_container_width=True,
        )

    st.plotly_chart(
        c.plays_anomaly_band(m.daily_plays_with_band(df, days=window), days=window),
        use_container_width=True,
    )
    st.plotly_chart(
        c.hourly_heatmap(m.hourly_heatmap(df)),
        use_container_width=True,
    )
