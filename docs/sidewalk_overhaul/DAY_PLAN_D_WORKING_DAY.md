# THE WORKING DAY
### *Sidewalk behaviour plan — Skybit, one full biome cycle (393.5 s)*

**Concept in one line:** *The whole street is on the clock — the town works the parrot fly-tournament as its single biggest payday, opening the course at dawn, feeding and servicing it all afternoon, counting it by lantern-light and settling up at sunrise — so Pip never flies past scenery, only past people whose day depends on him.*

---

## 1. Concept

### Candidates considered (all inside "Race Day")

**A. The Ledger Street.** The town's economy *is* a running book on the race: wager stones, odds boards, touts, a dawn payout. Rejected as a spine — an odds board that visibly moves is one step from a score HUD, and the brief forbids the street reading as UI. Kept as a *texture* (wager stones, touts) rather than the through-line.

**B. The Course Is the Street.** The sidewalk is literally the tournament's ground operation: marshal posts, flag stations, water points, the finish apron. Extremely legible in silhouette, and marshal-flag colour is a real, learnable, textless language ([FIA/F1 flag conventions](https://www.formula1.com/en/latest/article/watch-f1-explained-what-do-all-the-marshals-flags-mean.11m6Sp8b24f4gfFUnwprNJ)). Rejected as a *sole* spine because a pure operations layer has no economy and no warmth — it would be all officials and no life.

**C. The Working Day (chosen).** B's vocabulary, powered by C's engine: the race is the town's **labour and payday**. Everyone — marshal, noodle vendor, flag-selling kid, rival flyer's ground crew, tout, judge at the tally rack — is *working the race*. The day's arc is a shift: open, rush, lull, second rush, weather it, count it, be paid.

**Why it fits.** It solves the two hard constraints structurally rather than cosmetically. First, **it can never read as score UI**, because everything on the street is keyed to *the day's own schedule and the weather* — a stall covers up because it's raining, a rack fills because it's late, a pennant goes amber because the course ahead is closed. The street is busy with its own business; the player is one flyer among many, which is exactly why glancing down feels like *overhearing* rather than *reading a display*. Second, **it makes every chapter obligated**: a work shift has a legible arc (setup → rush → lull → rush → crisis → count → settle) that maps naturally onto a day-cycle that already has a morning market, a storm and a treasure at dawn.

**The test every beat must pass:** *does someone on this stretch of street have a job to do, and can I tell what it is from a silhouette?* If not, it's dressing — and dressing goes in the deliberate voids.

---

## 2. At a glance

| | |
|---|---|
| **Duration** | one biome cycle = **393.5 s** (`CYCLE_SECONDS = 320 + DAY_EXTRA_SECONDS 73.5`) |
| **Stage** | bottom strip y≈560–640, ground line y=595, scroll ~160 px/s (ramping 125→160 over the first ~59 s) |
| **Lanes** | far promenade (stalls, posts, racks, greenery, hung strands) + near lane (~18 px figures, animals, performers) |
| **Audience** | one-button mobile players; median run **~156 s ≈ phase 0.397**, i.e. most runs end in late golden hour, just short of the SUNSET keyframe |
| **Cast palette** | existing families only: `ped_cast` ×50, `day_cast` (6 kids / 6 elders / 7 vendors), `food_stalls` ×5, `animals_cast` ×9, `greenery_cast` ×30, `props_cast` ×15 (lamp/banner/fire/bench/dress), `performers_cast` ×8 acts, festival specials ×5, `cheering_crowd` kit |
| **New set pieces** | **5** (marshal post, tally rack, crew trestle, wager stone, finish arch) — all re-skins/extensions of existing prop pools |
| **Hard limits honoured** | no glyphs, no faces; coin stays brightest (night cap 150 luma); calm street during newbie ramp (0–19 s) and the clown gauntlet; nothing solid above y=560 |

### Assumptions (stated, not asked)

1. **Above y=560.** The existing hung strands already sit at y≈477–500 (`draw_prayer_flags` at `GROUND_Y-118`, lantern garland at `GROUND_Y-97`). I read the y=560 rule as applying to **solid/opaque objects**: only the existing thin overhead strands may cross it, and **no new element may**. All five new set pieces top out at y=563.
2. **Median-run phase.** The brief says median ≈ dusk; the remapped keyframes put 156 s at **phase 0.397 — late golden, ~7 s before SUNSET**. I've planned to the real number. Consequence: **Chapter 5's opening is the ending most players get**, and is weighted accordingly.
3. **Pillar-anchored events drift.** `_phase_for_pillar` assumes uniform inter-pillar dwell, but the clown warren compresses spacing 280→72 px. Real arrival of pillar-anchored events (rain at pillar 100, snow at 169) can run **~13–33 s earlier** than the nominal times below, depending on the clown roll (10–25 pillars). **Every street reaction to a pillar-anchored event must therefore fire off the live signal** (`rain_intensity`, `storm_intensity`, `thermal_intensity`, event flags) — never off a hard-coded second. Times below are the nominal axis; treat them as ±20 s.
4. **The calm-breeze mismatch.** `calm_breeze` is `_bump(phase, 0.18, 0.10)` — a raw literal that was **not** width-scaled with the extended cycle, so the "golden-hour" leaf drift now actually lands at **t ≈ 31.5–110 s, peaking at 70.8 s: late morning.** I've designed to where it really is (a warm mid-morning breeze), and flagged it below as a thing the team may want to rescale.
5. Native and web behave identically; nothing here needs `pygame.mixer` on the web path.

### The real day axis (extracted from `biome.py`)

`DAY_EXTRA_SECONDS = (30 + 12) × (280/160) = 73.5` → `CYCLE_SECONDS = 393.5`. `DAY_HOLD_FRAC = 0.51`, `NIGHT_BORROW_SECONDS = 26.0`.

| Keyframe | remapped phase | wall-clock |
|---|---|---|
| DAY (solid hold begins) | 0.0000 | 0.0 s |
| *(unnamed DAY-hold keyframe — fade to golden starts)* | 0.1575 | **62.0 s** |
| GOLDEN HOUR | 0.3088 | **121.5 s** |
| SUNSET | 0.4155 | **163.5 s** |
| DUSK | 0.5375 | **211.5 s** |
| NIGHT | 0.6442 | **253.5 s** |
| PREDAWN | 0.8323 | **327.5 s** |
| SUNRISE | 0.9238 | **363.5 s** |
| wrap → DAY | 1.0000 | **393.5 s** |

### The real event anchors (from `config.py` / `weather.py`)

| Event | phase | wall-clock (nominal) |
|---|---|---|
| Newbie plateau ends (pillar 5) | 0.040 | 15.9 s |
| Calm breeze (leaf drift) window | 0.080 → 0.280, peak 0.180 | 31.5 → 110.2 s, peak 70.8 s |
| Thermal sinter-rocks begin | 0.127 | 50.0 s |
| Onboarding ramp fully done (pillar 25) | 0.150 | 58.8 s |
| **Geysers** active (`intensity ≥ 0.35`) | 0.175 → 0.268 | **68.7 → 105.5 s** |
| Thermal peak | 0.244 | 96.0 s |
| **Genie lamp** (pillar 50) | 0.261 | 102.6 s |
| Thermal window ends (rocks stop) | 0.285 | 112.0 s |
| **Clown gauntlet** starts (pillar 65) | 0.327 | 128.8 s → runs ~10–20 s |
| **Drizzle begins** (pillar 100) | 0.483 | 190.1 s |
| Paving wets up (`rain ≥ 0.18`) | ~0.525 | ~206 s |
| Umbrella power-ups (pillars 112 / 124) | 0.536 / 0.590 | 211.1 / 232.1 s |
| Storm bump opens | 0.5645 | 222.2 s |
| **Lightning window** | 0.6215 → 0.6946 | **244.6 → 273.3 s** |
| **Storm peak** | 0.6296 | 247.7 s |
| Storm ends; paving dries | 0.695 → ~0.71 | 273.4 → ~280 s |
| **Snow** first flakes | 0.766 | 301.3 s |
| Snow cover accumulates on ground | 0.813 → 0.911 | 320 → 358.6 s |
| **Snow peak** (tailwind max) | 0.871 | 342.9 s |
| Ground snow melted / flakes gone | 0.953 / 0.977 | ~375 / 384.5 s |
| Finale window opens (`CYCLE_FINALE_PHASE_HI`) | 0.950 | 373.8 s |
| **Wrap → 3 forced coin-rush pillars + treasure chest** | 1.000 / 0.00 | **393.5 → ~399 s** |

