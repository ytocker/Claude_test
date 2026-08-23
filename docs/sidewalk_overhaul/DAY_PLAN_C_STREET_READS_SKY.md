# THE STREET THAT READS THE SKY
### Skybit sidewalk — one full day-cycle (393.5 s)

**One-line concept:** *The sidewalk is an all-day conversation between the town and the spirits of its weather — nature sends a sign, the street reads it, the street answers with an offering — and the tournament flight overhead is the omen everyone is waiting on.*

---

## 1. Concept

### Candidates considered (all inside "Nature, Omens & Spirits")

| # | Concept | Verdict |
|---|---|---|
| A | **The Town Reads the Sky.** Everyone on the street is an augur: animals bolt before the geysers, elders read the drifting leaves, swallows fly low before the rain. The street's job is *interpretation*. | Strong, but passive — reading alone gives no visible consequence. |
| B | **Feeding the Guardians.** A daylong roster of offerings to local spirits: earth-god at the shrine stones, the steam-spirit at the vents, the rain-dragon at dusk, the returning dead at night, the cold at predawn. Each spirit "answers" with the matching weather event. | Strong, but the causality runs the wrong way — the street would look like it *causes* the weather, which reads as magic rather than folklore. |
| **C** | **A ⟶ B fused: sign → reading → answer.** Nature moves first. The street *reads* it, then *answers* with an offering. Every chapter is one full turn of that triad, at rising stakes. | **Chosen.** |

### Why C wins

It gives the sidewalk a **job the player can feel**: the street becomes the game's diegetic weather forecast. The dogs sit facing downwind before the geysers open. The swallows skim low before the drizzle starts. The cloths go over the greenery before the first snowflake. A returning player learns to read the sidewalk the way the town reads the sky — which turns ambient decoration into *information*, without a single pixel of HUD.

It also solves three hard constraints for free:
- The **clown gauntlet must be calm.** On-concept: *the town does not watch what it did not invite.* Backs turned, no reactions. The silence is characterisation, not a hole.
- The **newbie ramp must be quiet.** On-concept: the morning offering round is presence without agitation — a street full of people who are all standing still.
- The **coin must stay brightest.** On-concept: every light on the street is an offering light, and offerings are small.

And it earns an **accumulation mechanic**: rope-markers tied, offering trays lit, stones stacked. The street visibly *accrues* across a run, so a 300 s run never reads as a loop of a 60 s run — then the finale spends the whole tally in one beat.

**The triad, stated once so every beat can be tested against it:**
> **SIGN** (nature moves) → **READING** (the street stops and interprets) → **ANSWER** (an offering is made, and something is left behind on the paving).
> If a beat is none of the three, cut it.

---

## 2. At a glance

| | |
|---|---|
| **Duration** | `CYCLE_SECONDS = 393.5 s` (`_BASE_CYCLE_SECONDS 320 + DAY_EXTRA_SECONDS 73.5`) |
| **Band** | y 560–640, ground line y 595. Far promenade lane + near lane (~18 px figures). Scroll 160 px/s base. |
| **Audience** | Mobile casual players. Median run **~156 s ≈ phase 0.396** — Chapters I–VI are seen by nearly everyone; VII–X are a reward. |
| **Cast palette** | Existing families only: 50 pedestrians, 6 kids, 6 elders, 7 vendors, 9 animals, 30 greenery, 5 food stalls, 15 props / 5 pools, 8 performer acts, 5 festival specials, lamp posts, garland, fairy strings, bunting, kiosk. |
| **New art** | **7 items, 3 of them overlays** (§9). Everything else is a re-direction of an existing family. |
| **Hard limits honoured** | Nothing drawn above y=560 (rising elements clamp at y=562). Coin stays brightest: lamps ≤150 luma (existing `NIGHT_GLOW_CAP`), new tray-lights ≤110, float lanterns ≤130, no additive halo wider than 3 px. Calm street for t 0–19 s and for the whole clown gauntlet. |

### Real anchors extracted from the repo

`biome.py` remap: `_DAY_EXTRA = 73.5`, `NIGHT_BORROW_SECONDS = 26.0`, `DAY_HOLD_FRAC = 0.51`.

| Anchor | Phase | t (s) | Source |
|---|---|---|---|
| DAY keyframe | 0.000 | 0.0 | `_KEYFRAMES[0]` |
| Calm-breeze leaves open | 0.080 | 31.5 | `calm_breeze` bump c=0.18 w=0.10 (unshifted) |
| Morning thermal begins (sinter rocks) | 0.127 | 50.0 | `THERMAL_START_PHASE = 50/CYCLE` |
| **DAY-hold releases → golden fade begins** | 0.157 | 62.0 | inserted hold keyframe = `_golden_phase × 0.51` |
| Geysers cross `GEYSER_SPAWN_THRESHOLD` | ~0.175 | ~68.7 | `_skew_bump` ≥ 0.35 |
| Calm-breeze peak | 0.180 | 70.8 | |
| **Thermal PEAK** | 0.244 | 96.0 | `THERMAL_PEAK_PHASE` |
| Genie lamp (pillar 50) | ~0.261 | ~102.6 | `GENIE_PILLAR = pillar_for_phase(peak) + 3` |
| Geysers stop / rocks-only tail | ~0.268 | ~105.5 | |
| Thermal ends; leaves end | 0.285 / 0.280 | 112 / 110 | |
| **GOLDEN HOUR keyframe** | 0.309 | 121.5 | remapped from 0.23125 |
| **Clown pre-clear fires** | 0.319 | 125.3 | `CLOWN_PRECLEAR_PHASE = _phase_for_pillar(63)` |
| Clown entrance / gauntlet | 0.327→~0.38 | ~128.8→~150 | `CLOWN_START_PILLAR 65`, warren spacing 72 px |
| **SUNSET keyframe** | 0.415 | 163.5 | remapped from 0.36250 |
| *(median run ends)* | *0.396* | *156* | brief |
| **Drizzle begins** (`RAIN_START_PILLAR 100`) | 0.483 | 190.1 | `RAIN_DRIZZLE_START` |
| Umbrellas appear in crowd (rain ≥0.12) | ~0.516 | ~203 | `WEATHER_UMBRELLA_RAIN_AT` |
| Paving starts wetting (rain ≥0.18) | ~0.525 | ~206 | `WEATHER_WET_ON_RI` |
| Umbrella power-up #1 (pillar 112) | ~0.536 | ~211 | `UMBRELLA_SPAWN_PILLARS` |
| **DUSK keyframe** | 0.537 | 211.5 | remapped from 0.51250 |
| Drizzle peak / storm onset | 0.564 | 222.1 | `RAIN_DRIZZLE_PEAK` |
| Umbrella power-up #2 (pillar 124) | ~0.590 | ~232 | |
| Lightning window opens | 0.621 | 244.5 | `LIGHTNING_PHASE_MIN` |
| **THUNDERSTORM PEAK** | 0.629 | 247.7 | `RAIN_STORM_PEAK` |
| **NIGHT keyframe** | 0.644 | 253.5 | remapped from 0.64375 |
| Rain ends; lightning closes | 0.695 | 273.3 | `RAIN_STORM_PEAK + WIDTH` |
| Paving dry again | ~0.708 | ~279 | `WEATHER_WET_DRY_RATE 0.18/s` |
| **Snow squall first flakes** | 0.766 | 301.2 | `SNOW_STORM_CENTER − WIDTH` |
| Snow anchor pillar 169 | 0.790 | 310.8 | `SNOW_START_PILLAR` |
| Snow crosses `WEATHER_SNOW_ON_WI` (cover builds, tailwind hard) | 0.813 | 320.1 | |
| **PREDAWN keyframe** | 0.832 | 327.5 | remapped from 0.79375 |
| **SNOW PEAK / max tailwind** | 0.871 | 342.8 | |
| Snow-cover defrost begins | 0.911 | 358.4 | `WEATHER_SNOW_MELT_AT 0.04` |
| **SUNRISE keyframe** | 0.924 | 363.5 | remapped from 0.90625 |
| Snow squall ends | 0.977 | 384.4 | |
| **CYCLE WRAP → treasure-chest finale** | 1.000→0.000 | 393.5 | `CYCLE_FINALE_PHASE_HI/LO` |
| Finale: 3 phantom pillars + long rush + chest | 0.000–0.015 | 393.5–~399 | `CYCLE_FINALE_RUSH_PILLARS 3`, `TREASURE_BOX_ANIM_T 1.5` |

