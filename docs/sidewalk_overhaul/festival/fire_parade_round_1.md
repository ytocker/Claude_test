# FIRE-TREE NIGHT — round 1 · THE IRON FLOWER + DRAGON-PARADE SUPPORT

**Sheet:** `docs/sidewalk_overhaul/festival/fire_parade_round_1.png` (1500 × 2240)
**Generator:** `tools/_festival_fire_round1.py` (scratch; touches no `game/` file)
**Covers:** FESTIVAL_PLAN.md §4 (the fire show, the dragon staging) and build-list
rows **A1 A2 A3 A4 A5 A6 A7 A8 A13 A15**.

---

## 0. The one structural decision on this sheet

**Every panel is a literal screen slice — world y 500 → 647, drawn at 1×.** The
far deck (595), the near deck (638), the 560 cast/prop band ceiling (blue dashes)
and the y=512 spark ceiling (amber dashes) are all *drawn into the panel*. So the
vertical budget — which is the single most contentious thing in this plan (R8
needs sign-off) — is verifiable by eye rather than asserted in a caption. If a
piece pokes above a dashed line, you can see it.

Measured outcome: **the only thing that crosses 560 is the spark FX, and it tops
out at y 512.2** — 0.2 px of headroom under the sanctioned ceiling, which is the
point of the exercise. Everything else lives in 560–640.

---

## 1. Why datiehua is the only fire that survives the cap

This is the load-bearing research call, so it goes first.

The brief's hard constraint is 150 luma at night, gold coin 230, sole-brightest.
Fire breathing, poi and torch juggling all read as fire through **raw
brightness** — a bright blob, a bright trail, three bright points — and every one
of them dies under a 150-luma ceiling, because you cannot make a dim blob look
hot.

打铁花 reads through **count, arc, motion and afterimage**: hundreds of
individually *dim* 1-px sparks on ballistic parabolas. That is precisely the axis
the cap does not constrain. The tradition is also a poor town's fireworks —
Northern-Song blacksmiths who couldn't afford gunpowder throwing 1,600 °C scrap
iron at a willow pergola — which is exactly this street's character.

Research fed three concrete construction decisions, not just the choice of act:

| Source detail | What it produced on this sheet |
|---|---|
| iron is struck against a **willow-branch pergola** with willow sticks, not a wall | A1 is a braced **A-frame truss with a shaggy straw SPLASH BOARD**, not a flat panel — a structure no stall in the game shares |
| performers work in **soaked straw hats and sheepskin** | A2's silhouette: a wide dark hat disc over a bulky pale fleece shoulder mass, the widest shoulder in the cast |
| sites are **watered down** for safety | A5, the doused apron — which is also how the plan gets spark reflections without touching the global wetness rate |
| a **wooden ladle** scoops, a second man **strikes at the apex** | A2 is two figures with opposite jobs, not two of the same figure |

---

## 2. Piece-by-piece rationale

### A1 · The scaffold, four states

The rig is **planted three times before it lights** (Ch5 frames-up, Ch6/7 storm,
then the show). That is only worth doing if the object is recognisable on sight
the fourth time, so the construction is deliberately un-stall-like and constant
across states: splayed A-frame legs, two cross braces, a head beam, a shaggy
straw splash board, a hearth at the foot. No awning stripe, no counter, no sign.

- **S1 BARE** — a drape roped over the head beam, rain running off its low
  corner, a brazier crew sheltering underneath. Only the *board* is covered; the
  truss stays fully visible, so the later reveal is recognition, not
  introduction.
- **S2 MANNED** — crew up, crucible lit. The hearth is the only steady lit thing
  between bursts (capped halo, +44 luma budget over dark stone → 94).
- **S3 MID-BURST** — the strike frame, with everything else on the sheet firing
  at once.
- **S4 COLD** — timber pulled 55 % toward ash, the thatch **burnt through in two
  bites** (a positive shape change, not just a recolour), two smoke threads at
  alpha 30 / 24.

Measured: 50 px tall against the plan's ~54.

### A2 · The crew

Read order at 1×: the hat brim (a hard horizontal), the fleece shoulder (a soft
pale mass), then the long diagonal of the handle. The scoop and the bat point
**opposite ways at every phase pair**, so two crew standing 48 px apart never
merge into one blob.

- **THROWER** T0 cocked low behind → T1 loaded high behind → T2 the throw across
  the body → T3 follow-through, scoop empty. 22 px willow handle, an open bowl at
  the tip carrying a capped molten charge on the three loaded phases.
- **STRIKER** S0 waiting (bat near-vertical) → S1 raised → S2 **CONTACT**, bat
  swung level and LEFT into the board → S3 recoil.

Every phase keeps the scoop and the bat above the deck line. A ladle dipping
through the paving is the single error that would break the apparatus read, so
the swing arcs are bounded, not free.

### A3 · The spark-burst system

- 70–120 sparks/burst (strip renders 104; the audit runs the **densest** case,
  120). 1 px heads, **3-frame fading trails**.