---

## 3. The race-day vocabulary

### Five NEW set pieces (everything else is recast)

| # | Piece | Build | Footprint | Job |
|---|---|---|---|---|
| N1 | **Marshal post** | `props_cast` lamp-pool sibling: slim pole + cloth pennant sleeve + 30 px foot platform | pole top **y=563**, pennant 563–571 | The street's punctuation and its flag language. Tallest solid thing on the sidewalk (32 px vs an 18 px pedestrian). |
| N2 | **Tally rack** | low wooden A-frame, 34 w × 20 h, hung with 0–14 short bamboo tokens | y 575–595 | The day's count. Tokens *accumulate with time*. |
| N3 | **Crew trestle** | trestle table + horizontal perch bar; feed pan, water bowl, folded wing-cloth | bar top **y=568** | A rival flyer's ground crew. The only place another parrot appears on the street. |
| N4 | **Wager stone** | re-skin of the existing planter/cairn prop: flat capstone + row of 3–7 flat slate pebbles | 9 h | The tout's business. Motion + colour only. |
| N5 | **Finish arch** *(finale only)* | two `_near_banner` poles + one sagging cloth span borrowed from the garland code | poles y=563, cloth sags to 573 | The day's full stop. Appears exactly once, from phase 0.95. |

### Recasting the existing families

| Family | Recast as |
|---|---|
| `ped_cast` ×50 | **Three liveries by role, recolour only** — *crew* (diagonal sash), *spectator* (plain), *official* (tall hat + carried pennant roll). Same 50 bodies, three palettes: 150 apparent variants. |
| `day_cast` kids ×6 | Runner-boys with token sheaves; flag-sellers hawking pennants along the barrier. |
| `day_cast` elders ×6 | Judges at the tally racks; the seated pose becomes the **stakes clerk**. |
| `day_cast` vendors ×7 | Stall-holders working the race trade. |
| `food_stalls` ×5 | Race-day catering. The **tea stall** doubles as the crew hydration point (grounded in real pigeon-racing recovery practice — birds come home depleted and are watered and fed immediately). |
| `animals_cast` ×9 | Dogs held short at the barrier rope; critters scavenging under the trestles. |
| `greenery_cast` ×30 | Planter beds become **course-edge barrier anchors** — the rope runs bed to bed. Keeps their existing "hold daytime colour all cycle" rule (they're the street's one constant). |
| `props_cast` ×15 | lamp → flag masts; banner → course banners; fire → braziers + night tally lights; bench → spectator seating; dress (laundry) → **drying wing-cloths** and stall awnings. |
| `performers_cast` ×8 | juggler → barrier crowd-warmer; musician → post band; **stilt-walker → the spotter** (raised, one arm up, tracking the sky); calligrapher → result-painter (paints a **colour bar**, never a glyph); teapour → crew hydration showpiece; fortune-teller → **odds tout**; fan-dance → victory salute. |
| Festival specials ×5 | lion/dragon → the **night prize procession**; banner poles + braziers → the tally shed and the finish apron. |
| `cheering_crowd.py` | The near-lane **spectator reaction kit** — pompom, flag, trumpet, drum, megaphone, tambourine, party horn already exist as drawables. This is the single biggest reuse win in the plan. |

### Three textless languages

1. **Pennant colour** (marshal posts) — the only "signal" system, and it reports on the **course**, never the player:
 **green** = course open, clear air · **amber** = caution ahead (thermals / gaunttlet / crowd on the line) · **white** = weather hold · **blue** = a flyer coming through (brief, rare) · **chequer** (black/white split cloth) = finish. Straight from real marshal convention, so it's intuitively legible to anyone who's watched a race.
2. **Token count** (tally racks) — bamboo tokens hung on an A-frame, grounded in the Chinese bamboo-tally (*qián chóu*) tradition of notched split-stick reckoning. Racks start empty at dawn and fill through the day. **Colour spec: pale bamboo (200,190,150) by day, cool (120,130,150) at night — never gold, never round**, so a rack can never be misread as coins.
3. **Pebble rows** (wager stones) — a tout re-orders 3–7 flat slate pebbles in red / blue / white. Pure motion and colour; no value is implied and no arrangement means anything. This is the plan's deliberate *nonsense* signal — it looks like a system, and isn't.

**The anti-HUD rule, stated plainly:** *pennant colour, token count and pebble rows are functions of time and weather only.* The player's score, coin count and power-ups **never** drive them. The player-reactive layer (§6) is limited to body language — heads turning, arms raising, a lean at the rope — and is always transient (<1.2 s) and always partial (a fraction of nearby figures, never all).

---

## 4. Master timeline — 393.5 s, 100 % accounted for

Nine chapters, 36 beats. `d` = target crowd density (the replacement `_POP_KEYS` curve is in §4.10).

---

### Chapter 1 — **GATES** · 0:00–0:19 · phase 0.000–0.048 · d 0.10 → 0.55
*Solid DAY. Newbie ramp — the street is calm by mandate, so the story is "the course isn't open yet."*

| t | phase | beat | street | signature moment | ties to | light & sound |
|---|---|---|---|---|---|---|
| 0–7 s | .000–.018 | **1a Empty apron** | d 0.10 → 0.30 via the existing 7 s `_run_fill`. Far lane: shuttered stalls, one sweeping elder, barrier rope lying **slack on the paving**. Near lane: two crew, no spectators. | The rope on the ground — the only frame of the whole day where the course line is not taut. | Run-start fill; nothing in the sky yet. | Flat noon light, no lamps. Broom scrape, distant single hammer. |
| 7–13 s | .018–.033 | **1b Opening vignette** *(1 of 5, seeded per run)* | d 0.30 → 0.42. One anchor only. | **V1 Rope:** two officials haul the rope taut between planter beds — it snaps straight as it passes Pip. **V2 Shutters:** three stall awnings roll up in a left→right ripple. **V3 Sweep:** elder sweeps, dog trails the broom, a kid drags a folded pennant twice his height. **V4 Weigh-in:** at a crew trestle a rival macaw is lifted onto a hanging scale-pan (real basketing ritual — done quietly, crew concealing their excitement). **V5 Second heat** *(day 2+ only)*: yesterday's tokens unhooked from a rack into a basket. | Pillars are still wide and slow. Street stays under the ramp's calm mandate: **one** moving anchor, no clumps. | Warm tan paving. Cloth snap (V1), wooden clatter (V2/V5). |
| 13–19 s | .033–.048 | **1c Green** | d 0.42 → 0.55. First **marshal post** scrolls in; official raises **green**. Behind him, first **tally rack — empty**. | The green pennant going up. It is the day's starting gun and it happens *below* the player, unannounced. | Pillar 5 (~15.9 s): the plateau ends and the ramp begins — course open, speed picks up. | Pennant colour is the first saturated non-sky green on screen. Single low gong (optional cue). |

**So the player feels…** *I've arrived somewhere just before it starts, and it's starting because of me.*

---

