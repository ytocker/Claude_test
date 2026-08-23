# THE REGULARS — Nine Silhouettes, One Day
### A behavioral redesign of the Skybit sidewalk across one full biome cycle (393.5 s)

---

## 1. Concept

**The through-line, in one sentence:**

> **The sidewalk is a nine-thread ensemble drama: the same nine townsfolk walk the tournament day, each defined by one silhouette-carried prop and one small want, and every time two of them share the screen the street tells a little more — until all nine wants collide at the night festival and pay off, one by one, at dawn.**

**Candidates considered inside the territory:**

| # | Concept | Verdict |
|---|---|---|
| A | **"The Understudies"** — the cast are all people who *almost* flew in the tournament (a retired champion, a kid saving for an entry token, a disqualified rival). | Cut. Every thread points at the same subject; nine variations on one want is a monologue, not an ensemble. |
| B | **"The Feud"** — two rival food stalls, the whole street taking sides, resolved at the festival. | Cut as the spine — magnetically readable but it's a *duet*. Kept and demoted: the feud becomes the ensemble's **strongest single thread** (Auntie Wok vs. Char), giving the braid a spine of its own without eating the other seven. |
| C | **"The Regulars"** — nine independent small wants that braid, cross, and converge. | **Chosen.** It is the purest form of the assigned territory, it front-loads (all nine are introduced before t=112 s, well inside the median run), and it degrades gracefully: a player who sees 40 seconds still meets three people and watches one of them get refused. |

**Why it fits this game.** Skybit's street is ~18px figures on a 160 px/s conveyor, seen in the corner of the eye of a player doing something else. Research on tiny-sprite readability is blunt about the ceiling: at this size **suggestion beats detail, 2–4 colours per figure, and the whole toolkit is silhouette + timing + exaggerated pose** ([Sprite-AI](https://www.sprite-ai.art/guides/how-to-create-16x16-pixel-art), [WigglyPaint](https://wigglypaint.com/blog/pixel-art-animation-guide/)). Players recognise a well-formed silhouette in **under half a second** ([Inviox](https://www.invioxstudios.com/blog/how-long-it-takes-for-players-to-recognize-a-character-silhouette)) — which is roughly the entire time a figure is worth looking at before the next pillar demands attention. So: a character the player can name in 0.4 s, repeated across a day, is the *only* narrative unit this canvas can carry. Nine of them, crossing, is a story.

