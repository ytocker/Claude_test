# The Town Is Having a Weekend

**One-line statement of the day:** *A cheerful Far-East market town spends one ordinary weekend on its own sidewalk — waking slowly, trading hard all morning, dozing through the long middle, strolling into gold, getting rained on while it sets up its night market, having the best twenty-five minutes of its week under lanterns doubled in wet stone, and then going quietly to bed in the snow — and Pip flies over all of it.*

---

## 1. Concept

**The through-line is the town's weekend rhythm.** No tracked object, no allegory, no troupe. The street's "plot" is the honest shape of a good Saturday: the market's crest, the lull nobody fills, the golden refill, the rain that arrives at the worst possible moment for the people setting up stalls, the flood-back when it stops, and the long cold quiet after.

Every beat is tested against one question: **would this happen on a real weekend street in this town, and would it happen *at this hour*?** If yes, it's in. If it's a spectacle scheduled for the player's benefit, it's out or it's demoted to a rare, incidental event.

Two candidate concepts I discarded and why:

- *"The street reads the sky"* — the town narrated as a reaction machine to weather/gameplay. Rejected: it makes the town an instrument, not a place. The weather reaction should be a *layer*, not the spine.
- *"The regulars"* — a recurring recognizable cast (the lamplighter, the tea aunty, the three-legged dog) as the day's continuity. Rejected as a spine because it collapses the "plethora" mandate into a handful of repeats. **Kept as a demoted flavour**: exactly one recurring figure survives (the lamplighter, once per day, three blocks running) because one is charming and six is a cartoon.

**The concept, in one sentence:** *The sidewalk is one town's genuine weekend, told at its own pace, so richly populated and so honestly paced that the quiet stretches are as worth watching as the crowded ones.*

---

## 2. At a glance

| | |
|---|---|
| **Duration** | One full biome cycle — **`CYCLE_SECONDS` = 393.5 s** (320 base + `DAY_EXTRA_SECONDS` 73.5), phase 0 → 1, then loops |
| **Canvas** | 360×640 portrait; sidewalk band **y ≈ 560–640**; far deck feet at `GROUND_Y` **595**, near deck at **638** |
| **Scroll** | 160 px/s base; ×0.78 during the newbie ramp; **×1.40 at the snow-squall tailwind peak** |
| **Audience** | Mobile casual players. **Median run ends at ~156 s (phase 0.396)** — late golden hour. Most players will never see past ~200 s in a given run |
| **Constraint set** | Procedural pixel art only; ~18 px far figures / ~22 px near; no text, no faces, no sprite sheets; coin stays brightest (`NIGHT_GLOW_CAP` 150, `_LIT_FACE_CAP` 122); calm during the newbie ramp and the clown gauntlet |
| **Register** | Warm, welcoming, celebratory-ordinary. A weekend, not a once-a-year festival |
| **Net-new art pieces** | **7**, all flagged 🆕 below. Everything else re-directs existing families |

### Assumptions I made and am stating

1. **"Nothing above y=560" applies to cast and to new elements.** The existing overhead lattice (bunting at `GROUND_Y−118` = 477, lamp tops ≈ 503, garland at 497, fairy at 511) is grandfathered at its established heights. I add **no new element above the existing lamp-top line**, and every figure, animal and prop I place lives in 560–640.
2. **The day's clock is real-time, not score.** All timings below are game-seconds from run start at base scroll. Where an anchor is pillar-derived (clown, genie, umbrella pickups) I give the computed second AND state that the runtime must key off the **live flag**, because pillar→time drifts under the ramp and the tailwind.
3. **The night market is not "the festival."** The existing lion/dragon festival specials are demoted from nightly institution to **rare weekend event** (≤1 per run, ~2% of eligible blocks). A night market that has a dragon in it every single night isn't a market.
4. **Ambient street audio is out of scope to author here.** I give a one-line "sound feel" per beat as *direction*; any actual SFX must go through `game/audio.py`'s dual-backend contract (never `pygame.mixer` on the web path) and belongs to the sound-designer.
5. **Wetness survives the rain's end by ~5 s.** `WEATHER_WET_DRY_RATE` is 0.18/s from a saturated 1.0, so the pavement is still visibly glossy for the first ~6 s of the night-market window. I have built the market's most beautiful image on that fact.

---

## 3. The real anchors (extracted, not invented)

These are computed from `game/biome.py`, `game/weather.py` and `game/config.py` on `v5_skybit`, not estimated.

**Remapped sky keyframes** (`DAY_EXTRA_SECONDS` = 73.5, `NIGHT_BORROW_SECONDS` = 26.0, `DAY_HOLD_FRAC` = 0.51):

| t (s) | phase | keyframe |
|---:|---:|---|
| 0.0 | 0.0000 | **DAY** (solid, held) |
| 62.0 | 0.1575 | day-hold ends → amber fade begins |
| 121.5 | 0.3088 | **GOLDEN HOUR** |
| 163.5 | 0.4155 | **SUNSET** |
| 211.5 | 0.5375 | **DUSK** |
| 253.5 | 0.6442 | **NIGHT** (74 s long — the borrowed night) |
| 327.5 | 0.8323 | **PREDAWN** |
| 363.5 | 0.9238 | **SUNRISE** |
| 393.5 | 1.0000 | wrap → DAY + **treasure chest** |

**Events, in seconds:**

| t (s) | event | source |
|---:|---|---|
| 0 – 15.9 | newbie plateau (5 pillars, scroll 125, spacing 370) | `PLATEAU_PIPES` |
| 0 – 7.0 | `_run_fill` — street ramps in from empty | `_FILL_SECONDS` |
| 0 – 58.8 | full onboarding ramp completes at pillar 25 | `RAMP_PIPES` |
| 31.5 – 110.2 | **calm breeze / drifting leaves**, peak 70.8 s (max 3 leaves) | `calm_breeze`, unscaled phase 0.18 ± 0.10 |
| 51 – 111.5 | sinter rocks scatter the ground | `ROCK_SPAWN_THRESHOLD` 0.02 |
| **69 – 105** | **thermal geysers erupt**, peak 96 s | `GEYSER_SPAWN_THRESHOLD` 0.35 |
| ~102.6 | **genie lamp** (pillar 50 = geyser-peak pillar + 3) | `GENIE_PILLAR` |
| **~127 – 147** | **clown gauntlet** (pillar 65; 10–25 fused pillars @ 72 px) | `CLOWN_START_PILLAR` |
| **~156** | **median run ends** (phase 0.396) | telemetry |
| **190.1** | **drizzle begins** (pillar 100) | `RAIN_DRIZZLE_START` |
| ~206 | pavement starts wetting (`rain ≥ 0.18`) | `WEATHER_WET_ON_RI` |
| 211.1 / 232.1 | umbrella power-ups (pillars 112, 124) | `UMBRELLA_SPAWN_PILLARS` |
| 222.1 | drizzle sub-peak (0.35) | `RAIN_DRIZZLE_PEAK` |
| 244.5 – 273.3 | **lightning window** — ~3 flashes | `LIGHTNING_PHASE_MIN/MAX` |
| **247.7** | **thunderstorm peak (rain = 1.0)** | `RAIN_STORM_PEAK` |
| **273.3** | **rain ends** | storm peak + `RAIN_STORM_WIDTH` |
| **273.3 – 301.2** | ★ **the clear dark window — 28 s** | derived |
| 309.2 | first snowflakes | `storm_intensity` > 0.10 |
| 316 – 370 | **tailwind: scroll ×1.0 → ×1.40** | `WEATHER_WIND_SCROLL_FACTOR` |
| 320.1 – 358.5 | snow accumulates on ground + Pip | `WEATHER_SNOW_ON_WI` 0.45 |
| **342.8** | **snow-squall peak** | `SNOW_STORM_CENTER` |
| ~375 | snow cover fully melted | `WEATHER_SNOW_MELT_RATE` |
| 384.4 | squall ends | derived |
| **393.5** | **wrap: 3-pillar forced coin rush, chest on the middle pillar** | `CYCLE_FINALE_*` |

**The proven finding, confirmed by the numbers:** the existing `_POP_KEYS` peaks at phase 0.66 = **259.7 s**, where `rain_intensity` is still **0.53** and the crowd factor is crushing the street to ~0.25. The market's peak is currently inside the thunderstorm. It moves to **phase 0.724 (285 s)** — dead centre of the clear window.

---

## 4. Master timeline — all 393.5 s

Format per beat: **t-range | phase** → *who's on the street* · **signature detail** · reaction to the concurrent event · light & sound feel.

---

### CHAPTER 1 — SHUTTERS UP · 0 – 20 s · phase 0.000 – 0.051
> *So the player feels: unhurried. Nothing is asking anything of me yet.*
> **CALM MANDATE ACTIVE.** Density 0.30–0.34. No performers. No waves. No darting dogs. Block personalities forced QUIET RESIDENTIAL → GREEN WALK.

