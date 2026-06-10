# Porting the Skybit sky designs into `game/` as a dormant registry

**Audience:** an implementing agent on a target branch (likely without the `archive/` tree).
**Goal:** bring **all three families** of explored background-SKY designs into the live `game/`
package as **dormant** code — present, importable, and renderable, but with the **active in-game sky
completely unchanged**. Scope is locked to **sky color field only** — no signature ridges /
structures / ground / foliage from the original scene explorations.

This document is fully self-contained: it names every source file, the exact modules to create, the
dormancy guarantee, and a verification checklist. Nothing here changes gameplay.

---

## 1. Where the designs live today (source of truth)

All three families currently exist **only** in the exploration area, on branch
**`v5_skybit_background_graphics_sky`** (the graphics merge line). A target branch may not contain
`archive/` at all, so the port must copy these files across from that branch.

### Family A — OKLab color-field treatments (5)
`archive/sky_redesign/field_variants.py`
- Functions: `draw_deep_space`, `draw_hiroshige_bokashi`, `draw_belt_of_venus`, `draw_alto_plum`,
  `draw_atmospheric_true` — each `(w, h, palette) -> pygame.Surface`.
- Registry dict `{name: fn}` plus a names/notes table (around line 277).
- Imports `from game.sky_field import …` — **the engine is already in `game/`** (see §2.0).
- Each treatment derives a richer 5–7 stop OKLab ramp from the four existing biome palette anchors
  (`sky_top`, `sky_mid`, `sky_bot`, `horizon`), so time-of-day arrives through `palette`; there is
  no `phase` argument.

### Family B — Shan-shui / ink-art candidate skies (~10)
`archive/sky_redesign/sky_variants.py`
- Functions: `draw_sky_ruyi_strata`, `draw_sky_goldleaf_byobu`, `draw_sky_aurora_veil`,
  `draw_sky_vapor_haze`, `draw_sky_cumulus_horizon`, `draw_sky_godrays_vapor`,
  `draw_sky_mesh_aurora`, … — each `(surf, w, h, ground_y, palette, phase) -> None` (paints onto
  `surf`).
- Registries: `VARIANTS` (int-keyed, ~line 955), `VARIANT_NAMES` (~970), `VARIANT_NOTES` (~985).
  Note the int keys are sparse (some indices were promoted/dropped during exploration) — preserve
  them as-is.
- Imports `from game.draw import …` only — already in `game/`.

### Family C — 10 biome skies
`archive/biome_redesign/`
- `biome_variants.py` — `BIOMES`, the group tables, `STAGES`, and per-biome keyframe lists such as
  `_DESERT_KF`. Each keyframe is `(phase, dict(...))` whose **sky-relevant keys are `sky_top`,
  `sky_mid`, `sky_bot`, `horizon`, `star_alpha`**; the dicts also carry `mtn_*`, `struct_*`,
  `ground_*`, `foliage_*` keys that are **out of scope** here.
- `scene_engine.py` — `BiomeSpec` dataclass and the sky-only painter
  `paint_sky(surf, spec, w, h, phase, stars=False, ground_y=None)`. It imports `import sky_field as
  sf` (the biome engine below — **distinct from `game/sky_field.py`**) and three helpers
  `from game.draw import make_gradient_surface, lerp_color, make_glow_surface`. `scene_engine.py`
  also defines `paint_scene` and structural drawers — **all out of scope**.
- `sky_field.py` — the biome-family sky engine. **Name collides** with `game/sky_field.py`; it must
  be renamed on copy (see §2.4).
- `biome_motifs.py` — structure/ridge motif drawers. **Do NOT port** (full-scene only).

### Look references (for visual QA)
`docs/sky_redesign/field_round_*.png`, `docs/biome_redesign/round_*.png`.

---

## 2. What to create under `game/`

No new top-level directory is introduced, so the CI `Stage minimal source` step and the 5 MB
`.apk` ceiling are unaffected. Everything is pure-Python and pygbag-safe (the OKLab engine already
documents: bake-path only, no numpy / surfarray / native calls).

### 2.0 `game/sky_field.py` — already present (no change)
The OKLab `make_sky_field(...)` engine (perceptual ramp + Bayer dithering) used by Family A is
already in `game/`. Leave it untouched.

### 2.1 `game/sky_field_treatments.py` ← copy `archive/sky_redesign/field_variants.py`
Copy verbatim. Its `from game.sky_field import …` is already correct. Provides the 5 color-field
treatments and their registry.

