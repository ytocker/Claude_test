# START-as-one-object — FIVE LOCKED CONCEPT BRIEFS (Phase 3)

Each of the five sections below is self-contained. Hand ONE section to ONE
render agent. No renders were produced in this phase.

---

## 0. SHARED FACTS (repeated inside each brief — do not require this section)

**Base.** `tools/menu-design/harbour_post_holistic.py`, `VARIANT=B`
("harbour-post"), user-approved. 360x640 virtual canvas.

**The three planks are frozen.** STORE (cx102, cy386, -3.0deg), TOP 10
(cx108, cy446, +2.4deg), SETTINGS (cx100, cy506, -1.6deg), all 172x44.
Do not restyle, re-ladder, re-light or repaint one pixel of them.

**Measured against the shipped code (`python3` + `game.hud`):**
- SETTINGS rotated bbox = **x13.4-186.6, y481.6-530.4**.
- The chain's tails leave SETTINGS at **left (41.5, 522.8)** and
  **right (158.5, 526.1)**. START ties to the RIGHT tail.
- Pip x59-122, y243-292. No concept goes near him.

**Free corridor.** x>=191 above y530; full width below y530; floor y624.
START must be the lowest control. Tap rect >=48dp, disjoint from
SETTINGS' x13-187 / y482-530.

**Local backdrop (orchestrator-verified).** The START quadrant is dark at
BOTH poles: **L36 day / L21 night**. It never goes bright. Every concept is
therefore a **light-value figure** with a single keyline — no two-step
contour. **No body colour below ~L70 for a large mass.**

**TYPE BUDGET — corrected, measured.** The critique's table used
`f.size("START") + track*4`. `hud._tracked_label` actually sums the
*per-glyph* render widths, which is 2-3px wider. Measured with
`_hud._font(size, True)`:

| size | f.size() | tracked+2 (REAL) | ink bbox |
|---|---|---|---|
| 17 (utility labels) | 54x19 | **65** | 54x12 |
| 22 | 72x25 | **83** | 72x15 |
| 24 | 78x27 | **88** | 78x17 |
| 26 | 85x30 | **95** | 85x18 |
| 30 | 97x34 | **108** | 96x21 |

All five briefs below are sized against the REAL column. Two footprints grew
because of it; both are called out with arithmetic.

**Colour gate.** Separate from gold `(240,192,64)` H43.6 C0.690 L191.8 and
rust `(240,55,55)` H0.0 C0.725 L110.3 by **dH>=110** OR **chroma-ratio>=3x
with dLuma>=35**. chroma = (max-min)/255; luma = 0.299R+0.587G+0.114B.

**DIRECTIVE 13 — binding on every render.** Publish (a) a 1x thumbnail strip
at PHASE 0.0 / 0.20 / 0.45 / 0.65, (b) a greyscale pass, (c) a 1x crop of the
START quadrant alone. Every risk in this set is a thumbnail risk.

---

## DISTINCTNESS AT 1x — how each silhouette differs in KIND

1. **`ring-out`** — the only silhouette that WIDENS downward: a convex
   trapezoid flaring to a scalloped bottom edge, hanging free on one line
   with a thin rope tail below it. Nothing else on screen has a scalloped
   or convex-flared base.
2. **`beacon`** — the only UPRIGHT silhouette with a pitched triangular cap
   over a straight-sided body on a flat heavy base, and the only object that
   emits light (its mass is L183-232 where every other object is opaque). Bell
   vs lantern is the closest pair in the set; the triangle cap, the flat foot
   and the emission separate them decisively.
3. **`clear-arm`** — the only DIAGONAL mass on the entire screen: a 45deg bar
   with a forked end crossing a vertical post. Everything else in the menu is
   horizontal or upright.
4. **`colours-up`** — the only silhouette with a deep FORKED end (26px bite)
   AND non-parallel curved long edges from the warp; the only shape whose
   outline changes every frame.
5. **`the-drop`** — the only CLOSED CURVE with an interior void: a wide flat
   ellipse with a hole in it, plus a lid standing behind. No straight
   silhouette edges at all.

Pairs on watch from the critique are resolved: `clear-arm` is now permanently
diagonal and `colours-up` gains a 26px fork plus a curled fly, so they no
longer share orientation, end-treatment or edge quality.

---
---

# BRIEF 1 — `ring-out` (the harbour bell)

**WHAT IT IS.** A cast-bronze harbour bell hanging on the last rope of the
sign chain, START struck across its flared skirt, with a hemp lanyard dropping
to a monkey's-fist knot at thumb height — control and sign are the same thing
because the bell IS the word's surface, and the thing you pull is the thing
that rings it.

**STRUCTURAL TIE TO THE CHAIN.** The chain's last rope stops being a mooring
line and becomes the **bell's hanger**: one continuous run, cloud -> STORE ->
TOP 10 -> SETTINGS -> bell. The chain's terminal weight. The planks hang; this
is what they hang *toward*. It reuses the same `rope()` catenary and the same
`_iron_ring` hardware the planks use, at the crown.

### Fixed base facts
Base `tools/menu-design/harbour_post_holistic.py` `VARIANT=B`, 360x640.
The three planks (STORE cx102/cy386/-3.0, TOP 10 cx108/cy446/+2.4, SETTINGS
cx100/cy506/-1.6, all 172x44) are **frozen** — do not touch. SETTINGS' rotated
bbox is x13.4-186.6, y481.6-530.4. The chain's right tail is at **(158.5,
526.1)**. Pip is x59-122, y243-292. Corridor: x>=191 above y530, full width
below y530, floor y624. Backdrop in this quadrant: **L36 day / L21 night** at
both poles — be a light figure, single keyline, no two-step contour, no body
colour under ~L70 for a large mass.

### Construction (geometry, all screen coords)
ONE closed polygon plus its hardware. No rectangle anywhere.

- **Crown.** `_iron_ring(surf, 258, 532, r=5)`. Two staple arcs drop from the
  ring to the shoulder, y532-542, ~16 apart at x250 and x266.
- **Body profile**, centred **x258** (this x is load-bearing: it keeps the tap
  rect clear of SETTINGS — see below):
  - shoulder, flattened dome, y542-551, width 40 -> 54
  - waist, concave, y551-562, width 54 -> 64
  - flare, convex, y562-594, width 64 -> 130, profile
    `w(y) = 64 + 66*((y-562)/32)**0.45` (widens early so the type band has
    room; at y575 this gives w=108)
  - sound-bow, y594-603, width 130 -> **132**, thicker and brighter than the
    skirt, with **five shallow scallops** bitten out of the bottom edge.
  - Lip therefore spans **x192-324**, bell bottom **y603**.