**B1 · 0.0 – 7.0 s | φ 0.000 – 0.018** — Density 0.30 × `_run_fill` (0 → 1 smoothstep).
The street literally fills in over these seven seconds: at t=0 you see paving, greenery clusters and the fixture lattice only (fixture density is phase-only, so the *dressing* is already there — the town isn't unbuilt, it's just not out yet). By t=3 the first two figures are on: one elder with a `cane` walking away from us, one shopkeeper crouched over a stack of `prop_dress` crates. By t=7 there are five.
**Signature:** the very first cast object on screen every run is a **cat** (`critter` index 0) sitting motionless on a stone step, tail flicking on a 2.4 s cycle. It never moves. It is there at 0 s and it is there at 393 s.
Sky: solid bright cyan DAY, tan sandstone, lush canopy. Newbie plateau — pillars wide and slow.
**Light:** flat noon-bright; garland and fairy lights at the `_STRING_DAY_FLOOR` 0.40 — glowing *a little*, which reads as "still on from last night." **Sound:** near-silence with one distant shutter-roll.

**B2 · 7.0 – 20.0 s | φ 0.018 – 0.051** — Density 0.34, full fill.
Second block enters: GREEN WALK. Three greenery clusters (dealt from the 30-pool, no two of the same silhouette class within 3 slots), a stone bench with one seated figure, a dog lying down — *lying*, not walking; the dog-speed multiplier is 0.4 through the calm mandate.
**Signature:** a shopkeeper on a stool **unrolling a bamboo blind** upward in 4 discrete 3-px steps over 6 s. The one motion in the frame, and it's slow.
Newbie plateau ends at 15.9 s; the ramp starts tightening underneath the player and the street does not comment.
**Light:** unchanged. **Sound:** one wooden clack per blind step.

---

### CHAPTER 2 — MORNING MARKET · 20 – 62 s · phase 0.051 – 0.158
> *So the player feels: I've arrived somewhere busy and I'm welcome in it.*
> The day's **first crest**. Density 0.58 → **0.86 at 35 s** → 0.78 → 0.55.

**B3 · 20 – 35 s | φ 0.051 – 0.089** — Density 0.58 → 0.80. Calm mandate lifts at 19 s.
Block deck shifts hard toward **STALL ROW** and **CROSSING**. Three food stalls arrive in the first STALL ROW, dealt so no two are the same kind: *steamer* + *tea* + *grill*. Vendors work their matched poses (`STALLS` maps each kind to a `day_cast` vendor index: steamer→V1 calling, grill→V3 fanning, tea→V1 calling). Between them, `prop_dress` produce crates and woven baskets.
**Signature:** the morning-market read is **buying, not eating** — figures with `basket_arm` walking *away* from stalls, one basket per two adults. (Research: morning markets are errands; night markets are meals. The two crowds must not look alike.)
Ramp is still tightening; the street's business is rising with it, which reads as the game "opening up."
**Light:** hard daylight, stall awnings casting a 3-px darker band on the paving. **Sound:** overlapping vendor calls, no music.

**B4 · 35 – 48 s | φ 0.089 – 0.122** — **★ MORNING PEAK, density 0.86.**
A CROSSING block: two-way pedestrian flow at double density, a knot of five around a hand-cart, two kids running (kid gait ×1.2), a hen underfoot. Near-lane `SidewalkCrowd` at `_BASE_N` 8.
**Signature:** the **crossing knot** — five figures at five different silhouette classes standing in a loose pentagon, three facing in, one leaving, one arriving. The single densest human moment before nightfall, and it lasts 8 seconds.
**Light:** full sun. Bunting (prayer flags) overhead at maximum span coverage — this is the daytime dressing at its fullest. **Sound:** the noisiest daytime beat.

**B5 · 48 – 62 s | φ 0.122 – 0.158** — Density 0.78 → 0.55.
Winding down. One stall's vendor starts stacking; a second STALL ROW is already half-packed (openness 0.8 → 0.6). Elders appear in numbers for the first time — the `elder` pool weighted 2.5× here, seated, with birdcage-adjacent staging (a cage hung from a lamp post arm; the bird is 3 px and doesn't move much).
**Signature:** two elders on stools with a low crate between them, both leaning in over something. They will still be there at 110 s.
At 51 s the first **sinter rocks** begin scattering the ground (thermal window opening). The street doesn't notice yet — one figure steps around a rock, that's all.
**Light:** first perceptible warmth as the day-hold expires at 62 s. **Sound:** thinning.

---

### CHAPTER 3 — THE LONG MIDDLE · 62 – 121.5 s · phase 0.158 – 0.309
> *So the player feels: pleasantly bored, in a good way. The town is dozing and so can I.*
> **This is the chapter most designs would fill and this one deliberately does not.** Density floor **0.31 at 110 s** — the lowest daytime value of the whole cycle. It exists so that everything else reads as busy.

**B6 · 62 – 80 s | φ 0.158 – 0.203** — Density 0.55 → 0.36.
Block deck flips to QUIET RESIDENTIAL / GREEN WALK / TEMPLE CORNER. Greenery goes to its own maximum (greenery density 1.0 here, independent of the cast curve). A wish tree. A napper under it.
**Signature:** the **leaf drift**. `calm_breeze` peaks at 70.8 s — a maximum of *three* autumn leaves on screen. Three. Two figures on the far deck track one leaf with a head turn as it passes. That is the entire event and it's enough.
**Light:** the sky has just started its amber crawl (day-hold ended at 62 s); stone warms from 225,195,155 toward 240,200,145. **Sound:** wind, one wind-chime.

**B7 · 80 – 96 s | φ 0.203 – 0.244** — Density 0.36 → 0.33. **Geysers erupting (69–105 s).**
This is the one daytime beat where the ground itself is doing something. Sinter rocks at `ROCK_PER_PILLAR_MAX` density; geyser cones with their 6-rock rings.
**Signature: the street reacts to the geysers, and this is the only place the sidewalk acknowledges a gameplay mechanic head-on.** Figures within ~60 px of a live vent **stand back**: a 3-figure arc facing the cone, arms slightly out, none of them walking. When the column erupts, all three flinch back 2 px, staggered 0.12 s apart. A dog barks at one (arm-equivalent: front legs drop, 0.6 s). A vendor has simply set his stall up next to a dud vent and is ignoring it — `GEYSER_DUD_CHANCE` is 0.25, so this happens naturally.
**Light:** golden creep, mountains going lavender. **Sound:** a low hiss under everything, rising and falling with `thermal_intensity`.

**B8 · 96 – 110 s | φ 0.244 – 0.280** — Density 0.33 → 0.31. Geyser peak 96 s → fade. **Genie lamp at ~102.6 s.**
The street's response to the genie is deliberately *understated* — the lamp is a huge gameplay moment and the town must not compete with it. One figure directly below the lamp's pillar stops walking and looks up-left, and holds that look for the full 3 s of the reveal. Nobody else does anything.
**Signature:** the two elders from B5 are still on their stools, in a new block, three hundred metres along. (They aren't the same two — but they're dealt from the same weighted band, so it *reads* as the same two, which is better.)
**Light:** deep gold. **Sound:** the hiss fading out under a single struck bowl.

**B9 · 110 – 121.5 s | φ 0.280 – 0.309** — Density **0.31, the floor** → 0.40.
The emptiest daytime stretch. One block of WORKS/EDGE: stacked sacks, rolled mats, a napper, nobody vertical. Then the curve turns up.
**Signature:** a genuinely **empty 5-second stretch of paving** — greenery, a lamp post, bunting overhead, no people at all. This is authored, not a failure. A street that is never empty never feels crowded.
**Light:** golden-hour keyframe lands at 121.5. **Sound:** birds, footsteps of one person.

---

### CHAPTER 4 — GOLDEN STROLL · 121.5 – 163.5 s · phase 0.309 – 0.416
> *So the player feels: this is the nicest the street has looked, and I'm still alive.*
> **The most consequential chapter in the plan.** The median run ends at 156 s, inside it.

**B10 · 121.5 – 127 s | φ 0.309 – 0.323** — Density 0.40, rising.
People come back out. `pedestrian` weighting shifts to strolling pairs (`hand_hold` accessory), parasols (not umbrellas — `parasol` is the dry-weather variant of the same accessory, angled back off the shoulder rather than overhead). A **SMALL SQUARE** block is likely here: `p_show` is 0.55 at golden, its daytime maximum.
**Signature:** the golden-band performers — musician (seated, drum), tea-pourer (tall, long-spout), fan-dancer. A ring of five spectators, backs to us, clapping on desynced 2 s cycles.
**Light:** amber horizon 255,220,140; the lamp-post row is up (installed from phase 0.20 = 78.7 s) but still dark. **Sound:** a drum, slightly too slow.

