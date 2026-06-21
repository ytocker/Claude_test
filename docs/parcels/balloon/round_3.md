# BALLOON BASKET — Round 3

Round 2 verdict: ITERATE. The teal swap fixed the red-on-red merge (KEEP),
but the dome had become a near-perfect SPHERE — it read as a striped
beach-ball/ornament — and the basket was occluded under Pip. This round
re-establishes the teardrop, frees the basket, and re-cuts the stripes as
converging gores.

## What changed (every priority note)

1. **Re-established the balloon TEARDROP (priority 1).** The envelope is no
   longer an ellipse. It is built from a per-row half-width profile
   (`_teardrop_halfwidth`): a rounded crown, the widest belly at ~46% down,
   then a taper that pinches the lower third inward to a narrow throat
   (`throat = 0.34` of max width) above the basket. The full round belly
   reads "balloon"; the pinched throat is the tell that stops it reading as a
   sphere. (First pass over-pinched into a parasol/umbrella; softened to a
   rounded onion/teardrop with a curved crown rather than a flat wide
   shoulder.)

2. **Freed the BASKET (priority 2).** The whole prop is dropped (`basket_top
   37 → 40`, envelope throat at y33) and nudged ~1px forward of Pip
   (`FWD = 1`, +x away from his body). A full basket row plus the suspension
   gap now clears Pip's belly in the carry — the basket reads as the box
   hanging under the envelope, not a hidden ornament.

3. **Gore stripes converging to an apex crown (priority 3).** Stripes are
   now baked as GORES: each pixel's panel index comes from its position
   ACROSS the local row width (−1..+1), so the panels run vertically through
   the belly and their boundaries pull together toward the crown because
   every row is narrower there. They converge to the apex (envelope read)
   instead of even horizontal/vertical barber-stripes (beach-ball read).
   6 bold gores survive the 22px smoothscale.

4. **Tilt frame 5 re-anchored (priority 4).** The suspension cords now anchor
   at the pinched THROAT (`throat_y − 2`), not the wide shoulder, and are
   kept short. The basket therefore stays tucked UNDER the canopy through the
   full −25°→90° sweep — at 90° the whole prop rotates as one coherent unit
   with the basket riveted to the envelope mouth, no detach/float-right.

KEEP carried through unchanged: the teal/azure + cream canopy (separates
from Pip's red), the warm lower-rim arc (night value rescue), and the wicker
basket with its bound-rim + course-line weave.

## Carry-crop read (the verdict)

- **DAY carry (zoom + gameplay-day):** the teal/cream teardrop sits below and
  slightly forward of Pip's red belly — total separation. The rounded envelope
  tapers to the throat, gores fan to the crown, and the wicker basket hangs
  clear below the suspension gap. It reads as a **balloon over a basket**, not
  a striped sphere and not an ornament.
- **NIGHT carry (gameplay-night):** mid-teal holds value against the dark
  purple sky, the cream gores stay bright, and the warm throat arc keeps the
  lower body from sinking. Still a balloon at 22px.

## Tilt survival (−25 / 0 / 30 / 60 / 90°)

- The teardrop silhouette + throat-anchored basket rotate as one unit across
  every bank on DAY, NIGHT, and GRAYSCALE. Frame 5 (90°) no longer detaches —
  the basket stays tucked against the canopy mouth. In grayscale the teal and
  cream gores sit at clearly different values, so the candy alternation
  survives value-only.

## 22px notes

- The rounded-crown-to-pinched-throat profile is the load-bearing change:
  even a few gores now read as an envelope because the silhouette tapers.
- Gores assigned by across-row position keep wide bold panels in the belly
  (good at 22px) while still converging at the crown.