- **Reeding.** Two incised lines across the skirt at y566 and y571 (1px
  `(34,96,94)` under 1px `(150,222,206)`).
- **Modelling.** Five-stop vertical bronze gradient plus two speculars: a hot
  vertical band at x238-248 (left of centre) and a cool bounce down x300-312.
  Scallops cut via a scratch SRCALPHA mask + `BLEND_RGBA_MIN` — the same
  pattern `timber_board` uses at :255.
- **Clapper.** Iron pear, x252-264, y603-610, hanging just below the lip.
- **Lanyard (the affordance).** 3px hemp from the clapper eye (258,610),
  sag 4, to a **monkey's fist** centred **(278, 617), r6** — three visible
  loops, bottom y623. This is the "pull me" note; the chain hangs, this is
  the one thing that invites a hand.
- **Hang.** `rope(surf, (158.5,526.1), (258,532), sag=10, width=3)`. The two
  ends are only 6px apart in y, so the **sag is what proves the load** — draw
  it at 10, not 5, and let the belly sit at y~540. The whole bell hangs 5deg
  off true (rotozoom the cached body), matching the planks' hang.
- **Idle:** +-1.5deg sway. **Tap:** swing 8deg with overshoot + two expanding
  bronze ring-arcs off the lip.

### Published tap rect
**`pygame.Rect(192, 526, 132, 97)`** = x192-324, y526-623.
- x192 > SETTINGS' right edge 186.6 -> **disjoint** (their y ranges overlap by
  4px, so the x separation is what carries it; this is why the bell is centred
  at x258 and not x250).
- Bottom 623 < 624 floor. 132x97 clears 48dp on both axes.
- The union covers the bell body (the big aimable mass, ~132x77) **and** the
  lanyard + knot, so the affordance and the hit area agree. The 3-loop knot is
  never the target on its own.
- START is the lowest control: its top (y526) is 20px below SETTINGS' centre
  and its mass is entirely under SETTINGS' bottom edge (y530).

### Colour table
| role | RGB | H | C | luma | vs L36 day | vs L21 night | dH gold/rust | ratio gold/rust |
|---|---|---|---|---|---|---|---|---|
| bell bronze (body) | (40,120,116) | 177.0 | 0.314 | **95.6** | +59.6 | +74.6 | 133.4 / 177.0 | 2.20x / 2.31x |
| bronze deep (shade stop) | (34,96,94) | 178.1 | 0.243 | **77.2** | +41.2 | +56.2 | 134.4 / 178.1 | 2.84x / 2.98x |
| polished lip + reeding | (96,196,180) | 170.4 | 0.392 | 164.3 | +128.3 | +143.3 | 126.8 / 170.4 | 1.76x / 1.85x |
| verdigris keyline | (150,222,206) | 166.7 | 0.282 | 198.6 | +162.6 | +177.6 | 123.0 / 166.7 | 2.44x / 2.57x |

Every stop is >=L77 — the darkest bronze still sits +41 over the day backdrop.
The gate passes on the **dH arm** (all >=123deg from gold, >=166deg from rust).
The single keyline is the **bright** verdigris line on the top/left arris,
hue-tinted to the object's own family, not a neutral white.

### Type
**26px, `track=2`, measured tracked run = 95px, ink 18px tall.**
- Seated LOW: ink spans **y575-593**, sitting directly on the sound-bow's top
  edge (y594). Centre (258, 584).
- The skirt at y575 is **108** wide -> 95 fits with **6.5px clear each side**.
  (30px would be 108 tracked and overflow — that is why the ruling is 26.)
