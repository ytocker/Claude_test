# HAND TRUCK / SACK BARROW — round 1

Concept 1 of 5 independent cart explorations. A flying two-wheel hand truck
(dolly) replaces Pip.

## The read

A tall narrow **L**: a long dark-steel handle-frame leaning back ~15° (the
long arm), a short toe-plate ledge at the floor (the foot), two wheels at the
elbow, and a stack of two kraft boxes strapped to the frame. Industrial,
leaning, angular — the only tall leaning L-frame in the cart set, so it can
never read as a basket. At true 40px the warm box stack + the dark leaning
frame + the elbow wheel resolve as "hand truck with a load" on both skies.

## Palette + double-duty keyline

| Part            | Colour    |
|-----------------|-----------|
| frame steel     | `#46525C` body / `#303A42` shade |
| frame keyline   | `#EDF1F4` (the double-duty highlight edge) |
| box kraft       | `#C99A5B` body / `#8A6433` shade / `#E0BA84` sunlit flap |
| tie-down strap  | `#262C34` with a `#7886?`-ish buckle catch-light |
| wheel           | `#2B3138` tyre / bright `#F0F4F7` keyline ring / `#D2DAE2` hub |

The `#EDF1F4` keyline runs down the LEADING edge of the frame bar, across the
grip and the toe plate, and rings each wheel. It does double duty: on a bright
DAY sky it holds the dark-steel silhouette (a near-dark bar otherwise
dissolves into blue); at NIGHT the lit edge IS the read, the rig glowing out
of the dark. The warm kraft boxes carry the day read independently — they pop
against `sky_bot ≈ (170,220,245)`.

## Frame map (the 4-frame tell — NO wings, NO particles)

`_WING_ANGLES = (50, 20, -10, -40)` → `_phase` 0..3. Two combined big-value
motions, both grayscale-safe:

| phase | box settle (px) | top-box extra | wheel spoke cross |
|-------|-----------------|---------------|-------------------|
| 0     | 0               | +0            | `+` upright       |
| 1     | 2               | +1            | `×` diagonal      |
| 2     | 1               | +0            | `+` upright       |
| 3     | 2               | +1            | `×` diagonal      |

- **Box settle:** the strapped stack drops 0–2px (and the top box a hair more)
  as if bouncing on the toe plate — a position shift, not a hue change, so it
  reads in grayscale.
- **Wheel spin:** the front-visible wheel cuts a dark spoke cross into its
  bright hub plate that flips `+ → × → + → ×` (a value flip inside a solid
  disc) — the rolling tell, also grayscale-safe.

## 40px risk + mitigations

- **L-arm vanishing.** The long arm of an L can read as a thin stick that
  blurs out. Mitigated by drawing the frame as a SOLID filled steel bar (not
  wire) with a shadow side, a hard contour, and the bright keyline — it stays
  a bar at 40px, confirmed in the render's play-size strip.
- **Rear wheel.** The dimmer rear wheel peeking behind the elbow is nearly
  lost at true 40px, but it is intentionally secondary; the bright front wheel
  carries the "two-wheel dolly" elbow read on its own. (A candidate round-2
  tweak: nudge the rear wheel up/left a touch for a clearer double-wheel read.)
- **Box-vs-Pip's-parcel collision.** Pip's parcel hangs just below centre and
  can read as another box; the frame+box stack is deliberately kept reading
  at/around centre (32,44) so the dolly's own load dominates.

## Lean vs. velocity tilt (contract caveat)

The ~15° back-lean is baked as a horizontal SHEAR about the body centre
(`_lean`), NOT a per-frame rotation: points above centre shift back toward the
handle, the toe plate shifts forward — the motion of tipping a real dolly back
onto its wheels. At 15° it stays MODEST, so when the getter later applies the
engine's velocity tilt a tilt-down still reads as a dive rather than fighting
the baked lean. Wheels are stamped AFTER the lean so they stay true circles
(a sheared circle would read as an ellipse).

## Contract conformance

- 64×84 SRCALPHA canvas; `COMPOSITE_W/H=64/84`, `DY=12`, `BCX,BCY=32,44`.
- dominant frame+box mass centred at (32,44); 14px collision circle lands in
  the box stack.
- `build(wing_angle_deg) -> Surface`; 4 frames driven by `_WING_ANGLES`.
- reuses `game.parrot._aaellipse` + `_WING_ANGLES`; getter via
  `game.animal_ufo._make_prebuilt_skin` (the gameplay lib wires it).
- drawn UPRIGHT with the lean baked in; NO wings, NO live particles; procedural
  pygame only.

## Render

`round_1.png` = GAMEPLAY DAY | GAMEPLAY NIGHT | REFERENCE (3x / play-size /
grayscale). Reads as a leaning L-frame hand truck with a strapped box load at
40px on both skies; the box-settle + wheel-spin tell is visible across the 4
reference frames and survives the grayscale strip.
