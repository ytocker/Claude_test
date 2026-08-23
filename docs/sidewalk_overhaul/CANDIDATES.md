# Sidewalk Day-Plan Candidates — Index & Comparison

Five complete full-day (393.5 s) behavioral designs for the sidewalk, all authored by the
event-director agent against the same brief (ancient Far East tournament town, real biome/weather
anchors, keep the end-of-day treasure finale, median run ≈156 s). Each is built on a deliberately
different creative territory so they are genuine alternatives, not variations.

| Doc | Plan |
|---|---|
| [DAY_PLAN.md](DAY_PLAN.md) | **A — The Fifth Drum to the Third** (wish-lantern relay + drum-tower day-clock) |
| [DAY_PLAN_B_THE_REGULARS.md](DAY_PLAN_B_THE_REGULARS.md) | **B — The Regulars** (nine recurring silhouette characters, ensemble drama) |
| [DAY_PLAN_C_STREET_READS_SKY.md](DAY_PLAN_C_STREET_READS_SKY.md) | **C — The Street That Reads the Sky** (omens & offerings: sign → reading → answer) |
| [DAY_PLAN_D_WORKING_DAY.md](DAY_PLAN_D_WORKING_DAY.md) | **D — The Working Day** (the tournament as the town's ground operation & payday) |
| [DAY_PLAN_E_MIRROR_PLAY.md](DAY_PLAN_E_MIRROR_PLAY.md) | **E — The Mirror-Play** (a troupe builds a stage all day; the night shadow-play mirrors the flight) |
| [DAY_PLAN_WEEKEND.md](DAY_PLAN_WEEKEND.md) | **★ The Town Is Having a Weekend** — the commissioned direction: an ordinary rich, lively weekend day (abundant crowd/decoration/animal variety, night food market in the clear window, incidental street shows, concrete weather-dress adjustments, organic block-by-block occupancy). Supersedes A–E as the chosen brief; folds in their portable findings. |

## Difference table

| | **A — Fifth Drum** | **B — Regulars** | **C — Reads the Sky** | **D — Working Day** | **E — Mirror-Play** |
|---|---|---|---|---|---|
| **Spine** | One red wish-lantern prepared all day, released at dawn | Nine townsfolk's small wants braid and converge at the festival | Nature signs → the street reads them → answers with offerings | The race is the town's biggest shift: open, rush, storm, tally, payday | A troupe raises a stage all day; at night performs the player's own flight in shadow |
| **The street is…** | a ritual community | a cast of characters | a diegetic weather-oracle | the tournament's ground crew & economy | front-of-house, backstage, and audience |
| **Relation to player** | the town prepares a gift for the flyer | people who eventually all watch together once | the flight is the omen everyone awaits | one flyer among many; the town works the race | the play is literally about you (shadow bird tracks Pip's y) |
| **Median-run (156 s) payoff** | the Lantern Raising crests on the median player's last seconds | Char's crate for Sprig — plant→payoff closes at ~150 s | street floods back post-gauntlet + sunset lights every marker | sunset trade crest "dressed as an ending" | the unresolved promise: *"there's a show tonight and I'll miss it"* (retry hook) |
| **Night reward** | festival + six-figure snow Watch | four staggered thread-payoffs at the festival peak | lantern remembrance on mirror-wet paving | full tally racks + prize procession | the Main Play: your silhouette on the lit screen |
| **Finale treatment** | lantern released; six answer as chest lands | curtain call — all nine share a frame once, then walk with Pip | the day's whole accrued tally spent (cairn knocked over) | chequer flags + finish arch; token rows raised in salute | the company bows in a scroll-speed wave; cart departs |
| **Anti-repetition engine** | 6 arrival cards × 3 moods; rare-sighting deck; coprime lattices | 40/60 anchored/floating beats; seeded permutations (≥18 openings); rationed Regulars | Omen-of-the-Day suits; monotonic accumulation (street visibly accrues) | role liveries (50 bodies × 3 palettes ≈ 150 variants); rhythm bands; designed voids | 24 distinct openings; build-state monotonic arc; role bag-randomizer |
| **Emotional register** | warm communal ritual | intimate, funny, humane | contemplative, mystical | industrious, sporting, proud | theatrical, awed, "that was for me" |
| **New art** | 3 set pieces | 4 props + 1 data layer | 7 items (3 overlays) | 5 set pieces (all reskins) | 4 + 1 recolour |
| **Biggest risk** | single tracked object at 18 px | 9 recognizable characters is the hardest legibility bet | subtle — least spectacular of the five | economy register could read dry without its human threads | highest implementation complexity (7 build states + live y-mirror screen) |

## Ranking (top 3)

**1. E — The Mirror-Play.** The shadow bird on the lit screen tracking the player's own altitude is
the single strongest idea across all five plans — a discoverable, unannounced, tell-your-friends
moment that no casual competitor has. The monotonic stage build gives the endless scroll a visible
arc, and the median-death chapter is engineered as an explicit retry hook. Costs the most to build,
and worth it.

**2. D — The Working Day.** The best thematic fit to the fixed premise (the town *hosts a
tournament* — this plan is the only one where that's the whole street). The marshal-flag language is
learnable, reports on the course (free diegetic telegraphing of hazards), and can never be mistaken
for HUD. Role liveries are the cheapest, most direct kill of the "same people repeating" complaint,
and the rival-macaw thread (launch → empty perch → home at dawn) is the best quiet storytelling in
the set. Most implementable of the top three.

**3. B — The Regulars.** The deepest emotional design: nine wants, crossing rules, and a
plant→payoff that lands exactly on the median player's final seconds. Across many runs the Regulars
become genuinely familiar — repetition converted from bug to feature. Ranked third only because
"nine recognizable 18-px characters" is the riskiest legibility bet, even with its tint-locked
accents and rationing rules.

**Worth stealing regardless of the pick:** A's density-curve fix (festival moved out of the
thunderstorm) and phase-window resync; C's accumulation mechanic (the street visibly accrues and the
finale spends the tally) and its "street as weather forecast" behaviors; B's freeze-on-death
reaction; D's two code findings (`calm_breeze` never width-scaled; `lightning_active()` dead code).
