# Concept — THE BLACK TRIANGLE (TR-3B) · round 1

`docs/animals/ufo_redesign/concepts/triangle/round_1.png`
(DAY gameplay | NIGHT gameplay | reference: 4 frames @3x / play-size / grayscale)

## Read

The hard-edged counterpoint to a set otherwise full of rounded saucers. A
**broad flat isosceles wedge** — 54px base, ~23px tall, so it is clearly WIDER
than it is tall and never collapses into a generic upward arrow. ZERO
curvature anywhere on the body: every edge is a straight line, the three
corners flat-clipped with a short bevel for the stealthy-slab read (not needle
tips). In pure black silhouette it resolves as a triangle and nothing else.

The instant 40px read is "black-triangle UFO": a dark hard slab carrying three
bright corner lights. Confirmed at true play-size on both skies — the wedge
silhouette survives the downscale and the three red corner dots pop.

## Palette

- Body: subtle top-down gradient `#3A3F4A` (top) → `#23262E` (base),
  masked to the wedge so the flat slab reads as lit metal rather than a sticker.
- `#9AA3B2` high-value keyline baked on the **lower edges only** (the two long
  edges + base + shoulder bevels), drawn 2px so it survives downscale. This is
  what holds the near-black slab against the night sky — see the NIGHT play
  strip where the lower rim stays crisp.
- Two faint hull seams (apex→base + one cross seam) break the dead-flat mass
  into three panels without adding any curve.
- Corner beacons: classic government-triangle red `#E8472C`, with a hot white
  pip in the lit corner, mid-red in the trailing corner, deep `#601E14` in the
  dim corner. (Cyan colorway constants are commented in `build.py`.)

## Beacon across the 4 frames (the rotating-light tell, no wings/particles)

Driven by `_WING_ANGLES = (50, 20, -10, -40)` → `_phase()` → 0..3:

| frame | phase | brightest corner | trailing (mid) | reads as |
|-------|-------|------------------|----------------|----------|
| 1 | 0 | top apex | bottom-left | light at the top |
| 2 | 1 | bottom-right | top apex | light moved CW |
| 3 | 2 | bottom-left | bottom-right | light moved CW |
| 4 | 3 | none — all three dim + wide bloom | — | beacon "off"/breath |

The trailing corner glowing mid-bright makes the eye read a single light
**travelling around the rim** rather than three lamps blinking. Pure brightness
sequencing → grayscale-safe (verified on the grayscale strip: the lit corner is
clearly the brightest pip in every pose).

## Contract

64×84 SRCALPHA canvas, body mass centred at (BCX,BCY)=(32,44), drawn UPRIGHT
(no baked rotation — velocity tilt applied later by the getter). `build(wing_angle_deg)`
returns the Surface; the 14px collision circle at (32,44) sits inside the wedge
mass. Reuses `_make_prebuilt_skin` from `game/animal_ufo.py` plus parrot
`_add_outline`/`_aaellipse` parity. Procedural pygame draw calls only.

## 40px risk

- Pip's parcel hangs just below centre and overlaps the lower-base region; the
  apex light and the two bottom-corner lights still ride the rim outboard of the
  parcel, and the keyline holds the wedge edges around it. Worth confirming the
  bottom-corner lights never sit fully behind the parcel in motion.
- The house `_add_outline` wraps the slab in a 1px dark halo that very slightly
  softens the hard corners at the smallest scale — the straight edges still read,
  but a thinner/lighter outline or a stronger keyline could sharpen the
  "hard slab" identity further if the director wants more edge.
- Three flat panels + seams are barely visible at play-size (intended — they're
  texture, not a read), so they cost nothing but could be dropped if they muddy.
