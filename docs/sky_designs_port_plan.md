# Porting the 10 biome sky designs into `game/` as a dormant registry

**Audience:** an implementing agent on a target branch (likely without the `archive/` tree).
**Goal:** bring the **10 biome sky designs** from the final exploration round into the live `game/`
package as **dormant** code — present, importable, and renderable, but with the **active in-game sky
completely unchanged**. Scope is locked to the **sky color field only** — no ridges / structures /
ground / foliage from the original biome scenes.

The reference sheet is `docs/biome_redesign/round_7_all_skystars_daynight.png`: 10 rows (one per
biome design) × 10 day/night stage columns. Each design is a **continuous day/night cycle** driven by
`phase` (0..1), sampled in the sheet at the named stages predawn → dawn → sunrise → morning → midday
→ afternoon → golden → sunset → dusk → night.

This document is self-contained: it names every source file, the exact modules to create, the
dormancy guarantee, and a verification checklist. Nothing here changes gameplay.

---

## 1. Where the designs live today (source of truth)

The biome designs currently exist **only** in the exploration area, on branch
**`v5_skybit_background_graphics_sky`** (the graphics merge line), under `archive/biome_redesign/`. A
target branch may not contain `archive/` at all, so the port must copy these files across from that
branch.

### The 10 biome designs
`archive/biome_redesign/biome_variants.py`
- `BIOMES` — the id → `BiomeSpec` map, in sheet order:
  `desert_mesa`, `alpine_snowpeak`, `volcanic_caldera`, `karst_watertown`, `autumn_highlands`,
  `misty_gorge`, `snow_temple`, `maple_monastery`, `cloud_sea_peaks`, `moonlit_pine_cliff`.
- `BIOME_NAMES` / `BIOME_NOTES` — human names ("Desert Mesa", "Alpine Snowpeak", …) and notes.
- `STAGES` — the 10 named day/night sample points used by the render sheet.
- `GROUP_A` / `GROUP_B` — exploration grouping metadata (used only for sheet section bands).
- Per-biome keyframe lists (`_DESERT_KF`, `_ALPINE_KF`, …). Each keyframe is `(phase, dict(...))`
  whose **sky-relevant keys are `sky_top`, `sky_mid`, `sky_bot`, `horizon`, `star_alpha`**; the dicts
  also carry `mtn_*`, `struct_*`, `ground_*`, `foliage_*` keys that are **out of scope** here.

### The sky painter
`archive/biome_redesign/scene_engine.py`
- `BiomeSpec` dataclass and the sky-only painter
  `paint_sky(surf, spec, w, h, phase, stars=False, ground_y=None)`.
- It imports `import sky_field as sf` (the biome sky engine below — **distinct from
  `game/sky_field.py`**) and three helpers
  `from game.draw import make_gradient_surface, lerp_color, make_glow_surface`.
- `scene_engine.py` also defines `paint_scene`, `draw_ridge`, and other structural drawers — **all
  out of scope**; do not port them.

### The sky engine
`archive/biome_redesign/sky_field.py`
- The biome-family OKLab sky engine (perceptual ramp + dithering). **Name collides** with the
  existing `game/sky_field.py`; it must be renamed on copy (see §2.2).

### Out of scope — do NOT port
- `archive/biome_redesign/biome_motifs.py` — structure/ridge motif drawers (full-scene only).
- `paint_scene` and every structural drawer inside `scene_engine.py`.

### Look reference (for visual QA)
`docs/biome_redesign/round_7_all_skystars_daynight.png`.

---

## 2. What to create under `game/`

No new top-level directory is introduced, so the CI `Stage minimal source` step and the 5 MB
`.apk` ceiling are unaffected. Everything is pure-Python and pygbag-safe (the OKLab engine is
bake-path only: no numpy / surfarray / native calls).

### 2.1 `game/biome_sky_field.py` ← copy `archive/biome_redesign/sky_field.py`
Renamed copy of the biome sky engine, to avoid the collision with the existing `game/sky_field.py`.
Update any internal self-references accordingly.

### 2.2 `game/biome_sky.py` ← extract the SKY path from `archive/biome_redesign/scene_engine.py`
Copy **only** `BiomeSpec` (plus the small dataclasses it nests, e.g. the sky-stop spec) and
`paint_sky`, plus any tiny helper they require. **Drop** `paint_scene`, `draw_ridge`, and every
structural drawer. Fix imports:
- `import sky_field as sf` → `from game import biome_sky_field as sf`
- keep `from game.draw import make_gradient_surface, lerp_color, make_glow_surface`.

