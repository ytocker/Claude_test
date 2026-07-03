# LANDER POD — round 2

Round 1 got `VERDICT: ITERATE`. Every punch-list note is addressed below; the
legged-lander identity, grayscale value-pop tell, day-band keyline, and stout
trapezoid proportion are all kept.

## Punch list — what changed

**1. Un-buried the porthole from the parcel.** The eye was at body centre (where
Pip's parcel hangs in play). It now sits in the UPPER THIRD, hard against the
flat top edge (`PORT_CY = TOP_Y + 6`). That opens a clear, unbroken dark band of
hull metal — the two horizontal panel seams + the base lip — between the amber
eye and anything carried below centre. At 40px the warm eye and the parcel never
touch.

**2. Made the 4 dilation states legible AT 40px.** Pupil radii are now explicit
per phase instead of a continuous ramp that flattened at the bottom:
- **f0** — dark closed pupil (the "off" state), no warm light at all.
- **f1** — a clearly small-but-LIT amber dot (`r2`, solid amber core).
- **f2** — brighter + larger (`r3`), core warms toward white, bezel ring lifts.
- **f3** — brightest (`r4`, hot-white pip) with the bloom held **~25% back** from
  round 1 (`halo_r` coefficient dropped from `1.0 + 1.4t` to `0.85 + 0.55t`), so
  it no longer spans the hull or erases the metal — f2→f3 reads as "brighter,"
  not "same big blob."
- Added a **bezel-ring brighten** on f2–f3 (`PORT_BEZEL_LIT`) as a secondary tell
  that survives even when the warm core is muted by a bright sky.

**3. Lifted the hull to jackpot quality.**
- **Specular sheen band:** a soft brighter highlight column offset left of centre
  (`sheen_cx = BCX - 6`, `HULL_SHEEN`), blended over the gradient and fading
  toward the shaded base — the hull now catches light like forged metal.
- **Warm-to-cool gradient:** `BODY_TOP` warmed to `#D6D4D2`, `BODY_BASE` cooled
  to `#707A8C`, replacing the flat neutral grey.
- **Bright seam/rivet accents:** `RIVET_LIT` pips on the chamfered upper corners
  + lit chamfer strokes, so the top edge reads hard and machined — matched to the
  legs' edge quality.

**4. Splayed the centre leg more.** The centre strut now fans forward to its own
LOWER footpad (`cfoot_y = foot_y + 5`, pad `r5`) instead of dropping nearly
straight beside the outer two. The tripod now reads unmistakably as THREE feet,
widening the negative space under the body that carries the legged identity.

**5. Night-bloom restraint.** The frame-3 halo radius shrank with the same ~25%
pull-back and the bloom is tied tight to the bezel, so on the NIGHT sky it stays
clamped to the craft and can't be mistaken for a free-floating coin mid-flight.

## 40px confirmation (day + night gameplay frames are the verdict)
- **Eye clear of the parcel:** YES — at play size the amber eye sits against the
  top edge with a solid dark metal band below it on both day and night swatches.
- **4 dilation states distinguishable:** YES — at 40px the row reads dark-closed
  → small-amber → brighter → brightest, on both day and night, in grayscale, and
  with the bezel-ring brighten as a backup tell.
- **Hull reads premium:** YES — the sheen column, warm-to-cool gradient, and lit
  keyline/rivets give a forged read instead of a flat stamped grey, while the
  metal stays present at every phase.

`round_2.png` rendered via the shared helper (`render.py` →
`L.render_concept_sheet(build, "LANDER POD", round_2.png)`); the DAY + NIGHT
gameplay frames at true play size read as intended.
