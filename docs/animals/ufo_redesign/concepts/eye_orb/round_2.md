# EYE-ORB — `skin_ufo` concept, round 2

Round 1 got `VERDICT: ITERATE`: right category (pure light) but the dark keyline
ring was too heavy and read as a dark hardware donut with a dot inside, and the
blink amplitude was too small to read in motion. Round 2 keeps the pure-light
identity — concentric pupil / halo / iris-ring / field stack, opposing-boundary
motion, no dome / rim / hardware — and amplifies it per the punch list.

## What changed

1. **Halved the keyline + pushed the rim glow OUTWARD.** The keyline dropped
   from a 2px, alpha-165 contour to a 1px, alpha-92 hairline. A bright cyan-WHITE
   rim-light (`RIMLIGHT = (190,240,255)`) now runs 4px wide and hot right at the
   body edge, drawn additively LAST so it overlaps and washes out the keyline's
   inner edge. The day read flips to "cyan glow with a crisp containing edge".

2. **Falloff ramp replaces the dark wall.** `_radial_orb` now ends the opaque
   body on the new MID cyan band (`IRIS_MID = (60,182,240)`) instead of deepening
   to navy at the rim — the body value RAMPS down gradient-style (bright iris →
   mid cyan → rim-light → bloom) so the edge steps into the bloom instead of
   hitting a dark contour. The dark navy is no longer in the disc at all.

3. **Cranked the blink amplitude ~40% and split frames 1/3.** Pupil radius range
   widened from `4.6→1.2` to `5.5 (fat) → 0.8 (pinpoint)`; the iris ring now
   travels `0.40 → 0.92` of the orb radius (was `0.46 → 0.84`). Frame 1 (`core
   3.4, ring 0.62`) and frame 3 (`core 2.2, ring 0.74`) are now clearly distinct,
   so the loop has FOUR beats: fat-open → narrowing → pinpoint-flare → distinct
   re-open. Per-frame pupil delta is ≥2–3px at 40px.

4. **Bloom flares at the pinpoint.** The pinpoint frame's `bloom` multiplier
   jumped to `1.40` (was `1.14`); the `_glow_dot` halo and the rim-glow reach
   both scale with it, so the whole orb visibly FLARES wider and hotter the
   instant the pupil vanishes — the premium tell.

5. **Warmed the pupil** from `#FFFFFF` to `(235,250,255)` so it reads as living
   plasma rather than a clinical LED.

6. **Night protected.** The lighter keyline + ramp don't let the bloom smear: the
   night swatch keeps a crisp concentric ring and the rim-light gives the orb a
   defined glowing edge against the dark sky, sharpest at the pinpoint frame.

## Confirm at 40px

- **DAY:** first read is GLOW — a cyan-white luminous orb with a bright crisp
  containing edge feathering into a cyan bloom. NO dark donut; the faint keyline
  is washed out by the rim-light.
- **NIGHT:** a glowing eye with crisp concentric pupil/ring structure, no
  shapeless smear.
- **Blink = 4 distinct beats:** fat warm pupil + tucked ring → mid pupil + ring
  stepping out → pinpoint spark + ring at rim + bloom flare → distinct smaller
  re-open with ring at an intermediate radius. Reads in motion and survives the
  grayscale strip (pupil shrinks, ring sweeps out with all colour removed).

## Render

`SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python
docs/animals/ufo_redesign/concepts/eye_orb/render.py` →
`round_2.png` (DAY gameplay | NIGHT gameplay | reference column). The DAY and
NIGHT gameplay frames at 40px are the verdict.
