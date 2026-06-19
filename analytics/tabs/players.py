"""
Tab 2 — Players & Retention.

The retention story: cohort curve + triangle, new-vs-returning balance,
session depth, engagement segments, and the per-player roster. Retention
math runs over the full fetched frame (the app fetches wide) so cohorts
are real; display charts honour the sidebar window.
"""
from __future__ import annotations

import pandas as pd

# Self-contained imports — see tabs/overview.py for the rationale.
from charts import players as c
from metrics import players as m
import identity


def render(df, window: int) -> None:
    import streamlit as st

    st.markdown("#### Do players come back?")

    ret = m.retention_summary(df)
    active = m.active_players(df, days=7)
    one_shot = m.one_shot_count(df, days=7)
    bounce = (one_shot / active * 100) if active else 0.0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("New players today", f"{m.new_players_today(df):,}",
              help="Devices whose first play seen in-window is today.")
    k2.metric("Returning rate (7d)", f"{m.returning_rate_7d(df) * 100:.0f}%",
              help="Share of 7d players active on ≥2 distinct days.")
    k3.metric("D1 retention", f"{ret['d1'] * 100:.0f}%",
              help="Cohort devices that played again the next day. "
                   "Hyper-casual benchmark: 25–35%.")
    k4.metric("D7 retention", f"{ret['d7'] * 100:.0f}%",
              help="Cohort devices that played again on day 7. "
                   "Hyper-casual benchmark: 6–12%.")
    k5.metric("Bounce (7d)", f"{bounce:.0f}%",
              delta=f"{one_shot:,} one-shots", delta_color="off",
              help="One-shot players as a share of 7d actives.")

    st.divider()

    left, right = st.columns(2)
    with left:
        st.plotly_chart(c.retention_curve(m.retention_curve(df, max_day=7)),
                        use_container_width=True)
    with right:
        st.plotly_chart(c.retention_matrix(m.retention_matrix(df, max_day=7)),
                        use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            c.new_vs_returning(m.new_vs_returning_by_day(df, days=window), days=window),
            use_container_width=True,
        )
    with right:
        st.plotly_chart(
            c.sessions_histogram(m.sessions_per_active_day(df, days=window), days=window),
            use_container_width=True,
        )

    st.plotly_chart(
        c.engagement_segments(m.engagement_segments(df, days=window), days=window),
        use_container_width=True,
    )

    _roster_table(st, df, window)


def _roster_table(st, df, window: int) -> None:
    st.markdown("##### Active players")
    ros = m.roster(df, days=window, top_n=50)
    if ros.empty:
        st.info("No plays in this window yet.")
        return
    nick_color = ros["device_id"].apply(identity.for_device)
    ros = ros.assign(Player=[n for n, _ in nick_color], Color=[c2 for _, c2 in nick_color])
    display = ros[[
        "Color", "Player", "plays", "days_active",
        "best_score", "avg_duration_s", "last_seen",
    ]].rename(columns={
        "plays": "Plays", "days_active": "Days active", "best_score": "Best score",
        "avg_duration_s": "Avg duration (s)", "last_seen": "Last seen",
    })
    display["Avg duration (s)"] = display["Avg duration (s)"].round(1)
    display["Last seen"] = pd.to_datetime(display["Last seen"]).dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(
        display,
        column_config={
            "Color": st.column_config.TextColumn("🎨", width="small",
                help="Deterministic color from device_id."),
            "Player": st.column_config.TextColumn("Player",
                help="Deterministic petname from device_id. Same UUID → same name."),
        },
        hide_index=True, use_container_width=True,
    )
    st.caption(
        f"Top {len(ros)} of {df['device_id'].nunique()} unique players in the last "
        f"{window} days. One-shots included — sorted by plays, then most recent."
    )
