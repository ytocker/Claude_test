# Weekend Street Kit — Round 1

**Sheet:** `docs/sidewalk_overhaul/art/weekend_kit/round_1.png` (1780 × 1692, 383 KB)
**Draft code:** `tools/_weekend_kit_round1.py` (self-contained; `SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/_weekend_kit_round1.py`)
**Brief:** `docs/sidewalk_overhaul/DAY_PLAN_WEEKEND.md` §8 (weather-adjustment layer) + §14 (the seven new pieces)
**Scope this round:** six of the seven — NEW-1 `_cart_folded`, NEW-3 `_stall_tarp`, NEW-4 `suoyi`, NEW-5 `winter`, NEW-6 `_sweeper`, plus the 8-rib umbrella upgrade. NEW-2 (wet-paving reflection) and NEW-7 (snow decoration states) are not in this brief.

No file under `game/` was touched.

---

## How the sheet is built

Each row is one piece: thesis + construction notes on the left, **3× nearest-neighbour zoom** cells in the middle (never smoothscaled — it would lie about the pixel work), and a **1× in-context panel** on the right that is a *real game frame*: `biome.palette_for_phase` → `draw.get_sky_surface_biome` → `draw.draw_mountains` → `foreground.draw_foreground_floor` (the baked running-bond sidewalk) → `foreground.draw_ground_weather` (live `wetness` / `snow_cover`) → the piece → `weather.Weather.draw` particles. Every strip carries the gold coin as the brightness yardstick.

Phases used: suoyi + tarp on the **storm** palette (0.63), the winter set on the **snow squall** (0.87), the umbrella at **dusk** (0.54), the cart in **day** (0.06), the sweeper at **sunrise** (0.94).

Everything is authored against shipped primitives rather than beside them — pedestrian geometry mirrors `ped_cast._draw_one`'s constants exactly, the tarp is built on `food_stalls._stall_shell`, the cart's crate/roll/basket parts echo `props_cast.draw_dressing`, the sweeper uses `foreground_promenade._draw_bench_person`, and the breath puff blits `weather._snow_flake` straight out of the live cache.

### Night-cap measurements (art-only delta over a real deck, coin = 229.5)

| piece | phase | max luma of new pixels |
|---|---|---:|
| suoyi (isolated, night 1.0) | storm | **139.8** |
| winter set on the snow street | 0.87 | **137.7** |
| umbrella row on the dusk street | 0.54 | **123.5** |
| cart row (daylight, night 0) | 0.06 | 154.2 *(day — cap is a night contract)* |
| tarp + suoyi on the storm street | 0.63 | **145.8** |
| sweeper row (daylight, night 0) | 0.94 | ~200 *(day)* |

The tarp lands at 145.8 — the same number `props_cast` measured as its hottest lit prop, because it goes through the same clamp (below).

---

## 1 · `suoyi` — palm-fibre straw rain-cape

**Built:** a shaggy 12 × 10 px trapezoid over the shoulders with a 3 px ragged fringe hem, in the existing `bamboo` dry-straw tan (170, 150, 96), worn with the shipped `hat == "conical"` cone and a shoulder-pole carry. Envelope with the pole: 26 px wide, 22 px tall — the CARRY-WIDE silhouette class. Cape-only (crate carry): 14 px wide.

**Construction choices:**
- The cape is drawn **between the torso and the shoulder pole**, so the pole rides *over* the straw. In integration this becomes a branch inside `_draw_one` between the torso block and the `A_POLE` accessory block; the draft recomputes `_draw_one`'s geometry constants in a `_Geom` helper so the shoulder line, hem line and head centre land identically.
- Edge notches down the two sides are **deliberately asymmetric**. A hand-bundled fibre cape is never mirror-symmetric, and the asymmetry is what stops the shape reading as a machine-drawn trapezoid once you're at 3×.
- Interior is **per-strand kinked 1 px lines** alternating dark/light, not a flat fill.
- **Shoulder spikes** proud of the cape top. Research consistently describes the fibre bulk as making the wearer look "like a clumsy hedgehog", and at 18 px that hedgehog cue is the single thing that separates a suoyi from a plain cloak in one glance.
- The **fringe is a comb**: every hem pixel gets its own 1–3 px tooth, so the bottom edge is never a drawn line.
- A dark neck notch under the hat, plus a **brim-underside shadow** on the conical hat, because without it the tan brim and the tan cape merge into one mass at night and the figure loses its head.
- Legs and a stub of trouser show below the cape — without them it reads as a bell hanging in the air.
- Because the suoyi *frees both hands* (the historical reason it beat an umbrella), this figure is always carrying. Two carries shown: shoulder pole + two hanging bundles (the primary), and a crate hugged at the chest with two straw forearms clamped over it.
- Rain drips fall from both brim edges on a 1.6 Hz cycle when `rain > 0.4`.

