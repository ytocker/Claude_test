# STAR PIÑATA — round 1

## The read
The classic 7-point star piñata, the original piñata shape. A fat round purple
core hull with **seven stubby cone spikes radiating outward** like a spiky
party-sun. The silhouette is the whole point: all radial points, instantly
non-creature. Nothing else in the flyer roster has radial spikes, so at 40px
the eye locks onto "spiky star party-ball" before any detail resolves.

Cones are deliberately STUBBY and **fringe-tipped** (a cream pom cap, not a
needle) so no point thins out and vanishes at gameplay scale. The top point is
centred upward; the remaining six are spaced evenly around the circle.

## Palette
- Hull: mid purple `#7A3FB0` body, `#4E2476` shade, `#A46ED6` upper sheen.
- Cone tips alternate the three candy colours around the star:
  magenta `#E8307A`, cyan `#1FB6D6`, gold `#F4C233` (each with a darker
  shade half so the cones read as 3-D, not flat triangles).
- Cream crepe fringe rim `#FFF4DA` (+ `#D6C49E` shade) keylines every cone and
  wraps the hull as two short-tick fringe bands — the layered crepe-paper read
  AND the night-survival keyline in one element.
- Candy-glow seam: hot cream `#FFF6D6` core over a warm amber `#FFC46E` halo;
  the dark crack itself is `#26123A`. Spilled candy dots in magenta/cyan/gold.

## Crack-&-glow tell across the 4 frames
No wings, no live particles. A horizontal seam sits at `cy-3` (at/above the
hull centre, so Pip's parcel hung below never hides it). `_WING_ANGLES =
(50,20,-10,-40)` maps through `_phase` to four crack stages with opening
fractions `(0.10, 0.55, 1.00, 0.42)`:

1. **Stage 0 (sealed)** — a thin dark seam line, faint glow. The "resting" pose.
2. **Stage 1 (parting)** — seam opens to a glowing lens; warm bloom builds.
3. **Stage 2 (widest)** — full crack, hottest candy-glow lens, **1–2 candy dots
   peek through** the gap (sweets about to spill).
4. **Stage 3 (snap back)** — eases toward shut so the loop snaps closed cleanly.

The opening is non-monotonic so the cycle reads as a living "breath/pulse",
not a one-way wipe. It is **value-first**: a dark crack lip (top + bottom)
opening over a bright interior. The grayscale strip in the sheet confirms the
tell survives with no hue — a pure value pulse. The warm glow is drawn additive
so it BLOOMS out of the dark hull at night (where it becomes the bright anchor),
while a solid non-additive hot-core fill keeps the lit interior legible on the
bright day sky too.

## 40px risk
- **Spike thinning** — mitigated by stubby length (13px reach) + a flat fringe
  pom cap + a cream keyline polygon around each cone, so points never needle
  down to sub-pixel and the dark candy colours don't dissolve into the sky.
- **Fringe-band shimmer** — the two short-tick crepe rings could read as noise
  at the smallest size; they collapse into a clean textured cream ring rather
  than resolving as separate ticks, which is the intended crepe read. Worth an
  art-director eye on whether the inner ring earns its keep at play size.
- **Hull-vs-spike colour separation at night** — the cream keyline carries it;
  the gameplay-NIGHT frame confirms the seven points stay distinct against the
  deep-night band, with the candy-glow seam as the bright focal point.

## Files
- `build.py` — `build(wing_angle_deg)` + palette/helpers.
- `render.py` — boilerplate that renders the gameplay sheet.
- `round_1.png` — DAY gameplay | NIGHT gameplay | reference column.
