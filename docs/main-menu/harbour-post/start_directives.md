# START-as-one-object — art-director critique + locked directives

VERDICT: REWORK [clear-arm].  Four proceed; `clear-arm` is re-specified.
**Do NOT bench-swap `the-windlass` in** — a horizontal timber cylinder carrying
gold type in a horizontal band, under three horizontal timber planks carrying
gold type in horizontal bands, is the rejected plate re-inflated. Bench it.

## THREE FINDINGS THAT REFRAME THE SET

### 1. The START quadrant is dark at BOTH poles (orchestrator-verified)
Measured on the approved base at PHASE 0.20 / 0.65:

| band | day | night |
|---|---|---|
| y468-500 | **L47.3** | **L26.1** |
| y600-636 (ground) | **L35.7** | **L20.0** |
| left flank x190-208, y494-594 | **L38.1** | **L23.8** |
| (STORE rung, open sky, for contrast) | L104.7 | ~L20 |

Round 7's "polarity inverts twice per cycle, every contour needs a two-step" is
true for the STORE rung at L105. **It is NOT true down here.** The mountain
silhouette and ground band hold this corner at L36 day / L21 night. It never
goes bright.

Consequences, binding on every concept:
- START must be a **light-value figure at both poles**. A single bright keyline
  separates here — no two-step contour needed. Real simplification.
- **Reject any body colour below ~L70 for large masses.** Bronze L103, signal
  teal L109, collar iron L70, arc cyan L201 all clear by d34-d180. **Lacquer
  ink L28 is d8 from the day backdrop and d4-7 from night** — invisible.
- The colour gate tested hue separation from gold/rust and said nothing about
  local value. It passed a colour that fails the screen.

### 2. Type budget (orchestrator-verified against the vendored font)
`_hud._font(size,True).size("START")`:

| size | width | tracked +2 |
|---|---|---|
| 17 (utility labels) | 54 | 62 |
| 22 | 72 | 80 |
| 24 | 78 | **86** |
| 26 | 85 | **93** |
| 30 | 97 | 105 |

The primary CTA must out-type a 17px utility label by a clear margin: **24px
minimum = 86px tracked run plus outline margin. Any unbroken type field
narrower than ~96px is not a primary control.**

### 3. Style-law rulings
- **`beacon`'s bloom pass is REFUSED.** No blur, no bloom. Use the sanctioned
  numpy-free path that already ships: `store_design._build_aura` (~line 200)
  falls back to 1px-stepped concentric rings precisely because numpy is absent
  on pygbag. Build the halo as 3-4 dilations of the text mask at falling alpha
  on a scratch SRCALPHA layer, hard-stepped. Better at this scale anyway -
  stepped falloff keeps the glyph edge crisp.
- **`beacon` must not repaint ONE pixel of the three planks.** The doc proposes
  casting light "up onto the SETTINGS plank's underside". The user said the
  planks stay exactly as they look. Light the bracket, hardware and ground
  only. This costs beacon its best diegetic argument - say so honestly rather
  than sneaking it in at low alpha.
- **`clear-arm`'s 1px bone keyline** (L236) around an ink body is a near-white
  outline, not hue-matched. A bright keyline is legal in this quadrant, but
  tint it toward the object's own hue or it reads as an ink-outline inversion
  of the "bolted-on" look `T_EDGE` exists to prevent.
- Otherwise clean: no gfxdraw, no numpy, all five use scratch SRCALPHA +
  BLEND_RGBA_MIN / MULT, the pattern `timber_board` and `soft_shadow` use.

## THE CENTRAL TEST — is it one object, or a decorated rectangle?

| | verdict |
|---|---|
| `ring-out` | **Passes hardest.** One closed polygon; the flared skirt IS the type field. No face-on-carcass anywhere. |
| `beacon` | **Passes.** The word is reserved out of the glass - it has no substrate at all. Purest reading of the brief. |
| `the-drop` | **Passes.** Not an object; there is nothing for a plate to sit on. |
| `colours-up` | **Passes on execution, not geometry.** Strip the ripple and it is a quadrilateral carrying a gold word in a horizontal band - the plank's construction in soft material. The execution must actually land. |
| `clear-arm` | **Passes on mechanism, FAILS on face.** "Ink field, bone band across the outer third, 1px keyline, two rivet rows, gold type" is a plate with a border and a highlight strip - `_enamel()` redrawn with a fishtail. **This is the concept that quietly reinvented the two-layer construction.** |

