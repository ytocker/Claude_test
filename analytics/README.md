# Skybit Analytics Dashboard

Live KPI dashboard for the Skybit game. Reads anonymous per-run
telemetry from Supabase (`public.plays`) and renders DAU, engagement,
skill, power-up economy, and an active-player roster — with each
player shown as a deterministic petname + color swatch instead of a
raw UUID.

Built with Streamlit + Plotly + pandas. Deployed to Streamlit
Community Cloud.

## Local development

The fast loop uses a bundled fixture (no Supabase credentials needed):

```bash
cd analytics
pip install -r requirements.txt
STREAMLIT_USE_FIXTURE=1 streamlit run app.py
```

To run against the live database locally, copy
`.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`, paste
the project's service-role key, and drop the env var:

```bash
streamlit run app.py
```

`secrets.toml` is gitignored.

## Tests

```bash
cd analytics
pip install pytest
pytest
```

## Deployment (Streamlit Community Cloud)

1. Sign in at <https://share.streamlit.io> with the GitHub account
   that owns `ytocker/skybit`.
2. New app → branch `v4_skybit_analytics`, main file `analytics/app.py`.
3. Settings → Secrets, paste:
   ```toml
   [supabase]
   url = "https://<project-ref>.supabase.co"
   service_role_key = "..."
   ```
4. Save. Streamlit Cloud builds and serves. Future pushes to
   `v4_skybit_analytics` auto-redeploy.

## Why the service-role key (and why not GitHub Pages)

`public.plays` deliberately has no `anon` SELECT policy — only the
service-role key can read it. That key bypasses RLS, so it must stay
server-side. Streamlit Community Cloud server-renders the Python and
injects the key via encrypted environment, so it never reaches the
browser. A static-only host like GitHub Pages would have to either
ship the key in the bundle (instant full DB compromise) or open up
RLS (telemetry table becomes public-readable). Neither is acceptable.

## What's on the dashboard

| Section | Visuals |
|---|---|
| Today (KPI row) | DAU, plays, plays-last-7d, returning rate |
| Engagement | Plays + uniques per day, avg duration, hourly weekday × hour heatmap |
| Skill | Score histogram (log-y) + median/p90/max per day |
| Power-ups | Pickup mix (last 7d) + power-ups per run trend |
| Active players | Top 50 by play count, nickname + color, best score, last seen |

All charts apply the same plausibility filter as the in-game
leaderboard (`score ≤ 10,000`).

## Refresh strategy

`streamlit-autorefresh` ticks every 60 seconds. Data fetchers are
cached with `st.cache_data(ttl=60)` so the autorefresh hits cache for
concurrent viewers — only one viewer per minute actually queries
Supabase. The sidebar "Refresh now" button clears the cache.
