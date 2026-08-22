# THE FIFTH DRUM TO THE THIRD
### A redesign of the Skybit sidewalk across one full 393.5-second tournament day

**Concept in one sentence:** *The town spends the whole day preparing a single red wish-lantern for the flyer overhead — it wakes under it, works around it, raises it at sunset, defends it through the storm and the snow, and lets it go at dawn.*

---

## 1. Concept

### The three candidates

**A. "The Town Is a Clock."** Ground the day in the real Tang/Song *morning bell, evening drum* (晨鐘暮鼓) system: the drum tower calls the hours, markets legally opened "at the fifth drum" (~3–5am) and closed "at the third drum" (~11pm–1am). Strong spine, historically real, gives the day audible bookends. **Weakness:** it's a structure, not a feeling. Nothing for the player to *care* about.

**B. "The Lantern Relay."** One physical object — a red paper lantern with a ribbon tail — is passed along the street all day: bought at the morning market, tied at the wish tree, carried by a kid, raised on a pole at sunset, lit at dusk, guarded through the snow, released at dawn. A baton the eye can follow, paying off in a real ritual (the Pingxi sky-lantern release, where wishes are written on the paper and let go in coordinated waves). **Weakness:** at 18 px a single tracked object is hard to keep legible across 393 seconds.

**C. "The Town Is the Scoreboard."** The street tallies Pip's flight — banners raised per milestone, a growing crowd. **Rejected:** the brief forbids HUD-like ambience, and this is a HUD wearing a costume.

### The pick — a fusion of A and B