### 2.3 `game/biome_sky_keyframes.py` ← from `archive/biome_redesign/biome_variants.py`
Port the 10 per-biome keyframe tables, the `BIOMES` ids, `STAGES`, and `BIOME_NAMES` / `BIOME_NOTES`.
**Sky-only:** strip each keyframe dict down to `sky_top`, `sky_mid`, `sky_bot`, `horizon`,
`star_alpha` (cleanest, matches scope). Leaving the extra scene keys in is harmless — `paint_sky`
ignores them — but stripping keeps the dormant code honest to "sky color field only." `GROUP_A` /
`GROUP_B` are optional (sheet-only metadata); keep them if convenient. Do **not** import
`biome_motifs`.

### 2.4 `game/sky_designs.py` — the one new hand-written file (the dormant registry)
A single catalog over the 10 biome designs, behind one signature:

```
render(surf, w, h, ground_y, palette, phase) -> None
```

Each entry binds `spec = BIOMES[id]` and calls
`paint_sky(surf, spec, w, h, phase, stars=True, ground_y=ground_y)`. These designs carry their
**own** per-biome day/night palettes via keyframes, so they ignore the live `palette` and key off
`phase` (0..1) — same `phase` the live biome clock already produces.

Expose:
- `CATALOG = [(design_id, human_name, note, render_fn), …]` — the **10** biome designs in sheet
  order.
- `ACTIVE_SKY_DESIGN = None` — the dormant switch (see §3).
- `render_active(surf, w, h, ground_y, palette, phase) -> bool` — returns `False` immediately when
  `ACTIVE_SKY_DESIGN is None` (so a future caller can fall through to the live path); otherwise looks
  up the catalog entry and renders it, returning `True`.

This module follows the existing **preview-only** convention already used by
`game/dollar_variants.py` and `game/surprise_box_variants.py`: it ships in the package but is
imported by nothing on the live render path.

---

## 3. Dormancy guarantee (do NOT change gameplay)

The active in-game sky is the current shan-shui ink-wash background and must stay byte-for-byte the
same. Touch **none** of the live sky path:
- `game/biome.py` — `_KEYFRAMES`, `palette_for_phase`
- `game/draw.py` — `get_sky_surface_biome`, the `_bg_cache`
- `game/scenes.py` — `App._draw_background` (≈ lines 952–1003)
- `game/world.py`

`game/sky_designs.py` must be imported by nothing on the live path. Leave a **documented but
unwired** activation seam so a future change can flip a design on with one line — e.g. in
`App._draw_background`:

```
# Future hook — intentionally not wired; ACTIVE_SKY_DESIGN is None so gameplay is unchanged.
# if sky_designs.ACTIVE_SKY_DESIGN and sky_designs.render_active(surf, W, H, GROUND_Y, palette, phase):
#     return
# ... existing live sky path ...
```

Do **not** add the call now. The registry stays inert until someone deliberately sets
`ACTIVE_SKY_DESIGN`.

---

## 4. Build-target & hygiene notes

- Both targets stay green: pure Python, no `pygame.mixer`, no native/numpy. The sky engine bakes on
  the cache-miss path only.
- All new files live under `game/`, so the CI `Stage minimal source` step needs no edits and the
  `.apk` size guard (5 MB) is unaffected — the designs are procedural with no new assets.
- `tests/test_plausibility.py` is untouched.

### Optional dev preview (a suggestion only — not part of the live game)
If a headless catalog sheet is useful, repoint the existing exploration render script
(`archive/biome_redesign/render_biome_variants.py`) at the new `game/` modules, or add a small
standalone `tools/preview_sky_designs.py`. This is a dev aid; the game must not import it.

---

## 5. Verification checklist

1. **Imports resolve, catalog complete:**
   `python -c "import game.sky_designs as s; print(len(s.CATALOG))"` → **10** designs, no import
   errors (proves every engine dependency is wired and nothing still points at `archive/`).
2. **Every design paints across the cycle:** render the 10 designs headless over the `STAGES` phases
   to a sheet and compare against `docs/biome_redesign/round_7_all_skystars_daynight.png`.
3. **Gameplay unchanged:** run `python main.py` (native) and the pygbag build — the live sky is
   visually identical to before, 60 fps, `ACTIVE_SKY_DESIGN is None`.
4. **Tests + bundle:** `python -m pytest tests/` is green; the pygbag `.apk` stays under 5 MB.
