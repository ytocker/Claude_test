"""
Tab 3 — Gameplay & Balance.

How hard is the game, is skill drifting, are the power-ups balanced, and
is the coin economy steady? The tuning-knob tab.
"""
from __future__ import annotations

# Self-contained imports — see tabs/overview.py for the rationale.
from charts import gameplay as c
from metrics import gameplay as m


def render(df, window: int) -> None:
    import streamlit as st

    st.markdown("#### Difficulty, skill & balance")

    score = m.score_summary(df, days=7)
    dur = m.duration_summary(df, days=7)
    ppr = m.powerups_per_run_by_day(df, days=7)
    ppr_last = float(ppr["per_run"].iloc[-1]) if not ppr.empty else 0.0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Median score (7d)", f"{score['median']:.0f}")
    k2.metric("p90 score (7d)", f"{score['p90']:.0f}",
              help="Top-decile run — the ceiling skilled players reach.")
    k3.metric("Median survival (7d)", f"{dur['median']:.0f}s")
    k4.metric("Coins / run (7d)", f"{m.coins_per_run(df, days=7):.1f}")
    k5.metric("Power-ups / run", f"{ppr_last:.2f}",
              help="Avg power-ups picked per run on the most recent day.")

    st.divider()

    left, right = st.columns(2)
    with left:
        st.plotly_chart(c.score_hist(m.score_distribution(df, days=7)),
                        use_container_width=True)
    with right:
        st.plotly_chart(c.duration_hist(m.duration_distribution(df, days=7)),
                        use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.plotly_chart(c.score_quantiles(m.score_quantiles_by_day(df, days=window)),
                        use_container_width=True)
    with right:
        st.plotly_chart(c.skill_over_time(m.skill_proxy_by_day(df, days=window)),
                        use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.plotly_chart(c.powerup_mix(m.powerup_totals(df, days=window)),
                        use_container_width=True)
    with right:
        st.plotly_chart(c.coin_economy(m.coin_economy_by_day(df, days=window)),
                        use_container_width=True)

    # Marquee balance read, given full width: the paired score/survival bars
    # need the room and this is the chart the team retunes against.
    st.plotly_chart(c.powerup_efficacy(m.powerup_efficacy(df, days=window)),
                    use_container_width=True)

    st.caption(
        "*Reverse* excluded (disabled in-game). *Surprise* counts only the box "
        "pickup. Efficacy is correlational — longer runs naturally see more "
        "power-up spawns; the score-vs-survival gap is the partial control for "
        "that. Bars marked * are below "
        f"{m.MIN_EFFICACY_N} picked runs — noisy, read with caution."
    )
