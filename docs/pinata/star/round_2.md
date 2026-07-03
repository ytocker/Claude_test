# STAR PIÑATA — round 2

Round 1 verdict was ITERATE. Every punch-list item below was applied; the
radial-spike star identity and the cream crepe-fringe keyline are kept.

## What changed, per punch-list item

1. **TRUE 7-point star, one point straight UP.** The spokes are now placed on a
   strict 7-fold ring with the top point fixed at -90° (straight up) and the
   rest at even 360/7 steps. Because 7 is odd, the bottom of the ring straddles
   the vertical as a PAIR (spikes at ~64° and ~116°) with **no spike pointing
   straight down** — so it can no longer be misread as an 8-point pinwheel.
   Verified on the play-size strip (40px), not the 3× hero.

2. **Star lifted off Pip's parcel.** The hull centre is raised on the canvas
   (`BCY` 44 → 30) so the whole star sits well above the composite centre. The
   parcel hangs 12 px below the bird centre (`PARCEL_Y_OFFSET`), so it now hangs
   cleanly BELOW the full radial ring instead of amputating the lower spikes.
   The bottom pair is additionally shortened + splayed (`BOTTOM_SPIKE_SCALE =
   0.74`) so even the lowest points read above the parcel. Confirmed in both
   DAY and NIGHT gameplay frames: the parcel sits under an intact 7-point star.

3. **Crack tell is VALUE-first → survives grayscale.** The four crack stages
   now step cleanly in VALUE with no hue help:
   - Stage 0 (sealed): a deep near-black **vertical groove** — the dark anchor.
   - Stage 1: a **dim** warm lens (its value tracks `crack`, kept well below the
     peak; the white-hot core does not fill in until `crack > 0.3`).
   - Stage 2: the **white-hot** widest lens — the value peak.
   - Stage 3: a **mid** lens, settling back between 0 and 2.
   The grayscale strip in the sheet shows a clear 4-step swing
   (dark → dim → bright → mid) with zero hue contribution.

4. **De-faced the widest frame.** The seam is now a **VERTICAL diamond candy-
   glow lens** (lips left + right, the bright interior a vertical diamond)
   instead of a horizontal slot, so the widest frame can never read as a smile
   on a round head.

5. **Night bloom boosted ~35%.** The additive glow gained an extra ring of
   reach (4 falloff steps vs 3, larger radii) and ~30% more peak alpha (150→190
   base), so the candy-glow seam is the genuine night focal anchor rather than
   the keyline carrying the frame alone.

6. **Cyan rescued on DAY.** The old cyan `#1FB6D6` dissolved into the mid-blue
   sky; it is shifted to **teal-green `#1AC4A8`** (with a matching darker
   shade), which separates cleanly from the day sky while still reading as a
   cool candy colour. Its spilled-candy dot moved to teal too.

**KEPT as-is:** the cream crepe-fringe keyline around every cone + hull and the
two crepe fringe bands — the decision that holds the silhouette on both skies.

## Confirmations
- **7 points, one up:** yes — strict 7-fold ring, top point at -90°, bottom is a
  splayed pair (no straight-down spike). Reads as 7 on the 40px play strip.
- **Star clears the parcel:** yes — hull raised to `BCY=30`; both DAY and NIGHT
  gameplay frames show the full radial ring above the parcel.
- **4-step value swing on grayscale:** yes — sealed-dark → dim-lens →
  bright-lens → mid-lens, distinct in value alone on the grayscale strip.

## Files
- `build.py` — round-2 geometry + palette + crack/glow.
- `render.py` — renders `round_2.png` via the shared gameplay helper.
- `round_2.png` — DAY gameplay | NIGHT gameplay | reference (3× / play-size /
  grayscale).
