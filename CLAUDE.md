# CLAUDE.md — Skybit project memory

This file is loaded by Claude Code at the start of every session in this
repo. Keep it tight: project shape, hard rules, and pointers to deeper
docs. Long-form rationale lives in `REVIEW.md` and `UPGRADE_BRIEF.md`
on `v4_skybit`.

## What this is

**Skybit — Pocket Sky Flyer.** A one-button Flappy-style casual arcade
game. Python 3.11+ / Pygame 2.x. Ships two build targets from the same
source: native desktop and pygbag/WASM in a browser. ~13k LOC Python.

## Active development branch
'main' is the deployed version. currently is based on 'v4_skybit'.
R&D activity is done on 'v5_skybit', and it will be te next deployed version.
from v_5 skyit there are many forked varions, each handling a different aspect of the game that will
be upgraded in formal version, such as - powerups, weather events, general graphics etc.
`main` and `gh-pages` are deployment artifacts.

When starting work, check out (or branch off) `main` unless the
user specifies otherwise. The current working tree on
`claude/organize-project-structure-wivHq` is intentionally stripped
down — it is NOT representative of the project.

## Run

```bash
pip install pygame
python main.py
```

Web build is driven by pygbag; entry point branches on
`sys.platform == "emscripten"`.

## Code map (on `v4_skybit`)

```
main.py                       Entry — sync + async for pygbag
inject_theme.py               JS bridge injected into the WASM bundle
                              (closure-private window.__sk dispatcher)
game/
  config.py                   Physics, spawn rates, durations, weights
  scenes.py                   Scene state machine + App + tap cooldown
  world.py                    Simulation: scroll/spawn/collision/FX
  entities.py                 Bird, Pipe, Coin, PowerUp, Particle,
                              FloatText (1.6k LOC — split candidate)
  parrot.py                   4-frame macaw + KFC/ghost/hat/grow variants
  draw.py                     Gradient surfaces, glow caches, terrain
  hud.py                      Score, timers, name entry, leaderboard UI
  intro.py                    Once-per-launch cinematic
  biome.py                    Day/night palette interpolation (5 min cycle)
  weather.py                  Rain/fog/thunder per biome phase
  audio.py                    Procedural SFX + browser AudioContext bridge
  leaderboard.py              Supabase fetch/submit (web) / JSON (native)
  play_log.py                 Per-run telemetry POST
  _proof.py                   Tamper-evident SHA-256 chain hash
  _plausibility.py            Score-ceiling check (read + write paths)
  pillar_variants.py          8 sandstone pillar silhouettes
  kfc_fries.py                Tilted fry sprite for KFC mode
  dollar_coin_glyphs.py       Procedural "$" coin glyph
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


## Power-ups (6 active + Surprisebox + late game undeclared ones)

Triple (3× coins), Magnet, Slow-Mo, KFC (fry-skin), Ghost (phase
through pillars), Shrink (0.6× scale), Surprise Box (re-rolls to one of
the six at pickup). Each lasts 8 s. 14% spawn chance per non-rush
pillar, 5.5 s cooldown. Float-text labels share a unified
gradient-fill + outline + 8-sparkle style.

More powerups are added during new versions, deliberately ones that are not declared beforehand, 
in order to surprise the user and make him feel the game has much more depth than he might expect.

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


## Graphic Design Tasks ##
- For any task you are given that includes to design so graphics - for instance - powerup effect/logo,
parrot looks, pillar, sky, mountains appearance, etc. You must follow these rules ALWAYS:
1. Always research online in order to understand better what you are asked for. this includes ideas, theme, casual gaming references, and more.
2. Create 5 distinctive and unique versions, that you believe align with the task. the versoins should be created
before adding in code to the actual game, for review purposes.
3. the 5 versions should be added as 1 image to git, including the original design (if such exists), so the uploaded image contains all versions for further review to the developer.
4. You are your own critique for th work you did - if the designs do not meet high standards of exceptional work and design,
then fix and change the designs accordign to your review. iterate until perfection.
5. only when done, add the final image to git for the user to review
6. you never add images to the chat inline. always add a link to it on git
