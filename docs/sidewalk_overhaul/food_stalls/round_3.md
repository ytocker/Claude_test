# Food-stall family expansion — round 3: SIX NEW STALLS

Sheet: `docs/sidewalk_overhaul/food_stalls/round_3.png` (1180 × 2217)
Generator: `tools/_food_stalls_round3.py` (scratch; nothing under `game/` is touched)
Lineage: `round_1.png` → `round_2.png` (SHIP-READY, the shipped five) → `integrated.png` → **this**

## The brief, restated as a shape problem

The shipped family's organizing principle is that the **shell never changes** —
two timber posts, a cloth awning, a counter, a back wall, a hanging sign,
`HALF_W = 22`, posts to `base_y - 34`. A stall *is* its **cooking-apparatus
silhouette** plus its **awning colour pair**. So "six new stalls" is really "six
new apparatus silhouettes", and the distinct-variants rule bites on the
apparatus, not on the paint.

Read as pure outline, the shipped five are **four squat stoves and one tall
kettle**. This round deliberately fills the shapes the row does not yet contain:

| | shape the row was missing |
|---|---|
| S6 roast-duck cabinet | a **tall enclosed box** — and the only lit *window* |
| S7 flat griddle | a **horizon** — the flattest, widest apparatus in the family |
| S8 clay-pot bank | **repetition** — a crenellated row instead of one object |
| S9 drum roaster | a **lying cylinder** — and the only rotating machine |
| S10 shaved ice | **nothing above it at all** — the cold stall, motion inverted |
| S11 noodle boiler | a **gantry** — a rail of hanging baskets over a column |

## The six

### S6 — ROAST-DUCK / CHAR-SIU HANGING CABINET · awning **plum / wheat** · vendor **CHOP (idx 6)**

A glazed vitrine standing on the counter: dark timber frame, a glass panel, a
hook rail, three lacquered birds hanging inside and swaying a hair out of phase
with `t`, lit by a small capped interior lamp. A cleaver and a chopping board sit
at the counter's right, and a stub roof vent breathes a thin sooty ribbon.

*Why it is unlike the other ten:* every existing stall is an **open cooking
surface with its heat on show**. This one puts the food **behind glass**, hangs
it **in the air**, and lights it **from inside** — at night it is the only stall
that reads as an upright bright rectangle in a row of glowing puddles, and the
only apparatus whose animation comes from what dangles rather than from what
rises. It punches through the awning line (ceiling y529), which is the family's
established idiom for a tall apparatus (the shipped steamer does it at y516).

*Pose:* the cleaver/board is a literal hand-off to the chopping vendor — no new
cast art, and the day_cast pool's `chop` variant already carries `blade` +
`board` in its palette.

### S7 — FLAT GRIDDLE (jianbing / pot-sticker pan) · awning **ochre / ink** · vendor **POUR (idx 7)**

A 36 px shallow iron disc — the widest thing in the family — with a crepe and its
folded half on it, a domed lid tipped up on its edge to the left, a wooden batter
**rake that sweeps an arc off `t`**, and a jar of tools at the right.

*Why it is unlike the other ten:* it is the only apparatus that stays **entirely
under the awning line** (ceiling y551, driven by steam, not by structure). Where
the steamer and the boiler are columns, this is a horizon — and the **steam
matches the shape**: four short offset wisps make a broad **low sheet** hugging
the iron instead of a plume, so it reads differently in motion as well as in
outline. The only tall thing at this stall is the pouring vendor's arm, by
design.

*Pose:* `pour` is the pool's only vertical-hairline action (a stream falling from
a raised vessel) — over a flat plate it is unmistakably batter going down.

### S8 — CLAY-POT BANK · awning **clay / slate** · vendor **WEIGH (idx 1)**

Five small lidded pots dropped into a five-hole stove, each burner ring glowing
capped, one lid at a time chattering up off its rim on a slow cycle, a bowl stack
at the right.

*Why it is unlike the other ten:* **repetition is the silhouette.** Every other
apparatus in the market is one big object; this is a crenellated row of small
domes. The steam follows the same logic — five little offset wisps that read as a
**keyboard**, not a plume — and the stove is lit by three faint burner halos
rather than one wash, so the fire reads as several small ones.

*Pose:* the bowl stack makes the counter a portioning bench, which is exactly
what the `weigh` vendor (hand scale, lean build) is doing above it.

### S9 — DRUM ROASTER (chestnuts / sweet potato) · awning **moss / ochre** · vendor **STACK (idx 4)**

A hooped barrel slung in a cradle over a firebox: body block closed by an end-cap
ellipse so it reads as a cylinder seen three-quarters, **hoop bands travelling**
around the shell with `t`, a **crank arm revolving** on its axle, a flickering
firebox mouth, a stub chimney with a slow sooty ribbon, and a tray of roasted
chestnuts on the counter front.

