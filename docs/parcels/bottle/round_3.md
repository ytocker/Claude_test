# MESSAGE BOTTLE — Round 3

Round 2 verdict was ITERATE: the standalone bottle + tilt row are DONE
(signed off — corked neck, scroll, translucency, grayscale separation all
kept untouched), but in the CARRY pose Pip occluded ~70% of the bottle and the
cork never cleared into open sky. Round 3 is a pure placement / anchoring fix
on the carry pose only. None of the bottle geometry or palette changed.

## What changed (carry pose only)

1. **Lowered + outset the bottle within the sprite.** Added a post-lean
   translation (`CARRY_DX = -6`, `CARRY_DY = 8`, in 2× pixels) that shoves the
   whole baked bottle toward the LOWER-LEFT of the 22px canvas. The sprite is
   centred on the parcel anchor at Pip's belly-bottom, so this drops the corked
   neck + lower belly OUT of his lower-left silhouette onto open sky — the cork
   now lands on sky, not on his warm-red feathers. The lean+translate are
   composited on a roomy padded surface first, then cropped back to the canvas,
   so the long diagonal axis never clips off before the downscale.
2. **Steeper lean along Pip's flight line.** `LEAN_DEG 45 → 48`, on a steep
   down-left diagonal so the long lying-down axis lies along his flight line and
   BREAKS FREE of the round-body silhouette instead of hiding inside it. (Tested
   both extremes: a near-vertical bottle dangles the cork but buries the belly
   under him; a near-horizontal one tucks fully beneath his width. The steep
   down-left diagonal is the only pose that shows the long axis AND floats the
   cork in sky.)
3. **1px dark contact rim.** A dark (`OUTLINE`) rim is drawn along the top wall
   + belly cap — the edges that, post-lean, face UP toward Pip — so the held
   bottle separates from his chest at 22px. Verified against both the warm-red
   DAY body and the darker NIGHT body: the rim + outline keep the green glass
   off his feathers in both.

KEPT EXACTLY: the tilt-row asset — corked neck, cream rolled scroll
(`#F6ECCE`) with its coil end-caps and writing ticks, the translucent glass
keyline + sky-value sliver, the cork seam, and the grayscale separation. Only
placement, lean angle, and the contact edge changed.

## Carry-pose confirmation (day + night, 22px)

On both the DAY and NIGHT gameplay crops the CORK now sits in OPEN SKY clearly
below and left of Pip — fully off his red/orange feathers (day) and off the
darker night body — which is the tell that sells "carrying a bottle". The neck
and the green glass belly with the cream scroll emerge below his belly on the
lower-left diagonal, separated from his chest by the dark contact rim, so the
held object reads as a corked message-in-a-bottle and not a round orb. The
cream scroll carries the read on the dark night sky; the cork's warm hue + dark
seam separate it from the green glass at true size. Bottle reads as a bottle at
22px, day and night.

## Residual note

The parcel anchor (`PARCEL_Y_OFFSET = 12`) is a shared game constant, so the
very top of the belly still tucks under Pip — true of every parcel cosmetic.
The round-3 placement makes the part that DOES show (cork in open sky + neck +
scroll-belly) the unambiguously bottle-shaped part, on the lower-left diagonal
against sky.
