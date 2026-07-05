# Paper Plane redesign — NOTEBOOK PAPER — Round 2 (ship build)

Converged the art-director's winner, **V5 · BOLD LOOSE-LEAF**, to ONE
production build. The five exploration variants are gone; `notebook_skins.py`
now exposes a single `build_notebook(wing_angle_deg)`, its cached getter
`get_notebook`, and `BUILDERS = {"skin_notebook": get_notebook}` — liftable
straight into `game/animal_paper_plane.py` (nose RIGHT, 64×84, mass (32,44),
baked self-rim, procedural-only, WHY-only comments).

## Punch list → what changed

1. **Wider keel value-split (~20%).** The under-fold dropped to `(164,167,174)` /
   crease-side `(132,137,148)` against the `(243,241,230)` lit facet — now the
   boldest value step in the skin. The crease wedge is deepest right at the
   fold, so the keel reads as a HARD fold in BOTH the level and the banked-dive
   poses (the dive no longer flattens).
2. **RED separated from BLUE.** The lit facet was given extra vertical room
   (far_tip pushed to `BCY-16`) so each feature gets its own lane: two heavy
   blue rules high on the facet (`BCY-13`, `BCY-8` — ~5px gap, two distinct
   lines at 40px), then a clear body-value gap, then the red margin in its own
   band low on the facet (`BCY-4`). They no longer touch or smear.
3. **Off-white, not pure white.** Lit facet is a soft warm-neutral
   `(243,241,230)`; the cool baked self-rim `(80,86,100)` does the silhouette
   work so the top edge holds against the bright pale-blue day cloud band.
4. **Colourblind safety.** The margin is a DARK warm band `(158,44,46)` over a
   `(118,30,34)` under-shade — it leans on VALUE, so a red-blind player still
   reads a dark margin rule. The two blue rules give a second independent value
   cue. Both kept.
5. **Ring-holes trimmed to TWO** so they stop reading as edge noise at 40px.
6. **Blue rules bend** a touch to follow the lit facet's slope (V2's 3D charm).
   Tested at 40px first — the inter-rule gap is wide enough that they still
   resolve as two rules, so the bend stays.
7. **Verified on the real DAY biome surfaces** (`game/biome.py` DAY phase): the
   pale-blue sky band, the sunlit sandstone pillar `(225,195,155)→(95,70,55)`,
   and the green ground `(80,200,80)`. The cool rim + dark crease keep the warm
   off-white dart legible even sitting directly on the warm stone column — the
   round-1 contrast trap is closed.

## How to read the sheet

`docs/animals/paper_plane_redesign/notebook/round_2.png` — a 130px hero on a
DAY-sky / DAY-ground-pillar / NIGHT triptych, then three truth cards (DAY sky,
DAY ground + sandstone pillar, NIGHT) each showing smooth-40px level/dive plus
the honest NEAREST-NEIGHBOR x3 magnified 40px reads (the gameplay-pixel truth).

## Render

```
python docs/animals/paper_plane_redesign/notebook/_render_sheet.py
# wrote docs/animals/paper_plane_redesign/notebook/round_2.png (792, 938)
```

Headless (SDL dummy), procedural-only, both build targets unaffected (no
desktop/web-specific APIs). Nothing wired into `game/` yet.