**Deviation from spec (flagged):** the straw retints toward `(54,64,96)` at **~34 %** where cloth retints at 55 %. The night contract is a *luma* ceiling, and 139.8 is comfortably under it — but the plan's promise is that this outline is "unmistakable at 18 px against dark rain", and at the cloth retint rate the straw goes to a neutral grey and the shape dies. Holding two-thirds of the warmth makes the piece read by **warm-vs-cool contrast** against a blue storm street, which is the mechanism the brief asks for. If the director wants the standard rate instead, say so and I'll trade legibility for uniformity.

**Also flagged:** the pole runs to ±10 px rather than the `_draw_one` `A_POLE` default of ±1.7·`body_w` (≈ ±7), so the hanging bundles clear the 12 px cape hem instead of sitting on it.

**Open questions:** (a) should the suoyi get its own `arch` key, or ride as an `accessory` flag over `A_POLE`/`A_TUNIC`? (b) 2–4 on screen at storm peak — do you want the crate carry in the deal at all, or is the pole the only correct suoyi?

---

## 2 · `winter` overlay set — coat · scarf · breath · posture

**Built:** four independently switchable sub-pieces, because the plan turns them on at different times (breath puffs survive the squall's end into the cold predawn after the coats have gone).

**Padded coat.** Torso goes from 8 px wide to **14 px** — `body_w × 1.35 + 2 each side` over the shipped `A_PADDED` — with a rounded outline (`border_radius=3`). At this size "padded" is a width and a corner radius, not a texture. Three horizontal stitch bands, each a dark line with a light line under it so the quilting has relief. Palette pulled to the `indigo` and `rust` `_COATS` banks.

**Hands tucked into opposite sleeves.** Rendered as one horizontal **sleeve roll** across the belly, with a dark mouth at each end and a lit top edge. That's the only way the classic posture survives here — but the two mouths and the highlight are what make the bar read as forearms inside cuffs rather than as a fourth stitch band.

**Collar over the chin** is drawn *after* the head, as a fur ellipse spanning the coat top, so it genuinely occludes the jaw.

**Scarf — two states, two constructions** (not one amplitude knob):
- **STREAM** — a horizontal ribbon torn downwind: a tapering polygon riding a travelling sine, ending in a **split fork**. Reads as a flag. Amplitude scales with `storm_intensity`; length 6–9 px.
- **DRAPE** — a vertical fall down the chest: a folded band with a visible **lapped-over step** (the cue for "wrapped twice") and a fringed square end. Reads as cloth hanging under its own weight.

Different axis, different outline, different terminal detail — swapping one for the other changes the figure's outline class, which is the point of the distinct-variants rule.

**Breath puff.** `weather._snow_flake(r, alpha)` blitted straight from the live cache — one blit, zero new art, and it quantises alpha in the same 16-step buckets the falling snow does, so the two read as one weather system. 2.8 s period (plan: 2.2–3.4 s, per-figure phase offset), 0.8 s life, α 70 → 110 peak, drifting right at tailwind speed and shrinking-then-fading. The sheet shows the whole 0.8 s life as four samples across one cell. **Dogs get their own**: lower (at the muzzle), faster (1.4 s), dimmer.

**Tucked posture.** Head −1 px into the shoulders and stride −20 % (achieved by scaling the `gait` term `_legs` derives its swing from, so only the stride changes). A 1 px lean *away from the wind* for anyone walking upstream.

**Deviation from spec (flagged):** the draft is a self-contained figure drawer rather than an overlay painted on top of `_draw_one`'s `A_PADDED`. Head-drop and stride can't be applied post-hoc, and I wanted the director to judge the real posture rather than an approximation. In integration these are flags inside `_draw_one`, not a new drawer.

**Open questions:** (a) the scarf state is per-slot-latched at entry — should a slot that entered in a lull keep DRAPE for its whole traversal even as the squall peaks (my assumption, per §5G "everything latches at slot entry"), or should the scarf be the one exception that morphs? (b) the plan says breath puffs are keyed on *palette coldness* in the shoulders — do you want a single `cold` scalar exposed from `biome`, or should the promenade derive it locally?

---

## 3 · 8-rib oil-paper umbrella

**Built:** a drop-in replacement for `foreground_promenade._draw_umbrella`'s canopy geometry. Keeps `_UMBRELLA_COLORS`, the night cap and the `_CUR_WIND` downwind lean **exactly as shipped** — only the canopy changes.

**Construction choices:** research is clear that the canopy is cut as *triangular segments* pegged to steamed bamboo ribs, so a real oil-paper umbrella is a fan, not a dome. Rib lines alone die at 16 px — a 1 px line over a 1 px value step vanishes on the first downscale. So the radial read is carried by **three** devices at once:
1. **Alternating panel value** between neighbouring wedges. An *area* cue, so it survives to 1×.
2. The **1 px rib** on every panel boundary, which sharpens it when the figure is near.
3. The hem **scallops once per rib**, so the silhouette itself counts the ribs even when the interior washes out.

Plus a 2 px finial with a 1 px spike above it, and a kid variant that tilts the canopy *off the pole axis* (`crooked`) rather than merely shrinking it — "held crooked" per the drizzle dress mix.

The context strip is a true before/after: five shipped rain pedestrians drawn by `_draw_one`, each with the new canopy overpainted at the exact anchor the body drawer uses.

**Deviation:** none of substance. The canopy is 1 px taller at the apex than the shipped shape at the same `r` because the finial needs somewhere to live.

**Open question:** at true 1× on the far lane the panel alternation is a 16-value step. Is that the right amount, or do you want it pushed to ~24 so the fan is unmistakable at the cost of the canopy looking slightly striped up close?

---

## 4 · `_cart_folded` — two-wheeled market handcart

**Built:** a 26 px bed (36 px envelope including the handles), in three load states.

**NEW wheel primitive.** Built inside-out, because at r = 4 there is no room for both a rim and gaps: a dark iron **tyre ring**, a light interior that reads as *the gap between spokes*, **three** full-diameter spokes (six arms) in the rim tone, and a 1 px hub. Three, not eight — at 8 px across, eight spokes fill the interior solid and the wheel goes back to being a disc. The off-side wheel draws 1 px smaller, one value darker and offset up-right; **that pair is what makes a side-on cart read as two-wheeled at all.** The near wheel turns with `t` only in the in-transit state.

**Three load states, three constructions** — not one cart with things deleted. Each has a different bed angle, ground contact and mass distribution, so the silhouettes are a bar, a wedge and a nose-down triangle:
- **LOADED** — bed level at axle height, handles lifted (in transit). A five-pole bundle laid diagonally with one binding band, a rolled awning, a crate. Wheels turn.
- **HALF** — **tipped to unload**: bed sloped down-left, handles up in the air, the last crate sliding to the low end, a basket already on the pavement. Reads as mid-action, not as a state.
- **EMPTY** — **parked**: bed level, handles dropped to the deck (with their own contact shadow), **bare slats showing** — the only state where the bed's own construction is visible, which makes "empty" a positive read rather than an absence — and a rolled mat leaned against the near wheel.

Crate, rolled-awning, basket and mat parts all echo `props_cast.draw_dressing` (slatted two-tone box; roll with a crisp end-circle and spiral; flare-rimmed woven ellipse) so a cart load and a kerbside crate stack are visibly the same town's woodwork.

**Deviation from spec (flagged):** the doc says the cart "reuses … the wheel geometry from the existing kiosk". **`draw_kiosk` has no wheel** — the kiosk is a posted booth on the ground. Hence the new primitive, which the brief separately asked for. I've noted it so the plan text can be corrected.

**Also flagged:** the HALF state's envelope is 41 px because the unloaded basket sits on the pavement beside the cart. The *cart* is 26 px; the basket is dressing. Say the word and it moves onto the bed.

**Open question:** the plan wants "one or two per STALL ROW block, plus a vendor beside it lifting poles". Should the cart ship with an attached vendor pose (a `_scene_` composite), or stay a pure prop the scene composes?

---

## 5 · `_stall_tarp` — the pitched rain sheet

**Built:** on `food_stalls._stall_shell(..., roof=False)` — the tarp **replaces** the awning rather than sitting on top of it. Shell geometry untouched (`HALF_W` 22, `post_top = base_y − 34`, counter at `base_y − 15`).

**Construction choices:** research on market-vendor practice is unambiguous — a flat tarp pools, sags and eventually dumps, so vendors *deliberately pitch* the sheet so water runs off away from customers and goods. **The slope is the storytelling.** So:
- The sheet is a taut parallelogram, **high corner upwind (left), low corner downwind (right)** — the same direction the umbrellas lean, so the whole street agrees about which way the weather is going.
- Short **fold ticks** across the slope. Cheap, and they stop 50 px of flat colour reading as a painted plank.
- **Rope turns at both post tops** (two 1 px passes + a knot pixel) plus one **taut guy line** down to the deck. The guy is what says "roped over" rather than "resting on".
- A translucent shadow band under the sheet so the vendor sits in a cave — which is what makes the warm steam and the lit face pop out of it.
- **Runoff**: travelling 1 px dashes down from the low corner (so it reads as *moving* at 60 fps with no particle system), a hanging bead at the lip, and a breathing splash ellipse on the paving.
- **Vendor seated, arms folded** — `_draw_bench_person` body on a stool behind the counter, one bar plus two hand pixels tucked under the opposite elbow. Three draws for the whole "waiting it out" posture.
- **Steam still rises and the brazier still glows.** This stall is open. That is the entire point of the piece.

**Night-cap handling:** this is the only lit member of the kit, and an additive halo summed over an already-warm counter is exactly the core+halo overlap that broke the cap for `props_cast` once before. So at night the whole piece draws onto its own SRCALPHA layer and goes through **`props_cast._clamp_surface_luma`** before blitting — the shipped contract, unmodified. Day is a straight-through draw, byte-identical. Measured composite: **145.8**, under the 146 ceiling.

**Open questions:** (a) the plan's B21 has the tarps come off in "one 3-step motion over 2 s" — should I author that as a `pitch` 0→1 parameter on this drawer (sheet rolling up toward the high corner) in a later round? (b) should the tarp carry a stall-kind variant (a wok stall's tarp would sit higher over the flame), or is one sheet enough for all five kinds?

