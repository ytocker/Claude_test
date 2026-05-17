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

`v4_skybit` is the canonical line. Topic branches off it:
`v4_skybit_game_design`, `v4_skybit_game_graphics`,
`v4_skybit_menu_redesign`, `v4_skybit_summary`. Earlier `v3_skybit_*`
branches are historical. `main` and `gh-pages` are deployment artifacts.

When starting work, check out (or branch off) `v4_skybit` unless the
user specifies otherwise. The current working tree on
`claude/organize-project-structure-wivHq` is intentionally stripped
down — it is NOT representative of the project. Read the real layout
from `v4_skybit`.

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
- **Reverse power-up stays disabled.** Implementation is intact but
  excluded from `POWERUP_WEIGHTS` and the Surprise Box pick. Don't
  re-enable.
- **Anti-cheat caveat stays honest.** The README's "soft leaderboard"
  paragraph must match reality. If validation isn't actually
  server-side, don't delete the caveat.
- **Comments are WHY-only.** Match the existing rationale style.
  Never line-by-line WHAT comments. Never reference the current task,
  PR, or caller in a comment.
- **No grind-gated difficulty.** Meta-progression (if added) unlocks
  cosmetics only. Never hide harder gaps behind playtime.

## Out of scope (don't burn tokens on these)

- Controller/gamepad support
- Story/cutscene/narrative layer
- Multiplayer/co-op
- Engine port off Pygame
- Re-enabling Reverse

## Power-ups (6 active + Surprise)

Triple (3× coins), Magnet, Slow-Mo, KFC (fry-skin), Ghost (phase
through pillars), Grow (1.3× scale), Surprise Box (re-rolls to one of
the six at pickup). Each lasts 8 s. 14% spawn chance per non-rush
pillar, 5.5 s cooldown. Float-text labels share a unified
gradient-fill + outline + 8-sparkle style.

Every 15th pillar is a **Coin Rush**: gap widened 30%, ~14 coins in a
sine/S/chevron/oval/double-arc formation. No power-ups on rush pillars.

## Anti-cheat (client-side hardening)

- One closure-private dispatcher: `window.__sk(action, payload)`
  (`inject_theme.py`). No `window.lbSubmitStart` etc. globals.
- Per-run UUID + append-only event ledger + rolling SHA-256 chain
  (`game/_proof.py`). JS recomputes and refuses on mismatch.
- Submitted score = ledger sum, not `world.score`. Poking
  `world.score = 99999` doesn't move the wire value.
- Plausibility ceiling (`game/_plausibility.py`) runs on submit AND
  on read — implausible rows hide from the displayed top-10.
- Dispatcher tracks consumed run UUIDs; replays rejected.

Known gap: Supabase anon key + permissive RLS still ship in the
bundle. A motivated attacker can `curl` the table directly. Moving
`_plausibility.check` into a Supabase Edge Function with tight RLS is
the priority anti-cheat upgrade — see `UPGRADE_BRIEF.md`.

## Where to find more

- **`REVIEW.md`** (on `v4_skybit`) — full 12-category review with
  justifications, scores, references.
- **`UPGRADE_BRIEF.md`** (on `v4_skybit`) — prioritized upgrade
  actions with target files + constants.
- **`README.md`** (on `v4_skybit`) — player-facing docs and
  procedural-art notes.

## Session hygiene

- One feature branch per topic, named for the work. The branch name
  is the chat's label in the web UI.
- Stripped-down branches like `claude/organize-project-structure-*`
  are not the project — always sanity-check against `v4_skybit`.
- This file is the durable context. Add new hard rules here rather
  than re-explaining them in every chat.
