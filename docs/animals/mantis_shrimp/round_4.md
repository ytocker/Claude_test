# MANTIS SHRIMP skin — Round 4 (FINAL designer pass)

`skin_mantis_shrimp` · production build in
`docs/animals/mantis_shrimp/mantis_shrimp_skins.py`. Sheet:
`docs/animals/mantis_shrimp/round_4.png` (hero cocked/level + punch on day AND
night; a large COCKED 40px NEAREST x4 read up top of each game panel, plus 40px
smooth and 40px NEAREST x3 cock / punch / dive on both biomes).

Loop budget is spent after this pass — it ships as-is. This pass applies ONLY
the round-3 must-fix list and touches NOTHING else.

## Frozen (NOT touched)

- PUNCH-pose arm geometry — the lead club crossing the snout and the dominant
  lead-fist→jewel diagonal. The rear arm's `s=1` endpoints (shoulder
  `(bcx+4,bcy+6)`, elbow `(bcx+13,bcy+8)`, fist `(bcx+21,bcy+10)`) are byte-for-
  byte what they were; the lead arm is fully untouched; the lead glow radius at
  `s=1` evaluates to 5, exactly the previous punch bloom. Punch frames are
  identical to round 3.
- Teal + orange duotone, two load-bearing orange stripes.
- Iridescent eye-jewels + banded gold/cyan mid-stripe (third accent).
- 3px eye-stalks (dark rim + core) with the hot specular pixel.
- 1px dark body contour (house outline in `_make_prebuilt_skin`).
- Night glow on eye-jewels + club-tips ONLY; body stays flat duotone.

## Must-fix applied (cocked/level pose only)

1. **Rear fist pushed clear of the body and the orange stripes.** In the
   cocked/level branch (`s=0`) the rear arm's shoulder/elbow/fist were re-aimed
   LOW + BACK — `far_fist` cocked target moved to `(bcx+4, bcy+20)` (dropped
   well below the shield's bottom edge and pulled left of the lead club), with
   the shoulder/elbow routed down so the limb no longer smears across the orange
   stripes. At 40px NEAREST on both day and night the rear fist now reads as its
   own orange mass with a clear dark gap above it (to the stripes) and to its
   right (to the lead club). Two distinct orange fists read in the cocked/level
   pose — verified at 40px on day and night. The punch (`s=1`) endpoints were
   left frozen, so only the cocked end of the interpolation moved.

2. **Night cocked club-tip halo pulled in.** `_club_arm` now takes an optional
   `glow_r`; the lead call passes a pose-dependent radius
   `int(round(3 + s*2))` — tight (3) when cocked so the halo no longer blooms
   into one hot ball that erased the two-mass read, widening to 5 at the punch
   (unchanged from before). On night, the lit lead club and the unlit rear fist
   now present as two separate orange masses beside each other.

## Contract (unchanged)

- `build_mantis_shrimp(wing_angle_deg) -> Surface` (64×84 SRCALPHA), day build.
- `get_mantis_shrimp = _make_prebuilt_skin(build_mantis_shrimp)` cached getter.
- `BUILDERS = {"skin_mantis_shrimp": get_mantis_shrimp}` — the single
  production API.
- `build_mantis_shrimp_night` / `get_mantis_shrimp_night` remain for review
  parity only.

Verified: module imports headless, `BUILDERS` maps the one production getter,
all 4 frames render non-empty. `round_4.png` written (1094×576).
