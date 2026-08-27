# START v2 — art-director critique + locked directives

VERDICT: REWORK [signal-pylon, marquee-hoarding]. Three proceed with mandatory
corrections (sunburst-medallion, go-lozenge, boarding-pass).

## THE HIGHEST-LEVERAGE NOTE — orchestrator-verified

**Every stack is authored in `m()` units, and `m()` is 2x.** `store_cards.py:39`
sets `SS = 2`; `m(v) = int(round(v*SS))`. `store_cards.py:1150` states the
mechanism in the project's own words:

> "Author oversized, then ONE smoothscale down turns the geometry crisp."

**None of the five concepts said they would do this.** Drawn straight onto the
360x640 menu surface, every stroke, inset, sheen height and shadow blur ships at
exactly **double** its intended weight: `drop_shadow(blur=m(6), dy=m(3))` becomes
a 12px-blur/6px-offset smudge; `top_sheen(h=m(16))` covers 32px of an 80px plate;
`facet_gem(r=7)`'s seat well becomes a 15px black disc around a 7px stone.

> **MANDATORY, ALL FIVE: build the button body on a 2x scratch SRCALPHA surface,
> then ONE `smoothscale` to final size, cached.** This is exactly what makes the
> store cards look premium and `_pill_btn` - drawn entirely at 1x, no supersample
> - look cheap.

- Corollary: `_draw_rim`'s 48 arcs and its `R//36` edge stroke are authored for
  the `_SS = 6` icon pipeline (`achievement_icons.py:105`). At 1x, R=74 they band.
- Corollary 2: `drop_shadow` and `smooth_aura` bleed OUTSIDE the rect. Draw those
  at 1x onto the menu surface with literal integers **after** the downscale, or
  pad the scratch by the full bleed - otherwise the downscale clips them hard.

## SECOND CRITICAL BUG — orchestrator-verified

**`_gloss_corrected(peak=110)` destroys `go-lozenge`.** It blits `BLEND_ADD`, so
it adds `a` to every channel. Lime top `(176,236,104)` + 110 = `(255,255,214)`.
Green stays clipped until `a < 19`, i.e. **`y/h > 0.52` - the entire top half
blows to flat desaturated yellow-white** and the candy-lime thesis dies on
arrival. Measured:

| y/h | alpha | result | |
|---|---|---|---|
| 0.00 | 110 | (255,255,214) | CLIPPED |
| 0.20 | 64 | (240,255,168) | CLIPPED |
| 0.40 | 32 | (208,255,136) | CLIPPED |
| 0.51 | 19 | (195,255,123) | CLIPPED |
| 0.60 | 12 | (188,248,116) | ok |

> **Rule, whole set: on any body above ~L120 use `top_sheen`(:499), which
> alpha-composites and cannot clip.** `_gloss_corrected` is for *near-black*
> enamel - that is why `_dark_chip_body`(:683) defaults it to `gloss=14`. If you
> insist on additive on the lime, `peak <= 18`.

## STUNNING, OR MERELY CORRECT?

All five pass the arithmetic. Only two would make a player stop.

| slug | verdict |
|---|---|
| `sunburst-medallion` | **Stunning.** The only one that changes the screen's *silhouette class* - five horizontal boards, then a struck circle. `_draw_rim` is the best metal in the codebase and has never touched the menu. Carries reward semantics: a minted token is a thing you want to pick up. **#1.** |
| `marquee-hoarding` (reworked) | **Stunning, conditionally.** A lit marquee is the highest-conversion CTA archetype in the genre. As written it is a stall sign. Re-materialled it is the strongest in the set. |
| `boarding-pass` | **Charming, the most original idea here** - and the most fragile. Three fixable defects each individually send it back to scenery. Worth the slot; the only one with wit. |
| `go-lozenge` | **Competent and forgettable.** That is precisely its job. It is the Royal Match / Candy Crush default and it will work. It is the floor, not the hero - **tell the user that in the showcase caption.** |
| `signal-pylon` | **Neither.** Scenery, and illegible type. |

## CONTROL vs SCENERY - ruled

**`marquee-hoarding`'s cartouche: RULES AGAINST.** `_cartouche_points`(:537) is
the game's own stepped stall silhouette, filled with the game's own
`GOLD_A_STOPS`, framed in gilt, studded with bulbs "built like `draw_sign`'s
six". That is not complementing environment art, it is a recolour of it. Ivory vs
lacquer is not enough - a player reads silhouette + bulb rhythm before plate
colour.

