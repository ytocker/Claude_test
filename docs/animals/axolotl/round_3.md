# AXOLOTL — Round 3 (final pass, minimal must-fix)

Round-2 verdict: **ITERATE** — apply ONLY the minimal must-fix list, keep the
outline / pulse / palette / level-face frozen, then stop. This round touches
exactly the three flagged items and nothing else. Single production build
unchanged: `build_axolotl` → `get_axolotl` → `BUILDERS = {"skin_axolotl":
get_axolotl}`. Contract unchanged: 64×84, body (32,44), head (44,34), 4 poses
over `_WING_ANGLES`, procedural-only, WHY-only comments.

## Frozen (untouched)
- **1px dark-coral rim (#A03A5E).** `_add_outline` unchanged.
- **Down-sweep / up-bloom pulse logic.** `_flap` still inverted: wing 50°
  (frame 0) = bloom 0 = tight; wing -40° (frame 3) = bloom 1 = full fan.
- **Single-pink two-value crown.** `_GILL = #FF6E96` + one `_GILL_H` tip pixel
  per tine. No third value added.
- **Level / upright face.** Same dot-eyed read, now legible in dive too (see #2).

## Must-fix, item by item

1. **Crown read as 5 clean forks in EVERY pose (incl. dive).** Two changes in
   `_fork`/`_crown`, no new logic:
   - Every tine is drawn a constant 2px along its WHOLE length and the tine
     split was narrowed (`±0.40 → ±0.28`, `tlen 0.62 → 0.55`), so the two tines
     read as ONE fork instead of fraying into a pair of 1px tendrils under the
     smoothscale→nearest gameplay pixel. That alone removed the 6–7-tendril read.
   - The bloom fan is **capped at ~98°** (`half = 15 + bloom*34`, was
     `15 + bloom*45` → 120°). At 120° the two outer forks splayed down into the
     body outline; at ~98° they stay above the brow with a clean sky-gap. Five
     forks, five sky-gaps, verified at 10× zoom on the up-pose (frame 3) and the
     -32° dive (frame 1).

2. **Dive-pose face no longer collapses to a vertical smudge.** Took option (a):
   the mouth is now a single 2px DOT (`_FACE` circle r=1 at `HCX+4, HCY+6`),
   not an upturned arc, and the eyes sit ~1px wider apart (`HCX-2` / `HCX+9`).
   Three separated dots can't merge into one column under the dive rotation —
   confirmed legible as dot-eyes + dot-mouth in both DIVE columns and the 10×
   dive crop. Face layer stays baked into the frame (no separate un-rotated
   layer), so the body still dives as one piece.

3. **Night-dive outer fork roots clear the head rim.** Pulled the root spread in
   (`spread_px = 1 + bloom*2.4`, was `1 + bloom*4`). On a bloomed dive the two
   outer roots no longer slide far enough along the brow for their coral rim to
   merge with the head rim — every fork launches from clear scalp. Verified on
   the NIGHT DIVE column and the dive crop.

## Proof
`round_3.png`: hero 130px on WHITE / real DAY / real NIGHT skies; 40px NEAREST
×5 level + dive on the actual `game/biome.py` DAY (`(40,110,200)→(170,220,245)`)
and NIGHT (`(5,8,30)→(35,55,115)`) keyframes; and the down→up pulse strip
(tight ~30° → capped ~98° bloom). Module imports clean; all 4 frames build at
64×84 and the cached getter rotates the dive.

Deliverables: `axolotl_skins.py` (single build), `_render_sheet.py`,
`round_3.png`, `round_3.md`.