- Ballistic, gravity 300 px/s², launch speed 62–172 px/s.
- **Cubic angular spread** — dense near vertical, thinning to a wide skirt. That
  is what makes it a chrysanthemum instead of a uniform fan, and it is what puts
  enough sparks near vertical to actually touch the ceiling.
- **The apex clamp is applied to LAUNCH VELOCITY**, not to the drawn pixel:
  `vy ≥ −√(2·g·(cy − 512))`. So no spark is ever clipped mid-flight — the
  parabolas stay honest and simply cannot exceed 512. Measured highest pixel over
  the whole cycle: **y 512.2**.
- Ground bounce: a 0.4 s skitter with an exponentially damped hop.
- Exactly **one 2 px core pixel** at the cap, for 4 frames, at contact.
- Deterministic per-index hash, no RNG state — the same burst renders identically
  on desktop and in WASM.

The **dark beat** is doing as much work as the burst. Four bursts at 2.6 s with
~1.1 s of nothing means the eye resets and the next throw lands as an event
instead of as ambience. The strip's phase 0.00 and 1.90 frames exist to show
that the square still reads (rig, crew, crowd, smoke) with no sparks on screen.

### A4 · The rim-light pass

The storm chapter flattens the street to a black silhouette on a lightning frame.
The iron flower does the exact inverse with the same one-blit machinery: the
block is drawn onto its own SRCALPHA layer, every "opaque pixel whose neighbour
above is transparent" is found in one sweep, and that 1 px top edge is mixed 35 %
toward (255,208,150), +18 value, then hard-capped at 140 luma.

Same cost profile as the existing lightning flash. Opposite meaning. And it is
the thing that ties the festival to the storm that paid for it.

The off/on pair on the sheet is the argument: with the rim off, the near-deck
crowd is one dark mass; for two frames with it on, it is sixty separate people.

### A5 · The doused apron

A 180 px locally-saturated patch, edges marked on the sheet. Reflections are
**vertical smears, not mirrored points** — 6–10 px dither columns, alpha 45,
length keyed off the spark's own x so neighbouring columns differ, every other
pixel skipped below the second row. At 1× it reads as a shimmer rather than as a
set of drawn lines, and its alpha scales with the parent spark's, so the apron
dims *with* the burst instead of outliving it.

This buys the spark-reflection image without retuning `WEATHER_WET_DRY_RATE` and
without spending the day plan's six-second lantern-doubling window.

### A6 · Pearl + bearer

Pole overhead, a 10 px amber sphere on a figure-8 at 0.8 Hz (path traced on the
middle figure of the three), capped halo r8, and a **tassel** so it reads as
*swung* rather than floating. The bearer teases it **up-left — toward Pip**, so
the one object leading the entire parade is pointing at the player. Pearl centre
sits at world 590; halo top 582, comfortably inside the band.

### A7 · Drum-and-cymbal cart

Research: the drum rides a **wheeled platform that a second person pulls**. So
the cart has a puller at the front, not a pusher. Barrel drum at 1.5× the
busker's, head-on so the ivory head is the cart's one big shape; seated drummer
striking in antiphase; two flanking cymbal figures whose clash is a **1-frame
capped ivory disc** with the halo laid down *before* the discs (so the additive
pass lands on dark paving instead of stacking on an already-capped highlight).
83 px wide against the plan's 70.

It trails the head because the player's reveal order runs right-to-left and the
dramatic sequence is *mystery → face → mass → drum*.

### A8 · The draped dragon-head handcart

16 px of red cloth **tenting** over two horn nubs of different heights, a brow
shelf, and a snout ridge running down-forward — plus a skirt of vertical fold
lines and three ropes lashing it to the bed. Unmistakably a head. Never a face.
It arrives 148 seconds before it dances and nobody looks at it.

### A13 · The lantern arch — **flagged for your call**

Drawn at **apex y = 560**, i.e. inside the 560–640 cast/prop band the brief
mandates. The plan specifies the grandfathered garland height
(`GROUND_Y − 118` = 477), which is 83 px higher and a materially different, more
gateway-like read. **Both are on the sheet**: the solid arch is the in-band
version; the dotted curve above it is the plan-height version, shown for sign-off
rather than assumed. Six capped shells on a catenary between two poles — a
different dressing register from the stall row.

### A15 · The residue set

Three blocks in sequence: the cold rig + fresh scorch + two masks → 55 % decayed
field, one mask, an ordinary walker back on the near deck → 90 % decayed, hand-off
to Ch9. The masks come in face-up (gold, ruff, plumes) and face-down (pale paper
back, snapped elastic) so a gutter with two of them doesn't read as a repeat.

---

## 3. Measured night-cap audit — **PASS**

Measured on **rendered pixels of label-free panels**. Sheet furniture (guide
dashes, yardstick captions, the coin reference itself) is excluded — an audit
that measures its own annotations measures nothing. Round-1's first pass failed
at 245 luma for exactly that reason plus an unbudgeted additive halo; both are
fixed below.

