# HAND TRUCK / SACK BARROW — round 2

Round 1 got `VERDICT: ITERATE` — at 40px it read as a "wagon of boxes": the
frame lost to the box stack, load + frame sheared together with no vertical
anchor, the double-wheel cue muddied into one fat tyre, the spoke-cross was
sub-pixel, and the box stack fused with Pip's parcel. Round 2 inverts the
gestalt so the FRAME is the silhouette.

## What changed (punch-list, in order)

1. **Frame is now the silhouette, not the boxes.** The handle-arm is stood up
   as a clear near-VERTICAL steel bar on the TRAILING (right) edge, run full
   height (`frame_top = BCY-26` → `frame_bot = BCY+20`) and thickened, capped
   by a bold handle grip. The box stack is rebuilt as ONE more UPRIGHT, squared
   block hugging the bar's FRONT (near-vertical sides — only the small 2px
   frame-tip shear remains). Target gestalt — a tall steel "I" with a warm
   block hugging its front and a wheel at the foot — now reads at 40px.
2. **Baked lean cut from 15° → 9°, and re-pivoted.** `LEAN_DEG = 9`, and
   `_lean` now pivots the tip about the WHEEL/foot (`_PIVOT_Y = BCY+18`) rather
   than the body centre — so the foot stays planted and the handle swings back
   (a wheels-forward TIP), instead of a uniform same-direction shear of load +
   frame. Gentle enough that the getter's velocity tilt still reads as a dive
   (a tilt-down rotates the whole upright rig nose-down; the 9° baked tip no
   longer fights it the way 15° did).
3. **Committed to ONE bold front wheel.** The faint half-hidden rear wheel is
   dropped. The remaining wheel is bigger (`r=8`), with a bright keyline ring
   and a large hub plate — one bold spoked disc reads better at 40px than two
   muddy ones.
4. **Spoke-cross rescued.** The hub plate is enlarged (`hub_r = r-1`) and
   brightened; the spokes are now full-DISC diameter lines (drawn `cx-d → cx+d`,
   not a radius) so the cross is a hard dark value flip across the entire bright
   plate. The `+ → × → + → ×` rotation survives the play-size and grayscale
   strips.
5. **Box mass separated from Pip's parcel.** The block is pulled UP
   (`box_top = BCY-19`, `box_bot = BCY+10`) so its mass sits clearly ABOVE the
   parcel zone the game composites just below centre — confirmed in the
   composited DAY and NIGHT gameplay frames (the parcel reads as its own small
   element below the dolly load, not fused into it).
6. **Body anchored horizontally across the 4 frames.** Geometry is expressed
   from fixed `BCX/BCY` anchors and the only per-frame deltas are the vertical
   `settle` offset and the wheel spoke orientation — no rightward drift; the
   only motion is the box-settle + wheel spin.
7. **Toe-plate read added at 40px.** A short steel ledge juts FORWARD of the
   wheel (`toe_front = BCX-17`) with a bright `#EDF1F4` keyline pixel-row along
   its leading edge — the "hand truck, not wagon" tell, visible at play size.

## Kept (per brief)

- Kraft box palette `#C99A5B` + sunlit `#E0BA84` flap.
- The `#EDF1F4` keyline double-duty strategy (holds the dark-steel silhouette
  on the bright DAY sky; IS the read at NIGHT, glowing off the frame edge, the
  toe-plate row, and the wheel ring).
- Box-settle (0–2px) as the primary tell, paired with the wheel spoke cycle.

## Confirmation at 40px (day + night)

`round_2.png` = GAMEPLAY DAY | GAMEPLAY NIGHT | REFERENCE (3x / play-size /
grayscale), rendered via the shared `_gameplay_lib` helper.

- **Tall-I-frame gestalt reads at 40px** on both skies: the vertical handle bar
  + grip cap dominates the silhouette, the squared kraft block hugs its front,
  the bold wheel sits at the foot, and the toe-plate juts forward.
- **Wheel + spoke spin read:** one bold spoked disc with a bright hub; the
  full-disc spoke cross flips `+ → × → + → ×` across the 4 frames and survives
  the grayscale strip.
- **Load separates from Pip's parcel:** in the composited day and night frames
  the dolly's box block reads above centre and Pip's parcel reads as its own
  element below it — no fusion.

## Contract conformance (unchanged)

64×84 SRCALPHA canvas; `BCX,BCY = 32,44`; `build(wing_angle_deg) -> Surface`;
4 frames driven by `_WING_ANGLES = (50,20,-10,-40)`; reuses
`game.parrot._WING_ANGLES`/`_aaellipse`; drawn UPRIGHT with the tip baked in;
NO wings, NO live particles; procedural pygame only.
