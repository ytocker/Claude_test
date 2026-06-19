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
from theme import CORAL, GOLD, MUTED, SKY


def _delta(cur: int, prev: int, label: str) -> str | None:
    return f"{cur - prev:+d} {label}" if (prev or cur) else None


# Status banner colours, keyed off the health_status level. Reuses the
# palette so the banner reads as part of the product, not a stock alert.
_STATUS_STYLE = {
    "OK":    (SKY,   "🟢", "Healthy"),
    "WATCH": (GOLD,  "🟡", "Watch"),
    "ALERT": (CORAL, "🔴", "Alert"),
}


def render(df, window: int) -> None:
    import streamlit as st

    # Single glance-and-go verdict first — alive / growing / clean rolled
    # into one line so the operator reads "am I OK?" before any number.
    health = m.health_status(df)
    color, dot, word = _STATUS_STYLE[health["level"]]
    reasons = " · ".join(health["reasons"])
    st.markdown(
        f"<div style='padding:10px 14px;border-left:4px solid {color};"
        f"background:rgba(255,255,255,0.03);border-radius:4px;margin-bottom:8px'>"
        f"<span style='font-size:1.05rem;font-weight:600'>{dot} {word}</span>"
        f"<span style='color:{MUTED};margin-left:10px'>{reasons}</span></div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Health at a glance")

    dau_t, dau_y = m.dau_today(df), m.dau_yesterday(df)
    plays_t, plays_y = m.plays_today(df), m.plays_yesterday(df)
    cur7, prev7 = m.plays_window_delta(df, days=7)
    fresh = m.minutes_since_last_play(df)
    rej = m.rejection_rate(df, days=7)
    rej_n, rej_total = m.rejection_count(df, days=7)

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
    # Show the numerator/denominator so a 1-in-20 blip can't read as a
    # trend, and only flag 'elevated' once the count itself is non-trivial.
    rej_elevated = rej_n >= 3 and rej > 0.05
    k5.metric("Rejected submits (7d)", f"{rej * 100:.1f}%",
              delta=("elevated" if rej_elevated else
                     (f"{rej_n}/{rej_total} runs" if rej_total else None)),
              delta_color="inverse" if rej_elevated else "off",
              help="Share of runs whose leaderboard submit failed a "
                   "plausibility gate — the cheat / client-bug signal. "
                   f"{rej_n} rejected of {rej_total} runs in the last 7d; "
                   "low counts are noisy.")

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
