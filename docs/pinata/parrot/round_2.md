# LOTERÍA PARROT PIÑATA — "El Perico" — Round 2

Sheet: `docs/pinata/parrot/round_2.png`
(GAMEPLAY — DAY | GAMEPLAY — NIGHT | REFERENCE: 3x / play-size / grayscale)

Round 1 verdict was ITERATE: hooked beak + two-block colour identity read, but
the tail-wag tell was occluded by Pip's centred parcel and was carried by hue
(same-value yellow/blue ribs), so it failed at 40px and in grayscale. Every note
on the punch list is addressed below.

## What changed (punch list, in order)

1. **Tail now swings in OPEN SKY beside the parcel — not behind it.** Pip's
   parcel composites centred 12px below body-centre (`PARCEL_Y_OFFSET = 12`),
   covering the old dead-centre pivot at (32, 56). The pivot moved to the
   LOWER-LEFT haunch (`TAIL_PIVOT_X/Y = 22, 46`) and the blade now sweeps
   DOWN-AND-LEFT, into the clean sky left of the parcel (head is upper-right,
   parcel is centred-low, so lower-left is open). Composited-over-parcel checks
   on all four frames confirm the blade and its cream-pom tip read fully against
   sky with zero parcel overlap. The body was lifted ~3px (`DY 12 → 9`,
   `BCY 44 → 41`) to buy the sweep room.

2. **Wag amplitude amplified at the silhouette edge.** Sweep re-aimed to a wide
   down-left pendulum: `_TAIL_SWEEP_BY_STAGE = (205°, 232°, 262°, 232°)`
   (measured from horizontal-right, +CCW; 270° = straight down). The pale pom
   tip travels from well LEFT of the body's vertical centreline (stage 0) to
   near straight-down UNDER the centreline (stage 2) — it visibly changes which
   side of centre it sits on across the loop. The tip is now the boldest mover:
   a dominant scalloped cream-pom cluster plus a fat terminal pom.

3. **Wag is VALUE-driven, not hue-driven.** The tail dropped the same-value
   yellow/blue rib pairing. It's re-banded as a VALUE PADDLE: a deep dark-green
   base (`TAIL_DARK #16 4E 28` over `TAIL_DARK_D #0E 36 1E`) with alternating
   CREAM ribs (`TAIL_CREAM #FF F4 D6`). The grayscale strip alone now shows the
   tail as a clear light/dark paddle that changes position frame-to-frame
   (verified on the blown-up grayscale debug pass).

4. **Day-sky separation lifted on the belly.** Added a darker green core-shadow
   crescent down the sky-facing lower-LEFT belly (`BODY_CORE_D #14 56 28`) plus
   a 1px darker-green inner contour arc along that same lower-left edge, so the
   body has its own internal value step against the bright day sky instead of
   leaning only on the cream keyline.

5. **Beak tightened.** Lower mandible shortened + narrowed (now a 4px stub vs
   the old 6px), the upper hook pulled in one px, and a deep hook-tip notch
   shadow added (`BEAK_HOOK_D #78 64 40`) so the down-hook curve is the read.
   The beak's brightest value was pulled off pure white (`BEAK_CREAM` now
   `#EC DA B2`) so it no longer out-shouts the red head on day.

6. **Tail differentiated from the flank.** The flank keeps the yellow/blue
   Lotería chevron; the tail is now a dark paddle with cream ribs and a
   dominant scalloped cream-pom tip — a different colour AND value rhythm, so it
   never reads as a continuation of the body bands.

## Kept (per the brief)
- Hooked-down cream beak, red-head / green-body two-block identity, the no-legs
  silhouette (tiny tucked perch-claw nubs only — flamingo-distinct), and the
  night legibility (cream fringe keylines on body + head + tail blade carry the
  saturated party colours out of the dark).

## Confirmation
- `round_2.png` rendered via the shared helper at `docs/pinata/parrot/round_2.png`.
- DAY + NIGHT gameplay frames at play-size read clearly: green body block, red
  hooked-beak head upper-right, dark cream-ribbed tail paddle swinging in open
  sky lower-left of the parcel.
- The tail swings in OPEN SKY beside (never behind) the centred parcel —
  confirmed by per-frame parcel-composite checks.
- The wag reads in GRAYSCALE ALONE as a dark paddle changing position across the
  four frames.
- The beak-tighten and day-contrast fixes landed (deeper hook notch, narrower
  lower mandible, dimmed beak value, belly core-shadow + inner contour).
