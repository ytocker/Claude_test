# Skybit v5_powerups — work handoff

Branch: `v5_powerups`. Everything below is live on that branch.
Conventions: procedural art only; both targets (native + pygbag/WASM)
stay green; fixed 60 fps physics; WHY-only comments. Design rounds are
tooling-only and screenshots go to GitHub — **links only, never inline
images in chat**.

## Biome cycle (the clock everything keys off)
`game/biome.py`: `CYCLE_SECONDS = 320`, `PHASE_BUCKETS = 32`. Phase is
`(biome_time / CYCLE_SECONDS) % 1`. Keyframes: DAY 0.0, GOLDEN 0.231,
SUNSET 0.363, DUSK 0.513, NIGHT 0.644, PREDAWN 0.794, SUNRISE 0.906.

Event spacing across the cycle (deliberately non-overlapping):
- SANDSTORM  day      phase 0.03–0.22  (visibility veil)
- RAIN       sunset   centers 0.35/0.50/0.62  (coin wobble + Pip shiver)
- THUNDER    dusk     phase 0.55–0.72  (coin loss on a strike)
- SNOW       predawn  phase ~0.85      (tailwind speedup)
- golden-hour breeze leaves at 0.18 (ambient, `calm_breeze`)

## Power-ups
`game/config.py`. All durations 8.0 s. `POWERUP_CHANCE = 0.24`,
`POWERUP_COOLDOWN = 5.5`, no power-ups on Coin Rush pillars.

Active pool `POWERUP_WEIGHTS`: triple (3× coins), magnet, slowmo, kfc
(fry skin), ghost (phase through pillars), grow (1.4× scale), surprise
(re-rolls to one of the six). Genie is test-promoted into the early
pool on this branch.

Secret pool `SECRET_POWERUP_WEIGHTS` (gated by `LATE_GAME_SCORE = 500`,
or the first `TEST_SECRETS_FIRST_N_PILLARS = 15` pillars in test mode):
skateboard, lottery, genie (0.125). **heist + phoenix are disabled —
weights removed but all code intact**, re-add the weight tuple to
restore. Reverse stays disabled (project rule).

Coin Rush: every `COIN_RUSH_INTERVAL = 15` pillars, gap ×
`COIN_RUSH_GAP_BOOST = 1.30`, ~`COIN_RUSH_COINS = 14` in a formation.

Genie powerup is a cinematic: a `GenieCharacter` (game/entities.py)
rises ahead of Pip and conjures three offer powerups on timed beats
(shine particles fly from its palms and poof into the offers). Wired
in `World._activate_genie`.

## Weather events — code map

All intensity curves live in `game/weather.py` and use the
`_bump(phase, center, width)` smoothstep. Each event fans its
intensity out to particles (weather.py) and gameplay (world.py).

### 1. THUNDERSTORM (dusk, coin loss)
- `lightning_active(phase)` true 0.55–0.72.
- `World._fire_storm_jolt` (world.py ~L1714): on a strike Pip loses
  `lost = min(100, self.coin_count)` coins (was 50 — changed this
  session), float text `f"-{lost}!"`, coin blast, full-screen flash,
  shake, and a 3.5 s X-ray skeleton flash on Pip. Ledgered via
  `_proof.record(..., -lost, "weather_jolt")`. 25 s lockout between
  strikes.
- Bolt rendered by `_draw_lightning_bolt` (scenes.py): 4 layered
  polylines (wide bloom + purple + cyan + white core), round joints.

### 2. SNOW SQUALL (predawn, tailwind speedup)
- `storm_intensity(phase)` centered 0.85, ~8 s plateau (×1.045 clamp).
- Gameplay (world.py `_apply_weather_effects` ~L1519):
  - `bird.wind_lean` = rightward visual push, `WEATHER_WIND_LEAN_AMP = 8.0`.
  - `_current_scroll` multiplies by `1 + WEATHER_WIND_SCROLL_FACTOR * wi`
    (`= 0.30`, so 1.30× scroll at peak — pipes approach faster).
  - `bird.snow_load` integrator: gain `WEATHER_SNOW_ACCUM_RATE = 0.12`,
    melt `MELT_BASE = 0.025 + MELT_FADE = 0.16 * (1 - intensity)` —
    melt accelerates as the storm fades so snow clears quickly.
- Snow on Pip: `Bird._draw_snow_cap` (entities.py ~L362). Emergent
  flake field built by `_build_snow_pool` (~L281); pool sort is the
  **PATCHY** key `abs(dy)*1.3 - w*3.0` → perimeter-first buildup that
  piles inward. `_SNOW_LINE_KEY` is the head-forward continuous snow
  line (tail → crown). Rotates with Pip via `ang = radians(-tilt)`
  (matches the sprite's `rotozoom` CCW convention — this fixed the
  "snow slides off during jumps" bug).
- Visual particles repurpose the `_WindDrift/_WindDust/_WindStreak/
  _WindSwirl` pools; `SNOW_TINT = (74,96,130)` cold wash in
  `Weather.draw`.