### Chapter 2 — **THE TRADE RUSH** · 0:19–1:02 · phase 0.048–0.158 · d 0.55 → **0.92** → 0.48
*Solid DAY, held. The commercial peak — the town monetising the morning.*

| t | phase | beat | street | signature moment | ties to | light & sound |
|---|---|---|---|---|---|---|
| 19–29 s | .048–.074 | **2a Doors** | d 0.55 → 0.80. All 5 `food_stalls` in rotation; vendors ×7 at full mix; flag-selling kids working the near lane. Roles: 45 % trader, 30 % spectator, 15 % crew, 10 % official. | A flag-seller kid trots the near lane at 1.4× relative speed with a fistful of pennants, overtaking the walkers. | Onboarding ramp still easing; pillars comfortable. Street rewards a first look down. | Steam plumes off two stalls (existing). Warm tan + red awnings. Broad market murmur. |
| 29–40 s | .074–.115 | **2b Peak trade** | **d 0.92 — the morning crest.** Rhythm band: *stall · stall · post · crowd-clump · void*. Wager stone with tout (fortune-teller pose) working a knot of four. | The **tout's first pebble move** — he sweeps the row left, re-lays it, and the knot around him re-clumps. Meaningless and completely convincing. | First `POWERUP_COOLDOWN`-spaced power-ups are appearing above. Street is at max life, sky at max plain. | Brightest, flattest light of the day — deliberately unlit, so night has somewhere to go. Peak murmur density. |
| 40–52 s | .115–.140 | **2c First token** | d 0.92 → 0.62. A judge (elder) hangs **the first token** on a rack that has been empty since 0:13. Runner-kid arrives, hands off, runs on. | The single token swinging on an empty rack. Plants Chapter 7's full racks and Chapter 9's stripped ones. | ~Pillar 15 territory: the first **coin rush** lands near here → barrier ripple (§6). | Token is pale bamboo, matte, deliberately dull against the coin. Wooden clack. |
| 52–62 s | .140–.158 | **2d Wind-down** | d 0.62 → 0.48. Stalls sell down; two vendors sit; crew trestle activity rises as trader activity falls — the shift changes from *selling* to *servicing*. | The **rival macaw on its perch bar**, being fed by a crew hand. Ten seconds of screen time. It will matter three times more today. | Ramp complete at 58.8 s — full 160 px/s scroll, full 280 px spacing. The street thins exactly as the game opens up. | Sky begins its DAY→GOLDEN fade at 62 s. First trace of amber on the stone. Murmur drops a third. |

**So the player feels…** *the busiest place I'll fly over all day, and it isn't about me at all.*

---

### Chapter 3 — **HEAT & THERMALS** · 1:02–1:52 · phase 0.158–0.285 · d 0.48 → 0.34 → 0.46 → 0.30
*DAY fading toward golden. Leaves drifting (breeze peak 70.8 s). Sinter rocks from 50 s, geysers 68.7–105.5 s, genie at 102.6 s.*

| t | phase | beat | street | signature moment | ties to | light & sound |
|---|---|---|---|---|---|---|
| 62–72 s | .158–.183 | **3a Heat lull** | d 0.48 → 0.34. Roles shift to 40 % idler. Benches occupied. Two dogs lying flat. Awnings extended for shade. A `props_cast` dress-pool line of **wing-cloths drying** in the far lane. | Four figures sitting in a row under one awning, all still — the first designed *stillness* of the day. | Calm breeze peaks at 70.8 s; the existing 3-leaf drift crosses the screen. The cloths on the line lift in the same wind. | Amber creeping into the stone. Cicada-flat quiet. First long **designed void** (~2.7 s of bare rope-and-paving). |
| 72–86 s | .183–.219 | **3b The vent line** | d 0.34 → 0.42. **Geysers now firing above.** Marshal posts in view flip **green → amber**. A stilt-walker **spotter** stands raised, one arm up, slowly tracking the sky. Water-carriers work the crew trestles. | ***SPECIAL: The Vent Rush.*** Two vendors physically drag a stall back from the vent line as a column bursts; a kid chases a hat lifted by the updraft. Fires once, gated on `thermal_intensity ≥ 0.35`. | Directly reacts to the live geyser event — the street is *afraid of the same thing that's helping Pip*. | Sinter rocks scattered on the far-lane paving (existing ground FX extended into the strip). Hiss, then a wet burst. |
| 86–98 s | .219–.249 | **3c Crowd at the vents** | d 0.42 → 0.46 (a small counter-peak). Spectators gather to *watch the geysers*, backs to the player, all facing upstage. Rope holds them. | Fifteen figures with their backs turned, one arm each raised, all pointed the same way — into the sky Pip is flying through. | Thermal peak at 96 s. Densest geyser activity. | Warm gold now clearly on the stone. A collective low "ooh" swell (optional cue) on each burst. |
| 98–112 s | .249–.285 | **3d The lamp** | d 0.46 → 0.30. Geysers taper (rocks only after 105.5 s). Crowd disperses back to trade. One **official walks the near lane pulling every amber pennant back to green**, post by post, as they scroll past. | ***SPECIAL: The Rival Launch*** (if not already fired 40–70 s). Crew lifts the rival macaw off the perch bar; it rises and exits the top edge of the sidewalk band into a pillar shadow. **Never crosses y=560.** | **Genie lamp at 102.6 s.** The street doesn't acknowledge it — the sky's business is not the street's. Restraint here makes the gauntlet reaction land harder. | Rocks stop scattering at 112 s. The green-pennant walk is the beat's only motion in the last 4 s. |

**So the player feels…** *the town is nervous about the ground and I'm above it.*

---

### Chapter 4 — **THE GAUNTLET HUSH** · 1:52–2:30 · phase 0.285–0.380 · d 0.30 → **0.14** → 0.55
*GOLDEN HOUR keyframe at 121.5 s. Clown gauntlet ~128.8 s onward. **The street must be calm** — so make the calm the story.*

| t | phase | beat | street | signature moment | ties to | light & sound |
|---|---|---|---|---|---|---|
| 112–124 s | .285–.315 | **4a The order comes** | d 0.30 → 0.24. An official walks fast, against the crowd's drift, hand out flat. Behind him, the crowd begins to turn. Every marshal post that enters: **amber**. | The single official moving faster than everyone else, in the wrong direction. Pure silhouette. | GOLDEN HOUR lands at 121.5 s — the amber pennants and the amber sky arrive together, by accident of the schedule and entirely to our benefit. | Long low sun; figures cast the day's longest shadows across the paving. Murmur drops. |
| 124–132 s | .315–.335 | **4b The sweep** | **d 0.24 → 0.14 in ~6 s.** | ***SPECIAL: The Sweep.*** Three marshals walk **abreast** down the near lane, arms out, herding the crowd off-screen right. The density drop is *visibly performed*, not faded. | Fires on the clown-event flag, 4 s before `CLOWN_START_PILLAR`. | Hush. Every ambient sound layer ducks ~40 % and stays ducked. |
| 132–142 s | .335–.360 | **4c Closed course** | **d 0.14 — the day's second-emptiest street.** Far lane: covered stalls, empty benches, coiled rope, one dog. Near lane: **one** marshal per screen, standing still, amber pennant. Nothing walks. | A completely motionless street scrolling past at 160 px/s. Nothing is more visible in a busy game than a thing that has stopped moving. | The gauntlet: `CLOWN_WARREN_SPACING = 72` — pillars come 4× faster. **Total foreground stillness during total sky chaos** is the plan's hardest contrast. | Golden light on an empty street. Only the ducked wind bed and the player's own flaps. |
| 142–150 s | .360–.380 | **4d Re-open** | d 0.14 → 0.55 over 8 s. Gates opened, rope re-anchored, crowd floods back **left to right in a wave**, not a fade. Pennants amber → **green** in sequence. | The flood-back. Deliberately the most *kinetic* crowd move of the day, purchased with 18 s of stillness. | Clown outro pillars; normal spacing resumes. The street celebrates the player's survival without acknowledging the player. | Ducking releases over 2 s. Braziers not yet lit — the last fully unlit beat. |