The ensemble form is also structurally correct here. Ensemble dramaturgy (Altman's *Nashville*, *Short Cuts*) works by **interweaving threads through a shared space and converging them on one event** ([Ensemble cast](https://en.wikipedia.org/wiki/Ensemble_cast), [Script Angel on Aronson](https://scriptangel.com/writing-non-linear-flashback-and-ensemble-scripts-by-linda-aronson/)). Skybit already *has* the shared space (one street) and already *has* the convergent event (the night festival at the crowd peak). The redesign supplies what's missing: people whose presence there means something. The scheduling model is *Majora's Mask* — a small cast on fixed clocks whose paths cross, where the drama is entirely in **who is where, when** ([Bombers' Notebook](https://zeldadungeon.net/wiki/Bombers%27_Notebook)) — except here the player never chases it; it happens whether they look or not.

---

## 2. At a glance

| | |
|---|---|
| **Duration** | One biome cycle = **`CYCLE_SECONDS` = 393.5 s** (`320.0 + DAY_EXTRA_SECONDS 73.5`), plus a ~5 s curtain call past the wrap for the treasure-chest finale |
| **Canvas** | y = 560–640; ground line y=595; far promenade lane (contact y≈597–604, figures ~12px) + near lane (contact y≈608–622, figures ~18px); scroll 160 px/s base |
| **Audience** | A one-thumb player whose eyes are on y=100–500. The street gets peripheral vision and the 0.4 s glances between pillars |
| **Cast** | **9 threads / 10 figures** (the Bench Pair is two people, one thread), all recast from existing families; + the anonymous cast (50 pedestrians, 6 kids, 6 elders, 7 vendors, 9 animals, 8 acts, 30 greenery, 5 stalls, prop pools) |
| **New art** | 4 small procedural props + 1 data layer (§8). Everything else is re-direction |
| **Constraints honoured** | Nothing above y=560 (tallest element, Long Sister on stilts: contact y≈618, height 36px → head y≈582); coin stays brightest (NIGHT_GLOW_CAP 150); street calm during the newbie ramp (0–19 s) and the clown gauntlet |

**Assumptions I made (stated, not hidden):**

1. **The phase↔seconds map is exact; the pillar↔seconds map is not.** `phase_for_time` is pure elapsed seconds, so every phase-anchored event below has an exact wall-clock time. Pillar-anchored events (the genie at pillar 50, the clown at pillar 65) drift earlier when the player takes a rail (×2.5), and the clown warren's 72px spacing compresses wall-clock inside the gauntlet. **Every director cue in this plan keys off `biome_phase`, never off seconds or pillar count.** Seconds are given for human legibility with a ±5 s tolerance after t=128.
2. The existing `_run_fill` 7 s ramp-in stays and is repurposed as the cold open's dramatic device rather than a technical fade.
3. Street audio is spec'd as *implied rhythm* — the visuals must carry every beat alone. If any of it ships, it routes through the existing dual-backend `audio` bridge and sits strictly under gameplay SFX.
4. Greenery keeps its day colour all cycle (existing decision). The **Regulars** do the opposite: they take the full biome tint like everyone else, *except* one tint-locked accent cluster each (§8) — that accent is what makes them recognisable at midnight.
5. I did not read the sibling `DAY_PLAN.md`. Any overlap is convergent, not derived.

### The real remapped keyframes (extracted, not assumed)

`DAY_EXTRA_SECONDS = (30 + 12) × (280/160) = 73.5` → `CYCLE_SECONDS = 393.5`. `_remap` shifts indices 1–4 by `73.5 − NIGHT_BORROW_SECONDS(26) = 47.5 s` and indices 5–6 by the full 73.5 s; the DAY-hold keyframe is inserted at `golden × DAY_HOLD_FRAC(0.51)`.

| Keyframe | phase (real) | t (s) |
|---|---|---|
| DAY | 0.00000 | 0.0 |
| *(DAY-hold ends — fade to golden begins)* | 0.15747 | 62.0 |
| GOLDEN HOUR | 0.30877 | 121.5 |
| SUNSET | 0.41550 | 163.5 |
| DUSK | 0.53749 | 211.5 |
| NIGHT | 0.64422 | 253.5 |
| PREDAWN | 0.83227 | 327.5 |
| SUNRISE | 0.92376 | 363.5 |
| wrap → DAY | 1.00000 | 393.5 |

### The real event anchors

| Event | Source | phase | t (s) |
|---|---|---|---|
| Newbie plateau (5 pillars) | `PLATEAU_PIPES` | 0 → 0.048 | 0 → ~19 |
| Ramp complete (25 pillars) | `RAMP_PIPES` | ~0.150 | ~58.8 |
| Calm breeze / autumn leaves | `calm_breeze` bump c0.18 w0.10 (**unscaled**) | 0.08–0.28, peak 0.18 | 31.5–110.2, peak **70.8** |
| Sinter rocks appear | `thermal ≥ 0.02` | ~0.128 | ~50 |
| Geysers erupting | `thermal ≥ GEYSER_SPAWN_THRESHOLD 0.35` | 0.174–0.268 | **68 – 106** |
| Thermal peak | `THERMAL_PEAK_PHASE` | 0.24396 | **96.0** |
| Genie lamp | `GENIE_PILLAR` = pillar 50 *(pillar-anchored — drifts)* | ~0.261 | ~102.6 |
| Clown reveal → warren → outro | `CLOWN_START_PILLAR 65`, 72px spacing *(drifts)* | ~0.325–0.374 | ~128 – ~147 |
| Rain drizzle begins | `RAIN_DRIZZLE_START` (pillar 100) | **0.48307** | **190.1** |
| Wet paving begins | `rain ≥ WEATHER_WET_ON_RI 0.18` | ~0.525 | ~207 |
| Umbrella pickup #1 / #2 | pillars 112 / 124 *(drift)* | ~0.537 / ~0.590 | ~211 / ~232 |
| Drizzle peak / storm bump starts | `RAIN_DRIZZLE_PEAK` | 0.56439 | 222.1 |
| Lightning window opens | `LIGHTNING_PHASE_MIN` | 0.62132 | 244.5 |
| **Thunderstorm peak** | `RAIN_STORM_PEAK` | **0.62945** | **247.7** |
| Rain over / lightning closes | `LIGHTNING_PHASE_MAX` | 0.69450 | 273.3 |
| Snow squall lower edge | `_SNOW_LOWER_EDGE` (pillar 169) | 0.78994 | 310.8 |
| Snow load builds on Pip | `storm ≥ WEATHER_SNOW_ON_WI 0.45` | 0.814 | 320.3 |
| **Snow peak + tailwind ×1.40** | `SNOW_STORM_CENTER` | **0.87126** | **342.8** |
| Defrost begins | `+WEATHER_SNOW_MELT_AT 0.04` | 0.91126 | 358.6 |
| Snow gone | `storm → 0` | ~0.957 | ~376–384 |
| **Cycle finale: 3 forced rush pillars + chest** | `CYCLE_FINALE_*` | wrap | 393.5 → ~398.7 |

**The load-bearing accident worth naming:** rain ends at 273.3 s and snow begins at 310.8 s. That leaves a **37-second clear, dark, warm-lit gap — the only one in the whole cycle.** That is where the festival goes, and it is why the convergence lands where it lands.

---

## 3. The cast — nine threads

Every Regular = **one existing family member + one silhouette prop + one tint-locked accent + one want.** No faces, no text. Reserved so no anonymous figure can ever be mistaken for them.

| # | Regular | Recast from | Silhouette tell | Tint-locked accent | Want | Payoff |
|---|---|---|---|---|---|---|
| 1 | **Wick**, the lamplighter | existing `lamplighter` + elder pool | stooped, 14px pole over the shoulder | ember-orange 2px at the pole tip | To light every lamp before dark | He's the only moving thing on the street through the storm's Relight; at predawn he snuffs them all again |
| 2 | **Sprig**, the ladder girl | kid pool | tiny, dragging a ladder taller than she is | pale-jade 3px sash | To hang the highest lantern | Lifted to the hook at the festival; her lantern hangs directly under Pip's flight line |
| 3 | **Auntie Wok** | vendor + **wok stall** | broad, one arm up with a ladle, permanent flare | deep-red 4px apron block | To out-sell Char | The only visible **queue** on the street; then the merge |
| 4 | **Steam**, the tea-man | vendor + **tea stall** | narrow, long-spout kettle, constant plume | brass 2px spout | For everyone to sit down | Last stall open in the whiteout, serving Wick |
| 5 | **Char**, the rival griller | vendor + **grill stall** | squat, wide brim, skewer fan, smoke column | charcoal-blue 4px hat brim | To beat Auntie Wok | Sets up *beside* her, not opposite, at dawn |
| 6 | **Long Sister**, the stilt-walker | performer pool (re-proportioned) | 1.8× everyone, two thin leg lines | saffron 3px ribbon at the hip | An audience | Leads the dance; walks home at ordinary height |
| 7 | **Bun**, the dog | animals pool (one reserved design) | light body, curl tail, always ~40px behind whichever Regular is on screen | cream body (never retinted below 50%) | Food | A ribbon at the front of the lion dance; asleep on Wick's boots at dawn |
| 8 | **The Bench Pair** | 2× elder pool + reserved bench prop | one round, one thin, **always seated**, arms mid-argument | one rust, one slate | To finish the argument | They **stand up** at the festival — the single biggest silhouette event of the day, because they've been seated for 260 seconds |
| 9 | **Broom**, the sweeper | pedestrian pool + broom prop | bent over a 16px broom, pushing a growing pile | dun 2px cap | A clean street | He sweeps the entire festival away at predawn — he is literally the mechanism that resets the world for day 2 |

**The crossing rule (the engine of the whole thing):** at most **two** Regulars share the screen (three only at the festival). When two do, they must **acknowledge** — a nod, a step aside, a turned back, a handed object, a refusal. Anonymous figures never acknowledge anyone. That single asymmetry is what makes nine sprites read as characters and forty read as traffic.

---

## 4. Master timeline — 100% of 393.5 s

**Density** = the crowd multiplier (replaces `_POP_KEYS`), before the weather factor. **Look** = the beat's one "look at that" image.

---

### CH 0 — COLD OPEN: AN EMPTY STREET · t 0–19 s · φ 0.000–0.048
*Solid DAY. Newbie plateau (5 pillars) — **mandated calm**.*
> **So the player feels:** *I've landed somewhere that was here before I arrived.*

| t (s) | φ | Beat | Street | Look | Sky / gameplay hook | Light & sound |
|---|---|---|---|---|---|---|
| 0–7 | .000–.018 | **One person** | Density 0.00→0.12. `_run_fill` reframed: not a fade-in, a *lone figure*. **Today's cold-open Regular** (seeded, rotates through 6) walks the far lane, doing their one defining action | The only moving thing in the bottom strip is one silhouette | Newbie tuning: wide gaps, slow scroll. Nothing competes | Full daylight; strings at the 0.40 day floor; implied: one repeated sound (broom / flint / shutter) |
| 7–13 | .018–.033 | **The action lands** | Same figure completes the action: Wick *snuffs* a lamp (his job is inverted at dawn) / Broom sweeps / Wok lifts a shutter / Char strikes flint / Sprig drags the ladder / Steam sets the kettle. A second Regular appears at the right edge and **does not interact** | The near-empty frame, one gesture, held | — | flat, clean, no glow |
| 13–19 | .033–.048 | **The awning wave** | Density 0.12→0.30, far lane only, 3–4 anonymous. Shutters and awnings flip up in a **left-to-right staggered wave**, one every ~40px of scroll | A wave of opening awnings travelling against the scroll | Pillar 5–6: the ramp begins to tighten under the player | first warm accents appear |

---

### CH 1 — NINE DOORS OPEN · t 19–50 s · φ 0.048–0.127
*Solid DAY. The morning market — the busiest street of the day. Every player sees this chapter.*
> **So the player feels:** *this town is full of people who know each other.*

| t (s) | φ | Beat | Street | Look | Hook | Light & sound |
|---|---|---|---|---|---|---|
| 19–26 | .048–.066 | **Two fires** | Density 0.30→0.65; near lane opens. **Auntie Wok's flare is the first fire of the day**; 1.5 s later **Char's flint answers, directly opposite her**, mirrored across the lane | Two fires lighting in mirror image, one each side | — | brightest daytime warm accents, both capped well under coin luma; implied sizzle |
| 26–34 | .066–.086 | **Market peak** | **Density 0.88 — the day's daytime maximum.** 6 anonymous + max 2 Regulars. Bun works the line of legs. Kids run counter-scroll so they appear to hold position | **The queue at Wok's**: four figures in a straight line — the only straight line in a chaotic crowd | Coin rush every 15th pillar: Regulars **point horizontally** (never up — up is reserved for milestones) | dense, hot, cluttered |
| 34–42 | .086–.107 | **★ THE REFUSAL** *(anchored)* | Density 0.85. Sprig raises a lantern toward passing adults. **Three refusals in a row** — arm-wave, turn-away, flat ignore. The third refuser is **Char** | A tiny figure holding something up, three times, to nobody | This is the plant. It pays off at t≈150 — inside the median run | crowd noise; her gesture is the only slow motion in a fast frame |
| 42–50 | .107–.127 | **Two untouched cups** | Density 0.85→0.72. **Bench Pair established** — they enter *already seated and already arguing* (arms only). Broom sweeps the market's wake. **Steam sets two cups on the bench between them; neither touches them** | Two cups nobody picks up | — | the market's roar starts to thin |

---

### CH 2 — THE GROUND BREATHES · t 50–112 s · φ 0.127–0.285
*DAY-hold ends at 62 (sky begins warming). Sinter rocks from 50, geysers 68–106 (peak 96), calm-breeze leaves 31.5–110 (peak 70.8), genie lamp ~102.6.*
> **So the player feels:** *the ground itself has joined the cast, and the people are giving it room.*

| t (s) | φ | Beat | Street | Look | Hook | Light & sound |
|---|---|---|---|---|---|---|
| 50–58 | .127–.147 | **Grit** | Density 0.72→0.66. Sinter rocks scatter. **Broom starts sweeping grit and cannot keep up** — from here to 112 he re-enters every ~20 s with a visibly bigger pile | The first rock lands and a walker sidesteps it without breaking stride | Rocks are the geyser telegraph; the street reads the telegraph *before* the player does | dry, gritty; a repeated scrape |
| 58–70 | .147–.178 | **Long Sister stands up** | Density 0.66→0.58. **Breeze peaks at 70.8** — autumn leaves at max; **Bun chases a leaf** across the near lane, path crossing the real leaf particles. At the right edge, **Long Sister rises to full stilt height** | A silhouette that *grows* — she appears to double in size in one second | DAY-hold ends at 62: the sky begins its amber drift and the street's rims warm with it | leaves; the first amber on the paving |
| 70–82 | .178–.208 | **The steamer on the vent** | Density 0.58→0.55. **First geysers.** The far lane **bends around the vent line** in a visible curved path. **Auntie Wok slides a steamer basket over a vent** and her plume doubles for free | A market steamer riding a geyser | Geysers give Pip a continuous updraft; the street's reaction (detour + exploitation) tells the player the vents are *real*, not decoration | hiss; bursts of white against warm ground |
| 82–95 | .208–.241 | **The wobble** | Density 0.55→0.50. Floater window (§7). **Long Sister practises and wobbles — and catches herself.** This is the plant for The Fall | A near-topple that doesn't topple | Rail power-up (score 100) may fire from here: if the scroll goes ×2.5, near lane drops a notch and switches to static poses (§9) | breeze; sparse |
| 95–102 | .241–.259 | **The vent field** | **Thermal peak (96).** Density **0.42** — the day's cluttered-ground / empty-street inversion. Rock rings ring every cone. The townsfolk have **given the ground to the vents** | A full rock-ringed vent field with one lone Regular threading through it | Peak geyser density = peak player lift. The street's emptiness reads as *deference* | loudest hiss of the morning; humans quiet |
| 102–112 | .259–.285 | **The lamp flash** | Genie lamp ~102.6. **Every figure on screen turns toward the flash and holds for 0.6 s. The Bench Pair do not.** Thermals fade out (end 112). Density 0.42→0.30 | The whole street turning — and two who don't | The genie is the day's first *magic*; the street being surprised by it sells it. The Bench Pair not caring is their entire character in one frame | a single held chord; then the hiss dies |

---

### CH 3 — LONG SHADOWS · t 112–128 s · φ 0.285–0.325
*GOLDEN HOUR keyframe at 121.5. A **deliberate quiet valley** — the day's first real breath, and the ramp-down into the gauntlet hush.*
> **So the player feels:** *the afternoon has gone soft; something is about to change.*

| t (s) | φ | Beat | Street | Look | Hook | Light & sound |
|---|---|---|---|---|---|---|
| 112–121 | .285–.308 | **The failed light** | Density 0.30→0.20. Lamp posts come up (existing fixture window opens ~φ0.20). **Wick appears with the pole for the first time** and tests one lamp — **it doesn't catch. Too early.** He moves on | A lamp that doesn't light | Pure plant: his whole evening arc, established in one failure | thin crowd; the first lamp-post silhouettes |
| 121–128 | .308–.325 | **The shadow rake** | **GOLDEN (121.5).** Density 0.20→0.13. Every near-lane figure gains a 2px warm rim on its left edge; the Bench Pair's shadows stretch across the paving. Floater window (The Nap) | Long raked shadows crossing the whole strip in one direction | The sky's amber and the street's shadows are the same event, seen twice | golden, still; almost silent |

---

### CH 4 — HUSH FOR THE GAUNTLET · t ~128–147 s · φ ~0.325–0.374
*Clown reveal → warren → outro. **Mandated calm.** The deepest daytime valley — designed as a story beat, not an absence.*
> **So the player feels:** *the town is holding its breath for me.*

| t (s) | φ | Beat | Street | Look | Hook | Light & sound |
|---|---|---|---|---|---|---|
| 128–133 | .325–.338 | **A street of backs** | Die/clown reveal in the sky. **Everyone on screen turns their back to the sky and stops walking.** Density frozen at 0.12. **Only Steam's plume still moves** | A row of turned backs | The inversion of the tournament layer: everywhere else the street *watches*. Here it looks away — which is far more ominous, and keeps the strip visually dead-quiet while the gauntlet demands 100% of the player's attention | strings dim 15%; street audio floor drops to zero |
| 133–142 | .338–.361 | **Nothing** | The warren. **Zero near-lane motion.** Far lane holds exactly 3 static bowed silhouettes. No new spawns | Nothing happens. *That is the moment.* | Absolute readability protection through the tightest gaps in the game | one thin steam column, no other motion in the bottom 80px |
| 142–147 | .361–.374 | **Heads up, one at a time** | Outro. Heads lift and walk cycles restart in a **left-to-right ripple** — the deliberate rhyme of CH 0's awning wave. Density 0.12→0.20 | The street coming back to life one head at a time | Release. The player has just survived something and the town noticed | audio floor returns; a single rising note |

---

### CH 5 — GOLDEN VERDICT · t 147–190 s · φ 0.374–0.483
*SUNSET keyframe at 163.5. **The median run (~156 s) ends here** — so this chapter must contain a complete, satisfying payoff.*
> **So the player feels:** *that little thing from this morning just came back.*

| t (s) | φ | Beat | Street | Look | Hook | Light & sound |
|---|---|---|---|---|---|---|
| 147–158 | .374–.401 | **★ THE HAND** *(anchored — the median player's payoff)* | Density 0.20→0.42. **Char walks up to Sprig, sets a crate down in front of her, and walks off without looking back.** She steps onto it. | The crate | The man who refused her at t≈40 gives her three inches. Plant→payoff inside 110 seconds, landing exactly at the median exit. **This is the beat that makes a one-run player believe the street has memory.** | crowd returning; warm |
| 158–170 | .401–.432 | **Pink on one side** | Density 0.42→0.58. Two busker acts out. **SUNSET (163.5)** — the rose palette lands; every warm rim turns pink and every shadow goes long and cold | An entire crowd lit pink on one side and dark on the other | The prettiest 12 seconds in the bottom strip. Deliberately placed *after* a payoff and *before* a gag — the rest between two peaks | the day's warmest, softest light |
| 170–182 | .432–.462 | **★ THE FALL** *(anchored)* | **Density 0.62 — afternoon peak.** Long Sister topples. **Wick catches her stilt with his lamp pole.** She's off the stilts for the next ~40 s | **Two poles crossing** — the day's best silhouette gag, and its first real physical contact between two Regulars | The wobble at t≈88 paid off. Two threads that had nothing to do with each other are now tied | the biggest single crowd reaction of the daylight hours |
| 182–190 | .462–.483 | **Umbrellas under a dry sky** | Density 0.62→0.55. Awnings unroll left-to-right. **Three umbrellas open before the first raindrop falls** | Open umbrellas, clear sky | **The street reads the weather faster than the player does** — a free, diegetic 8-second telegraph for the storm block | wind picking up; the light goes flat |

---

### CH 6 — FIRST DROPS · t 190–222 s · φ 0.483–0.564
*Drizzle from 190.1. Wet paving from ~207. DUSK keyframe 211.5. Umbrella pickup #1 ~211. Drizzle peaks 222.*
> **So the player feels:** *the town is closing around me, and one old man has a job to do.*

| t (s) | φ | Beat | Street | Look | Hook | Light & sound |
|---|---|---|---|---|---|---|
| 190–200 | .483–.508 | **One fire dies, one grows** | Drizzle 0→0.10; umbrellas per `WEATHER_UMBRELLA_RAIN_AT 0.12` at t≈196. Density 0.55→0.46. **Char claps a lid on his coals and his smoke dies. Wok unfurls her awning and her flare grows.** | Two fires on opposite sides of the street, one going out and one going up | The feud, decided by weather. Char protects his stock; Wok never closes. Their characters are now *legible* rather than asserted | first rain hiss; the street's colour drains |
| 200–211 | .508–.537 | **The first lamp catches** | **Wetness from ~207:** paving glazes and every lamp/lantern gains a vertical smear reflection in the sheen. **DUSK (211.5): lamps kindle** (`_lit_intensity ≈0.40`). **Wick's run begins** — he now moves *faster than the scroll*, so he keeps re-entering from the left edge. Density 0.46→0.38 | The first lamp catching, and its smear on the wet stone | The failed light at t≈115 pays off. And the "faster than scroll" trick makes one 18px figure feel like he's outrunning the world | rain on stone; a small dry *tick* per lamp |
| 211–222 | .537–.564 | **Backs to the storm** | Umbrella power-up in the sky at ~211 — **a near-lane figure closes their umbrella and holds it up as Pip passes** (a salute, not a HUD). Floater window: **The Shared Awning**. Density 0.38→0.32 | **Wok and Char under one awning, backs to each other, both refusing to acknowledge it** | Seeds the Merge. The forced proximity is the weather's doing, not theirs | drizzle steady; the crowd's sound thins to footsteps |

---

### CH 7 — THE DOWNPOUR · t 222–273 s · φ 0.564–0.694
*Storm bump 222→273, **peak 247.7**. NIGHT keyframe 253.5. Lightning 244.5–273.3. Crowd floor `WEATHER_CROWD_RAIN_MIN 0.22`. Umbrella #2 ~232. Storm-jolt on Pip near the peak.*
> **So the player feels:** *everyone went inside except one man with a pole.*

| t (s) | φ | Beat | Street | Look | Hook | Light & sound |
|---|---|---|---|---|---|---|
| 222–232 | .564–.590 | **The walk-off** | Storm rises. Effective density → ~0.10. Figures **walk off once** (existing stable-gate idiom, never pop); survivors raise umbrellas; shelter figures tuck under kiosk awnings and lamp posts | The street emptying as one continuous departure | The sky peaks while the street troughs — the inverted energy that keeps the two layers from shouting over each other | rain to a roar; footsteps gone |
| 232–244 | .590–.620 | **Bun watches the rain line** | Umbrella #2 at ~232 (same salute). Deep night falls. Lit objects reduce to: lamps, Wok's awning-flare, Steam's kettle, the strings. **Bun curls under the kiosk at the exact edge of the dry line** | One dog, dry, watching the water fall two inches from his nose | Minimum ambient distraction during the heaviest weather-on-gameplay coupling (flap dampen, coin shake, Pip shiver) | rain; one kettle |
| 244–256 | .620–.651 | **★ THE RELIGHT** *(anchored)* | **Lightning opens 244.5; storm peak 247.7; NIGHT 253.5.** The first flash **blanks every lamp on screen for 0.6 s.** Wick then walks the length of the street relighting them, **one at a time, 0.3 s apart, left to right.** For ~8 s he is **the only moving figure in the game** | Nine lamps coming back on, one by one, in a black street | The night keyframe lands *inside* his walk, so the palette's coldest turn happens while he is manufacturing the only warmth. Contrast, not brightness — the coin is still king | thunder tail; then nine small ticks in the quiet |
| 256–265 | .651–.673 | **The stilts go back up** | Storm falls off. Sheltered figures test the rain: **one foot out, retreat, then commit.** **Long Sister remounts the stilts in the last of the rain.** Density 0.10→0.25 | Wet stilts rising | Recovery. She was down for 85 seconds; she is about to lead the festival | rain easing; the first voices back |
| 265–273 | .673–.694 | **The braziers catch** | Rain ends ~273; wetness peaks then begins drying. Floater: **The Wet Dog** (Bun shakes; the near lane steps back in a ripple). **Three braziers light in sequence down the far lane** — the first true warmth since the storm. Density 0.25→0.50 | Braziers catching one after another down the street | The festival's overture, and the visual rhyme of the Relight — but now it's the whole town lighting up, not one man | drums and voices rising from off-screen |

---

### CH 8 — THE FESTIVAL · t 273–310 s · φ 0.694–0.788
*The **only** long clear, dark window in the cycle (rain ends 273.3, snow begins 310.8). **Crowd peak 1.00.** The convergence.*
> **So the player feels:** *everything I saw today just walked into the same square.*

| t (s) | φ | Beat | Street | Look | Hook | Light & sound |
|---|---|---|---|---|---|---|
| 273–285 | .694–.724 | **Doubled lanterns** | Density 0.50→0.85. Lion dance enters; banner poles up. **For the first ~5 s the stone is still wet, so every lantern is doubled in the sheen** — then the reflections dry away | The lion and its reflection, until the reflection evaporates | A free, perfectly-timed visual gift from `wetness`'s decay rate. Use it | full festival wall of sound |
| 285–297 | .724–.755 | **★ THE MERGE** *(anchored)* | **Density 1.00 — the day's absolute peak.** Wok's and Char's stalls are **side by side** with a **shared queue**, and **their two smoke columns bend and braid into one plume.** *(NEW set piece — §8)* | **One plume rising from two fires** | The day's thesis image. The feud, established at t=20 as two mirrored fires, resolves as one column. Nothing brighter than the coin: the flare is capped and the *contrast* comes from cooling everything around it | loudest the street ever gets — then it must not get louder again |
| 297–306 | .755–.777 | **★ THE LIFT + ★ THE STANDING** *(anchored, simultaneous)* | Density held 1.00. **Long Sister lifts Sprig to the highest hook. The lantern lights, and it hangs directly under Pip's flight line — for ~2 s the player flies over Sprig's lantern.** In the same window: **the Bench Pair stand up** for the first time in 260 seconds. Broom gives up and dances with the broom. Bun wears a ribbon at the head of the lion | **The lift** — the day's smallest character carried by its tallest | Every thread resolves inside nine seconds, but staggered, not stacked: lift → stand → dance → dog. The stand is the loudest because it's the *stillest* character finally moving | one crowd roar, then the sound *drops* under the standing |
| 306–310 | .777–.788 | **First flakes in the firelight** | The crest breaks. Dragon exits right; the crowd thins **from the far lane inward**. **The first snow (lower edge ~309) is visible only where it crosses a brazier's glow** | Snow that exists only inside the light | The turn. The festival doesn't end — it gets interrupted | the roar decays; a cold note underneath |

---

### CH 9 — SWEEPING IT AWAY · t 310–345 s · φ 0.788–0.877
*Snow squall builds. PREDAWN keyframe 327.5. Snow load from 320.3, tailwind ramping to ×1.40. Crowd floor `WEATHER_CROWD_SNOW_MIN 0.06`.*
> **So the player feels:** *someone is putting the day away while I'm still flying.*

| t (s) | φ | Beat | Street | Look | Hook | Light & sound |
|---|---|---|---|---|---|---|
| 310–320 | .788–.813 | **★ THE GREAT SWEEP** *(anchored)* | Squall arrives (drifts+flakes >0.10 from ~309, streaks >0.15 from ~315). Banner poles come down; **braziers are banked, not extinguished** — they stay as the last warm anchors. **Broom pushes a full screen-width of festival litter off the right edge in one continuous pass, moving faster than the scroll.** Density 0.72→0.40 | **A line of litter travelling rightward against every other motion in the game** | Broom's want — a clean street — becomes the mechanism that resets the world. The sweeper is the loop | the sound of the festival being physically removed |
| 320–330 | .813–.839 | **Stilts in a whiteout** | Snow load builds on Pip from 320.3; **tailwind ramps toward +40% scroll → near lane drops one density notch and switches to static poses only** (readability valve, §9). **PREDAWN (327.5)**: cold pink. Footprint trails appear as 1px dark lines in the snow layer. **Long Sister refuses to dismount and walks the squall on stilts — the tallest thing in the whiteout, half-erased by flakes.** Density 0.40→0.20 | A stilt-walker dissolving into white | Her want was an audience. There is nobody left, and she's still up there | wind; everything else muffled |
| 330–345 | .839–.877 | **The lamps go out** | Swirls >0.30 from ~325; squall thickens toward the 342.8 peak. Density → 0.08. **The Bench Pair are still there, snow gathering on their shoulders, still arguing.** **Wick walks the line snuffing lamps — the exact inverse of the Relight, and of the cold open** | Lamps going out one by one, and two figures who will not leave the bench | The day's structural mirror closes: he snuffed a lamp at t=9 and he snuffs them all at t=340 | wind only; each snuff is a soft *pop* |

---

### CH 10 — THE WHITEOUT VIGIL · t 345–364 s · φ 0.877–0.925
*The **quietest 19 seconds of the cycle.** Defrost begins 358.6. SUNRISE keyframe 363.5.*
> **So the player feels:** *the town survived the night, barely, and someone kept a kettle on.*

| t (s) | φ | Beat | Street | Look | Hook | Light & sound |
|---|---|---|---|---|---|---|
| 345–355 | .877–.902 | **Two figures and a kettle** | **Density 0.05** — two or three silhouettes across the entire stretch. **Steam's kettle stall is the last open thing in town, and one dark seated shape (Wick) is at it.** Ground reads white; strings are the only colour left | Two figures, a kettle, and a white field | **The plan's emotional floor, placed immediately before the recovery.** Also the safest possible street during the tailwind's fastest scroll | the whiteout wash; one kettle whistle |
| 355–364 | .902–.925 | **The dog comes back** | Defrost at 358.6; snow load sheds. **Bun trots back into frame and lies against Wick's boots.** Density 0.05→0.14. First sunrise pink at 363.5 | The dog arriving | The smallest possible signal that the day is going to be alright, delivered by the least verbal character | wind dropping; the whistle steadying |

---

### CH 11 — PAYOFF DAWN · t 364–393.5 s · φ 0.925–1.000
*SUNRISE. Snow gone ~376–384. The deliberate mirror of CH 0 and CH 1 — every thread pays out.*
> **So the player feels:** *I know all of these people now.*

| t (s) | φ | Beat | Street | Look | Hook | Light & sound |
|---|---|---|---|---|---|---|
| 364–374 | .925–.951 | **Two awnings in unison** | The **awning wave replays** — different order (seeded), and **Wok and Char raise theirs at the same instant, side by side**, where at dawn they were opposite and mirrored. Ground melts white → wet → dry. Density 0.14→0.30 | Two awnings going up together | The Merge, made permanent. The feud didn't get resolved by a speech; it got resolved by a night | soft; the first sizzle of the new day |
| 374–384 | .951–.975 | **The payoff run** | Delivered in sequence, one per ~2 s of scroll: **Sprig asleep at the foot of the lantern pole, ladder folded beside her. The Bench Pair asleep, leaning on each other, argument unfinished. Long Sister walking home carrying her stilts — ordinary height. Broom leaning on the broom, looking at a clean street. Steam finally banking his kettle.** Density 0.30→0.44 | **Long Sister at normal height** — a joke only a player who saw her at t=65 can get | Nine threads, closed. Nothing is *stated*; each is a pose | quiet, warm, unhurried |
| 384–393.5 | .975–1.000 | **The held breath** | Snow gone. **The widest figure spacing of the entire day** — the street deliberately uncluttered. **Everyone faces right, the direction Pip is flying.** Strings ramp back to the 0.40 day floor. Density 0.44→0.58 | An entire street facing the same way | The runway into the finale. Empty enough that the coin rush that's coming has clean air | a rising kettle whistle under everything |

---

### CH 12 — THE CURTAIN CALL · wrap → ~+5.2 s · finale coin rush + treasure chest
*`CYCLE_FINALE_PHASE_HI/LO` rollover → 3 forced rush pillars, chest on pillar 2, `TREASURE_BOX_ANIM_T = 1.5`.*
> **So the player feels:** *they were all watching. They were all waiting for this.*

| Cue | Street |
|---|---|
| **wrap + 0.0 s** | **Every sleeping figure on screen sits up in one frame** — a single synchronised 2px head-lift travelling the whole strip. No new sound but the kettle whistle topping out |
| **wrap + 0.5 s** | **Wok and Char strike their fires simultaneously** — two flares, one per lane, framing the incoming coin rush like stage lights |
| **wrap + 1.5 s** *(chest pillar entering)* | **Near lane fills to 0.90 in 1.5 s — the fastest crowd ramp of the day.** All nine threads on screen **at once, for the only time in the cycle**, spaced left-to-right so every silhouette reads clear of its neighbours: **Broom · Bench Pair · Steam · Bun · Wick · Sprig · Long Sister · Wok · Char** |
| **chest pickup** | Every figure **arms up, held 1.5 s** (matched to the fanfare tail). The coin/chest bloom stays the brightest thing on screen; the street's contribution is *shape*, not light |
| **fanfare tail** | All ten figures **turn and walk right — the direction Pip flies.** The street empties in the direction of travel, and what's left is **CH 0's empty street.** The loop's seam, dressed as a bow |
| **if the player dies first** | No curtain call. The **freeze rule** applies (§6): all motion halts on the collision frame; 1.0 s later a single figure lowers their head or removes a hat. Nothing else. No fanfare, no wave |

---

## 5. Narrative arc

**Shape: a braid with a hollow midpoint, a late convergence, and a long cold denouement that resets the stage.**

The day opens on **one person** and widens to a full market inside thirty seconds (rising), then hands the ground over to the geysers while the humans step back (a *density* trough that is also a *spectacle* peak — the first deliberate inversion). Golden hour goes soft and empty, and then the gauntlet drives the street to near-total stillness at t≈133 — **the hollow midpoint**, and the only place in the plan where nothing happens on purpose. Release comes as a payoff rather than a bang: Char's crate, landing at t≈150, precisely where the median run ends, so the most common experience of this street is *plant, wait, payoff, exit*. From there the arc climbs through the golden verdict, then executes its second and biggest inversion: **the storm is the sky's loudest hour and the street's emptiest**, and the whole of it belongs to one old man relighting nine lamps. That trough is what makes the festival land. The convergence occupies the single 37-second clear-dark window the weather system leaves open, and its four payoffs are **staggered, never stacked** — merge, lift, stand, dance — with the crowd sound dropping *under* the Bench Pair standing, because the stillest character moving is the loudest thing in an ensemble. Then the snow arrives and the falling action is given a **physical agent**: Broom sweeps the festival off the right edge of the world. The vigil at t=345–355 is the emotional floor, deliberately nineteen seconds long and deliberately adjacent to the recovery. Dawn pays out all nine threads in a run of poses, none of them stated. And the chest is a **curtain call** — the only moment the entire ensemble shares a frame — after which they walk off in the direction the player is flying, leaving behind exactly the empty street the run began on.

**Energy pacing check:** market peak (t 29) → grit trough (t 96) → gauntlet hollow (t 133) → payoff (t 150) → golden crest (t 175) → storm trough (t 235) → relight (a *quiet* peak, t 248) → festival peak (t 291) → sweep (t 315) → vigil floor (t 350) → dawn warm (t 380) → curtain call (t 395). **No two peaks are adjacent.** Every peak is preceded by at least eight seconds of trough.

---

## 6. Tournament-awareness layer

Ambient only. Never a HUD, never text, never above y=560. Every response is a **pose change plus a 2px offset** — cheap, and legible at 18px because the whole strip moves as a group.

| Trigger | Street response | Duration |
|---|---|---|
| **Pip passes a pillar** (routine) | Any Regular within 60px of x=90 does a **1-frame head-tilt-up** (2px) | 1 frame |
| **Near-miss** (gap cleared within a tight margin) | **Stadium ripple**: nearest 3 near-lane figures flinch, then arms-up — the wave travels right-to-left at scroll speed, so it looks like it's chasing Pip | 0.4 s per figure, ~1.2 s total |
| **Milestone** (every 25 pillars) | 5–8 figures arms-up for 1.2 s, **plus one Regular's specific tell**: Wok bangs the ladle; Long Sister raises both arms; Bun spins; Broom lifts the broom | 1.2 s |
| **Coin rush** | Regulars **point horizontally** (arm out, toward the coins) — never up. Up is reserved so milestones stay distinct | duration of the rush |
| **Power-up collected** | Nothing. The sky's fanfare owns it; the street must not double it |
| **Life lost / knight save** | **The gasp**: the entire near lane's walk cycles halt for 0.5 s, all heads up, then resume | 0.5 s |
| **Clown gauntlet** | **Inverted**: everyone turns their back, bows their head, stops moving. "Don't look." Also the readability guarantee | full gauntlet |
| **Genie lamp** | Every figure turns toward the flash and holds 0.6 s — **except the Bench Pair** | 0.6 s |
| **Umbrella pickup** (~211, ~232) | One near-lane figure **closes their umbrella and raises it** as Pip passes — a salute | 1.0 s |
| **Rail active** (scroll ×2.5) | Near lane thins to 0.30 and switches to **static poses only** | duration |
| **Treasure chest** | Full curtain call (§CH 12) | 1.5 s + exit |
| **Death** | **The stop.** All motion halts on the collision frame. 1.0 s later, one figure lowers their head or removes a hat. Nothing else, ever | until scene change |

---

## 7. Weather overlay matrix

**Rule: weather modulates a chapter; it never replaces it.** The chapter's cast, density curve and story beats are the constant; weather changes *how* they do the same thing.

### 7a. Chapter × condition

| Chapter | **Clear** | **Calm breeze** (t 31–110) | **Thermal / geysers** (t 50–112) | **Drizzle + wet** (190–222) | **Thunderstorm** (222–273) | **Snow + tailwind** (309–384) |
|---|---|---|---|---|---|---|
| **CH0 Cold Open** | as written | leaf drifts past the lone figure; their prop catches the wind | *n/a* — vent line held clear of the ramp | doorways stay shut; the lone figure has an umbrella; awning wave becomes a **shutter-closing** wave | + puddle reflections of the unlit strings | frost line on the paving; figure leaves a footprint trail |
| **CH1 Nine Doors Open** | as written | leaves settle in the queue; kids chase them | vents thin the far lane 15%; walkers detour | density × rain factor; **the queue at Wok's survives** (that's her character); Char covers early | market compresses under the awnings, doesn't disperse — it's morning, they have to trade | stalls open anyway; steam plumes double against cold air |
| **CH2 Ground Breathes** | as written | **canonical** — the leaf-chase is written for it | **canonical** — the detour curve, the steamer gag, Broom losing to grit | rain + vents = the biggest white plumes of the day; crowd halves, Wok stays | vents flare against the flashes; the street clears entirely | vents melt circular bare patches in the snow_cover — the only ground colour |
| **CH3 Long Shadows** | as written | last leaves; the failed lamp gutters | fade-out grit; Broom finally clears his pile | Wick's lamp **fails to light because it's wet** — a better version of the same beat | lull cancelled; go straight to CH6 behaviour | lamps kindle early against the dark |
| **CH4 Gauntlet Hush** | as written | **suppressed** — no leaf spawns during the hush | vents suppressed on the near lane | backs turned *and* umbrellas up; still zero motion | the only permitted motion is a lightning-lit freeze-frame of turned backs | snow gathers on motionless shoulders — **the hush becomes visually richer, not poorer** |
| **CH5 Golden Verdict** | as written | ribbons and leaves; the Fall is wind-assisted | grit under Sprig's crate | **canonical** — the pre-rain umbrellas ARE this chapter's exit | Long Sister never mounts; the Fall becomes **a slip on wet stone** | she can't mount at all; Wick hands her the pole instead (same crossed-poles image) |
| **CH6 First Drops** | drizzle-free variant: awnings stay rolled, Wick's run starts on schedule anyway | umbrellas invert once, comically | — | **canonical** | escalate straight into CH7 | replace rain sheen with early frost; Wick's lamps halo bigger |
| **CH7 Downpour** | crowd holds 0.40 and the Relight happens under a clear night sky (still works — the flash becomes a **firework**) | — | — | — | **canonical** | Relight in snow: each relit lamp catches falling flakes in its cone. Arguably better |
| **CH8 Festival** | **canonical** — this window is clear by design | — | — | rain would cut density to 0.22 and **cost the convergence**; if the storm ever overruns, **move the Merge/Lift/Stand earlier rather than shrink the crowd** | as above; braziers hiss and gutter under drips | early snow: the dance continues, flakes lit only by braziers (the CH8 exit beat, arriving early) |
| **CH9 Sweeping** | Broom's sweep against a clear predawn is cleaner and reads better | — | — | Broom pushes **water**, leaving a dark clean streak through the sheen | lightning silhouettes the litter line | **canonical** — he sweeps snow into a bank at the frame edge |
| **CH10 Vigil** | 3–4 figures instead of 2; Steam gets one more customer | — | — | rain on the kettle; Wick under an umbrella | — | **canonical** |
| **CH11 Payoff Dawn** | **canonical** | first leaves of the new day drift past the sleeping Sprig | early vent bubbles under the awnings | payoff poses under umbrellas; the two awnings still go up in unison | — | snow melting off the sleeping Bench Pair as the sun hits them |
| **CH12 Curtain Call** | **canonical** | ribbons stream right | vents punctuate the arms-up | arms up under umbrellas; the flares reflect in the wet stone (**best-looking variant**) | flash-lit curtain call | snow blowing right, with the ensemble, in the tailwind |

### 7b. Per-Regular weather responses (the cheap richness layer)

| Regular | Breeze | Thermal | Rain / wet | Storm | Snow / tailwind |
|---|---|---|---|---|---|
| **Wick** | flame flickers, he cups it | unaffected | cups the flame, walk slows 20% | **the Relight** | pole shouldered; lamp halos grow; **the Snuff** |
| **Sprig** | her lantern swings | grit under the crate | **leans the ladder as a lean-to and hides under it** | stays under the ladder | drags the ladder, leaving a 1px track in the snow |
| **Auntie Wok** | — | **steams a basket over a vent** | awning unfurls, **flare doubles** | **never closes** | still open; biggest plume in the whiteout |
| **Steam** | plume bends | **taps a vent for hot water** | best day of his life — a ring forms | one of four lit things | **the last stall in town** |
| **Char** | smoke leans | shields the coals from grit | **lids the coals; his smoke dies** | shut | hands over the banked coals, shivering |
| **Long Sister** | she sways with it | steps over the rock rings | dismounts, carries the stilts | dismounted through the whole storm | **refuses to dismount — the tallest thing in the whiteout** |
| **Bun** | **chases a leaf particle** | flinches at each eruption | under the kiosk, at the dry line | curled, watching | digs |
| **Bench Pair** | unmoved | **lift their feet without pausing the argument** | **one umbrella between them, tilted so it covers neither** | unmoved | **snow accumulates on their shoulders. Still arguing.** |
| **Broom** | sweeping against the leaves, losing | sweeping grit, losing | pushes water — a dark clean streak through the sheen | sheltered, watching his pile wash away | **pushes snow into a bank** |

---

## 8. Production notes

### NEW art (kept to four props + one data layer)

| # | Item | Size | Why it can't be a recast |
|---|---|---|---|
| **NEW-1** | **Sprig's ladder** — 3-rung silhouette; doubles as her rain lean-to and leaves a snow track | ~10×22 px | No existing prop reads as a ladder |
| **NEW-2** | **Stilt legs** — two 16px leg lines under a re-proportioned existing performer torso. **Contact y≈618, total height 36px → head y≈582** (clear of the y=560 ceiling by 22px) | +16px | The performer pool has no height outlier, and the outlier *is* the character |
| **NEW-3** | **The merged plume** — a two-source smoke column that bends and braids into one above the paired stalls | ~24×30 px, festival only | Extends the existing fire/smoke prop; the bend is the whole point of the beat |
| **NEW-4** | **Broom + litter pile** — a 16px broom prop and a pile that grows across the festival and is pushed off the right edge | ~16px + variable | The pile's *growth* is the storytelling; no existing prop accumulates |
| **NEW-5** | **Regular keys** *(data, not art)* | — | Nine reserved (family, variant, accent-colour, prop) tuples, excluded from the anonymous pools so a Regular can never be mistaken for traffic |

Everything else — Wick, Wok, Char, Steam, the Bench Pair, Bun, the crate, the bench, the awnings, the braziers, the lion and dragon, the wet sheen, the snow cover, the leaves, the rocks — is **existing families re-directed**.

### Readability guardrails (non-negotiable)

- **Motion budget: max 2 "big-motion" actors on screen at once** (stilt-walk, dance, lion, sweep). Everything else is a walk cycle or static.
- **Silhouette spacing: never two figures of the same height class within 24px.** Big/small/big alternation across the strip.
- **Fast-scroll valve:** whenever scroll > 1.3× base (rail ×2.5, snow tailwind ×1.4), near lane drops one density notch and goes **static poses only**.
- **Slow-mo (0.7×):** everything scales with world time — **except Steam's plume**, which keeps real time. One element out of sync makes the whole world feel held.
- **Power-up reskins (KFC, ghost, etc.):** the street **never** reskins. The Regulars are the game's continuity anchor; when Pip becomes a fry, they are what tells you it's still the same town.
- **Glow contract:** nothing on the street exceeds `NIGHT_GLOW_CAP 150` per channel. The Merge plume, the brightest permitted street element, gets its impact from **cooling its surroundings**, not from more luma.

### Variety & no-repetition rules

1. **Three-sighting rule.** A Regular must be seen ≥3 times before their payoff beat. The director tracks per-run sightings and force-spawns any Regular below quota before their deadline chapter.
2. **Anchored vs. floating: 40/60.** Roughly 40% of beats are *anchored* (always, at the same phase — the load-bearing story). 60% are *floating*, drawn from pools and placed by the director inside a window. Identity plus surprise.
3. **Seeded permutation, not randomness.** Each run seeds: (a) which of six Regulars gets the cold open, (b) one of three morning street-states (half-raised awnings / crates still stacked / bunting being strung), (c) which 4 of 8 micro-beats fill the market peak, (d) the crossing order in CH5, (e) the awning-wave order at dawn. **≥18 distinct openings** — the brief's "the opening must not feel identical" requirement, satisfied structurally rather than by noise.
4. **No anonymous design repeats within 40 s,** and never the same design twice on screen (existing rule — keep).
5. **2-of-3 floaters per window** (below), so a run never sees all of them. Replay reason, no extra art.
6. **Density hysteresis:** all crowd changes ramp over ≥3 s. Figures walk off once; nothing pops.
7. **Regulars are rationed:** max 2 on screen (3 only at the festival). Scarcity is what makes them read as characters instead of set dressing.
8. **One reserved slot per lane** for a Regular; the rest is anonymous traffic.

### Once-per-day special happenings

**Anchored (always fire, in window):**

| Special | Window | Beat |
|---|---|---|
| **The Refusal** | t 30–48 · φ .076–.122 | Three adults refuse Sprig's lantern; the third is Char |
| **The Hand** | t 148–158 · φ .376–.401 | Char sets a crate down for Sprig. *(The median player's payoff)* |
| **The Fall** | t 165–190 · φ .419–.483 | Long Sister topples; Wick catches the stilt with his lamp pole |
| **The Relight** | first flash after t 244.5 · φ ≥.621 | Nine lamps blanked, then relit one by one |
| **The Merge** | t 285–300 · φ .724–.762 | Two smoke columns braid into one |
| **The Lift** | t 288–305 · φ .732–.775 | Sprig raised to the highest hook; her lantern hangs under Pip's line |
| **The Standing** | t 290–312 · φ .737–.793 | The Bench Pair stand for the first time in 260 s |
| **The Great Sweep** | t 310–322 · φ .788–.818 | Broom pushes the festival off the right edge |

**Floating pool — draw 3 of 6 per run:**

| Floater | Window |
|---|---|
| **The Theft** — Bun steals a skewer; Char chases; both exit right | t 85–105 · φ .216–.267 |
| **The Sold-Out Cloth** — Wok drapes the wok and folds her arms; Char's queue doubles | t 95–125 · φ .241–.318 |
| **The Nap** — Wick asleep under the bench while the Bench Pair argue over him | t 112–128 · φ .285–.325 |
| **The Shared Awning** — Wok and Char under one awning, backs turned | t 200–225 · φ .508–.572 |
| **The Wet Dog** — Bun shakes; the near lane steps back in a ripple | t 262–275 · φ .666–.699 |
| **The Salute** — the umbrella-closing figure at a pickup pillar | t ~211 or ~232 |

### Contingencies

- **Player dies mid-beat.** Any special in progress aborts to the freeze rule. No special is allowed to be load-bearing for *comprehension* — every one reads as a complete image on its own.
- **Short runs (the common case).** The plan front-loads: all nine threads are introduced by t=112, and the first full plant→payoff closes at t=158, inside the median. A 40-second player still meets three people and watches one get refused three times.
- **Very long runs (multi-cycle).** Day 2+ runs the same nine on the same clock — that repetition **is** the point (they're *Regulars*), but the seeded layer re-rolls: different cold open, different floaters, different awning order, different crossing order in CH5.
- **Anchor drift.** If `RAIN_START_PILLAR`, `SNOW_START_PILLAR`, `CLOWN_START_PILLAR` or the thermal window are retuned, **every cue in this plan keys off `biome_phase`**, so the chapters travel with the weather automatically. The only hand-check needed: confirm the clear night gap (currently φ .694–.789) still exists and still contains CH8. **If that gap ever closes, the festival — not the storm — must move.**
- **Overrun risk on the convergence.** CH8's four payoffs occupy 24 s. If density or motion budget can't hold, cut in this order: the dragon, the dance, Broom's dance. **Never cut the Merge, the Lift, or the Standing** — those three are the plan.

---

## 9. Sources & inspiration

- **Silhouette readability at tiny sizes** — the 0.4-second recognition ceiling, and the rule that a good silhouette must read as one clear shape in a single colour, set the hard constraint that each Regular gets **one prop + one tint-locked accent** and nothing more: [Inviox — how long it takes to recognise a silhouette](https://www.invioxstudios.com/blog/how-long-it-takes-for-players-to-recognize-a-character-silhouette), [Salivity — importance of character silhouettes](https://salivity.github.io/game-development/article/importance-of-character-silhouettes-in-game-design), [Binus DKV — designing readable characters in motion](https://binus.ac.id/bandung/dkv/2025/11/04/the-power-of-silhouette-designing-readable-characters-in-motion/).
- **Tiny-sprite animation** — "at 16px, timing/anticipation/exaggeration are the entire toolkit; 2–4 colours per figure; squint until blurry and check the action still reads" directly produced the pose-only vocabulary (arms-up, head-tilt, freeze, turn-back) and the ban on facial or textual signalling: [Sprite-AI — 16×16 sprites](https://www.sprite-ai.art/guides/how-to-create-16x16-pixel-art), [WigglyPaint — making tiny characters feel alive](https://wigglypaint.com/blog/pixel-art-animation-guide/).
- **NPC tiering** — the distinction between characters who exist to *reveal stakes* versus background traffic underwrites the Regulars-vs-anonymous asymmetry and the "only Regulars acknowledge each other" crossing rule: [Game Developer — a narrative designer's approach to NPCs](https://www.gamedeveloper.com/design/a-narrative-designer-s-approach-to-npcs).
- **Ensemble dramaturgy** — Altman's model (interwoven threads bound by a shared space, converging on one event; ironic distance; overlapping action rather than sequenced scenes) is the structural template for the braid and for the festival as the single convergence point: [Ensemble cast](https://en.wikipedia.org/wiki/Ensemble_cast), [Script Angel on Linda Aronson's ensemble forms](https://scriptangel.com/writing-non-linear-flashback-and-ensemble-scripts-by-linda-aronson/), [Couch to 4K — the ensemble structure](https://checkplease.neocities.org/couchto4k/p/the-ensemble-structure-magnolia).
- **Scheduled-cast precedent** — *Majora's Mask*'s twenty tracked townsfolk on fixed three-day clocks, whose quests interlock by timing (Anju & Kafei), is the closest working model for "the drama is entirely in who is where, when": [Zelda Dungeon — Bombers' Notebook](https://www.zeldadungeon.net/wiki/Bombers%27_Notebook), [Zeldapedia](https://zelda-archive.fandom.com/wiki/Bombers%27_Notebook).
- **Historical texture** — Tang-era markets ran on regulated hours with distinct **dawn markets** ("grass market"/"dawn market") and, after night curfews eased, lantern-lit **night markets** described as *yanhuoqi* — "smoke, fire and steam." That documented **two-peak daily rhythm** (morning trade → lull → lantern-lit night trade) is what the crowd curve's morning peak at φ.075 and night peak at φ.740 are modelled on, and it's the source of the smoke-and-steam-as-light vocabulary used for Wok, Char and Steam: [ChineseLearning — morning markets](https://www.chineselearning.com/chinese-culture/vibrant-morning-markets-a-glimpse-into-china-s-urban-culture), [Night market (Wikipedia)](https://en.wikipedia.org/wiki/Night_market), [Korea Herald — "smoke, fire and steam"](https://www.koreaherald.com/article/10535521), [Hanfugirl — shopping havens of ancient China](https://hanfugirl.sg/2024/10/23/shopping-havens-of-ancient-china/). *Note: no source gave specific Tang opening/closing clock times, so the exact hour-by-hour timings above are dramatised, not historical.*
- **From the codebase (not research):** every phase and second in §2 was derived directly from `game/biome.py` (`_remap`, `DAY_HOLD_FRAC 0.51`, `NIGHT_BORROW_SECONDS 26.0`), `game/weather.py` (`_WIDTH_SCALE 0.8132`, the rain/snow/thermal curves), and `game/config.py` (`DAY_EXTRA_SECONDS 73.5`, the clown block, umbrella pillars, crowd/wet/snow constants, `CYCLE_FINALE_*`). The element catalogue and the existing `_POP_KEYS` / glow-contract conventions come from `docs/sidewalk_overhaul/README.md`.