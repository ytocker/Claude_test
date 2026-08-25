# menu-v4 — art-director critique (Phase 2)

VERDICT: REWORK [cinnabar-gate, silk-noren]

`jade-seal`, `cloisonne-gong`, `ridge-cut` proceed. Two are fixed before render.

## 0. BLOCKING — the upper-left is already occupied (verified by orchestrator)

`scenes.py:1682-1693` + `hud._draw_profile_card` (1967, called 2078): the menu
already draws a **160x120 `skyhouse_post` sprite at rect(28,208,160,120)** with
Pip in front, then frames both as **PROFILE — a pulsing gold double-rule card at
rect(16,196,184,164)** with a brass nameplate at y336-360.

That is a 184x164 element owning the upper-left down to **y=360**. All five
concepts put a horizontal member through it (gate beam 300-330; gong post
242-330; valance 300-340; paper edge 290+; jade lid ~200-420).

PROFILE is not a "discovered fourth entry point" — it is the **largest object on
the screen**, it is tappable, and its docstring states *the player's equipped
look shows through the frame*, so it is where store purchases pay off. All five
silently demoted it to a badge/medallion/aperture. That is a product decision and
it was unargued.

**Draw order is a hard constraint.** House + near lane + Pip are drawn FIRST,
then `draw_menu` blits the `(6,1,21,110)` veil over them, then stars, then
mountains, then all UI. So:
- Anything drawn in `draw_menu` lands **on top of Pip and the house**.
  `jade-seal`'s gold-leaf lid "behind Pip" and `cloisonne-gong`'s perch peg are,
  as specified, **in front of** him. Each needs either a scenes.py two-pass order
  (background art -> Pip -> foreground UI) or a re-blit of `world.bird` after UI.
- Pip and the house are veiled ~43% toward near-black while new art is full
  strength — a large opaque plane will make Pip look like he is behind glass.
  Cheap fix: skip the veil in the region the plane covers.

**ROUND-1 GATE, every concept, one line each:** (a) fate of `skyhouse_post`
rect(28,208,160,120); (b) what PROFILE rect(16,196,184,164) becomes and whether
the equipped skin still shows on the menu; (c) draw order for anything meant to
sit behind Pip. **Nothing renders until this is written.**

## 1. Ruling on the strategy — half right

Correct half: `store_design`/`store_cards` metalwork IS Skybit's own UI
vocabulary, is the highest craft bar shipped, and is not gameplay furniture.
Building from `bevel_rim`, `frame_double_bevel`, `make_rim_shine_frame`,
`facet_gem`, `vgrad_stops`, SS=2-then-smoothscale is right and gives a high floor.

Wrong half: **four of five don't deploy that language, they deploy a new object
metaphor rendered WITH it.** The eye reads the metaphor first, the material
second. "The gilt is ours" does not rescue "the object is a temple gate."

And the two rejection buckets OVERLAP; the metaphors land in the overlap:
- `pillar_pagodas` ships Horyu-ji, Fogong, Shwedagon, Pha That Luang, Boudhanath
  **as pillars**. East-Asian temple architecture is not foreign — so
  `cinnabar-gate` and `cloisonne-gong`'s A-frame fall into bucket 2, *"too much
  like current in-game design."* cinnabar-gate is the low-risk hedge on
  cross-screen consequence ONLY; **on user rejection it is the highest-risk item.**
- `silk-noren`'s valance lobes are `_ruyi_lobe` from `cloud_variants.py` — the
  shipped in-game cloud. Building the crown ornament out of literal clouds.
- `ridge-cut`'s "shan-shui skyline" top edge sits directly above
  `_draw_mountain_silhouette`'s real ridgeline. **Two stacked ridgelines.**

**The seam is narrower than drawn: the organising metaphor must itself be a UI
object — a frame, plate, case, aperture, lit panel — not a depicted thing from a
world.** By that test only `jade-seal` (a container = the store popup's own
skeleton) and `ridge-cut` (material + light, no depicted object) are on it.
`cloisonne-gong` survives only if the disc reads as a MEDALLION, which means
weakening the A-frame hard.

## 2. Quantitative audit