**So the player feels…** *whatever just happened up there, the town cleared the street for it — and they're back the moment it's over.*

---

### Chapter 5 — **EVENING TRADE** · 2:30–3:10 · phase 0.380–0.483 · d 0.55 → **0.78** → 0.60
*SUNSET keyframe at 163.5 s. **This is where the median run ends (≈156 s).** It must play as an ending even though it isn't one.*

| t | phase | beat | street | signature moment | ties to | light & sound |
|---|---|---|---|---|---|---|
| 150–162 s | .380–.412 | **5a Second wind** | d 0.55 → 0.72. The whole cast returns *changed*: role mix flips to 35 % spectator, 25 % trader, 25 % crew, 15 % official. Tally racks now visibly **half-full**. Two performers working the barrier (juggler, fan-dance). | The racks. A player who ends here has watched a rack go from one token to seven, and will feel a day has passed even if they can't say why. | Median run dies around 156 s. The last thing most players see is **a busy, warm, generous street** — not a lull. | Rose and orange sunset stone; the first lamp-post kindle (`_lit_intensity ≈ 0.4` from ~0.40). Full murmur returns, warmer than morning. |
| 162–172 s | .412–.439 | **5b Sunset trade** | **d 0.78 — the second crest.** Rhythm: *stall · rack · crowd-clump · post · void · trestle*. Wager stones busiest of the day; three touts visible across a screen-width. | A tout, a judge and a runner-kid meeting at one rack: hand-off, hang, run on. Three roles in one 40-px composition. | SUNSET at 163.5 s. Peak colour, peak commerce, deliberately together. | Lantern garland (always strung) now visibly *gaining* over the sky. Warm. |
| 172–182 s | .439–.466 | **5c First look up** | d 0.78 → 0.68. Two or three figures per screen stop and **look upstage-left**, unprompted. Stall-holders begin glancing at their goods. | A vendor's hand resting on a folded cloth he hasn't thrown yet. Pure pre-tension. | Sky is beginning to darken toward DUSK. Nothing has happened yet. **This beat's whole job is to plant the storm.** | Light dropping fast now. Murmur thins slightly and pitches lower. |
| 182–190 s | .466–.483 | **5d The first cover** | d 0.68 → 0.60. Two stalls throw cloth over their goods. One awning comes down. Crowd still trading, but pennants start going **white** on one post in three. | The first thrown cloth — and the man who throws it is the vendor from 5c. He is the character we'll follow through the storm. | ~190 s: **drizzle begins.** The street covers up *one beat before the first raindrop renders.* The town knows its own weather better than the player does. | Wind lifting the bunting. First slate-blue drizzle streaks appear at the very end of the beat. |

**So the player feels…** *this is the good part of the day, and it's ending.*

---

### Chapter 6 — **THE STORM SHIFT** · 3:10–4:33 · phase 0.483–0.695 · d 0.60 → **0.26** → 0.72
*DUSK 211.5 s, NIGHT 253.5 s. Drizzle 190 s → wet paving ~206 s → storm 222–273 s → lightning 244.6–273.3 s → peak 247.7 s. Umbrella pickups at 211 / 232 s. The energy trough of the lit day.*

