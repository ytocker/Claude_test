## What this is

**Skybit — Pocket Sky Flyer.** A one-button Flappy-style casual arcade
game. Python 3.11+ / Pygame 2.x. Ships two build targets from the same
source: native desktop and pygbag/WASM in a browser. ~13k LOC Python.

## Active development branch

`main` is the live deployed version (currently built from the `v4_skybit`
lineage). `main` and `gh-pages` are deployment artifacts — never develop
on them.

`v5_skybit` is the active R&D line and the next deployment. Branch off it
for new work unless the user says otherwise. Work is split into per-aspect
forks off `v5_skybit`, each maturing one upgrade — power-ups, weather
events, graphics, etc. — before it folds into the next formal version.

`claude/*` task branches are single-chat scratch space; some are
intentionally stripped down and are NOT representative of the project.
Sanity-check the real layout against `v5_skybit`.

## Run

```
pip install pygame
python main.py
```

Web build is driven by pygbag; the entry point branches on
`sys.platform == "emscripten"`.

## Code map (`v5_skybit`)

```
main.py                       Entry — sync + async for pygbag
inject_theme.py               JS bridge injected into the WASM bundle
                              (closure-private window.__sk dispatcher)
game/
  config.py                   Physics, spawn rates, durations, weights,
                              score gates + per-kind replacement
  scenes.py                   Scene state machine + App + tap cooldown
  world.py                    Simulation: scroll/spawn/collision/FX (~1.3k)
  entities.py                 Bird, Pipe, Coin, PowerUp, Particle,
                              FloatText (~2.2k LOC — split candidate)
  parrot.py                   4-frame macaw + KFC/ghost/hat/grow variants
  draw.py                     Gradient surfaces, glow caches, terrain
  ambient.py                  Background ambient elements
  biome.py                    Day/night palette interpolation (5 min cycle)
  weather.py                  Rain/fog/thunder per biome phase
  hud.py                      Score, timers, name entry, leaderboard UI
                              (~2k LOC — split candidate)
  intro.py                    Once-per-launch cinematic
  powerup_help.py             In-game power-up hint overlay
  audio.py                    Procedural SFX + browser AudioContext bridge
  leaderboard.py              Supabase fetch/submit (web) / JSON (native)
  play_log.py                 Per-run telemetry POST
  _proof.py                   Tamper-evident SHA-256 chain hash
  _plausibility.py            Score-ceiling check (read + write paths)
  pillar_variants.py          8 sandstone pillar silhouettes
  pillar_kfc.py               KFC-branded pillar overlay
  ground_variants.py          Ground-texture variants
  lottery_slot.py             Slot-machine UI for the lottery power-up
  kfc_fries.py                Tilted fry sprite for KFC mode
  fries_mountains.py          KFC-themed mountain silhouettes
  dollar_coin_glyphs.py       Procedural "$" coin glyph
  dollar_variants.py          $-glyph variant explorations
  dollar_parrot_ghost.py      Ghost-parrot variant
  dollar_parrot_hat.py        Top-hat parrot variant (triple mode)
  surprise_box_variants.py    Procedural gift-box sprites
  assets/                     ONLY vendored fonts + KFC logo + sound OGGs
supabase/schema.sql           public.scores table + RLS policies
tests/test_plausibility.py    Only test file — 7 unit tests
docs/                         Screenshots + asset exploration galleries
```

## Hard rules

These are project identity. Don't violate without explicit user OK.

- **Procedural art only.** Every visual is drawn from code. No PNG
  sprite sheets. The few PNGs under `game/assets/` (KFC logo, fonts)
  are the exception; don't add more. Re-skin via code.
- **Both build targets must stay green.** Native Python desktop *and*
  pygbag/WASM browser. Branch on `sys.platform == "emscripten"` for
  audio, leaderboard, and storage paths. Never call `pygame.mixer` on
  the web path — route through `window.skyPlay`.
- **Fixed-timestep 60 FPS physics.** `GRAVITY = 1600`, `FLAP_V = -520`,
  `MAX_FALL = 700` (in `game/config.py`). Tap feel is identical across
  targets because of this. Don't switch to variable-step.
- **Comments are WHY-only.** Match the existing rationale style.
  Never line-by-line WHAT comments. Never reference the current task,
  PR, or caller in a comment.

