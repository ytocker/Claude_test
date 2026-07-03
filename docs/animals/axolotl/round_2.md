# AXOLOTL — Round 2 (converge to ship-ready)

Round-1 verdict: **ITERATE**, winner **v3 ANTLER LEUCISTIC**. This round drops
the 5-up exploration and ships a single production build, `build_axolotl`,
exposed as `get_axolotl` + `BUILDERS = {"skin_axolotl": get_axolotl}` so it
lifts straight into `game/animal_skins.py`. Contract unchanged: 64×84, body
(32,44), head (44,34), 4 poses over `_WING_ANGLES`, procedural-only, WHY-only.

## Punch-list, item by item

1. **Permanent 1px dark-coral rim (#A03A5E).** `_OUTLINE = (160,58,94,255)`
   is now a solid (alpha 255) rim grown from the alpha mask in `_add_outline`,
   8-neighbour so diagonal fork tips don't leak. It wraps body AND crown as one
   silhouette. Proofed on a **white/pale stress field** (hero, top-left) — the
   near-white leucistic body holds its edge against pale blue, not just on the
   dark card.

2. **5 bold forks, 3/2, with sky-gaps.** `_crown` draws exactly five forks at
   fixed fractions `(-1, -0.5, 0, 0.5, 1)` of the fan — three lean left of the
   head's up-axis, two right. Each fork's ROOT also slides along the brow by the
   same fraction (`spread_px`), so the bases separate too — a clear pixel of sky
   between every fork at 40px NEAREST. The negative space is the tell.

3. **Down tight vs up bloom.** `_flap` is inverted (`1 - …`) so wing 50°
   (down-pose, frame 0) = bloom 0 = tight ~30° sweep, and wing -40° (up-pose,
   frame 3) = bloom 1 = wide ~120° fan. The bottom "Crown pulse" strip shows the
   four poses opening up; the right-hand hero pair shows tight→bloom side by
   side. The pulse now reads in motion at 40px.

4. **One pink, two values.** Crown is `_GILL = #FF6E96` core only, with a single
   lighter `_GILL_H` pixel set at each tine tip. No third value anywhere on the
   frill.

5. **Dive-pose face.** Eyes are 2px solid dots and the smile a 2px arc; because
   the face is baked into the frame and the whole sprite rotates, both survive
   the -32° dive tilt — checked in the DIVE columns on both day and night.

6. **v1 closed dot-smile + single blush.** Swapped the round-1 v3 wide open grin
   for v1's clean closed dot-smile (`_face`): two dot eyes + a short upturned
   2px arc. Blush is now ONE soft pixel per cheek (`set_at`), not a 2px circle.

7. **Proofed on real skies.** Both 40px NEAREST strips use the actual
   `game/biome.py` keyframes — DAY (`sky_top (40,110,200)` → `sky_bot
   (170,220,245)`) and NIGHT (`(5,8,30)` → `(35,55,115)`) — for level + dive.

## Alt palettes
Melanoid and gold morphs are retained as commented constant sets at the foot of
`axolotl_skins.py`; retint `build_axolotl` by swapping the `_BODY/_GILL/_FACE`
constants. The leucistic build is the lead.

Deliverables: `axolotl_skins.py` (single build), `_render_sheet.py`,
`round_2.png`.
