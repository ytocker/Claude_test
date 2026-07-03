# AXOLOTL — Round 4 (FINAL pass)

Round-3 verdict: **ITERATE** — one remaining failure. The level/upright poses
are SHIP-QUALITY and the dive FACE fix (3 separated dots) landed clean; both are
frozen. The sole defect: the gill crown collapsed into a solid coral paddle (no
sky-gaps) in the DIVE pose, on day AND night. This is the last loop turn; the
skin ships as-is after it. Single production build unchanged: `build_axolotl` →
`get_axolotl` → `BUILDERS = {"skin_axolotl": get_axolotl}`. Contract unchanged:
64×84, body (32,44), head (44,34), 4 poses over `_WING_ANGLES`, procedural-only,
WHY-only comments.

## Root cause (per the art-director)

The fan is baked into the upright frame, then the getter rotates it for the
dive. The DIVE pose lands near `bloom 0.33` (frame 1), where the old splay
(`half = 15 + bloom*34` → only ~53° total → ~13° per gap) packed the five tips
too tightly; the dive `rotozoom` + the gameplay smoothscale→NEAREST downsample
then filled the narrow inter-fork gaps and fused the crown into one paddle.

## The fix — re-gap the forks so the gaps survive rotation

Two geometry changes, both inside `_fork` / `_crown`. No new logic, no new layer.

1. **Tapered tips (`_fork`).** Each fork now tapers from a fat 3px root → 2px
   mid stalk → a 2px-then-1px tine pair, so the LAST pixel of every tine is a
   single pink pixel with sky on both sides. The fan's widest point (the tips)
   now carries the thinnest pink, which is exactly where a clear sky-gap has to
   survive the dive downsample. The old constant-2px tip bled into its neighbour
   and welded the crown solid; the tapered tip does not.

2. **Wider splay + wider outer forks (`_crown`).**
   - Splay floor raised: `half = 23 + bloom*27` → **46°→100°** total (was
     `15 + bloom*34` → 30°→98°). The DIVE pose now opens to ~65° (≈18° per gap)
     instead of ~53° — wide enough that five distinct fronds survive rotation.
   - Fractions made non-linear (`-1, -0.46, 0, 0.46, 1`, was ±0.5) so the OUTER
     forks splay proportionally further than the inner pair; the widest gaps —
     the ones that have to read after the downsample — open first.
   - Root spread scaled up a touch (`spread_px = 1.6 + bloom*2.2`, was
     `1 + bloom*2.4`) so the five roots separate along the brow without sliding
     so far that the outer coral rim merges with the head rim.

   Result: **five distinct forks, five visible sky-gaps in the DIVE pose on BOTH
   day and night** — verified at 40px NEAREST x6 (top row of `round_4.png`).

## Frozen (untouched)

- **Level / upright crown.** Already clean; the splay change keeps it a crisp
  fan (see the pulse strip + LEVEL columns — still distinct forks, more open).
- **Dive FACE layer.** Three separated dots (two eyes + a mouth dot); legible in
  both dive columns and the dive zoom. Unchanged.
- **1px dark-coral rim (#A03A5E).** `_add_outline` unchanged.
- **Down-sweep / up-bloom pulse logic.** `_flap` still inverted (wing 50° =
  bloom 0 = tight; wing -40° = bloom 1 = full fan). The pulse still reads ~2×:
  ~46° tight → ~100° bloom.
- **Single-pink two-value crown.** `_GILL = #FF6E96` + one `_GILL_H` tip pixel
  per tine. No third value added.

## Night-dive root check (the earlier merge concern)

Re-verified now that the forks exist again: on the NIGHT DIVE the outer fork
roots launch from clear scalp — a visible band of body between each crown root
and the head rim, no coral-on-coral merge (top-right panel + NIGHT row).

## Proof

`round_4.png` leads with the targeted read — a **big DIVE crown at 40px NEAREST
x6 on real DAY and NIGHT skies** (five fronds, five gaps) — then the standard
proof: HERO 130px on WHITE / DAY / NIGHT; 40px NEAREST x5 level + dive on DAY
and NIGHT; and the down→up pulse strip (tight ~46° → capped ~100° bloom). Sky
colours are the actual `game/biome.py` DAY (`(40,110,200)→(170,220,245)`) and
NIGHT (`(5,8,30)→(35,55,115)`) keyframes. Module imports clean; all 4 frames
build at 64×84 and the cached getter rotates the dive.

Deliverables: `axolotl_skins.py` (single build), `_render_sheet.py`,
`round_4.png`, `round_4.md`.