| t | phase | beat | street | signature moment | ties to | light & sound |
|---|---|---|---|---|---|---|
| 190–206 s | .483–.524 | **6a Drizzle** | d 0.60 → 0.50. Existing `_wants_umbrella` opens at `rain ≥ 0.12` — umbrellas bloom across the crowd over ~6 s. Traders keep trading. Kids keep running. | The umbrella bloom itself, staggered left→right so it reads as a spreading realisation. | `WEATHER_UMBRELLA_RAIN_AT = 0.12`. | Rain colour is the warm-lit blue (180,192,220) at this stage. Soft hiss; splashes on the sidewalk band (existing `_Splash` already lands across GROUND_Y..H). |
| 206–222 s | .524–.565 | **6b Scramble** | d 0.50 → 0.38. | ***SPECIAL: The Downpour Scramble.*** The tea-stall awning unrolls in one motion and **eight figures pack under it in 2 s**, including the vendor from 5c/5d. Fires on the first frame `rain_intensity ≥ 0.35`. | `wetness` starts building at `rain ≥ 0.18` (~206 s) — paving glazes; pennant colours now **reflect** in the sheen. **Umbrella power-up at 211 s**: as it passes, the crowd's umbrellas are already up. The pickup reads as *joining the street*. | Braziers kindle early, out of schedule — storm gloom, not nightfall. Rain hiss up; murmur nearly gone. |
| 222–238 s | .565–.591 | **6c Weather hold** | d 0.38 → 0.30. Every marshal pennant in view: **white**, hanging wet and heavy (reduced snap amplitude — a wet flag doesn't fly). Crew trestles get cloths thrown over the perch bars. Shelter figures tuck under kiosk and lamp-post bases (existing behaviour). | A crew hand standing in the open rain with both arms over the covered perch bar, not sheltering himself. | DUSK at 211.5 s already passed; storm bump climbing. **Umbrella #2 at 232 s.** | Full wet sheen. Slate-blue rain (135,162,212). Lamp glow doubling in the reflection. |
| 238–254 s | .591–.645 | **6d Lightning** | **d 0.30 → 0.26 — the trough.** Near-empty near lane. Far lane: only lit shelter clusters, two per screen. Everything else is rope, rain and reflection. | On each existing full-screen lightning flash, **every sheltering figure is silhouetted black for 0.18 s** against the flash — the street rendered as pure shape, once, three times over the storm. | Lightning window opens 244.6 s; **storm peak 247.7 s**; NIGHT keyframe 253.5 s. `STORM_JOLT_RAIN_MIN = 0.85` — the jolt strike on Pip can land here. | Thunder (existing `audio.play_thunder`). Between strikes, the quietest 16 s of the day. Deliberate valley. |
| 254–265 s | .645–.673 | **6e Holding on** | d 0.26 → 0.34. First figures step **out** from under awnings and look up. One shakes out a cloth. The vendor from 5c starts uncovering. | One person walking in the open again while everyone else is still sheltering. | Storm falling off its peak; sky at full NIGHT palette but still rain-washed. | Rain thinning audibly. Braziers now the dominant light — warm against a cool wet street. Coin still brightest. |
| 265–273 s | .673–.695 | **6f Break** | d 0.34 → 0.72 over 8 s. Awnings roll back. Rope re-tightened. White pennants come down; **green** goes back up. Crowd re-floods. | The vendor from 5c re-opening his stall in the last of the rain, first man back in business. Payoff of a thread planted at 182 s. | Rain hits 0 at ~273.4 s; `wetness` dries over the next ~6 s. | Wet paving still mirror-bright under new brazier light — **the best-looking 8 s of the whole day.** Murmur returns, big. |

**So the player feels…** *the town got hit as hard as I did, and it's opening back up before the rain even stops.*

---

### Chapter 7 — **THE TALLY** · 4:33–5:27 · phase 0.695–0.832 · d 0.72 → **1.00** → 0.20
*NIGHT, full palette. The true crowd peak and the warmest street of the cycle.*

| t | phase | beat | street | signature moment | ties to | light & sound |
|---|---|---|---|---|---|---|
| 273–286 s | .695–.727 | **7a Lights up** | d 0.72 → 0.90. | ***SPECIAL: The Tally Shed Lights.*** Braziers along the rack row kindle **in sequence, left→right over 3 s**. Fires on the first frame `rain_intensity == 0`. | Post-storm. The dry-out of `wetness` runs underneath, so the reflections fade *as* the lights come up — a natural cross-fade nobody has to author. | Every light source capped at 150 luma per channel. Warm amber vs. the cool night stone — the contrast doing the work, not brightness. |
| 286–300 s | .727–.762 | **7b Full count** | **d 1.00 — the crowd peak of the day.** Every rack **full** (12–14 tokens). Judges seated. Runner-kids at their busiest. Food stalls all five in rotation, all glowing. Performers: musician + fan-dance + teapour. | A rack so full the tokens overlap into a solid textured band. Seven hours of accumulated work, readable in one glance, with no numbers. | Deep night; player is now well past most runs' ending — this is the reward tier and should be the densest, most detailed street. | Peak warm glow, peak murmur, food steam catching brazier light. |
| 300–312 s | .762–.790 | **7c Procession** | d 1.00 → 0.80. The existing **lion dance / dragon dance** specials, recast as the **prize procession** — they move *along* the near lane rather than performing in place, so they scroll past as a single long event rather than a repeated loop. | The dragon's body passing behind three marshal posts in sequence, occluding each pennant in turn. | ~301 s: **first snowflakes** appear at the top of the screen. Nobody on the street notices yet. | Loudest, brightest, warmest. Then the first flake crosses a brazier. |
| 312–327.5 s | .790–.832 | **7d Strike the shed** | d 0.80 → 0.20. Racks unhooked, tokens dropped into baskets. Stalls come down in a rolling wave. Crowd walks off-screen right in clumps. Pennants: **white** as the wind rises. | The dragon exiting frame right at the same moment the last stall shutters — the party leaving on the same beat the work ends. | Snow building; tailwind ramping (`WEATHER_WIND_SCROLL_FACTOR`). PREDAWN at 327.5 s. | Braziers thinning one by one. Murmur collapsing. Wind rising into the gap it leaves. |

**So the player feels…** *this is the night they've been working toward all day, and I'm allowed to see it because I'm still flying.*

---

### Chapter 8 — **THE COLD SHIFT** · 5:27–6:03 · phase 0.832–0.920 · d 0.20 → **0.07** → 0.26
*PREDAWN. Snow squall builds to peak 342.9 s; ground cover accumulates 320 → 358.6 s. The loneliest minute of the day, and the plan protects it.*

| t | phase | beat | street | signature moment | ties to | light & sound |
|---|---|---|---|---|---|---|
| 327.5–338 s | .832–.859 | **8a Handover** | d 0.20 → 0.12. Bare street: coiled rope, empty racks, three braziers, snow starting to lie in the far lane. | ***SPECIAL: The Cold Shift Handover.*** Two figures at a brazier pass a wing-cloth between them; one walks off right. The other stays — and stays for the whole of Chapter 8. | Snow cover starts accumulating at ~320 s (`WEATHER_SNOW_ON_WI = 0.45`). The whitening paving buries the wager stones and the low planter beds first. | Cool blue-grey wash climbing (`SNOW_TINT` → `SNOW_TINT_WHITE`). Wind only. |
| 338–350 s | .859–.888 | **8b Whiteout** | **d 0.07 — the emptiest street of the cycle.** One brazier and one figure per 1.5 screen-widths. Marshal posts still standing, pennants **white**, snapping hard in the tailwind (max snap amplitude of the day). | The lone brazier-keeper, snow-blown, holding a **green** pennant furled under his arm — ready to re-open, not yet allowed. | **Snow peak 342.9 s** — the tailwind is *helping the player fly faster* while the street is at its most abandoned. Maximum divergence between sky and ground; that's the point. | `SNOW_TINT_PEAK_A = 146` whiteout. Everything but the brazier and the coin desaturates. Wind roar. |
| 350–362 s | .888–.920 | **8c First light, first movers** | d 0.07 → 0.26. Snow easing after 358.6 s; the ground cover starts melting. Two or three figures out, sweeping snow off a rack. **The crew trestle passes with an EMPTY perch bar and a folded wing-cloth on it.** | The empty perch. The rival that launched at ~105 s hasn't come home. No emphasis, no music sting — 2 s of screen time, once. | Melt begins; predawn pink entering the palette. | Wind dropping. First scrape of a broom on snow — the same sound that opened the day at 0:00. |

**So the player feels…** *everyone went home and I'm still out here.*

---

### Chapter 9 — **SETTLING UP** · 6:03–6:33.5 (+~6 s over the wrap) · phase 0.920–1.000 → 0.00 · d 0.26 → **0.88** → 0.62
*SUNRISE keyframe 363.5 s. Finale window opens at 373.8 s. Wrap + treasure at 393.5 s.*

| t | phase | beat | street | signature moment | ties to | light & sound |
|---|---|---|---|---|---|---|
| 362–374 s | .920–.950 | **9a The town comes back** | d 0.26 → 0.55. Snow melting off the paving; figures arriving from the right in a steady stream — **walking against the scroll**, which reads as *converging*. Racks re-hung, this time with baskets underneath. Stakes clerk sets up a table. | The stream of arrivals. The first time all day people move *toward* something rather than along the street. | Ground snow gone ~375 s; SUNRISE colours peaking. Player is 6 minutes in and should feel arrival. | Peach and rose stone. Braziers still lit but losing to the sky. Murmur building fast. |
| 374–384 s | .950–.975 | **9b The chequer raise** | d 0.55 → 0.78. | ***SPECIAL: The Chequer Raise.*** The finale window opens (`CYCLE_FINALE_PHASE_HI = 0.95`). Every marshal post from this moment raises **chequer**. The far lane stops being stalls and becomes **a continuous line of people at the rope, three deep**. | The whole street's role mix collapses to one: everybody is a spectator now. Traders stop trading. | Last flakes clearing (~384.5 s). Existing bunting window re-opens at phase ≥0.85 — daytime prayer-flags are already back overhead. | Chequer cloth is the only black-and-white on screen: maximum silhouette contrast, and white capped at 150 so the coin stays king. Big cloth snap. |
| 384–393.5 s | .975–1.000 | **9c The apron** | **d 0.88.** **FINISH ARCH** (N5) scrolls in — two poles, a sagging cloth span across the near lane. Braziers relit along the apron. Every `cheering_crowd` prop in rotation: pompoms, flags, trumpets, drums, tambourines, party horns. Dogs up on hind legs at the rope. | The arch passing overhead-ish — it crosses the sidewalk band as a single object and is gone in ~2.5 s. It appears **once per cycle**, ever. | Runs directly into the wrap. | Roar. Everything warm. The one moment the street is *allowed* to be about the player. |
| 393.5 s → ~399 s | 1.000 → .014 | **9d Payday** | d 0.88 → 0.62 over ~6 s. The three forced coin-rush pillars fire; **treasure chest on pillar 2 of 3**. | On chest pickup: every chequer pennant in view **snaps to full extension for 1.0 s**, and every tally rack on screen **lifts its whole token row at once** — the day's entire count raised in salute, one gesture, no numbers. Existing `treasure_banners` + balloons fire on top. | `TREASURE_BOX_GRANT × day`. The street's payoff and the player's payoff are the same event. | Peak everything, then a hard exhale. |
| ~399 s → day 2 | .014 → … | **9e Second heat** | d 0.62 → 0.30 → back into Chapter 2's curve. Apron disperses; **the rope is coiled** (paying off Chapter 1's V1); tokens carried off in baskets; the crew trestle passes with the **rival macaw back on its perch, being fed**. Chapter 1's vignette pool switches to the day-2 set. | The re-fed rival. It came home after all. | The wrap never empties the street on a continuing run — the finish crowd *becomes* the morning crowd. A day-2 opening therefore never looks like a day-1 opening. | The gong from 0:13 again, one octave up. |

