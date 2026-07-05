# CLASSIC TROLLEY — round 2

Round 1 got `VERDICT: ITERATE`: the flared basket + handle silhouette was
strong, but the SPINNING-WHEELS tell — the concept's whole motion premise —
failed at 40px. The fine spoke-cross was sub-pixel mush, the two near-black
tyres collapsed into one dark blob, and Pip's parcel fused with them. Round 2
rebuilds the wheels for legibility at true play size and clears the wheel zone.

## What changed (punch list)

1. **Bigger, fewer-detail wheels.** Tyre radius 6 → 8 (in the 64px build).
   Each wheel is now a FAT disc with a bright hub plate and a SINGLE bold
   spoke BAR — no fine 4-arm cross cut into a small disc.
2. **Spin re-told as a rotating BAR.** The single bar steps through four
   ABSOLUTE angles `_BAR_ANGLES = (90, 45, 0, 135)` — vertical → diagonal →
   horizontal → diagonal — one per spin phase, paired with the 1px bob. This
   replaces the round-1 `+ → ×` flip, which is nearly rotationally symmetric
   and read static. A rotating bar at ~45° steps is never self-similar
   frame-to-frame, so the rotation reads as MOTION even in grayscale.
3. **Tyres lifted off near-black.** Tyre is now dark STEEL `#4A5460`
   (`WHEEL_TYRE`) instead of near-black `#2B3138`. The bright keyline ring
   (`#F4F7FA`, r+1) carries each wheel's edge, so on a bright DAY sky the two
   tyres no longer muddy into one blob — each circle holds its own edge.
4. **Cargo moved OUT of the wheel zone.** The warm cargo block is seated HIGH
   in the basket (bottom at `top_y + 11`, near the flared mouth) instead of
   reaching down to basket centre. Nothing the skin draws occludes the wheels.
   Pip's parcel is composited by the game (not drawn here) and now rides in the
   clean central gap BETWEEN the two wheels rather than on top of them.
5. **Wider wheel track.** Track ±9 → ±13 (centres 26px apart vs a 16px tyre
   pair edge-to-edge), so a clear strip of sky shows between the two circles.
   The visible gap is what sells "two wheels" at 40px.
6. **Spin re-verified in grayscale at TRUE 40px.** Confirmed via the
   play-size + grayscale strips, not a 4x hero — see below.

## Kept from round 1

- Flared trapezoid basket (wide flared top, narrow base) as the dominant mass.
- Bright fat top RIM bar across the open mouth.
- Fat suggested verticals (no thin diagonals) + one fat mid rail.
- Rear handle-hook curl up off the back-right corner.
- Chrome vertical value banding (`STEEL_HI/MID/LO`, clamped to the trapezoid).

## Verified

- **Two distinct wheels at 40px DAY.** In the DAY gameplay frame and the
  play-size DAY swatch the two wheels read as separate bright-hub circles with
  a visible sky gap between them — no single dark blob. Dark-steel tyre +
  bright keyline ring per wheel carry the separation.
- **Rotating-bar spin reads in grayscale.** In the play-size grayscale strip,
  frame 0 (bar vertical) vs frame 1 (bar diagonal) are distinguishable with no
  colour help; the four bar angles step visibly through the cycle.
- **Parcel no longer fuses with the wheels.** The skin draws nothing in the
  wheel zone; Pip's composited parcel sits above/between the wheels, which stay
  clean and visible below the basket on both DAY and NIGHT frames.

## Contract (unchanged)

64×84 SRCALPHA canvas; basket mass centred at `(BCX,BCY)=(32,44)`
(`COMPOSITE_W=64, COMPOSITE_H=84, DY=12`). `build(wing_angle_deg) -> Surface`,
drawn UPRIGHT (velocity tilt applied later by the getter cache). 4 spin frames
driven by `_WING_ANGLES = (50, 20, -10, -40)`. Procedural pygame only; reuses
`game/parrot.py` and the `game/animal_ufo._make_prebuilt_skin` getter pattern
via the gameplay lib. The verdict frames are the DAY + NIGHT gameplay frames
at 40px in `round_2.png`.