### Assumptions stated

1. Beats are driven by **elapsed seconds / biome phase**, not pillar count — matching how `weather.py` and `world.py` actually gate. Pillar numbers quoted are the game's own `_phase_for_pillar` estimates and may drift during the compressed clown warren; the sidewalk never reads pillar count directly.
2. The clown gauntlet's rolled length is 10–25 pillars at 72 px spacing, so its wall-clock duration varies ~5–12 s. Chapter V is authored to fill the **whole reserved slot** (t 125.3–152) regardless of the roll, by holding its still-state until the world reports the gauntlet clear.
3. "Calm street" for the newbie ramp is defined as **low charge, not low population**: figures may be present, but no near-lane relative motion, no set pieces, no flashes, no reactions.
4. `_run_fill` (7 s ramp-in from empty) is kept and made diegetic.
5. New SFX go through `audio.py`'s dual backend (`window.skyPlay` on the web path); nothing calls `pygame.mixer` on emscripten.

---

## 3. The two curves (the pacing engine)

The existing street has one density curve. This plan splits it into **two**, because the whole arc depends on never letting them peak together.

- **POP** — how many actors. *Pre-weather* value; the weather crowd factor multiplies on top.
- **CHARGE** — how agitated they are: relative motion, posture break, head-turns, clustering, sound density.

```
 phase   t(s)  POP   CHARGE   chapter
 0.000    0.0  .30    .10     I   first light
 0.048   19.0  .45    .12     I   offering round  (calm mandate)
 0.080   31.5  .55    .30     II  leaf-reading
 0.127   50.0  .60    .45     III steam sign
 0.180   70.8  .48    .70     III THE BOLT — pop falls as charge rises
 0.244   96.0  .35    .85     III ███ CHARGE PEAK 1 (vents answer)
 0.290  114.0  .55    .35     IV  gratitude round
 0.319  125.3  .30    .10     V   ███ VALLEY (clown — mandated)
 0.386  152.0  .50    .25     VI  street returns
 0.440  173.0  .75    .40     VI  evening offering market
 0.483  190.1  .60    .55     VI/VII first drops
 0.537  211.5  .40    .80     VII willow dragon
 0.629  247.7  .18    .95     VII ███ CHARGE PEAK 2 (the strike)
 0.660  260.0  .35    .30     VIII the quiet after
 0.700  275.0  .85    .55     VIII lantern setting
 0.740  291.0  1.00   .65     VIII ███ POP PEAK (remembrance crest)
 0.766  301.2  .55    .40     IX  first flakes
 0.832  327.5  .16    .25     IX  cloth-draped street
 0.871  342.8  .06    .10     IX  ███ VALLEY (the true empty)
 0.924  363.5  .20    .20     X   the unwrapping
 0.970  382.0  .45    .35     X   the counted stones
 1.000  393.5  .60    .90     ✦   FINALE
```

Rule enforced by this table: **no two adjacent rows both exceed .70.** The two big peaks (t 96 charge, t 291 pop) are 195 s apart with a mandated valley between them.

---

## 4. Master timeline — 100 % of 393.5 s

Chapters I–IV carry the highest beat density and the most seeded variation, because early day is what everyone sees.

---

### CHAPTER I — FIRST LIGHT: THE QUIET READING
**t 0 – 31.5 s · phase 0.000 – 0.080 · POP .30→.45 · CHARGE .10→.30**
*So the player feels:* **"I've flown into somewhere that was already praying before I got here."**

| t (s) | phase | Beat |
|---|---|---|
| 0 – 7 | .000–.018 | **The street opens.** `_run_fill` ramps the cast in from empty over 7 s — now diegetic. One of **three seeded opening variants** (§8, Rule 3): **(A) Sweeping** — two elders and a vendor drag slow arcs across the paving right-to-left, each stroke kicking a 3-mote dust puff. **(B) Watering** — a vendor tips a can along the far lane, trailing a dark wet strip on the kerb that dries over ~12 s (reuses the `wetness` sheen on a local strip only). **(C) Cloth-lifting** — white drapes come *off* the stalls and greenery, a direct callback to last night's Chapter IX. Far-lane motion only; the near lane is empty. |
| 7 – 19 | .018–.048 | **The First Offering.** The **shrine stones** (NEW-1 — three stacked river stones, roadside, ~14×16 px) scroll past for the first time, bare. Behind them, 3–5 figures in a loose line, each pausing exactly 1.2 s. **Offering trays** (NEW-3) are set on the kerb one at a time; the first **incense thread** (NEW-2) lights. Every walker moves at exactly scroll speed — zero relative motion except the pauses. Presence without agitation: the calm mandate satisfied by ritual stillness rather than by an empty street. **Signature:** the incense thread — a 1 px wavering warm-grey ribbon rising to y=562 and dissolving. It is the first thing in the entire game that moves *upward*. **Sky/gameplay:** solid DAY hold; newbie ramp still running (wide gaps, 125 px/s scroll). **Light & sound:** flat daylight, strings at their 0.40 day floor, lamps dark. Two wood-block knocks (t≈9, t≈17) and otherwise silence. |
| 19 – 31.5 | .048–.080 | **The Street Wakes.** Newbie ramp is winding down; the near lane opens. First kid skips in, first dog trots, two vendors raise stall frames. First **magpie** perched on a lamp arm — the good-omen bird, present only in bright chapters (§7). **Signature:** a kid runs a lap around a greenery cluster and stops dead the instant the dog does — the day's first "an animal noticed something," played as harmless comedy so the same shape reads as dread at t=62. |

