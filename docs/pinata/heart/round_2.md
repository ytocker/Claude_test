# HEART PIÑATA — round 2

Round 1 verdict was ITERATE: the heart silhouette was strong, but the WHITE top
crepe band ran straight across the gold seam, so at 40px / in grayscale the
bright white bar + the vertical seam read as a medical-cross "T". Round 2 kills
the "T" and rebuilds the seam tell around GLOW.

`round_2.png` columns: GAMEPLAY — DAY | GAMEPLAY — NIGHT | REFERENCE. The two 40px
gameplay frames are the verdict.

## What changed (punch list)

1. **Killed the "T" (#1).** The white top fringe is now carried ONLY by the
   single topmost crepe row, and only on the two OUTER lobe shoulders — a WIDE
   clear coral channel (`WHITE_CHANNEL = 8`px either side of centre) runs down
   the middle. The gold seam now passes through an unbroken red/coral field, not
   a white cross-bar. The two white crests sit out on the shoulders as separated
   dots, never joining over the seam.
2. **Seam is a pure vertical GOLD WEDGE.** `_seam_glow` now draws an additive
   gold wedge — widest at the cleft, tapering toward the point (taper 0.62) —
   with ONE hot sugar-white core column dead-centre and no horizontal competitor.
3. **Motion sold in GLOW, not gape.** The per-phase drive is now
   `(rim-peel, glow radius, glow-alpha mul, spark)`: phase 2 is a clear bright
   bloom (radius 6.4, alpha ×1.20); phases 0/3 fall back to a thin warm line
   (radius 3.0/3.6, alpha ×0.55/0.65). The two cream rim edges peel laterally by
   ~1px to shimmer the seam without gaping the heart.
4. **Candy peek replaced.** The invisible 3px candy dab is gone; phase 2 now pops
   a single 2px gold sugar-spark just above the cleft (gold core + sugar-white
   highlight) as the flash of escaping sugar at the bloom.
5. **Bottom point cleared from the parcel.** The whole heart is lifted ~3px
   (`LOBE_CY = BCY-9`), the point raised (`POINT_Y = BCY+14`) and sharpened by
   tucking the triangle base in (`POINT_TUCK = 3`), so the tip clears Pip's
   parcel knot on the day frame instead of fusing into one brown blob.
6. **Night anchor preserved.** With the interior white band removed, each lobe
   crown carries a thin cream rim arc (hugging only its outer crown, stopping
   short of the seam) so the lobes keyline against the dark sky as two separate
   crests, never a horizontal line over the centre.

KEPT: the bold two-lobe heart + deep cleft, the cream rim keyline, the crepe band
stacking (red → coral → white shoulders).

## Verification at 40px

- **Grayscale (colorblind / value check):** the brightest shape is a clean
  VERTICAL BAR — the gold wedge + white core column down dead-centre — with only
  two dim, separated lobe-crest highlights out on the shoulders. There is NO
  horizontal bright bar crossing the seam. **No "T".** (Verified by upscaling the
  phase-2 grayscale frame; the top of the value mass is the wedge cleft, not a
  cross-bar.)
- **Motion reads via glow swing:** phase 0 shows a thin faint warm seam line;
  phase 2 shows a full bright gold bloom with the sugar-spark; the swing in glow
  radius + brightness carries the flap tell rather than any change in heart width.
- **Bottom point clears the parcel:** on the 40px DAY gameplay frame the sharpened
  raised tip sits above Pip's composited parcel knot with visible separation — no
  single brown blob.
- **Night:** the gold seam wedge is the bright anchor; the two lobe-crown cream
  arcs keyline the silhouette against the deep-night sky.

## Contract compliance

- 64×84 SRCALPHA canvas; `COMPOSITE_W/H=64/84`, `DY=12`, `BCX,BCY=32,44`.
- `build(wing_angle_deg) -> Surface`; phases driven from
  `parrot._WING_ANGLES = (50, 20, -10, -40)` → phase 0..3 via `_phase`.
- Drawn UPRIGHT — no rotation baked; velocity tilt applied by the getter.
- Procedural pygame only; reuses `game.parrot._aaellipse`. No new raster assets.
