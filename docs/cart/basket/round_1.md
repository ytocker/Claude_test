# HAND-BASKET — round 1

Secret flyer skin: a deep red plastic carry-basket replaces the bird. One of
5 independent cart concepts. The point is the **wheelless** "quick trip"
silhouette — a deep U-shaped bucket with twin folding handle loops peaking
above centre — and a 4-frame tell driven entirely by **jostling groceries**.

## Read (40px target)
- **Silhouette:** deep U-shaped flared bucket (rim half-width 21px → bottom
  16px, rounded base) with a bold lipped rim cap, and TWO thin handle loops
  rising from rim shoulders to a peak ~22px above the rim. NO wheels.
- **Instant read:** "shopping basket." The twin-handle peak over a solid red
  bucket is the icon; the absence of wheels is the distinctness from any
  rolling-cart concept.
- Bucket mass is centred at (BCX,BCY)=(32,44); handles rise above; collision
  is the 14px circle at (32,44). Pip's parcel hangs just below centre and
  reads as extra cargo slung under the basket.

## Palette
- Basket body `#D6453E`, shade `#92241F`, rim highlight `#F2C9C5` (the night
  keyline), interior void `#681814`, slot ribs `#AA302A`.
- Handles a touch darker (`#C43A34`) with the `#F2C9C5` keyline on the upper
  arc so the loops catch light at night.
- Groceries multi-pop: green fruit `#6FB24A`, yellow bottle `#F0C03A`, bread
  `#E8E2D4`, plus a small red juice-bottle shoulder for a fuller cargo read.
- Deep red holds value on day (sky_bot ≈ 170,220,245) and night; the pale rim
  + handle keyline is the night silhouette guarantee.

## Jostle frame map (`_WING_ANGLES = 50,20,-10,-40` → phase 0..3)
The cargo IS the animation — NO wings, NO live particles. Per phase the three
lumps [green fruit, bottle, baguette] bob and re-stack, and the handle apexes
sway:
- **phase 0** (50°): bottle high, bread mid; handle sway +2 (apexes part).
- **phase 1** (20°): green fruit rises; handles centred (sway 0).
- **phase 2** (-10°): baguette pops up, bottle settles; handle sway -2.
- **phase 3** (-40°): cargo settles, bread sinks; handles centred.
A small horizontal shuffle per phase makes the trio re-stack rather than bob
uniformly, so the eye reads a jostling load. In grayscale the lumps survive as
moving high-contrast blobs over the dark rim line (colourblind/value check in
the bottom reference strip).

## 40px risk
- The handle loops are the thinnest element; at true play size they fatten
  toward the 3–4px draw width and the apex gap can close. Mitigated because the
  bold red bucket carries the silhouette regardless, and the keyline keeps the
  arc visible at night. If the art-director finds the twin-loop peak muddy at
  40px, next round can widen the apex parting and thicken the loops.
- Grocery individuation (which lump is which) is secondary at 40px; the read
  that matters is "lumpy moving cargo over a basket rim," which holds.
- Slot ribs are intentionally low-contrast texture; they may wash to flat red
  at 40px (acceptable — the rim cap + handles are the load-bearing read).