---

### CHAPTER II — THE LEAF-READING
**t 31.5 – 50 s · phase 0.080 – 0.127 · POP .55 · CHARGE .30→.45**
*So the player feels:* **"someone down there knows something I don't."**

| t (s) | phase | Beat |
|---|---|---|
| 31.5 – 40 | .080–.102 | **First Leaves.** `calm_breeze` opens at *exactly* phase 0.080 — the sidewalk beat is scheduled on the same frame. Autumn leaves begin drifting (existing `_Leaf`). On the street: two elders halt mid-lane, palms up. A third ties the day's **first rope-and-paper marker** (NEW-4) around a greenery cluster — the first *declaration*: this one is inhabited. **Signature:** three figures halt on the same frame, all facing right/downwind, as a leaf crosses them. **Sound:** one dry rope-creak tick per marker tied, forever after. |
| 40 – 50 | .102–.127 | **The Count.** The stone-stacker (elder pool) starts the day's **cairn** on the kerb: one stone, then two. Pedestrians reach POP .55 and, for the first time, walk at *differential* speeds — some faster than scroll, some slower — so the band gains internal parallax right as the difficulty ramp finishes tightening. **Signature:** two dogs sitting side by side, both facing **right**, not at Pip. Nobody has reacted to Pip yet. **Sky:** still solid DAY; the hold releases in 12 s. |

---

### CHAPTER III — THE STEAM SIGN
**t 50 – 96 s · phase 0.127 – 0.244 · POP .60→.35 · CHARGE .45→.85 (CHARGE PEAK 1)**
*So the player feels:* **"the ground is alive, and these people are negotiating with it."**

| t (s) | phase | Beat |
|---|---|---|
| 50 – 62 | .127–.157 | **Sinter on the Paving.** `thermal_intensity` opens at t=50 and the sky layer starts scattering sinter rocks. The street answers on the same frame: the same pale sinter appears as chalky lumps along the kerb (planter/cairn prop pool, retinted to the rock palette). Two vendors drag their stalls one body-width back from the kerb. **Signature:** a vendor kicks a lump and it steams — a 4-mote puff. |
| 62 – 72 | .157–.183 | **✦ SPECIAL S1 — THE BOLT.** Every animal on screen bolts rightward at 1.6× scroll and clears the frame inside 3 s. Every human **freezes for 2 s** — motion halts while the ground keeps scrolling under them at 160 px/s, which is a violently strong effect in this band. Then the whole street turns to face the ground. **The coincidence that sells it:** the DAY hold releases at t≈62, so the sky's colour *itself* begins changing on the same beat the dogs run. **Sound:** one low sub-thump and a rising hiss under the mix. **This is the chapter's "look at that."** |
| 72 – 84 | .183–.210 | **Feeding the Vents.** Geysers now firing in the play field. The street's ANSWER: figures kneel along the kerb and slide offering trays toward the paving cracks; three more incense threads light; the shrine gets its first fruit pile; the rope-marker count reaches 3–4. POP drops to .48 while CHARGE climbs to .70 — **a smaller, more intense crowd.** This is the pop/charge split doing its job. |
| 84 – 96 | .210–.244 | **The Steam Answers.** Geysers at full duty cycle (up to `GEYSER_MAX_CONCURRENT 3`). The 8 performer acts are re-cut here as **vent-tenders**: the same animations, but facing *away* from the street, toward the vents. One flag flip, and the whole family re-reads. **Signature:** at t 93–96 (thermal peak) every incense thread on screen bends hard right in unison for ~1 s — the street exhaling. |

---

### CHAPTER IV — THE GRATITUDE ROUND
**t 96 – 125.3 s · phase 0.244 – 0.318 · POP .35→.55 · CHARGE .85→.35**
*So the player feels:* **"we got away with something, and everyone is grateful."**

| t (s) | phase | Beat |
|---|---|---|
| 96 – 108 | .244–.275 | **✦ SPECIAL S2 — THE CAGE RELEASE.** A vendor sets a covered cage down in the near lane; the cover lifts; three bird dots rise on arcs and exit the top of the band at y=562. Grounded in **fangsheng**, the Buddhist merit-release of captive birds and fish. CHARGE falls .85→.35 in four seconds — the release *is* the release. **Genie tie-in:** the lamp lands at t≈102.6; if it's picked up in this window, a far-lane elder kneels and the cairn gains a stone. |
| 108 – 118 | .275–.300 | **The Wide Breath.** Thermal over, geysers gone, rocks thinning out (t 105.5→112). POP back to .55, CHARGE .35. Stalls return to the kerb. The **kids** pool runs at maximum representation — the only chapter of the day where kids outnumber adults in the near lane. Leaves stop at t≈110. **Signature:** a kid tries to place a stone on the cairn, can't reach, and an elder lifts them. |
| 118 – 125.3 | .300–.318 | **Golden.** GOLDEN HOUR lands at 121.5. Lamp posts are up (existing 0.20 gate) but unlit shells. Cast shadows on the paving skew long to the right (a 1 px per-figure shear — cheap, and the strongest single read of "afternoon"). **Sound:** the busiest ambient bed of the whole day, layered stall clatter — deliberately, because the next chapter kills it stone dead. |

---

### CHAPTER V — THE STILL HOUR *(mandated calm)*
**t 125.3 – 152 s · phase 0.318 – 0.386 · POP .30 · CHARGE .10 (VALLEY)**
*So the player feels:* **"the town has looked away, and I'm alone with this."**

| t (s) | phase | Beat |
|---|---|---|
| 125.3 – 131 | .318–.333 | **Backs Turned.** The frame `CLOWN_PRECLEAR_PHASE` fires, the tournament-awareness layer switches **off entirely** and every near-lane figure turns to face away from the play field. POP collapses .55→.30 over five seconds by walk-off (stable inclusion gates — figures leave once, they never pop out). The ambient bed ducks 8 dB. |
| 131 – 150 | .333–.381 | **The Gauntlet Passage.** The plan's designed dead space, and it is fully on-concept: *the town does not watch what it did not invite.* What remains on screen: the recurring shrine stones, greenery, static fixtures, exactly two far-lane figures kneeling with their backs to the street. **No** animals, **no** performers, **no** kids, **no** reactions, **zero** near-lane relative motion, and **nothing new enters from the right edge** for the entire gauntlet. **Signature (single, low-key):** the incense threads keep rising, perfectly straight. The only motion in the band. **Readability:** this is a hard gameplay-safety requirement; the concept *earns* it instead of fighting it. Hold this state until the world reports the gauntlet clear, so it fits any rolled length from 10 to 25 pillars. |
| 150 – 152 | .381–.386 | **Peeking.** Two figures turn back around. One kid re-enters at the right edge. |

