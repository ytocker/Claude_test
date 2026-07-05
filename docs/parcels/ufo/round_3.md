# MINI UFO — Round 3

Sheet: `docs/parcels/ufo/round_3.png`
Build: `docs/parcels/ufo/build.py` → `render.py` →
`SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python docs/parcels/ufo/render.py`

Round 2 verdict was ITERATE: the standalone tilt strips were signed off and the
dropped disc helped, but in the CARRIED read the BEAM — the required tractor-beam
tell — was gone, reduced to a few pale specks under Pip, and the disc's left
third was lost behind his tail. Both are fixed; the standalone strips and the
hero dome/disc proportions are untouched.

## What changed (priority — carried read)

1. **Hard-edged beam with a solid near-white core column.** The soft additive
   gradient cone is replaced by a HARD-EDGED trapezoid built in three stacked
   passes (`_hard_beam`, near-flat alpha): a thin teal `BEAM_EDGE` outline, a
   teal `BEAM_GLOW` fill, and a SOLID near-white `BEAM_CORE` (#F4FFFC) column
   down the middle. Because the disc + its inflated keyline are drawn after the
   beam and overpainted the column's top rows (crushing it to ~2px after
   smoothscale), the core + frame are RE-EMITTED on top of the disc just below
   the lip — so a full hard column erupts from the rim. The tell is now value,
   not hue: a bright bar that wins the value fight against day clouds and the
   night purple.

2. **UFO nudged 2px right + low.** The whole stack moved off the canvas centre
   (`cx = SIZE//2 + 4`, i.e. +2px at 1×) and the disc weighted low
   (`disc_cy = 26`) so the FULL chrome ellipse + both rim points clear Pip's
   wing/tail — the left third no longer disappears behind his tail in carry.

3. **Near-white core + thin teal outline, not hue-only.** The core no longer
   relies on the teal hue (which failed grayscale / colourblind and lost the
   value fight). It is near-white, framed by a thin teal `BEAM_EDGE` so it still
   reads as a teal beam in colour while holding on value alone in grayscale.

KEPT: the standalone tilt strips and the hero dome/disc proportions (unchanged
geometry); the teal lower-rim that snaps the disc off Pip's red; disc + beam
weighted to the bottom of the sprite.

## Read confirmation (carry crops + 1× pixel audit)

Pixel audit of the final 22px sprite (disc lower rim ≈ y16):
- **Solid near-white beam core below the disc rim: 6px** (rows y16–y21).
- **Full teal-framed beam below the rim: 7px** (rows y15–y21).

This clears the ~6–8px target.

- **Day carry:** the full wide chrome disc clears Pip's tail, the teal lower rim
  snaps it off his red belly, and a solid bright near-white beam column with a
  teal frame erupts well below the disc rim. Unmistakable tractor-beam at 22px.
- **Night carry:** same — the near-white core holds against the night purple
  (value-first), so the beam reads just as strongly as on the day sky.
- **Tilt row (day/night/grayscale):** the saucer silhouette holds across the
  bank arc and the hard beam survives the GRAYSCALE swatch — confirming the read
  no longer depends on the teal hue.