**B11 · 127 – 147 s | φ 0.323 – 0.374** — **★ CLOWN GAUNTLET. CALM MANDATE ACTIVE.**
Density clamped to **0.30**. Block personality forced to GREEN WALK. All performers suppressed. Near-lane sim paused (existing walkers finish and exit; no new spawns). No waves, no glances, no once-per-day happenings. Dogs static.
**Drive this off the live `clown_active` flag, not the clock** — the gauntlet is pillar-anchored at 65 and drifts by several seconds depending on the roll (10–25 fused pillars at 72 px spacing = 4.5–11.3 s of actual gauntlet).
**Signature:** the street is *deliberately boring for twenty seconds*: greenery clusters, one bench, one motionless dog, repeating. The warren is a wall of tightly-fused pillars and the player has no attention to spare; giving them a busy sidewalk here is actively hostile.
**Light:** deep gold going rose. **Sound:** drop the street bed entirely. Let the gauntlet own the mix.
**Recovery:** hold the clamp 2 s past the flag clearing, then ramp density back to curve over 3 s.

**B12 · 147 – 156 s | φ 0.374 – 0.396** — Density 0.44 → **0.62. The refill.**
The street comes back and it should feel like relief. Three blocks in a row at above-average density: SHOPFRONT ROW → CROSSING → STALL ROW. The first food stall since the morning (a *tea* stall, always — tea is the afternoon).
**Signature:** the refill is authored as a **wave of return**, not a fade-in: figures enter the right edge walking *with* the flow at 1.15× gait for the first 4 s, so the street visibly repopulates in the direction Pip is flying.
**Light:** sunset keyframe approaching — rose sandstone 240,170,155, autumn canopy, `star_alpha` lifting off zero.
**Sound:** the bed returns, warmer and lower than the morning's.

