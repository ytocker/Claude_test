# EYE-ORB — `skin_ufo` concept, round 1

A glowing sentient plasma sphere: the flyer is basically one giant blinking
eye-light. The point of this concept is **category**, not detail — it is a
floating LIGHT, not a metal craft, so it can never be mistaken for the old
domed-saucer designs the redesign rejected. Pure orb: no dome, no saucer rim,
no hardware. Identity lives entirely in the GLOW and the concentric eye
structure.

## What it is / the read at 40px

A perfect circle of bright cyan light with a clear concentric structure:

- a hot **white pupil** at the centre,
- a brighter cyan **catch-light halo** hugging the pupil,
- a mid-cyan **iris ring** orbiting it,
- a luminous **cyan iris field** filling the orb,
- a **rim glow** that bridges the body into a soft outer **bloom**.

At true play size (~40px) the verdict frames show a glowing cyan eye sitting on
Pip's parcel body — instantly "alien energy orb / blinking eye", never "flat
dot" and never "saucer". The concentric pupil-in-iris read is the silhouette's
whole identity, so it survives the smoothscale where a hull's fine detail would
not.

## Palette

| token      | hex / rgb            | role                                          |
|------------|----------------------|-----------------------------------------------|
| `CORE`     | `#FFFFFF`            | hot white pupil (the contracting bright mass) |
| `IRIS_HI`  | `(150,230,255)`      | brightened iris so the body survives downscale|
| `IRIS`     | `#48D1FF (72,209,255)` | canonical iris cyan (body lift + pupil halo)|
| `IRIS_DEEP`| `(40,150,214)`       | iris ring + rim of the body gradient          |
| `RIM`      | `#1B4E8C (27,78,140)`| deep-rim reference colour                     |
| `BLOOM`    | `(96,198,255)`       | additive corona / rim glow (blooms at night)  |
| `KEYLINE`  | `#0E2A4A (14,42,74)` | mandatory day edge contour                    |

Core `#FFFFFF` → iris `#48D1FF` → rim `#1B4E8C`, exactly as briefed, with the
additive bloom baked around the rim.

## The iris pulse across the 4 frames (the motion tell)

No wings, no live particles — the whole life is a **slow breathing blink**
baked into the 4 frames. `_WING_ANGLES = (50,20,-10,-40)` maps to phase 0→3 via
`_phase()`, and each phase pulls a keyframe from `_PULSE`:

| phase | `_WING_ANGLES` | pupil `core_r` | iris ring `ring_t` | bloom | reads as            |
|-------|----------------|----------------|--------------------|-------|---------------------|
| 0     | 50             | 4.6 (fat)      | 0.46 (tucked in)   | 0.92  | eye wide open       |
| 1     | 20             | 2.8            | 0.64               | 1.00  | narrowing           |
| 2     | -10            | 1.2 (pinpoint) | 0.84 (at the rim)  | 1.14  | mid-blink pinpoint  |
| 3     | -40            | 2.8            | 0.64               | 1.00  | re-opening          |

Two boundaries move in **opposition**: as the white pupil contracts to a
pinpoint, the bright iris ring EXPANDS outward toward the rim, and the bloom
peaks at the pinpoint. That counter-motion of a bright/dark boundary is the
loudest grayscale signal in the set — the bottom grayscale strip shows the
pupil shrinking and the ring sweeping out even with all colour removed, so a
colourblind player still reads a live pulse, not a static dot. It loops 0→3→0
as a smooth inhale/exhale rather than a hard on/off blink.

## The day blow-out risk + how the keyline solves it

A bright cyan orb on the day biome's pale-blue top band (`sky_bot ≈
(170,220,245)`) is at real risk of dissolving at the edges — its value is too
close to the sky. **The mandatory fix is the `#0E2A4A` keyline ring** (step 5),
a thin dark contour at the orb's circumference that bites against the brightest
sky and holds a hard, readable circle. The DAY gameplay frame and the day
play-size swatch confirm the orb keeps a crisp edge.

Crucially the keyline is **semi-transparent (alpha 165) and drawn BELOW the rim
glow**, not a hard opaque black ring. A fully opaque keyline is exactly what
turns a bright disc into "a dark vignette ring + a dot" when downscaled to
40px (the failure this concept exists to avoid); the additive rim glow then
lifts cyan back over the keyline's inner edge so the body flows into its bloom
with no dark gap. The keyline costs nothing at night — the bloom and rim glow
sit over it and the orb glows hard out of the dark sky.

## Contract compliance

- 64×84 SRCALPHA canvas, orb mass centred at `(BCX,BCY)=(32,44)`; the iris tell
  sits above where Pip's parcel hangs.
- `build(wing_angle_deg)` returns the upright Surface; 4 frames driven from
  `_WING_ANGLES`, NO baked rotation (velocity tilt applied later by the getter).
- Procedural pygame draws only; reuses `parrot._aaellipse` and an
  `animal_ufo`-style `_glow_dot` radial-glow helper for the bloom; the
  cached `(frame, tilt)` getter comes from `animal_ufo._make_prebuilt_skin`.

## Render

`SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python
docs/animals/ufo_redesign/concepts/eye_orb/render.py` →
`round_1.png` (DAY gameplay | NIGHT gameplay | reference column).