- **This is the only concept that keeps arced type.** Total arc 6deg: per-glyph
  angles `[+3, +1.5, 0, -1.5, -3]`, per-glyph dy `[0, +1.2, +2, +1.2, 0]`
  (sagitta 2px, centre lowest, following the lip's curve).
- Struck in relief: gold-pale `(255,232,168)` glyph over a 1px-down dark twin
  in `(34,96,94)`, so it reads incised into bronze rather than printed on it.
- 26px is **46% larger** than the 17px utility labels (95 vs 65 tracked).

### What changes elsewhere
- **The timber post and the diagonal brace are DELETED.**
- **The bell-cot is DELETED** (directive 3). The bell hangs on the chain
  alone. A bell cannot hang from a cross-head and from a rope arriving from a
  cloud 200px away.
- The mooring `_iron_ring` at (214,500) goes; the crown ring replaces it.
- **Ground:** nothing is planted. The ground band stays exactly as it is.
- **`_best_tag` moves** from (276,610) — where the knot now is — to
  **(96, 566)** (x44-148, y554-578), clear of the bell's x192 left edge.

### Shipped helpers to reuse
`rope`, `_iron_ring`, `nail`, `soft_shadow` (tier `"raised"`, with the bell's
own rotated mask), `under_shade`, `_grad_fill`, `_mix`, `hud._tracked_label`
(wrap the glyph loop in a rotozoom, cache on `(char, size, angle)`),
`store_cards.gloss_sweep` for the specular pattern. Cache the bell body per
biome key on a 140x110 surface; rotozoom for sway.

### Directive 13 (binding on this render)
Publish a 1x thumbnail strip at PHASE 0.0 / 0.20 / 0.45 / 0.65, a greyscale
pass, and a 1x crop of the START quadrant alone.

---
---

# BRIEF 2 — `beacon` (the lantern whose light spells the word)

**WHAT IT IS.** A three-facet glazed harbour lantern, iron and glass with a
timber cap, hanging from a cranked iron bracket, its lit centre panel carrying
START in relief — control and sign are the same thing because the word has no
substrate at all: it is the light, or the shadow in the light.

**RULING ON RECORD:** cleared against the round-6 `lantern-street` rejection.
That failed on *composition*, not on lanterns. Keep this a hard-edged
iron-and-glass vessel with a timber cap — a different object class from the
shipped soft `pillar_variants.draw_paper_lantern`. Do not let them converge.

**STRUCTURAL TIE TO THE CHAIN.** The chain's last rope **belays to an eye on
the bracket** — a termination into structure, deliberately different from
`ring-out`'s suspension: this rope is made fast, not carrying load. The
lantern's **roof cap is a miniature of the plank silhouette**: the same
chamfer + V-notch cut profile, in the same timber, folded into a pitched cap.
The iron corner posts are the plank nails drawn out into iron.

### Fixed base facts
Base `tools/menu-design/harbour_post_holistic.py` `VARIANT=B`, 360x640.
The three planks (STORE cx102/cy386/-3.0, TOP 10 cx108/cy446/+2.4, SETTINGS
cx100/cy506/-1.6, all 172x44) are **frozen**. SETTINGS' rotated bbox is
x13.4-186.6, y481.6-530.4. The chain's right tail is at **(158.5, 526.1)**.
Pip is x59-122, y243-292. Corridor: x>=191 above y530, full width below y530,
floor y624. Backdrop: **L36 day / L21 night** at both poles — light figure,
single keyline, no body colour under ~L70 for a large mass.

### Construction (geometry, all screen coords)
Overall body **x211-333**, roof/collar flare to **x208-336**, **y466-592**.
Dropped ~8px from the original spec so the roof no longer sits level with
SETTINGS' band (directive: layout table).

- **Bracket (replaces the timber post + brace entirely).** A slim iron
  standard **x196-204** (8 wide) rising from a stone footing pad
  (x188-212, y596-606) to y462, **cranked right** along y462 to x272, with a
  scrolled stay from (200,494) to (252,466). No second timber competes with
  the planks. x196 clears SETTINGS' right edge by 9px.
- **Bail.** `_iron_ring(surf, 272, 466, r=6)`; two straps fork around the gold
  finial down to the roof shoulders at (256,486) and (288,486).
- **Roof.** Timber pitched cap: apex (272,478), base 132 wide **x206-338**,
  eave line y496-500 with a chamfered overhanging lip. The eave's end faces
  carry the planks' **V-notch** at full size. Gold finial x268-276, y474-480.
- **Glazed drum, y500-572, THREE facets** (directive 5):
  - rake facet x211-219 (8), iron corner post x219-221 (2),
  - **centre glass x221-323 = 102 unbroken**,
  - iron corner post x323-325 (2), rake facet x325-333 (8).
  - One glazing bar across the centre glass at its lower third, y548.
- **Base collar, y572-592**, 128 wide **x208-336**: heavy iron with a drip lip
  and three vent slots at x236/272/308.
- **Type polarity — render BOTH at 1x side by side before committing**
  (directive 5). **Polarity A is the primary build**: a **dark word in relief
  against a fully lit panel** — the panel is bright, the letters are the dark
  figure with a 1px pale top arris so they read as raised glass. **Polarity B**
  is the comparison: bright knockout letters on smoked glass. B is expected to
  clog — the T-stem is fine but the A and R counters fall to 2-3px islands at
  24px. Prove it at 1x rather than asserting it.
- **Halo — NO BLUR, NO BLOOM** (directive 6). Build it as **3-4 dilations of
  the panel mask at falling alpha, hard-stepped**, on a scratch SRCALPHA
  layer, following `store_design._build_aura`'s numpy-free branch (~line 200,
  which exists precisely because numpy is absent on pygbag). Stepped falloff
  keeps the glyph edge crisp at this scale.
- **ZERO pixels of light on the three planks** (directive 7). Wrap every halo
  and light-pool blit in `surf.set_clip(pygame.Rect(190, 0, 170, 640))` and
  restore after. SETTINGS ends at x186.6, so a clip at x>=190 is provable, not
  approximate. This costs beacon its "diegetic plank lighting" argument —
  accept the loss; do not sneak it back at low alpha.
- **Light pool** (inside the clip): an elliptical cyan wash on the ground band
  centred (272,604), 150x26, plus a wash up the bracket's inner face.
- Specular: one diagonal sweep across the centre glass — copy the
  `store_cards.gloss_sweep` pattern (:618), composited `BLEND_ADD` off a
  cached masked layer.
- **Idle:** flame breathes +-6% at ~1.2 Hz with jitter — one
  `fill(..., BLEND_RGBA_MULT)` on the cached 128x126 layer per frame.
  **Tap:** a flare washing the bottom band for 0.2s.
- Halo alpha keys off the `biome` phase so the lantern earns the 5-min cycle:
  at night it is the brightest object on screen and pulls the eye to the thumb.

### Published tap rect
**`pygame.Rect(208, 474, 128, 118)`** = x208-336, y474-592.
- x208 > SETTINGS' right edge 186.6 -> **disjoint** by 21px.
- Bottom 592 < 624. 128x118 clears 48dp. Live fill (roof + drum + collar)
  ~82% of the rect.
- START is lowest: the lantern's mass runs to y592, 62px below SETTINGS'
  bottom edge.

### Colour table
| role | RGB | H | C | luma | vs L36 day | vs L21 night | dH gold/rust | ratio gold/rust |
|---|---|---|---|---|---|---|---|---|
| lit glass, top stop | (196,248,248) | 180.0 | 0.204 | **232.5** | +196.5 | +211.5 | 136.4 / 180.0 | 3.38x / 3.56x |
| lit glass, bottom stop | (108,214,220) | 183.2 | 0.439 | **183.0** | +147.0 | +162.0 | 139.6 / 176.8 | 1.57x / 1.65x |
| word in relief (polarity A) | (18,78,92) | 191.4 | 0.290 | 61.7 | +25.7 | +40.7 | 147.7 / 168.6 | 2.38x / 2.50x |
| iron collar / posts / bracket | (86,92,104) | 220.0 | 0.071 | **91.6** | +55.6 | +70.6 | 176.4 / 140.0 | 9.78x / 10.28x |
| arc cyan (halo, pool) | (120,236,238) | 181.0 | 0.463 | 201.5 | +165.5 | +180.5 | 137.4 / 179.0 | 1.49x / 1.57x |

Every large mass is >=L91.6. Note the old `collar iron (66,70,80)` measures
**L69.9** — right on the reject line; it is replaced by `(86,92,104)` L91.6.
The relief word at L61.7 is a *letterform*, not a mass, and it never carries a
silhouette against the sky — it sits inside an L183-232 panel (dLuma 121-171).
The timber cap uses the shipped `timber_board(exposure=110)` ladder (lit
~L141) — inherited material, not a new gate colour.

### Type
**24px, `track=2`, measured tracked run = 88px, ink 17px tall.**
- Set on the centre glass, centred (272, 534).
- Centre glass is **102** wide -> 88 fits with **7px clear each side** before
  the 2px iron corner posts. This is why the drum is 122 wide with 8px rakes
  and 2px posts rather than the original five facets: five facets across 124
  put the centre at ~52px and would have forced ~14px type.
