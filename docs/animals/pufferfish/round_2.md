# PUFFERFISH — Round 2 (converged)

VERDICT in round 1 was **ITERATE**, winner **V4 STAR-BURST**. This round folds
the whole punch list into ONE production lead, `skin_pufferfish`
(`build_pufferfish`), and keeps two small alts for comparison only.

## Punch list — what changed

1. **V1 face on the V4 star body.** The vivid urchin needle-halo silhouette is
   kept; the startled dot-eyes are replaced by V1's big friendly eyes + a pouty
   warm-dark **O**-mouth + blush. Eyes are radius-4 with the iris pushed
   outward, so they survive 40px as **two distinct dots** (confirmed in the
   NEAREST x3 and grayscale reads).
2. **Eyes locked to a fixed offset.** The face cluster is now derived from
   constants (`EYE_OFF_X/Y`, `EYE_DX`, `MOUTH_DY`) relative to the fixed body
   anchor (32,44) — identical on all four poses, so it no longer slides on the
   dive frame. `cx,cy` is pinned every frame; only `r`/`spk`/brightness pulse.
3. **Internal body value + body-wide inflate pulse.** New `_radial_body()`
   lays a soft core→mid→edge radial gradient so the ball reads as a sphere, not
   a flat disc. A restrained value-only brightness factor (`bf = 0.90+0.20·inf`)
   brightens the whole ball ~10% on the puffed down-frame and dims it ~10% on
   the deflated up-frame, so the gag now reads in the BODY as well as the
   spikes. No bloom halo — pure value steps + a small top-left specular.
4. **Two-tone spikes with their own value step.** `_spike_ring()` was rebuilt
   so each ray is a darker BASE wedge at the rim + a brighter TIP wedge on its
   outer half. Every ray carries a bright-tip / dark-base contrast that holds
   after downscale instead of flattening into a starburst.
5. **Night + grayscale verified explicitly.** The sheet renders the hero and
   the 40px truth test on BOTH a bright-day and a night backdrop, plus a
   **desaturated 40px thumbnail** (level + dive). The silhouette and the
   face/eyes hold on pure luminance — the read does not depend on yellow.
6. **Hitbox stays fair.** Body mass is pinned at (32,44) on every frame even
   fully inflated; the swell is +2px radius only, so the fixed 14px collision
   circle is unaffected.

## Deliverables
- `pufferfish_skins.py` — single lead `build_pufferfish` +
  `get_pufferfish = _make_prebuilt_skin(build_pufferfish)` +
  `BUILDERS = {"skin_pufferfish": ...}` (plus `alt_dense_star`,
  `alt_coral_star` for comparison).
- `_render_sheet.py` → `round_2.png`: hero 130px day & night, 40px NEAREST x3
  per sky, grayscale 40px proof, and the two alt cards.

## Alts (comparison only)
- **alt_dense_star** — tighter single 20-ray needle halo (more sea-urchin,
  less balloon). Lead kept the two-ring version for a fuller body read at 40px.
- **alt_coral_star** — coral/orange palette to sanity-check the night read off
  a non-yellow hue; lead stays golden as the canonical pufferfish colour, now
  validated against the grayscale proof.

Contract unchanged: 64×84 SRCALPHA, body at (32,44), 4 poses over
`_WING_ANGLES`, procedural-only, WHY-only comments.
