# Sugar Glider — Animal Store skin · Round 3 (final pass)

Round-2 verdict was **ITERATE** with a minimal three-item must-fix list. Round 3
applies ONLY those three fixes and freezes everything the critique said was
working. Single production build, contract unchanged:
`build_sugar_glider(wing_angle_deg)` → `get_sugar_glider` →
`BUILDERS = {"skin_sugar_glider": get_sugar_glider}` (liftable straight into
`game/animal_skins.py`). 64×84, body (32,44), 4 poses, procedural-only, WHY-only.

Sheet: `docs/animals/sugar_glider/round_3.png` — hero 130px + 40px NEAREST x3
(level + dive) on DAY, PALE-CLOUD, NIGHT, plus the glide-cycle strip.

---

## Frozen (untouched per the critique)
Dark membrane rim (crisp on day + pale-cloud), squared kite corners, capped
belly glow, bat-distinctiveness (flat horizontal kite + round ears), and the
spread/tuck silhouette endpoints.

---

## Must-fix — what changed (only these three)

1. **Spine stripe now LIGHT, and survives 40px night.** The old `_SPINE` /
   `_SPINE_D` were *darker* than the slate fur, so the stripe drowned dark-on-dark
   at gameplay scale. It is now a SINGLE light stroke at the leading-edge
   highlight value (`_SPINE = _FUR_H`, one value step LIGHTER than the fur), 2px
   in the 64px build so it lands as a solid 1px line at 40px. It runs UNBROKEN
   from the tail root, over the body, up onto the brow — and is now drawn AFTER
   the head fill so the brow segment isn't overpainted, keeping it one continuous
   line. Verified on the 40px NIGHT level + dive magnifications: the light spine
   reads as one stroke across the back and brow.

2. **Eyes no longer fuse at 40px.** Each eye's dark fill is pulled a full step
   inside the rim (pupil radius `r-2` instead of `r-1`) so the mint reads as a
   clean RING around a small dot rather than a dark disc. The dark mask rings are
   held apart and a 2px fur separator column is re-asserted between them in the
   64px build, which survives as a real ~1px column at 40px. Confirmed on the
   worst case (40px NIGHT dive AND level): two distinct mint-rimmed dots with a
   visible separator, no single dark blob.

3. **Mid-cycle delta pushed monotonic.** The two mid frames previously sat
   near-identical. A centre-EXPANDING remap of the pose factor
   (`fm = clamp(0.5 + (f-0.5)*1.7)`) stretches the mids away from 0.5 — one mid
   pulled toward the spread, the other toward the tuck. Half-span now sweeps
   14 → 17 → 24 → 27 px across the four frames (vs the old flat 14 → 18 → 22 → 27),
   with `droop` 6 → 5 → 1 → 0 and `flat` 0 → 1 → 2 → 3 tracking it, so the
   membrane visibly travels every frame. The glide strip is relabelled to the
   true frame order (tucked → mid-tuck → mid-spread → spread).

---

## Verification
- 40px NEAREST x10 NIGHT magnifications (level + dive) confirm fixes 1 and 2 at
  the worst-case read: continuous light spine, two separated eyes.
- The glide-cycle strip confirms fix 3: monotonic, visibly travelling membrane.
- Endpoints (full spread / full tuck), rim, square corners, capped belly, and
  bat-distinctiveness are unchanged from the round-2 build that the critique
  signed off on.