## CHAIN RELATIONSHIP — structural in all five, but one conflict
`ring-out` rope-as-hanger; `beacon` belay-to-hook (termination into structure,
usefully distinct from ring-out's suspension); `clear-arm` operating wire — the
strongest claim in the set and it is true; `colours-up` halyard through a
masthead block with a real termination; `the-drop` the chain holds the door
open. **None is "a shared colour." This is the document's strongest work.**

**Conflict:** `ring-out` hangs the bell from the rope AND plants a bell-cot
under it. A bell cannot hang from a cross-head and from a rope arriving from a
cloud 200px away. **Delete the bell-cot.**

## RULING — `beacon` vs the rejected `lantern-street`: CLEARED, BUILD IT
Round 6's recorded reason was *"close enough to the shipped menu that they
didn't earn the change"* — about **compositional novelty, not lanterns**.
`lantern-street` failed because it reassembled `pillar_pagodas` +
`mountains_v14` + the promenade into what the player sees every run. `beacon` is
a single glazed vessel as the primary control inside the approved `harbour-post`
composition: it shares a *motif*, not a *composition*, and the motif was never
the defect. `pillar_variants.draw_paper_lantern` already ships, so a lantern is
established vocabulary — provided beacon's is hard-edged iron-and-glass with a
timber cap, a different object class from the soft paper lantern. Do not let
them converge.

## RULING — `clear-arm`: three independent failures
- **Fourth-plank risk is real and the mitigations do not work.** 96x28 is 3.4:1;
  planks are 3.9:1. Same orientation, same pitch, same gold-tracked type, 25px
  below SETTINGS. Post, spectacle, counterweight, lattice are all sub-8px and
  dissolve at 1x. Shortening to 88 makes it worse — sameness of *kind* is the
  problem, not length.
- **The blade cannot hold the word.** Blade 96, bone band takes the outer third
  (32), leaving **64px of ink field. START at 22px tracked is 80px. It does not
  fit.** Dropping to 18px (66px) makes the primary CTA *smaller than the 17px
  SETTINGS label plus tracking*. Letting the word run onto the bone band puts
  GOLD_PALE L232 on bone L236 — **d4, the last two letters vanish.**
- **The ink body is invisible** (finding 1): d8 day, d7 night. The fishtail —
  the entire structural-inheritance argument — is a silhouette nobody can see.
  And the bone band at L236 becomes the brightest object in the quadrant while
  carrying no information, inverting the focal hierarchy.

The fixes pull against each other: more type needs a longer blade, which worsens
the plank read; fixing the plank read needs a shorter blade, which worsens type.

**REPLACEMENT DIRECTION.** Keep the signal thesis and the operating-wire chain
tie verbatim, but kill the horizontal blade: rest the arm permanently at
**-45 deg "clear" as its IDLE state** (a diagonal is instantly not-a-plank, it
points the way the bird flies, and the tap becomes a snap-and-overshoot along
the same axis rather than a state change); **lengthen to ~124 along the
diagonal** so 24px type fits with margin; **invert the values** to a
limewashed/bone body with an ink band and ink type (`bleached-board` from round
7 is the shipped precedent for figure/ground inversion in this exact quadrant);
and move the bone band **off the type run to the fishtail tip only**, where it
becomes a marker instead of a competitor.

## TYPE RULINGS, PER CONCEPT
- **`ring-out` — 26px tracked +2 (93px), NOT 30px.** Lip is 120 wide; minus
  reeding and the thickened sound-bow leaves ~104 usable, and 30px tracked is
  105 — it overflows, worsening upward as the skirt narrows. Seat 26px low
  against the sound-bow where the trapezoid is widest, 5px clear each side.
  Still 53% larger than the utility labels. The 6 deg arc is nearly flat and
  costs almost nothing — **this is the only concept that should keep arced type.**
- **`beacon` — three visible facets, not five.** Five facets across 124px with
  iron corner posts puts the centre facet at ~52px; START would be chopped by
  two posts or set at ~14px. **One unbroken 96-104px centre glass flanked by two
  narrow rakes** still reads round without a circle, and 24px (86) then fits.
  **Also test both knockout polarities at 1x before committing:** thin bright
  strokes on dark glass optically clog — the T-stem is 15px at 24px but the A
  and R counters become 2-3px islands and will fill in. A *dark* word in relief
  against a fully-lit panel is the more robust build.
- **`colours-up` — healthiest carrier, but the warp must not touch the type.**
  24px = 78 flat (86 tracked) into a 112 hoist: fits with 13px margins.
  Gold-pale on signal teal is d123 luma and complementary — the strongest
  pairing available. **Refuse the per-column sampled warp on the word:** a 1px
  granularity y-offset stair-steps the horizontal strokes of S, T, A, R, and a
  3px stroke broken by 1px steps reads as a *broken* stroke on a phone. Warp the
  cloth, not the letters — render the word flat, apply the local warp as a
  single whole-word integer y-offset plus <=2 deg rotation.
- **`the-drop` — unshippable as drawn; take the doc's own second option.** Five
  glyphs at 18-20px each rotozoomed to a tangent around a 136x54 ellipse at 24
  deg: the near rim is a ~136x14 crescent, so glyphs need vertical squash *as
  well as* rotation — two destructive transforms on a 12px-tall letterform.
  Flattening to +-8 deg doesn't rescue it. **Move the word to a struck flat
  chord on the collar's front face: horizontal, 22px tracked = 80px across a 136
  collar, gold-pale over the dark cast twin.** The aperture concept is intact.

## LAYOUT
SETTINGS (`cx=100, cy=506, 172x44, -1.6 deg`) publishes a rotated bbox of
**x13-187, y482-530**. Free corridor for START: **x>=191 above y530, full width
below y530**, floor y624. Pip verified at x59-122, y243-292 — no concept goes near.

| | footprint | ruling |
|---|---|---|
| `ring-out` | lip x200-320, body y500-580, knot <=y600 | OK, 13px clear. **Tap target = the bell body 120x80, NOT the monkey's fist** (a 3-loop knot is under 48dp and players aim at the big shape). |
| `beacon` | x210-334, y480-584 | OK (x210 > 187) but the roof sits level with SETTINGS' band — **drop it ~8px**. Tap 124x104 OK. |
| `colours-up` | **UNRESOLVED** | The doc never states the flag's y. A flag hoisted up a raked mast with a masthead block above it would put the cloth at the SETTINGS band or higher — **which breaks "START is lowest."** Resolve explicitly: **masthead <=y532, flag rect ~y536-608.** That means a genuinely short mast — accept it (it's a jack-staff, not a topmast) or fly at half-hoist. **Publish the rect.** |
| `the-drop` | collar x204-340, y529-583; leaf back to ~y500 | OK. **Publish the union of collar + raised leaf, ~136x62** — an ellipse's rect is only ~78% live. |

