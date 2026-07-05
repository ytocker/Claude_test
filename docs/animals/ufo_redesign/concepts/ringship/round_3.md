# RINGSHIP — Round 3 (final designer pass)

Sheet: `docs/animals/ufo_redesign/concepts/ringship/round_3.png`
Builder: `docs/animals/ufo_redesign/concepts/ringship/build.py`

Round 2 verdict was ITERATE: the brown bowl was fixed, but the hole was
refilled with saturated CYAN instead. Round 3 closes that gate.

## Root cause (round 2) and the fix (round 3)

The hole kept refilling because three things ganged up:
1. An **additive inner glow / gel** painted across the aperture, and
2. a **fat central amber pip + bloom** sat in the gap, and
3. the **transparent gap was too narrow** (~7px raw → ~3.6px at 40px),
so after the getter's outline pass (`mask.from_surface(threshold=8)` grows
every alpha≥8 pixel 1px inward) and the smoothscale-down, the cyan tube +
feathering dominated the visible hole.

Round 3 takes the brief's fallback: **abandon the inward glow and ship a
flatter, hard-edged open ring.**

What changed:
- **No inner glow, no gel in the gap.** `_outer_rim_glow` now draws ONLY on
  rings at `OUT_RX..OUT_RX+2` — strictly outward of the body — so it can never
  bleed across the aperture. The inner edge is a crisp dark keyline
  (`INNER_KEY`) plus a lifted upper-left bevel, nothing else.
- **The whole hole is open.** The separate central amber pip + protected
  centre disc are GONE. `_punch_hole_last` now zeroes the entire inner
  ellipse (two passes: an aa punch then a 1px-eroded hard punch) so the edge
  is unambiguously transparent before the outline grows. Pip's parcel
  (composited by the game) is now the single focal object hosted in the lower
  arc of the open ring — no two-amber-blob clutter.
- **Wider gap.** Inner radius grown to `17/15` (~0.57 of outer, was ~0.50).
  The transparent band is now r=0..15 in the 64px canvas (was ~7px), which
  survives the 1px outline growth AND the smoothscale to 40px with margin.
- **Narrow traveling crest.** `_spin_crest` rides a ~22° white-hot head with
  a short dim wake behind it; the rest of the rim is left darker.
- **Inner-rim value contrast re-established.** Bevel lifted (`INNER_BEVEL`
  176,236,252) and inner keyline darkened so the tube reads round from inside
  against the now-darker, open aperture.

## PASS/FAIL proof — the hole shows SKY, not cyan

Sampled inside the open hole on the real staged gameplay composite (the
verdict frame), multiple clock positions and radii. An open hole must MATCH
the local sky; cyan would be ~(66,176,216).

### DAY (local sky periwinkle ≈ (154,161,197))
```
local sky (60px left of craft): (154, 161, 197, 255)
hole ang   0 r 4 : (154, 161, 197, 255)
hole ang   0 r11 : (154, 161, 197, 255)
hole ang  90 r 8 : (151, 159, 197, 255)
hole ang 135 r11 : (151, 159, 197, 255)
hole ang 180 r 8 : (154, 161, 197, 255)
hole ang 225 r11 : (155, 162, 197, 255)
```
Every hole sample = periwinkle sky. NO cyan.

### NIGHT (local sky deep purple ≈ (91,51,127))
```
local sky (60px left of craft): (91, 51, 127, 255)
hole ang   0 r 4 : (91, 51, 127, 255)
hole ang   0 r11 : (91, 51, 127, 255)
hole ang  90 r 8 : (89, 50, 125, 255)
hole ang 135 r11 : (89, 50, 125, 255)
hole ang 180 r 8 : (91, 51, 127, 255)
hole ang 225 r11 : (94, 52, 127, 255)
```
Every hole sample = purple sky — the SAME local sky on each biome, NOT the
identical cyan round 2 produced on both. NO cyan.

### 40px play-size strip (where round 2 cyan-bled on smoothscale)
```
play hole ang   0 : alpha 0  (0,0,0,0)
play hole ang  90 : alpha 0  (0,0,0,0)
play hole ang 180 : alpha 0  (0,0,0,0)
play hole ang 270 : alpha 0  (0,0,0,0)
```
Fully transparent at every clock at 40px — the wider gap survives the
smoothscale-down.

## Spin crest travels at 40px

White-hot crest cluster (pixels ≥250 on all channels) per frame, measured by
angle from the ring centre (12=top, 3=right, 6=bottom, 9=left):
```
phase 0  → cluster mean ~94°  (12 o'clock / top)
phase 1  → cluster mean ~ 2°  ( 3 o'clock / right)
phase 2  → cluster mean ~-95° ( 6 o'clock / bottom)
phase 3  → cluster at 180/-178° ( 9 o'clock / left)
```
A 2-3px white-hot arc segment appears at a clearly different clock position in
each of the 4 frames (12→3→6→9), with the rest of the rim notably darker — a
true traveling crest, not a soft cyan smear. Confirmed visually on the sheet's
4-frame play-size and grayscale strips (the crest reads in grayscale, so the
tell does not lean on hue).

## Kept
- Torus + traveling-arc identity.
- Outer-edge night bloom (restrained, OUTWARD only).
- The "O" negative-space silhouette as the 40px tell — now genuinely open,
  hosting Pip's parcel as the single focal centre object.