---

### CHAPTER VI — THE CROW SIGN
**t 152 – 190.1 s · phase 0.386 – 0.483 · POP .30→.75→.60 · CHARGE .25→.55**
*So the player feels:* **"the sky is about to do something, and they told me before it did."**

> **Retention note:** median death is t≈156, two seconds inside this chapter. The density ramp below is tuned so the crowd is *visibly* flooding back by t=154 — the median player's last image is the street bursting back to life after 20 s of silence, and the sunset flare at 163.5 is the visible "just a little further" hook.

| t (s) | phase | Beat |
|---|---|---|
| 152 – 163.5 | .386–.415 | **The Street Comes Back Loud.** POP ramps .30→.75 in eleven seconds — the sharpest density ramp of the day. Vendors, performers (facing the street again), two dogs, three kids. The **evening offering market**: the trays are now being *sold*, not just set, so the food stalls swap their food silhouettes for tray silhouettes. **Signature:** SUNSET lands at 163.5 and **every rope-and-paper marker tied since t=31 catches the low amber light at once** — a line of small bright flutters running the whole street. A payoff for something the player has watched being assembled for two minutes. |
| 163.5 – 175 | .415–.445 | **The Crow Arrives.** A crow silhouette lands on a lamp arm — larger, darker, heavier than the magpies. **From this beat the magpies are gone until sunrise.** In East Asian bird lore the magpie announces good news and the crow announces warning; the swap is a pure palette-and-scale change, no new animation. CHARGE .40. **Signature:** two figures stop and point at the lamp arm; the whole cluster's heads tilt up. |
| 175 – 190 | .445–.483 | **Low Swallows.** NEW-7 in full: 3–5 dot flocks skimming the promenade lane at head height on shallow arcs. Grounded — swallows genuinely fly low ahead of rain, because falling pressure and rising humidity push their insect prey down. The street reads it: awnings out, cloth covers over the tray displays, one vendor starts folding. **Signature:** a dog lies flat on the paving and refuses to move as its owner tugs — the "cows lie down before rain" omen, recast onto the dog pool. **Sound:** ambient bed goes dry and close; the wind noise floor lifts. |

---

### CHAPTER VII — CALLING THE RAIN-DRAGON
**t 190.1 – 253.5 s · phase 0.483 – 0.644 · POP .60→.18 · CHARGE .55→.95 (CHARGE PEAK 2)**
*So the player feels:* **"they asked for this, and it came, and now they're frightened of what they asked for."**

| t (s) | phase | Beat |
|---|---|---|
| 190.1 – 205 | .483–.521 | **First Drops.** Rain 0→~0.15. `_weather_crowd_factor` begins thinning; pre-weather POP is authored high (.60) so the post-factor result lands ~.45. Umbrellas from rain 0.12 (t≈203) — **and here they characterise:** figures preferentially hold the umbrella over a *tray* or over the *shrine*, not over themselves. **Signature:** the first `_Splash` particles land on the offering trays and snuff two warm dots; a figure re-lights them, shielding the flame with their body. |
| 205 – 222 | .521–.564 | **✦ SPECIAL S3 — THE WILLOW DRAGON.** DUSK lands at 211.5 and the lamps kindle to `_lit_intensity ≈ 0.40`. The existing **jade dragon-dance** special is recast as the **willow-water dragon**: five green segments carried down the near lane, followed by two figures splashing water from buckets with willow withes. Grounded in the real Water Dragon rain-praying ritual, where the dragon's scales are green willow branches and attendants splash the crowd with willow withes crying "here comes the rain." The splashes reuse the existing rain `_Splash` particle at raised intensity — near-zero new art. **Gameplay hook:** the umbrella power-up spawns at t≈211; the frame it passes overhead, three near-lane umbrellas tip up toward the sky in unison. **Sound:** slow procession drum + water slap at quarter time — a texture only, gone by 222. |
| 222 – 240 | .564–.610 | **The Answer Comes Too Well.** The storm ramps to full. This is the concept's dark joke: *they called for rain and got a thunderstorm.* Pre-weather POP .40 → post-factor ~.20. What remains is the **shelter cast** (exempt from weather thinning): 4–6 figures under kiosk awnings and lamp posts, stall-keepers physically holding their frames down, and **one figure who does not leave the shrine.** `wetness` reaches 1.0 — the paving glazes, the lamps double into smear-reflections, band contrast roughly doubles. **Signature:** the dragon is **abandoned mid-street** — its five segments set down on the wet paving and left. It stays there, scrolling past, for the rest of the storm. |
| 240 – 253.5 | .610–.644 | **THE STRIKE.** Lightning opens at 244.5; the storm peaks at 247.7; NIGHT lands at 253.5. Each 0.18 s flash renders the whole band as flat silhouette for free — so **every actor design in this band must read at flat black**, a testable constraint on the whole cast. **✦ SPECIAL S4 — THE ASH WIND:** within 6 s of a flash, every offering tray's warm dot goes out at once and pale ash motes lift off the kerb and drift right. **Nobody re-lights them this time.** The reading: *the offerings were accepted.* **Gameplay hook:** if the storm-jolt strikes Pip, every visible umbrella dips in unison for 0.3 s. |

---

### CHAPTER VIII — LANTERNS ON THE WET STREET
**t 253.5 – 301.2 s · phase 0.644 – 0.766 · POP .18→1.00 (POP PEAK) · CHARGE .30→.65**
*So the player feels:* **"this is why they endure the weather. This is the night the whole day was for."**

| t (s) | phase | Beat |
|---|---|---|
| 253.5 – 268 | .644–.681 | **The Quiet After.** Rain falling off from peak. POP .18→.45, CHARGE down to .30. People come out and **stand in the wet street doing nothing.** Full night lighting: lamps 1.0, strings full, all capped at 150 luma; the still-wet paving doubles every light into a reflection smear. This is the most beautiful frame of the day and it is deliberately placed inside a *low-charge* beat, so it can be looked at. **Signature:** the abandoned willow dragon is picked back up — by children this time, dragging it, clearly too heavy for them. |
| 268 – 288 | .681–.732 | **✦ SPECIAL S5 — THE LANTERN SETTING.** Rain ends at 273.3 but `wetness` stays ~1.0 for another five seconds. In that overlap window: 7–11 **float lanterns** (NEW-5) are set down along the gutter line at y≈600 and drift right at **0.55× scroll** — the only objects in the game that move against the parallax convention, so they read as not-quite-of-this-world. Warm amber, ≤130 luma. Grounded in the Zhongyuan / Ullambana river lanterns floated at dusk to guide returning spirits home. **The reframe:** POP hits .85 and the existing night-festival specials layer in exactly as they always did — braziers, campfire, kiosk, busier crowd — but the *tempo* is halved. This is not a party, it's a **remembrance**. Density peak, CHARGE only .55. Pure behaviour change; zero new art. |
| 288 – 301.2 | .732–.766 | **The Crest.** POP 1.00 at t≈291. Lion dance and red dragon come out — now legible as the *thanks* for having survived the storm, bookending the willow dragon that called it. CHARGE .65. **Signature:** at the crest, every float lantern, every string light and every brazier lights on the same frame while the entire crowd stands still for 1.5 s. The only motion on the sidewalk is the lanterns drifting the wrong way. |