*Why it is unlike the other ten:* the only **horizontal cylinder** in the market,
and the only genuinely **rotating machine** anywhere in the family. Against four
squat stoves and two columns, a lying-down barrel with a wheel on its end is
instantly a separate outline; its smoke is pitched lower and lazier than the
skewer grill's so the two smoking stalls don't twin.

*Pose:* the `stack` vendor is the one carrying a `basket` in its palette —
bagging chestnuts is the read.

### S10 — SHAVED ICE / cold sweets · awning **teal / wheat** · vendor **SIGN (idx 5)**

A cast-iron hand shaver: foot plate, column, blade housing, a clamped ice block,
a **crank that turns** with `t`, a bowl of snow with a syrup arc under the blade,
and three syrup bottles on the counter.

*Why it is unlike the other ten:* **no steam, no flame, no glow — nothing at
all** rises off this stall. In a row where every silhouette is topped by vapour,
the one stall with clear air above it is what makes the others read as hot. Its
motion vector is inverted too: the crank turns and ice flecks fall **down** into
the bowl — the only downward motion in the family. It is also the dimmest stall
on the sheet (night peak 142.6, **zero** pixels over the cap even including the
halo pass, because it has no halo).

*Pose:* the syrup bottles are the stall's whole colour story, so the
flavour-board `sign` vendor is the natural match.

### S11 — NOODLE BOILER · awning **ink / wheat** · vendor **WOK (idx 8)**

A tall straight-sided stock column on a ring burner, rolling boil at the rim, and
above it a **gantry rail** carrying three long-handled strainer baskets that dip
into the water on their own phases. Bowls stacked and chopsticks in a jar at the
right.

*Why it is unlike the other ten:* the shipped cauldron is a **sphere**; this is a
**cylinder**, and the gantry is the real separator — an ordered row of hanging
teardrops on a bar, sitting where every other stall has open sky. It is also
deliberately in the **boiling-and-serving** register, not the performance one:
bowls, chopsticks, no dough, no arms-wide showman, so it can never be confused
with `festival.theatre_noodle`'s hand-pulled-noodle act (or with
`theatre_tanghulu`'s radial spike pole, which the gantry's ordered verticals
answer rather than echo).

*Pose:* `wok` is the pool's "wide vessel held away from the body" arm — a
strainer basket being shaken out.

## Awning pairs

Shipped: terra/cream, indigo/cream, rust/cream, jade/cream, bamboo/indigo. Six
**new** pairs from the same muted shan-shui band (new entries: plum, wheat,
ochre, ink, clay, slate, moss, teal — nothing saturated, because the awning must
never out-read the apparatus it frames):

| stall | awning | why |
|---|---|---|
| S6 duck cabinet | plum / wheat | lacquer mulberry, the roast-meat colour |
| S7 flat griddle | ochre / ink | the boldest pair — hot gold against near-black |
| S8 clay-pot bank | clay / slate | earth + cool grey; quietest awning for the busiest apparatus |
| S9 drum roaster | moss / ochre | autumnal olive + gold, both stripes warm |
| S10 shaved ice | teal / wheat | the only cool-dominant pair in the market — sells "cold" before the apparatus does |
| S11 noodle boiler | ink / wheat | charcoal + pale, the highest-contrast pair; a dark awning under a pale steam column |

## Vendor pairing

The shipped five use only `call` (×2), `ladle` and `fan` (×2). All six new stalls
take poses the row has **never** used, so the vendor line diversifies with the
stall line and no new cast art is needed. Indices verified against
`game/day_cast.py::_build_vendors()`:

| idx | pose | stall |
|---|---|---|
| 1 | weigh | S8 clay-pot bank |
| 4 | stack (carries `basket`) | S9 drum roaster |
| 5 | sign (carries `sign`) | S10 shaved ice |
| 6 | chop (carries `blade` + `board`) | S6 duck cabinet |
| 7 | pour (carries `pot` + `tea`) | S7 flat griddle |
| 8 | wok (carries `pan` + `food`) | S11 noodle boiler |

Pool order for reference: 0 call · 1 weigh · 2 fan · 3 ladle · 4 stack · 5 sign ·
6 chop · 7 pour · 8 wok · 9 weigh.

## Measured night-cap + ceiling audit

Scanned off **8 rendered frames per stall** on the night deck (`night = 0.95`,
deck `(30,34,52)`), not a colour list — alpha wisps stack, ellipse edges blend,
and the additive halo lands on the deck as pixels a colour-list audit can't see.
Two passes, because the cap means two different things:

* **MATERIAL** — the drawn colours, which is what `_cap150` actually governs.
  Hard contract: `<= 150`, zero pixels over.