- 24px is **35% larger** than the 17px utility labels (88 vs 65 tracked).
- Polarity A: `(18,78,92)` glyphs + a 1px `(196,248,248)` top arris.
  Polarity B (comparison only): `(236,252,250)` glyphs knocked out of
  `(20,68,84)` smoked glass.

### What changes elsewhere
- **Timber post DELETED, diagonal brace DELETED** — the brace becomes the
  bracket's scroll stay.
- **Mooring:** the chain's right tail runs from (158.5,526.1) **up-right** to
  a belay eye at (200, 512) on the bracket standard, `sag=3` — near-taut,
  made fast, with a short lashing turn. Rising is correct here: this rope
  terminates into structure, it does not carry the lantern.
- **Ground:** a stone footing pad (x188-212, y596-606) under the standard,
  plus the cyan light pool. The ground band itself is untouched.
- **`_best_tag` moves** from (276,610) to **(280, 610)** (x228-332,
  y598-622) — it sits inside the light pool, which is legitimate (it is not a
  plank).

### Shipped helpers to reuse
`store_design._build_aura` (numpy-free stepped halo — the sanctioned path),
`store_cards.gloss_sweep` (:618), `hud._tracked_label` (:1189), `soft_shadow`,
`under_shade`, `timber_board` (roof cap, exposure 110), `_board_points`
(the V-notch profile for the eave ends), `nail`, `_iron_ring`, `rope`,
`_grad_fill`. Cache one body per biome key.

### Directive 13 (binding on this render)
Publish a 1x thumbnail strip at PHASE 0.0 / 0.20 / 0.45 / 0.65, a greyscale
pass, and a 1x crop of the START quadrant alone. **Additionally publish both
type polarities at 1x, side by side.**

---
---

# BRIEF 3 — `clear-arm` (the launch signal) — REWORKED

**WHAT IT IS.** A lower-quadrant signal arm resting **permanently at -45deg
"clear"** — a limewashed tapered blade with a fishtail end, pivoted on a
spectacle casting at the head of a hooped timber post, carrying START in ink
down its length, held down by the sign chain acting as its operating wire —
control and sign are the same thing because the blade's *position* is the
message and the word is painted on the mechanism that makes it.

**THIS IS A REWORK.** The previous spec failed three ways: a 96x28 horizontal
blade read as a fourth plank; 64px of ink field could not hold 80px of type;
and an L28 lacquer body was d8 from the day backdrop, i.e. invisible. The
replacement keeps the signal thesis and the chain tie **verbatim** and kills
the horizontal blade.

**STRUCTURAL TIE TO THE CHAIN — KEEP VERBATIM.** The chain's last rope becomes
the **operating wire**. It leaves SETTINGS, runs through a guide pulley on the
post, and ties to the arm's crank. The sign chain literally works the control.
And the mechanism makes the line quality *necessary*, not decorative: a
lower-quadrant arm is fail-safe — the counterweight returns it to danger if
the wire goes slack, so the wire must be **taut and dead straight with one
kink at the pulley**, against three sagging hangs above it. The utilities
hang; START is rigged. **Keep this contrast verbatim — it is the best idea in
the document.**

### Fixed base facts
Base `tools/menu-design/harbour_post_holistic.py` `VARIANT=B`, 360x640.
The three planks (STORE cx102/cy386/-3.0, TOP 10 cx108/cy446/+2.4, SETTINGS
cx100/cy506/-1.6, all 172x44) are **frozen**. SETTINGS' rotated bbox is
x13.4-186.6, y481.6-530.4. The chain's right tail is at **(158.5, 526.1)**.
Pip is x59-122, y243-292. Corridor: x>=191 above y530, full width below y530,
floor y624. Backdrop: **L36 day / L21 night** at both poles.

### Construction (geometry, all screen coords)
- **Post.** Timber (not iron — timber+iron is the base's own vocabulary and a
  vertical is not a plank), `timber_board(14, 128, exposure=110)`, **x211-225,
  y484-612**, standing into the ground band. Cast finial y484-492. Three iron
  hoops at y500, y540, y580.
- **Pivot / spectacle plate.** Figure-eight iron casting centred **(218,500)**,
  two 20px lenses stacked along the blade axis. At clear, the **lit** lens is
  in the lamp position (arc cyan); the upper lens is dark.
- **Blade — the idle state is -45deg, permanently.** Axis unit vector
  `u = (0.7071, 0.7071)` (down-and-right, the way the bird flies), root
  centred on the pivot, **length 138**, width **32 at the root tapering to 28**
  at the fishtail shoulder.
  - Tip at **(315.6, 597.6)**. Corners **(228.6,489.4) (207.4,510.6)
    (326.2,587.0) (305.0,608.2)**; bbox **x207.4-326.2, y489.4-608.2**.
  - The corner that sits above y530 is at x207.4 — **16px clear** of the
    x>=191 line and **21px clear** of SETTINGS.
  - **Fishtail:** a V bitten into the free end, depth 12, opening 28 — the
    planks' `_board_points` notch promoted from decoration to silhouette, at
    full size, as the defining feature.
  - **Rolled top edge:** a 2px bright arris `(222,236,240)` along the
    upper-left long edge; a 1px hue-tinted contour `(64,80,92)` around the
    whole blade. **The keyline is tinted to the object's own hue** — the
    previous 1px bone keyline on ink was a near-white outline, which is the
    "bolted-on" inversion `T_EDGE` exists to prevent.
  - **Rivets:** two rows of three, **sunk** (slate-ink pits with a 1px pale
    lower arris), near the root only. Not proud, not a highlight strip.
- **Counterweight.** A crank lever from the pivot up-and-left to a cast iron
  weight centred **(202, 482), r9** -> x193-211, y473-491. **x193 > 186.6, so
  it is disjoint from SETTINGS by 6px.** It is RAISED, which is what "the wire
  is pulling and the arm is at clear" looks like — the one heavy round note,
  and it is mechanically true.
- **Operating wire (verbatim contrast).** From the chain's right tail
  **(158.5,526.1)** dead straight down-right to a **guide pulley** bracket at
  **(208, 566)** on the post's left face; one kink; then dead straight **up**
  the post's left face at x204 to the crank eye at **(204, 490)**. `sag=0` on
  both runs, drawn with `rope()`'s two-tone lay so the material still matches.
- **Lattice stay REPLACES the fat diagonal brace:** a zigzag of 2px iron
  struts from (225,560) triangulating down-right to an iron eye in the ground
  band at (262,608). Thin enough that the corner stops feeling boxed in.