- Snow visual design history: rejected "sparkles" and "forced curve"
  looks in favor of the emergent flake field; rejected a max-snow
  whole-body/parcel variant; final = perimeter-first patchy buildup,
  head-forward line, fuller bridge.

### 3. SANDSTORM (day, visibility-only) — newest
- `sand_intensity(phase)` (weather.py L82): 0 outside [0.03, 0.22];
  rise 0.03→0.15 (long tease); plateau 0.15→0.17 = 1.0; fade →0.22.
  Ends before sunset rain at 0.23 — no overlap. Read in bands by the
  renderer: `<0.35` tease, `0.35–0.65` encroaching, `>=0.65` peak.
- Palette = the EXACT original-haboob tones: `SAND_HI / SAND_BODY /
  SAND_DEEP / SAND_HAZE` (weather.py ~L104). One palette for both
  walls (user rejected two-tone).
- Rendering (weather.py): `_sand_disc` cached soft disc; `class
  _SandMote`; `_render_sand_wall(s, kind, seed)` builds 2×-supersampled
  'far'/'front' haboob walls, **cached per intensity bucket** for
  60 fps. Two new draw passes:
  - `Weather.draw_far(surf)` — distant wall + dust-devils, called
    BEFORE `draw_mountains` (scenes.py ~L852) so it sits on the
    horizon behind the peaks (the tease).
  - `Weather.draw_front(surf)` — warm-haze veil + mountain-bury +
    foreground engulfing wall + sand motes, called AFTER the bird,
    before the HUD (scenes.py ~L1000). **This is what puts the sand
    in FRONT of Pip** while the HUD stays readable.
- Gameplay: visibility-only — NO scroll/physics change. Only a
  cosmetic `bird.sand_load` integrator (world.py, mirrors snow):
  `WEATHER_SAND_ACCUM_RATE = 0.13`, `MELT_BASE = 0.030`,
  `MELT_FADE = 0.17`.
- Sand on Pip: `Bird._draw_sand_coat` (entities.py ~L442) — ochre dust
  SPREAD over the whole body (vs snow's top drift), R2 scatter, eyes
  kept light, banks with tilt. Both coats called in `Bird.draw` after
  the sprite (~L1297-1310).

## Render-order layering (scenes.py, why Pip is behind the sand)
sky → `weather.draw_far` (sandstorm horizon wall) → mountains → ground
→ pipes → ramps → `weather.draw` (rain/snow) → coins → bird → snow/sand
coats (in Bird.draw) → `weather.draw_front` (sandstorm veil+wall, in
front of Pip) → HUD. The `draw_far`/`draw_front` passes are gated to
`STATE_PLAY`.

## TEST-MODE bootstrap (v5_powerups only — revert before merge)
`World.__init__` (~L237): `self.biome_time = biome.CYCLE_SECONDS * 0.015`
(~5 s, a few seconds before the sandstorm tease at 0.03) so the
sandstorm is the first thing you see. Other presets noted in the
comment: 0.46 dusk storm, 0.73 predawn snow. Also `score = 250`,
`coin_count = 250`. `config.py`: `RAMP_PIPES = 0`/`PLATEAU_PIPES = 0`
(no newbie ramp), `TEST_MODE_NO_SUBMIT = True`, genie test-promoted,
phoenix removed from secret weights. All marked with revert comments.

## Tooling (design rounds, all under tools/)
render_wind_event.py, render_wind_themes.py (theme_haboob RESERVED for
a future event), render_snow_buildup.py, render_buildup_order.py,
render_maxsnow.py, render_snow_placements.py, render_snow_variants.py,
render_sandstorm.py (renders from the LIVE weather.py methods +
the timeline graph), render_storm_jolt.py. Screenshots in
`docs/screenshots/wind_themes/` (+ snow_back/, sandstorm/). The
sandstorm timeline + stage sheet are `docs/screenshots/wind_themes/
sandstorm/timeline_graph.png` and `stages_sheet.png`.

Run a tool headless:
`SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_sandstorm`

## Deploy / CI note
`.github/workflows/pages.yml` builds GitHub Pages for 4 branches
(main, v4_skybit, v4_skybit_powerups, v5_powerups) via sequential
checkouts. A deploy this session failed on the "Checkout
v4_skybit_powerups" step with "could not read Username for
github.com" — diagnosed as a transient Actions multi-branch-checkout
auth/infra issue, NOT a code problem (commits reached GitHub). Fix =
re-run the workflow. Bundle-size ceiling 5 MB; pytest must stay
22/22 before any build.

## Verification quickstart
- `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m pytest tests/`
  → 22/22.
- Headless sandstorm smoke: step a `World` from phase 0.01→0.25 with a
  pinned (non-dying) bird; assert `sand_intensity(0.23) == 0` and that
  `bird.sand_load` rises then clears by ~0.22.
- In-game (deployed v5_powerups): start → a few seconds clear day →
  sandstorm tease (distant wall) → engulf → fade, Pip behind the sand,
  course veiled but HUD readable.