---

### CHAPTER IX — THE WHITE BREATH
**t 301.2 – 363.5 s · phase 0.766 – 0.924 · POP .55→.06 (VALLEY) · CHARGE .40→.10**
*So the player feels:* **"the town gave the street back to the cold on purpose, and left the lights on for whoever's still out."**

| t (s) | phase | Beat |
|---|---|---|
| 301.2 – 312 | .766–.793 | **First Flakes / Pack Up.** The first `_WindDrift` flakes appear. The street reads it *instantly* — POP .55 and falling, CHARGE .40. Stalls fold, braziers get lids, the float lanterns are nudged further into the gutter to keep them going. |
| 312 – 327.5 | .793–.832 | **✦ SPECIAL S6 — THE CLOTH-DRAPING.** As the tailwind builds toward `WEATHER_SNOW_ON_WI` (320.1), figures throw **white cloths** (NEW-6, an overlay fitted to any existing bounding box) over the shrine stones, the greenery clusters and the stall frames, then walk off right. By PREDAWN (327.5) the street is a field of pale draped shapes, near-empty of people. **Signature:** the last figure ties a rope-marker around the tallest draped shape — the day's final declaration. This beat is what makes Chapter I's "Cloth-lifting" opening variant land for anyone who survives into a second day. |
| 327.5 – 350 | .832–.889 | **The Empty Street.** Snow peaks at 342.8 with maximum tailwind. POP bottoms at **.06** — the true empty of the day, and the *only* place in this plan where the band is allowed to be nearly bare. Gameplay is at its hardest here (tailwind push, `SNOW_TINT` whiteout wash, snow burying Pip) so an empty band is also a readability gift. **Signature:** at the peak, the wind takes **one white cloth off a shape** and carries it right across the entire screen, tumbling, at 1.4× scroll — the single largest moving object the sidewalk ever produces, and the only one that crosses the whole width. **Sound:** the ambient bed drops to one filtered wind layer. **No human sound at all for ~20 s.** This is the plan's deepest valley and it sits immediately before the restoration — never beside a peak. |
| 350 – 363.5 | .889–.924 | **Snow Cover.** `snow_cover` accumulates on the band: the kerb, the draped shapes and the cairn take white caps. Defrost begins at 358.4. The float lanterns are still going — now the only warm objects in an entirely cool field. The coin and the lanterns are the whole colour story of this beat, which is exactly how the night palette is supposed to work. |

---

### CHAPTER X — THE SIGN RETURNED
**t 363.5 – 393.5 s · phase 0.924 – 1.000 · POP .20→.60 · CHARGE .20→.90**
*So the player feels:* **"the day is being counted, and I'm part of the count."**

| t (s) | phase | Beat |
|---|---|---|
| 363.5 – 376 | .924–.955 | **✦ SPECIAL S7 — THE UNWRAPPING.** SUNRISE lands at 363.5. One elder walks the street **leftward, against the scroll** — the only actor in the entire day who does — lifting each white cloth in turn. Every lift restores the daytime colour of what's underneath (the greenery already holds its day colour all cycle by existing convention, which is precisely what this beat needs). POP .20 and rising. **Signature:** the elder reaches the shrine last; the cloth comes off and the stones stand at exactly the height *this run* built them to. |
| 376 – 388 | .955–.985 | **✦ SPECIAL S8 — THE COUNTED STONES.** Snow ends at 384.4. Vendors return; the **magpies come back** to the lamp arms for the first time since t=163. POP .45. A figure places the final stone on the cairn and kneels. For the first time in the run, the whole tally — every rope-marker tied, every tray lit, every stone stacked — is visible in one screen. **Signature:** as the last stone lands, every incense thread on screen lights at once. |
| 388 – 393.5 | .985–1.000 | **The Held Breath.** POP holds .45, motion slows, and every figure on screen turns to face **right** — downstream, toward the coming day. CHARGE climbs to .90 **with no change in density at all**: the tension is entirely in posture and in the ambient bed's rising tone. Nothing else happens for five seconds. This is the run-up. |

---

### ✦ FINALE — THE CHEST
**t 393.5 → ~399 s · phase wraps 1.000 → 0.000**
*So the player feels:* **"the whole town was waiting on my flight, and it just paid out."**

The wrap fires `_activate_treasure_box`: three phantom pillars, one continuous coin rush across the full span, the chest on the middle pillar, `TREASURE_BOX_GRANT` +100, then `TREASURE_BOX_ANIM_T` 1.5 s of lid-pop and halo bloom. The street participates on exactly those beats:

1. **On the wrap frame.** Every warm light in the band — trays, braziers, strings, float lanterns — snaps to full for two frames, then holds. Simultaneously the **lamp posts go out** (their existing gate closes at phase 0.93) — use the gate as a *beat*: the street switches from lamp-light to daylight in a single visible step. Sunrise answered.
2. **Across the coin rush (~5 s).** The entire cast turns to face up-and-right and tracks the rush. **This is the only moment in the whole day when the whole street looks at the player at once.** Every other reaction all day has involved 2–5 figures. That restraint is what makes this land.
3. **On chest pickup.** The existing banner / bunting / balloon celebration fires above the band. Below it, **the cairn is knocked over** — deliberately — and the stones scatter along the kerb. The day's tally is *spent*. It resets to zero for day 2, which is what makes the accumulation mechanic survive multiple cycles: `DAY_SCROLL_STEP` already makes day 2 legibly harder, and now it's legibly a *fresh street* too.
4. **On the 1.5 s animation tail.** The near lane empties in one sweep and the `_run_fill` opening begins again from empty — with a **new seeded opening variant, guaranteed different** from day 1's.
5. **If the player dies during the finale.** Freeze the band on the death frame, hold the lights at full, and leave the scattered stones scattered. The last thing on the game-over screen is a town caught mid-celebration.

---

## 5. Narrative arc

**Shape: two summonings and a reckoning — peak, mandated valley, bigger peak, long warm afterglow, deep cold empty, tender restoration, burst.**

