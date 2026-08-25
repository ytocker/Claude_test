# menu-v4 — LOCKED briefs (Phase 3). Shared block + 5 concepts.

# SHARED CONTEXT — applies to every concept

## S1. Measured backdrop (real pipeline, not reconstructed)
Built with the shipped stack — sky -> `foreground.draw_near_lane` -> `(6,1,21,110)`
veil -> `_draw_mountain_silhouette(alpha=180)` — sampled at biome phase 0.20 (day)
and 0.75 (night). Rec.601 luma 0-255.

| footprint | day min/med/max | night min/med/max |
|---|---|---|
| x60-300, y468-544 (canonical CTA band) | 45.0 / 48.5 / 50.1 | 16.5 / 20.9 / 21.3 |
| x132-228, y458-554 (jade seal) | 45.0 / 48.5 / 50.1 | 16.5 / 21.0 / 21.3 |
| disc cx180 cy508 r64 (gong) | 45.0 / 47.3 / 50.1 | 16.5 / 20.3 / 21.3 |
| x92-268, y452-584 (noren panel) | 45.0 / 46.2 / 50.1 | 16.5 / 17.5 / 21.3 |
| x20-340, y412-620 (plaster plaque) | 19.0 / 46.5 / **115.9** | 14.1 / 18.4 / 28.1 |
| x40-320, y558-616 (secondary row) | 45.3 / 46.2 / 46.9 | 17.1 / 17.5 / 18.5 |
| open sky y300-366 | 45.2 / 102.4 / 106.4 | 17.6 / 18.6 / 130.4 |
| y402-458 (the SHIPPED pill) | 45.2 / 47.6 / **113.4** | 18.8 / 21.0 / 23.0 |

1. **Below y~468 the polarity does NOT invert.** Near-constant ink plate: day
   45-50, night 16.5-21.3, total swing 29 luma. A permanently light CTA there
   clears >=140 at BOTH poles with no trickery. Every concept places its CTA there.
2. **The shipped pill's straddle is confirmed and worse than the brainstorm said** —
   day max **113.4** inside its own footprint (open sky at x110-120 above the far
   ridge, which crosses y~394 at centre but only y~445 at x=110). One shape, two
   backdrops, 66 luma apart.
3. `x20-70, y412-466` is the ONE sky wedge surviving below y412 (day up to 115.9).
   Only `plaster-tablet` touches it, and it covers it with an opaque plane.
4. Night backdrop above L60 is 136 scattered near-lane lamp pixels total, all in
   y181-367, max L130.4 — 0.1% of that region, outside every CTA footprint.

## S2. The chroma-ratio test (replaces bare hue-distance)
Hue distance alone mis-scores near-neutrals. What actually killed `cinnabar-gate`
and old `silk-noren` was *same hue AND same chroma AND same value*.
chroma = (max-min)/255. Reference: gold `_GOLD_BRIGHT (240,192,64)` chroma
**0.690**, luma 191.8; rust `_SCARLET_TOP_DIM (220,45,22)` chroma **0.776**, luma 94.7.

| | dH vs reference | chroma | ratio vs gold | dLuma |
|---|---|---|---|---|
| CULLED cinnabar mid (206,52,34) vs rust | 0.7 | 0.675 | 1.02x | 1.3 |
| CULLED silk amber (248,196,86) vs gold | 2.9 | 0.635 | 1.09x | 7.2 |
| ridge lamp body (250,241,224) | 4.4 | 0.102 | **6.77x** | 50.0 |
| silk raw top (234,231,229) | 19.6 | 0.020 | **35.2x** | 39.9 |
| plaster lit (236,231,222) | 5.1 | 0.055 | **12.6x** | 39.7 |
| jade mid (96,178,146) | 112.9 | 0.322 | 2.15x | 41.9 |
| gong body (46,150,190) | 153.0 | 0.565 | 1.22x | 68.3 |
| lapis top (46,70,152) | 177.2 | 0.416 | 1.66x | 119.6 |

**RULE: a surviving CTA clears gold/rust either by dH >= 110 deg, OR by
chroma-ratio >= 3x with dLuma >= 35.** Both culled candidates fail both arms at
~1.0x. All five locked concepts pass.

## S3. Shared layout (identical in all five; hud.py-only)
Unchanged: SKYBIT y126, subtitle y184, divider y208, `skyhouse_post`
rect(28,208,160,120), Pip, and the
`menu_profile_rect`/`menu_store_rect`/`menu_top10_rect`/`menu_settings_rect`
publication contract.

Changed, same in all five:
- **START moves cy 430 -> the concept's footprint inside y444-584.**
  `menu_start_rect` is still whatever `draw_menu` publishes;
  **`scenes.py` is UNTOUCHED in all five concepts.**
- **Secondary row moves cy 554 -> cy 587** (tiles 84x54 -> y560-614, 26px bottom
  margin). Its backdrop is flat at both poles (day 45.3-46.9, night 17.1-18.5).
