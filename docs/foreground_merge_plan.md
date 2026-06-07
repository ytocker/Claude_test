# Foreground integration plan — "Living Promenade" (pale-buff sidewalk) → live game

**Target branch:** `v5_skybit_merge_graphics` (branch off `v5_skybit`).
**Goal:** port the SHIP-READY buff-sidewalk foreground (floor + embedded surface detail +
promenade props/characters + near/front activity lane + day→night performances) from
exploration into the live `game/`, additively.

This is an implementation handoff. The design is finished and validated; this doc explains
exactly **what to copy, where to hook it in, and what to change** to make it run live at 60 fps
on both build targets.

---

## 1. Source of truth (where the finished code + art live)

All on branch **`claude/skybit-graphics-sky-variant-eTxX7`** (NOT on `v5_skybit` — copy from
there):

- Code: `archive/foreground_redesign/`
  - `foreground_grounded.py` — floor painters + all shared scaffolding/helpers.
  - `ground_detail_r18.py` — embedded surface detail layer.
  - `sidewalk_props_r15.py` — promenade props + `_world_xs` + glow system.
  - `promenade_r17.py` — promenade characters (kids, old-man, kiosk, flock, strollers, campfire, napper).
  - `near_lane_r19.py` — near/front lane + the four performances.
  - `render_buff_preview.py`, `render_foreground_r19.py` — review harnesses (reference only).
- Galleries (the look to match): `docs/foreground_redesign/round_19.png` (3 bases × 4 phases,
  full stack) and `docs/foreground_redesign/round_20_buff.png` (the chosen pale-buff base with
  the full stack, day→night).
- Key commits: round-19 `3e03b8e` (lion rebuild + night-cap) and `55b6734` (polish); buff
  preview `1b90e9a`.

**Chosen base:** pale-buff sandstone running-bond (`fg_swatch_buff_running_bond`). The other
two finalists (terracotta, honey flagstone) and the painters for them come along for free and
can be kept as alternates.

---

## 2. Decisions already made (do not re-litigate)

1. **Base = pale buff** (`fg_swatch_buff_running_bond`). It replaces the grass floor.
2. **Ambient reconciliation = ADDITIVE.** Keep the existing random ground ambient
   (`game/ambient.py` dog/sheep/bench/etc.) running AND add the promenade on top.
   - Known risk: duplicate dog/sheep on screen at once. Optional, low-risk mitigations the
     implementer MAY apply (not required): lower `_GROUND_EVENT_SPAWN_RATE`, or have the
     promenade skip re-instantiating the dog/sheep it borrows. Leave both running by default;
     flag for QA.

---

## 3. Live hooks (verified against the live game)

- **Injection point:** `game/scenes.py`, `PlayScene._render()`, immediately AFTER the
  `draw_ground(...)` call (~line 1002), BEFORE pipes/coins/bird. Everything drawn after the
  injection (pillars, coins, bird, weather, HUD) correctly layers on top.
- **Per-frame inputs available there:**
  - scroll: `self.world.bg_scroll` (float px; updated in `world.py:865`). World-space; pillars
    and ground already scroll off this.
  - palette: `self.world.biome_palette` (dict).
  - phase: `self.world.biome_phase` (float 0..1, continuous day cycle).
  - elapsed: `self.world.biome_time` (float seconds) — use as the animation clock `t`.
  - cycle length: `biome.CYCLE_SECONDS = 320`.
- **Palette keys:** the live `game/biome.py` palette already provides every key the painters
  read — `sky_top/sky_mid/sky_bot`, `horizon`, `ground_top/ground_mid`, `stone_light/mid/dark/
  accent`, `foliage_top/mid/dark/accent`, `star_alpha`. **No adapter needed.**
- **Constants:** `W=360`, `H=640`, `GROUND_Y=595` already in `game/config.py`. Fixed 60 fps.

---

## 4. Port manifest — new modules under `game/`

Keep everything under `game/` (no new top-level dir, so the CI `Stage minimal source` step is
unchanged). Procedural only — no new assets.

### `game/sky.py` (or add to `game/config.py`) — the ONLY external archive dep (~50 LOC)
Port from `archive/pillar_redesign/`:
```python
NIGHT_LUMA_CAP = 153
def _is_dark_sky(pal) -> bool:
    r, g, b = pal.get('sky_top', (60, 120, 200))
    return (0.2126*r + 0.7152*g + 0.0722*b) <= 95
def _clamp_night(color, alpha=255):
    r, g, b = color[:3]
    return (min(r, NIGHT_LUMA_CAP), min(g, NIGHT_LUMA_CAP), min(b, NIGHT_LUMA_CAP), alpha)
```

### `game/foreground.py` ← `foreground_grounded.py` + `ground_detail_r18.py`
Copy the REUSABLE painters/helpers:
- Colour/scatter/plane helpers: `_clamp/_mix/_shade/_luma/_sat/_nightf/_horizon`, `_scatter`,
  `_flat_slab/_perspective_y/_grain_tiles/_apply_grain/_apply_grain_scroll`, `_premium_base_v8`,
  `_spec_dab`.