**`signal-pylon`: RULES AGAINST, decisively. CUT IT.** Casing + three stepped
collars + four rivets + a `cabochon_glass` lantern head + a foot plate that
"visibly *stands*" - every one is a construction note for a **prop**. Its own
defence ("head starts y350 so it never reads as propping up Pip's cloud") is an
admission: you only need that argument for scenery. It is also the *tallest*
object and the first read, inverting the START-lowest hierarchy, and its 100x270
tap rect means a tap at y=360, up near the title band, fires the game. Its
cream-on-amethyst type measures **1.81:1 at the core's top stop** (3.00:1 at mid
- zero margin on AA-large).

## LAYOUT - ruled. Three of five overlap SETTINGS with glow.

SETTINGS' rotated bbox is **x13.4-186.6, y481.6-530.4**.

- **`sunburst-medallion` FAILS as specified.** Not the 3px it flagged: the plate
  clears by ~5.6px. **The collision is `smooth_aura` R+16 = radius 92, reaching
  x=174 - ~12px into the SETTINGS plank with a gold wash.** Also bottom =
  548+76 = **624 exactly**, with `drop_shadow(dy)` and a contact circle below
  that - phone gesture-bar territory.
  **Fix: cy 548->538, R 76->74** (bbox x192-340, y464-612); **aura R+10 peak 32**.
  Bright mass at R74 ~15,900, still 1.29x title.
- **`go-lozenge` same defect.** `smooth_aura` r30 on a block whose left edge is
  x192 reaches **x~162, 25px into the SETTINGS plank, in lime.** Cut to r18 or
  bias the centre right.
- **`boarding-pass`: the rotation claim is FALSE.** "The only non-orthogonal mass
  on screen" is wrong - the three frozen planks are rotated **-3.0 / 2.4 / -1.6**.
  A ticket at **-3 deg is the STORE plank's exact rotation** and will read as a
  fourth rung. Go to **-8** (clearly a different gesture) or **0**. Its top edge
  at y536 also leaves only ~6px to SETTINGS' bbox bottom, before `drop_shadow`.
- **`marquee-hoarding`: bulb halos collide.** `smooth_aura` r11 seated on the
  plate's top edge y538 reaches **y527, inside SETTINGS' bbox**. And 328/360 =
  91% width reads as a **footer nav bar**, not a hero CTA - the drop shadow has
  nowhere to fall. **Inset to x28-332, top y546.**

**Cap `smooth_aura` peak at 32 set-wide.** Shipping code defaults to 27; sunburst
asked 40, pylon 38. Above 32 the disc stops reading as struck metal and starts
reading as bloom.

## DISTINCTNESS - one collapse, one near-collapse

Silhouettes and dominance strategies genuinely differ. **Palette does not.**

- **`sunburst-medallion` x `marquee-hoarding` - COLLAPSE.** Both are *gold ornate
  frame around a bright warm plate*. **Resolution: sunburst owns gold. Marquee
  goes ivory + INK** - frame `(22,46,58)->(14,30,40)` deep teal-ink via
  `frame_double_bevel`, warm bulbs the only gold. This cures the collapse, the
  stall resemblance, and pairs correctly with the cobalt ink type, in one move.
- **`sunburst-medallion` x `boarding-pass` - NEAR-collapse.** H44 vs H34 is 10
  apart, both warm orange-gold. Survivable only because boarding-pass carries a
  magenta stub, a cream field and a die-cut silhouette. **Push tangerine top to
  `(255,178,92)` (H30)** and let the magenta stub run larger.
- With pylon cut the set loses its only cool option, leaving 3 warm + 1 lime.
  **`keycap-launch` MUST be cool. Hard requirement, not a preference.**

## IS `go-lozenge` WORTH A SLOT? Yes - but it isn't currently a control.

Keep it. The user said "disaster"; one bulletproof-conventional option gives them
a floor, and the ornament-vs-mass question is genuinely unanswered.

**But the spec breaks its own thesis:** it ends with a `bevel_rim` chrome collar
*and* a big `facet_gem` r13. That is ornament. **If the control carries ornament
it tests nothing**, and the chrome collar - "one cool ring in a warm screen" - is
the single cheapest-looking element in the brainstorm: a bright cool ring around a
lime slab reads as bootleg-toy plastic. **Strip both.** Body + gloss + double rim
+ two-line type. Nothing else.

**On H94 vs the ground's H120 - the designer is over-worried.** Hue separation is
the wrong metric when one field is **S0.12**; a near-neutral dark green-teal has
effectively no hue to separate from. S0.68 at L214 against S0.12 at L38.6 is a
4.6x luma ratio and a 5.7x chroma ratio. **The lime is fine.** The real reason it
won't be the pick is that it is forgettable, not that it is camouflaged.

