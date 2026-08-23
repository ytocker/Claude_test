# THE MIRROR-PLAY
### A twelve-chapter street plan for one full Skybit day (393.5 s)

**Concept, in one sentence:** *A travelling shadow-and-acrobat company arrives on the sidewalk at dawn, spends the whole day raising a stage and rehearsing the play in scattered fragments, and after dark performs — in silhouette, wordlessly, under the real bird — the story of the very flight the player is flying.*

---

## 1. Concept

### Candidates considered (all inside the assigned territory)

**A. "The Red Boat Company."** A named itinerant troupe unloads at dawn, builds a bamboo stage, performs at night, strikes and moves on. Strong worldbuilding, real historical grounding — but on its own it's a *logistics* story: it tells you the troupe is busy, not that the troupe is about *you*.

**B. "The Rehearsal Assembles."** The troupe rehearses fragments all day in the wrong order — a wing here, a leap there, a hoop-dive, a mask flip. At night the fragments snap together into one continuous play and the player retro-recognises every daytime scrap. Great payoff shape, weak first 60 seconds (fragments read as noise until you know what they're fragments *of*).

**C. THE CHOSEN — A ∪ B, spined on the mirror.** The company's workday gives the day its physical build (something visibly, monotonically *becomes*), the fragment-rehearsal gives it its narrative payoff, and the mirror gives it its point: at night a lit white screen carries a shadow bird whose **vertical position is a smoothed read of Pip's own y**. The street is not decorating the flight. The street is *staging* it.

### Why this fits Skybit specifically

- **It survives the median run.** 50% of runs end at ~156 s — inside Chapter VI, before a single note of the show is played. A "build toward tonight" spine is the only structure where seeing *only the preparation* is still a complete, satisfying, hook-planting experience. The player who dies at 156 s leaves thinking *"something is happening in that town tonight."* Night stays a reward, and the reward is now specific rather than generic.
- **It solves the endless-scroller problem honestly.** You cannot show one stage being built when the street never stops moving. So the governing fiction is: **the street is one company's workday, sampled at many points along the road.** Every troupe sighting inside a chapter shows the *same stage of work*. The build reads as time passing, not as travel.
- **It uses the engine's existing lane-cull as a feature.** `_char_x_ok` culls *characters* out of the bird lane (x≈48–188) and pillar lane (x≈212–320), while *structures* (kiosk-class) scroll through freely. That means: the screen is drawn everywhere; the puppeteers behind it are automatically invisible half the time. The shadow play works **because** the operators cull out. Free magic.
- **It obeys the coin contract by area, not intensity.** The night's second-brightest thing is a *large dim* rectangle (~44×30 px at ≤132 luma), not a small bright one. It wins the eye without ever threatening the coin at ~206.

---

## 2. At a glance

| | |
|---|---|
| **Duration** | `CYCLE_SECONDS = 393.5 s` (one phase 0→1), + ~9 s of finale bleeding past the wrap |
| **Surface** | Sidewalk band y 560–640, ground line y=595, feet at y=594. **Nothing above y=560, ever.** |
| **Scroll** | 160 px/s base (×1.40 at snow-squall peak; +8 px/s per completed day) |
| **Scenario slot period** | 640 world-px ≈ **4.0 s** between scene slots at base scroll |
| **Cast palette** | 50 pedestrians · 6 kids · 6 elders · 7 vendors · 9 animals · 8 busker acts (A1–A8) · 5 food stalls · 30 greenery · 15 props across 5 pools · lion + dragon + banner + brazier festival specials |
| **New set pieces** | **4 NEW + 1 recolour** (listed in §8) |
| **Audience** | One player, phone, portrait, 360×640, playing a one-button game. The street is *peripheral vision only.* |

### Real anchors extracted from the repo

`DAY_EXTRA_SECONDS = 73.5`, `_BASE_CYCLE = 320`, `CYCLE_SECONDS = 393.5`, `DAY_HOLD_FRAC = 0.51`, `NIGHT_BORROW_SECONDS = 26.0`. Remapping every keyframe through `_remap` gives:

| Keyframe | phase (remapped) | seconds |
|---|---|---|
| DAY | 0.0000 | 0.0 |
| *(DAY-hold ends, golden fade begins)* | 0.1575 | **62.0** |
| GOLDEN HOUR | 0.3088 | **121.5** |
| SUNSET | 0.4155 | **163.5** |
| DUSK | 0.5375 | **211.5** |
| NIGHT | 0.6442 | **253.5** |
| PREDAWN | 0.8323 | **327.5** |
| SUNRISE | 0.9238 | **363.5** |
| DAY (wrap) | 1.0000 | **393.5** |

Weather + event anchors (computed from `weather._phase_for_pillar` with `BIRD_X=90`, plateau 5 / ramp 25, and the `_WIDTH_SCALE = 320/393.5 = 0.8132` duration-preserving scale):

| Event | phase | seconds |
|---|---|---|
| Newbie plateau (5 pillars) | 0 – 0.040 | 0 – **15.9** |
| `_run_fill` cast ramp-in | — | 0 – **7.0** |
| Onboarding ramp complete (pillar 25) | 0.150 | **58.8** |
| Calm breeze / drifting leaves (`_bump(p, 0.18, 0.10)`) | 0.080 – 0.280, peak 0.180 | **31.5 – 110**, peak **70.8** |
| Thermal rocks scatter | 0.127 – 0.285 | **50 – 112** |
| Thermal **geysers** (≥0.35) | ~0.173 – 0.269 | **~68 – 106** |
| Thermal peak | 0.244 | **96** |
| **Genie lamp** (pillar 50 = `pillar_for_phase(peak)+3`) — also `LATE_GAME_PILLAR` | 0.261 | **102.6** |
| **Clown gauntlet** block opens (pillar 65, 2 phantom pre-clear) | 0.327 | **~126 – 128.8** |
| Clown block cleared (roll-dependent, latest ~pillar 90) | ≤0.439 | **~142 – 172** |
| **Rain drizzle start** (pillar 100) | 0.483 | **190.0** |
| Wet paving begins (rain ≥ 0.18) | ~0.526 | **~207** |
| Umbrella power-ups (pillars 112 / 124) | 0.537 / 0.590 | **211 / 232** |
| Drizzle peak | 0.564 | **222.1** |
| **Thunderstorm peak** | 0.630 | **247.7** |
| Lightning window | 0.621 – 0.695 | **244.5 – 273.3** |
| Rain ends / paving dries by | 0.695 / ~0.737 | **273.3 / ~290** |
| Snow squall first flakes (storm > 0.10) | 0.786 | **309.3** |
| Snow builds on Pip (≥0.45) + tailwind bites | 0.812 | **319.6** |
| **Snow peak** (scroll ×1.40) | 0.871 | **342.9** |
| Snow defrost begins | 0.911 | **358.6** |
| Snow wash clears | 0.977 | **384.5** |
| **Cycle wrap → 3 forced coin-rush pillars, chest on #2** | 1.000 → 0.000 | **393.5 → ~402** |
| Coin rush (every 15th pillar) | — | ~40, 68, 94, 120, 146, 173, 199, 225, 251, 278, 304, 330, 356, 383 |

### Assumptions I made (stated, not hidden)

1. **Seconds/phase are the ground truth, not pillar numbers.** The promenade reads `phase` and `t`; the clown warren's 72-px spacing means real elapsed time at a given pillar drifts from `_phase_for_pillar`'s normal-dwell model. Every chapter boundary below is keyed to a **biome keyframe or a weather intensity signal**, so the plan survives retuning; the second-marks are the *current* resolution of those keys.
2. **The die roll (10–25 warren towers) makes Chapter V elastic** (~14–26 s). Chapter V is authored as a *held pose*, which is the only kind of beat that stretches gracefully.
3. **Sound is an optional layer.** Every beat must read on silhouette, colour, motion, grouping and light alone. The six proposed cues in §7 are additive, need `sound-designer` work, and must route through `audio.py`'s dual backend (never `pygame.mixer` on web).
4. **The existing crowd curve `_POP_KEYS` is replaced** (§7). Existing shelter-figures, umbrella, latched-slot and no-repeat systems are reused as-is.
5. The lion/dragon "festival specials" already gated to night become **this troupe's marquee** — no new art, new meaning.

---

## 3. The company (cast recasting — no new sprite families)

The whole troupe is drawn from existing pools. Their **company colourway** is rolled once per run and persists all day, tinting banners, screen border, lion, and cart: *crimson & bone* / *indigo & gold* / *jade & ash*.

| Role | Drawn from | What they do |
|---|---|---|
| **The Master** (calls every cue, dots the lion's eyes) | elders ×6 — one variant locked per run | Points, holds the brush, stands still while others move |
| **Lead — the Bird** | A7 fan/ribbon dancer | Carries the rod-bird; is the play's protagonist |
| **Lead — the Rival** | A8 mask-changer (bian-lian) | The mask-flip is the day's "something changed" verb |
| **The Crane** | A3 stilt-walker | Tallest silhouette; the antagonist bird |
| **Percussion** | A2 musician (seated, `arms='drum'`) | The company's pulse; every cue lands on his stroke |
| **Tumblers ×2–4** | A1 juggler + pedestrian variants re-posed | Hoop-dive, pole-climb, plate-spin; the acrobatic layer |
| **The Scribe** | A4 calligrapher | Paints the playbill banner; his brush = the eye-dotting brush |
| **The Cook** | A5 tea-pourer + food stalls | Feeds the company; at night, feeds the audience |
| **The Ritualist** | A6 fortune-teller | Runs the Libation; tends the brazier |
| **Apprentices ×2–3** | kids ×6 | Carry, fetch, mimic the leads badly, sit front row at night |
| **Riggers / hands** | pedestrians ×50, re-posed | Haul rope, lash bamboo, stack crates |
| **The Lion / The Dragon** | existing `perf_lion_dance` / `perf_dragon_dance` | Inert props by day; awakened at the Libation |
| **The audience** | pedestrians, vendors, animals | Pass → pause → gather → sit |

**The rod-bird motif** — a single 9×7 px three-point silhouette (body + two swept wings) — is the plan's through-line object *as a motif, not as a tracked prop.* It appears **seven times** across the day in seven different materials: lashed to the cart, a rehearsal rod-puppet, a daylight test-shadow, a kite, the shadow-play lead, a snow-battered rag on a pole, and the shape of the company's final bow. That repetition is the wayfinding.

---

## 4. Master timeline

Format per chapter: **time / phase**, target crowd density, roster deck, then timed beats, then Signature · Sky-tie · Light & sound · *So the player feels…*

---

### CHAPTER I — THE ROAD IN
**0.0 – 19.0 s · phase 0.000 – 0.048 · pop 0.12 → 0.30 · deck: {arrival}**
*Hard constraint: newbie plateau + gauntlet-class calm. **Max 3 figures on screen.** All content x < 46 or x 150–200.*

| t | phase | Beat |
|---|---|---|
| 0.0–3.0 | .000–.008 | **Bare road.** Wet-dark paving, one shuttered kiosk, two greenery beds. Nothing moves but the scroll. `_run_fill` is at zero and that is *correct* — the day starts empty on purpose. |
| 3.0–7.0 | .008–.018 | **The arrival vignette** (one of four, rolled per run — see §6-V1): **A** a two-wheel cart rolls in from the left, tarpaulin lashed; **B** a bundle of bamboo poles thumps off a tailgate and rolls; **C** the drum comes off first and one hand strikes it, once, to test it; **D** four figures carry a long white roll shoulder-high like a body. |
| 7.0–13.0 | .018–.033 | One figure drops off the cart and walks alongside it. A dog joins from a doorway. The tarpaulin lifts a hand's width in the scroll-wind and shows, for ~1 s, a crimson edge and the corner of the **rod-bird** lashed to the load. *That is the promise, planted in the first ten seconds.* |
| 13.0–19.0 | .033–.048 | The cart passes a shuttered food stall; the vendor pushes the shutter up halfway. Road goes bare again for the last ~4 s. The morning has not started. |

- **Signature:** the tarpaulin corner lifting on a red-and-gold wing shape.
- **Sky tie:** solid DAY palette (holding until 62 s), cyan sky, no weather. The street's emptiness is the sky's stillness on the ground.
- **Light & sound:** flat morning key, no glow (`_lit_intensity = 0`), string lights on their 0.40 daylight floor. One drum thud in vignette C; otherwise the run's own flap.
- ***So the player feels…*** *nothing is happening yet — and something just arrived.*

---

### CHAPTER II — UNLASHING
**19.0 – 50.0 s · phase 0.048 – 0.127 · pop 0.30 → 0.62 · deck: {unload, market, cook, apprentice, bystander}**

| t | phase | Beat |
|---|---|---|
| 19.0–26.0 | .048–.066 | **The town wakes into the troupe's mess.** Two food stalls open (steamer breathing, cauldron). Between them, crates coming off the cart in a chain of three hands. Vendors work *around* the troupe, faintly annoyed. |
| 26.0–34.0 | .066–.086 | **Bamboo comes out.** Poles laid on the ground in tidy parallel rows — a strong, instantly readable graphic: 6–8 horizontal lines on the paving where yesterday there were none. The Master walks the row, pointing. Nobody's built anything yet. |
| 34.0–41.0 | .086–.104 | **Rope and lashing.** Riggers coil rope; an apprentice is buried under a coil twice his size and staggers. First dog-follows-the-cart gag. Pigeons on the crates. |
| 41.0–50.0 | .104–.127 | **Breakfast.** The Cook's tea-pour, the company squatting in a ring of six around a low pot. First deliberate *low-motion* beat of the day: a group that is sitting still while the world scrolls past them is more legible than a group that's busy. Coin rush at ~40 s: the drummer, mid-bowl, taps the rim twice on the rush's downbeat. |

- **Signature:** the row of bamboo poles laid out on the paving — geometry appearing where there was none.
- **Sky tie:** DAY holds solid; no weather. Onboarding ramp still tightening under the player, so the street stays *readable-busy*, never dense.
- **Light & sound:** hard noon-ish key, saturated tan/green, steam plumes as the only vertical motion. Low frame-drum, irregular, like someone idly practising.
- ***So the player feels…*** *a working morning; strangers have moved in.*

---

### CHAPTER III — RAISING THE POLES
**50.0 – 96.0 s · phase 0.127 – 0.244 · pop 0.62 → 0.70 → 0.48 · deck: {raise, lash, market, leaf, gawker, apprentice}**
*Coincides exactly with the thermal rock-scatter (50→112 s) and the calm-breeze leaf drift (peaks 70.8 s).*

| t | phase | Beat |
|---|---|---|
| 50.0–58.0 | .127–.147 | **Sinter appears.** Pale thermal rocks scatter across the near lane; the troupe simply *works around them* — a rigger kicks one aside, a vendor sets a crate on one. The street treats the geology as furniture, which sells it as real. |
| 58.0–66.0 | .147–.168 | **First uprights.** Two poles stand, guyed with rope, four hands on lines. The stage exists as a *silhouette of two verticals* — the minimum readable "something is being made." Onboarding ramp completes ~58.8 s; the street's busiest daytime density arrives with it. |
| 66.0–74.0 | .168–.190 | 🌟 **SPECIAL S1 — THE POLE RAISE.** A whole scaffold bay swings from horizontal to vertical over ~2.5 s on four rope-lines, figures leaning back at 30°. Peak leaf-drift (70.8 s) puts amber leaves through the raise. Meanwhile the **first geysers** (~68 s) start lifting Pip. The ground crew below hauls *down* while the bird above is pushed *up*: a single frame containing both vectors. |
| 74.0–84.0 | .190–.213 | **Crossbeams.** The frame gets its horizontals. Two apprentices lash the joints; a tumbler goes up a pole hand-over-hand (existing pole-climb read) to reach a high knot, then slides down. Gawkers gather — 3–5 civilians standing with their backs to us, watching the build. *(Backs-to-camera crowds are the cheapest legible "audience" grouping there is, and we'll reuse the pose all night.)* |
| 84.0–96.0 | .213–.244 | **The frame closes.** A recognisable stage skeleton passes: two bays, a lintel, no roof, no cloth. Second coin rush ~94 s. Golden-hour fade has begun on the sky (from 62 s); the raw bamboo starts going honey-coloured. Geysers at peak intensity (96 s). |

- **Signature:** S1, the bay swinging vertical against a rising geyser column.
- **Sky tie:** thermals lift Pip; on the ground, everything is being lifted too. The day's one visual pun, used once.
- **Light & sound:** sky drifting cyan→warm; leaves crossing the whole screen. Rope-creak, wood-knock, a cymbal *tap* (not a crash) at the moment the bay locks vertical.
- ***So the player feels…*** *they're building something, and I want to know what.*

---

### CHAPTER IV — FRAGMENTS
**96.0 – 128.5 s · phase 0.244 – 0.327 · pop 0.48 → 0.22 → 0.30 · deck: {rehearse, cloth, quiet, gawker}**
*Contains the genie lamp (102.6 s), the golden-hour keyframe (121.5 s), and the day's first authored **quiet valley** (110–125 s).*

| t | phase | Beat |
|---|---|---|
| 96.0–104.0 | .244–.264 | **Rehearsal, out of order.** In three consecutive slots: a tumbler dives through a hoop held by two others; the ribbon dancer sweeps one arc and stops; the mask-changer flips one mask and turns away. **No fragment is finished.** Each is 1.5–2 s and cut off by the scroll. At 102.6 s the **genie lamp** appears in the sky — the Ritualist, mid-fragment, stops and bows toward it. |
| 104.0–112.0 | .264–.285 | 🌟 **SPECIAL S2 — THE SCREEN TEST.** The white cloth is hoisted into the frame and pulled taut by four hands. For ~2 s a single **black rod-bird silhouette** flicks left-to-right across it — in *daylight*, so it reads as a shape, not a glow. Nobody watches. It's a technician checking a rig. Geysers fade out (~106 s) and the rocks thin. |
| 112.0–125.0 | .285–.318 | **QUIET VALLEY 1.** Deliberate near-empty road: the frame passes finished-but-bare, cloth furled to one side, one figure asleep against a pole (existing napper). Two greenery beds, one dog, nothing else. **13 seconds of almost nothing, on purpose** — the eye needs to rest before the clown block, and the contrast is what makes Chapter V's stillness read as *tension* instead of *emptiness*. |
| 125.0–128.5 | .318–.327 | The clown's 2 phantom pre-clear pillars. On the street: heads start turning right. Nobody's stopped working yet, but three figures are looking. |

- **Signature:** S2 — the shadow bird, in daylight, seen by no one but the player.
- **Sky tie:** genie lamp gets a bow; geysers subside as the rehearsal winds down; golden hour arrives on the last beat.
- **Light & sound:** amber creeping in; the white cloth is now the brightest object in the band — but it's *daylight-white* (unlit fill), well under the coin. Drum falls silent through the valley.
- ***So the player feels…*** *I just saw something I don't understand yet.*

---

### CHAPTER V — THE STREET LOOKS UP
**128.5 – ~155.0 s (elastic, 14–26 s by die roll) · phase 0.327 – 0.394 · pop 0.30 · deck: {frozen}**
*Hard constraint: the clown gauntlet demands a calm street. This chapter's solution is that **stillness is the drama**.*

| t | phase | Beat |
|---|---|---|
| 128.5–132.0 | .327–.335 | **The die reveal.** Every figure on the street stops mid-action and turns to face right-and-up. Poses freeze in whatever they were doing — a rope half-hauled, a bowl half-raised. **Motion drops to near-zero while density stays constant.** |
| 132.0–~148 | .335–.376 | **The warren.** The held pose *continues*, unbroken, for the entire gauntlet. The only movement in the band: the scroll itself, steam from the stall, and — once — the Master's head tracking right to left as Pip passes him. That single tracking head is worth more than fifty animated figures. If the roll is long, the pose simply holds longer; nothing needs re-timing. |
| ~148–155 | .376–.394 | **Release.** 1.5 s after Pip clears the last warren tower, a ripple of raised arms travels left-to-right **at exactly scroll speed**, so it reads as a wave *following Pip down the street*. Then everyone returns to work. The drum, silent for 20+ seconds, comes back in on a single hard stroke. |

- **Signature:** the tracking head. Then the scroll-speed arm-wave.
- **Sky tie:** the gauntlet is the day's first genuine peril; the street's answer is to become an audience. This is where the tournament-awareness layer stops being subtext.
- **Light & sound:** full golden hour; long amber rake across the paving. Total ambient silence for the gauntlet — the *absence* of the drum is the cue. One stroke on release.
- ***So the player feels…*** *everyone down there is watching me.*

---

### CHAPTER VI — DRESSING
**155.0 – 190.0 s · phase 0.394 – 0.483 · pop 0.42 → 0.68 · deck: {dress, kite, rope, gather, vendor}**
*SUNSET keyframe at 163.5 s. **The median run (~156 s) dies at the top of this chapter** — so this chapter carries the hook.*

| t | phase | Beat |
|---|---|---|
| 155.0–163.5 | .394–.415 | **Costume and mask.** Trunks open on the paving; a mask is lifted out and held up to the light; the lion's head sits on a crate, eyes blank, facing the road. Blank lion eyes are the single strongest "not ready yet" image available — and they set up the Libation 90 seconds later. |
| 163.5–172.0 | .415–.437 | 🌟 **SPECIAL S4 — THE KITE.** A figure walks backwards up the street paying out line; the **rod-bird kite** lifts off the near lane, rises to y≈562 (ceiling-legal), and holds there, small, line taut at a steep angle, drifting for ~6 s. It never leaves the band; it reads as ascending because the line steepens and the shape shrinks by 30%. A bamboo whistle tone rides with it. **The motif's fourth appearance, and the first one that flies.** |
| 172.0–181.0 | .437–.462 | 🌟 **SPECIAL S5 — THE ROPE-WALK.** An acrobat crosses a rope strung between two stage poles, arms wide, in flat silhouette against the sunset sky. Rose stone, orange horizon, one black figure balancing. ~3 s of screen crossing. Lamp posts kindle behind him (`_lit_intensity ≈ 0.40`). |
| 181.0–190.0 | .462–.483 | **Front of house.** The Scribe paints the playbill banner (existing calligrapher + banner prop, company colourway). Benches are dragged into rows facing the stage. Vendors reposition, backs to us. Density climbs hard: the audience is arriving. Third-from-last dry beat of the day. |

- **Signature:** S5 — the rope-walk against the sunset.
- **Sky tie:** sunset palette does the heavy lifting; the lamps' first kindling is timed to the rope-walk so the acrobat crosses into light.
- **Light & sound:** rose/lavender stone, string lights climbing off the day floor, lamps at 0.40. Kite whistle; a tuning suona figure, two notes, unresolved.
- ***So the player feels…*** *tonight there is going to be a show, and I'm going to miss it.* **(This is the retry hook. It is the most valuable single sentence in the plan.)**

---

### CHAPTER VII — THE RUINED DRESS REHEARSAL
**190.0 – 253.5 s · phase 0.483 – 0.644 · dry-pop 0.68 → 0.80, weather-multiplied to ~0.18 at peak · deck: {rain, shelter, salvage, storm}**
*Drizzle 190 → storm peak 247.7 → NIGHT keyframe 253.5. Lightning from 244.5. Umbrella power-ups at 211 and 232. DUSK keyframe 211.5.*

| t | phase | Beat |
|---|---|---|
| 190.0–200.0 | .483–.508 | **First drops.** The dress rehearsal has already started — the ribbon dancer and the Crane are running a full sequence on the stage. Drizzle begins. Nobody stops. Two civilians in the back row open umbrellas (`WEATHER_UMBRELLA_RAIN_AT = 0.12`). |
| 200.0–211.5 | .508–.537 | **The audience thins, the company doesn't.** Civilian slots gate off once, cleanly, off-screen (no flicker); shelter-figures tuck under the kiosk awning and lamp posts. The rehearsal continues in the rain, now for an audience of six. Paving glazes (`wetness` rising from ~207 s) and starts throwing dim inverted lamp-reflections. Umbrella power-up at 211.5 — a hand in the far lane raises an umbrella on the same beat. |
| 211.5–222.0 | .537–.564 | **Salvage begins.** The Master calls it: crates go under the stage deck, the mask trunk gets a tarp, the drum is turned face-down. The stage stands in a thinning street. Drizzle peaks at 222. |
| 222.0–244.5 | .564–.621 | **Downpour.** Rain to full. Crowd factor bottoms toward 0.22. Deep slate rain, wet-black paving, a single lit lamp per screen. On the stage: **two figures**, the Master and the Lead, arguing in gesture — the Master pointing at the sky, the Lead pointing at the stage. No faces, no text; just two opposed arm-lines. Umbrella power-up at 232 s. |
| 244.5–248.0 | .621–.630 | 🌟 **SPECIAL S6 — THE SCREEN TEARS LOOSE.** On the **first lightning flash**, the white cloth rips from one top corner and billows sideways across the frame. Six figures run in and haul it down hand-over-hand. Flash 2 catches them mid-haul, all-black, arms overhead. **The loudest non-Pip image of the entire day, and it happens at the exact bottom of the story.** |
| 248.0–253.5 | .630–.644 | **After.** Storm past its peak. The frame stands bare and wet, cloth bundled at its foot, a single brazier guttering. The street is as close to empty as it has been since 0 s. Rain still falling. **Nobody has left.** |

- **Signature:** S6 — the cloth billowing white against a black street on a lightning flash.
- **Sky tie:** the thunderstorm is the crisis; the umbrella power-ups are diegetically supplied by an audience that came prepared; the storm's peak and the story's low point coincide *by construction*.
- **Light & sound:** existing lightning flash; wet-paving sheen doubles the lamp count by reflection; palette collapses toward dusk lavender then night blue. Thunder (existing). Drum: silent from 222 s.
- ***So the player feels…*** *they're going to lose the show.*

---

### CHAPTER VIII — LIBATION
**253.5 – 276.0 s · phase 0.644 – 0.701 · dry-pop 0.86 → 1.00, weather-lifting as rain clears at 273 · deck: {libation, return, awaken}**
*Named for the first of the three parts of temple-fair opera: **Libation → Main Play → Additional Play**. This is the Libation.*

| t | phase | Beat |
|---|---|---|
| 253.5–261.0 | .644–.663 | **The hush.** Full NIGHT palette arrives; rain fading. The company re-hangs the screen in near-total quiet — four figures, a ladder, deliberate slow motion. No audience yet. This is the deliberate **breath before the peak**: the story's lowest energy sits 20 s after its lowest point, not on top of it. |
| 261.0–268.0 | .663–.681 | **They come back.** Civilians return in ones and twos as the rain drops under 0.3 — walking *in from the right*, i.e. toward Pip's oncoming direction, so the audience assembles against the scroll and reads as gathering rather than passing. Benches refilled. The Cook relights the stall. Fourth-from-last coin rush at ~251 s already passed; the next at ~278 lands inside the Main Play. |
| 268.0–274.0 | .681–.696 | 🌟 **SPECIAL S3 — THE EYE-DOTTING.** The Master lifts the Scribe's brush and touches the lion's head: **horn, ears, mouth, then the eyes.** The blank eyes we saw on a crate at 155 s go bright. A red ribbon is tied to the horn. Then the lion's head *lifts* — the first frame in which it moves on its own. Rain hits zero at 273.3. |
| 274.0–276.0 | .696–.701 | **The lamp goes in.** A single flame is carried behind the screen and set down. **The screen lights from within** — a large, low-luma warm rectangle (≤132 luma, area-brightness rule) in a cool blue-black street. The whole band re-reads in one frame. |

- **Signature:** S3 — the eyes going bright. The plan's best 1.5 seconds.
- **Sky tie:** the rain's end and the lion's awakening are the same beat. The screen lights the instant the sky finishes going black.
- **Light & sound:** warm-vs-cool takes over completely: amber screen + amber brazier + capped lantern garland against moonlit blue stone. Suona: the two-note figure from 163 s finally *resolves*. Then the drum, back, on a slow four.
- ***So the player feels…*** *they saved it. It's starting.*

---

### CHAPTER IX — THE MAIN PLAY
**276.0 – 309.0 s · phase 0.701 – 0.786 · pop 1.00 → 0.94 → 0.34 · deck: {play, audience, marquee, empty}**
*The night's crowd peak. The emotional peak of the whole day.*

| t | phase | Beat |
|---|---|---|
| 276.0–284.0 | .701–.722 | **The mirror opens.** On the lit screen: two black vertical bars and a **rod-bird silhouette threading between them.** The shadow bird's y is a heavily smoothed (τ ≈ 0.6 s), clamped read of **Pip's own y**, remapped into the screen's 30-px height. When the player climbs, the shadow climbs. Nothing announces this. Some players will never notice. The ones who do will tell someone. *(Fail-safe: if Pip is dead or off-clamp, the shadow flies a canned loop — it must never look broken.)* |
| 284.0–292.0 | .722–.742 | **Full house.** Densest street of the cycle: seated rows, standing backs, kids on shoulders, dogs under benches, the Cook working a queue, braziers. **All of it faces away from us, into the stage.** A crowd of backs is calm to look at and instantly readable as attention — it will not fight the pillars for the player's eye. Coin rush ~278 s: the drummer lands the downbeat and the shadow bird **dives** on it. |
| 292.0–300.0 | .742–.762 | **The marquee.** The existing lion and dragon acts take the near lane in front of the stage — the play's spectacle movement. The Crane (stilt) enters as the rival. On the screen behind them, the shadow bird is chased. Two layers of the same story at two scales, in one frame. |
| 300.0–305.0 | .762–.775 | **Applause and disperse.** Arms up in a scroll-speed ripple (the Chapter V wave, reused as the play's ovation — planted, paid off). Rows break. Vendors move. |
| 305.0–309.0 | .775–.786 | 🌟 **SPECIAL S8 — THE EMPTY STAGE.** Once per day, exactly here: the stage passes **lit, screen glowing, and completely deserted.** No performer, no audience, no motion but a slight breathing of the cloth. Four seconds. **This is the quietest and most memorable image in the plan**, and it costs one boolean. It also functions as QUIET VALLEY 2 — the room to breathe before the climax. |

- **Signature:** the shadow bird tracking the player's altitude. And then, five minutes later, an empty stage.
- **Sky tie:** deep night, `star_alpha 235`; the coin still the brightest thing by a wide margin; screen area does the work.
- **Light & sound:** the day's only fully-lit band. Warm amber pool centred on the stage, falling off to cool blue at the screen edges. Full percussion + cymbal on the marquee entrance, then **nothing at all** for the empty stage.
- ***So the player feels…*** *that's me. …and then: oh.*

---

### CHAPTER X — THE ADDITIONAL PLAY (performed in a blizzard)
**309.0 – 363.5 s · phase 0.786 – 0.924 · dry-pop 0.62 → 0.70, weather-multiplied toward 0.06 (troupe exempt) · deck: {snow, endure, additional}**
*Snow first flakes 309.3 · hard snow + tailwind 319.6 · PREDAWN keyframe 327.5 · peak 342.9 (scroll ×1.40) · defrost 358.6.*

| t | phase | Beat |
|---|---|---|
| 309.0–319.5 | .786–.812 | **First flakes.** The audience, still seated, starts pulling collars up. The company begins the **Additional Play** — the third part, the encore. On the screen: a **dragon silhouette** rising from the bottom edge. Flakes drift past the lit screen and are visible *as flakes* only where they cross the light. |
| 319.5–327.5 | .812–.832 | **The squall bites.** Tailwind pushes Pip; the crowd factor collapses toward 0.06. Civilians blow off screen — but the **troupe is exempt (floor 0.55)**. Weather removes the audience and never the company. Banners snap horizontal. The rod-bird kite from Chapter VI reappears, now a **torn rag on a pole**, thrashing. |
| 327.5–343.0 | .832–.871 | **They play through it.** Predawn cold-pink palette under a white wash. On the stage: the lion dances for **eleven people**. Two riggers hang bodily off the guy-ropes to keep the frame standing, one at each end of the screen, mirrored — a perfectly symmetrical human bracket. Snow accumulates on the deck (`snow_cover` ground state), on shoulders, on the lion's back. **Peak at 342.9:** everything leans right at once — banners, rope, cloth, snow, Pip. One vector, whole screen. |
| 343.0–358.5 | .871–.911 | **Endurance.** The squall holds. The screen is still lit and the shadow bird is still flying — now barely visible through the wash. The drum is the only steady thing. Coin rush ~356 s under the tailwind: the fastest, brightest ten seconds of the day. |
| 358.5–363.5 | .911–.924 | **It breaks.** Snow begins to shed. The lion's head goes down. The riggers let go of the ropes one at a time. Sky lifting toward sunrise. |

- **Signature:** the two mirrored riggers hanging off the guy-ropes at the squall's peak — the whole company reduced to two bodies holding up a piece of cloth.
- **Sky tie:** the tailwind that carries Pip is the same wind trying to take the stage down. Pip is *helped* by the thing that is *hurting them*. Nobody has to say that.
- **Light & sound:** cold blue-white wash over warm amber — the day's strongest colour opposition. Kite whistle returns, pitched down and unsteady. Drum: slow, unbroken, never stops.
- ***So the player feels…*** *they're not going to stop. Neither am I.*

---

### CHAPTER XI — STRIKE AT FIRST LIGHT
**363.5 – 393.5 s · phase 0.924 – 1.000 · pop 0.40 → 0.54 → 0.16 · deck: {strike, bow}**
*SUNRISE keyframe 363.5 · snow wash fully clear 384.5 · wrap 393.5.*

| t | phase | Beat |
|---|---|---|
| 363.5–374.0 | .924–.951 | **Strike.** Peach sunrise light on cool snow-covered paving — the best-looking five seconds of palette the engine produces all cycle. The screen comes down and is rolled by four hands, exactly reversing the 104 s hoist. Poles unlashed. Crates stacked. |
| 374.0–384.5 | .951–.978 | **The takings.** The Cook hands out bowls. The audience that stayed — maybe eight — stands about, not leaving. The lion's head is set on the cart facing back down the road, red ribbon still on the horn. Snow melting off the deck in visible steps. Last coin rush ~383 s. |
| 384.5–390.0 | .978–.992 | **They line up.** Every troupe figure currently on screen stops moving and squares to face **right-and-up**, along Pip's flight line. Held. Two full seconds of an entire street standing still and facing the same way. |
| 390.0–393.5 | .992–1.000 | 🌟 **SPECIAL S7 — THE BOW.** They bow. Once. Deep. The bow propagates left-to-right **at exactly scroll speed**, so from the player's frame it is one continuous wave travelling *with* them down the whole length of the street. Full sunrise on the sandstone. The rod-bird motif's seventh and last appearance: the shape their bent backs and outflung arms make is the shape of the bird. |

- **Signature:** S7, the scroll-speed bow. Same mechanic as the clown-release wave (128 s) and the ovation (300 s), used a third time and now meaning something completely different. **Plant, echo, pay off.**
- **Sky tie:** the day's finish and the sun's arrival are the same event.
- **Light & sound:** warm horizon (255,235,180) across a still-cool street; lamps guttering out one by one behind the bow. Suona, full phrase, resolved. Then one cymbal, allowed to ring out.
- ***So the player feels…*** *that was for me.*

---

### CHAPTER XII — THE COMPANY BOX
**393.5 → ~402 s · the cycle wrap + 3 forced coin-rush pillars, chest on pillar #2**
*Note the real mechanic: `CYCLE_FINALE_PHASE_HI/LO` detects the rollover, so **the chest is actually claimed in the first seconds of the new day.** The finale is a dawn event. The plan leans into that rather than fighting it.*

| t | phase | Beat |
|---|---|---|
| 393.5–396.5 | .000–.008 | **Rush pillar 1.** Palette snaps to fresh DAY. The street would normally go bare here — instead the **finale overlay holds the company on screen**, still bowed, for all three rush pillars. Coins pour. |
| 396.5–399.5 | .008–.016 | **Rush pillar 2 — THE CHEST.** As Pip takes the treasure box (+100, `TREASURE_BOX_ANIM_T = 1.5` of lid-pop and halo), the street's answer, in the same 1.5 s: the company **straightens out of the bow all at once** and every arm goes up. The cart's lid closes on the crates. The takings are in. |
| 399.5–402.0 | .016–.024 | **Rush pillar 3 — they go.** The cart rolls off right. The lion's head faces backward down the road at the player as it leaves. The rod-bird kite goes up off the departing cart, one last time, small. Behind it: **bare road**, exactly as at t=0. |
| 402.0+ | .024+ | **Day 2 begins.** The street empties into a fresh Chapter I — but the arrival vignette is re-rolled to a *different* one, and the **company colourway changes**. Per the real touring practice, a company plays a different repertoire each night: on day 2 the rehearsal fragments are different, the Lead and the Rival swap actors, and the shadow play is a second story. The day-difficulty step (`DAY_SCROLL_STEP`, `DAY_GAP_STEP`) has a diegetic partner. |

- **Signature:** the lion's head facing backward at the player from the departing cart.
- ***So the player feels…*** *paid — and then, immediately: a new cart is coming.*

---

## 5. Narrative arc

**Shape: a working day that turns into a performance — build, disaster, triumph, endurance, farewell.** Energy is deliberately asymmetric and never stacks. It ramps steadily from an empty road (0–96 s) to the day's busiest working stretch; drops into an authored 13-second void (112–125 s) that exists solely to make the clown-block's *frozen street* (128–155 s) read as tension rather than absence; recovers into the golden-hour dressing beats (155–190 s), where the median run ends holding a promise it hasn't been paid; then falls, over sixty seconds of rain, to the day's true low point — the screen torn down in a lightning flash at 245 s. Critically, the recovery is **not** immediate: a twenty-second hush (253–274 s) separates the disaster from the triumph so that the Libation's eye-dotting and the lighting of the screen land on a rested audience rather than on top of a peak. The Main Play (276–300 s) is the emotional summit; it is followed by four seconds of an empty lit stage — the day's second authored void, and the room to breathe before the climax. The climax proper is not the show but the **surviving** of it: the blizzard at 320–360 s, where the same tailwind that carries Pip fastest is the wind trying to pull the stage down, and the company plays anyway. Resolution is the strike at first light; the coda is the bow; the reward is the chest, claimed at dawn on the next day, as the cart rolls away. Three separate scroll-speed wave gestures — the clown-release ripple, the ovation, the bow — plant, echo and pay off the same motion. The rod-bird silhouette appears seven times in seven materials, so that the shadow on the screen at 276 s is something the player has been shown, unexplained, since second seven.

---

## 6. Variety & no-repetition rules

**V1 — Per-run roll (24 distinct openings).** 4 arrival vignettes × 3 company colourways × 2 lead-actor assignments (ribbon-dancer or mask-changer plays the Bird). Two of the four vignettes start with a **half-unloaded** cart, which shifts Chapter II's whole work-stage sequence forward — so even the *build order* varies. Colourway persists all day across banners, screen border, lion, cart, footlights.

**V2 — Same-hour coherence (the governing rule).** Every troupe sighting inside a chapter shows the **same stage of work**. Never a raised bay next to a bay still on the ground. This is what turns an infinite scroll into a single workday.

**V3 — Role bag-randomiser.** Each 640-px slot draws a *role* from the chapter's deck **without replacement** until the deck empties, then reshuffles. With 5–6 roles per deck, no role repeats within ~5 slots ≈ 20 s of screen time.

**V4 — Cross-family variant memory.** Extend the existing per-family no-repeat rule to a shared 3-deep ring across families, so you don't get "kid variant 2 → dog variant 5 → kid variant 2" inside four seconds.

**V5 — Call-and-answer pairs.** ~30% of slots emit a two-part gesture spanning slots N and N+1: a figure points right; the thing pointed at arrives four seconds later. Gives continuity *without* tracking any single object across the day.

**V6 — Density breathing.** Never more than two consecutive busy slots. At least one **bare-road** slot per four. Enforced at the director, not left to random.

**V7 — Latch off-screen.** All inclusion gates (crowd, weather, chapter) latch at slot entry, off-screen. Nothing pops in or out in view. (Existing behaviour — preserve it.)

**V8 — Non-repeating specials.** Each of the eight below fires **at most once per cycle**, on the first eligible slot inside its window, with a one-shot lock cleared at the wrap.

### The eight once-per-day happenings

| # | Happening | Window | Trigger / gate |
|---|---|---|---|
| **S1** | **The pole raise** — a scaffold bay swings vertical on four rope-lines | 62–80 s (.157–.203) | first eligible far-lane slot after the DAY-hold ends |
| **S2** | **The screen test** — cloth hoisted; one black rod-bird flicks across it in daylight | 100–118 s (.254–.300) | after S1 has fired |
| **S4** | **The kite** — rod-bird kite walked up, holds at y≈562, bamboo whistle | 163–176 s (.415–.447) | at/after the SUNSET keyframe |
| **S5** | **The rope-walk** — acrobat crosses between poles in flat sunset silhouette | 172–190 s (.437–.483) | after S4; requires rain < 0.05 |
| **S6** | **The screen tears loose** — cloth billows, six figures haul it down | 244.5–252 s (.621–.640) | fires on the **first lightning flash** |
| **S3** | **The eye-dotting** — horn, ears, mouth, eyes; red ribbon; the head lifts | 268–276 s (.681–.701) | requires rain < 0.15 and a dark sky |
| **S8** | **The empty stage** — lit, glowing, deserted, 4 s | 305–312 s (.775–.793) | requires crowd density < 0.40 |
| **S7** | **The bow** — whole company faces the flight line and bows in a scroll-speed wave | 390–393.5 s (.992–1.000) | fires at the last eligible slot before the wrap |

---

## 7. Logistics

### 7.1 Revised crowd curve (`_POP_KEYS`)

These are **dry-day** targets. `_weather_crowd_factor` multiplies on top (rain floor 0.22, snow floor 0.06) — do **not** pre-dip the keys for weather, or you double-dip.

```
phase  pop   t(s)    what it is
0.000  0.12    0.0   bare road — the arrival
0.048  0.30   18.9   unloading begins (newbie calm ends)
0.127  0.62   50.0   morning market + troupe work
0.200  0.70   78.7   busiest daytime
0.244  0.48   96.0   rehearsal; onlookers thin
0.290  0.22  114.1   ██ QUIET VALLEY 1
0.327  0.30  128.7   clown block — same density, near-zero motion
0.394  0.42  155.0   dressing the stage
0.483  0.68  190.1   audience gathering (rain factor takes over here)
0.564  0.72  221.9   crowd WANTS to be there; rain cuts it to ~0.16
0.630  0.80  247.9   storm peak; ×0.22 → ~0.18 actual
0.681  0.86  268.0   rain clearing; they come back
0.705  1.00  277.4   ██████████ MAIN PLAY peak
0.752  0.94  295.9   full house holds
0.775  0.34  305.0   ██ QUIET VALLEY 2 / empty stage
0.812  0.62  319.6   snow bites; ×0.06 → ~0.04 civilians
0.871  0.70  342.9   squall peak (troupe floor holds ~8 figures)
0.924  0.40  363.5   sunrise, strike
0.985  0.54  387.6   curtain call gathering
1.000  0.16  393.5   bare road again
```

**The single most important weather rule:** add a **troupe-exempt roster floor of 0.55** applied *before* `_weather_crowd_factor`. Weather removes the audience; it never removes the company. Without this, `WEATHER_CROWD_SNOW_MIN = 0.06` deletes the entire third act.

### 7.2 Weather overlay matrix

Weather **modulates the chapter's job — it never replaces the chapter.** Five universal verbs, applied to whatever the company happens to be doing:

1. **SHELTER** — civilians thin (existing gate), survivors raise umbrellas / tuck under awnings.
2. **PROTECT** — the company covers the *work in progress*: tarps on trunks, drum face-down, cloth furled.
3. **BRACE** — bodies oppose the weather vector: leaning, hauling ropes, holding poles.
4. **PERSIST** — whatever the chapter's action is, it continues at reduced cast. Never cut.
5. **REACT-ONCE** — a single one-shot beat per weather event, not a continuous animation.

| Chapter | Calm breeze / leaves (31–110 s) | Thermals + rocks (50–112 s) | Drizzle → storm (190–273 s) | Wet paving (207–290 s) | Snow squall + tailwind (309–384 s) | Snow cover (320–384 s) |
|---|---|---|---|---|---|---|
| **I Road in** | n/a — window opens at 31.5 s; if retuned, tarpaulin flutters | n/a | n/a | n/a | n/a | n/a |
| **II Unlashing** | leaves cross the crate-chain; one hand swats at them | rocks appear at 50 s and are *worked around*, kicked, used as seats | n/a | n/a | n/a | n/a |
| **III Raising** | peak drift through the pole raise (S1); leaves stick to wet rope | rocks thicken; geyser plumes behind the frame; riggers glance at them, keep hauling | n/a | n/a | n/a | n/a |
| **IV Fragments** | leaves settle on the furled cloth | rocks thin out as rehearsal winds down; last geyser is a beat, not a background | n/a | n/a | n/a | n/a |
| **V Street looks up** | leaves are the *only* moving thing in the frozen street — use them | window closed | n/a | n/a | n/a | n/a |
| **VI Dressing** | window closed; kite (S4) carries the wind read instead | n/a | n/a | n/a | n/a | n/a |
| **VII Ruined rehearsal** | n/a | n/a | **the chapter IS this**: SHELTER → PROTECT → BRACE → S6 at the flash | paving glazes; every lamp doubles by reflection; figures step around puddles | n/a | n/a |
| **VIII Libation** | n/a | n/a | tail: last drops; the re-hang happens **in the wet**, deliberately slow | still wet at 253–290 s; the lit screen throws a long inverted reflection down the paving — free spectacle | n/a | n/a |
| **IX Main Play** | n/a | n/a | clear by 273 s | drying through 290 s; last reflections under the marquee | first flakes at 309 s catch the screen light | n/a |
| **X Additional Play** | n/a | n/a | n/a | n/a | **the chapter IS this**: SHELTER (audience gone) → BRACE (mirrored riggers) → PERSIST (they play on) | deck, shoulders, lion's back accumulate; melt in visible steps from 358.6 s |
| **XI Strike** | n/a | n/a | n/a | n/a | tail: snow shedding; banners stop snapping mid-chapter | **peach sunrise on cool snow — the cycle's best palette; do not waste it** |
| **XII Company box** | n/a | n/a | n/a | n/a | cleared at 384.5 s | last melt patches under the departing cart wheels |

**Fallback rule for retuning:** every troupe behavior above is keyed to the *live intensity signals* (`rain_intensity`, `storm_intensity`, `thermal_intensity`, `calm_breeze`, `wetness`, `snow_cover`) — not to seconds. Move `RAIN_START_PILLAR` or `SNOW_START_PILLAR` and the street follows automatically. Only the eight specials use time windows, and each has a wide window plus a fire-on-first-eligible-slot rule.

### 7.3 Tournament-awareness layer (ambience only — never HUD, never text)

| Player event | Street response | Cooldown / cap |
|---|---|---|
| **Near-miss** (Pip within ~8 px of a pillar edge) | one far-lane clump of 2–3 flinches: arms up, one half-rises off a bench | 6 s; max 1 per 2 pillars |
| **Coin rush** (every 15th pillar) | drummer lands a stroke on the downbeat; string lights ripple left→right. **At night: the shadow bird dives on the same beat** | intrinsic (~26 s) |
| **Power-up collected** | the mask-changer flips a mask — the day's "something changed" verb | 8 s |
| **Score milestone** (every 25) | the Scribe adds a stroke to the playbill banner; by night, a ribbon sweeps a full arc | per milestone |
| **Genie lamp** (102.6 s) | the Ritualist stops mid-fragment and bows toward the sky; brazier flares | once |
| **Clown gauntlet** | **the whole street freezes and faces the flight line** for the duration; scroll-speed arm-wave 1.5 s after clearing | once |
| **Chest claimed** (~397 s) | the company straightens out of the bow, all arms up, inside the 1.5 s `TREASURE_BOX_ANIM_T` | once |
| **Pip dies** | the drum stops for exactly one beat; **the shadow bird stalls and slides out of the bottom of the screen frame** | once |
| **Continuous, night only** | the shadow bird's y = smoothed (τ≈0.6 s), clamped read of Pip's y, remapped into the 30-px screen | continuous, with canned-loop fail-safe |

**The restraint rule:** at most **one** reaction beat may be active in the band at any time, and none may occupy the bird lane. If two fire together, the higher-priority one wins and the other is dropped, not queued. Peripheral vision has a budget.

### 7.4 Light, glow and the coin contract

- **Area-brightness cap.** Small lit elements keep the existing `NIGHT_GLOW_CAP = 150`. **Large fills (>400 px², i.e. the shadow screen) cap at 132.** The screen wins attention by *area*, not luma. Coin stays ~206 and unchallenged.
- **Night reads by warm-vs-cool**, per the existing contract: amber screen + brazier + capped garland against `stone_light (150,170,210)` moonlit sandstone.
- The screen's lit face is the **only new light source** in the plan. Everything else reuses lamps, braziers, string lights and the kiosk lantern.
- **Wet paving (207–290 s) is free production value**: the lit screen's inverted reflection down the paving is the single cheapest "expensive-looking" frame in the cycle. Cap the reflection at 60% of source luma.

### 7.5 Sound (optional layer — flag to `sound-designer`, dual-backend, never `pygame.mixer` on web)

Six procedural cues, all ≥12 dB under gameplay SFX (flap / coin / hit), all skippable:

1. **Frame drum** — low sine + short noise envelope. The company's pulse. Irregular by day, steady four at night, **silent through the clown block and the empty stage**, unbroken through the blizzard.
2. **Cymbal / gong** — bright noise burst, long decay. **Exactly five uses per day:** pole raise lock (tap), clown release (stroke), marquee entrance, storm rescue, curtain call (allowed to ring).
3. **Suona** — thin reedy two-note figure. Unresolved at 163 s (tuning); **resolved** at the Libation; full phrase at the bow. One motif, three states.
4. **Bamboo kite whistle** — soft airy tone during S4; returns pitched-down and unsteady in the blizzard.
5. **Rope-and-wood** — creak + knock, used sparingly during raising and strike.
6. **Thunder** — existing (`audio.play_thunder`).

**Reading rule if sound is cut entirely:** nothing in this plan depends on it. Every beat above is authored to read on silhouette, colour, motion, grouping and light.

### 7.6 Director state (implementation cues keyed to the timeline)

The director needs five signals per frame, and nothing else:

| Signal | Source | Drives |
|---|---|---|
| `chapter` | phase, against biome keyframes + rain/snow intensity | role deck, build state, dressing flags |
| `build_state` (0–6) | monotonic function of chapter | which scaffold/screen/stage sprite the far-lane structure slot draws |
| `pop` | revised `_POP_KEYS` × `_weather_crowd_factor` × `_run_fill`, **with troupe floor 0.55** | slot inclusion gates |
| `motion_gate` (0–1) | 0 during the clown block, 1 otherwise | global animation-amplitude multiplier — how the freeze is implemented |
| `special_locks` (8 bits) | cleared at wrap | one-shot specials |

**Build states:** 0 = crated · 1 = poles laid flat · 2 = uprights guyed · 3 = frame with crossbeams · 4 = cloth hoisted, unlit · 5 = dressed (banner, footlights, benches) · 6 = lit and playing. Plus **state −1 = struck** for Chapter XI, which is state 1 drawn in reverse — free.

### 7.7 Placement & readability constraints (non-negotiable)

- **Nothing above y = 560.** Max height above the ground line is 35 px. The stage frame tops at y=562; the kite holds at y≈562 and reads as ascending via line-angle and 30% scale-down; the stilt-walker must be re-authored to fit the ceiling (current `h=18 + stilt_h=24` overshoots).
- **Characters obey `_char_x_ok`** (culled out of the bird lane x≈48–188 and pillar lane x≈212–320). **Structures are kiosk-class and exempt.** Consequence, and it's a gift: the puppeteers cull out while the screen doesn't. The shadow play works because the operators are invisible.
- **Crowds face away.** A crowd of backs is calm, instantly readable as attention, and does not compete with the pillars for the eye. Use it for all four gathering beats.
- **Negative space is content.** Two authored voids (112–125 s, 305–309 s) plus V6's one-bare-slot-in-four. Do not fill them in a later tuning pass; they are load-bearing.
- **Procedural only**, ~18 px near-lane figures, no faces, no text. Every beat above resolves at 18 px in silhouette.

### 7.8 Contingencies

- **Median death at ~156 s.** Chapters I–VI must each stand alone, and each contains at least one rod-bird appearance (tarpaulin corner → rehearsal rod → daylight screen test → kite). Chapter VI ends on the strongest unresolved promise in the plan; that is the retry hook.
- **Run under 19 s.** The player sees only the arrival vignette — so all four are authored as complete micro-stories with a beginning and an end inside 4 s.
- **Elastic clown block (14–26 s).** Chapter V is a *held pose*; it stretches without re-timing.
- **Frame budget under storm/blizzard particle load.** Degrade the roster in strict priority order: screen > stage structure > lead performer > drummer > audience clumps > dogs > greenery beds. The screen and the drummer are the last two things to go, because they are the concept.
- **Anchors retuned.** All behavior keys off intensity signals and biome keyframes, not seconds. Only the eight specials use windows, each wide, each fire-on-first-eligible.
- **Day 2+.** Colourway re-rolls, arrival vignette re-rolls, Lead and Rival swap actors, rehearsal fragments change, the shadow play is a second story. The per-day difficulty step gets a diegetic partner: a different night, harder air.

### 7.9 New assets (flagged — everything else is recast)

| # | Asset | Notes |
|---|---|---|
| **NEW-1** | **Bamboo stage frame**, 7 build states (−1, 0–6) | far-lane structure, kiosk-class; reuses `_pagoda_roof` for state 5–6 |
| **NEW-2** | **Shadow screen** — lit rect ≤132 luma + silhouette layer (bird, crane, dragon, gold disc) | the concept, in one sprite |
| **NEW-3** | **Rod-bird motif** — one 9×7 three-point silhouette | used 7 ways across the day; ~40 lines total |
| **NEW-4** | **Troupe cart / prop bundle**, 3 load states | crates + rolled screen + drum; can lean hard on `props_cast` dressing |
| **recolour** | Company colourway pass over the existing banner / brazier / lion / dragon families | no new geometry |

---

## 8. Self-critique applied before delivery

Four problems found in the draft and fixed, noted here because they're the reasoning that shaped the final:

1. **Two peaks were stacked.** The storm peak (247.7 s) sat directly against the night crowd peak. Fixed by making the storm a *negative* peak and inserting a 20-second hush (253.5–274 s) so disaster → hush → triumph. The Libation now has room to land.
2. **The crowd curve double-dipped weather.** Original keys pre-dipped at 222 / 248 / 343 *and* got multiplied by `_weather_crowd_factor`. Keys are now dry-day only, with an explicit troupe-exempt floor so the third act doesn't get deleted by `WEATHER_CROWD_SNOW_MIN = 0.06`.
3. **The finale was mis-placed.** I initially wrote the chest into the end of the day; `CYCLE_FINALE_PHASE_HI/LO` detects the *rollover*, so the chest is actually claimed in the opening seconds of the next day. Chapter XII now leans into that: the bow at last light, the chest at first light, the cart leaving into a bare road that is also Chapter I.
4. **The scroll-speed wave was used once.** Now used three times — clown release, ovation, bow — so the finale's gesture is one the player has already learned to read, and its third meaning lands without explanation.

---

## Sources & inspiration

- **Shadow-puppet troupe structure and lighting** — the five-person company (puppeteer, suona, banhu, percussion, singer), the taut white cloth on a wooden frame, and the single tended oil lamp as "the true magician" gave me the Libation's lamp-carried-behind-the-screen beat, the screen's build states, and the decision to make the company small and role-defined rather than a crowd: [Chinese Shadow Play: History and Evolution](https://www.chinatravel.com/culture/shadow-play) · [Cultural Keys — Shadow Play](https://www.culturalkeys.cn/2020/10/10/chinese-treasures-shadow-play/) · [Mandarin Factory — The Art of Chinese Shadow Theater](https://mandarin-factory.com/en-us/blogs/blog-china/the-art-of-chinese-shadow-theater)
- **Itinerant troupe practice and temple-fair opera structure** — the Red Boat companies touring the Pearl River Delta, the bamboo-theatre build (thousands of reused rods and poles), the fact that a company plays a **different repertoire each day** and packs up on the night of its last show, and above all the three-part temple-fair form — **Libation → Main Play → Additional Play** — which is the literal skeleton of Chapters VIII–X and the Day-2 variation rule: [Temple Fair Opera](https://baike.baidu.com/en/item/Temple%20Fair%20Opera/117440) · [CNN — Building a bamboo opera theater in Hong Kong](https://www.cnn.com/travel/article/hong-kong-bamboo-theater/index.html) · [West Kowloon Bamboo Theatre](https://en.wikipedia.org/wiki/West_Kowloon_Bamboo_Theatre) · [SCMP — Cantonese Opera](https://multimedia.scmp.com/infographics/culture/article/3036661/cantonese-opera/index.html)
- **The eye-dotting ceremony (開光 / hoi gwong)** — dotting horn, ears, mouth then eyes to awaken the lion, the red ribbon tied to the horn marking it as tamed, the ceremony led by a respected elder, and the drum cue that starts it. This is Special S3, essentially verbatim, and it is the plan's best single moment: [Eye-Dotting in Lion Dance](https://www.liondance.sg/blog/eye-dotting-in-lion-dance-what-it-is-and-why-this-tradition-is-so-important) · [USA Lion Dance — The Eye-Dotting Ceremony](https://usaliondance.com/blogs/news/the-eye-dotting-ceremony-awakening-the-lion) · [USDLDF — Consecration and Blessing of the Chinese Lion](https://usdldf.org/divine-spirit-consecration-and-blessing-of-the-chinese-lion/)
- **Kite tradition** — bamboo whistles tied to kites since the Five Dynasties period (Nantong's multi-whistle kites nicknamed "Symphony on Air"), and the swallow-kite form, which is where the rod-bird motif and S4's whistle cue come from: [Chinese Kites — TravelChinaGuide](https://www.travelchinaguide.com/intro/arts/kites.htm) · [Chinese Kite & Weifang Kite Festival](https://www.topchinatravel.com/china-guide/kite.htm) · [Weifang International Kite Festival](https://en.wikipedia.org/wiki/Weifang_International_Kite_Festival)
- **Zaji acrobatics** — hoop diving ("Swallow Play", Han dynasty), pole climbing, plate spinning, the itinerant street-selling tradition, and the folk-utensil origin (bowls, plates, benches, ladders) which justified building the whole tumbler layer out of existing props: [Chinese Acrobatics — chinatravel.com](https://www.chinatravel.com/culture/chinese-acrobatics) · [Circopedia — The Chinese Acrobatic Theater](https://www.circopedia.org/The_Chinese_Acrobatic_Theater)
- **Ambient restraint** — "prioritise gameplay clarity over visual complexity," "use parallax to enhance, not distract," and *don't be scared of negative space* directly produced V6 (density breathing), the two authored quiet valleys, the single-active-reaction rule in §7.3, and the backs-to-camera crowd device: [The Parallax Paradox — Wayline](https://www.wayline.io/blog/parallax-scrolling-game-development-pitfalls) · [Environmental Storytelling in Video Games](https://gamedesignskills.com/game-design/environmental-storytelling/)
- **Repo, not the web** — all timings, phases, keyframes, weather curves and event anchors were computed from `/home/user/skybit/game/biome.py`, `/home/user/skybit/game/weather.py`, `/home/user/skybit/game/config.py`, and the cast catalogue in `/home/user/skybit/docs/sidewalk_overhaul/README.md`, with the lane-cull and structure-exemption behaviour read out of `/home/user/skybit/game/foreground_promenade.py`.

*No files were written — this was a read-only planning session, as briefed.*