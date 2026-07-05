# MANTIS SHRIMP skin — Round 3 (final pass)

`skin_mantis_shrimp` · production build in
`docs/animals/mantis_shrimp/mantis_shrimp_skins.py`. Sheet:
`docs/animals/mantis_shrimp/round_3.png` (hero cocked/level + punch on day AND
night; 40px smooth + 40px NEAREST x3 cock / punch+dive on both biomes).

Round-2 verdict was ITERATE with a tight must-fix list — restore the two-fist
strike, drive the punch across the snout. This pass applies ONLY those notes.

## Frozen (untouched from round 2)

- Teal + orange duotone shield structure, two load-bearing orange stripes.
- Iridescent eye-jewels + banded gold/cyan mid-stripe (third accent).
- 3px eye-stalks (dark rim + core) with the hot specular pixel.
- 1px dark body contour (house outline in `_make_prebuilt_skin`).
- Night glow on eye-jewels + lead club-tip ONLY; body stays flat duotone.

## Must-fix applied

1. **Second club restored as a separate orange mass.** The fists are no longer
   built as one self-contained surface that collapsed into the belly. Both
   arms now draw in ABSOLUTE world coordinates (`_club_arm` takes explicit
   shoulder/elbow/fist points) so each fist is aimed independently. The rear
   fist parks LOWER than the lead fist in every pose with clear sky between
   them — two distinct orange masses read in cocked, level, punch, and dive on
   both the 130px hero and the 40px NEAREST x3 truth tiles.

2. **Punch crosses the snout.** On the up-pose the lead fist interpolates to
   `(hcx+15, hcy-10)` — up + forward, landing OVER the snout/eye region — and
   the striking-face spark is now oriented along the shoulder→fist throw vector.
   The orange mass overlaps the snout vector instead of dangling down-left under
   the gut, so the up-pose reads as a haymaker, not a dive with trailing legs.

3. **Dominant lead-club→snout diagonal.** With the rear fist driven low and the
   lead fist driven up-forward, the punch poses resolve to a single clean
   diagonal from the orange lead fist up to the jewel periscopes — the tell
   that sells "strike" at 40px.

## Contract (unchanged)

- `build_mantis_shrimp(wing_angle_deg) -> Surface` (64×84 SRCALPHA), day build.
- `get_mantis_shrimp = _make_prebuilt_skin(build_mantis_shrimp)` cached getter.
- `BUILDERS = {"skin_mantis_shrimp": get_mantis_shrimp}`.
- `build_mantis_shrimp_night` / `get_mantis_shrimp_night` remain for review
  parity only; the single production API is unchanged.

Verified: module imports headless, all 4 frames render non-empty, `BUILDERS`
maps the one production getter. `round_3.png` written (1094×576).