## Power-ups (6 early-game + Surprise Box + late-game gated tier)

Early game (in the spawn roll from score 0, and the Surprise re-roll
pool): Triple (3× coins), Magnet, Slow-Mo, KFC (fry-skin), Ghost (phase
through pillars), Shrink (0.6× scale). Surprise Box re-rolls at pickup to
one of those six. Each active effect lasts 8 s. Spawn chance is 24% per
non-rush pillar (`POWERUP_CHANCE`), ramping up from 10%
(`POWERUP_CHANCE_NEWBIE`) over the onboarding ramp; min 5.5 s between
spawns (`POWERUP_COOLDOWN`). Float-text labels share a unified
gradient-fill + outline + 8-sparkle style.

More power-ups arrive in new versions — deliberately undeclared, to make
the game feel deeper than a player expects. They sit behind score
thresholds (`POWERUP_SCORE_GATES`), are kept out of the Surprise pool so
they can't bypass the gate, and some swap in for an early kind at a score
(`POWERUP_REPLACED_AT`). The full roster lives in `config.py`; keep new
power-ups gated and unannounced.

Every 15th pillar is a **Coin Rush**: gap widened 30%, ~14 coins in a
sine/S/chevron/oval/double-arc formation. No power-ups on rush pillars.

## Deploy hygiene (CI-side)

Pygbag 0.9.2 bundles every file in the directory it runs in — there
is **no include / exclude flag**. The CI workflow
(`.github/workflows/pages.yml`) stages a minimal source tree
(`main.py`, `inject_theme.py`, `pyproject.toml`, `game/`) into a
`<branch>_stage/` dir before each pygbag build, so the player-facing
`.apk` stays ~544 KB instead of pulling in `docs/`, `archive/`,
`tools/`, etc. (~33 MB before the fix).

Two guards in the same workflow:

- **Bundle-size ceiling.** The `Report bundle sizes + size guard`
  step fails the build if any branch's `.apk` exceeds **5 MB**.
  Raise the ceiling deliberately if you ship a genuine asset push
  past it; never raise it to silence a regression you don't
  understand.
- **Unit tests.** `python -m pytest tests/` runs on every branch's
  full checkout before any pygbag build. A regression to
  `test_plausibility.py` halts the deploy.

Practical rules:

- All runtime assets live in `game/assets/` (vendored fonts, KFC
  logo, OGG audio) per the long-standing convention. New sprites
  and audio belong there.
- If you ever add a **new top-level dir** the runtime imports, you
  must also update the workflow's `Stage minimal source` step.
  By convention, don't — keep it under `game/`.
- The workflow is intentionally identical on all four deploy
  branches (`main`, `v4_skybit`, `v4_skybit_powerups`,
  `v5_powerups`). Any edit needs syncing across all four — see
  the sequential checkout pattern in the session history if doing
  this by hand.

## Graphic Design Tasks

For any task that involves designing graphics — e.g. a power-up
effect/logo, parrot looks, pillar, sky, or mountains appearance — you
must ALWAYS follow these rules:

1. Always research online first to understand what's being asked — ideas,
   theme, casual-gaming references, and more.
2. Create 5 distinctive, unique versions that you believe align with the
   task. Build them for review BEFORE adding anything to the actual game.
3. Commit the 5 versions as ONE image to git (including the original
   design, if one exists), so the uploaded image holds every version for
   the developer to review.
4. Be your own critic: if the designs don't meet a high bar for
   exceptional work and design, fix them and iterate until they do.
5. Only when finished, add the final image to git for the user to review.
6. You never add images inline in chat — always add a link to it on git.

The `graphics-designer` subagent enforces this workflow; the
`sound-designer` subagent follows an analogous candidate-based approach
for audio. Delegate design work to them.

## Subagents

Project subagents ship in `.claude/agents/` and load automatically in
every session (cloud + local); each is auto-delegated by its
`description`:

- `graphics-designer` (opus) — procedural visual design; enforces the
  Graphic Design Tasks workflow above.
- `sound-designer` (opus) — dual-backend SFX; never `pygame.mixer` on the
  web path.
- `gaming-experience-tester` (sonnet) — read-only QA for feel, balance,
  power-ups, scene flow, and both build targets.