**A gives the day its skeleton; B gives it a heart.** The drum frames the loop (and the loop is *literally* a loop — the biome wraps at 393.5 s, so "closes at the third drum, reopens at the fifth" is a seamless join, not a cut). The lantern gives every chapter a job: *what is the town doing to the lantern right now?* Legibility is solved by never asking the player to track one 6-px object — instead the lantern is present as a **recurring red note** (the only saturated red in the street's palette at any given moment), appearing in a different scale each chapter: a dot on a cart, a shape on the wish tree, a full-height silhouette on the pole at sunset, a glow in the snow, a rising point at dawn.

**The test every beat must pass:** *does this beat show the town doing something to, for, or because of the lantern and the flyer?* If a beat is just "people walking," it gets a job or it gets cut.

---

## 2. At a glance

| | |
|---|---|
| **Medium** | Bottom strip, y≈560–640; far promenade deck at GROUND_Y=595, near deck at 638; scroll ~160 px/s |
| **Duration** | `CYCLE_SECONDS = 393.5 s` (base 320 + `DAY_EXTRA_SECONDS` 73.5) |
| **Audience** | Median run **156 s** (phase 0.396) — half of all players never see the sunset keyframe |
| **Cast palette** | 50 pedestrians · 6 kids / 6 elders / 7 vendors · 5 food stalls · 9 animals · 30 greenery · 15 props (5 pools) · 8 busker acts · 5 festival specials |
| **Hard constraints** | Procedural only; ~18 px figures; no text, no faces; coin stays brightest (`NIGHT_GLOW_CAP=150`); nothing above y=560; calm street during the newbie ramp |
| **New set pieces** | Exactly **three**, all flagged NEW |

### Real anchors extracted from the code

`_KEYFRAMES` are remapped by `DAY_EXTRA_SECONDS = (30 + 12) × (280/160) = 73.5 s`, with `NIGHT_BORROW_SECONDS = 26` pulling GOLDEN…NIGHT earlier, and a `DAY_HOLD_FRAC = 0.51` keyframe inserted. The **real** numbers:

| Keyframe | Phase | Seconds |
|---|---|---|
| DAY | 0.000 | 0.0 |
| *(DAY hold ends — amber begins)* | 0.157 | 62.0 |
| GOLDEN HOUR | 0.309 | 121.5 |
| SUNSET | 0.415 | 163.5 |
| DUSK | 0.537 | 211.5 |
| NIGHT | 0.644 | 253.5 |
| PREDAWN | 0.832 | 327.5 |
| SUNRISE | 0.924 | 363.5 |
| wrap → DAY | 1.000 | 393.5 |

**Weather & event anchors** (`_WIDTH_SCALE = 320/393.5 = 0.813`; pillar→time from `_phase_for_pillar`: pillar 26 = 60.6 s, then 1.75 s/pillar):

| Event | Phase window | Seconds |
|---|---|---|
| Calm breeze (drifting leaves only) | 0.08 – 0.28, peak 0.18 | 31 – 110, peak 71 |
| Thermal field — sinter rocks | 0.127 – 0.285 | 50 – 112 |
| Thermal — **geysers** (≥0.35) | 0.174 – 0.268 | **68 – 106**, peak 96 |
| Genie lamp (pillar 50) | 0.261 | **102.6** |
| Clown gauntlet (pillar 65 + 10–25 fused @0.45 s) | ~0.323 – 0.363 | **~127 – 143** |
| Rain drizzle start (pillar 100) | 0.483 | **190.1** |
| Drizzle peak / storm rise | 0.564 | 222.1 |
| **Thunderstorm peak** (rain = 1.0) | 0.630 | **247.7** |
| Lightning window | 0.621 – 0.694 | 244.5 – 273.3 |
| Storm-jolt strike (`rain ≥ 0.85`) | ~0.61 – 0.65 | ~241 – 256 |
| Umbrella power-up (pillars 112 / 124) | 0.537 / 0.590 | 211 / 232 |
| Wet paving (`rain ≥ 0.18` builds; dries 0.18/s) | ~0.50 – 0.74 | ~197 – 290 |
| Rain over | 0.694 | **273.3** |
| Snow squall begins | 0.766 | **301.3** |
| Snow heavy (`≥0.45`) / tailwind bites | 0.814 – 0.929 | 320 – 366 |
| Snow plateau (clamped 1.0) | 0.855 – 0.888 | 336 – 349, peak 343 |
| Snow squall ends / cover melted | 0.977 | 384.5 |
| **Cycle finale** — 3 rush pillars, chest on #2, +100 | wrap | **393.5** |
| Newbie plateau (`PLATEAU_PIPES=5`) | — | 0 – ~19 |
| Newbie ramp complete (`RAMP_PIPES=25`) | — | ~60.6 |

### The headline finding

Run the current `_POP_KEYS` at the median death phase of **0.396**: it interpolates between `(0.34, 0.24)` and `(0.50, 0.30)` and returns **0.261**.

> **Half of all players die in the emptiest street of the entire day.** The golden lull sits exactly on the median run's last ten seconds.

Everything below is built around fixing that: the day's **second-biggest crowd event is moved to 152–175 s**, so the median player's final image is a red lantern climbing a pole to meet them against a turning sunset.

### Assumptions stated

- Weather is deterministic and phase-locked, so each chapter meets a known weather state. The overlay matrix (§4) is written to also cover the case where curves are later randomized.
- **There is no fog in `weather.py`** — only rain/lightning, snow+tailwind, calm breeze, thermals, plus the ground-state signals `wetness` and `snow_cover` (`draw_ground_weather`). §4 proposes an optional vent-mist as NEW.
- The clown gauntlet is pillar-anchored, so its wall-clock window drifts ±3 s with scroll ramp and the 10–25 roll. Street beats around it are written as *gated on the event firing*, not on a fixed clock.
- On day 2+ (`DAY_SCROLL_STEP`) the whole street compresses proportionally; the plan holds because everything is phase-driven, not pillar-driven, with the two flagged exceptions (clown, genie).

---

## 3. Master timeline — 100% of 393.5 s

Density figures are **fair-weather base** — the weather factor multiplies on top. *Do not double-dip:* during the storm the base stays high and `_weather_crowd_factor` does the emptying, otherwise `0.10 × 0.22` gives a ghost town 30 seconds early.

### Proposed density curve (replaces `_POP_KEYS`)

```
phase  base   |  what it is
0.000  0.30   |  arrival — the town is mid-morning, Pip is new
0.056  0.55   |
0.090  0.85   |  ████████  MARKET PEAK
0.127  0.62   |
0.170  0.42   |  steam morning — working density, clustered
0.244  0.36   |  thermal peak — onlookers, not crowds
0.285  0.20   |  the lull (deliberate valley)
0.323  0.16   |  ▁ pre-gauntlet hush — the day's quietest daylight
0.363  0.34   |  gauntlet exit
0.415  0.75   |  ███████  THE LANTERN RAISING  ← the median run's last sight
0.470  0.50   |  dispersal
0.520  0.55   |  dusk trade (rain factor will thin this to ~0.4)
0.630  0.60   |  storm peak base (× 0.22 weather = ~0.13 effective)
0.694  0.70   |  rain stops — the town pours back out
0.732  1.00   |  ██████████  NIGHT FESTIVAL PEAK
0.768  0.85   |
0.800  0.45   |  third drum — teardown (× ~0.76 snow = ~0.34)
0.855  0.30   |  squall (× 0.06 snow = ~0.02) + THE WATCH floor
0.930  0.22   |  fifth drum — shutters going up
0.977  0.45   |
1.000  0.30   |  wrap to arrival
```

Two named peaks became three. Critically, the **festival peak moves from 0.66 to 0.732** — at 0.66 the current curve puts its 1.00 crest inside the thunderstorm, where the weather factor cuts it to 0.22. Today the biggest crowd event of the day is being rained out and nobody sees it.

---

### CHAPTER 1 — **ARRIVAL** · 0 – 22 s · phase 0.000 – 0.056
*So the player feels: I have just flown into somewhere that was already busy before I got here.*

Bright cyan `DAY` palette, solid (the hold runs to 62 s). Newbie plateau covers the first ~19 s: no tall near-lane props, zero attention verbs, one clean silhouette event only. `_run_fill` is **re-staggered**: far lane fills over 5 s, near lane over 10 s, performers not before 14 s — so the street assembles in depth order instead of all at once.

| t (s) | phase | Beat | Street | Signature | Ties to | Light & sound |
|---|---|---|---|---|---|---|
| 0–6 | .000–.015 | **The Card** | far lane only, base 0.30 → mostly greenery clusters + two vendors | one of six **Arrival Cards** (§6) — a different way the town notices Pip every run | run-open; `_run_fill` | flat noon light, unlit lamp shells, string lights at the 0.40 day floor. One bright shutter-clang or bell if the card calls for it |
| 6–14 | .015–.036 | **Depth arrives** | near lane fades in: one dog, one strolling pair, larger and lower | the near lane's first figure crosses *in front of* a far vendor — the depth cue lands in one pass | newbie plateau — nothing above y=560 | steam plume off the first steamer stall; awning shadows short and hard |
| 14–22 | .036–.056 | **First trade** | base 0.30→0.55; grill + tea stalls enter; kids appear | a kid buys a **small red lantern** off a cart and runs with it — the baton's first appearance, held at near-lane scale so it reads | plants the finale | warm oil-sizzle register; no music cue; the red is the only saturated hue on the deck |

---

### CHAPTER 2 — **THE MARKET ROARS** · 22 – 50 s · phase 0.056 – 0.127
*So the player feels: this town is loud and it has noticed me.*

Highest density of the daylight half. Roster: `food_grill / food_soup / food_steamer / food_tea / market / vendor / dawn_setup`. Real detail worth stealing: morning markets run 5:00–9:00, dough hits hot oil in a constant rhythm, steam curls off bamboo baskets, soy-milk vats sit beside every fryer. Give the deck **three concurrent steam sources** — that's the chapter's signature texture at 18 px, because steam reads where faces don't.

| t (s) | phase | Beat | Street | Signature | Ties to | Light & sound |
|---|---|---|---|---|---|---|
| 22–30 | .056–.076 | **Crest** | base → 0.85; stalls at max, all 5 kinds within 3 screens; hens and pigeons under the tables | the day's tightest cluster: 4 figures around one cauldron, one ladling, three waiting | attention verbs unlock at 19 s — first LOOK/POINT of the run | densest steam; string lights invisible against daylight; chatter texture |
| 30–40 | .076–.102 | **The wish tree** | 0.85→0.70; the wish tree scenario is *guaranteed* once in this window | the kid ties the red lantern into the **wish tree** — the town's claim on the flyer. First POINT-at-Pip fires here | plants the sunset raising and the dawn release | leaf-shadow flicker; a single low bell |
| 40–50 | .102–.127 | **Songbird & sweep** | 0.70→0.62; birdcage stand + street sweeper; first busker (day band: juggler / calligrapher / fortune-teller) | **Happening #1 — The Runaway Songbird:** a cage door swings, a `draw_flock` burst launches off the deck and out of frame. Once per day | the flock exits *upward and right*, following Pip — free tournament-awareness | the sweeper's water arc darkens the paving in a band that catches the sky (reuses the wetness reflection path) |

---

### CHAPTER 3 — **STEAM MORNING** · 50 – 112 s · phase 0.127 – 0.285
*So the player feels: the ground itself has woken up, and the town lives with it.*

`thermal_intensity` opens at exactly 50 s. Sinter rocks scatter from ~51 s; the first geysers at ~68 s; peak 96 s; genie lamp at 102.6 s; rocks-only tail to 112 s. The `calm_breeze` bump peaks at 71 s, drifting autumn leaves. This chapter's whole idea: **the street is built around the vents.** The town has lived here a long time; they use the vents and they respect them.

| t (s) | phase | Beat | Street | Signature | Ties to | Light & sound |
|---|---|---|---|---|---|---|
| 50–60 | .127–.152 | **Sinter** | 0.62→0.50; scattered sinter rocks appear on the deck as ground texture | vendors' pots are set **directly over small ground vents** — the town cooks on the geothermal. Establishes the vents as normal before they're dangerous | rocks lead the geyser event as a telegraph in the sky *and* on the ground | first drifting leaf crosses the deck; light still flat, day-hold holds to 62 s |
| 60–68 | .152–.174 | **Amber turns** | 0.50→0.44; the last newbie-ramp pillar passes at ~60.6 s — street may now use tall near-lane props | the first **stilt-walker** or fan-dancer takes the near lane, tall against the first amber in the sky | the DAY hold ends at 62 s: the palette begins its slide to golden | shadows lengthen perceptibly for the first time; a long low leaf-drift |
| 68–82 | .174–.208 | **First vent** | 0.44→0.42; a low rope fence and a cairn mark a vent slot | **Reaction beat:** when a geyser fires, the 2 figures nearest its screen-x back off 4 px, one shields their face, a hen scatters. Throttled to once per 8 s | the geyser column is a gameplay *gift* (updraft) — the street treats it as weather, not threat | rising column shifts the deck light 8% cooler in its band for 0.5 s; kettle-whistle register |
| 82–96 | .208–.244 | **The Kettle Chorus** | 0.42→0.36; density thins but *clusters* — knots of 3 with gaps between | **Happening #2 — the Kettle Chorus:** three vendors in a row lift their lids in stagger as the geyser field peaks; three plumes rise on the deck at once, mirroring the columns above. Once per day | the deck echoes the sky's geometry: three low plumes below, three tall columns above | maximum steam; the coin cuts through all of it (steam alpha capped so it never fights the gold) |
| 96–106 | .244–.268 | **The Conjurer** | 0.36 flat; incense smoke doubles | **Happening #3 — The Conjurer's Cart:** a covered cart is wheeled to a stop and its cloth pulled back, arriving 5–6 s *before* the genie lamp spawns at 102.6 s. On pickup, the whole far-lane cast performs the day's **only synchronized LOOK** | the genie chamber opens directly after; the street's stillness sells it | everything on the deck holds still for 1.2 s except the smoke — the day's first held breath |
| 106–112 | .268–.285 | **Vents cool** | 0.36→0.22; rocks fade | the rope fence is coiled and carried off; one figure taps a cooling vent with a stick | thermal curve's short fade tail | steam drops to one source; light warms toward golden |

---

### CHAPTER 4 — **THE LULL** · 112 – 127 s · phase 0.285 – 0.323
*So the player feels: I can breathe, and something is about to happen.*

A **deliberate quiet valley**, 15 seconds long. `GOLDEN HOUR` lands at 121.5 s. This is the only place in the day where near-emptiness by daylight is correct, and it exists to give the gauntlet a floor to rise from.

| t (s) | phase | Beat | Street | Signature | Ties to | Light & sound |
|---|---|---|---|---|---|---|
| 112–121 | .285–.309 | **Wide and warm** | 0.22→0.19; benches, an elder, one napper, greenery gets the space | the widest gaps of the daylight day — three screens with a single silhouette. Golden-hour light does the work instead of population | golden keyframe arrives at 121.5 s | long low amber; lamp posts installed but dark; leaves at their densest drift |
| 121–127 | .309–.323 | **The hush** | 0.19→0.16 — the day's quietest daylight | **Inversion:** attention verbs are switched OFF. Everyone on the deck keeps working and pointedly does *not* look up | the clown gauntlet is 0–3 s away; the town ignoring Pip is more ominous than the town watching | one lamp post's glass catches the low sun as a single specular flick — the only bright event |

---

### CHAPTER 5 — **THE JESTER'S GAUNTLET** · ~127 – 143 s · phase ~0.323 – 0.363
*So the player feels: nobody is going to help me with this.*

Pillar-anchored (pillar 65), so gated on the event, not the clock. Fused warren spacing 72 px = **0.45 s per pillar** — a 10-roll is ~4.5 s, a 25-roll ~11.3 s. This is the hardest sustained gameplay of the day, so the sidewalk's job is **to get out of the way and make that legible**.

| Beat | Street | Signature | Ties to | Light & sound |
|---|---|---|---|---|
| **Pre-clear** (2 phantom pillars before the die) | base drops to 0.14, near lane cleared entirely | the near deck goes empty — the largest, most distracting figures leave first. Reads as the street clearing a lane | matches the 2-pillar phantom pre-clear in the sky | deck contrast flattened 10% so the warren silhouettes pop |
| **Die reveal + lead-in** | far lane only, ≤2 figures on screen, both walking away from camera-right | one child is **pulled back** by an adult's arm — the whole "this is dangerous" read in one 18-px gesture | the die reveal | a single struck-wood tick |
| **Gauntlet** | frozen: no new spawns, no verbs, no weather flourish, greenery only | absolutely nothing happens on the sidewalk for 4.5–11 s. This is a design *decision*, not a gap | player attention is 100% on the warren | deck light held perfectly steady — no flicker, no glint, nothing that could read as a hazard |
| **Outro** (1 pillar) | base 0.16 → 0.34 over 4 s | **Happening #4 — The Jester's Coin:** a small figure in the far lane flips something bright that arcs and is caught. The single sustained **SWELL** of 4 fires, a flock launches, the near-lane drummer hits twice | the only moment the street applauds a gameplay outcome directly | the drum is the day's first of the four drum cues — plants the finale's language |

---

### CHAPTER 6 — **THE LANTERN RAISING** · 143 – 190 s · phase 0.363 – 0.483
*So the player feels: they did this for me. (And if I die now, I die at the good part.)*

**The most important chapter in the plan.** `SUNSET` keyframe at 163.5 s. Median death at **156 s** falls inside the haul. Three-stage build, so the payoff starts early enough for the median player and crests for the survivor.

| t (s) | phase | Beat | Street | Signature | Ties to | Light & sound |
|---|---|---|---|---|---|---|
| 143–152 | .363–.386 | **The crew** | 0.34→0.52; a bare banner pole enters the near lane with four rope figures; the red lantern lies on a trestle, unlit | the crew is **standing still, looking up** — the only stationary group of the day. They are waiting for the flyer | pure setup; reads even if the player dies here | golden hour at full amber; the lantern's red is the deck's only saturated colour |
| 152–163 | .386–.415 | **THE HAUL** | 0.52→0.72 | **Happening #5 — The Raising.** Ropes go taut in stagger; the lantern climbs the pole over ~6 s of visible rise, cresting at near-lane full height. *This is the median run's last image: a red lantern rising to meet Pip as the sky turns.* Once per day | the sky hits `SUNSET` at 163.5 — lantern and sunset crest together | a rope-creak / hauling-chant rhythm in 4; the sky goes rose behind a red silhouette |
| 163–175 | .415–.445 | **The cascade** | 0.72→0.75 — day's second-highest crowd | prayer-flag bunting **unrolls off the pole in both directions**, a wave travelling with the scroll so it opens ahead of Pip. Second flock launch. Buskers all switch to the golden band (musician / tea-pourer / fan-dancer) | pays off the wish-tree tie at 30–40 s | the busiest silhouette frame of the daylight half; garland strings begin to read as *light* rather than beads |
| 175–183 | .445–.470 | **Dispersal** | 0.75→0.55 | the crowd breaks up in threes and the pole recedes; one figure stays, looking up at the lantern | breathing room before the storm chapter | rose → lavender; first true lamp-kindle as the sky darkens |
| 183–190 | .470–.483 | **Lamplighter** | 0.55 flat | the **lamplighter** walks left-to-right *ahead of the scroll*, kindling posts in front of Pip — the town lighting the road forward | the drizzle begins at 190.1; the last calm frame | lamps kindling at ~0.4 intensity, capped at 150; the first cool cast on the deck |

---

### CHAPTER 7 — **THE STORM** · 190 – 273 s · phase 0.483 – 0.694
*So the player feels: the town got caught out too, and it stayed anyway.*

The longest chapter (83 s) and the one that most needs internal shape. `DUSK` at 211.5, `NIGHT` at 253.5, storm peak 247.7, lightning 244.5–273.3.

| t (s) | phase | Beat | Street | Signature | Ties to | Light & sound |
|---|---|---|---|---|---|---|
| 190–200 | .483–.508 | **First spots** | base 0.50; weather factor 1.0→0.94 | awnings **unroll** stall by stall in a stagger travelling with the scroll; goods get cloth thrown over them. No one has left yet | drizzle onset; `WEATHER_UMBRELLA_RAIN_AT = 0.12` crosses at ~196 s | first splash particles on the deck; paving begins to darken (`wetness` builds past `rain ≥ 0.18` at ~197 s) |
| 200–212 | .508–.537 | **Umbrellas** | 0.50→0.55 base; weather 0.88→0.78 | umbrellas raise **together** (single frame-wide gate — never per-figure strobing). The festive brolly palette is the deck's colour event | umbrella power-up spawns at pillar 112 (~211 s) — the street shows you what it's for a beat before the game hands it to you | lamps at half; first wet reflections as vertical smears under each lamp; rain hiss |
| 212–224 | .537–.564 | **Buskers pack** | base 0.55; weather 0.78→0.65 | the performer folds up in one visible beat *before* leaving — departure is a **choice**, not a despawn. Kids gone. Animals gone except the one dog under the kiosk | `DUSK` keyframe; drizzle peaks 222 | reflections lengthen; the deck is now more reflection than surface |
| 224–241 | .564–.612 | **Emptying** | base 0.57; weather 0.65→0.30 | shelter figures accumulate under kiosk awnings and lamp bases — 3–5 tight clusters. **The cauldron and the tea stall never close** (night-market food ran latest, historically). Second umbrella at pillar 124 (~232 s) | the street thins as the storm builds — one-way, staggered over ~8 s per slot, no flicker | the cauldron's fire is now the warmest thing on the deck; steam vs. rain, warm vs. cool |
| 241–256 | .612–.661 | **THE PEAK** | base 0.60 × weather 0.22 = **~0.13 effective** | **Happening #6 — The Boy Who Wouldn't Shelter.** One small near-lane figure stands out in the open, face up, arms out, while everyone else is tucked in. An adult silhouette comes out, stands beside him, and they both stay. Once per day | storm-jolt lightning fires above `rain ≥ 0.85` (~241–256 s); `NIGHT` keyframe at 253.5 | on each flash the whole deck **rim-flashes**: silhouettes pure dark against a pale wet ground for one frame. 1 in 3 flashes makes sheltered figures flinch (shoulders drop 1 px) |
| 256–273 | .661–.694 | **The break** | base 0.60 × weather 0.30→0.95 | umbrellas come down in stagger; awnings roll back one at a time; the cauldron vendor steps out and looks up. Density climbs fast | lightning window runs to 273.3; rain ends 273.3 | wetness at maximum but rain gone: **the deck is a mirror under the first festival lights**. The most beautiful 17 seconds of the night and it costs nothing new |

---

### CHAPTER 8 — **THE FESTIVAL** · 273 – 302 s · phase 0.694 – 0.768
*So the player feels: I outlasted the storm and the whole town came back out for it.*

Only 29 seconds, and it must be the biggest thing in the day. Moved off the rained-out 0.66 crest to **peak at 0.732 (288 s)** where rain = 0 and snow = 0.

| t (s) | phase | Beat | Street | Signature | Ties to | Light & sound |
|---|---|---|---|---|---|---|
| 273–281 | .694–.714 | **Ignition** | 0.70→0.90 | the braziers light in a **chain travelling left-to-right**, faster than the scroll, so the street ignites *ahead of* Pip. Every food stall reopens; banner poles go up | rain over; deck still wet, so every new flame doubles in reflection | the day's largest warm-vs-cool contrast; all glow ≤150, coin still sole-brightest |
| 281–295 | .714–.750 | **PEAK** | **1.00** — the day's fullest street | **Happening #7 — The Lion Wakes.** Lion dance and dragon (red + jade) both in frame; the drummer hits the day's second drum cue. Mask-changer busker in the near lane. Onlookers ring the acts | the crowd is thickest exactly where the night sky is darkest — maximum contrast | lantern garland + fairy lights + lamps, all full; wet reflections underneath; drums and gongs |
| 295–302 | .750–.768 | **The lantern glows** | 1.00→0.85 | the pole lantern from Chapter 6 is **lit** for the first time and is now the deck's single brightest red — the baton, paid off in the middle of the loudest moment | pays 152–163; sets up the release | flame flicker only; the first flake crosses frame at ~301 and nobody reacts yet |

---

### CHAPTER 9 — **THE THIRD DRUM & THE SQUALL** · 302 – 366 s · phase 0.768 – 0.930
*So the player feels: everyone went home, and a few stayed for me.*

The longest single chapter (64 s) and near-empty by design (`WEATHER_CROWD_SNOW_MIN = 0.06`). Tailwind runs scroll at +40%, so the street whips past — sparse is *correct*. The spectacle here is **not crowd, it is singular figures, light, and the deck visibly changing state.**

Historically anchored: markets legally closed "at the three drum beats" (~11pm–1am) and reopened "at the five drum beats." The drum is the chapter's opening gesture.

| t (s) | phase | Beat | Street | Signature | Ties to | Light & sound |
|---|---|---|---|---|---|---|
| 302–315 | .768–.800 | **The Third Drum** | 0.85→0.45 base; weather 1.0→0.76 | three deep drum hits (the day's third cue). On each hit, a **row of stalls shutters in sequence** — a teardown wave travelling with the scroll. Crates stack, awnings roll, banner poles come down | closing time, structurally identical to the historic curfew drum | the deck loses a third of its light sources in 13 s; cooling fast |
| 315–327 | .800–.832 | **First cover** | 0.45→0.34 base; weather 0.76→0.45 | `snow_cover` starts whitening awning tops, bench slats, lantern crowns, cairn caps — **the street changes colour without changing cast**. Near-lane walkers leave footprint trails | `PREDAWN` keyframe at 327.5; snow crosses 0.45 at ~320 and starts loading on Pip | bunting and garlands stream near-horizontal in the tailwind; flames lean |
| 327–336 | .832–.855 | **THE WATCH assembles** | base 0.30 × weather 0.10 ≈ 0.03 — plus the **Watch floor** | **Six figures placed on a fixed world-slot row, exempt from the density gate** (same idiom as shelter figures): the lamplighter · the shrine keeper by the incense · the noodle cauldron that never closes · the dog under the kiosk · the sleeper on the bench under snow · the sweeper clearing one square of deck, over and over | the town's answer to "night is a reward" — the reward is *intimacy*, not volume | six warm points in a cold blue field; the coin passing overhead is the seventh and brightest |
| 336–349 | .855–.888 | **Whiteout** | Watch floor only | snow cover reaches full. **The pole lantern is still lit**, wearing a snow cap, guarded by one figure with an arm raised over it. The single strongest "they're doing this for you" image of the run | snow plateau (clamped 1.0); Pip's `snow_load` full | `SNOW_TINT` wash; everything cool except six warm dots; wind roar |
| 349–360 | .888–.915 | **Easing** | Watch floor + 0.02 | the sweeper's cleared square finally holds. Breath puffs become visible against the lightening sky | snow falling off peak; melt begins | wind drops, wash thins; the cool blue starts admitting pink |
| 360–366 | .915–.930 | **Pink** | 0.02→0.22 | one shutter goes up — the first of the finale's chain. The lamplighter turns and starts walking back the way he came | `SUNRISE` keyframe at 363.5 | the deck reads pink-on-white for the first time all day |

---

### CHAPTER 10 — **THE FIFTH DRUM** · 366 – 393.5 s · phase 0.930 – 1.000
*So the player feels: the whole town got up to see me off, and then they let it go.*

The existing beloved beat, amplified. `CYCLE_FINALE_RUSH_PILLARS = 3` forced coin-rush pillars fire at the wrap with the chest on pillar 2 (`+100`, `TREASURE_BOX_ANIM_T = 1.5`). The street's job is to build the last 27 seconds toward it and then answer it.

| t (s) | phase | Beat | Street | Signature | Ties to | Light & sound |
|---|---|---|---|---|---|---|
| 366–378 | .930–.961 | **Shutters** | 0.22→0.35 | five deep drum hits (the day's fourth and final cue — the fifth drum, market reopening). Shutters go up **left to right in accelerating cadence**, each with a puff of steam. Snow melting off awnings in drip lines; puddles reuse the wet-paving reflection | the historic "reopen at the five drum beats" closes the loop the third drum opened | drip, steam, shutter-clang rhythm accelerating into the finale |
| 378–386 | .961–.981 | **The Wick Line** | 0.35→0.45 | every brazier and lamp on the street **relights in a single left-to-right chain running faster than the scroll**, so the light arrives ahead of Pip. Mirrors the festival ignition at 273 — the day's rhyme | snow cover gone by 384.5 | the deck goes from white-cold to gold in eight seconds; the coin still wins |
| 386–392 | .981–.996 | **THE BOW** | spike to **0.75** — the day's third peak | every figure on the deck **stops walking and turns to face screen-right**, arms rising in a slow stagger. Not a cheer. A held gesture. A row of raised silhouettes at 18 px, which is exactly the scale at which this reads best | the forced coin rush is about to start; the street is bracing for it | held; almost no motion; only the flames move |
| 392–393.5 | .996–1.000 | **THE RELEASE** | 0.75 held | **Happening #8.** The pole ropes are cut and **the Flyer's Lantern rises out of the near lane** — the same red lantern bought at 14 s, tied at the wish tree at 35 s, hauled at 152 s, lit at 295 s, guarded through the squall. The only thing on screen moving *upward* | the coin rush + chest fire in the sky at the wrap | one soft breath-cue; the lantern's glow capped ≤130 luma so the chest and coins own the frame |
| **wrap +0 → +6** | new day 0.000+ | **The Answer** | 0.75 → 0.30 over 6 s | on chest pickup, **5–7 more sky lanterns lift from the far lane in a coordinated wave** (the real Pingxi ritual releases in coordinated waves; ours is a wave of six, which is all 360 px can hold). They drift up and right and off-screen over ~6 s as the new `DAY` palette snaps in | the sky's `+100` fanfare is answered from the ground; then the street resets to Chapter 1 without a cut | the loop closes on the same flat noon light it opened on — the shutters already up, because the fifth drum already rang |
| **day 2+** | — | **The Second-Day Mark** | — | one persistent change per completed day: **an extra banner on the pole**, up to 5. The only diegetic acknowledgment of `DAY_SCROLL_STEP` / `DAY_GAP_STEP` | silent difficulty ramp gets a silent visual | — |

---

## 4. Weather overlay matrix

Weather **modulates** a chapter; it never replaces it. Governing rule: *the town's job for the day does not change because of the sky — only how it does that job changes.*

### Universal rules (apply in every chapter)

| Rule | Detail |
|---|---|
| **One-way departure** | Figures leave once, staggered over ~8 s, latched per slot. Never flicker, never re-enter as conditions oscillate. |
| **Leaving is an action** | Every departure is preceded by one visible beat of packing (fold the busker's mat, cloth over the goods, lid on the pot). A despawn without a pack-up beat reads as a bug. |
| **Base density is fair-weather intent** | `_weather_crowd_factor` does the emptying. Never author a low base *and* let weather multiply it. |
| **Weather never reaches the bird lane** | All weather-driven street changes stay below y=560. |
| **Contrast, not brightness** | Wet and snow both work by making warm sources read warmer against a cooler deck. No element's luma rises. |

### Per-condition × per-chapter behaviour

| Condition (real code signal) | Ch 1–2 Arrival / Market | Ch 3 Steam Morning | Ch 4–5 Lull / Gauntlet | Ch 6 Lantern Raising | Ch 7 Storm | Ch 8 Festival | Ch 9 Squall | Ch 10 Fifth Drum |
|---|---|---|---|---|---|---|---|---|
| **CLEAR** (default) | full stall complement, hard short shadows | vents steam freely, rope fences up | widest gaps, longest shadows | pole raised dry, bunting cascade at full spread | *(n/a — always wet here)* | braziers + wet deck | *(n/a)* | drip-free, straight to Wick Line |
| **CALM BREEZE** ph .08–.28, peak .18 | leaf drift starts, bunting has a slow lift | **its natural home** — leaves cross the deck against the rising steam; awning cloth ripples 1 px | last leaves settle into the greenery beds | — | — | — | — | — |
| **DRIZZLE** rain .05–.35, ph .483–.564 | *(fallback)* awnings out, hats tipped, nobody leaves; density ×0.94→0.78 | vents steam **harder** against the cool — the deck's best-looking weather state | gauntlet: drizzle allowed but **splash particles suppressed** during the warren | pole raised in the wet; the lantern's red is the only warm thing | **canonical** — awnings unroll, umbrellas raise together, reflections begin | umbrellas over the lion dance; the dance continues | — | — |
| **THUNDERSTORM** rain ≥.5, peak 1.0 @ .630 | *(fallback)* market collapses to 3 shelter clusters; the tea stall stays | *(fallback)* vents produce **more** steam; two vendors work the cauldrons regardless | never permitted during the gauntlet (visual noise) | *(fallback)* the crew hauls it up anyway and it swings — a better image than the dry version | **canonical** — 0.13 effective, 3–5 shelter clusters, cauldron + tea stall open, the Boy Who Wouldn't Shelter | *(fallback)* the festival under a roof of umbrellas; the lion dances anyway | — | — |
| **LIGHTNING** flash, ph .621–.694 | *(fallback)* one-frame rim-flash; hens scatter | *(fallback)* the flash whites out the steam plumes | forbidden during the gauntlet | *(fallback)* the pole silhouettes black against a white deck | **canonical** — full-deck rim-flash; 1-in-3 flashes cause a 1-px flinch | rim-flash reads as part of the festival | — | — |
| **WET PAVING** `wetness`, ~197–290 s | *(fallback)* the sweeper's water arc pre-figures it | *(fallback)* geyser mineral pools read as puddles | — | — | reflections build as vertical smears; deck darkens 12% | **the 273–302 payoff** — every festival flame doubles in the mirror | melts back in at 384 s as puddles | puddle reflections carry the Wick Line |
| **SNOW SQUALL + TAILWIND** ph .766–.977 | *(fallback)* stalls shutter early, one brazier per screen | *(fallback)* vent steam vs. snow — the strongest warm/cool image available | — | *(fallback)* the lantern is hauled up through the snow | *(fallback)* umbrellas on only 40% of survivors | **canonical tail** — the festival's last 7 s take the first flakes and ignore them | **canonical** — Watch floor of 6; bundled poses, breath puffs, streaming bunting | squall ends 384.5 |
| **SNOW COVER** accum/melt | *(fallback)* white caps on awnings from frame one | — | — | — | — | white edging on lantern crowns | **the chapter's real spectacle** — the deck changes colour with no cast change | melt: drip lines, patchy white, puddles |
| **VENT MIST** — **NEW (optional)** | — | a low ground haze on the deck band only, alpha driven by `thermal_intensity`, capped so silhouettes stay readable. The only genuinely missing weather layer, free from an existing curve | — | — | — | — | — | — |

> **Note:** there is no fog in `weather.py`. Vent mist is the only new atmospheric proposed, and it reuses an existing signal.

---

## 5. Tournament-awareness layer

The street is the audience. It must never be the HUD.

### Seven attention verbs, all readable at 18 px

| Verb | Motion | Duration | Lane |
|---|---|---|---|
| **LOOK** | figure stops, head tilts up 2 px | 0.8 s | far only |
| **POINT** | arm to 45°, hold, drop | 0.6 s | far only |
| **WAVE** | fan / scarf / hat raised and shaken 2 px | 1.2 s | near |
| **RUN-ALONG** | a kid runs right at ~1.1× scroll, drifts ahead, falls back | 2.5 s | near |
| **HUSH** | all figures currently in LOOK freeze; one flock launches | 0.35 s | far |
| **SWELL** | 2–4 figures enter LOOK/POINT staggered over 1.5 s, then release | 1.5 s | far |
| **TURN** | everyone faces screen-right, arms rising | held | both |

### Gating rules — these keep it ambience

1. **Never above y=560.** Nothing enters the play area.
2. **Zero verbs** during: the first 19 s (newbie plateau), the entire clown gauntlet, and any frame with `rain ≥ 0.5`.
3. **Max 2 concurrent** verbs on screen; **min 1.2 s** between triggers.
4. **No motion faster than the scroll** except RUN-ALONG, capped at 1.1×.
5. RUN-ALONG at most **once per 25 s**.
6. LOOK/POINT/SWELL live in the far lane (~11 px figures, read as texture). The near lane stays calm.

### Event reaction bindings

| Gameplay event | Street response |
|---|---|
| Near-miss (Pip within ~6 px of a pillar edge) | **HUSH** + one flock launch. Throttled to once per 10 s |
| Score milestone (every 25) | **SWELL** of 2–4. Never more than 4 |
| Geyser erupts | 2 nearest figures back off 4 px; one shields; a hen scatters. Once per 8 s |
| Genie lamp pickup | the day's only **synchronized LOOK**; incense smoke doubles for 3 s |
| Clown gauntlet begins | **verbs OFF** — the town pointedly ignores Pip. The inversion is the beat |
| Gauntlet cleared | sustained SWELL of 4 + flock + two drum hits |
| Power-up pickup | **nothing.** Deliberate — the street reacts to flight, never to inventory |
| Treasure box picked up | the Answer: 5–7 sky lanterns lift in a wave |
| **Death** | every visible figure goes to LOOK for 1 s; near-lane lights dim 15% under the game-over overlay. Cheap, and it says *the town saw it* |

---

## 6. Variety & no-repetition rules

1. **Beat-scoped pools.** Each chapter draws from 4–7 scene builders. A chapter never repeats a builder within 3 consecutive slots.
2. **Slot-frozen variants.** Each world slot freezes its variant index from its world key (the existing `_slot_latch` / `_prop_latch` idiom) — a figure never morphs mid-pass.
3. **No identical neighbours.** Within any 3 consecutive slots: no repeated `(family, variant)` pair, and no repeated silhouette height class. Height-class alternation is what actually kills the "loop" read at this scale — more than colour does.
4. **Per-run shuffle: 6 Arrival Cards × 3 Town Moods = 18 opening flavours.**
   - *Cards:* **Flag Drop** (a vendor on a stepladder finishing the tournament banner, ladder wobbling) · **Runaway Cart** (a wheel goes, oranges roll, two figures chase) · **Sweep & Water** (the sweeper's arc, wet paving catching sky) · **The Bell Boy** (a kid sprinting the near lane, heads turning one by one behind him) · **Pigeon Launch** (`draw_flock` bursting off an awning as Pip's shadow crosses) · **Half-Open** (half the stalls still shuttered, one thrown up on a bright clang).
   - *Moods (cosmetic reweights only, whole-run):* **Fair Day** (default) · **Pilgrim Day** (more elders, incense, wish-tree; fewer performers) · **Trade Day** (more carts, crates, animals, vendors).
5. **Rotation offsets.** Each run picks a random pool rotation offset per chapter, so even the same mood lands a different sequence.
6. **One-per-day budget.** Each scripted Happening fires at most once per cycle, tracked by a per-cycle flag reset at the wrap.
7. **The rare-sighting deck (7 cards).** Each run shuffles the deck and arms the **top 2** with independent ~35% rolls inside their windows, so a typical run sees 0–1 and seeing one feels like luck: *the white cat on the awning ridge · the beekeeper · the bride's red-umbrella procession (3 figures) · the ox-cart · the monkey on a leash · the paper-kite seller with a real kite aloft · the blind erhu player under the last lamp.*
8. **Density breathes.** Within any chapter, modulate the slot gate by a slow sine (period ~11 s, ±25%). Evenly-spaced figures at constant density is the single strongest "this is a loop" tell.
9. **Anti-tiling on fixtures.** Fixture row periods must be mutually coprime and non-harmonic with `PIPE_SPACING = 280`. Prefer something like **233 / 179 / 311** over the current 250 / 128 / 205.

### The eight once-per-day Happenings

| # | Happening | Trigger window |
|---|---|---|
| 1 | **The Runaway Songbird** — cage door swings, flock bursts out and up | 40–50 s (ph .102–.127) |
| 2 | **The Kettle Chorus** — three vendors lift lids in stagger, three plumes mirror the geysers | 82–96 s (ph .208–.244) |
| 3 | **The Conjurer's Cart** — cloth pulled back 5–6 s before the genie spawns | 96–106 s (ph .244–.268) |
| 4 | **The Jester's Coin** — a bright arc flipped and caught, on gauntlet clear | gated on gauntlet outro |
| 5 | **The Raising** — the lantern climbs the pole over ~6 s | 152–163 s (ph .386–.415) |
| 6 | **The Boy Who Wouldn't Shelter** — one figure stands out in the storm; an adult joins him | 241–256 s (ph .612–.661) |
| 7 | **The Lion Wakes** — lion + dragon together, drum cue | 281–295 s (ph .714–.750) |
| 8 | **The Release** — the Flyer's Lantern is cut loose and rises | 392–393.5 s (ph .996–1.000) |

---

## 7. Narrative arc

**Shape: two rising crests, a trough, a third crest, a long lonely hold, and a coda that becomes the next morning.**

The day opens *in medias res* — the market is already loud, and the town's first act is to buy a red lantern and tie it into a wish tree for a flyer it has only just noticed. The market roar (35 s) is the first crest, deliberately front-loaded because everyone sees it. The steam morning trades crowd for texture — fewer people, more happening — and hands the day to a genuine fifteen-second valley, the emptiest daylight of the run, whose only job is to make the jester's gauntlet feel dangerous. During the gauntlet the sidewalk does *nothing at all*: the town's refusal to look up is the most eloquent thing it does all day.

Then the second crest — deliberately placed to land on the median player's last ten seconds. The lantern is hauled up a pole at 152 s and crests exactly as the sky hits its SUNSET keyframe; bunting cascades open ahead of the scroll; the crowd hits 0.75. **Half of all runs will end on a red lantern rising to meet the bird.** That is the single most important pacing decision in this plan, and it replaces a status quo in which the median player dies in the emptiest street of the entire day.

The storm is the trough — 83 seconds of the town being driven indoors, given internal shape by awnings, umbrellas, a lightning peak, and one child who won't come in. It must be a trough, because the third crest depends on it: at 273 s the rain stops, the deck is still a mirror, and the whole festival ignites into the reflection. Twenty-nine seconds at full density — the loudest, warmest, most crowded frame in the game — earned by outlasting the weather.

Then the deliberate long hold. Sixty-four seconds of snow and near-emptiness, where the reward changes register from spectacle to intimacy: six figures stay out all night, and one of them is standing over your lantern with an arm raised against the snow. The finale doesn't add people first — it adds *light*, in a wick line running ahead of the bird, then adds the crowd, then takes all the motion away for the Bow, then releases the lantern into a sky that answers with a chest. And because the loop rejoins on the same flat noon light it opened on, with the shutters already up, the ending is also a beginning — which is what "the fifth drum" meant in the first place.

**Energy pacing check:** no two peaks are adjacent — market (35 s) → texture → valley → gauntlet → raising (163 s) → trough → festival (288 s) → hold → finale (392 s). Every crest is preceded by a designed quiet. The two longest quiets (the lull, the squall) are the two that directly precede the two most important events.

---

## 8. Logistics

**Sound.** Four one-shot cues for the entire day, all quiet, gated to never mask gameplay SFX: the **shutter clang** (Arrival Card F), the **drum** (used exactly four times — gauntlet clear, festival peak, third drum, fifth drum), the **crowd swell whoosh** (the Bow), and the **release breath** (the lantern). Everything else in the "sound feel" columns is atmosphere to be *drawn*, not played — steam, sizzle, rain hiss, and chatter are carried by motion and particle density.

**Light contract.** `NIGHT_GLOW_CAP = 150` is inviolable: sky lanterns at ≤130, festival braziers at cap, the coin sole-brightest in every frame. Night chapters work by warm-vs-cool contrast — six warm dots in a cold blue field beats one brighter dot every time. Wet paving and snow cover are both *free* contrast amplifiers, which is why the two most beautiful moments in the day (273–302 and 336–349) cost almost nothing new.

**Gameplay readability.** Nothing above y=560, ever. Tall near-lane elements stay out of the bird lane (x 48–188) and the pillar lane (x 212–320). During the gauntlet the deck's contrast is flattened 10% and all motion stops. During the first 19 s the density ceiling is 0.35, no tall props, no attention verbs.

**Run-of-show signals (all already exist in code).**

| Signal | Drives |
|---|---|
| `phase` | chapter selection, density curve, roster, dressing, lighting |
| `t` (biome_time) | staggered run-fill: far 5 s / near 10 s / performers 14 s |
| `rain_intensity` / `storm_intensity` | crowd factor, umbrellas, awnings, shelter clusters, bundled poses |
| `wetness` / `snow_cover` | deck reflections and whitening — chapter texture, not cast |
| `thermal_intensity` | vent reactions, Kettle Chorus gate, optional vent mist |
| pillar counter | clown-gate, genie-gate (the only two pillar-anchored beats) |
| score / near-miss / pickup hooks | attention verbs, throttled per §5 |
| cycle-wrap flag | Happening budget reset, Second-Day Mark increment |

**Contingencies.**
- *Day 2+ compression:* everything is phase-driven, so all chapters hold. The two pillar-anchored beats (clown, genie) drift earlier; both are event-gated, not clock-gated.
- *Short runs:* the plan front-loads two crests before 165 s. A 30-second run still gets an Arrival Card, the market roar, and a wish-tree tie.
- *Long runs / multiple days:* the rare-sighting deck reshuffles per run, not per day; the Second-Day Mark gives repeat days a visible ledger.
- *Performance:* object count dominates cost. Peak density now occurs at 288 s, where rain and snow particle systems are both at zero — the three crests are deliberately placed where the particle budget is free.
- *If the Bow reads as too much:* cut the arm-raise and keep only the TURN. A row of 18-px figures all facing the same way is already the gesture.

---

## 9. Sources & inspiration

- **The drum framing** — Tang/Song *morning bell, evening drum* (晨鐘暮鼓) timekeeping; drum-tower beats opened and closed the city gates.
- **"Closes at the third drum, reopens at the fifth"** — Northern Song night-market regulation recorded in Meng Yuanlao's *Dongjing Meng Hua Lu* (c. 1147); direct source for Chapters 9–10.
- **Morning-market texture** (5:00–9:00 hours, dough in hot oil, steam off bamboo baskets, soy-milk vats) — Chapter 2's three-concurrent-steam-sources rule.
- **Temple-fair structure** (incense/paper-offering stalls ringing a temple; lion and dragon dances announced by gongs and drums) — the Pilgrim Day mood and the festival chapter.
- **The release** — the Pingxi sky-lantern ritual: wishes on the paper, coordinated release waves; hence one lantern followed by a wave of six.
- **Ambient-background restraint** — Team Alto's strip-away method and Tsuki's Odyssey's environmental storytelling justify the gauntlet's total silence, the no-reaction-to-power-ups rule, and the 2-concurrent-verb cap.
- **From the repo:** all phase/second anchors computed from `game/biome.py` (`_remap`, `DAY_HOLD_FRAC`, `NIGHT_BORROW_SECONDS`), `game/weather.py` (`_phase_for_pillar`, `_WIDTH_SCALE`, rain/snow/thermal curves), and `game/config.py`. The density diagnosis came from evaluating the live `_POP_KEYS` at the median death phase 0.396.
