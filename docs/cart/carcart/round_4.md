# KIDDIE CAR-CART — Round 4 (final pass)

Sheet: `docs/cart/carcart/round_4.png`
(GAMEPLAY — DAY and GAMEPLAY — NIGHT at ~40px are the verdict frames.)

## The single residual addressed
Round 3 was strong (3 of 4 checks PASS + LOCKED). The art-director's final
note flagged ONE narrow residual: at 40px the rear read as a soft warm
BUNDLE/SACK rather than a woven BASKET — the staves blurred and one arc-rail
carried it alone. This pass fixes that surgically, touching ONLY the rear
basket geometry/shading.

## What changed (rear basket only)
1. **Open MOUTH, not weave (bundle→basket flip).** The top edge is now a clear
   CONCAVE ELLIPSE: a dark interior-shadow rim (`BASKET_BODY_D`) hugs the BACK
   lip, with a lighter interior pocket (`BASKET_IN`) dropped 2px BELOW it and a
   dark floor crescent under that. The eye now reads DOWN INTO the box instead
   of across a domed top. This one ellipse stack is the change that flips the
   read.
2. **Two staves, front face only.** Replaced the three across-the-curve staves
   (which became noise at 40px) with TWO 2px dark verticals on the FRONT wall,
   starting below the open mouth and running full-height to the floor where
   they hold the most pixels and the highest contrast against the (now darker)
   terracotta.
3. **Silhouette notch.** Added a 2px dark rim-lip OVERHANG (`TRIM_DARK`) where
   the back wall meets the arc-rail, breaking the smooth top-back corner so the
   OUTLINE itself carries the basket read — a cue that survives downscale when
   interior detail does not.
4. **Rear one value-step darker (day-tightening).** `BASKET_BODY` moved
   `#B0604A → #A25642` (same terracotta hue, one step down). Against the bright
   DAY sky this lets the candy-red hull lead more cleanly; against the dark
   NIGHT sky the step is negligible, so the single shared sprite honours the
   day-only nudge without a per-sky build. Night, already correct, is visually
   unchanged.

## Confirmed reads at 40px (round_4.png)
- **DAY gameplay frame:** rear reads as an OPEN-MOUTH basket — concave top
  ellipse + 2 front staves + silhouette notch — riding behind a candy-red toy
  car. Red clearly leads; the rear recedes.
- **NIGHT gameplay frame:** same open-box read holds; rear value relationship
  unchanged from the signed-off r3.
- Toy-car silhouette intact: bubble cabin, hood scoop, bumper, fat red-hubcap
  wheels.

## Locked items — untouched (verified by diff scope)
- Bounce system (dome protection, +2px width-squash cap, vertical travel,
  wheel-spread) — `_BOUNCE`, cabin-radius protection, body/wheel code all
  unchanged.
- Red-leads hierarchy + candy-red hull value win.
- Parcel hue/value separation (no parcel drawn here).
- Rest-frame toy-car silhouette.
- Warm terracotta colour FAMILY for the rear (hue preserved; only a single
  value step on the wall).
