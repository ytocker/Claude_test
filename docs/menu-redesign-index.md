# Main-menu redesign — showcase index

Every comparison figure produced during the main-menu redesign effort
(19–22 Aug 2026), in the order it was made. All links point at this branch,
`claude/menu-buttons-redesign`.

**Outcome: the shipped menu stands.** No `game/*.py` file was changed by this
effort — everything below is exploration. The rounds are kept because each one
established something the next depended on.

## Reference frames

| Figure | What it is |
|---|---|
| [`current_ingame.png`](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/main-menu/current_ingame.png) | The live shipped menu, rendered from `hud.draw_menu`. The baseline every round is judged against. |
| [`menu_buttons/original.png`](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/menu_buttons/original.png) | Same screen, captured at the start of round 1. |
| [`launch-perch/base_v1.png`](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/main-menu/launch-perch/base_v1.png) | The accepted `launch-perch` design, frozen so later variants forked from a fixed point. |

## Round 1 — buttons only, novelty-first

[**showcase.png**](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/menu_buttons/showcase.png)

Five treatments of the bottom button cluster: `docked-deck`, `hero-secondary`,
`sky-rail`, `poster-clean`, `perch-rail`. Optimised for distinctiveness.
Rejected — did not improve usability.

## Round 2 — buttons only, usability-first

[**showcase_v2.png**](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/menu_buttons/showcase_v2.png)

`thumb-slab`, `value-ladder`, `stone-plinth`, `tab-slab`, `max-primary`, driven
by thumb-reach and tap-target maths. Established the rule that START belongs
lowest, closest to the thumb.

## Round 3 — full screen

| Figure | What it shows |
|---|---|
| [`showcase_pre_anchor_fix.png`](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/main-menu/showcase_pre_anchor_fix.png) | First cut of `launch-perch`, `dispatch-board`, `sky-window`, `courier-card`, `pip-hello` — before Pip was pinned to his real spawn point. |
| [`showcase.png`](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/main-menu/showcase.png) | The same five after the anchor fix. |
| [`showcase_combined.png`](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/main-menu/showcase_combined.png) | Both rows together, before over after. |
| [`showcase_selected.png`](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/main-menu/showcase_selected.png) | The six picked out of those two rows, plus the in-game reference. |

The anchor fix mattered because the menu draws the **live** `world.bird`, and a
fresh `Bird` respawns at the same coordinates when START is tapped — so any
design that moved Pip caused a visible pop into gameplay.

## Round 4 — evolutions of the accepted design

| Figure | What it shows |
|---|---|
| [`perch-evolutions/showcase.png`](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/perch-evolutions/showcase.png) | Five descendants of `launch-perch`: `dock-descent`, `launch-catapult`, `sky-balloon`, `post-tower`, `launch-bench`. |
| [`balloon-ladder/showcase.png`](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/perch-evolutions/balloon-ladder/showcase.png) | Three ways to resolve "balloon raised, its base is START, ladder below": `basket-start`, `gondola-ladder`, `mooring-dock`. |

## Round 5 — themed, at the store-hub quality bar

[**menu-v2/showcase.png**](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/menu-v2/showcase.png)

Three full art directions — *The Dispatch Seal*, *The Launch Bulletin*,
*Last Light on the Pass*. Per-concept sheets carry four biome phases plus a
greyscale thumbnail:
[one-button](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/menu-v2/one-button/round_2.png) ·
[cover-type](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/menu-v2/cover-type/round_2.png) ·
[first-light](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/menu-v2/first-light/round_2.png)

Rejected: beautifully made, but unrelated to the game's visual style.

## Round 6 — the game's own visual language

[**menu-v3/showcase.png**](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/menu-v3/showcase.png)

`lantern-street` and `the-gap`, composed from the game's *existing* world —
`pillar_pagodas`, `mountains_v14`, `cloud_variants`, `foreground_floor`, the
promenade — rather than an invented one. Per-concept sheets:
[lantern-street](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/menu-v3/lantern-street/round_1.png) ·
[the-gap](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/menu-v3/the-gap/round_1.png)

Rejected: close enough to the shipped menu that they didn't earn the change.

## Detail figures

| Figure | What it shows |
|---|---|
| [`shadow_before_after.png`](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/main-menu/launch-perch/shadow_before_after.png) | Shadows retuned to Material's opacity budget, sky-tinted instead of black, with real falloff. |
| [`settings_fix.png`](https://github.com/ytocker/skybit/blob/claude/menu-buttons-redesign/docs/main-menu/launch-perch/settings_fix.png) | The SETTINGS label overflowing its plank, and the fix (2× crop). |

## Findings worth keeping

Defects the audits turned up in the **shipped** menu. Fixed once, then reverted
for later timing — the work is preserved at commit `a38dad57` and restores with
`git cherry-pick a38dad57`.

- **The menu shows the wrong Pip.** `_sync_bird_cosmetics` runs only at run
  start, so a fresh launch always shows `skin_base` regardless of what the
  player owns, and a skin equipped in the store doesn't appear until the next
  run. The `World` is never rebuilt on menu entry either, so a failed run can
  leave a *dead* Pip on the menu — `Bird.draw` blits the death palette whenever
  `death_fade_t > 0`, and nothing resets it outside `Bird.__init__`.
- **The menu drives a finished run's spawner.** `world_idle_tick` keeps calling
  `_spawn_pipe`, which advances the dead run's clown lead-in, can construct a
  `ClownEvent`, and inflates `coins_spawned`. Invisible only because the next
  run discards the object.
- **The mountain silhouette is off-palette.** `_draw_mountain_silhouette` draws
  hardcoded `(14,26,12)` / `(10,18,8)` greens copied from an old welcome-screen
  SVG — they come from no biome palette and match nothing else on screen.
- **`hud._outlined_text` isn't phase-proof at the top of the screen.** At y110
  both the gold fill and the `_RED_OUTLINE` measure ~2:1 against `sky_top`.
- **`_dark_panel` is documented as canonical but has zero call sites.**
- **`intro.py:204` seeds sprite RNG with `hash()`**, which Python salts per
  process, so the sky-house renders slightly differently every launch.