The town asks the *earth* in the morning and the earth answers with fire and steam (first crest, t≈96). The gauntlet then forces a twenty-second silence, which the concept converts from a hole into the loneliest beat in the game — the only stretch where nobody is watching. The second act builds much longer and much wider: swallows, crow, evening market, a willow dragon calling for rain, and the sky over-delivering into a thunderstorm (second and largest crest, t≈248). The storm does not resolve into another peak — it resolves into forty-five seconds of warm, dense, *slow* remembrance on wet paving lit by drifting lanterns, which is the emotional home of the whole day and the place a long-run player will remember. Only then does the plan spend its deepest valley: sixty seconds of white, empty, near-silent street at the snow peak, placed as far from every crest as the day allows. The restoration that follows is small and human — one person walking the wrong way, lifting cloths — and it earns the finale, where the accumulated evidence of the entire run is displayed for twelve seconds and then spent in one burst.

Everything late is planted early: the incense thread lit at t=9 is the thing that bends at t=95, goes out at t=248, and relights at t=386. The rope-markers tied from t=31 are what catch the sunset at t=163 and get draped in white at t=320. The cairn started at t=42 is what the elder unwraps at t=375 and what gets knocked over at the chest. And the crow that lands at t=164 leaves precisely when the magpies come back at t=380.

---

## 6. Weather overlay matrix

**Governing rule: weather modulates a chapter, never replaces it.** The chapter's cast list, its offering state and its accumulated props are unchanged. Weather may change only four things: **density**, **posture**, **shelter**, and the *staging* of that chapter's one signature moment.

**Three global rules:**
- **Pre-weather authoring.** All POP values in §3 are *pre-multiplier*. `WEATHER_CROWD_RAIN_MIN 0.22` and `WEATHER_CROWD_SNOW_MIN 0.06` are severe, so rain/snow chapters are authored high to compensate. The **shelter cast** (awning figures, stall-holders, the shrine-keeper) is **exempt from thinning**, so the floor is never zero people.
- **Ground states bleed across chapter borders.** `wetness` and `snow_cover` lag their weather by seconds, so *every* chapter needs a wet and a snowed variant of its ground dressing even where that weather cannot currently occur — wetness carries VII→VIII, snow_cover carries IX→X→finale.
- **Umbrellas are shelters for offerings, not for people.** One behaviour flag, applied everywhere rain appears.