**Shape:** 156x122 is aspect 1.28:1 - that is a *tile*, and this game already has
tiles (store cards). **Re-proportion to 176x96** (1.83:1). Bright mass ~14,400 =
1.17x title; still clears both bars and reads as a control.

## PER-CONCEPT CORRECTIONS

### 1 `sunburst-medallion` - PROCEED (top pick)
KEEP: the circle; `_draw_rim` + `_draw_step` + `_draw_face`; **the inversion
(bright plate, dark type) - the correct read of a dark corner and the single best
decision in the brainstorm**; `facet_gem` quoting Pip's scarlet as a jewel.
FIX:
1. Build at 2x, one smoothscale. Non-negotiable.
2. cy 548->**538**, R 76->**74**; aura **R+10, peak 32**.
3. **Five ornaments on a 152px disc is four too many.** Wedges + chevron + gem +
   laurel + sparkle ring will be grey mush at 1x on a phone. **Keep the 16
   sunburst wedges (they carry the struck read) and the gem. CUT the laurel, the
   sparkle ring and the chevron.** Re-test at 1x before adding anything back.
4. Top face stop `(255,222,132)` has zero red headroom - any highlight clips
   instantly. Pull to **`(250,216,128)`**.
5. START 34px (123) in a 152 face is a 12px margin. **Drop to 30px (108)** for a
   22px optical margin; the disc's mass carries the emphasis, not the type size.
6. Type `(96,40,10)` on the plate measures **7.62:1** - excellent, keep exactly.

### 2 `marquee-hoarding` - REWORK
KEEP: the thesis; the ivory plate; **cobalt `(30,64,120)` ink, which measures
8.29:1 - the best type contrast in the set**; giving the chain a floor.
FIX (this is the re-spec):
1. **Delete `_cartouche_points`.** Plain rounded-rect with a shallow 2-step crown
   you author yourself - a stepped *crown*, not the stall silhouette.
2. **Delete the gilt.** Frame becomes deep ink-teal `(22,46,58)->(14,30,40)` via
   `frame_double_bevel`(:59) with one warm `(232,196,108)` hairline.
3. **10 bulbs -> 6**, r4 seat / r3 glass. Ten glowing dots across 328px on a
   360px phone is a dotted noise band competing with the word. Six reads as rhythm.
4. Inset **x28-332** (304 wide), top **y546** so bulb halos clear SETTINGS.
5. 42px START (148) in a 304 plate is right - keep. Keep `_swash_underline`; drop
   the `_micro_gem` (third small bright thing after bulbs and underline).
6. Recount: ~304x72 at ~88% = **~19,300**, still the largest. Doesn't need the width.

### 3 `go-lozenge` - PROCEED as the control, but make it actually a control
KEEP: the thesis; the three lime stops (L214/179/138); `_dark_chip_body`'s
structure; **the 3px press-down - tactility IS the idea, so it must ship**.
FIX:
1. `_gloss_corrected` peak 110 -> **`top_sheen` peak 46**. This one change decides
   whether the concept exists.
2. **Delete the chrome collar and the `facet_gem`.**
3. Re-proportion 156x122 -> **176x96**, at **x168-344, y520-616** - clear of
   SETTINGS and off the y624 floor.
4. Aura r30 -> **r18** or bias right.
5. Keep the two-line lockup - "TAP TO FLY" 13px under START 38px is genuinely
   good and it is **the only concept that tells a first-time player what the
   button does**. Type `(14,48,14)` on lime measures **7.46:1**.
6. **Caption it plainly in the showcase: this is the safe floor.**

### 4 `boarding-pass` - PROCEED with three mandatory fixes
KEEP: the die-cut silhouette - the most distinctive shape in the set; the cream
print panel carrying the mass; scarlet surviving as *print* not plate; the
`_engraved` rule + "ADMIT ONE - SKY LINE".
FIX:
1. **-3 -> -8 deg.** At -3 it matches the STORE plank exactly.
2. **Cut the chain tie.** `_tails` terminating in `_iron_ring` on the ticket
   re-attaches START to the chain - the accepted VARIANT=B logic is that START
   *leaves* the chain and is planted. Re-hooking it is the scenery move, and it
   drags `_iron_ring`'s alpha-punch bug along.
3. **The bright-mass claim is optimistic.** 15,700 from a 19,000 box implies ~83%
   conversion, but the 46x76 magenta stub is L118->**77**, 7 luma above the floor,
   so ~2,000-3,000px won't count. Realistic: **13,000-14,000 = ~1.10x title** -
   the thinnest margin in the set. Either lift the stub to
   `(244,104,168)->(206,64,128)` or grow the body to **264x80**.