### 2.2 `game/sky_shanshui.py` ← copy `archive/sky_redesign/sky_variants.py`
Copy verbatim. Its `from game.draw import …` is already correct. Provides the ~10 candidate skies
and `VARIANTS` / `VARIANT_NAMES` / `VARIANT_NOTES`.

### 2.3 `game/biome_sky.py` ← extract the SKY path from `archive/biome_redesign/scene_engine.py`
Copy **only** `BiomeSpec` (or a trimmed spec holding just the keyframe list) and `paint_sky`, plus
any small helper they require. **Drop** `paint_scene` and every structural drawer. Fix imports:
- `import sky_field as sf` → `from game import biome_sky_field as sf`
- keep `from game.draw import make_gradient_surface, lerp_color, make_glow_surface`.

### 2.4 `game/biome_sky_field.py` ← copy `archive/biome_redesign/sky_field.py`
Renamed copy of the biome-family sky engine, to avoid the collision with `game/sky_field.py`. Update
any internal self-references accordingly.

### 2.5 `game/biome_sky_keyframes.py` ← from `archive/biome_redesign/biome_variants.py`
Port the 10 per-biome keyframe tables, the `BIOMES` ids, the group/`STAGES` metadata, and the
names/notes. **Sky-only:** strip each keyframe dict down to `sky_top`, `sky_mid`, `sky_bot`,
`horizon`, `star_alpha` (cleanest, matches scope). Leaving the extra scene keys in is harmless —
`paint_sky` ignores them — but stripping keeps the dormant code honest to "sky color field only."
Do **not** import `biome_motifs`.

### 2.6 `game/sky_designs.py` — the one new hand-written file (the dormant registry)
A single catalog that imports §2.1 / §2.2 / §2.3 / §2.5 and normalizes all three families behind one
signature:

```
render(surf, w, h, ground_y, palette, phase) -> None
```

Adapters:
- **Family A** (`f(w, h, palette) -> Surface`): blit the returned surface at `(0, 0)`. `palette` is
  the live biome palette; `phase` is unused (time-of-day is encoded in the palette anchors).
- **Family B** (`f(surf, w, h, ground_y, palette, phase)`): call directly.
- **Family C** (`paint_sky(surf, spec, w, h, phase, stars=True, ground_y)`): bind `spec =
  BIOMES[id]`. These carry their **own** per-biome day/night palettes, so they ignore the live
  `palette` and key off `phase`.

Expose:
- `CATALOG = [(design_id, family, human_name, note, render_fn), …]` — roughly 25 entries
  (5 + ~10 + 10).
- `ACTIVE_SKY_DESIGN = None` — the dormant switch (see §3).
- `render_active(surf, w, h, ground_y, palette, phase) -> bool` — returns `False` immediately when
  `ACTIVE_SKY_DESIGN is None` (so a future caller can fall through to the live path); otherwise looks
  up the catalog entry and renders it, returning `True`.

This module follows the existing **preview-only** convention already used by
`game/dollar_variants.py` and `game/surprise_box_variants.py`: it ships in the package but is
imported by nothing in the live render path.

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

- Both targets stay green: pure Python, no `pygame.mixer`, no native/numpy. Family A's engine bakes
  on the cache-miss path only.
- All new files live under `game/`, so the CI `Stage minimal source` step needs no edits and the
  `.apk` size guard (5 MB) is unaffected — the designs are procedural with no new assets.
- `tests/test_plausibility.py` is untouched.

### Optional dev preview (a suggestion only — not part of the live game)
If a headless catalog sheet is useful, repoint the existing exploration render scripts
(`archive/sky_redesign/render_field_variants.py`, `archive/sky_redesign/render_sky_variants.py`,
`archive/biome_redesign/render_*`) at the new `game/` modules, or add a small standalone
`tools/preview_sky_designs.py`. This is a dev aid; the game must not import it.

---

## 5. Verification checklist

1. **Imports resolve, catalog complete:**
   `python -c "import game.sky_designs as s; print(len(s.CATALOG))"` → ~25 designs, no import
   errors (proves every engine dependency is wired and nothing still points at `archive/`).
2. **Every design paints:** render the catalog headless to a sheet and compare against the gallery
   PNGs in §1.
3. **Gameplay unchanged:** run `python main.py` (native) and the pygbag build — the live sky is
   visually identical to before, 60 fps, `ACTIVE_SKY_DESIGN is None`.
4. **Tests + bundle:** `python -m pytest tests/` is green; the pygbag `.apk` stays under 5 MB.