Arithmetic verified sound. Ink-plate figures reconstruct correctly. Finding A's
structure is real and "move START below y490" is the single best structural idea
in the document. But sampling the shipped day frame gives real day ink at
y520-560 of **L16-50**, wider than the claimed 41-46.

**Hue — never computed by the designer, and it decides the verdict.** All values
below re-verified by the orchestrator:

| | H | S | vs |
|---|---|---|---|
| current `_SCARLET_TOP_DIM` (220,45,22) | **7.0** | .82 | — |
| title `_GOLD_BRIGHT` (240,192,64) | **43.6** | .85 | — |
| cinnabar face top (236,88,52) | 11.7 | .83 | **delta 4.7 from the shipped pill** |
| cinnabar face mid (206,52,34) | 6.3 | .72 | **delta 0.7** |
| silk top (248,196,86) | 40.7 | .92 | **delta 2.9 from the title** |
| jade mid (96,178,146) | 156.6 | .35 | delta 150 OK |
| cloisonne body (46,150,190) | 196.7 | .61 | delta 190 OK |
| ridge-cut light (255,228,168) | 41.4 | 1.00 | gold-adjacent, separated by L.83 + S |

The user asked verbatim about **"the color of the start button."** cinnabar-gate
answers *the same red*; silk-noren answers *the title's gold*. The first is a
re-render of the status quo, the second a hierarchy collision with the largest
element on screen. Neither survives a seventh review.

**Rim vs mass.** `cinnabar-gate` is rim-carried by its own admission ("the frame
holds the silhouette"); its body bottom stop L60 vs real day ink L48-50 is
**delta 10-12**, and red at L60 on dark ink is the classic protanope failure
pair. `cloisonne-gong`'s delta 78-83 is a MEAN — petal cells are deep at the rim,
so the disc's outermost 3px is L78 => delta 28-38 by day; mass separation is
genuinely strong so it isn't fatal, but the silhouette edge is its weakest step.
`jade-seal`, `silk-noren`, `ridge-cut` are correctly mass-carried at both poles;
ridge-cut's "no step below delta 180 at any phase" checks out.

**Internal type contrast — the delta nobody computed:**

| concept | label | face | delta |
|---|---|---|---|
| ridge-cut | paper L15 | aperture L229-247 | **214-232** |
| silk-noren | ink L26 | silk L149-199 | 123-173 |
| cinnabar-gate | gilt L232 | lacquer L96 | 136 |
| cloisonne-gong | gilt L183 | enamel L78 | 105 |
| **jade-seal** | cinnabar groove L95 | jade mean 150 | **~55** |

`jade-seal` has the best figure/ground separation and the **worst label
legibility**, encoded as red-in-green — the worst pair for protan/deutan vision.
Must be fixed in round 1 or the concept fails on accessibility.

## 3. Distinctness — one convergence, three wide

The five differ genuinely on CTA form. They FAIL on secondary construction:
cinnabar (3 plaques hung from a beam, y~355), gong (3 bells on a crossbeam,
y~365), noren (3 panels from a rod, y~390-450). **One skeleton — horizontal
member at y~300-340 with three small things suspended beneath — worn three
times.** Only `jade-seal` (secondaries as HOLES, START the only thing proud) and
`ridge-cut` (aperture size + lamp brightness = a LIGHTING hierarchy) propose a
genuinely different CTA/secondary relationship.

Culling cinnabar takes it to two-wide; silk-noren's rework must break the pair.

## 4. Cross-screen ruling — diverging IS defensible

The three `dim=True` sites are a family by implementation convenience, not design
intent. Menu START is a front-door launch affordance on a composed brand screen;
TAP TO GAME and PLAY AGAIN are utility confirmations on a scrim over live
gameplay, in a different emotional register, never seen beside the menu. A
bespoke front door and a generic pill elsewhere is standard practice.

But the regression risk is "same word, different meaning," so:
1. **PLAY AGAIN must never be more prominent than menu START.** It currently
   carries `primary=True` at `min_width=240` — same weight. If START gets richer,
   PLAY AGAIN gets QUIETER, not level.
2. **Position and wording stay put.**
3. **Every concept owes a 2-line "what PLAY AGAIN becomes" spec.** ridge-cut's is
   best in the set (the overlays already draw a dark scrim, so the aperture
   propagates near-free and unifies all three CTAs MORE than today).

## 5. Pip ruling
- **ridge-cut** — genuinely intentional, the only one with no conflict. Cut cloud
  rises to meet him from below at x60-125; nothing occludes him, no draw-order
  change, his fixed bbox dictates where the cut goes. Caveat: shape it as an
  **ornamental ruyi scroll, not a mountain.**
- **cloisonne-gong** — right instinct, colliding in fact. Left post runs through
  the house sprite and draws OVER Pip.
- **silk-noren** — worked around. Notch at (90,300) is inside the house sprite
  and the profile card.
- **jade-seal** — worked around and technically broken; the lid occludes Pip.
- **cinnabar-gate** — post-hoc justification for a beam that has to clear him.

## 6. Feasibility — the cross-cutting trap

**At SS=2 with one smoothscale down, the minimum authored feature is 3px.**
Every "1px" in the brainstorm is authored as one supersampled pixel, downsamples
to a half-pixel, and returns as a 50%-alpha grey smear with its hue washed out.
Hits: cloisonne's 1px gilt wire (the defining feature of the technique — the mesh
will resolve as grey haze, taking its claimed second contrast step with it);
jade's thin gilt band and 1px groove catch-light; ridge-cut's 1px cut-edge bevel,
which is precisely what makes it read as paper. **Author all at 3px.**

