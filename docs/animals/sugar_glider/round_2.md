# Sugar Glider — Animal Store skin · Round 2 (converged)

Round-1 verdict was **ITERATE**, winner **V4 TWILIGHT FLYING-SQUIRREL**. Round 2
collapses the five explorations down to a SINGLE production build —
`build_sugar_glider(wing_angle_deg)` exposed as
`get_sugar_glider = _make_prebuilt_skin(build_sugar_glider)` and
`BUILDERS = {"skin_sugar_glider": get_sugar_glider}` (liftable straight into
`game/animal_skins.py`).

Sheet: `docs/animals/sugar_glider/round_2.png` — hero 130px + 40px NEAREST x3
(level + dive) on DAY, **PALE-CLOUD**, and NIGHT, plus a glide-cycle strip
showing the full silhouette delta across all four poses.

Contract unchanged: 64×84, body (32,44), 4 poses, procedural-only, WHY-only.

---

## Punch list — what changed

1. **Signature spine stripe restored.** A single continuous dark dorsal line now
   runs from the tail root, over the body, up onto the brow on the centreline —
   one value step darker than the slate fur (`_SPINE`) with a darker 2px core
   (`_SPINE_D`) so it survives the 40px downscale as ONE stroke instead of the
   old short belly bar. It stops just before the eyes so it never collides with
   the catch-lights.

2. **Bright-day pop fixed (the biggest risk).** Ported V5's dark membrane RIM:
   the kite is now drawn rim → mid → light, so a dark outline frames the whole
   patagium (~+25% edge contrast). Verified specifically on the PALE near-white
   cloud panel — the flat-glider silhouette stays razor-crisp where the old
   body-colour membrane used to wash out. The leading-edge fur highlight is kept
   for the dark-sky case.

3. **Eyes resolved.** Two clean DISTINCT round night-eyes, each with a tight
   mint rim + one specular catch-light, held apart by an explicit ~1px dark gap
   stroke between them so they read as two eyes, not one fused blob.

4. **Glide cycle widened.** Spread swing exaggerated (half-span 27→14 px) plus a
   `flat` term that flattens the taut kite on the spread pose and a steeper
   `droop` on the tuck — the down pose is a visibly wider/flatter taut kite, the
   up pose a tighter dart. The glide-cycle strip makes the delta obvious.

5. **Square kite corners** (borrowed from V1) — the membrane is a near
   right-angled quad so it reads as a stretched FLAT glider, not a soft diamond.

6. **Belly glow capped.** The cream chest patch is smaller than the body with a
   small off-centre highlight — lit fur, not a neon orb. Warm cream value, not
   pure white.

7. **Bat-differentiation confirmed.** Flat horizontal kite + soft ROUND ears +
   oversized round eyes reads clearly distinct from the existing bat's pointed
   scalloped wings + pointy ear-tufts.

---

## Why ship-ready
The 40px NEAREST reads carry the four named tells at gameplay scale on all three
skies: flat square kite, glowing belly, two glowing eyes, and the unbroken
dorsal spine. The pale-cloud column proves the rim holds the silhouette in the
worst-case daylight. The silhouette is novel to the set (only flat glider) and
unmistakably not the bat.
