# LOTERÍA PARROT PIÑATA — "El Perico" — Round 3

Sheet: `docs/pinata/parrot/round_3.png`
(GAMEPLAY — DAY | GAMEPLAY — NIGHT | REFERENCE: 3x / play-size / grayscale)

Round 2 verdict was ITERATE: the grayscale value-paddle wag was SOLVED and the
tail cleared the parcel, but the tail read as a DETACHED object (a striped flag
on a string) because of a sky gap between it and the body, and the DAY
silhouette lost the "bird" gestalt (head merged into a green lump). Every note
on the punch list is addressed below.

## What changed (punch list, in order)

1. **Tail re-anchored — the sky gap is killed.** The down-left sweep and the
   value paddle are KEPT, but the tail ROOT is now welded deep inside the
   lower-left flank:
   - Pivot pulled UP and IN toward body-centre (`TAIL_PIVOT_X/Y 22,46 → 26,43`).
   - The blade quad's near end is pushed BACK along the sweep axis past the
     pivot, up into the body (`root_back = 12`), so the root is buried under the
     green mass with no sky seam.
   - The root half-width is fattened (`root_hw = TAIL_HALF + 2`) so the neck
     never thins to a sky pixel after downscaling.
   - A lower-LEFT haunch lobe was added to the body (`_body`) so the green flank
     physically reaches the tail root even in the extreme leftward swing.
   - Frame 0 (the most extreme swing) was eased from 205° to 214° so its root
     stays under the flank while the tip still swings well left of centre.

   PASS TEST (per-frame scan at 40px, opaque-run split detection): frames 1, 2,
   and 3 have ZERO clean-sky pixels between tail and flank at every alpha
   threshold. Frame 0 shows one flagged 40px row, which the full-res alpha dump
   confirms is the body's natural belly concavity UNDER the centred feet — not a
   tail-to-flank gap; the tail root is continuously welded to the flank in all
   four frames. The 3x reference tile shows the tail growing out of the flank as
   one shape.

2. **Value bridged between flank and tail root.** A flank-matching mid-green
   (`TAIL_ROOT_GREEN #2C9E42`) floods the root third of the blade so one
   continuous green band flows out of the body into the tail. The dark/cream
   paddle only takes over PAST the root, so the dark base no longer cleaves the
   tail off. The cream keyline was dropped along the flank→tail seam — it now
   runs ONLY along the two outer (sky-facing) long edges and the tip cap, so no
   keyline fences the tail off from the body. The cream ribs were shifted to
   start past the green bridge so they belong to the swinging outer blade, not
   the welded root.

3. **Head/body step restored on the DAY frame.** A neck pinch is re-introduced:
   a dark contour arc (`BODY_CORE_D`) hugging the lower-left of the red head
   where it meets the green shoulder, drawn AFTER the head so it sits crisply on
   the seam, plus a short dark-green shadow line into the shoulder. The red head
   now steps off the body as a HEAD, not a ball sunk into a green lump — reads on
   day and night.

4. **Parcel untouched.** Pip's parcel is FIXED/centred by the game; no parcel is
   drawn here. The tail's territory is held in the lower-LEFT and the body shape
   keeps the centred parcel from crowding the tail.

## Kept (per the brief — did NOT touch)
- The grayscale value-paddle wag (dark base + cream ribs + scalloped cream-pom
  tip; a light/dark shape changing POSITION across the four frames — preserved on
  the grayscale strip).
- The tightened hooked-down cream beak.
- The red-head / green-body two-block identity.
- The no-legs silhouette (tiny tucked perch-claw nubs only).
- Night legibility (cream fringe keylines on body, head, and the outer tail
  edges carry the saturated party colours out of the dark).

## Confirmation
- `round_3.png` rendered via the shared helper at `docs/pinata/parrot/round_3.png`
  (`render.py` updated to output `round_3.png`).
- Zero sky-gap between tail and flank: the tail root is welded continuously to
  the lower-left flank in all four frames (per-frame 40px run-split scan +
  full-res alpha dump; the single frame-0 flag is the belly concavity under the
  feet, not a tail seam).
- The head/body step reads on the DAY frame (neck-pinch contour) — the red head
  no longer merges into the green body.
- The grayscale value-paddle wag is preserved (dark paddle changing position
  across the four frames on the grayscale strip).