- Tone helpers: `_buff_body` (+ `_clay/_paver_cool_body/_honey_body` if keeping alternates),
  `_brick_tones`, `_running_bond_courses`.
- Floor painter: **`fg_swatch_buff_running_bond`** (+ optional alternates
  `fg_brick_running_bond`, `_cool`, `fg_swatch_honey_flagstone`).
- Embedded detail: `add_embedded_detail` + the 7 detail painters `_cracks/_weeds/_moss/_litter/
  _medallion/_grate/_damp`, plus `_nretint/_cap_hi/_course_edges/_bond_layout/_mid_band/_tones/
  _body_for`. Replace the `_base_kind(floor_painter)` identity dispatch with an explicit `kind`
  string argument (the live game knows it's "buff").

### `game/foreground_promenade.py` ← `sidewalk_props_r15.py` + `promenade_r17.py`
- Props + placement + glow: `_world_xs`, `_cap150`, `_lit_intensity`, `_glow`, `_warm_glow`,
  `_add_lamp_glow`, faint-catenary helpers, `_draw_bench/_draw_planter/_draw_lamp_post/
  _draw_lantern_head/_draw_glass_head/_draw_lantern_garland/_draw_fairy_lights/_draw_cairn/
  _draw_barrel/_draw_vine_trail`, lane helpers `_ground_clear/_post_ok`.
- Characters: `draw_kids/draw_old_man/draw_flock/draw_strollers/draw_kiosk/_pagoda_roof/
  draw_campfire/draw_napper/_draw_bench_person/_retint_person`.
- Keep its `game/` imports as-is (they already point at live modules): `game.ambient`
  (`_RunningDog/_WishingWell/_Bench/_Napper`, `_build_bench_sprite`), `game.pillar_variants`
  (`draw_prayer_flags/draw_cairn/draw_cascading_vine`), `game.draw.draw_side_shrub`.

### `game/foreground_near_lane.py` ← `near_lane_r19.py`
- Performers: `_perf_body/_watch_arc/_seated_spectator/_gathered_crowd/perf_juggler/
  perf_musician/perf_stilt/perf_lion_dance`.
- Near decor + scaling: `_near_planter/_near_pine/_near_vine_lantern/_near_brazier/_near_banner/
  _near_dog/_scaled_cast`, caps `_cap_lum/_fang_ivory/_lip_ivory/_warm_ivory_cap`, `_near_glow`,
  placement `_near_xs/_tall_ok`. Constants: `NEAR_GROUND_Y=638`, `NEAR_MULT=0.35`.
- Keep its `game/` imports: `game.ambient._RunningDog`, `game.draw.draw_side_shrub/
  draw_wuling_pine`, `game.pillar_variants.draw_cascading_vine/draw_paper_lantern/draw_cairn/
  draw_darchog_pole/draw_incense_smoke`.

### DROP (harness-only — do NOT port)
`phase_day/phase_golden/phase_dusk/phase_night` dispatchers (all 3 files), `_stepped`,
`_clamp_pillar_base_trim`, the harness `_char_x_ok`, `_general_pedestrians/_general_greenery`,
demo floor painters (`fg_beach_*`, mosaic/cobble/dune/riverbank demos), every `render_*.py`, and
the fixed cream-pagoda + clouds + parrot/coin review actors (the live game supplies its own
pillars, clouds, bird, coin).

---

## 5. New live composition logic (replaces the discrete harness beats)

The review harness drew four discrete cells (`phase_day/golden/dusk/night`). The live game has a
**continuous** `phase` (0..1), so write three public entry points that select composition by the
live biome phase windows (mirror `game/ambient.py` phase-window style):

```python
# game/foreground.py
def draw_foreground_floor(surf, scroll, pal):
    fg_swatch_buff_running_bond(surf, W, GROUND_Y, H, scroll, pal)
    add_embedded_detail("buff", surf, W, GROUND_Y, H, scroll, pal)

# game/foreground_promenade.py
def draw_promenade(surf, scroll, pal, phase, t):
    # far-lane props + cast; density/lighting escalate sparse(day) -> festival(night).
    # day/night look already follows `pal`; pick which props/characters by `phase`.

# game/foreground_near_lane.py
def draw_near_lane(surf, scroll, pal, phase, t):
    # near decor + the ACTIVE performance, selected by phase window:
    #   juggler  ~ day      (phase ~0.90–0.15, wraps 0)
    #   musician ~ golden   (phase ~0.10–0.25)
    #   stilt/prep ~ dusk   (phase ~0.36–0.55)
    #   lion dance ~ night  (phase ~0.55–0.72)
```
- Animate all characters from `t = world.biome_time` (the gait helpers already take `t`).
- Map the four harness beats onto the live 8 keyframes in `game/biome.py`; tune the windows so
  one performance is active at a time with brief gaps, like the ambient scheduler.

---

## 6. Wiring (`game/scenes.py` `PlayScene._render`, ~line 1002)

```python
# BEFORE: draw_ground(surf, GROUND_Y, W, H, scroll, palette['ground_top'], palette['ground_mid'], (60,40,25))
# REPLACE the grass floor with the buff sidewalk, then add the promenade layers:
foreground.draw_foreground_floor(surf, self.world.bg_scroll, self.world.biome_palette)
foreground_promenade.draw_promenade(surf, self.world.bg_scroll, self.world.biome_palette,
                                    self.world.biome_phase, self.world.biome_time)
foreground_near_lane.draw_near_lane(surf, self.world.bg_scroll, self.world.biome_palette,
                                    self.world.biome_phase, self.world.biome_time)
# (pipes, coins, bird, weather, HUD already drawn after this — unchanged)
```
- **The buff sidewalk REPLACES the grass `draw_ground`** (the sidewalk IS the floor). Reconcile/
  retire the grass `ground_variants` decorations (hero blades, flowers, accent bugs). Confirm no
  other caller depends on `draw_ground` for the play floor (menu/HUD use `draw_mountain`, not the
  play ground).
- **Leave `world.ambient` AS-IS** (additive). Both the random ambient ground events and the
  promenade run.

---

## 7. Live-world anchor adaptation (the harness assumed a FIXED pillar)

- **Keep** bird-column clearance (`BIRD_X≈90`) for TALL near props (banner pole, lion head,
  stilt-walker) so they don't block the player's view of the bird.
- **Drop** the harness fixed-pillar-lane gating (`_PILLAR_LANE` x≈212–320): live pillars scroll
  and are drawn on top of the foreground, so no fixed exclusion is needed.
- Scroll anchoring is already world-space (`x = world_x - scroll*mult`). Pass live `bg_scroll`;
  keep the mults (near lane 0.35, props 0.20, `_scatter` speeds). Verify no seam at wrap with two
  scroll values.

---

## 8. Both build targets + deploy hygiene

- Visual-only / pygbag-safe: the whole stack uses only `fill/blit/draw.*/SRCALPHA/
  BLEND_RGB_ADD/transform.scale` — no `pygame.mixer`, no numpy, no `sys.platform` branches. Safe
  on native + web.
- New modules under `game/` → the CI `Stage minimal source` step needs NO change.
- Procedural (~4.8k LOC, no assets) → the player `.apk` stays far under the 5 MB ceiling.
- `tests/test_plausibility.py` untouched. Optional: add a headless smoke test that imports the
  modules and renders one frame at each phase (`SDL_VIDEODRIVER=dummy`).

---

## 9. Performance

- Already cached (keep): grain tiles (`_grain_tiles`), warm-glow halos (`_warm_glow`), and the
  ambient sprite builders (`_build_*_sprite`).
- ADD: cache the near-lane scaled sprites — `_scaled_cast` currently `transform.scale`s to a
  scratch surface per call; memoize by (cast_fn, scale, frame) or pre-scale once.
- Target a stable 60 fps on native and web; profile one frame in each phase.

---

## 10. Risks / interactions to verify

- **KFC mode** (kfc pillars + fries mountains): ensure the buff sidewalk still reads under KFC
  visuals; consider a KFC tint if it clashes.
- **Coin Rush / weather** (rain/fog draw AFTER the foreground — fine; confirm fog density still
  reads), **slow-mo** (animations via `biome_time` slow with the world — acceptable),
  **magnet/lottery overlays** (drawn after — fine).
- **Grass-floor retirement:** confirm nothing else relies on the old play-ground decorations.
- **Additive ambient:** watch for duplicate dog/sheep; apply a mitigation from §2 if it reads as
  a bug.

---

## 11. Implementation checklist

1. Branch `v5_skybit_merge_graphics` off `v5_skybit`.
2. Copy the source modules from `claude/skybit-graphics-sky-variant-eTxX7` (§1) and split into
   `game/foreground.py`, `game/foreground_promenade.py`, `game/foreground_near_lane.py`,
   `game/sky.py` per the manifest (§4); drop harness-only code.
3. Add the three public entry points (§5).
4. Wire them into `game/scenes.py` (§6); retire the grass floor.
5. Adapt anchoring (§7); keep ambient additive (§2).
6. Verify (§12); tune phase windows so the day→night escalation + performance rotation match
   `round_20_buff.png` / `round_19.png`.

---

## 12. Verification

- **Native:** `python main.py` — over the 320 s biome cycle, see the buff sidewalk + embedded
  detail + promenade + near-lane performances escalate day→night; the coin + bird stay on top and
  brightest at night; 60 fps.
- **Web:** pygbag build green; same visuals; `.apk` < 5 MB.
- **Tests:** `python -m pytest tests/` green.
- **Match the target look:** compare against `docs/foreground_redesign/round_20_buff.png`
  (buff base, full stack) and `round_19.png`.