- **BEST is surfaced.** `draw_menu(self, surf, dt, best)` currently never reads
  `best`. Every concept renders `BEST {best}` (`BEST —` when best == 0) **on its
  own opaque plane**, never on raw sky.

## S4. The upper-left ruling (identical in all five — the round-1 gate)
- **(a) `skyhouse_post` rect(28,208,160,120): KEPT, UNTOUCHED.** Drawn by
  `scenes.py:1688-1691` exactly as today. No concept draws over it.
- **(b) PROFILE rect(16,196,184,164): stays a full tappable card at the same rect**,
  same brass nameplate slot y336-360, same `self.menu_profile_rect = fr`.
  **The player's equipped skin remains fully visible on the menu.** Only the
  *frame material* is restyled per concept, replacing the pulsing gold double-rule
  so the screen carries one material language. Not demoted to a badge anywhere.
- **(c) Draw order: NO concept places anything behind Pip. No `scenes.py` two-pass
  split, no `world.bird` re-blit, in any of the five.** Every concept's furniture
  begins at or below **y>=360** (the card's bottom edge); the PROFILE frame is a
  thin perimeter that legitimately draws on top because it *frames* him. The veil
  issue does not arise because nothing opaque covers the diorama.

## S5. `_draw_mountain_silhouette` — explicit position
- **Repalette (jade-seal, cloisonne-gong, silk-noren, plaster-tablet):** replace
  the off-palette SVG greens `(14,26,12)`/`(10,18,8)` with the luma-matched cool
  ink pair **far `(18,22,28)`, near `(12,15,20)`**, alpha 180 unchanged. Source
  luma 20.8/14.5 -> new 21.5/14.7. **Every backdrop number in S1 holds within 1.0
  luma**, so nothing needs re-deriving; only the hue defect is gone (the new pair
  matches the `(6,1,21)` veil).
- **Occlude (ridge-cut only):** delete the `_draw_mountain_silhouette` call. The
  paper sheet covers y>=366 at every x, so the ridge is never visible. This is
  what structurally removes the two-stacked-ridgelines defect. Saves one
  full-screen SRCALPHA blit per frame.

## S6. PLAY AGAIN / TAP TO GAME — baseline for all five
`hud.py:2514` PLAY AGAIN is currently `_pill_btn(..., size=22, alpha=255,
min_width=240, primary=True, dim=True, shadow=False)` — identical weight to menu
START. **VERIFIED by the orchestrator: `primary` controls ONLY the gold halo
(hud.py:474-481) and nothing else.**

> **Baseline (all five):** drop `primary=True` at 2514 — a one-token change that
> makes PLAY AGAIN strictly quieter with no move, no rewording, no size change.
> `TAP TO GAME` (2032) is already dim and non-primary; leave it alone. Each
> concept then adds ONE cheap token behind PLAY AGAIN (per brief) so the two
> screens are related without being equal.

## S7. Shared craft rules
- **No 1px features anywhere.** `store_cards.SS = 2`, so a "1px" author becomes a
  half-pixel after `smoothscale` and returns as a 50%-alpha grey smear with its
  hue washed out. Every hairline below is stated at **>=3px authored at SS=2**
  (= 1.5 logical px). Any contrast step that depended on a 1px feature has been
  re-derived onto a >=3px carrier.
- **Two-step contour on everything:** hue-matched near-black keyline (luma 8-32)
  + pale crown (luma 185-240). One step separates by day, the other at night.
- **No blur, no bloom.** Banded stepped ramps and hard specular slivers only.
- **Fixed absolutes, stated deliberately.** Unlike `pillar_pagodas`
  (`_cedar(palette)`), every colour here is a fixed absolute like `store_design`.
  Correct for a UI layer — but say so, because these planes sit on world art that
  shifts underneath. Consequence: each static plate is biome-independent and can
  be cached once forever.
- **Build budget.** Do NOT build a full-screen SS=2 surface — 720x1280x4 = 3.7 MB
  and a 20-40 ms `smoothscale` hitch at menu entry on WASM. Author each concept's
  static plate as **at most a 360x300 logical region** (720x600 @ SS=2 = 1.65 MB)
  plus the PROFILE frame as a separate 184x164 region (368x328 = 0.48 MB). Two
  smoothscales, each <20 ms, split across the first two menu frames, cached
  module-level. Only the CTA pulse (and noren's sway) redraws per frame.
- Reuse `store_cards.bevel_rim / vgrad_stops / top_sheen / contact_shadow /
  facet_gem` and `store_design.make_rim_shine_frame / frame_double_bevel`
  wherever they fit — that is where the round-1 floor comes from.
- `gfxdraw` is BANNED (crashes mobile SDL). numpy is ABSENT on pygbag.
  `pygame.draw` WRITES alpha rather than compositing — route translucent work
  through scratch layers. `Rect.inflate()` takes the TOTAL delta, not per-side.

Measurement script kept for re-verification: `scratchpad/measure_bands.py`

---

# 1. `ridge-cut`

**Thesis.** The whole lower UI is one sheet of ink-black paper, cut away in the
剪紙 window-lattice tradition and lit from behind. START is not an object with a
colour — it is a hole with lamplight coming through it, structurally immune to the
day/night flip.

**Top edge is ORNAMENT, not landscape.** The sheet's top boundary is a repeating
**window-lattice profile**: a 6-unit run of squared 卍-fret returns and
quarter-round ruyi scrolls, envelope y366 (peaks) to y398 (valleys), strictly
rectilinear-plus-quarter-arcs, **no peak-and-valley silhouette that could read as
a ridge**. Clears the profile card's bottom edge (y360) by 6px at the peaks.
Because it occludes the real ridgeline entirely (S5), there is exactly one skyline
on screen and it is the fret.

**The cut edge is lit at BOTH poles.** The entire top cut edge and every aperture
edge carries a **3px warm lamp-rim `(150,102,52)`** on the paper side, with the
outermost **3px of paper darkened to `(10,6,16)`** as a hard keyline. Day: keyline
luma 8.3 vs sky 102.4-106.4 -> **d94-98**. Night: lamp-rim luma 110.7 vs sky
17.6-18.6 -> **d92-93**. The signature line is drawn by *shadow* by day and by
*light* at night, and never disappears.

**START.** A **200x76 lozenge aperture with ruyi-lobed ends at (180,506)**
(footprint x80-280, y468-544). Paper removed; behind it a lamp plane as **5 hard
concentric bands, no blur**: `(255,253,250)` 253 -> `(250,241,224)` 242 ->
`(246,232,206)` 233 -> `(232,210,176)` 213 -> `(222,198,164)` 201. Cut-edge bevel
is **3px `(255,250,238)` on the lower-right wall and 3px `(8,4,12)` upper-left** —
that asymmetry is what makes it read as cut paper rather than a glowing rectangle,
and at 1px it would have vanished. Type is **retained paper**: render "START" in
`(18,12,26)` onto the lamp plane, with **paper-cut bridge tabs left visible**
(3px min) on the A and R counters. Paper fibre speckle L15<->L22 at 4% density
across the sheet. **The bevel, the tabs and the speckle are the three things that
must land in round 1 or the sheet reads as a loading screen.**

**CTA/secondary — LAMP POWER.** Three **r=26 circular lattice roundels** at cy 587,
cx 90/180/270, identical construction, icon retained as paper inside the light,
but on a **dimmer lamp**: 2 bands only, `(206,188,158)` 190 -> `(180,160,130)` 163,
no hot centre, no bevel kiss. Hierarchy is the *brightness of the light source*.
START 201-253 vs paper 15.4 -> **d186-238**; secondaries 163-190 vs 15.4 ->
**d148-175**. START is the brighter lamp by 63 luma at the core.

**BEST.** A narrow **140x26 slot-cut at (180,445)** directly above START, in the
paper, on the secondary lamp — `BEST {best}` as retained paper.

**PROFILE.** Same rect; frame becomes a **3px lattice-fret border `(150,102,52)`
with a 3px `(10,6,16)` outer keyline**, four corner ruyi-scroll cut-outs on their
own small lamp planes, nameplate slot reworked as a slot-cut. Pulse rides on lamp
brightness, not gold alpha.

**PLAY AGAIN.** S6 baseline + a **200x62 lamp-plane lozenge at 45% alpha behind
the pill** on the overlay's existing dark scrim. Cheapest propagation in the set.

| role | RGB | H | luma | notes |
|---|---|---|---|---|
| paper field | (18,12,26) | 265.7 | 15.4 | d91.0 vs day sky |
| paper keyline 3px | (10,6,16) | 264.0 | 8.3 | **d98.1 vs day sky** |
| lamp-rim 3px | (150,102,52) | 30.6 | 110.7 | **d92.1 vs night sky** |
| lamp hot centre | (255,253,250) | 36.0 | 253.3 | d237.9 vs paper |
| lamp body | (250,241,224) | 39.2 | 241.8 | d226.4 vs paper |
| lamp outer band | (222,198,164) | 35.2 | 201.3 | d185.9 vs paper |
| **sign** = retained paper | (18,12,26) | 265.7 | 15.4 | internal **d218-226** |
| secondary lamp | (206,188,158) | 37.5 | 190.0 | d174.6 vs paper |

**Gold-collision (S2).** Lamp bands 1-3 sit at chroma-ratio **35.2x / 6.77x /
4.40x** vs gold with dLuma 41-62. Band 5 is 3.03x at dLuma 9.5 but is a 3px ring
at <=8% of aperture area. Area-weighted mean chroma ~0.10 vs gold 0.690 — the
aperture reads as *white light*, not gold pigment.

**CTA below y490?** Top edge y468, 22px above — but it sits on the sheet, opaque
from y366 down. Self-grounding.

**Delight.** Lamp flickers on a 3-line sine; the five apertures breathe out of
phase. On tap START's aperture blooms to fill the screen and the paper burns away.

---

# 2. `jade-seal`

**Thesis.** The screen is a collector's presentation case holding one carved jade
seal. START is the seal's face — a precious object, the menu the velvet it sits on.

**The lid is GONE.** The brainstorm's raked open lid occluded Pip and the house and
forced a draw-order change. Deleted. The case is now a **shallow closed-back tray,
y412-620 only** (S4-c: nothing above y360, no `scenes.py` change, no bird re-blit).
What the lid was for — a bright ground behind Pip — was never needed: Pip has his
own internal contrast and the profile card already frames him.

**The label is rebuilt on RELIEF, not hue.** The brainstorm's cinnabar-in-jade
groove was d55 luma encoded as red-in-green, the worst pair for protan/deutan
vision. Replaced: the groove is a **dark cut**, fill `(30,50,42)` luma **43.1**
against jade mean **149.8** -> **d106.7 luma, hue-independent** (both stops H156-157,
so the label survives full desaturation). Groove walls carry a **3px `(244,240,232)`
catch-light upper-left** and a **3px `(18,30,26)` shadow lower-right** — at 1px
these were the first things the downsample washed out. Genuine 朱文 intaglio, now
read by light instead of by red.

**START.** A **square 96x96 chamfered jade seal at (180,506)** — footprint
x132-228, y458-554 — corners cut 45 deg to an octagonal outline. Square, not a
pill: the real 印章 form, and the only square CTA in the set. 5-band vertical ramp
`(168,224,192)` 203.6 -> `(96,178,146)` 149.8 -> `(44,116,96)` 92.2, plus two
low-alpha diagonal cloudiness polygons so it reads as stone, not plastic. A **3px
gilt band `(232,196,110)`** wraps the chamfer, with a **3px `(10,34,30)` outer
keyline**. "START" set large and centred at the seal's full width, as a real seal
face.

**CTA/secondary — RELIEF SIGN (+z vs -z).** START is the **only thing standing
proud** of the tray floor: `contact_shadow` under all four chamfered edges, gilt
band catching light top and left. The three secondaries are **holes** — 76x46
sunken square wells at cy 587, cx 90/180/270, icon struck *into* the brocade felt,
3px gilt lip, inner shade `(18,30,26)`. Nothing competes, because they are the
opposite sign of the same axis.

**Case.** Black-lacquer walls `(20,14,16)` luma 16.0, mitred **3px** gilt inlay set
6px in from every edge (`store_design.frame_double_bevel` directly), brocade-red
felt bed `(88,26,22)` luma 44.1 as fine cross-hatch. No curves anywhere except the
seal's cloudiness — chamfered blocks throughout.

**BEST.** Engraved in gilt intaglio into the case's **front lip, x60-300, y566-590**
— same relief construction as the START label at half scale, on opaque lacquer.

**PROFILE.** Same rect; frame becomes a **matching lacquer-and-gilt case wall**:
3px `(232,196,110)` mitred inlay, 3px `(10,34,30)` keyline, corner miter notches,
nameplate slot re-cut as a gilt-lipped well.

**PLAY AGAIN.** S6 baseline + a **3px gilt mitred inlay rectangle 6px inside the
pill** — the case's own edge detail, one `draw.rect`, no new colours.

| role | RGB | H | luma | d vs day 45.0-50.1 | d vs night 16.5-21.3 |
|---|---|---|---|---|---|
| jade face top | (168,224,192) | 145.7 | 203.6 | **153.5-158.6** | **182.3-187.1** |
| jade mid | (96,178,146) | 156.6 | 149.8 | 99.7-104.8 | 128.5-133.3 |
| jade bot (lowest step) | (44,116,96) | 163.3 | 92.2 | **42.1-47.2** | **70.9-75.7** |
| gilt chamfer 3px | (232,196,110) | 42.3 | 197.0 | 146.9-152.0 | 175.7-180.5 |
| outer keyline 3px | (10,34,30) | 170.0 | 26.4 | 18.6-23.7 | 5.1-9.9 |
| **sign** groove fill | (30,50,42) | 156.0 | 43.1 | internal **d106.7** vs jade mean | constant |
| sign catch-light 3px | (244,240,232) | 40.0 | 240.3 | d197.2 vs groove | constant |
| sign shadow 3px | (18,30,26) | 160.0 | 26.0 | d17.1 vs groove | constant |
| lacquer case | (20,14,16) | 340.0 | 16.0 | opaque, self-grounding | — |

dH vs gold **112.9** (>=110, passes hue arm); vs rust 149.6.

**CTA below y490?** Seal top y458, 32px above — but on the opaque lacquer tray
(y412-620). Self-grounding. The seal's own footprint measures day 45.0-50.1 /
night 16.5-21.3 even without the tray.

**Delight.** On tap the seal presses down 3px and stamps a cinnabar impression of
the Skybit mark onto the felt beside it.

---

# 3. `cloisonne-gong`

**Thesis.** A single 景泰藍 enamelled medallion — the only closed curve on a screen
of rectangles — hung from a minimal gilt rail. START is a disc you strike.

**The A-frame is DEAD.** The raked cedar posts ran through the house sprite, drew
over Pip, and pushed the concept into the "too much like the in-game pillar set"
bucket. Deleted. Replaced by a **minimal gilt rail: a 220x14 horizontal bar at
(180,441)**, x70-290, 3px bezel stack, from which the disc hangs on **two 3px
braided cords** with a visible knot. This is UI furniture — a hanging-rail, the
same object class as the store's card rails — not depicted architecture. The whole
assembly lives y434-572, clear of the profile card by 74px.

**The rim is now the LIGHT step and the wire is buildable.** The brainstorm's petal
cells were deep-at-rim, making the outermost 3px luma 78 -> only d28-38 by day.
Inverted: **the outer ring's cell gradient now runs highlight-at-rim ->
body-at-centre**, so the outermost cell is `(140,214,236)` luma **194.4**. On top,
a **solid 3px gilt outer bezel `(240,206,120)` luma 206.4** with a **3px
`(44,30,10)` contact keyline** outboard. Outer ring cut **16 -> 10 ruyi-lobe
petals** so each cell is wide enough to hold its 2-step gradient after downsample.
All cloisonné wire authored at **3px** — at 1px the defining feature of the
technique would have resolved as grey haze and taken the disc's second contrast
step with it.

**START.** Disc **r=64 at (180,508)** (footprint y444-572). Construction: 3px gilt
bezel -> outer ring of 10 ruyi-lobe cells -> middle ring of 8 -> plain central boss
carrying the type. Enamel `(140,214,236)` 194.4 / `(46,150,190)` 123.5 /
`(22,96,134)` 78.2, cells separated by 3px gilt wire `(226,180,86)` 183.0. Boss is
enamel-deep 78.2 with type in **pale gilt `(250,226,160)` luma 225.7 -> internal
d147.5** (the brainstorm's gilt-on-deep was d105; the pale stop buys 43 more free).

**CTA/secondary — CHROMATIC PRESENCE.** The disc is the **only enamelled object on
the screen**. The three secondaries are **bare struck bronze**: 60x48 octagonal
tokens at cy 587, cx 90/180/270, `(122,96,54)` luma 99.0, struck icon in relief,
3px bevel, **zero enamel, zero saturated colour**. Hierarchy is presence/absence of
the second material's colour. **They are NOT on the rail** — the rail carries the
medallion and nothing else, which is what breaks the banned "horizontal member with
three things hung beneath" skeleton.

**BEST.** Struck into the **gilt rail** at (180,441) — `BEST {best}` in `(44,30,10)`
intaglio on the rail's gilt face. The rail is opaque and self-grounding, which it
needs to be: its own footprint x70-290 y430-452 measures day max **113.1** (the
x110-120 sky wedge).

**PROFILE.** Same rect; frame becomes the **same 3px gilt bezel stack as the disc's**
(`store_design.make_rim_shine_frame(s=1.0)`), with four small enamel corner cells in
`(46,150,190)` — the only other place enamel appears, tying the card to the CTA.
Nameplate becomes a struck bronze token.

**PLAY AGAIN.** S6 baseline + a **single r=13 enamel cell in `(46,150,190)` with a
3px gilt wire ring, inset at the pill's left cap**. One dot of the CTA's material;
the pill stays a pill, at strictly lower weight than a 128px medallion.

| role | RGB | H | luma | d vs day 45.0-50.1 | d vs night 16.5-21.3 |
|---|---|---|---|---|---|
| enamel highlight (**now the rim**) | (140,214,236) | 193.8 | 194.4 | **144.3-149.4** | **173.1-177.9** |
| enamel body | (46,150,190) | 196.7 | 123.5 | 73.4-78.5 | 102.2-107.0 |
| enamel deep (boss only) | (22,96,134) | 200.4 | 78.2 | 28.1-33.2 | 56.9-61.7 |
| gilt bezel 3px | (240,206,120) | 43.0 | 206.4 | **156.3-161.4** | **185.1-189.9** |
| bezel keyline 3px | (44,30,10) | 35.3 | 31.9 | 13.1-18.2 | 10.6-15.4 |
| cloisonné wire 3px | (226,180,86) | 40.3 | 183.0 | 132.9-138.0 | 161.7-166.5 |
| **sign** pale gilt | (250,226,160) | 44.0 | 225.7 | internal **d147.5** vs boss | constant |
| bronze token (secondaries) | (122,96,54) | 37.1 | 99.0 | 48.9-54.0 | 77.7-82.7 |

dH vs gold **153.0**; vs rust 170.3. Both >>110. Blue/yellow is also the CVD-safest
axis available, so the one saturated element is the one every colour-vision type
can separate from the gold.

**CTA below y490?** Disc top y444, 46px above — sits directly on the ink plate with
no ground plane, and **the disc's own circular footprint measures day
45.0/47.3/50.1, night 16.5/20.3/21.3.** The bounding-box corners that clip the
x114-120 sky wedge contain no disc pixels. Confirmed by measurement.

**Delight.** On tap the disc swings on its cords with the knot lagging. **Cap this
at a precomputed 5-frame rotation LUT** — do not rotate a 128px alpha surface per
frame on WASM.

---

# 4. `silk-noren`

**Thesis.** The menu is cloth, not architecture. START is a single hanging panel of
**undyed raw silk** — a huge near-achromatic bright mass with resist-dyed indigo
type. The only concept with dark-on-light type, and the only one that moves.

**Redyed to raw silk.** The old imperial amber `(248,196,86)` was H40.7 / chroma
0.635 — a **1.09x chroma ratio and 7.2 luma** from the title gold, i.e. the same
colour on the largest element on screen. Replaced by **bleached raw silk
`(234,231,229)` -> `(219,215,210)`**, HSL S **0.106 -> 0.111**, luma **231.7 ->
215.6**.

> **Measured push-back, on the record.** `S <= 0.12` in HSL is only satisfiable in
> the L215-235 band by a max-min spread of <=6/255, because HSL's denominator
> collapses to `2-max-min ~ 0.19` up there. That is why the locked stops are
> near-neutral. The result is compliant, but S-in-HSL is NOT the metric that
> separates this from gold: the top stop is **dH 19.6 from gold**, which by the old
> test looks marginal, while by the S2 chroma-ratio test it is **35.2x diluted at
> dLuma 39.9**, and the bottom stop **19.6x at dLuma 23.9**. Both clear S2 with
> enormous margin; the culled amber was 1.09x. The separation is chromatic dilution
> plus line-vs-mass (a 3px gold outline stroke versus a 176x132 field), not hue.

**No `_ruyi_lobe`.** The valance lobes must NOT be `cloud_variants._ruyi_lobe` (the
shipped in-game cloud). Author a new lobe profile: a **flat-topped 官式 scallop** —
straight rod-line, a short vertical drop, then a single shallow catenary sag to a
squared-off point. Cloth geometry, not cloud geometry.

**No brushed terminals.** "Hand-brushed 2px taper at terminals" is impossible from
LiberationSans-Bold, and polygon letterforms are a whole round that reads amateur
if they miss. Dropped. The dye character comes from a **3px resist-halo**:
`(58,66,116)` set 3px outside every glyph edge — what real 絞り resist does, one blit.

**Pip's notch is gone.** The old notch at (90,300) sat inside both the house sprite
and the profile card. The cloth assembly now begins at **y392**, 32px below the
card. Nothing touches Pip; no draw-order change.

**Construction.** A rod at y392; five flat-top scallop lobes hang y392-452 across
full width, indigo `(28,36,74)` luma 37.9 shading to `(16,20,46)` luma 21.8, with a
**3px gold-thread border `(226,190,110)`** and a knotted tassel at each lobe's low
point. Lobes 2 and 4 hang 8px lower than 3, so the row is staggered, not ruled.

**START.** The raw-silk panel hangs from the *same rod*, emerging from behind lobe 3
at y452 and falling to y584 — **x92-268, 176x132, portrait**. The only tall CTA in
the set. It is cloth: straight rod-pocket top, shallow catenary hem sag, left/right
edges bowing out 4px, two low-alpha fold-shadings at 28% and 72% width. Type:
**"START" in indigo `(30,38,84)` luma 40.9 on silk 215.6-231.7 -> d174.7-190.8**,
correct polarity because that is how dyed cloth signage works. **3px `(14,16,34)`
hem keyline** at the bottom edge.

**CTA/secondary — OBJECT vs SURFACE-DECORATION.** START is a *thing that hangs*.
The secondaries are **r=25 embroidered roundels stitched onto lobes 2, 3 and 4**
(cx 108/180/252, cy 428/418/428) in pale gold-thread satin stitch `(226,190,110)`
on indigo — marks on a surface, never objects. You cannot confuse a hanging bolt of
cloth with stitching on another bolt. Tap targets 50px diameter. **The bottom chip
row is retired in this concept only** — the panel occupies y452-584 and owns that band.

**BEST.** Embroidered on the **centre lobe at (180,404)**, gold-thread satin stitch
on opaque indigo cloth.

**PROFILE.** Same rect; frame becomes a **fabric-bound edge**: 3px gold-thread
couching `(226,190,110)` over a 6px indigo silk binding `(28,36,74)`, mitred at the
corners, nameplate slot re-cut as a woven-label patch.

**PLAY AGAIN.** S6 baseline + a **176x8 raw-silk rod-pocket strip `(234,231,229)` at
55% alpha directly under the pill**, reading as the pill hanging from cloth.

| role | RGB | H | luma | d vs day 45.0-50.1 | d vs night 16.5-21.3 |
|---|---|---|---|---|---|
| raw silk top | (234,231,229) | 24.0 | 231.7 | **181.6-186.7** | **210.4-215.2** |
| raw silk bottom | (219,215,210) | 33.3 | 215.6 | **165.5-170.6** | **194.3-199.1** |
| **sign** indigo resist | (30,38,84) | 231.1 | 40.9 | internal **d174.7-190.8** | constant |
| resist halo 3px | (58,66,116) | 228.0 | 66.4 | d25.5 vs sign (soft step) | constant |
| indigo valance | (28,36,74) | 229.6 | 37.9 | opaque, self-grounding | 16.6-21.4 |
| valance deep | (16,20,46) | 232.0 | 21.8 | 23.2-28.3 | 0.5-5.3 |
| gold thread 3px | (226,190,110) | 41.4 | 191.6 | 141.5-146.6 | 170.3-175.1 |
| hem keyline 3px | (14,16,34) | 234.0 | 17.5 | 27.5-32.6 | 1.0-3.8 |

**CTA below y490?** Panel top y452, 38px above — the panel is an opaque bright mass
and is its own ground. Its footprint x92-268, y452-584 measures day 45.0/46.2/50.1
and night 16.5/17.5/21.3, so even the top 18px sits on ink. Confirmed.

**Delight.** Panels and lobes sway on independent out-of-phase pendulums, tassels
lagging — a 3-line sine per element, ~0.15 ms/frame. On tap the START panel lifts
as though you pushed through it. **Only concept in the set that moves.**

---

# 5. `plaster-tablet` (NEW — replaces `cinnabar-gate`)

**Thesis.** Every other menu in Skybit is light-on-dark. This one inverts the
screen's **value structure**, not its ornament: a large warm-limewash plaque makes
the entire lower half a permanently *light* field, and START is the only dark thing
on it — a single deep-lapis stone inlay set into the plaster. Both biome poles are
solved by construction, because the plaque is opaque and the CTA is dark on it.

**Why this and not cinnabar-gate.** cinnabar died four ways — hue-identical to the
shipped pill (dH 0.7, chroma-ratio 1.02x, dLuma 1.3), pagoda architecture is
literally the game's own pillar set, the CTA was a red rounded rect with a gold
frame, and its lower third was d10-12 and rim-carried. `plaster-tablet` shares none:
the CTA is **dH 177.2 from gold and 140.6 from rust**, the organising metaphor is a
*plaque* (a UI object, not a depicted building — the seam the director defined), and
it is mass-carried in the opposite direction from everything else on screen.

**Material.** `pillar_pagodas._white_plaster_warm` is the game's own limewash, but
it is `_mix(palette['stone_light'], (244,232,206), 0.62)` — biome-driven and, at its
target, H41.0 / chroma 0.149, i.e. cream. As a 320x208 field that is the same trap
that killed silk's amber. **Locked as a fixed absolute instead, pulled toward
neutral:** lit `(236,231,222)` (chroma 0.055, **12.6x diluted vs gold**, dLuma 39.7)
-> shade `(206,198,185)` (chroma 0.082, **8.38x**). Still reads as warm limewash;
cannot read as gold.

**Construction.** One **320x208 plaque, x20-340, y412-620**, opaque, filling the
lower screen. Vertical ramp lit->shade with a **banded top sheen**
(`store_cards.top_sheen`), a 3px `(38,30,24)` outer keyline all round, a 3px
`(206,198,185)` inner shadow return 6px in, and **chipped corners with a 3px darker
core exposed** at two of four corners — the plaster-chip token that propagates
cross-screen. Surface tooth: 5% stipple at +-8 luma, no blur.

**START.** A **208x64 lapis inlay at (180,512)** — x76-284, y480-544 — set *into*
the plaster, i.e. recessed: 3px `(38,30,24)` shadow on the upper-left inner wall,
3px `(236,231,222)` catch-light on the lower-right (the opposite sign to jade's
proud seal, deliberately). Lapis ramp `(46,70,152)` luma 72.2 -> `(24,40,104)` luma
42.5, with **3px gold-pyrite flecks `(214,178,92)` at <=2% area** — the only gold
below y412, and it is the material's real inclusion.

**The type is RESERVED PLASTER.** "START" is not painted on the lapis — the lapis is
inlaid *around* the letterforms, so the glyphs are the plaque itself showing
through, in `(236,231,222)` luma **231.5** against lapis mean **57.4 -> internal
d174.1**. Construction-honest (真嵌 reserve inlay) and the second-best type contrast
in the set after ridge-cut.

**CTA/secondary — MATERIAL SUBSTITUTION.** The plaque is a **two-material screen**,
and START is the **only occurrence of the second material.** The three secondaries
are the field material itself, merely *tooled*: 76x46 rounded-square recesses at
cy 587, cx 90/180/270, groove `(150,140,126)` luma 141.4 with a 3px `(112,102,90)`
luma 103.6 cast shadow on the upper-left wall. No inlay, no second colour, no gold,
no light source of their own. **Nothing on the screen but START has stone in it.**

**BEST.** **Incised into the plaque's upper band at (180,437)** — `BEST {best}` in
the same tooled-groove treatment as the secondaries, at 60% scale. Opaque ground.

**PROFILE.** Same rect; frame becomes a **limewash-rendered surround**: 6px plaster
edge in the same lit->shade ramp with a 3px `(38,30,24)` keyline and one chipped
corner, matching the plaque. Nameplate slot re-cut as an incised groove. **This is
the concept's biggest compositional win** — the card and the plaque become the same
material, top and bottom, which is what makes the value inversion read as a
designed screen rather than a panel dropped on a night sky.

**PLAY AGAIN.** S6 baseline + a **240x70 plaster chip `(236,231,222)` at 40% alpha
with one chipped corner, behind the pill** on the overlay's existing scrim.

| role | RGB | H | luma | d vs day (19.0/46.5/**115.9**) | d vs night (14.1/18.4/28.1) |
|---|---|---|---|---|---|
| plaster lit | (236,231,222) | 38.6 | 231.5 | **115.6-212.5** | **203.4-217.4** |
| plaster shade | (206,198,185) | 37.1 | 198.9 | **83.0-179.9** | **170.8-184.8** |
| plaster keyline 3px | (38,30,24) | 25.7 | 31.7 | 12.7 / 14.8 / **84.2** | 3.6 / 13.3 / 17.6 |
| **CTA** lapis top | (46,70,152) | 226.4 | 72.2 | internal **d126.7-159.3** vs plaster | constant |
| **CTA** lapis bottom | (24,40,104) | 228.0 | 42.5 | internal **d156.4-189.0** vs plaster | constant |
| **sign** reserved letterform | (236,231,222) | 38.6 | 231.5 | internal **d174.1** vs lapis mean 57.4 | constant |
| pyrite fleck 3px | (214,178,92) | 42.3 | 179.0 | <=2% area accent | — |
| incised groove (secondaries) | (150,140,126) | 35.0 | 141.4 | d57.5-90.1 vs plaster | constant |
| incised shadow 3px | (112,102,90) | 32.7 | 103.6 | d37.8 vs groove | constant |

**CTA hue gates.** Lapis top **dH 177.2 from gold H43.6** and **140.6 from rust
H7.0**; lapis bottom **175.6 / 139.0**. Both stops clear the >=60 double gate by >=79.

**CTA below y490?** Inlay top y480, 10px above — and the whole thing sits on the
opaque plaque (y412-620), the substituting ground plane. The inlay's own footprint
x76-284 y480-544 also measures day 45.0-50.1 / night 16.5-21.3 independently. The
plaque's one exposure is the day sky wedge at x20-70, y412-466 (up to **115.9**),
which is exactly where the 3px `(38,30,24)` keyline runs — d84.2 there. Confirmed.

**Delight.** On tap the lapis inlay sinks 2px and a puff of plaster dust lifts from
the chipped corner.

---

# Distinctness — the five CTA/secondary relationships

1. **`ridge-cut` — lamp power.** CTA and secondaries are the *same* aperture cut in
   the *same* paper; only the brightness behind differs (core 253 vs 190, d63).
2. **`jade-seal` — relief sign.** START is the only thing standing **proud** of the
   tray floor; secondaries are **holes** sunk into it. Opposite z-sign.
3. **`cloisonne-gong` — chromatic presence.** START is the only **enamelled**
   object; secondaries are bare struck bronze with zero saturated colour.
4. **`silk-noren` — object vs surface-decoration.** START is a **thing that hangs**;
   secondaries are **stitching on another thing's surface** — a different noun.
5. **`plaster-tablet` — material substitution.** START is the only place a **second
   stone** exists; secondaries are the field material merely **tooled**.

Nearest pair is jade (proud vs void) and plaster (inlay vs incision), both
involving cutting. Separated by direction and material count: jade's CTA is the
*raised* element on a screen of *one* material; plaster's is the *sunken* element
and the *only* instance of a *second* material. Also opposite in value polarity
(jade: light figure on dark case; plaster: dark figure on light plaque) and in
silhouette (96x96 square vs 208x64 landscape). The banned skeleton — horizontal
member at y300-340 with three small things suspended beneath — **appears in none of
the five**: gong's rail carries the medallion and nothing else, noren's secondaries
are stitched onto the valance rather than hung from it, and no concept places any
furniture above y392.