Per concept: `jade-seal` lowest risk / highest floor (direct
`store_cards`/`store_design` calls). `ridge-cut` deceptively cheap — type is the
easiest of the five (render in PAPER colour onto the light plane; the letterforms
ARE the retained paper) — but its failure mode is **"reads as unfinished"**: a
black rect with holes looks like a loading screen unless the cut-edge bevel, the
paper fibre speckle (L18<->L22) and the visible bridge tabs all land in round 1.
`cloisonne-gong` highest ceiling, hardest to reach; cap the swing to a
precomputed 5-frame rotation LUT. `silk-noren` has one impossible claim —
"hand-brushed 2px taper at terminals" cannot come from LiberationSans-Bold; drop
it (polygon letterforms are a full round and read amateur if they miss).

**All concepts:** a full-screen SS=2 surface is 720x1280x4 = 3.7 MB and one
smoothscale is a **20-40 ms hitch at menu entry** on WASM. Build during the intro
cinematic, or across three frames in strips.

`_draw_mountain_silhouette` is a known defect (hardcoded off-palette (14,26,12)
greens from an old SVG). Each concept must state its position — repalette or
occlude, don't inherit silently.

## 7. Ranking + the one biggest fix each

1. **`ridge-cut`** — only concept that solves day/night by CONSTRUCTION; clean
   Pip solution; best type contrast (delta 214); best accessibility
   (luminance-only, immune to every CVD type); cleanest cross-screen propagation.
   "Warm lantern light, not pigment" is a real answer to "what colour," and it
   sidesteps the trap that killed cinnabar and silk.
   **FIX 1:** at night the paper is delta 0-5 and the cut skyline — the concept's
   best line — ceases to exist for half the cycle. Framing that as intent is
   wrong; it's a hole. Run `paper lit edge (30,22,42)` along the ENTIRE cut top
   edge as a 2-3px warm rim lit by the lamp behind, so the silhouette is drawn by
   light at night. **FIX 2:** re-cut the top edge as an ORNAMENTAL lattice
   profile, not a shan-shui skyline — you cannot put a ridgeline above the real
   ridgeline.
2. **`jade-seal`** — most literal satisfaction of the ask; highest round-1 floor;
   best silhouette separation; "secondaries are holes, START is the one thing
   proud" is an excellent hierarchy idea. Holistic only conditionally — the case
   owns y420-620 and its reach into the top depends on the lid, which collides.
   **FIX 1:** rebuild the label on RELIEF, not hue — 3px L240 catch-light on the
   groove's upper-left wall, 3px L26 shadow lower-right, drop the cinnabar fill
   to ~L45 so the groove reads as a dark cut. Target >=delta 90 luma,
   hue-independent. **FIX 2:** the lid draws over Pip and the house.