- **Idle:** a 0.5deg tremor keyed off the existing `weather` gust state.
  **Tap:** a snap-and-overshoot along the same 45deg axis (the arm bites down
  another 6deg and rebounds) with the lens flaring — not a state change,
  because the arm is already clear. "Line clear, proceed" is the literal
  semantic of the button.

### Published tap rect
**`pygame.Rect(194, 476, 134, 136)`** = x194-328, y476-612.
- x194 > SETTINGS' right edge 186.6 -> **disjoint** by 7px.
- Bottom 612 < 624. 134x136 clears 48dp comfortably.
- **Honest live-area note:** a 45deg blade fills only ~34% of its
  axis-aligned bbox (blade 138x30 + post 14x128 + weight ~254px of 18224).
  This rect is the **whole START quadrant panel** and nothing else in it is
  interactive, so the generosity is legitimate; tapping the post or the
  counterweight also fires, which is correct — they are all one signal.
- START is lowest: the blade runs to y608, 78px below SETTINGS' bottom edge.

### Colour table — values INVERTED (the round-7 `bleached-board` precedent)
| role | RGB | H | C | luma | vs L36 day | vs L21 night | dH gold/rust | ratio gold/rust |
|---|---|---|---|---|---|---|---|---|
| limewash body | (176,196,204) | 197.1 | 0.110 | **190.9** | +154.9 | +169.9 | 153.5 / 162.9 | 6.29x / 6.61x |
| limewash shade (lower-right edge) | (128,150,160) | 198.8 | 0.125 | **144.6** | +108.6 | +123.6 | 155.1 / 161.2 | 5.50x / 5.78x |
| bright arris (upper-left) | (222,236,240) | 190.0 | 0.071 | 233.0 | +197.0 | +212.0 | 146.4 / 170.0 | 9.78x / 10.28x |
| tinted contour keyline | (64,80,92) | 210.0 | 0.110 | 76.6 | +40.6 | +55.6 | 166.4 / 150.0 | 6.29x / 6.61x |
| slate ink (type + rivets) | (34,44,54) | 210.0 | 0.078 | 42.1 | +6.1 | +21.1 | 166.4 / 150.0 | 8.80x / 9.25x |
| bone tip band | (240,236,226) | 42.9 | 0.055 | 236.1 | +200.1 | +215.1 | 0.8 / 42.9 | 12.57x / 13.21x |
| lit lens | (120,236,238) | 181.0 | 0.463 | 201.5 | +165.5 | +180.5 | 137.4 / 179.0 | 1.49x / 1.57x |

- The body is now **L190.9 — +155 over the day backdrop, +170 over night.**
  The rejected lacquer ink `(26,28,34)` measures **L28.1: d7.9 day, d7.1
  night**, i.e. invisible. That is why the values are inverted.
- The gate passes on the **dH arm** for everything except bone, which passes
  on the **chroma arm** (12.6x / dLuma 44.3 vs gold, 125.8 vs rust).
- **Slate ink at L42.1 is a letterform, not a mass** — it never carries a
  silhouette against the sky; it sits inside an L191 body at dLuma 149.
- **The bone band is OFF the type run** (directive): it is now the outer 28 of
  the blade only, so it is a **tip marker**, not a competitor to the word.
  Previously it was the brightest object in the quadrant carrying no
  information.

### Type
**24px, `track=2`, measured tracked run = 88px, ink 17px tall**, set flat and
then rotated -45deg with the blade (single whole-word rotozoom, one transform).

Run budget along the 138 axis:
| from | to | length | content |
|---|---|---|---|
| 0 | 16 | 16 | pivot boss clearance |
| **16** | **104** | **88** | **START in slate ink** |
| 104 | 110 | 6 | gap |
| 110 | 138 | 28 | bone tip band + fishtail bite |

