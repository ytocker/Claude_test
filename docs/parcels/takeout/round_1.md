# TAKEOUT PAIL — Round 1

LOW-tier parcel cosmetic for the PARCELS store tab. The classic Chinese-takeout
paper pail Pip carries below him.

## 22px read
- **Body:** a TRAPEZOID narrower at the BASE (top half-width 14, base half-width
  10 at 2×) — the inverted taper is the pail's primary tell vs. a gift box.
- **Handle:** a thin ARCHED wire loop rising from two feet on the box rim. Drawn
  3px grey on a 5px dark keyline at 2× → ~2px wire at 22px, so the loop survives
  the smoothscale. The trapezoid + half-circle arch is a self-contained glyph.
- **Top flaps:** a red fold band with a central V notch reads as the two crimped
  paper flaps even after fine detail collapses at 22px.

## Palette
- DAY — white body `#F4F1EA` (lit `BODY_HI` → shaded `BODY_LO` vertical
  gradient), red fold-flap accent `#D33A2C`, grey wire `#7A7A82`.
- NIGHT — the white paper body self-lights; a 1px lit left edge + the dark
  keyline keep the silhouette crisp against `(18,22,48)` without a heavy outline.
- A dark high-value `OUTLINE (40,28,24)` keyline is baked around the body and
  under the wire so the pail reads on the bright day sky `(170,220,245)`.

## Tilt survival
Across −25/0/30/60/90° the arched handle stays a recognizable loop and the
trapezoid taper is still legible — the handle was drawn thick (and over the dark
keyline) specifically so banking doesn't erase it. Verified on the DAY, NIGHT,
and GRAYSCALE tilt rows in `round_1.png`.

## 22px risk
- **Wire handle** is the highest-risk element: at 22px the 2px loop is near the
  floor of legibility. Mitigated by the 5px dark backing stroke + a 1px highlight
  arc; if the art-director finds it too faint when banked, thicken the keyline or
  raise the arch.
- The red flap band can read as a single stripe rather than two flaps at the
  smallest size — the central V notch is the only separator and may need
  widening.
- Drop shadow reads slightly dark on the checker hero; it is subtle in-scene.
