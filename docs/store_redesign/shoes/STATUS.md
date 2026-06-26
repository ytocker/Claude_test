# SHOES Category — Status

Branch: `v5_store_shoes`
Integration commit: `cadaa3d`
Tests: 61 pass + 9 subtests

---

## Full Roster (15 shoes, cost-sorted)

| ID | Name | Cost | Rarity | Status |
|----|------|------|--------|--------|
| `skin_shoe_flipflops` | FLIP-FLOPS | 240 | common | existing |
| `skin_shoe_poolslides` | POOL SLIDES | 300 | common | existing |
| `skin_shoe_courtgreen` | COURT GREEN | 420 | rare | existing |
| `skin_shoe_canvashigh` | CANVAS HIGH | 460 | rare | existing |
| `skin_shoe_checkerslip` | CHECKER SLIP | 480 | rare | existing |
| `skin_shoe_shelltoe` | SHELL TOE | 540 | rare | existing |
| `skin_shoe_airflyer` | AIR FLYER | 620 | rare | existing |
| `skin_shoe_airbubble` | AIR BUBBLE | 680 | rare | existing |
| `skin_shoe_boostknit` | BOOST KNIT | 760 | rare | existing |
| `skin_shoe_megadad` | MEGA DAD | 780 | rare | **NEW** |
| `skin_shoe_retro1` | RETRO 1 | 850 | epic | existing |
| `skin_shoe_jellycore` | JELLYCORE | 1200 | epic | **NEW** |
| `skin_shoe_neoncircuit` | NEON CIRCUIT | 1800 | epic | **NEW** |
| `skin_shoe_wingboots` | WING BOOTS | 3200 | legendary | **NEW** |
| `skin_shoe_afterburner` | AFTERBURNER | 4800 | legendary | **NEW** |

Rarity bands: `<400` common · `<800` rare · `<2500` epic · `≥2500` legendary (cost-derived, no hardcoding).

---

## New Additions

### Design 1 — MEGA DAD (rare · 780) · `game/shoe_megadad.py`

Chunky triple-stacked foam dad-shoe runner. Sole occupies bottom ~45% of the box (vs ~22% on normal sneakers) — the bulk IS the read. Three foam tiers separated by carved grooves with bright lip highlights. Dominant orange mudguard block (~0.12–0.15h) as the 16px hero colour cue. Teal rounded toe-cap caps the front. Two fat reflective lace straps. Heel pull-loop standing proud of the back silhouette. No fantasy — believably enormous footwear.

Design loop: R1 → C1 (ITERATE: mudguard too thin, lace cage muddy noise, pull-loop not legible) → R2 (dominant orange block, fat strap pair, loop pushed proud).

### Design 2 — JELLYCORE (epic · 1200) · `game/shoe_jellycore.py`

Translucent candy-gel runner. Draws on SRCALPHA temporary layer so partial transparency is genuine. Opaque pale-lilac substrate laid first (bright candy ground); translucent pink→cyan banded outsole + lilac upper at elevated alphas (130/190). Full-alpha cyan heel slab + pink toe slab guarantee the two-tone reads at 40px. 3–4 bubble pockets (lighter fill + bright rim + white specular hotspot). Cyan+pink inner bloom ellipses. Single bright meniscus gloss line at the sole/upper seam.

Design loop: R1 → C1 (ITERATE: transparency collapsing at foot scale, bubbles invisible, sole banding lost) → R2 (opaque substrate + elevated alphas, guaranteed full-alpha terminal slabs, reduced bubble count).

### Design 3 — NEON CIRCUIT (epic · 1800) · `game/shoe_neoncircuit.py`

LED light-up cyber high-top. Scale-aware split (`foot = w < 25 or h < 20`): product shot gets circuit traces, eyelets, fine rim; foot scale gets only the highest-contrast elements — solid near-black backing mass (critical dark ground), fat ankle collar band (cyan→magenta, halo capped at `h*0.16`), heel chevron, chunky sole strip. Glow via SRCALPHA layer + `BLEND_RGBA_ADD`. Collar intentionally rises above box top (t<0) for silhouette drama.

Design loop: R1 → C1 (ITERATE: no dark ground so cyan glows floated on white void, sole strip invisible, collar clipped) → R2 (scale-aware split, near-black backing mass, collar above-box).