## DISTINCTNESS — holds, one pair on watch
Material classes (bronze / glass+flame / iron-lacquer / cloth / void+iron) and
chain relationships (hanger / belay-to-hook / operating wire / halyard /
belay-to-leaf) are five genuinely different kinds. But:
- **`clear-arm` and `colours-up` collapse at 1x as specified** — both roughly
  horizontal quadrilaterals carrying gold type in a band, and they are the
  designer's #1 and #2. The fixes separate them decisively: clear-arm goes
  permanently diagonal; colours-up gets a **deep** swallowtail (bite >=22px, not
  "shallow") and a real curl so top and bottom edges are visibly non-parallel.
  **Insist on both.**
- Two of five used arced type, both flagged weak. Only `ring-out` keeps the arc.

## ITERATION DIRECTIVES (all binding)
1. **Local-value constraint:** backdrop L36 day / L21 night. Every concept is a
   **light-value figure**; single bright keyline legal, no two-step needed.
   **Reject any body colour below ~L70 for large masses.**
2. `clear-arm`: rework per the replacement direction. **Keep the operating-wire
   tie and the taut-vs-sagging line-quality contrast verbatim** — best ideas in
   the document.
3. `ring-out`: **delete the bell-cot.** Bell hangs on the chain alone. Promote
   the hemp bell-rope to the affordance — the thing at thumb height is a rope
   you pull, which rings the sign.
4. `ring-out`: type **26px tracked +2 (93px)**, seated low against the sound-bow.
5. `beacon`: **three facets**, one unbroken 96-104px centre glass. Render **both
   type polarities** side by side at 1x before committing.
6. `beacon`: **no bloom** — stepped text-mask dilations per `store_design._build_aura`.
7. `beacon`: **zero pixels of light on the three planks.**
8. `the-drop`: **flat struck chord on the collar's front face, 22px.** Kill the arc.
9. `colours-up`: **publish the flag rect, prove masthead <=y532**, then deepen
   the swallowtail to a >=22px bite and curl the fly.
10. `colours-up`: **warp the cloth, not the word.**
11. `the-drop`: **justify or cut the cloud-bank floor.** It is a second design,
    not "elsewhere" — it fights `_draw_mountain_silhouette` (alpha 180), risks
    reading as the scrolling near-lane ("the game already started"), and a
    high-luma cloud mass *below* the dark mountain band inverts the screen's
    value structure at the bottom edge. If kept: under y600 and darker than any
    sky cloud.
12. `the-drop`: **resolve the leaf's shape.** "Foreshortened ellipse-plate" and
    "identical chamfer + V-notch plank profile" are contradictory. **Take the
    plank profile** — the V-notch inheritance is the whole tie — tilted back 70
    deg, underside in shade. It carries no type and sits at an angle, so it
    reads as a lid, not a fourth sign.
13. **Every concept: publish a 1x thumbnail strip at PHASE 0.0 / 0.20 / 0.45 /
    0.65 plus a greyscale pass**, and a crop of the START quadrant alone at 1x.
    Every risk in this set (fourth-plank read, knockout clogging, arced type,
    warped type) is a **thumbnail** risk and cannot be judged at 2x.
14. **Do not bench-swap `the-windlass`.**

## REUSE, don't reinvent
- `store_design._build_aura` (~200) — numpy-free stepped-falloff glow.
- `store_cards.gloss_sweep` (:618) — shipped specular; composites via BLEND_ADD
  off a cached masked layer. Copy the pattern.
- `hud._tracked_label` (:1189) — per-glyph tracking. Arced type needs a rotozoom
  wrapper around the loop, ~10 lines; key the glyph cache on (char, size, angle).
- `tools/menu-design/launch_perch_start.py:79 soft_shadow`, `:157 timber_board`
  — reuse rather than reinvent; source of the BLEND_RGBA_MIN masking pattern.
- Round 7 `bleached-board` — the figure/ground inversion precedent the reworked
  `clear-arm` should be built on.