| Chapter | **Clear** (default) | **Calm breeze / leaves** (0.08–0.28) | **Thermal: rocks → geysers** (0.127–0.285) | **Rain → storm + wet paving** (0.483–0.708) | **Snow squall + tailwind + cover** (0.766–0.977) |
|---|---|---|---|---|---|
| **I** First Light | Base. Seeded opening variant. | *n/a in window* — if moved here, the sweeping variant becomes leaf-sweeping and the dust puffs become leaf puffs. | *n/a* — sinter would arrive as kerb lumps; the sweepers sweep them into a pile instead. | *n/a* — variant **B (Watering)** is suppressed (nature already did it); openers carry the trays under awnings; POP floor .22. | *n/a* — variant **C (Cloth-lifting)** becomes mandatory and doubles in length; cloths come off snow-capped shapes. |
| **II** Leaf-Reading | Elders read still air by dust instead of leaves; markers tied to lamp posts, not plants. | **Native.** Leaves are the sign; the reading is literal. Marker count +1. | Overlap 0.127–0.28: leaves and sinter drift together; elders read the *rocks* first, then the leaves — two signs stacking is the day's first escalation. | Markers go limp and dark-wet; elders shelter the rope while tying it. POP .60→.38 post-factor. | Cloths would already be up: the leaf-reading becomes a **cloth-reading**, elders watching which draped shape the wind lifts first. |
| **III** Steam Sign | Sign reads by dust plume only; the Bolt still fires. | Native overlap — the Bolt's animals run *with* the leaves, doubling the perceived wind. | **Native.** The whole chapter exists to answer this. | Rain would snuff the vent offerings as fast as they're lit; the kneeling round becomes a huddle and the trays are held, never set down. | Steam and snow together: the geyser plumes read as white-on-white; drop the street to silhouette-only and let the vent-tenders be the only dark shapes. |
| **IV** Gratitude | Base. Cage release, kids peak. | Native tail (leaves end t≈110) — the released birds fly *through* the last leaves. | Native tail — the rocks-only fade is the "all clear" the release answers. | Release is still performed but **under an awning**, and the birds exit at a steeper angle; kids halve; stalls stay back from the kerb. | Cage stays covered; the release is **deferred**, and if the run reaches sunrise the birds are released in Chapter X instead — a real, visible consequence. |
| **V** Still Hour | Base still-state. | Leaves keep drifting past the motionless figures — the only motion besides the incense. Beautiful, and free. | Rocks land among the kneeling figures and nobody moves. Strongest possible read of the still-state. | **The still-state overrides the weather.** No umbrellas go up, nobody shelters, the two kneelers get rained on. Nothing enters the frame. | Same override: snow settles on unmoving shoulders. Both readings say *these people are not going to react to anything right now.* |
| **VI** Crow Sign | Base. Crow, low swallows, the flat dog. | *out of window* | *out of window* | **Native at the tail** (drizzle from 190.1). The swallows' omen is confirmed on screen inside 15 s — the payoff for the whole reading system. | Snow would replace the swallow omen with a **crow-only** sign and the market folds 20 s earlier. |
| **VII** Rain-Dragon | Dragon procession still runs, dry — the ritual *fails*, the trays stay lit, and the town keeps calling. A genuinely different, sadder version. | *out of window* | *out of window* | **Native.** Full arc: drips → willow dragon → over-delivery → abandonment → strike → Ash Wind. | Snow instead of rain: the willow dragon is carried but not splashed, and the Ash Wind motes read as flakes going *up*. |
| **VIII** Lantern Night | Lanterns still set, but on dry paving — no reflection doubling, so raise brazier count +2 to compensate for the lost light. | *out of window* | *out of window* | **Native via the ground state.** `wetness` is still 1.0 for the first ~6 s of the lantern setting; the reflection smear is the whole point of the timing. | Snow arriving early cuts the crest short: POP peak drops 1.00→.70 and the lanterns are set in the gutter *before* the cloths go up. |
| **IX** White Breath | No snow → the cloths still go up (the town prepares for a cold that doesn't come) and the street is empty anyway. A quiet, slightly foolish, very human version. | *out of window* | *out of window* | Rain instead of snow: cloths become oilcloth, darker; no whiteout, so POP floor rises to .18 because rain is survivable and cold is not. | **Native.** The flying cloth at the peak; snow caps on the cairn. |
| **X** Sign Returned | Base unwrapping. | *out of window* | *out of window* | Wet paving under sunrise: the unwrapping elder leaves a dry trail of lifted cloths on a wet street. | **Native via the ground state.** `snow_cover` melts 358→375 under the elder's path — melt the cap on each object *on the frame its cloth is lifted*, so the elder appears to be thawing the street by hand. |
| **✦ Finale** | Base. | — | — | Wet paving doubles every light of the all-lights-up beat. **Best-looking version — do not suppress it.** | Remaining snow caps blow off every object on the wrap frame in one gust; the knocked-over cairn scatters through snow. |

---

## 7. Tournament-awareness layer

Ambience only. No HUD, no text, no faces. **The governing constraint is restraint:** every cue below involves 2–5 figures at most, so that the finale's whole-street turn (§4) is the only mass reaction in the entire day.

| Trigger | Street response | Cooldown |
|---|---|---|
| **Near-miss** (Pip clears a gap within ~12 px of an edge) | The 2–3 nearest near-lane figures flinch and tilt back for 0.4 s — head pixels tilt, arms half-raise. Nothing else. | 6 s |
| **Score milestone, every 25** | One cluster raises arms in a small wave, front-to-back, 0.15 s apart. | 25 pts |
| **Score milestone, every 100** | One kid throws a small light dot upward — a paper streamer — clamped at y=562. | — |
| **Power-up pickup** | The nearest offering tray lights one extra warm dot for 3 s. The street matching the sky. | 3 s |
| **Coin rush** (every 15th pillar) | Every tray on screen lights one extra dot for the duration of the rush. | — |
| **Genie lamp pickup** | One far-lane elder kneels; the cairn gains a stone permanently. | once |
| **Storm-jolt strike on Pip** | Every visible umbrella dips in unison for 0.3 s. | — |
| **Lightning flash** | Whole band renders as flat silhouette for free (existing overlay). Design constraint: **every silhouette must read at flat black.** | — |
| **Clown gauntlet** | **All reactions off.** Backs turned. See Chapter V. | duration |
| **Newbie ramp (t 0–19)** | **All reactions off.** Ritual stillness. | duration |
| **Treasure chest** | The one mass reaction. See Finale. | once/day |
| **Death** | Every actor in the band halts on the next frame for 0.6 s, then all near-lane figures turn to face **left** — toward where Pip fell. The nearest incense thread bends left. Hold on the game-over frame. | — |

---

## 8. Variety & no-repetition rules

1. **The seeded day-deck.** Every run rolls a `day_seed`. All optional beats draw from per-family decks shuffled by that seed with no-repeat-until-exhausted. No two runs share a beat order.
2. **The Omen of the Day.** One of six suits is drawn at run start: **Steam / Wind / Water / Bird / Stone / Fire.** It biases the recurring accent — which greenery designs get rope-marked, which animal appears most, which offering sits on the shrine, which prop pool dominates the kerb, which of the once-per-day specials are eligible. **Same timeline, different vocabulary**, so the most-replayed minutes of the game read differently every run without touching the pacing.
3. **Three opening variants** for t 0–31.5 (Sweeping / Watering / Cloth-lifting), seed-selected, never the same two days running. The single most-viewed stretch of the game is never identical twice.
4. **Stable slot lifetimes.** Every actor slot has a minimum on-screen dwell and a *stable* inclusion gate that is never re-rolled per frame. Figures walk off; they never pop. (This is already how `_weather_crowd_factor` behaves — extend it to every gate.)
5. **The rule of one.** At most **one** "look at that" set piece visible at a time, with a 6 s minimum between set pieces. No set piece may *enter* the right edge while Pip is inside a pillar gap — hold the spawn until clearance.
6. **Anti-adjacency.** No family in two consecutive far-lane slots. No specific design recurs within 40 s.
7. **Chapter fingerprints.** Each chapter owns two exclusive silhouettes it never shares with any other. At night and in the whiteout, colour is unreliable — *shape* must carry "where am I in the day."
8. **Monotonic accumulation.** Cairn height, rope-marker count, lit-tray count and kerb chalk marks only ever increase across a run. Even with randomised beats, the street visibly *accrues*, so a 300 s run cannot read as a longer loop of a 60 s run. The finale spends the entire tally.

### Once-per-day special happenings

| # | Special | Window | Trigger condition |
|---|---|---|---|
| **S1** | **The Bolt** — all animals flee, all humans freeze 2 s | t 62 – 72 (φ .157–.183) | Fires when `thermal_intensity` first crosses 0.20 rising |
| **S2** | **The Cage Release** — three birds freed | t 96 – 120 (φ .244–.305) | Only after the thermal actually peaked; deferred to Ch X if snow arrives early |
| **S3** | **The Willow Dragon** — rain-calling procession | t 205 – 235 (φ .521–.597) | `rain_intensity ≥ 0.25`; runs dry (and fails) if rain is absent |
| **S4** | **The Ash Wind** — every tray goes dark at once | t 244 – 262 (φ .621–.666) | Within 6 s of a lightning flash |
| **S5** | **The Lantern Setting** — 7–11 gutter lanterns at 0.55× scroll | t 268 – 290 (φ .681–.737) | Rain has ended AND `wetness > 0.5` |
| **S6** | **The Cloth-Draping** — white cloths over everything | t 305 – 327 (φ .775–.832) | `storm_intensity` rising past 0.15 |
| **S7** | **The Unwrapping** — one elder walking against the scroll | t 366 – 384 (φ .930–.976) | `snow_cover` falling |
| **S8** | **The Counted Stones** — final stone, all threads light | t 378 – 392 (φ .960–.996) | Always; the pre-finale payoff |

---

## 9. Logistics

### New art (flag: NEW) — 7 items, 3 of them overlays

| # | Item | Size | Notes |
|---|---|---|---|
| **NEW-1** | **Shrine stones** — three stacked river stones, roadside, far lane | ~14×16 px | Six offering states: bare → tray → incense lit → fruit pile → white-draped → swept. Grounded in real village Earth-God shrines built from three stones (stacked to suggest the character 磊) at a roadside or under a tree. |
| **NEW-2** | **Incense thread** — 1 px wavering warm-grey ribbon | 1×~30 px | A particle, not a sprite. Reusable on braziers, stalls, campfire. Can bend on a global wind signal. |
| **NEW-3** | **Offering tray** — kerb prop with a warm dot | 8×5 px | Dot is on/off, ≤110 luma, max 3 px halo. Never competes with the coin. |
| **NEW-4** | **Rope-and-paper marker** — *overlay* | drawn onto any host | Straw rope + hanging paper strips, fitted to any greenery / lamp / planter / cairn bounding box. Not a new family. Grounded in shimenawa-and-shide marking of spirit-inhabited trees and rocks. |
| **NEW-5** | **Float lantern** — gutter, drifts right at 0.55× scroll | 6×7 px | ≤130 luma. The only object that violates the parallax convention, on purpose. Grounded in Zhongyuan / Ullambana river lanterns. |
| **NEW-6** | **White cloth drape** — *overlay* | fitted to host box | Fits any stall / greenery / shrine / cairn bounding box. Doubles as the snow-cover base. |
| **NEW-7** | **Low swallow flock** — 3–5 dots on arcs, plus perched magpie & crow variants | 4–6 px | One flock drawer, three colour/scale presets. Grounded in the swallows-fly-low-before-rain omen. |

Everything else is a re-direction: performers become vent-tenders (facing flag); the jade dragon becomes the willow dragon (a bucket prop and the existing `_Splash`); the night festival becomes a remembrance (tempo halved); the elder pool gains a stone-stacker and a cloth-lifter (path direction flag); the planter/cairn pool retints to sinter; the food stalls swap food silhouettes for tray silhouettes at t=152.

### Light contract
- Lamp posts unchanged: gated to a dark sky, ≤150 luma, kindling at dusk to full at night, out at phase 0.93.
- Strings keep the 0.40 day floor.
- **New sources:** trays ≤110 luma, float lanterns ≤130 luma, no additive halo over 3 px, and both are suppressed entirely while a lightning flash is active.
- The coin remains the brightest object at every phase, by construction.

### Sound design (feel cues only; all through `audio.py`'s dual backend)
- **Signature per chapter:** I wood-block knocks over silence · II rope-creak ticks · III sub-thump and rising hiss · IV the widest, warmest stall bed of the day · V an 8 dB duck to near-nothing · VI dry and close, wind floor lifting · VII procession drum at quarter time, then rain wash, then thunder · VIII the slowest, softest crowd bed in the game · IX one filtered wind layer, twenty seconds with no human sound · X ambient tone rising with no density change · Finale everything at once.
- The plan's two silences (V and IX) are the plan's most valuable sound events. Protect them.

### Staffing / implementation cues keyed to the timeline
The whole sidewalk reads exactly two signals it doesn't already read: `thermal_intensity(phase)` and a `gauntlet_active` flag. Everything else is already available — `phase`, `rain_intensity`, `storm_intensity`, `wetness`, `snow_cover`, `flash_remaining`, plus the score/pillar/power-up events for §7.

### Contingencies
- **Run ends before the chapter completes** (the common case): every chapter's signature moment sits in its **first third**, so a player who dies mid-chapter has already seen the thing that chapter is for.
- **Clown roll is short (10 pillars, ~5 s):** Chapter V holds its still-state for the full reserved slot regardless, then runs the two-second "Peeking" beat. A short gauntlet gets a longer silence, which is fine.
- **Second and third day-cycles:** the tally resets at the chest; `DAY_SCROLL_STEP` makes day 2 faster, so tighten every beat's dwell by the same scroll ratio and *reduce* set-piece count by 20 % per day — the street should feel like it's struggling to keep up.
- **Weather absent or moved:** every chapter has a defined clear-weather reading in §6, and three of them (VII, IX) are arguably *better* dry. Nothing in the plan breaks if a weather curve is retuned.
- **Performance:** the accumulation props (cairn, markers, trays) are static kerb geometry — cheap. The float lanterns and incense threads are the only per-frame particle additions; both are pooled and both are capped (≤11 lanterns, ≤6 threads on screen).

---

## 10. Sources & inspiration

Research grounded four specific mechanics; everything else is invented and labelled as design.

- **The shrine stones (NEW-1)** and the morning/evening offering round come from documented Chinese village Earth-God (Tudigong) practice: daily incense, offerings of fruit and incense at least at new and full moon, and — in villages without a temple — small roadside shrines built from two base stones and a capstone, under a tree or at the side of the road. — [Grokipedia: Tudigong](https://grokipedia.com/page/Tudigong), [Old World Gods: Tudigong](https://oldworldgods.com/chinese/tudigong-chinese-earth-god/)
- **The rope-and-paper markers (NEW-4)** come from shimenawa: rice-straw or hemp rope with paper shide, used to mark *yorishiro* — trees and rocks a spirit is understood to inhabit — and to bound sacred ground. Sacred stones (iwakura) ringed with rope and ritual paper are a real, and very silhouette-friendly, form. — [Japan Experience: Shimenawa](https://www.japan-experience.com/plan-your-trip/to-know/understanding-japan/shimenawa), [My Japan Clothes: sacred stones in Japan](https://myjapanclothes.com/blogs/japan-blog/the-sacred-stones-in-japan-symbolism-and-unknown-places)
- **The geothermal chapter's register** — steaming vents treated as a place you negotiate with, with a shrine sited at the vents themselves — is grounded in Unzen Jigoku and its Onsen Shrine, and the wider tradition of siting shrines at volcanic hot springs. — [Tokyo Weekender: legendary onsen of Kyushu](https://www.tokyoweekender.com/travel/kyushu-legendary-onsen/)
- **The willow dragon (S3)** is the Water Dragon rain-praying ritual: a dragon whose scales are green willow branches, an altar, a procession, and attendants splashing onlookers with water using willow withes and crying that the rain is coming. — [Water Dragon Rain-Praying Ritual](https://baike.baidu.com/en/item/Water%20Dragon%20Rain-Praying%20Ritual/123100), [Stephen Jones: rain rituals in north China](https://stephenjones.blog/2018/08/08/rain-rituals/)
- **The lantern setting (S5)** is the Zhongyuan / Ullambana custom of floating lotus lanterns at dusk to guide spirits home, with water understood as the boundary of the netherworld — which is exactly why the lanterns in this plan go in the *gutter*, on the wet paving, and drift the wrong way. — [China Highlights: Hungry Ghost Festival](https://www.chinahighlights.com/festivals/hungry-ghost-festival.htm), [Britannica: Hungry Ghost Festival](https://www.britannica.com/topic/Hungry-Ghost-Festival)
- **The cage release (S2)** is fangsheng, the Buddhist merit-release of captive birds and fish, practised at temples since at least the sixth century. — [Wikipedia: Life release](https://en.wikipedia.org/wiki/Life_release), [Culture Trip: fangsheng basics](https://theculturetrip.com/asia/china/hong-kong/articles/buddhist-animal-release-basic-fangsheng-facts-you-should-know)
- **The animal omens** (swallows skimming low before rain; the dog that lies flat and won't move) are real barometric behaviours, not invention: falling pressure and rising humidity push flying insects down, so swallows hunt lower, and the "cows lie down before rain" observation has the same pressure link. — [Farmers' Almanac: animal weather folklore](https://www.farmersalmanac.com/animal-weather-folklore), [Old Farmer's Almanac: can animals predict weather](https://www.almanac.com/can-animals-predict-weather-animal-folklore)
- **The magpie/crow swap** (magpie announces good news, crow announces warning) is a well-attested East Asian contrast and is the cheapest possible omen to render — two dots of different size and value on a lamp arm. — [Chinasage: bird symbolism in Chinese art](https://www.chinasage.info/symbols/birds.htm), [K-Occult: Kkamagwi, the Korean crow](https://koccult.com/creatures/kkamagwi-korean-crow)

The town, the tournament, the pagodas, the Omen of the Day suits, and every specific timing above are invented for this plan. Nothing is claimed as a real named festival.