---

## 6 · `_sweeper`

**Built:** the `foreground_promenade._draw_bench_person` body idiom (so he matches the bench couple in scale and palette) + a ~12–15 px angled besom on a 1.8 s cycle + a pushed pile. Envelope 24 × 19 px.

**Construction choices:**
- The broom is a **besom** — a fan of split bamboo twigs wire-bound to a shaft — because that is what actually sweeps a street in this town at 6 a.m. That splayed triangle at the end of a long diagonal is legible where a flat brush head is not. Six 1 px twigs at alternating straw values, a 1 px binding pixel, twigs clamped so they **flatten along the deck instead of punching through it** (which is what a bamboo bundle does under load, and it reads as bristles biting stone).
- **The head stays on the paving for the whole stroke.** A broom that lifts off mid-sweep reads as a staff being waved. The tip is pinned to the ground line and only its reach and angle change.
- The **1.8 s cycle is deliberately asymmetric**: a fast eased-out push over 45 % of the cycle, a slower eased-in recover over the rest. A symmetric sine reads as a metronome, not as work.
- He faces **left** like the rest of the cast, so the push is leftward, and the body pitches left into it.
- The **two gait frames differ in stance width as well as arm angle** — the back leg extends on the push — so the frames are distinguishable in silhouette, not just in the broom.
- The **pile** nudges forward with the stroke and puffs at full extension (the breath-puff helper, reused). Held a step *under* the paving's own value: it is swept-up slush and litter, not a highlight, and it must never be the brightest thing on a sunrise street where the coin is about to appear.

**Deviation:** the shaft measures 12 px at rest and 15 px at full reach rather than a fixed 14 px, because pinning the head to the deck while the hands travel makes the drawn length vary. 14 px is the nominal.

**Open question:** the plan wants "one per two blocks" from 363 s. Should the sweeper share the WORKS/EDGE personality's slot budget, or get his own guaranteed slot the way the storm holdouts do?

---

## What I'd like steered next

1. The **straw retint rate** on the suoyi (piece 1) is the one genuine judgement call in this round — legibility vs. palette uniformity.
2. Whether the **panel-alternation strength** on the umbrella is right at true 1× on the far lane.
3. Whether the **cart's three load states** are distinct enough as silhouettes, or whether HALF and EMPTY still read as the same object.
4. Whether the **tarp's pitch angle** is steep enough to read as deliberate at 1× — it is currently ~13° over the 55 px span.