3. **`cloisonne-gong`** — boldest silhouette (only closed curve on a screen of
   ridgelines and rectangles = genuine pre-attentive win); best CTA colour logic
   (single cool accent on an all-warm screen, and blue/yellow is the CVD-safest
   axis available — a plus not claimed); best IDEA for Pip.
   **FIX 1:** weaken the frame until the disc reads as a MEDALLION, not an
   instrument — kill the raked cedar posts, hang the disc from a short bracket or
   two cords off a minimal gilt rail. **FIX 2:** the disc's outer edge is its
   darkest step; invert the outer ring's cell gradient so the rim is the LIGHT
   step, add a solid 3px gilt outer bezel, cut the outer ring 16 -> 10 petals.
   **FIX 3:** write the PLAY AGAIN spec.
4. **`silk-noren` (reworked)** — best composition instinct; only purely
   proportional CTA/secondary hierarchy; only concept bringing motion. KEEP the
   catenary/scallop language and the sway.
   **FIX in order:** (a) redye START to **undyed/bleached raw silk, L215-235 at
   S<=0.12**, with indigo resist-dyed ink type — keeps the huge bright value mass
   (delta 175-195 at both poles) and the correct dark-on-light polarity, and
   removes the hue collision by going achromatic; (b) secondaries stop being
   three small hanging panels in a row — make them **embroidered roundels on the
   valance itself**; (c) lobes cannot be `_ruyi_lobe` (shipped in-game clouds);
   (d) drop the brushed-terminal taper; (e) Pip's notch sits inside the house
   sprite.
5. **`cinnabar-gate` — CULL.** Hue-identical to the shipped pill (delta 4.7 /
   0.7); pagoda architecture is literally the game's pillar set so it lands in
   rejection bucket 2; the CTA is a red rounded rect with a gold frame, i.e. the
   current pill with scenery; the body's lower third is delta 10-12 and
   rim-carried by its own admission; and the beam slices the profile card. Four
   independent problems, not one fix.

   **REPLACE with `plaster-tablet`:** invert the screen's VALUE structure instead
   of its ornament. A large warm-plaster/limewash plaque
   (`pillar_pagodas._white_plaster_warm` — the game's own material) fills y~420-620
   as a permanently LIGHT field; the whole lower menu becomes dark-on-light; START
   is a single deep malachite or lapis inlay panel set into the plaster. Nobody
   else in the set inverts value, it solves both biome poles by construction, and
   it keeps a cheap cross-screen token (a plaster chip behind PLAY AGAIN).
   CTA hue must be >=60 from rust AND >=60 from gold.

## 8. Round-1 gate (all of it applies)
1. Resolve the upper-left (section 0). Nothing renders until written.
2. Cull cinnabar-gate; brief `plaster-tablet`.
3. Redye silk-noren's START; convert its secondaries to roundels.
4. jade-seal: rebuild the label on relief.
5. ridge-cut: light the whole cut edge; re-cut the profile as ornament.
6. cloisonne-gong: shrink frame to a bracket, bezel the disc.
7. **Global: no 1px features.** Restate every hairline at >=3px authored, and
   re-derive any delta that depended on one.
8. Every concept writes its PLAY AGAIN / TAP TO GAME spec (<=2 lines). PLAY AGAIN
   must end up quieter than menu START and must not move.
9. State a position on `_draw_mountain_silhouette` — repalette or occlude.
10. Confirm the CTA sits below y~490 with its own opaque ground plane if not, and
    post a real measured backdrop min/median/max for the CTA band at both poles
    from the ACTUAL pipeline (veil -> stars -> mountains over the near lane).
11. Budget the build hitch (3.7 MB surface, 20-40 ms smoothscale).
12. Surface BEST. Confirmed: `draw_menu(self, surf, dt, best)` never touches
    `best`. All five place it — keep that, it is a genuine product win
    independent of which concept wins.

## Note on materials
`pillar_pagodas` derives every material FROM the biome palette
(`_cedar(palette)`, `_bronze(palette)`), while the store UI uses fixed absolute
golds. These concepts use fixed absolutes — correct for a UI layer, but say so
explicitly, because these UI planes sit directly on world art that shifts
underneath them.