* **COMPOSITED** — the same frames *including* the shared additive `_warm_glow`
  halo (soft light summed onto the deck with `BLEND_RGB_ADD`). The shipped five
  use the identical primitive, so this column is judged **against them**.

```
stall                       awning          pose          matD    matN  matOver   compN  compOver  ceiling
S6 roast-duck cabinet       plum / wheat    CHOP (6)       197   113.7        0   173.9       129     y529
S7 flat griddle             ochre / ink     POUR (7)       198   128.9        0   173.1       128     y551
S8 clay-pot bank            clay / slate    WEIGH (1)      199   124.6        0   176.1       424     y543
S9 drum roaster             moss / ochre    STACK (4)      155   115.2        0   170.2       352     y523
S10 shaved ice              teal / wheat    SIGN (5)       220   142.6        0   142.6         0     y548
S11 noodle boiler           ink / wheat     WOK (8)        198   143.6        0   173.3       160     y520
—— shipped five, identical scan ————————————————————————————————————————————————————————————————
S1 steamer     (shipped)    terra/cream     call (0)       225   131.1        0   177.3       320     y516
S2 cauldron    (shipped)    indigo/cream    ladle (3)      225   124.3        0   183.3       288     y526
S3 grill       (shipped)    rust/cream      fan (2)        254   219.1       91   242.9       790     y538
S4 wok         (shipped)    jade/cream      fan (2)        225   132.9        0   179.9       120     y530
S5 tea urn     (shipped)    bamboo/indigo   call (0)       217   141.6        0   186.5       160     y526

gold coin core rgb=(255, 232, 150) luma=230   cap=150   ceiling floor=y518
```

Results:

* **Material cap held on all six** — hottest is S11 at **143.6**, and **zero**
  pixels over 150 on any of the six.
* **Composited peak of every new stall (170.2 – 176.1) sits below the lowest
  shipped stall (S1 steamer, 177.3)** — the six are, measurably, the *calmest*
  stalls in the market at night. The coin's 230 core is untouched.
* **Ceilings**: y520 … y551, all at or under the family maximum (shipped steamer
  y516; brief floor y518). The three that punch through the awning (S11 y520,
  S9 y523, S6 y529) are the three intended tall reads.
* Day material peaks (155 – 220) sit inside the shipped band (217 – 254); the ice
  block and snow bowl were pulled down twice to keep the market's only near-white
  material off the top of that band.
* **Incidental finding on the shipped family:** S3 grill measures **91 material
  pixels over the cap (peak 219.1)** at night. It is not from `_warm_glow` — it's
  the ember particles, which `stall_grill` blits with `BLEND_RGB_ADD` directly
  and therefore outside `_cap150`'s reach. Flagging, not fixing (this round
  touches nothing under `game/`).

## Sheet contents (`round_3.png`)

* **A** — the six at true far-lane size, day then night, each with its assigned
  vendor, the y518 ceiling line drawn where it actually falls, and the adult
  (17 px, `VEND_H`) + gold-coin yardsticks.
* **A2** — the shipped five, imported **live** from `game/food_stalls.py` (not a
  stale copy), same treatment: the coherence check.
* **B** — per-stall cells, day then night: 3 animation frames at true size, a
  2.4× zoom inset, the assigned vendor pose, an in-cell coin, and the apparatus
  note.
* **C** — the full **eleven** interleaved, old and new, each with its vendor, day
  and night: does the row read as one market with eleven trades?
* **D** — the three `openness` assembly states (0.2 skeleton / 0.4 frame / 1.0
  full) for all six; the apparatus draws only at `>= 0.5`, exactly as the shipped
  shell does.
* **E** — the audit table above, rendered on the sheet.

## Constraints checked

* Pure `pygame.draw` + `Surface(SRCALPHA)` + `BLEND_RGB_ADD`; no numpy, gfxdraw
  or PIL anywhere in the stall code — pygbag-safe on both targets.
* All motion drives off `t`: steam, smoke, swaying birds, sweeping rake,
  chattering lids, travelling hoop bands, revolving cranks (×2), dipping
  baskets, falling ice flecks. Nothing is static.
* `_wisp` / `_warm_glow` / `_steam_col` / `_smoke_col` / `_cap150` are reused
  verbatim from the shipped family, not reinvented.
* Horizontal footprint of every new apparatus stays inside the shell (measured
  extent −24…+25 for all eleven, which is the awning, not the apparatus).
* No overlap with `festival.py`'s three theatre overlays (`noodle`, `sugar`,
  `tanghulu`) — see S11's note.
* Nothing under `game/` was modified; sheet and generator live in `docs/` and
  `tools/`, outside the pygbag bundle.