**Sum = 138.** This is why the blade is **138 long, not the 124 in the
directive**: 88 (measured, not the 86 in the critique's table) + 16 + 6 + 28
= 138 with zero slack at 124. Stated with numbers as required; the footprint
above shows 138 still clears the corridor by 16px and the y624 floor by 16px.

Perpendicular: the ink is 17 tall in a blade 32 wide at the root falling to
~29 where the word ends -> **6px clear each side**.

Ink on limewash needs **no dark twin and no outline** (dLuma 149), which is
what buys the full 88px — the previous spec lost 6px to an outline it also
could not afford. 24px is **35% larger** than the 17px utility labels.

### What changes elsewhere
- **The fat diagonal brace is DELETED**, replaced by the thin lattice stay.
- **The mooring `_iron_ring` at (214,500) is DELETED** — the rope no longer
  moors, it works.
- **The chain's last rope changes line quality**: taut, straight, one kink.
- **Ground:** a stone base block with a bolt ring under the post at
  (206-230, 604-616), plus the lattice stay's ground eye at (262,608).
- **`_best_tag` moves** from (276,610) to **(100, 570)** (x48-152, y558-582),
  out of the blade's swept quadrant.

### Shipped helpers to reuse
`timber_board` (post, exposure 110), `_board_points` (the fishtail is this
notch at full size), `soft_shadow` with the blade's rotated mask,
`under_shade`, `rope` (drawn with `sag=0` for the wire), `nail`, `_iron_ring`,
`_grad_fill`, `hud._tracked_label` (:1189), `store_cards.gloss_sweep` for the
lens specular. Cache the blade once and rotozoom per frame (~12 `draw.line`
calls for the lattice).

### Directive 13 (binding on this render)
Publish a 1x thumbnail strip at PHASE 0.0 / 0.20 / 0.45 / 0.65, a greyscale
pass, and a 1x crop of the START quadrant alone. **The fourth-plank read is
the specific risk this rework exists to kill — it can only be judged at 1x.**

---
---

# BRIEF 4 — `colours-up` (the launch flag)

**WHAT IT IS.** A deep-swallowtail signal flag bent onto a halyard and flying
from a short jack-staff, its field carrying START in gold, the halyard's fall
coiled on a cleat — control and sign are the same thing because the flag is
the message *and* the only soft, moving thing on a screen of timber, iron and
rope, so the eye lands on the thumb target without being told to.

**STRUCTURAL TIE TO THE CHAIN.** The chain's last rope **IS the halyard**. It
leaves SETTINGS' tail, reeves through the iron block at the masthead, and the
flag's head cringle bends onto it — so the flag's hoist edge is literally
where the whole chain terminates, and the fall carries on down to a cleat with
a real hemp coil. The **swallowtail is the planks' V-notch rendered in cloth**:
the same bite out of the end face, softened by material. The iron grommets
down the luff are the plank nails.

### Fixed base facts
Base `tools/menu-design/harbour_post_holistic.py` `VARIANT=B`, 360x640.
The three planks (STORE cx102/cy386/-3.0, TOP 10 cx108/cy446/+2.4, SETTINGS
cx100/cy506/-1.6, all 172x44) are **frozen**. SETTINGS' rotated bbox is
x13.4-186.6, y481.6-530.4. The chain's right tail is at **(158.5, 526.1)**.
Pip is x59-122, y243-292. Corridor: x>=191 above y530, full width below y530,
floor y624. Backdrop: **L36 day / L21 night** at both poles.

### Construction (geometry, all screen coords)
- **Mast (a jack-staff, not a topmast — accepted).** Timber,
  `timber_board(8, 92, exposure=104)`, **x196-204**, base in the ground band
  at y608, truck at **y516**, raked 4deg to the right (leaning away from
  SETTINGS). x196 clears SETTINGS' right edge by 9px.
- **Masthead block.** Iron sheave at **(202, 526), r5**. **MASTHEAD IS y526,
  <= the y532 ceiling** (directive 9). This is what keeps START lowest.
- **PUBLISHED FLAG RECT: `pygame.Rect(204, 532, 140, 82)`** = x204-344,
  y532-614 (the warped/curled bbox; the nominal untwisted cloth is
  x204-344, y536-608 = 140x72).
  - **The flag flies RIGHT**, hoist against the mast, so the eye reads
    left-to-right into the swallowtail.
  - hoist band **x204-218** (14, darker), field **x218-318** (100),
    swallowtail notch vertex **x318**, fly tips **x344**.
  - **Swallowtail bite = 26px** (directive 9 requires >=22). Upper fly tip
    (344,546), lower fly tip (344,602), notch vertex (318,570).
- **The fly is CURLED** (directive 9), so top and bottom edges are visibly
  non-parallel at 1x:
  - top edge: y538 at the hoist -> rises to y532 at x290 -> the curled tip
    falls to y546 at x344, showing a **6px sliver of the reverse (darker)
    side** where the cloth rolls over.
  - bottom edge: y606 at the hoist -> falls to y612 at x300 -> rises to y602
    at the fly tip.
- **Warp — CLOTH ONLY.** 14 vertical strips across the 140 length. Each
  strip's top and bottom edges follow a travelling sine, **amp 4px, lambda 70,
  phase = t*1.6**; each strip is shaded by its local normal — crests +18%,
  troughs -18%. 14 quads + 14 subsurface blits per frame, no numpy, identical
  on both targets.
- **THE WARP DOES NOT TOUCH THE WORD** (directive 10). Render START flat ONCE
  with `hud._tracked_label`, cache it, then apply the local warp as **a single
  whole-word integer y-offset plus a <=2deg rotation**. **No per-column
  sampling.** A 1px-granularity y-offset stair-steps the horizontals of S, T,
  A and R, and a 3px stroke broken by 1px steps reads as a *broken* stroke on
  a phone.
- **Grommets:** three iron grommets down the luff at (210,542), (210,572),
  (210,602), drawn with `nail`'s iron ramp.
- **Border:** 2px `GOLD_BRIGHT (240,192,64)` following the warped outline,
  swallowtail included.
- **Cleat + fall.** The fall drops from the block down the mast's LEFT face
  from (198,528) to a timber cleat at **(192, 588)** (below y530, so full
  width is free), with a figure-eight hemp coil hanging to y612.
- **Idle:** the flag ripples continuously — a living primary CTA, the only
  continuous motion on the menu. **Tap:** it snaps taut and two-blocks up 6px
  with a cloth crack. **First launch:** run it *up* from half-hoist over 0.4s —
  colours up, we're flying.

### Published tap rect
**`pygame.Rect(196, 528, 150, 86)`** = x196-346, y528-614.
- x196 > SETTINGS' right edge 186.6 -> **disjoint** by 9px.
- Bottom 614 < 624. 150x86 clears 48dp. Live cloth ~73% of the rect
  (140x72 minus the 26px bite). Includes the mast, which is correct — mast,
  halyard and flag are one object.
- START is lowest: the cloth runs y536-608, entirely below SETTINGS' bottom
  edge (y530).

### Colour table
| role | RGB | H | C | luma | vs L36 day | vs L21 night | dH gold/rust | ratio gold/rust |
|---|---|---|---|---|---|---|---|---|
| teal field | (20,132,146) | 186.7 | 0.494 | **100.1** | +64.1 | +79.1 | 143.0 / 173.3 | 1.40x / 1.47x |
| teal crest | (58,178,190) | 185.5 | 0.518 | **143.5** | +107.5 | +122.5 | 141.8 / 174.5 | 1.33x / 1.40x |
| teal trough | (16,104,116) | 187.2 | 0.392 | **79.1** | +43.1 | +58.1 | 143.6 / 172.8 | 1.76x / 1.85x |
| hoist band / reverse side | (18,96,108) | 188.0 | 0.353 | **74.0** | +38.0 | +53.0 | 144.4 / 172.0 | 1.96x / 2.06x |
| type: gold-pale | (255,232,168) | 40.0 | 0.341 | 231.6 | — | — | (is the plank gold) | — |

Every cloth value is >=L74 — the trough and hoist band were lifted from the
original `(12,86,98)` L65.3 and `(14,74,84)` L57.2, both of which fell under
the L70 floor. Gate passes on the **dH arm** (>=141deg from gold, >=172deg
from rust). Gold-pale on teal field is **dLuma 131.5** and complementary — the
strongest legibility pairing available, and being complementary it reads as
the *same* gold the planks use rather than a second yellow.

### Type
**24px, `track=2`, measured tracked run = 88px, ink 17px tall.**
- Centred **(268, 570)** -> ink x224-312 inside the x218-318 field.
- **6px clear each side.** Height 17 in a 72-deep flag — set in the flag's
  flattest third, well inside the border.
- 24px is **35% larger** than the 17px utility labels (88 vs 65 tracked).

**Why the flag is 140 long, not the 112 in the concept:** the critique sized
24px type "into a 112 hoist" without subtracting the mandated swallowtail. At
112 with a 26px bite and a 14px hoist band the usable field is **72px** and
88px of type does not fit. 140 = 14 (hoist band) + 100 (field) + 26 (bite).
Fly tip x344 leaves 16px to the canvas edge.

### What changes elsewhere
- **The timber post and the fat diagonal brace are DELETED**, replaced by the
  jack-staff plus **two thin shroud lines** to iron eyes in the ground band at
  (176,606) and (224,606) — diagonals instead of a fat timber, which opens the
  corner.
- **The mooring `_iron_ring` at (214,500) is DELETED** — the chain now reeves
  through the masthead block and terminates properly: block, fall, cleat, coil.
- **Ground:** a small timber mast-step at the foot (x190-210, y602-612) and
  the two shroud eyes. The ground band itself is untouched.
- **`_best_tag` moves** from (276,610) to **(100, 566)** (x48-152, y554-578).

### Shipped helpers to reuse
`timber_board` (mast, mast-step, cleat), `rope` (halyard fall + shrouds +
coil), `nail` (grommets), `_iron_ring` (masthead block), `soft_shadow` with
the flag's warped mask, `under_shade`, `_grad_fill`, `_mix` (strip shading),
`hud._tracked_label` (:1189) rendered flat once and cached,
`store_cards.gloss_sweep` for the crest sheen. Cache the flat flag + type;
only the warp runs per frame.

### Directive 13 (binding on this render)
Publish a 1x thumbnail strip at PHASE 0.0 / 0.20 / 0.45 / 0.65, a greyscale
pass, and a 1x crop of the START quadrant alone. **Warped-type softening and
the depth of the swallowtail read are both 1x-only judgements.**

---
---

# BRIEF 5 — `the-drop` (the sky-well)

**WHAT IT IS.** Not an object but an opening: a raised dressed-stone well-head
with an iron wear-ring, its hinged timber leaf standing open behind it, cyan
light and vapour pouring up out of the shaft, START struck in gold across the
coping's front face — control and sign are the same thing because the button
doesn't *say* "start", it IS the way in, and in a flyer the way in is falling.

**STRUCTURAL TIE TO THE CHAIN.** The chain's last rope **belays to a ring on
the raised leaf and takes its weight** — the sign chain is what is holding the
door open. It is the only rope on screen pulling *upward* under load. The open
leaf is a timber plate cut with the **identical chamfer + V-notch profile as
the three planks**, so the one plank-shaped element in the composition is the
one that has been *lifted out of the way*. The eight iron **dogs** round the
rim are the plank nails scaled up and given a job.

### Fixed base facts
Base `tools/menu-design/harbour_post_holistic.py` `VARIANT=B`, 360x640.
The three planks (STORE cx102/cy386/-3.0, TOP 10 cx108/cy446/+2.4, SETTINGS
cx100/cy506/-1.6, all 172x44) are **frozen**. SETTINGS' rotated bbox is
x13.4-186.6, y481.6-530.4. The chain's right tail is at **(158.5, 526.1)**.
Pip is x59-122, y243-292. Corridor: x>=191 above y530, full width below y530,
floor y624. Backdrop: **L36 day / L21 night** at both poles.

### DIRECTIVE 11 — THE CLOUD-BANK FLOOR IS **CUT**
It was a second design, not "elsewhere": it fought `_draw_mountain_silhouette`
(alpha 180), risked reading as the scrolling near-lane ("the game already
started"), and a high-luma cloud mass *below* the dark mountain band inverts
the screen's value structure at the bottom edge.

**Replacement:** the aperture becomes a **raised stone coping** — a well-head
kerb standing proud, which is self-supporting and needs no floor plane at all.
The composition's floor stays the existing ground band. Stone is a single new
material, introduced once, and it passes the gate on **both** arms.

### Construction (geometry, all screen coords)
An ellipse, never a rectangle. A shallow view angle so the coping's front face
is a real type surface.

- **Coping top surface:** outer ellipse **152x44 centred (272,560)** ->
  **x196-348, y538-582**. Dressed stone, lit top-left, dark bottom-right.
- **Void mouth:** inner ellipse **108x30 centred (272,562)** ->
  **x218-326, y547-577**.
- **Iron wear-ring:** a 4px band inset on the coping's inner edge, plus
  **eight dogs** (wing-bolts) at 45deg intervals around the outer top.
- **Front wall (the type field):** the outer ellipse's lower arc extruded down
  **26px**; bottom-most point (272, 608). Widest and tallest at the centre —
  152 across, 26 deep — falling away to nothing at the extreme flanks. This is
  the largest unbroken type surface in the whole set.
- **The void.** A vertical ramp: **near-black at the near (lower) edge ->
  mid-teal -> arc cyan at the far (upper) lip.** This polarity is correct
  perspective (looking into a shaft at a shallow angle you see the lit FAR
  inner wall) and it keeps the near lip dark, so the gold type below it sits
  on clean stone instead of being washed out.
  - Three **vapour arcs** curling over the front edge on sine paths + a few
    drifting motes, drawn as three cached puffs.
- **The leaf** (directive 12 — plank profile, NOT an ellipse-plate):
  `_board_points(132, 48, chamfer=6, notch=7)` — the planks' own silhouette —
  scaled to **y*0.70** for foreshortening (apparent 132x34), rotated -10deg,
  standing back from a hinge along the well's far lip. Footprint
  **x206-338, y504-542**.
  - We see its **underside**, in shade (`timber_board(exposure=62)`), with the
    top arris catching a 2px cyan rim-light `(150,226,232)` off the well.
  - **It carries no type and sits at an angle, so it reads as a lid, not a
    fourth sign.**
  - Two iron strap hinges across the far lip at (240,540) and (304,540).
- **Chain belay.** `rope(surf, (158.5,526.1), (214,514), sag=2, width=3)` to an
  `_iron_ring` on the leaf's upper-left corner. Nearly straight and rising —
  the only line on screen under upward load.
- **Ground:** a soft elliptical cyan wash on the ground band, centred
  (272,614), 170x20, on a scratch SRCALPHA layer.
- **Idle:** vapour curls upward continuously. **Tap:** the leaf slams shut
  behind you as the scene cuts.

### Published tap rect
**`pygame.Rect(196, 504, 152, 106)`** = x196-348, y504-610 — the **union of
coping + raised leaf** (directive: an ellipse's own rect is only ~78% live).
- x196 > SETTINGS' right edge 186.6 -> **disjoint** by 9px.
- Bottom 610 < 624. 152x106 clears 48dp. Live fill ~71%.
- Visual target sub-rect (for centring FX and the focus ring):
  `pygame.Rect(196, 538, 152, 70)` — the coping alone, 78% live.
- START is lowest: the coping runs y538-608, entirely below SETTINGS' bottom
  edge (y530); the leaf above it is a lid, not the control's face.

### Colour table
| role | RGB | H | C | luma | vs L36 day | vs L21 night | dH gold/rust | ratio gold/rust |
|---|---|---|---|---|---|---|---|---|
| stone body (coping + wall) | (138,148,160) | 212.7 | 0.086 | **146.4** | +110.4 | +125.4 | 169.1 / 147.3 | 8.00x / 8.41x |
| stone lit (top-left) | (186,194,204) | 213.3 | 0.071 | **192.7** | +156.7 | +171.7 | 169.7 / 146.7 | 9.78x / 10.28x |
| stone shade (bottom-right) | (96,106,120) | 215.0 | 0.094 | **104.6** | +68.6 | +83.6 | 171.4 / 145.0 | 7.33x / 7.71x |
| iron wear-ring + dogs | (98,104,116) | 220.0 | 0.071 | **103.6** | +67.6 | +82.6 | 176.4 / 140.0 | 9.78x / 10.28x |
| void, far lip | (120,236,238) | 181.0 | 0.463 | 201.5 | +165.5 | +180.5 | 137.4 / 179.0 | 1.49x / 1.57x |
| void, mid | (26,110,126) | 189.6 | 0.392 | 86.7 | +50.7 | +65.7 | 146.0 / 170.4 | 1.76x / 1.85x |
| void, shaft (see note) | (12,16,22) | 216.0 | 0.039 | 15.5 | -20.5 | -5.5 | 172.4 / 144.0 | 17.60x / 18.50x |

Stone passes on **both** gate arms (dH 169/147 AND ratio 8.0x with dLuma 45.4
vs gold, 36.1 vs rust). Every solid mass is >=L103.6 — the original
`collar iron (66,70,80)` measures **L69.9**, on the reject line, and is
replaced.

**The shaft is the one sanctioned dark value in the set.** A hole must be dark
or it is not a hole. It is fully enclosed by the L146 coping on every side, so
it never has to carry a silhouette against the L36/L21 backdrop, and the
darkest third is ~850px of a 2545px ellipse. State this explicitly in the
render notes.

### Type
**22px, `track=2`, measured tracked run = 83px, ink 15px tall.**
- **FLAT and horizontal, struck on the coping's front face** (directive 8 —
  the arc is killed). Centred **(272, 594)** -> ink **x230-314, y587-602**.
- Front-wall coverage, checked at both ends of the word:
  - at the word's ends (d=42 from centre) the wall spans **y578.3-604.3** ->
    8.7px clear above the ink, 2.3px below.
  - at the centre (d=0) the wall spans **y582-608** -> 5px above, 6px below.
- Gold-pale `(255,232,168)` over a `KEYLINE (22,14,10)` cast twin at alpha 150,
  offset +1px down — the shipped plank pattern, so it reads as struck into
  stone.
- **Why the view angle is shallow (152x44, not 136x54):** at a 54-deep ellipse
  the lower arc sags 4.6px across the word and a 22px word will not clear the
  wall at both ends. At 44 deep it sags **3.3px** and clears everywhere. The
  aperture still reads unambiguously as a hole.
- 22px is **28% larger** than the 17px utility labels (83 vs 65 tracked). It is
  the smallest CTA in the set — this is the price of the aperture concept, and
  it is paid on the largest unbroken type field in the set (152px available for
  an 83px run).

### What changes elsewhere
- **The timber post, the diagonal brace and the mooring ring all go.**
- **The cloud bank is CUT** (see above) — replaced by the self-supporting
  raised coping.
- The chain's right tail belays to the leaf's ring instead of a post head.
- **Ground:** untouched apart from the soft cyan wash under the well.
- **`_best_tag` moves** from (276,610) — now inside the well's front wall — to
  **(100, 566)** (x48-152, y554-578).

### Shipped helpers to reuse
`_board_points` (the leaf IS this profile), `timber_board(exposure=62)` for
the leaf's shaded underside, `soft_shadow` with the coping's elliptical mask,
`under_shade`, `_grad_fill` (the void ramp), `_mix`, `nail` / `_iron_ring`
(dogs, strap hinges, belay ring), `rope`, `hud._tracked_label` (:1189) — flat,
no rotozoom wrapper needed, `store_cards.gloss_sweep` (:618) for the stone's
lit top-left. Ellipse arcs + polygons only; vapour is three cached puffs on
sine paths; the ground wash goes on a scratch SRCALPHA layer.

### Directive 13 (binding on this render)
Publish a 1x thumbnail strip at PHASE 0.0 / 0.20 / 0.45 / 0.65, a greyscale
pass, and a 1x crop of the START quadrant alone. **The greyscale pass is the
real test here: the whole concept depends on a bright ring reading against a
dark hole, which is a pure value proposition.**

---
---

## APPENDIX — MEASURED PUSH-BACKS (with numbers, as required)

1. **Type budget is 2-3px wider than the critique's table.** The critique
   computed `f.size("START") + track*4`; `hud._tracked_label` sums the
   per-glyph render widths, which is wider. Real values: 17px=65, 22px=83,
   24px=**88**, 26px=**95**, 30px=108. All five briefs are sized against these.
2. **`clear-arm` blade is 138 long, not ~124.** 16 (pivot boss) + 88 (type) +
   6 (gap) + 28 (bone tip band) = 138. At 124 there is zero slack. The 138
   footprint still clears the x>=191 corridor by 16px and the y624 floor by
   16px.
3. **`colours-up` flag is 140 long, not 112.** The critique's "24px fits into
   a 112 hoist with 13px margins" did not subtract the mandated swallowtail:
   112 - 14 (hoist band) - 26 (bite) = 72px usable, against 88px of type.
   140 = 14 + 100 + 26.
4. **`the-drop`'s ellipse is 152x44, not 136x54.** At 54 deep the front wall's
   top edge sags 4.6px across the word and 22px type does not clear it at both
   ends; at 44 deep it sags 3.3px and clears everywhere.
5. **`ring-out` is centred x258, not x250.** At x250 the bell's tap rect would
   start at x184 and overlap SETTINGS' bbox by 3x4px at the top-left corner.
6. **Two colours from the concept doc are rejected under the L70 floor and
   replaced:** `collar iron (66,70,80)` measures L69.9 (used by `beacon` and
   `the-drop`); `colours-up`'s trough `(12,86,98)` L65.3 and hoist band
   `(14,74,84)` L57.2. Replacements are in each colour table.