| Metric | Value |
|---|---|
| **Hottest festival pixel** | **149.8** luma |
| Pixels over the 150 cap | **0** |
| Gold coin core | **229.5** luma — sole brightest, **53 % hotter** than anything the festival draws |
| Spark primary (191,142,82) own luma | 149.8 (sits *on* the cap by construction) |
| **Highest pixel any spark reached** | **y 512.2** (ceiling 512, headroom 0.2 px) |
| Sparks alive per burst frame (densest case) | 11 → 120 → 120 → 120 |

**Spark luma calibration** — one spark drawn at each sustain alpha over the real
night paving (bg 32.5 luma), read back off the rendered surface:

| alpha | 120 | 130 | 140 | 150 | 160 | 170 | 180 | 190 | 200 |
|---|---|---|---|---|---|---|---|---|---|
| **luma** | 88 | 92 | 96 | 102 | 106 | 111 | 115 | 120 | 124 |

So the sustain band **alpha 120–200 → effective 88–124 luma.** The plan estimated
90–130; on our actual night paving it lands one notch cooler at both ends. I have
**not** fudged the alphas to hit the estimate — the number printed on the sheet is
the number the renderer produces. Including the 3-frame trails the full rendered
spread is 50–123, the low end being the dying tail.

**Per-piece hottest (night = 0.95):**

```
burst.contact 150   burst.bloom  140   burst.apex   137   burst.fall   142
burst.dark    138   rig.manned   140   rig.bare     120   rig.cold+res 119
pearl+bearer  145   drum cart    131   draped cart  107   lantern arch 110
crew.thrower  140
```

### Two audit fixes worth recording

1. **`BLEND_RGB_ADD` ignores alpha.** The inherited `_warm_glow` idiom draws
   concentric alpha-graded circles and additively blits them — but the blend adds
   RGB outright, so the "falloff" was a hard additive disc adding up to a full
   150-luma colour wherever it landed. Over an already-lit surface that reached
   245. Replaced with the `performers_cast._warm_halo` construction: the falloff
   is baked into RGB and the **peak added luma is pre-scaled to an explicit
   budget**, so `base + budget` is the worst case *by construction* and every
   halo site is auditable as one number.
2. **Draw order for additive light.** The cymbal clash halo now goes down
   *before* the ivory discs, not after. Same for the hearth and the pearl.

---

## 4. Deliberately not done in round 1

- **The dragon itself is untouched.** `perf_dragon_dance` is intact and is the
  centrepiece; this sheet is staging *around* it (A6/A7/A8/A13), per §4.
- **No sky lanterns**, per §4's rejection — nothing enters the play space.
- **No text, no HUD marker, no confetti.**
- The lantern-arch height is presented as a choice, not resolved unilaterally.


---

## ROUND 2 REVISION (art-director punch list, all items verified on rendered pixels)

1. Parade drift +0.55x scroll: dwell 2.52s static -> 5.61s drifting; THREE bursts
   visible per pass (fallback if drift is refused: three static scaffolds).
2. Real trails: sub-stepped comets, median 11.1px (peak 24.5) -> 1276 lit px =
   2.87% of frame, luma mass 95,606 (was ~300px / 14,408), ZERO peak-luma gain.
3. Flat top killed: per-spark apex jitter -> clamped population spans 7 scanlines
   (512.1-519.0), only 3 sparks on the top line (was 24 on one).
4. Tree proportions: spread +/-62deg, G_ACC 700 -> envelope 152w x 80h
   (was 218 x 77 splash); faster fall lengthens the comets.
5. Contrast ladder: at contact the hearth/rig/paving dim (non-spark 140 -> 108)
   so the 123-luma sustain owns the frame's top.
6. Near-deck figures rescaled to 31px (spark-watch crowd, pearl-bearer,
   drum-cart crew) matching the shipped 1.5x near lane.
9. Corridor safety: spark alpha x1.0 -> x0.35 over y540->512, hue cooled to
   (170,120,90) at the arc top. FX composites with the promenade layer, before
   pillars/coins/bird; rim-light applies to promenade silhouettes only.
10. Rim-light 3 frames, 100/60/30 decay; measured avg +59.5 (spec corrected
    from the old +18 claim).
11. Lantern arch apex y 497 — the shipped night garland's own top_y
    (grandfathered geometry); the mislabeled 477 ghost is dropped.
12. Honesty: rig tops y 543, cold smoke 523, burst smoke 517 (the old
    "only sparks cross 560" claim deleted). R8 restated: the 512 spark ceiling
    is a 6px extension of the shipped steamer's y518 AND sits 13px inside the
    lowest pillar gap (y525) — sparks are behind the pillars, dim, cooled and
    attenuated there. Burst arithmetic corrected to 3 per square. Pearl dimmed
    to 127.6 with its 3px pole always legible; procession gaps widened to
    40/30 (415px total — never fits one frame).

AUDIT (round 2): hottest 149.8, 0 px over the 150 cap, apex y 512.1,
sustain 53.8-123.0 effective luma, coin core 229.5 sole-brightest.