**B13 · 156 – 163.5 s | φ 0.396 – 0.416** — **★ THE MEDIAN FRAME. Density 0.62, at the top of a rise.**
Half of all runs end inside this beat. The last frame of the game the typical player sees must be **full, warm, gold, and moving.**
Composition mandate for this window: at minimum **6 far-lane figures, 4 near-lane figures, one lit stall, one dog, one child, greenery, and the lamp row** in frame at all times. No empty stretch may be scheduled between 152 and 166 s — the block deck is *masked* here to exclude WORKS/EDGE and QUIET RESIDENTIAL entirely.
**Signature:** a child on the near deck with a **paper pinwheel** (reuse the fan-dancer's fan geometry at 40% scale) spinning at a rate tied to the scroll speed. It's the warmest small thing in the game and it's placed exactly where most people will last see it.
**Light:** peak sunset. Sky 230,95,120 over 255,160,90; the stone is rose; the first stars at alpha 20. **Sound:** full, warm, unhurried.

---

### CHAPTER 5 — LAMPS AND SETUP · 163.5 – 190.1 s · phase 0.416 – 0.483
> *So the player feels: something is being built for tonight, and I'm early.*
> Density 0.66 → 0.60. **Decoration density climbs 0.55 → 0.85 — this is the only chapter where the street visibly gains dressing.**

**B14 · 163.5 – 178 s | φ 0.416 – 0.452** — Density 0.66.
**The carts arrive.** 🆕 **NEW-1 `_cart_folded`**: a two-wheeled handcart, ~26 px, with a bundle of poles laid diagonally across it and a rolled awning. Reuses the `prop_dress` palette bank and the wheel geometry from the existing kiosk. One or two per STALL ROW block, plus a vendor beside it lifting poles.
**Signature:** **stall frames without stalls.** Extend the 5 `food_stalls` drawers with the same `openness` 0..1 parameter `draw_kiosk` already has. At openness 0.35 you get poles and a rolled awning and nothing else — a skeleton. The market is visibly being *assembled*, which is a thing no game shows and every real market does.
**Light:** dusk approaching; `_lit_intensity` crossing ~0.30 — the lamp posts are *just* kindling, faces warming before any halo.
**Sound:** rope, wood, poles knocking.

**B15 · 178 – 190.1 s | φ 0.452 – 0.483** — Density 0.62 → 0.60.
**★ ONCE-PER-DAY: the lamplighter's round.** The existing `_scene_lamplighter` is promoted to a single travelling figure who appears in **three consecutive blocks**, each time one lamp further along, and **each lamp he touches lights.** Lamps ahead of him are dark; lamps behind him are lit. The player can tell it's the same person. This is the only recurring character in the whole day and one is exactly the right number.
Stall frames reach openness 0.6 — awnings unrolled, goods going onto counters, no steam yet.
**Light:** DUSK arrives at 211.5 but the ramp is well under way; lavender stone 180,160,200, `star_alpha` 130.
**Sound:** a single struck note per lamp lit — three notes, ascending, across the three blocks.

---

### CHAPTER 6 — THE RAIN COMES · 190.1 – 247.7 s · phase 0.483 – 0.629
> *So the player feels: oh no — they've been setting up for an hour.*
> **The chapter that earns the night.** Fair-weather density rises 0.60 → 0.84 (the market's *intent* keeps building) while the weather factor drags actual occupancy down to ~0.19. That gap is the drama.

**B16 · 190.1 – 206 s | φ 0.483 – 0.523** — `rain_intensity` 0 → 0.18. Actual density 0.60 → 0.52.
**★ ONCE-PER-DAY: the first umbrella.** Fires the exact frame `rain_intensity` crosses `WEATHER_UMBRELLA_RAIN_AT` (0.12), ~196 s. The nearest far-lane figure **stops dead**, tilts its head back 2 px for 0.6 s, then raises an oil-paper umbrella. Every other adult in that block raises theirs over the following 2 s, in a left-to-right ripple, 0.25 s apart. It is the single most legible weather beat in the day and it costs one scripted trigger.
Umbrella spec (extends existing `_draw_umbrella`): bamboo-ribbed tung-oiled paper — **8 visible 1-px rib spokes** radiating from a 2-px finial, so at 18 px scale the canopy carries a faint radial texture rather than reading as a flat disc. Palette from `_UMBRELLA_COLORS`, night-capped.
**Signature:** stalls **do not stop.** Openness holds at 0.6 and climbs. The vendors keep working in the rain because they've already carted everything here.
**Light:** dusk keyframe at 211.5; lamps at `_lit_intensity` ≈ 0.40 with the first halos. **Sound:** rain onset on canvas awnings.

**B17 · 206 – 222 s | φ 0.523 – 0.564** — `rain` 0.18 → 0.35. **`wetness` begins building at 206 s.** Actual density 0.52 → 0.44.
**Drizzle dress mix** (frozen per slot at entry, so nobody re-dresses mid-screen):
- **45% oil-paper umbrella** (as above)
- **25% hand-over-head hurry** — one arm flat above the head, torso pitched 6°, gait ×1.15, no prop
- **20% hood/shawl up** — a 5×4 px hood block in the coat's dark tone replacing the hair pixels; shoulders raised 1 px
- **10% nothing at all** — an elder walking exactly as before. *Variety by absence.* Without this the crowd looks uniformed.
- Kids: 6-px umbrellas held crooked, or a hood two sizes too big.
Umbrella power-up spawns at ~211.1 s (pillar 112) — one far-lane figure directly beneath it is holding an *identical* umbrella. No highlight, no glow; just a rhyme.
**Decoration weather states:** bunting sag +2 px, saturation −12% — **soaked bunting**. Greenery foliage darkens 8%.
**Light:** DUSK proper. First wet-paving reflection smears appear under the lamps (see NEW-2, below).
**Sound:** steady rain, awning drum.

**B18 · 222 – 236 s | φ 0.564 – 0.600** — `rain` 0.35 → 0.72. Actual density 0.44 → 0.30.
**Departures begin, and this is where most street sims break.** A slot whose stable threshold rises above the live density does **not** vanish. It enters **LEAVING**: the figure turns to face right (upstream), gait ×1.35, and walks off the right edge over 2–4 s; the slot then goes dark and will not relight until density recovers by **+0.10** (hysteresis kills flicker). Departure delays stagger by `(k mod 7) × 0.8 s`. **Figures leave once, visibly, and never pop.**
🆕 **NEW-3 `_stall_tarp`**: stalls don't leave — they **tarp**. A blue-grey sheet roped to two poles with a deliberate **pitch** so it sheds rather than pools (this is what market vendors actually do), with a 1-px water stream running off the low corner. The vendor sits under it, arms folded, waiting. **Steam still rises.** This stall is open.
Second umbrella power-up at ~232.1 s (pillar 124).
**Light:** heavy. Lamps at ≈0.75 intensity, halos meaningful. **Sound:** rain dominant, calls stopped.

**B19 · 236 – 247.7 s | φ 0.600 – 0.629** — `rain` 0.72 → **1.00**. Actual density → **0.22 floor**.
**Light:** NIGHT keyframe passed at 253.5; the sky is already deep. **Sound:** the loudest the world gets.

---

### CHAPTER 7 — STORM AND SHELTER · 247.7 – 273.3 s · phase 0.629 – 0.694
> *So the player feels: the town is down to its stubborn people.*
> Actual density **0.19 – 0.25** — the day's low point. This has to feel *inhabited*, not dead. Four guaranteed holdouts do that.

**B20 · 247.7 – 262 s | φ 0.629 – 0.666** — **Storm peak. Lightning window open (244.5 – 273.3 s, ~3 flashes).**

The four storm holdouts, all guaranteed rather than probabilistic:

1. **Shelter knots** (expand `_shelter_figures`): **minimum one per two blocks, hard-guaranteed.** 3–5 figures pressed under a kiosk awning or temple eave, shoulders touching, standing very still. One holds a *folded* umbrella pointed down with a 1-px drip every 1.4 s.
2. **The tarped stall** (NEW-3, above) — one per three blocks minimum.
3. 🆕 **NEW-4 the `suoyi` figure — the signature storm silhouette.** A palm-fibre straw rain-cape: a shaggy 12×10 px trapezoid over the shoulders with a 3-px ragged fringe at the hem, in dry-straw tan (170,150,96 — the existing `bamboo` prop bank), plus a **conical straw hat** as a 9-px-wide flattened triangle replacing the head entirely. Historically exact for this setting, and — critically — the suoyi *freed both hands*, so this is the figure still **carrying** something: a shoulder pole with two hanging bundles, or a crate. **2–4 on screen at storm peak.** They walk at normal speed. They are the town's stubbornness, and at 18 px their outline is unmistakable and shared with nothing else in the game.
4. **Runners** — 1–2 at gait ×1.6, torso pitched 12°, a bundle held over the head as a makeshift roof.

Every umbrella at `rain > 0.6` gets a 4-px lateral tilt into the wind plus a 1 Hz wobble.
**★ The lightning beat.** On each of the ~3 flashes: for **2 frames**, every street figure, stall and prop draws as a **flat silhouette** in the flash's own value — the only moment in the entire game the sidewalk is graphically bold. Then it returns. Afterwards the shelter-knot figures **flinch**: heads drop 1 px for 0.4 s, staggered 0.1 s each, so the flinch *ripples down the row*. One blit and one stagger, and the storm has a human reaction.
**Light:** `wetness` at 1.0 — maximum reflection smear. **Sound:** thunder (existing `audio.play_thunder`).

**B21 · 262 – 273.3 s | φ 0.666 – 0.694** — `rain` 0.53 → 0.
**The turn.** As rain drops through 0.35, the tarps come off — vendors reach up and pull the sheet in one 3-step motion over 2 s, staggered per stall from a dealt 0–5 s spread. **Steam returns first**, before any crowd does. Braziers relight. Openness climbs 0.6 → 0.8.
**Signature:** for about four seconds around 270 s the street is *lit, steaming, glossy and almost empty*. It is the best-looking frame of the entire day and it has nobody in it. Hold it.
**Light:** lamps at full, `wetness` still ~0.9. **Sound:** rain tailing to drips; one vendor's call, alone.

---

### CHAPTER 8 — THE NIGHT MARKET · 273.3 – 309.2 s · phase 0.694 – 0.785
> *So the player feels: this is what the whole day was for.*
> **★ THE SUMMIT.** Density **0.94 → 1.00 at 285 s → 0.95 → 0.72**. Clear, dark, and for the first six seconds still wet.

**B22 · 273.3 – 280 s | φ 0.694 – 0.712** — **The flood-back.** Density 0.94.
Returning slots use a **shortened 0.3 s stagger** (vs 0.8 s for departures) so the refill feels eager rather than administrative. In under four seconds the street goes from ~5 figures to ~20.
🆕 **NEW-2 wet-paving reflection** is at its peak and about to die: while `wetness > 0.15`, every lit source (lantern, lamp globe, stall face, brazier) mirrors as a **vertical smear below its base** — 2 px wide, 8–18 px tall, source colour at alpha `60 × wetness`, with a 1-px horizontal jitter at 8 Hz. `WEATHER_WET_DRY_RATE` is 0.18/s from saturation, so **the reflections fade out over ~276 – 280 s, exactly as the crowd arrives.**
**This is the storm's payoff and it is the whole reason the rain exists.** The night market's opening image is a hundred lanterns doubled in black wet stone, and it lasts six seconds, and it never happens again that cycle.
**Light:** night palette (sky 15,25,70), everything lit warm from below against it. **Sound:** the bed swells fast.

**B23 · 280 – 292 s | φ 0.712 – 0.742** — **★ PEAK, density 1.00 at 285 s.**
**Layout rhythm — the 4-block phrase** (≈3600 px ≈ 22 s of flight), repeated with dealt contents:
1. **STALL ROW** — 3 stalls: one steam family (*steamer*/*cauldron*), one flame family (*grill*/*wok*), one drink (*tea*), with eating knots between
2. **CROSSING** — thickest crowd, two-way, kids
3. **STALL ROW** — a different 3 (stall-kind deck ensures no adjacent repeat)
4. **SMALL SQUARE or GREEN WALK** — **the breath**: a show, or just lanterns over an empty stretch of paving

Dense, denser, dense, breathe. Never a 22-second wall of stalls.

**Eating and strolling behaviours** (all silhouette-legible at 18 px, all with per-instance random phase offsets):
- **Standing eaters** — 2–3 figures in a tight inward-facing triangle at a stall corner; elbow bends to the face on a 1.6 s cycle; a steam wisp between them
- **Walk-and-eat** — the `reach_up` accessory retargeted to chest height holding a 3-px skewer or cup; gait 15% slower than a plain walker. *The single most "night market" read available.*
- **Queue** — 4 figures in a line, evenly but not identically spaced (±3 px jitter), all facing one way, the front one leaning in. Max one per phrase, steam stalls only
- **Table sit** — two figures on `prop_bench` stools flanking a `prop_dress` crate, both leaning in
- **The stroll** — near-lane `SidewalkCrowd` with `_BASE_N` raised 6 → 9, `_roll_ped_vel` biased toward the slow end and toward standing (0 velocity), plus a **browse pause**: a stroller halts 1.5–3 s within 40 px of a stall

**Market lighting — bottom-up and warm against a cold sky:**
- Each stall: one lit awning-underside face (≤ `_LIT_FACE_CAP` 122) + one capped additive halo (radius 16, alpha ≤ 120)
- **Steam is lit from below** — wisps 6–14 px above each stall drawn in that stall's halo colour at 22–40 alpha, so the steam *glows*. Cheapest night-market cue in the plan.
- Overhead doubles: garland `per_span` 3 → 4, plus a **second garland row** at `GROUND_Y − 112`, period 127 offset by 63, so the two rows interleave and the ceiling reads dense
- Everything obeys `NIGHT_GLOW_CAP` 150. The coin stays brightest by a mile.

**Signature:** at 285 s, the frame contains ~20 figures, 3 lit stalls, 4 steam plumes, 2 dogs, ~30 lantern bulbs and a queue — and the gold coin is still the brightest pixel on screen.
**Sound:** the fullest mix of the day; overlapping calls, a busker's drum somewhere behind.

**B24 · 292 – 301 s | φ 0.742 – 0.765** — Density 0.95.
Still full. `p_show` is at its cycle maximum of 0.65 — the best odds all day of catching a busker, and a ~2% shot per eligible block at **the big one** (lion or dragon, ≤1 per run, gated to `rain < 0.15` and `storm == 0`).
**★ ONCE-PER-DAY (night only): the dropped noodles.** A figure at a stall; a small spill; a dog arriving within 2 s. The dog wins. 4 s.
**Sound:** unchanged, plus one bark.

**B25 · 301 – 309.2 s | φ 0.765 – 0.785** — Density 0.95 → 0.72. The clear window closes at 301.2.
No visible weather yet, but the crowd curve has already started down — people leave a market before the weather turns, not after. Fair-weather density falls on its own.
**Signature:** the first stall to close is a **tea** stall, and the last to close (at ~325 s) will also be a tea stall. Tea opens the day and tea closes it.
**Light:** unchanged, full. **Sound:** first thinning.

---

### CHAPTER 9 — SNOW AND SMALL HOURS · 309.2 – 363.5 s · phase 0.785 – 0.924
> *So the player feels: it's late, it's cold, and there's almost nobody left — and that's lovely.*
> Density 0.72 → 0.34 → **0.07 floor at 354 s**. **Tailwind ×1.40 from ~316 s**, so the street also scrolls past 40% faster: the emptiness arrives quickly.

**B26 · 309.2 – 322 s | φ 0.785 – 0.818** — First flakes 309.2; streaks 311.1; ground accumulation begins 320.1.
**The staggered close-down.** No stall pops out. Each runs a visible 5-step sequence, with per-stall start offsets dealt from a 0–14 s spread so the market closes **raggedly, from both ends**:
1. vendor stops calling (arm drops)
2. goods come off the counter (`prop_dress` removed)
3. awning rolls (openness 0.8 → 0.35 over 4 s)
4. lit face dims to 0
5. the 🆕 handcart appears alongside; the slot's figures leave
**Light:** flakes crossing lantern halos — draw the halo *over* the flake layer so lit snow reads. **Sound:** wind rising; calls stopping one by one.

**B27 · 322 – 342.8 s | φ 0.818 – 0.871** — Density 0.34 → 0.12. Snow accumulating. PREDAWN keyframe at 327.5.
🆕 **NEW-5 the winter overlay set** — the cold-dress layer, on the ~1-figure-per-2-blocks who remain:
- **Padded coat** — torso widened 2 px each side with a rounded quilted outline; 3 horizontal stitch bands; arms held close; **hands tucked into opposite sleeves** (the classic posture); collar raised over the chin. Palette pulled to the `indigo` and `rust` prop banks
- **Scarf** — a 2-px neck band plus a **6–9 px tail that streams rightward with the tailwind**, amplitude scaling with `storm_intensity`. *This one detail sells the wind better than any particle layer.*
- **Breath puffs** — a 3-px soft white disc (reuse `weather._snow_flake(2, alpha)`; the cache already exists), spawned at head height every 2.2–3.4 s per figure, drifting right at tailwind speed, fading over 0.8 s, alpha 70–110. Active when `storm_intensity > 0.15`. **Also on dogs**, lower and on a faster 1.4 s cycle
- **Tucked posture** — head 1 px lower into the shoulders, stride −20%, a 1-px lean *away* from the wind for anyone walking upstream

🆕 **NEW-7 the snow-state decoration set** — a 2-px white crescent on the upper arc of every lantern and lamp globe; a 1-px white line along every awning top; bunting sag +3 with white speckle; greenery cluster tops capped white; paving lightened toward `SNOW_TINT_WHITE` at `0.35 × snow_cover`; and **footprints** — a 2-px darker track behind each figure, decaying over 6 frames. Footprints exist *only* in snow, so this is the one moment the street records that anyone was here.
**Braziers are the only fixture whose density goes UP.** Two figures stand at each with hands out. A brazier halo blended over falling snow is the single warm image of the small hours.
**Sound:** wind, and the fire.

**B28 · 342.8 – 358 s | φ 0.871 – 0.910** — **Squall peak → density floor 0.07.**
Near-empty by design. One or two figures on screen at a time, sometimes none for 3 s.
**★ ONCE-PER-DAY (squall only, `storm > 0.5`): the snowball.** Two kids — the *only* two figures in the block — and one 2-px white dot arcing between them. Fires once per cycle. In an otherwise empty, cold, near-white street, this is the entire point of the small hours.
**Light:** `SNOW_TINT` wash at `SNOW_TINT_PEAK_A` 146; the street is a pale suggestion under it. Lamp halos punch through as the only warm points.
**Sound:** wind only, plus two small voices.

**B29 · 358 – 363.5 s | φ 0.910 – 0.924** — Melt begins 358.5; density 0.08 → 0.10.
**Signature:** the **cat** from B1 is here, under an awning, out of the snow, in exactly the same pose. It has been on this street for six minutes.
**Sound:** wind dropping.

---

### CHAPTER 10 — FIRST LIGHT & THE CHEST · 363.5 – 393.5 s · phase 0.924 – 1.000
> *So the player feels: I made it all the way round, and the town knows.*
> Density 0.10 → 0.24 → 0.36 → 0.30. SUNRISE keyframe 363.5; squall out at 384.4.

**B30 · 363.5 – 375 s | φ 0.924 – 0.955** — Snow thinning, cover melting to zero at ~375 s. Tailwind releasing.
🆕 **NEW-6 `_sweeper`**: the bench-person body plus a 14-px angled broom, arms on a 1.8 s sweep cycle, pushing a small pile of snow and paper. **One per two blocks.** It is the correct first inhabitant of a morning.
Also: one delivery figure with a shoulder pole; the **cold-shoulder condition** — no full winter kit, but **the breath puffs remain**, because they're keyed on palette coldness rather than on `storm_intensity`. That's the beat that says "it's cold, and the day is starting."
**Light:** peach stone 255,205,175 under a still-cool wash; lamps beginning to gutter out one span at a time. **Sound:** brooms.

**B31 · 375 – 387.6 s | φ 0.955 – 0.985** — Density 0.24 → 0.36. Squall ends 384.4.
**The first thing to open is always a tea stall**, and it is lit before anything else on the street is. Then a steamer. Two elders arrive and sit at the crate — the same silhouette pair as B5 and B8, closing the day's shape.
Bunting reverts to the daytime look, span by span, as each scrolls in.
**Light:** sunrise 255,150,150 over 255,220,170; `star_alpha` at zero. **Sound:** the day's bed, quiet, restarting.

**B32 · 387.6 – 393.5 s | φ 0.985 – 1.000** — **★ THE CHEST.** 3-pillar forced coin rush; chest on the middle pillar.
The chest is beloved and untouched. The street's job is to participate warmly and steal nothing.
- **387.6 s, as the rush begins:** **every lantern on screen relights for the last time**, at 0.6 intensity, even though the sky is brightening. It reads as the town leaving the lights on for one more minute. (0.6 × cap — nowhere near the coin.)
- **392 – 394 s, the chest pillar:** the block is forced to **SMALL SQUARE with no show** — an unusually wide clear stretch holding a **half-ring of ~9 near-lane figures, all facing up-left, all waving**, staggered 0.15 s apart so the wave **travels left-to-right along the row**, arriving with Pip. Kids in front. Two dogs. One elder who just watches and doesn't wave.
- **On pickup (`TREASURE_BOX_ANIM_T` 1.5 s):** the wave holds the full 1.5 s. Then the ring **breaks up** — figures turn and resume walking in ordinary directions over the next 3 s. The town goes back to its Sunday.
- No text. No confetti. No light change. No sound sting from the street.
- **At the wrap:** density drops to 0.30, sky snaps to DAY, Chapter 1 restarts — **and the block-personality deck is reseeded**, so day 2's street is laid out differently from day 1's. A player who survives two full cycles sees two different towns.

---

## 5. The abundance system — how the plethora stays visible

The pools are already large (50 pedestrians, 6 kids, 6 elders, 7 vendors, 5 dogs, 4 critters, 30 greenery, 15 props, 5 stalls, 8 acts). The problem is never the pool size — it's that `select_variant`'s weighted pick is **with replacement**, so by the birthday principle you see a repeat within about 8 draws from a 50-pool. Six rules fix that.

**A. Deal, don't roll.** Per run, per family, build a **weighted shuffle** (sort key `−ln(U)/w`, which preserves the existing `beat_weights`/`weather_weights` bias in the *ordering*) and deal indices off the head. Reshuffle only on exhaustion, with the constraint that the new deck's first 3 don't collide with the old deck's last 3. Result: across any 50 pedestrian placements you see **all 50 exactly once**, and the weights still control *when in the day* each one shows up.

**B. Two independent neighbour-exclusion keys, within 3 slots, near and far lanes counted separately:**
- (i) family + variant index
- (ii) **silhouette-height class** — the one that actually reads at 18 px. Six classes: `TALL-STRAIGHT`, `TALL-STOOPED`, `MID-BROAD`, `MID-SLIM`, `SHORT` (kid / stooped elder), `CARRY-WIDE` (basket / bundle / shoulder-pole widens the outline). Palette variety without outline variety reads as one person in six shirts.

**C. Block personality zoning — the spatial ebb and flow.** Divide the world x-axis into **900-px blocks** (≈5.6 s of flight at base scroll, ≈4 s under tailwind). `b = floor(world_x / 900)`; each `b` is dealt a personality from a daypart-weighted deck. Eight personalities:

| Personality | Contents | Density × | Weighted toward |
|---|---|---|---|
| **STALL ROW** | 2–3 food stalls, vendors, crates, eating knots, steam | ×1.5 | morning, night market |
| **QUIET RESIDENTIAL** | greenery, one bench, a cat, a hen, a lone elder | ×0.4 | midday, small hours |
| **SMALL SQUARE** | widened clear zone, one performer + crowd ring, brazier, bunting | ×1.1 | golden, night |
| **GREEN WALK** | 3–4 greenery clusters, wish tree, planters, dogs | ×0.5 | any (the calm-mandate default) |
| **SHOPFRONT ROW** | banners/signboards, kiosk, hanging goods, browsing pairs, tied dog | ×1.0 | morning, golden |
| **TEMPLE CORNER** | stone shrine lamp, censer, elders, pigeons, fortune-teller | ×0.7 | midday, dusk |
| **CROSSING** | two-way flow at double density, a 4–5 knot, running kids, stalled cart | ×1.6 | morning peak, market peak |
| **WORKS/EDGE** | stacked sacks, a sweeper, rolled mats, a napper | ×0.35 | any (the gap) |

Placement rules: no personality repeats within 3 blocks; **CROSSING never adjacent** to SMALL SQUARE or to another CROSSING; **every 4-block window must contain ≥1 low-density personality** (QUIET / GREEN / WORKS). That last rule is what guarantees the street breathes.

**D. Density breathes, it doesn't comb.** Per-slot admission = `day_curve(phase) × block_multiplier × weather_factor × (1 + 0.28·sin(2π·world_x / 1730 + φ_run))`. Period **1730 px** is deliberately near-coprime with the 900-px block period and the scenario period, so knots and gaps never phase-lock into a visible rhythm. `φ_run` is per-run.

**E. Mutually coprime fixture lattices.** Set every fixture period to a distinct prime: lamp row A **251**, lamp row B **253** (x0 offset 152), lantern garland **127**, fairy lights **199**, bunting **149**, greenery clusters **173**, `prop_dress` **211**, benches **313**. The combined pattern doesn't repeat for hundreds of thousands of pixels. It costs nothing and it kills the wallpaper read.

**F. Decoration density by daypart** (phase-only, never multiplied by `_run_fill` or weather, so static dressing never flickers):

| Window | Density | What's up |
|---|---:|---|
| Morning 0.00–0.16 | 0.62 | bunting at max span coverage, banners at shopfronts, strings at the 0.40 day floor |
| Midday/golden 0.16–0.42 | 0.55 | bunting thins; **greenery at its own 1.0 max** |
| Setup 0.42–0.54 | 0.55 → **0.85** | *new dressing goes up*: garland 3→4/span, extra pennants, braziers arrive |
| Night market 0.54–0.79 | **1.00** | full: two garland rows, fairy 5/span, lamps lit, braziers, banner poles |
| Small hours 0.79–0.90 | 1.00 | **decorations stay up, unlit.** Nobody takes down bunting at 3 a.m. A *dressed and empty* street is far more evocative than a bare one |
| First light 0.90–1.00 | 1.00 → 0.62 | bunting reverts to daytime; lanterns switch off one span at a time |

**G. Everything latches at slot entry.** Use the existing `sp._slot_latch` idiom for: variant index, weather bucket, day-arc beat, block personality, show tier, and dress. A slot that entered in clear weather keeps its clear dress for its whole traversal; only *new* slots entering in rain get brollies. Nothing on screen ever morphs.

**H. Per-instance animation phase offsets, always.** Gait, clapping, eating, breath puffs, scarf wave, blind-unrolling, tail-flicks — all get a random per-instance offset at spawn. Synchronised idles read robotic instantly; a random phase offset produces natural variety at zero extra art cost.

---

## 6. The street-show system — occasional, not scheduled

Shows live **only in SMALL SQUARE blocks** (and very rarely in CROSSING).

**Frequency.** A SMALL SQUARE block rolls a show at `p_show(phase)`: **0.35** morning, **0.55** golden, **0.30** dusk, **0.65** night market, **0.05** small hours. SMALL SQUARE is itself about 1-in-6 blocks (~every 33 s of flight at fair weather), so a show lands roughly **every 60–90 s in daylight and every ~45 s at the market peak.** That's a busker here and there.

**Cooldown.** A hard 40 s of flight time (≈6400 world px) between show *starts*, so two never stack. Fully suppressed during the newbie ramp (t < 19 s) and while `clown_active`.

**Act selection.** Use the existing `PERFORMERS_BY_BEAT` bands (`day`: juggler/calligrapher/fortune · `golden`: musician/tea-pourer/fan-dancer · `dusk`: stilt/juggler/mask-changer · `market`: calligrapher/fortune/juggler), **dealt not rolled**, with a per-run no-repeat-until-exhausted rule across the whole day. Tall acts (`is_tall`: stilt, tea-pour, fan-dance) are gated to `_tall_ok` clear zones outside the bird lane (48–188) and pillar lane (212–320).

**Crowd-gathering — the show as a 3-stage tableau across its 900 px.** Pip flies through, so he experiences the show's arc *spatially*, exactly the way you experience a real busker: you approach, you see the ring, you pass.

| Block px | Stage | Content |
|---|---|---|
| 0 – 250 | **Approach** | 1–2 pedestrians *turned* to face right/upstream with slowed gait; one child pulling a parent's hand toward the noise. Reads as "something's over there" |
| 250 – 620 | **The ring** | `_gathered_crowd` arc of 4–7 spectators, **backs to us**, heads at staggered heights, one raised hand clapping on a 2 s cycle **with per-figure phase offset**. Performer at the ring's focus, on the near lane, so it's the largest thing on the street |
| 620 – 900 | **The tail** | 1–2 people drifting away; a kid walking backwards, still watching; a dog sitting facing the ring; an upturned hat with 2–3 dull-bronze coin pixels (luma ≤ 90 — never competes with the real coin) |

**Three tiers of show:**
- **Tier 1 — busker** (~80%): ring of 4, one performer
- **Tier 2 — draw** (~18%): ring of 7 + a tall act or a second performer. Clear zones only
- **Tier 3 — the big one** (~2% per eligible block): **lion dance or dragon.** Hard-capped at **≤1 per run**, gated to phase ≥ 0.60 **and** `rain_intensity < 0.15` **and** `storm_intensity == 0`. Most runs never see it. The runs that do have a story.

**Telegraph.** A show is hinted 400 px early by ground detail only — a few dropped paper flags, a leaning bicycle, the ring's cast shadow reaching into frame. Never a sound sting, never a HUD marker.

---

## 7. The night food market — build, peak, wind-down

| Stage | Window | What happens |
|---|---|---|
| **Carts arrive** | 163.5 – 178 s | 🆕 `_cart_folded` handcarts with pole bundles and rolled awnings; vendors carrying stacked stools |
| **Frames up** | 178 – 190 s | Stalls at `openness` 0.35 — poles and rolled awning, no goods, no steam. The market is visibly *assembled* |
| **Rained on** | 190 – 273 s | Setup continues *through* the storm. Tarps go up (NEW-3), goods stay covered, steam persists. Fair-weather intent keeps rising while actual occupancy collapses to 0.19 |
| **Reopen** | 262 – 273 s | Tarps come off staggered 0–5 s; **steam returns before the crowd does**; braziers relight; openness → 0.8 |
| **★ PEAK** | 273.3 – 301.2 s, crest **285 s** | The 4-block phrase (STALL ROW → CROSSING → STALL ROW → breath). Density 1.00. Wet-stone reflections for the first ~6 s |
| **Wind-down** | 309 – 327 s | Staggered 5-step close-down per stall, offsets dealt 0–14 s. Closes raggedly, from both ends |

**Layout rhythm at peak — the 4-block phrase** (≈3600 px ≈ 22 s): dense, denser, dense, **breathe**. The fourth block is a show or just lanterns over empty paving. A 22-second unbroken wall of stalls would read as wallpaper within one pass.

**Stall deck:** the 5 kinds (`steamer` / `cauldron` / `grill` / `wok` / `tea`) are dealt so no adjacent STALL ROW shares a kind, and a full night market shows all 5 at least twice. Each stall keeps its matched `day_cast` vendor pose from the existing `STALLS` map.

**Behaviours:** standing eaters (inward triangle, 1.6 s elbow cycle), walk-and-eat (`reach_up` retargeted to chest, gait −15%), queues (4 deep, ±3 px jitter, steam stalls only, one per phrase), table-sits (two stools + a crate), and browse-pauses in the near-lane sim (`_BASE_N` 6 → 9, velocities biased slow and toward standing).

**Lighting:** bottom-up and warm against a cold sky. One lit awning face per stall (≤122 luma) + one capped halo (r16, α≤120). **Steam drawn in the stall's own halo colour at 22–40 alpha so it glows.** Two interleaved garland rows overhead (period 127 at `GROUND_Y−97` and `GROUND_Y−112`, offset 63). Everything under `NIGHT_GLOW_CAP` 150; the coin remains the brightest object by a wide margin.

---

## 8. The weather-adjustment layer

**Crowd factor — computed once, never double-dipped.**
```
m_rain = max(0.22, 1 − 0.78 × rain_intensity)        # WEATHER_CROWD_RAIN_MIN
m_snow = max(0.06, 1 − 0.94 × storm_intensity)       # WEATHER_CROWD_SNOW_MIN
weather_factor = min(m_rain, m_snow)                 # min, never product
density = day_curve(phase) × block_mult × weather_factor × breathe(x)
```
The day curve in §9 is authored as **fair-weather values**. This is the only weather term anywhere in the density chain.

**Departure choreography** (applies to every condition): a slot going below threshold enters **LEAVING** — turn upstream, gait ×1.35, walk off the right edge over 2–4 s, then dark; will not relight until density recovers by **+0.10** (hysteresis). Stagger `(k mod 7) × 0.8 s`. Returns use a shorter 0.3 s stagger so refills feel eager. **Stalls never leave — they run the pack-up sequence instead.** Nothing pops; nothing flickers.

### (a) Drizzle — `rain` 0.05–0.35 (≈195–222 s, 258–273 s)
**Population:** 0.96 → 0.78. Barely thinner. Weekend crowds don't run from a drizzle.
**Dress mix (frozen at slot entry):** 45% oil-paper umbrella · 25% hand-over-head hurry (arm flat overhead, torso 6° forward, gait ×1.15) · 20% hood/shawl up (5×4 px hood block in the coat dark tone replacing hair pixels, shoulders +1 px) · **10% nothing at all**.
**Umbrella spec:** bamboo-ribbed tung-oiled paper — 8 × 1-px rib spokes from a 2-px finial, `_UMBRELLA_COLORS` palette, night-capped. Kids get 6-px crooked ones.
**Decorations:** bunting sag +2 px, −12% saturation (**soaked bunting**); greenery −8% value.

### (b) Thunderstorm — `rain` > 0.5 (≈233–262 s), peak 247.7 s
**Population:** floor 0.22. Four **guaranteed** holdouts keep it inhabited:
1. **Shelter knots** — min. one per 2 blocks. 3–5 figures under an awning or eave, shoulders touching, motionless; one folded umbrella pointed down, dripping every 1.4 s
2. 🆕 **NEW-3 tarped stall** — min. one per 3 blocks. Pitched blue-grey sheet on two poles, 1-px runoff stream off the low corner, vendor seated with arms folded. **Still steaming. Still open**
3. 🆕 **NEW-4 the `suoyi` figure** — 2–4 on screen at peak. Shaggy 12×10 px palm-fibre cape with a 3-px ragged hem fringe in dry-straw tan (170,150,96), plus a 9-px conical straw hat replacing the head. Because the suoyi frees both hands, this figure is the one still **carrying** — a shoulder pole with hanging bundles, or a crate. Normal walking speed. Unmistakable silhouette, shared with nothing else in the game
4. **Runners** — 1–2 at gait ×1.6, torso 12° forward, a bundle held overhead as a roof

Umbrellas at `rain > 0.6` tilt 4 px into the wind with a 1 Hz wobble.
**Lightning (≈3 strikes, 244.5–273.3 s):** on each flash, every street figure/stall/prop draws as a **flat silhouette for 2 frames**, then returns. Shelter-knot figures then **flinch** — heads down 1 px for 0.4 s, staggered 0.1 s apart, rippling down the row.
**Ground:** paving 1 px darker; 🆕 **NEW-2 reflection smears** under every light (2 px wide, 8–18 px tall, source colour at `α = 60 × wetness`, 1-px jitter at 8 Hz).

### (c) Snow squall — `storm_intensity` (309–384 s), peak 342.8 s, tailwind ×1.40
**Population:** floor 0.06. Guarantee **exactly one figure per ~2 blocks** so the street is nearly-abandoned, never abandoned.
🆕 **NEW-5 winter overlay:** padded coat (torso +2 px each side, rounded quilted outline, 3 stitch bands, **hands tucked into opposite sleeves**, collar over the chin, indigo/rust palette) · **scarf** (2-px band + a 6–9 px tail streaming rightward, amplitude scaling with `storm_intensity`) · **breath puffs** (3-px disc via the existing `_snow_flake(2, α)` cache, every 2.2–3.4 s at head height, drifting right, 0.8 s fade, α 70–110 — **also on dogs**, 1.4 s cycle) · **tucked posture** (head −1 px into shoulders, stride −20%, 1-px lean away from the wind when walking upstream).
🆕 **NEW-7 snow decoration states:** 2-px white crescent on every lantern/globe upper arc (α tracking `snow_cover`) · 1-px white line along every awning top · bunting sag +3 with white speckle · greenery cluster tops capped · paving lightened toward `SNOW_TINT_WHITE` at `0.35 × snow_cover` · **footprints** (2-px darker track, 6-frame decay — the only condition in which the street records that anyone was there).
**Braziers** are the sole fixture whose density *rises*: two figures at each, hands out. The brazier halo over falling snow is the warm image of the small hours.

### (d) Cold predawn, no squall — the shoulders (301–309 s, 375–393.5 s)
**Population:** 0.06 → 0.36. No full winter kit. **Breath puffs persist** — keyed on palette coldness, not on `storm_intensity`, so they survive the squall's end and become the beat that says *it's cold, and the day is starting.*
**Cast:** 🆕 **NEW-6 `_sweeper`** (bench-person body + 14-px angled broom, 1.8 s sweep cycle, pushing a pile) · one shoulder-pole delivery figure · **one lit tea stall — always the first thing to open** · and the cat. Always the cat.

---

## 9. Occupancy choreography — the fair-weather density curve

Replaces `_POP_KEYS`. **All values are fair-weather**; `weather_factor` multiplies on top, once.

| phase | t (s) | density | note |
|---:|---:|---:|---|
| 0.000 | 0.0 | 0.30 | street opening — calm mandate; `_run_fill` also ramping |
| 0.030 | 11.8 | 0.34 | still calm (newbie plateau ends 15.9 s) |
| 0.055 | 21.6 | 0.58 | market waking |
| **0.090** | **35.4** | **0.86** | ★ **MORNING MARKET peak** |
| 0.130 | 51.2 | 0.78 | still busy |
| 0.160 | 63.0 | 0.55 | winding down |
| 0.215 | 84.6 | 0.34 | lazy midday |
| **0.280** | **110.2** | **0.31** | the long middle — lowest daytime floor, authored |
| 0.309 | 121.5 | 0.40 | golden hour; people come back out |
| **0.330** | **129.9** | **0.30** | **CLOWN CALM** — dip authored, and clamped by the live flag |
| 0.375 | 147.6 | 0.44 | clown over; the refill wave |
| **0.396** | **155.8** | **0.62** | ★ **MEDIAN RUN ENDS HERE** — warm, full, golden |
| 0.416 | 163.5 | 0.66 | sunset; setup begins under it |
| 0.470 | 184.9 | 0.62 | stalls assembling |
| 0.483 | 190.1 | 0.60 | first drop — weather factor takes over from here |
| 0.538 | 211.5 | 0.72 | dusk; lamps kindle; setup pushes on through the rain |
| 0.600 | 236.1 | 0.80 | *(weather crushes to ~0.25 — deliberate)* |
| 0.629 | 247.5 | 0.84 | storm peak *(→ ~0.19 actual)* |
| 0.694 | 273.3 | 0.94 | **rain ends — the street floods back in** |
| **0.724** | **285.0** | **1.00** | ★ **NIGHT MARKET PEAK** (clear, dark, drying) |
| 0.755 | 297.1 | 0.95 | still full |
| 0.785 | 308.9 | 0.72 | first flakes |
| 0.820 | 322.7 | 0.34 | closing under the squall |
| 0.860 | 338.4 | 0.10 | small hours |
| **0.900** | **354.2** | **0.07** | the floor |
| 0.924 | 363.5 | 0.10 | sunrise begins |
| 0.955 | 375.8 | 0.24 | squall gone; sweepers + the first tea stall |
| 0.985 | 387.6 | 0.36 | early vendors; the chest approaches |
| 1.000 | 393.5 | 0.30 | wrap → back to the opener (matches φ 0.000 exactly) |

**The single most important property of this curve:** it **rises 0.60 → 0.84 through the storm** while the weather factor drags actual occupancy down to 0.19. So when the rain stops at 273.3 s the crowd doesn't ramp — it **floods**. The 0.19 → 0.94 swing across four seconds is the largest single change in the day, and it is the emotional turn of the whole thing.

**Spatial layer:** block personalities (§5C) provide the knots and gaps; the 1730-px sine (§5D) provides the slow breathing; the ≥1-low-density-per-4-blocks rule guarantees the gaps exist. Together, occupancy varies in **time** (the curve), in **space** (blocks), and in **texture** (the sine) — three independent frequencies, which is what stops it reading as a uniform field.

---

## 10. Tournament awareness — warm, never HUD-like

- **Baseline glance:** at any moment ~**1 in 12** near-lane figures has its head turned up-left (2-px head offset, eye-side pixel omitted) for 1.2–2.5 s, then returns. Uncorrelated with anything. This alone makes the street feel aware.
- **Wave:** ~**1 in 25** figures raises one arm to head height for 1.5 s. Weighted ×3 toward kids, ×2 at the night market, ×0.3 in rain, **×0 in the squall**.
- **Milestone (score % 25 == 0, and on power-up pickup):** for 3 s, glance probability **triples** and up to 3 near-lane figures wave, staggered 0.25 s. No sound, no text. The player who's paying attention notices the street noticed; the one who isn't, doesn't.
- **Coin Rush (every 15th pillar):** kids in the current block **point** up-left for the rush's duration. Pointing is a distinct silhouette from waving — arm at 30°, not 90°.
- **Score 100 / 200 / …:** the nearest performer's crowd ring **turns as one** to face up-left for 2 s. It's ~7 figures. It's the closest the town comes to applauding, and it costs one flag.
- **Hard mutes:** zero glances, waves or points during the newbie ramp (t < 19 s) and during `clown_active`.
- **Never:** text, arrows, cheer SFX, any figure above y=560, any pixel brighter than the coin.

---

## 11. Once-per-day happenings — pick 3 of 8

Each fires at most once per biome cycle in a random eligible block within its window. The **order is dealt per run and only the first 3 fire**, so which ones a given run sees varies — and all are suppressed during the calm mandates.

1. **The dropped tangerine** *(any daytime)* — a small orange dot rolls right-to-left along the near deck faster than the scroll; 15 px behind it, a child chasing, arm out. 3 s.
2. **The red palanquin** *(φ 0.16–0.42)* — a red-draped two-bearer palanquin crosses one block with 4 figures walking behind; **every pedestrian in the block turns to watch**. Reuses the dragon's pole-carry idiom.
3. **The escaped hen** *(any daytime)* — the `hen` critter at 3× speed, a vendor two steps behind with arms out. 2.5 s. Reuses existing drawers entirely.
4. **The pigeon flush** *(any phase)* — a passing dog triggers `draw_flock`; 8 pigeons lift to y≈565 and settle 200 px later. The only moment birds other than Pip are airborne, and it's low enough never to read as an obstacle.
5. **The first umbrella** *(fires the frame `rain` crosses 0.12, ≈196 s)* — one figure stops, looks up, raises; the whole block ripples over 2 s. **Scheduled at B16.**
6. **The lamplighter's round** *(φ 0.46–0.54)* — one figure, three consecutive blocks, one lamp further each time, each lamp lighting as he touches it. **Scheduled at B15.** The only recurring character in the day.
7. **The dropped noodles** *(night market, φ 0.70–0.78)* — a spill at a stall; a dog arrives within 2 s; the dog wins. 4 s. **Scheduled at B24.**
8. **The snowball** *(squall, `storm > 0.5`)* — two kids, the only two figures in the block, one 2-px white dot arcing between them. **Scheduled at B28.** In an empty, cold, near-white street, this is the whole point of the small hours.

*(Items 5–8 are window-locked and effectively always fire when the run reaches them; items 1–4 are the dealt trio for the daytime.)*

---

## 12. Narrative arc

**Shape: a double peak with a storm in the trough, then a long fade to a small warm ending.**

The morning market (0.86 at 35 s) is the first, smaller crest — bright, busy, ordinary, and over quickly. Then the day does what most designs refuse to: it gets quiet. The long middle bottoms out at 0.31 around 110 s, with an authored five-second stretch of genuinely empty paving, and that emptiness is the reason everything else reads as full. Golden hour lifts the street back to 0.62 exactly where the median run ends, so **the typical player's last frame is a full, warm, gold-lit street with a child spinning a paper pinwheel** — the game's most-seen goodbye, and it is designed as one.

Then the day does something no scripted festival would: **it rains on the setup.** The stalls have already been carted in, the frames are up, and the sky opens. The market builds anyway, in the wet, under pitched tarps, thinning to almost nothing at the storm's peak — a street of shelter knots, straw rain-capes and three lightning strikes. That's the true low point, and it exists solely to be paid off.

The rain stops at 273.3 s into a 28-second window of clear dark sky, and the street **floods** back. The night market crests at 285 s, and for its first six seconds every lantern is doubled in still-wet stone before the paving dries. It holds full for twenty-five seconds — steam, queues, walk-and-eat, two garland rows overhead, and the coin still the brightest thing in the frame. Then the first flakes arrive at 309 and the market closes raggedly, stall by stall, into near-empty snowy small hours where a brazier, a streaming scarf, a line of footprints and two kids throwing a snowball are the entire population. The squall blows out at 384; a sweeper appears; a tea stall lights; and at the wrap the town leaves the lanterns on for one more minute and waves Pip through to the chest before going back to its Sunday.

**Pacing check.** Nothing is stacked: the two peaks are 250 s apart with a genuine trough between them; the storm's low sits **directly before** the day's highest crest; the calm mandates (newbie ramp, clown gauntlet) fall on authored dips rather than fighting authored peaks; and the quietest 40 s of the whole cycle (338–378 s) come *after* the night's finale rather than before the chest — so the chest arrives into **rising** energy, not falling.

---

## 13. Sources & inspiration — what the research contributed

- **Night-market crowd behaviour and lighting** — the finding that peak crowding is a narrow evening window, that stretches only a few hundred metres long become almost impassable, and that the visual signature is a noisy, neon-and-food-display sensory wall directly shaped the **4-block dense/dense/breathe phrase**, the queue-and-knot vocabulary, and the decision to make the market's peak short (25 s) and unmistakable rather than a long plateau. ([Taiwan Panorama](https://www.taiwan-panorama.com/en/Articles/Details?Guid=82d7d011-638b-40d2-a1a5-9b2603ad1a86&CatId=10&postname=Bustle%2C+Not+RomanceTaiwan%27s+Night-Market+Culture), [Night markets in Taiwan — Wikipedia](https://en.wikipedia.org/wiki/Night_markets_in_Taiwan))
- **Xiaochi eaten standing or while walking, on folding tables in the street** — the direct source for the standing-eater triangle, the walk-and-eat pose, and the stool-and-crate table-sit. ([Night markets in Taiwan](https://en.wikipedia.org/wiki/Night_markets_in_Taiwan))
- **Suoyi (蓑衣) straw rain capes and oil-paper umbrellas** — the suoyi is palm-fibre or coir, pre-Qin in origin, and was preferred over an umbrella specifically because **it freed both hands to work**. That single fact is why the storm's straw-cape figure is the one still carrying a shoulder pole. The oil-paper umbrella's tung-oiled, bamboo-ribbed construction gave the 8-spoke canopy detail. ([Garland Magazine — Suoyi](https://garlandmag.com/suoyi/), [CITS — History of Raincoats of Ancient China](https://www.cits.net/china-travel-guide/the-history-of-raincoats-of-ancient-china.html), [Newhanfu — Brief History of Ancient Chinese Umbrellas](https://www.newhanfu.com/18259.html))
- **Market-vendor tarp practice** — flat tarps pool and sag, so vendors deliberately **pitch** them so water runs off away from customers and goods. That's why NEW-3 has a slope and a 1-px runoff stream rather than being a flat rectangle. ([Tarp Supply — Outdoor Market Vendor Shade Tarps](https://www.tarpsupply.com/blogs/tarps-articles/outdoor-market-vendor-shade-tarps-for-summer))
- **Morning-market culture** — the finding that morning markets are errand-driven, skew older, and are where elders do tai chi and keep songbirds between the noodle stalls, while younger people return **on weekends** out of nostalgia, is what separates the morning crowd (baskets, buying, elders, birdcages) from the night crowd (eating, strolling, families). ([The Silk Road Echo — China's Vibrant Morning Markets](https://www.silkroadecho.com/local-lives/2494.html), [Chineselearning — Vibrant Morning Markets](https://www.chineselearning.com/chinese-culture/vibrant-morning-markets-a-glimpse-into-china-s-urban-culture))
- **Temple-fair and street-performance repertoire** — calligraphy and tea stands beside food carts, with lion dance, dragon dance, stilt-walking, acrobatics and erhu buskers as the performance vocabulary — confirms the existing 8-act pool is authentic and justified demoting lion/dragon to **rare** rather than nightly. ([China Highlights — Beijing Temple Fairs](https://www.chinahighlights.com/festivals/beijing-temple-fairs.htm), [SCMP — street performance in Chinese history](https://www.scmp.com/magazines/post-magazine/short-reads/article/2160001/ancient-china-mong-kok-street-performance-was))
- **Ambient-NPC craft** — the guidance that ambient crowds need *consistency and variety* rather than depth, that fewer than ~4 idle variants per archetype produces visible repetition, and above all that **a random phase offset on initialisation desynchronises footfalls** (synchronised idles read robotic) is the direct basis for rule §5H and for every "per-figure phase offset" note in the timeline. ([Making Digital Worlds Feel Alive](https://eric-buitron.hashnode.dev/making-digital-worlds-feel-alive-my-research-into-realistic-ambient-characters), [MoCap Online — Crowd & NPC Animation Guide](https://mocaponline.com/blogs/mocap-news/crowd-npc-animation-guide))

---

## 14. The seven new pieces (everything else re-directs existing families)

| # | Piece | Where | Why it's net-new |
|---|---|---|---|
| 🆕 1 | `_cart_folded` — handcart with pole bundle + rolled awning | Setup (163–190 s), close-down (309–327 s) | Nothing in the prop pools reads as "a stall in transit" |
| 🆕 2 | Wet-paving reflection smear | `wetness > 0.15` (206–280 s) | The storm's entire visual payoff; one draw call per light |
| 🆕 3 | `_stall_tarp` — pitched rain sheet with runoff | `rain > 0.35` | Lets a stall stay *open* in a storm instead of vanishing |
| 🆕 4 | `suoyi` overlay — straw cape + conical hat | `rain > 0.5` | The signature storm silhouette; shares its outline with nothing else |
| 🆕 5 | `winter` overlay — padded coat, scarf tail, breath puffs, tucked posture | `storm_intensity > 0.15` and cold shoulders | The cold-dress layer the brief specifies |
| 🆕 6 | `_sweeper` — bench body + 14-px broom | 363–393 s | The correct first inhabitant of a morning |
| 🆕 7 | Snow decoration states — lantern crescents, awning lines, bunting speckle, greenery caps, footprints | `snow_cover > 0` | Decorations must have a snow state, and footprints are the small hours' best detail |

Everything else in this plan — all 50 pedestrians, 6 kids, 6 elders, 7 vendors, 5 dogs, 4 critters, 30 greenery designs, 15 props, 5 food stalls, 8 performer acts, the festival specials, the bunting, the two garland rows, the fairy lights and the lamp rows — is **existing art re-directed** by the rotation, zoning, show, market, weather and occupancy systems above.