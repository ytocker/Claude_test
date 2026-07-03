# GRIFFIN skin — Round 2 (converged to ONE ship build)

Art-director verdict on Round 1 was **ITERATE**, winner **V4 SOARING WIDE-WING**.
Round 2 drops the 5-way exploration and ships a single production build,
`build_griffin(wing_angle_deg)` → `get_griffin` → `BUILDERS = {"skin_griffin": ...}`,
liftable straight into `game/animal_skins.py`. Contract unchanged: 64×84 canvas,
body (32,44), head (44,34), 4 wing poses, procedural-only, WHY-only comments.

Sheet: `round_2.png`. Left card = the griffin at hero 130px (night/day) + 40px
smooth + 40px NEAREST x3 across level / dive / widest-down poses on both skies.
Right card = the SHIPPING bald-eagle skin (`game.animal_skins.get_eagle`) at the
SAME 40px NEAREST x3 read, directly beside the griffin, so the distinctiveness
is provable rather than asserted.

## Punch list — what changed (all six)

1. **Lion rump as the primary silhouette tell, on EVERY frame.** The
   hindquarter is now drawn as its own `_lion_rump()` mass pushed LOW + REARWARD
   (centre at `(BCX-4, BCY+3)`), and the near wing root is anchored forward/high
   (`(BCX-8, BCY-1)`) so its lower-inner edge clears the rump. The dedicated
   widest-down-pose row on the sheet confirms the warm rump bulge + tail root
   stay OUTSIDE the wing footprint even when the wings are at their widest — so
   the rear never collapses into the eagle's single brown body.
2. **Feather→fur value split raised ~30%.** Wing feathers moved to a darkened,
   cooler `#6E4416` (`WING`, with `WING_D #4A2C0E`); the rump fur stays warm gold
   `#E8C24A` (`FUR`). The seam is now a genuine value STEP, not a neighbouring
   brown — it survives the NEAREST x3 read on both skies.
3. **Permanent chunky 3-blob dark-tipped tail-tuft.** `_tail_tuft()` is now a
   fat club of three stacked near-black blobs (`TUFT_TIP`/`DARK`) on a furred
   whip, drawn in ALL four poses well clear of the rear — no longer an
   up-pose-only flick. It is solid blobs (not thin radiating strokes) so the
   back-end lion anchor holds at 40px.
4. **Sharp 2–3px hooked raptor beak in dark beak color.** `_hooked_beak()` is a
   tighter gold wedge whose down-hook is a sharp `#3A2A12` (`DARK`) talon-tip and
   whose whole outline is ticked in `DARK`, so the hook stays a crisp predator
   point on bright sky instead of a gold smear.
5. **Day-sky legibility via a dark edge.** The house `_add_outline` pass already
   rims the silhouette; on top of that the pale head gets an inner dark ring
   (`HEAD_EDGE`) and the seam/ruff use the dark `FUR_RUFF`, so both the pale head
   and the gold rump hold an edge against the bright-day backdrop (see the
   day-tile rows).
6. **Dark fur neck-ruff at the head→body join.** Borrowed from V3: a small
   radiating `FUR_RUFF` mane collar at `(BCX+8, BCY-8)` where the eagle head
   meets the lion body — the literal "two creatures joined" seam.

## Eagle-distinctiveness note

On the right card, griffin and eagle are rendered with identical pipeline and
scale. The separation reads instantly at gameplay size:

- **Rear half.** Eagle = one continuous dark-brown body, no tail-tuft. Griffin =
  a warm-gold lion hindquarter + a dark-tipped tail-tuft trailing OUTSIDE the
  wing. That second material on the back end is the cheapest, most reliable
  40px tell.
- **Body value map.** Eagle's wing and body sit at the same brown value.
  Griffin's wing feathers are pushed darker/cooler than the gold rump, so the
  body shows a clear feather|fur value break the eagle never has.
- **Wingspan + join.** Griffin's swept wings are larger (span 56/60 vs the
  eagle's 48) and the neck-ruff marks an explicit eagle→lion seam; the eagle has
  a smooth white-head-on-brown-body transition with no ruff.

Procedural-only, both build targets unaffected (pure Pygame draw calls + the
shared prebuilt-skin factory). `round_2.png` confirmed at 860×600.