**So the player feels…** *I finished the race, the town was waiting at the line, and now they're setting up to do it all again.*

---

### 4.10 Replacement crowd-density curve

Drop-in for `_POP_KEYS`. Note the deliberate non-empty wrap.

```
phase   d      t(s)     what
0.000   0.10     0.0    gates — near-empty (×_run_fill on a fresh run)
0.030   0.30    11.8    opening vignette
0.048   0.55    19.0    ramp ends; course open
0.075   0.92    29.5    ██████████  MORNING TRADE PEAK
0.120   0.70    47.2
0.158   0.48    62.0    heat, day-hold ends
0.200   0.34    78.7    lull / longest void
0.244   0.46    96.0    counter-peak at the vent line
0.285   0.30   112.0    thermals over
0.315   0.24   124.0    the sweep begins
0.335   0.14   131.8    ██  GAUNTLET HUSH — closed course
0.380   0.55   149.5    re-open flood
0.415   0.78   163.5    ████████  SUNSET TRADE CREST
0.483   0.60   190.1    drizzle
0.524   0.50   206.2    scramble
0.591   0.30   232.5
0.630   0.26   247.9    ██  STORM TROUGH
0.695   0.72   273.5    the break
0.740   1.00   291.2    ████████████  NIGHT TALLY PEAK
0.790   0.80   310.8
0.832   0.20   327.5    strike the shed
0.871   0.07   342.8    █  WHITEOUT — emptiest of the cycle
0.920   0.26   362.0    first movers
0.950   0.55   373.8    settling up
0.985   0.88   387.6    ██████████  FINISH APRON
1.000   0.62   393.5    wrap — crowd PERSISTS into day two
```

Multiplied as today by `_run_fill` (7 s) and `_weather_crowd_factor` (`WEATHER_CROWD_RAIN_MIN 0.22`, `WEATHER_CROWD_SNOW_MIN 0.06`).

---

## 5. Weather overlay matrix

**Rule: weather modulates the chapter, never replaces it.** The people are still doing the same job — they're doing it wet, cold, or in a hurry. Eight universal modulation verbs, applied at chapter-specific strengths:

`crowd×` · `shelter` · `umbrella` · `cover` (goods) · `posture` · `pennant` (colour + snap amplitude) · `light` (bring braziers forward) · `ground` (sheen / snow burial)