4. Tangerine top -> **`(255,178,92)`** (H30) to open separation from sunburst.
5. **Accept the axis-aligned bbox** for hit-test; don't build an inverse rotation.
6. Type `(150,26,70)` on cream measures **7.07:1**. Fine.

### 5 `keycap-launch` - NEW, replaces `signal-pylon`
**Thesis.** The one control on screen with real thickness. Everything in this menu
is a flat plate hung on a rope; this is an **extruded key-cap with a visible side
wall**, sitting nearest to camera. Dominance is **Z-depth** - a strategy the set
doesn't have, and a construction the world cannot borrow. **It clears the scenery
trap structurally: there is no such object in the Skybit world.**
Spec:
- Face `Rect(96, 534, 248, 76)`, radius 20. **Side wall = the same rounded-rect
  offset +11px down, drawn first.** Wall bottom y621 - 3px clear of the floor.
- Face `vgrad_stops` **[(0,(96,166,244)),(0.5,(48,116,214)),(1,(26,84,178))]** ->
  L**156.7 / 108.7 / 78.4**, every stop above the floor.
- Wall `(24,66,142)` L62.6 - deliberately below the floor; it is the shadow face,
  not mass.
- `top_sheen(h=18, peak=44)`. **No additive gloss.**
- `bevel_rim` deep `(14,44,104)` / bright `(210,232,255,235)`, plus a 1px
  `(160,206,255)` inner glint on the top edge only.
- `drop_shadow(blur=8, alpha=120, dy=5)` at 1x under the **wall**, not the face.
- START **38px (133)** in cream `(255,248,232)` - **4.32:1** against the face mid,
  the only cool-plate/light-type pairing in the set that passes AA at normal size
  (pylon's failed at 1.81:1).
- One warm accent only: a 2px `(246,206,110)` baseline rule under the word.
- **Press state: face translates +8px down, wall compresses to 3px.** That is the
  entire animation and it is the point.
- Bright mass ~248x76 x 0.92 = **17,300 = 1.40x title, 4.2x plank.** Tap 248x87.
- **Alternate if blue is rejected:** same key-cap construction in cool graphite
  `(96,104,120)->(52,58,72)` with a hot gold face plate.

## OTHER LAWS
- `pygame.draw` **writes** alpha. boarding-pass correctly flagged `_iron_ring`'s
  `(0,0,0,0)` punch - the die-cuts have the same issue, as does the
  `store_design` frame stack composited onto anything but a fresh SRCALPHA layer.
  Every subtractive op goes through a scratch layer + `BLEND_RGBA_MIN`.
- **numpy: you're clear.** `smooth_aura` has a pure-Python 1D fallback
  (`store_design.py:200-228`). Also marquee's ten bulb halos are ten blits of
  **one** cache entry, so the "heaviest build" risk note was wrong.
- `Rect.inflate()` takes the TOTAL delta. `bevel_rim` already accounts for it;
  hand-rolled insets must use `-2*k`.
- No gfxdraw, no blur/bloom - all five clean.

## PUNCH LIST, PRIORITISED
1. **Build every concept on a 2x scratch + one smoothscale.** Nothing else in
   this list matters if the strokes ship at double weight.
2. Cut `signal-pylon`; build `keycap-launch` in its slot (**must be cool**).
3. Re-spec `marquee-hoarding`: no `_cartouche_points`, no gilt (ink-teal frame),
   6 bulbs, inset x28-332, top y546.
4. `go-lozenge`: kill `_gloss_corrected(110)` -> `top_sheen(46)`; delete the
   chrome collar and gem; re-proportion 176x96 at x168-344 / y520-616.
5. `sunburst-medallion`: cy->538, R->74, aura R+10 peak 32; cut laurel + sparkle
   ring + chevron; START 34->30px; top stop -> `(250,216,128)`.
6. `boarding-pass`: rotate -8, cut the chain tie, lift the magenta stub above L77
   or grow to 264x80, tangerine top -> `(255,178,92)`.
7. Cap `smooth_aura` peak at 32 set-wide; check every aura's outer radius against
   SETTINGS' bbox x13.4-186.6 / y481.6-530.4 - three of five currently overlap.
8. Draw all outer effects (`drop_shadow`, `smooth_aura`) at 1x with literal
   integers, after the downscale.
9. Render every candidate at **1x against both biome poles** (day ground L38.6 /
   night L21.7) and squint-test before adding a single ornament back.
