"""
Skybit analytics dashboard — Streamlit entrypoint.

Layout follows the F-pattern: the most critical metric (today's DAU)
sits top-left, then a KPI row, then engagement / skill / power-up
panels, with the player roster at the bottom. ≤8 visuals total to
stay inside the established dashboard-design guidance.

Live refresh: streamlit-autorefresh ticks every 60s; data fetchers
are st.cache_data(ttl=60) so concurrent viewers share the same pull.
The sidebar "Refresh now" button clears the cache for an immediate
reload.

Run locally with sample data:
    STREAMLIT_USE_FIXTURE=1 streamlit run analytics/app.py
With live Supabase: drop creds into .streamlit/secrets.toml first.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

import charts
import data
import identity
import metrics
from filters import plausible


st.set_page_config(
    page_title="Skybit · Analytics",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tick every 60s. The cached fetchers absorb the load — repeat viewers
# hit cache rather than Supabase.
st_autorefresh(interval=60_000, key="tick")


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### Skybit · Analytics")
    st.caption("Live, anonymous gameplay telemetry. UTC.")

    window = st.selectbox(
        "Window",
        options=[7, 30, 90],
        index=1,
        format_func=lambda d: f"Last {d} days",
        help="How far back to pull. Affects most charts (the 'today' "
             "KPIs always look at UTC-today regardless).",
    )

    if st.button("Refresh now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.caption(
        "Plausibility-filtered: rows with score > 10,000 are dropped "
        "before any chart sees them. Matches the in-game leaderboard."
    )


# ── Data ─────────────────────────────────────────────────────────────────────

try:
    raw = data.fetch_plays(days=max(window, 30))
except RuntimeError as e:
    st.error(str(e))
    st.stop()

df = plausible(raw)

if df.empty:
    st.warning("No plays in the selected window yet. Once players run "
               "the deployed game, rows will appear here within ~60s.")
    st.stop()


# ── Section A — Headline KPI row ─────────────────────────────────────────────

st.markdown("## Today")

k1, k2, k3, k4, k5 = st.columns(5)

dau_today = metrics.dau_today(df)
dau_yest = metrics.dau_yesterday(df)
k1.metric(
    "Unique players today (DAU)",
    f"{dau_today:,}",
    delta=f"{dau_today - dau_yest:+d} vs yesterday" if dau_yest or dau_today else None,
)

plays_today = metrics.plays_today(df)
plays_yest = metrics.plays_yesterday(df)
k2.metric(
    "Plays today",
    f"{plays_today:,}",
    delta=f"{plays_today - plays_yest:+d} vs yesterday" if plays_yest or plays_today else None,
)

by_day = metrics.by_day(df, days=7)
k3.metric(
    "Plays last 7 days",
    f"{int(by_day['plays'].sum()):,}",
)

ret = metrics.returning_rate_7d(df)
k4.metric(
    "Returning rate (7d)",
    f"{ret * 100:.0f}%",
    help="Share of last-7-day players who played on ≥2 distinct UTC days. "
         "Hyper-casual benchmark for D1 retention is 25–35%.",
)

one_shots = metrics.one_shot_count(df, days=7)
k5.metric(
    "One-shot players (7d)",
    f"{one_shots:,}",
    help="Players who tried the game exactly once in the last 7 days. "
         "High values mean the first-run experience isn't pulling people "
         "back for a second attempt. Hyper-casual benchmark: 60–75% of "
         "unique players are one-shots.",
)


# ── Section B — Engagement over time ────────────────────────────────────────

st.markdown("## Engagement")

b30 = metrics.by_day(df, days=window)
left, right = st.columns(2)
with left:
    st.plotly_chart(charts.plays_and_uniques(b30), use_container_width=True)
with right:
    st.plotly_chart(charts.avg_duration(b30), use_container_width=True)

st.plotly_chart(
    charts.hourly_heatmap(metrics.hourly_heatmap(df)),
    use_container_width=True,
)


# ── Section C — Score & skill ────────────────────────────────────────────────

st.markdown("## Skill")

left, right = st.columns(2)
with left:
    st.plotly_chart(
        charts.score_hist(metrics.score_distribution(df, days=7)),
        use_container_width=True,
    )
with right:
    st.plotly_chart(
        charts.score_quantiles(metrics.score_quantiles_by_day(df, days=window)),
        use_container_width=True,
    )


# ── Section D — Power-up economy ─────────────────────────────────────────────

st.markdown("## Power-ups")

left, right = st.columns(2)
with left:
    st.plotly_chart(
        charts.powerup_mix(metrics.powerup_totals(df, days=7)),
        use_container_width=True,
    )
with right:
    st.plotly_chart(
        charts.powerups_per_run(metrics.powerups_per_run_by_day(df, days=window)),
        use_container_width=True,
    )

st.caption(
    "*Reverse* is excluded (disabled in-game). *Surprise* counts only the "
    "Surprise Box pickup itself — the rerolled outcome increments its own key."
)


# ── Section E — Player roster ────────────────────────────────────────────────

st.markdown("## Players")

st.plotly_chart(
    charts.engagement_segments(
        metrics.engagement_segments(df, days=window), days=window,
    ),
    use_container_width=True,
)

ros = metrics.roster(df, days=window, top_n=50)

if ros.empty:
    st.info("No plays in this window yet.")
else:
    # Resolve display names + color swatches.
    nick_color = ros["device_id"].apply(identity.for_device)
    ros = ros.assign(
        Player=[n for n, _ in nick_color],
        Color=[c for _, c in nick_color],
    )
    display = ros[[
        "Color", "Player", "plays", "days_active",
        "best_score", "avg_duration_s", "last_seen",
    ]].rename(columns={
        "plays": "Plays",
        "days_active": "Days active",
        "best_score": "Best score",
        "avg_duration_s": "Avg duration (s)",
        "last_seen": "Last seen",
    })
    display["Avg duration (s)"] = display["Avg duration (s)"].round(1)
    display["Last seen"] = pd.to_datetime(display["Last seen"]).dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(
        display,
        column_config={
            "Color": st.column_config.TextColumn(
                "🎨",
                help="Deterministic color from device_id.",
                width="small",
            ),
            "Player": st.column_config.TextColumn(
                "Player",
                help="Deterministic petname from device_id. Same UUID → same name.",
            ),
        },
        hide_index=True,
        use_container_width=True,
    )

st.caption(
    f"Showing top {len(ros)} of {df['device_id'].nunique()} unique players "
    f"in the last {window} days. One-shot players are included — sorted "
    f"first by total plays, then by most recent."
)