### Design 4 — WING BOOTS (legendary · 3200) · `game/shoe_wingboots.py`

Hermes winged gold greave boot. Wings drawn first (behind the gold shell) so roots are overlapped by metal. Two bold feather plumes via `feather()` helper using convex arc sampling (9-point `math.sin` bow) — top plume clears box top (tip ~t −0.34), lower plume sweeps past heel (t<0 in x). Gold shell has light/dark/deep trio for metallic sheen; vertical greave seam. Laurel ankle wrap (bold leaf wedges, survives downscale). Gemmed cyan clasp. Three tight sparkle motes framing the wing fan. Wings exceed the unit box in both x (behind heel) and y (above cuff).

Design loop: R1 → C1 (ITERATE: wings too narrow/straight at foot scale, gold reads putty not metal, clasp invisible) → R2 (broad convex fan belly, GOLD_L specular stripe, cuff highlights).

### Design 5 — AFTERBURNER (legendary · 4800) · `game/shoe_afterburner.py`

Chrome rocket thruster boot. Flame plume drawn first (behind boot) via nested teardrop tongues — `_tongue(root_t, half, tip_t, sink)` helper builds a drooping centreline biased down-and-back (thrust vector). Three nested values (red rim / orange body / white-hot core) give hard readable edges at 17px. Supersampled SRCALPHA glow underlay blooms under the chunky shape without making the shape depend on it. Ignition flare at nozzle throat (white-blue blob). Warm yellow-white ember circles off the tail (no teal — colorblind-safe). Chrome shell with specular highlight band + steel-dark shadow for curved-metal sheen. Three angled heat-exhaust vents with `_VENT_GLOW` lip. Riveted seam + rivet dots clamped to ≥1px.

Design loop: R1 → C1 (ITERATE: plume a dead horizontal diamond, no glow atmosphere, vents invisible at foot scale) → R2 (teardrop tongue with droop bias, supersampled glow underlay, scale-clamped vent pair).

---

## Integration Details

Three touches per shoe (additive — existing 10 untouched):

1. `game/shoe_<id>.py` — self-contained `draw_shoe(surf, x, y, w, h, facing=1)` module ported from scratch builder; WHY-only comments; no `tools/` imports.
2. `game/shoe_skins.py` — module added to `from game import (...)` tuple; entry added to `_DRAW` dict. `ICONS` and `BUILDERS` auto-derive.
3. `game/store_catalog.py` — entry added in cost-sorted position in the SHOES block.

---

## Verification Results

```
SDL_VIDEODRIVER=dummy python -m pytest tests/   →   61 passed, 9 subtests
```

Per-ID render check (all 5 new shoes):

| ID | frame | icon | rarity | in_renderer |
|----|-------|------|--------|-------------|
| skin_shoe_megadad | ✓ | ✓ | rare | ✓ |
| skin_shoe_jellycore | ✓ | ✓ | epic | ✓ |
| skin_shoe_neoncircuit | ✓ | ✓ | epic | ✓ |
| skin_shoe_wingboots | ✓ | ✓ | legendary | ✓ |
| skin_shoe_afterburner | ✓ | ✓ | legendary | ✓ |

Store gallery regenerated: `docs/store_gallery/shoes.png` — 15 shoes, correct tier outlines (rare-blue, epic-purple, legendary-gold).

---

## Design Loop Config

Item-design skill cap (permanently reduced for this project): **≤2 designer turns + ≤1 critic turn per design**, ending on a designer revision, always ≥1 critique. Committed in `.claude/skills/item-design/SKILL.md` (`b43e4a5`).

---

## Scratch Artifacts (not bundled)

```
tools/shoe_candidates/design_1.py  …design_5.py   — final scratch builders
tools/shoe_candidates/render_design_1.py …_5.py   — per-design render scripts
docs/store_redesign/shoes/concepts.md              — concept briefs
docs/store_redesign/shoes/design_N/round_1.png     — R1 sheets (×5)
docs/store_redesign/shoes/design_N/round_2.png     — R2 sheets (×5)
docs/store_redesign/shoes/final_comparison.png     — 6-column comparison figure
```

The `tools/` directory is excluded from the pygbag bundle by the CI staging step — no bundle-size impact.