| Condition (live signal) | Chapters it can touch | Modulation |
|---|---|---|
| **Clear** (default) | all | Baseline. Pennants green, full snap. Goods uncovered. Ground dry. |
| **Calm breeze** `calm_breeze` >0 · 31.5–110 s · peak 70.8 s | **2d, 3a, 3b, 3c** | `pennant`: lazy 0.3 Hz ripple, never a snap. Drying wing-cloths on the `props_cast` dress line lift and settle. Awnings billow. Two idlers hold hats. **No crowd change** — this is a pleasant wind. *(Note: the bump literal `_bump(phase, 0.18, 0.10)` was never width-scaled, so this now lands mid-morning, not golden hour. Design assumes mid-morning; if the team rescales it by `_WIDTH_SCALE`, move this modulation to Ch.4a–5a and treat the leaves as a sunset breeze instead.)* |
| **Thermals / geysers** `thermal_intensity` · 50–112 s, geysers ≥0.35 from 68.7 s | **3a–3d** | `pennant`: **amber** on all posts while `≥0.35`; pennants blow *upward* (inverted lift) near an active vent. `crowd×`: 1.0 at the rope, but a 60-px exclusion zone around each active vent — figures physically don't stand there. `cover`: stalls within a vent's footprint get dragged back once (the Vent Rush). `ground`: sinter rocks scatter across the far-lane paving; a thin heat-shimmer band along y=590–595. Kids *approach* the vents; elders don't. |
| **Drizzle** `0 < rain < 0.35` · ~190–206 s and ~265–273 s | **5d, 6a, 6e, 6f** | `umbrella` on (existing `_wants_umbrella` ≥0.12). `crowd×` ≈0.85. `cover`: one stall in three. `pennant`: green→**white** on one post in three; snap amplitude −30 % (wet cloth). `ground`: `wetness` starts, sheen begins to mirror pennant colour. Traders **keep trading** — this is not a crisis yet. |
| **Thunderstorm** `rain ≥ 0.35`, lightning 244.6–273.3 s | **6b, 6c, 6d** | `crowd×` → `WEATHER_CROWD_RAIN_MIN 0.22` at peak. `shelter`: all survivors under awnings/kiosk/lamp bases in clusters of 4–8 (never singletons — clusters read as people, singletons read as props). `cover`: **everything** — stalls, racks, perch bars. `posture`: hunched, hands in sleeves. `pennant`: **white** on every post, hanging near-vertical, snap −70 %. `light`: braziers kindle ~25 s early. **Lightning frames**: for the 0.18 s flash, every sheltering figure renders as flat black silhouette (no interior detail) — cheap, and the single most striking image on the street all day. |
| **Wet ground** `wetness > 0` · ~206–280 s | **6b–6f, 7a** | `ground`: existing `draw_ground_weather` sheen. Add: each lit source (brazier, lamp, lantern) gets a vertical smeared reflection in the near-lane paving at `alpha = 70 × wetness`, capped so it can never exceed the coin. Figures' feet get a 1-px bright contact line. Dries out under 7a, cross-fading with the brazier line coming up — no authoring needed, it falls out of the two curves. |
| **Snow squall + tailwind** `storm_intensity` · 301–384.5 s · peak 342.9 s | **7c (tail), 7d, 8a–8c, 9a** | `crowd×` → `WEATHER_CROWD_SNOW_MIN 0.06`. `posture`: lean *forward into the direction of travel* (tailwind pushes right, so figures brace right — matches Pip's own wind-lean). `pennant`: **white**, maximum snap amplitude of the entire day, streaming fully horizontal. `light`: braziers are the only light; each gets a small warm halo through the cold wash. `shelter`: the remaining 1–2 figures per screen stand *at* the brazier, not under cover — cold, not wet. |
| **Snow ground cover** `snow_cover` · 320–375 s | **8a–8c, 9a** | `ground`: paving whitens from the far lane inward. **Burial order** (by height): wager stones → planter beds → benches → tally-rack feet → trestles. Marshal posts and braziers never bury — the street's skeleton stays legible. Melt (from 358.6 s) reverses the order, so Ch.9a's returning crowd walks onto paving that's clearing under them. |
| **Storm jolt** (`STORM_JOLT_RAIN_MIN 0.85`, strike on Pip) | **6d** | The one player-coupled weather reaction: on the jolt frame, **three** sheltering figures nearest the strike x flinch (single-frame 2-px recoil) and one dog jumps. 0.5 s, then nothing. Never repeated. |

---

## 6. Tournament-awareness layer

Ambience, never HUD. Every rule is **transient**, **partial**, and **silhouette-only**.

| Trigger | Reaction | Budget |
|---|---|---|
| **Pillar passed** (any score) | 8–15 % of near-lane figures within 120 px do a 0.4 s head/torso turn toward the pillar line. Scales with density; disabled below d 0.20. | continuous, cheap |
| **Near-miss** (bird within ~8 px of a pillar edge) | 1–3 nearest near-lane figures raise one arm for 0.8 s. If a **spotter** (stilt-walker) is on screen, he tracks Pip's y for 1.5 s. No sound. | max 1 per 4 s |
| **Coin rush** (every 15th pillar) | **Barrier ripple** — 3–5 figures lean toward the rope in sequence, 0.15 s apart, left→right. A 5-figure wave, not a stadium wave. Optional low crowd swell. | once per rush |
| **Score gates** 100 / 200 / 250 (`POWERUP_SCORE_GATES`) | **Milestone flag-run** — a runner-kid sprints the far lane at 2× relative speed with a token sheaf toward the next tally rack, and hangs one token. Once per gate, max once per 20 s. | 3× per run, max |
| **Power-up collected** | Nothing. Deliberate. The street does not applaud pickups; if it did, it would be a HUD. | — |
| **Clown gauntlet** | The Sweep (§4, beat 4b) + total near-lane stillness + amber pennants. The single largest street reaction of the day, and it's a reaction to *danger*, not to score. | once |
| **Genie lamp / geysers** | Geysers: fear (§5). Genie: **no reaction at all.** Withholding here is what makes the gauntlet and the finale land. | — |
| **Pip dies** | Near lane does **not** mock or cheer. Every marshal pennant on screen drops to **half-mast over 1.2 s**, timed to `DEATH_FADE_DURATION` + the death-fade tail. Nothing else changes. Quiet, dignified, once. | once |
| **Finale** (phase ≥0.95 → chest) | Chequer raise → finish apron → full `cheering_crowd` kit → on pickup, pennants snap full + every rack lifts its token row for 1.0 s. | once per cycle |

**The line:** the street reacts to *events* (a pillar, a near-miss, a rush, a death, the finish) and never to *quantities* (score, coins, combo). Events are things that happen; quantities are things you'd have to read.

---

## 7. Variety & no-repetition rules

**R1 — Role-first casting.** Every figure is drawn from an existing family and assigned a **role** (crew / spectator / official / trader / idler) at slot entry. A chapter's roster is a *role mix ratio*, not a scene list. Identical prop layouts read completely differently because the people in them are doing different jobs. This is what turns 50 pedestrian bodies into ~150 apparent characters with three palettes.

**R2 — Slot-latched, never re-rolled.** Use the existing `_slot_latch` idiom: a world slot decides its content once on entry and never re-decides. Kills pop/flicker at window edges *and* guarantees a given x-offset never carries the same content twice running.

**R3 — No-repeat window of 4, per family **and** per role.** A variant can't reappear until 4 others from its family have been placed. Extend the existing per-family rule to also apply per-role, so you never get two officials in a row even if they're different bodies.

**R4 — Rhythm banding.** Each chapter carries a target *placement rhythm*, e.g. Ch.2 = `stall · stall · post · clump · void`; Ch.7 = `rack · rack · void · brazier · clump`; Ch.8 = `void · void · brazier · void`. The director fills by rhythm slot, so spacing reads as composed rather than evenly random.

**R5 — One anchor per screen-width.** At most **one** "look at that" set piece (marshal post, tally rack, crew trestle, wager stone, food stall) per 360 px. Everything else is texture. This is the rule that stops the street from competing with the pillars for attention.

**R6 — Deliberate voids.** Every chapter must contain at least one designed empty stretch of ≥1.2 screen-widths (≥430 px ≈ 2.7 s) carrying nothing but rope and paving. Voids are *placed by the rhythm band*, not left over. Chapters 3, 4, 6 and 8 carry two.

**R7 — Seeded run offset + vignette pool.** The day's content stream is offset by a per-run seed of 0–40 s of world-x within the Chapter 1–2 palette, and Chapter 1 picks 1 of 4 opening vignettes (5 on day 2+). The first 20 s therefore differ every single run while staying inside the newbie-ramp calm mandate.

**R8 — Day-index shift.** The wrap never empties the street on a continuing run: the finish crowd becomes the morning crowd, and the vignette pool switches to the "second heat" set. A player's second day never opens like their first.

**R9 — Once means once.** Every special in §8 has a fired-flag. If its trigger window passes unfired (e.g. the player dies, or a signal never crosses threshold), it is skipped, not deferred — a special that shows up late is worse than one that doesn't show up.

### Once-per-day specials (8)

| # | Special | Trigger window | Gate |
|---|---|---|---|
| S1 | **The Course Opening** — rope pulled taut, first green pennant | 8–16 s | `t` |
| S2 | **The Rival Launch** — crew lifts a macaw off the perch bar; it exits the band's top edge | 40–110 s | `t`, prefers a screen with a crew trestle |
| S3 | **The Vent Rush** — stall dragged back from a bursting geyser; kid chases a lifted hat | 72–100 s | `thermal_intensity ≥ 0.35` |
| S4 | **The Sweep** — three marshals abreast clear the near lane; density 0.55→0.14 in 6 s | clown-event flag −4 s | event flag |
| S5 | **The Downpour Scramble** — tea-stall awning unrolls, 8 figures pack under in 2 s | first frame `rain_intensity ≥ 0.35` | live signal |
| S6 | **The Tally Shed Lights** — braziers kindle left→right over 3 s | first frame `rain_intensity == 0` after S5 | live signal |
| S7 | **The Cold Shift Handover** — wing-cloth passed at a brazier; one leaves, one stays alone through the whiteout | 330–345 s | `t` + `storm_intensity > 0.3` |
| S8 | **The Chequer Raise** — finish arch + chequer on every post thereafter | `phase ≥ 0.95` | phase, then persistent to the wrap |

---

## 8. Narrative arc

**Shape: a double-peak working day with a storm trough, a night crest, and a dawn payoff — five movements, no two peaks adjacent.**

The day opens *below* its own energy (an empty apron, a slack rope) so the morning trade rush at 0:30 reads as a genuine crest rather than a starting state. That crest is spent by 1:02 and the street sags into a heat lull — and the geysers give the sag a small counter-peak at 1:36 that is about *fear*, not commerce, so it doesn't compete. Then the plan's boldest move: **eighteen seconds of a totally motionless street** through the clown gauntlet, the deepest void of the lit day, purchased deliberately so that the 2:22 flood-back can be the most kinetic crowd move on the clock. The sunset trade wave (2:42) is the second peak — smaller in headcount than the morning but far richer in light, and it is the ending most players will actually get, so it is dressed as one.

The storm is the trough: energy falls from 2:42 to a floor at 4:08 under lightning, and the plan spends that trough on *silhouette* rather than motion. The break at 4:25 — wet mirror paving, braziers coming up, one vendor re-opening in the last of the rain — is the visual high point of the cycle even though the crowd hasn't returned yet. From there the night tally climbs to the true crowd crest at 4:51, holds through the prize procession, and then strikes the shed. The snow whiteout at 5:43 is the emptiest and loneliest sixty seconds of the day, placed exactly where the player needs to breathe before the finale and nowhere else. Sunrise brings the town back walking *against* the scroll, the chequer goes up, the arch passes once, and the treasure lands into a street that has been waiting at the rope.

**Planted → paid off:** the slack rope (0:00) → pulled taut (0:13) → coiled and carried off (6:40). The first token on an empty rack (0:47) → racks overflowing (4:55) → racks stripped into baskets (5:25) → the whole token row lifted in salute (6:39). The rival macaw fed on its perch (0:57) → launched (1:45) → **an empty perch and a folded cloth** (5:55) → back on the perch, being fed (6:42). The vendor who covers his goods (3:05) → shelters under the tea awning (3:32) → is first man back in business in the last of the rain (4:29). The gong at 0:13 → the same gong, an octave up, at 6:42.

---

## 9. Logistics

### 9.1 Light & the glow contract
The existing contract holds unchanged: `NIGHT_GLOW_CAP = 150` per lit channel, `_lit_intensity` 0 by day → ~0.40 at dusk → 1.0 at night, string lights carry `_STRING_DAY_FLOOR = 0.40`. Additions:

- **The chequer pennant** is the only pure black-and-white object in the game. Its white is capped at 150 luma like every other lit surface, so at sunrise it reads by *contrast and shape*, never by brightness. The coin remains the brightest thing on screen at all times, including the finale frame.
- **Tally tokens are never gold and never round** (pale bamboo 200,190,150 by day; cool 120,130,150 at night). Wager pebbles are flat slate ovals in red/blue/white. Both rules exist purely so nothing on the sidewalk can be misread as a coin.
- **Braziers come up early in storm gloom** (~25 s ahead of the night schedule) and go down early at sunrise. This is the one place the light schedule is allowed to disagree with the sky, and it's the beat that makes 6f look expensive.
- Night works by **warm-vs-cool**: brazier amber against the NIGHT palette's cool stone (150,170,210 / 80,100,150) — never by cranking alpha.

### 9.2 Sound feel
The existing audio layer is procedural SFX plus `audio.play_thunder`; there is no ambient street bed and this plan does not require one. **Every beat above must read with the sound off.** Where I describe murmur, hiss and roar, treat it as the *feel* the visuals should imply — and if a bed is ever added, it should follow one curve: the crowd-density curve in §4.10, low-passed. Three optional cheap procedural cues, in priority order:

1. **Token clack** — a short wooden tick on the milestone flag-run (S-tier payoff for 6 lines of code).
2. **Cloth snap** — on the chequer raise and the finale pennant snap.
3. **Crowd swell** — a filtered-noise bump on the coin-rush barrier ripple.

All three must branch on `sys.platform == "emscripten"` and route through `window.skyPlay` on the web path — **never** `pygame.mixer`. Thunder already does this correctly; copy its shape.

### 9.3 Staffing cues (director-side signal contract)
The promenade director should key off **live signals**, never wall-clock, because of the clown-roll drift (Assumption 3):

| Signal | Consumed by |
|---|---|
| `phase` | chapter selection, role mix, density curve, light schedule |
| `t` (`biome_time`) | `_run_fill`, specials with `t` windows, seeded run offset |
| `thermal_intensity` | amber pennants, vent exclusion zones, S3 |
| `rain_intensity` | umbrellas, cover, white pennants, S5, S6, `crowd×` |
| `wetness` | ground sheen, reflections |
| `storm_intensity` | snow posture, pennant snap amplitude, `crowd×`, S7 |
| `snow_cover` | prop burial order |
| clown event flag | S4, the hush mandate |
| finale phase flags (`CYCLE_FINALE_PHASE_HI/LO`) | S8, apron, chest salute |
| pillar-passed / near-miss / rush / death events | §6 awareness layer only |
| `day` index | vignette pool, wrap density persistence |

### 9.4 Contingencies
- **Player dies mid-special.** All specials abort on death; fired-flags reset with the run.
- **Player survives past the wrap.** Density persists (R8); chapter machinery re-enters at Ch.2's curve, not Ch.1's. Day 2+ raises the vignette pool and may bias role mix toward *crew* (the town is more practised).
- **Clown roll runs long (25 pillars).** The hush stretches; Ch.4c simply holds its motionless-street state longer. Because 4c is *defined by stillness*, it is the one chapter that cannot get boring by lasting longer — it gets more oppressive, which is correct.
- **Weather signals overlap unexpectedly** (e.g. retuned anchors put rain inside the thermal window). Precedence order for `pennant`: **white (weather) > amber (hazard) > blue (flyer) > green**. Chequer overrides everything from phase 0.95.
- **Low-end device / high particle load** during the storm and snow peaks: the awareness layer (§6) is the first thing to shed — head-turns and barrier ripples drop out below a frame-time budget before any prop or figure does. Density and set pieces are the story; the reactions are the garnish.

---

## 10. Sources & inspiration

- **Marshal flag language** — the green/amber/white/blue/chequer system, and the idea that flag posts report on *the course* rather than on any one competitor, is taken directly from real motorsport marshalling convention. This is what makes the pennant layer readable to a player who has never seen the game before, and what keeps it from being a score display. ([Formula 1 — what marshals' flags mean](https://www.formula1.com/en/latest/article/watch-f1-explained-what-do-all-the-marshals-flags-mean.11m6Sp8b24f4gfFUnwprNJ), [Autosport flag guide](https://www.autosport.com/f1/news/what-do-the-different-colour-flags-mean-in-f1-everything-to-know-about-the-10-flags/10583727/))
- **Race-day street economy and the wordless odds trade** — the tic-tac hand-signal system, invented by Charles and Jack Adamson in 1888 so bookmakers could trade odds across a roaring betting ring without the punters reading them, is the direct model for the wager stones and the tout: a busy, gestural, deliberately opaque signalling economy running alongside the race. ([Tic-tac — Wikipedia](https://en.wikipedia.org/wiki/Tic-tac_(horse_racing)), [Tic-tac decoded](https://grandnational.horseracing.guide/26827/tic-tac-odds-racecourse/))
- **Bird-racing ground culture** — pigeon racing supplied the crew trestle, the perch bar, the hydration point and the weigh-in vignette: basketing is done deliberately calmly, with handlers concealing their excitement; and a returning bird is watered and fed immediately because it comes home depleted. It also supplied Chapter 8's empty perch — in racing culture, not every bird comes home. ([Humber Valley Racing Pigeon Club — inside pigeon racing](https://www.humbervalleyracingpigeonclub.ca/inside-pigeon-racing), [What is basketing?](https://pigeonweb.co.uk/pigeon-racing-explained/getting-started/what-is-basketing-in-pigeon-racing), [Basketing, race day and recovery protocol](https://www.auspigeonco.com.au/basketing-race-day-and-race-recovery-protocol.html))
- **Chinese temple-fair (*miaohui*) commerce** — the historical pattern of vendors setting up around a gathering and the fair growing into a three-part event of ritual, performance and trade is the structural model for the morning and evening trade crests, and for recasting the existing performer and food-stall families as *race-trade* rather than generic buskers. ([Miaohui — Wikipedia](https://en.wikipedia.org/wiki/Miaohui), [People's Daily — history of China's temple fairs](http://en.people.cn/n3/2017/0124/c90000-9171010.html))
- **Bamboo tallies (*qián chóu*)** — East China's notched split-stick and bamboo-token reckoning, and Marco Polo's account of illiterate traders in Yunnan recording transactions by notching each half of a split stick, is the grounding for the tally rack: a real, historically attested, entirely textless counting system. ([Bamboo tally — Wikipedia](https://en.wikipedia.org/wiki/Bamboo_tally), [Primaltrek — bamboo tallies](https://primaltrek.com/bamboo.html))
- **Background restraint** — the "one anchor per screen-width", "deliberate voids" and "reactions shed first" rules come from standard parallax-background guidance: parallax should enhance rather than distract, dense layers add processing load, and negative space prevents visual fatigue. ([Wayline — the parallax paradox](https://www.wayline.io/blog/parallax-scrolling-game-development-pitfalls), [GameMaker — creating depth & immersion](https://gamemaker.io/en/blog/creating-depth-and-immersion-parallax))
- **From the repo itself** (not invented): the remapped keyframe table, `DAY_HOLD_FRAC = 0.51`, `NIGHT_BORROW_SECONDS = 26.0`, `DAY_EXTRA_SECONDS = 73.5`, every event anchor in §2, the existing cast catalogue and `_POP_KEYS` curve, `_slot_latch` / `_run_fill` / `_weather_crowd_factor` / `_wants_umbrella`, the `NIGHT_GLOW_CAP = 150` contract, and `cheering_crowd.py`'s existing pompom / trumpet / drum / megaphone / flag / tambourine / party-horn drawables — which the finale reuses wholesale rather than building anything new.

**Two findings the team may want to act on independently of this plan:** (1) `calm_breeze` is `_bump(phase, 0.18, 0.10)` with unscaled literals, so with the extended cycle the "golden-hour" leaf drift now peaks at **t ≈ 70.8 s — mid-morning**; and (2) `weather.lightning_active()` gates `0.55 ≤ phase ≤ 0.72` but `Weather.update` uses `LIGHTNING_PHASE_MIN/MAX` instead, so the former appears to be dead code.