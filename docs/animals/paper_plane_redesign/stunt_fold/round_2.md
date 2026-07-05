# Paper Plane redesign — STUNT / FIGHTER FOLD · Round 2 (production convergence)

The art-director picked **V1 · RED RACING STRIPE** (VERDICT: ITERATE). Round 2
converges to ONE ship-ready production build and drops the other four
explorations. `stunt_fold_skins.py` now exposes a single
`build_stunt_fold(wing_angle_deg)` + `get_stunt_fold` +
`BUILDERS = {"skin_stunt_fold": get_stunt_fold}`, liftable straight into
`game/animal_paper_plane.py`.

Sheet: `round_2.png` — the production build (top) staged beside the CURRENT
dollar-bill dart (bottom, the baseline to beat). Each: hero 130px (left); 40px
NEAREST x3 LEVEL / DIVE on a DAY sky and a NIGHT sky (right) — the honest
gameplay read. The DIVE pose is the value stress-test (the fold flattens most
there).

## Punch list — how each note was addressed

1. **Stripe locked to the keel crease.** The red is no longer a free-floating
   airbrushed band inside the white. It is now a KEEL BAND whose TOP edge is
   the fold crease line itself: white lives ABOVE the crease (top facet), red
   lives BELOW it (keel band), and the boundary is a hard white→red value
   step. The top facet is painted AFTER the red so the seam is a clean edge,
   and the dark crease line is stroked last over the seam. No trailing-edge
   feathering — the red wedge ends in flat fills, not a bleed into white.
2. **Three hard values at 40px, DIVE-tested.** Sampled at TRUE 40px on the
   dive frame (frame 1, tilt −32): 147 white px (lum > 195), 106 saturated
   red px (avg ≈ 173,41,48 — red survives the downscale, not muddied), and a
   distinctly darker under-fold cluster (median lum ≈ 91). Three clusters, not
   a gradient mush.
3. **Night-sky safety.** The white top facet sits at full value (244–246) on
   both skies; the under-fold was bumped ~10% deeper (108,116,132 /
   80,88,104) so the white-top → under-fold delta never collapses to a single
   mid-grey sliver against a dark sky.
4. **Matte-paper finish.** No glossy specular ramp. Every facet is a flat
   fill; the value steps inside the red band and at the nose are FACETS (hard
   fold breaks), not highlights. One crisp crease only.
5. **Rim discipline.** The baked self-rim is single-pixel-offset stamped, so
   it is exactly 1px. Measured along the swept trailing edge: outer rim
   thickness = 1px on every scanned row, no 2px halo doubling.
6. **Moderate delta sweep kept.** Held V1's moderate sweep + sharp nose
   (sweep baked into `_hull_pts`); did NOT lean to a thin sliver, so it still
   reads as a banked folded SHEET in the dive frame.
7. **Beats the baseline.** Staged beside the current dollar dart at 40px on
   both skies: obviously more dynamic (sharper swept delta, longer nose, the
   red keel spine driving the eye forward) while staying equally legible — the
   silhouette and three-value read hold as hard as the calm green glider's.

## Contract held
- `build_stunt_fold(wing_angle_deg) -> 64×84 SRCALPHA`; mass centred (32,44);
  fixed 14px collision circle there. Nose points RIGHT (forward).
- Single getter via local `_make_prebuilt_skin`;
  `BUILDERS = {"skin_stunt_fold": get_stunt_fold}`.
- No wings — the 4 base poses (`_WING_ANGLES`) drive a snappy BANK/FLUTTER +
  nose-bob, clamped at `_ROLL_MAX = 7°` so a stunt roll never flattens the
  delta to a sliver.
- Procedural only; WHY-only comments; baked 1px self-rim on every frame.
  Sky-agnostic single build — works on native desktop and pygbag/WASM from the
  same code.
