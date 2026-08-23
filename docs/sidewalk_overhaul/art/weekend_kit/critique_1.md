# Art-director critique — round 1

VERDICT: ITERATE

**Kit-level headline:** four of six pieces are on the right track and two of them are close to shippable. But the round rests on a premise the canvas doesn't support, and I measured it: **the band your 18px figures actually occupy (y 577–594, above the far deck line at GROUND_Y 595) is BRIGHT at every phase** — 173 luma at storm 0.63, 211 at snow 0.87, 225 at sunrise, 228 at day. The near lane (y 620–638) is the opposite: 56 at storm, 106 at snow. The plan's "unmistakable at 18px against dark rain" is wrong about the backdrop. Figures on this street are silhouetted against light, and the near lane needs the reverse treatment. Several of this round's colour decisions were tuned for a dark street that doesn't exist. Everything below follows from that.

---

## Ranking

| # | Piece | Status |
|---|---|---|
| 1 | `_stall_tarp` | **Closest to ship.** Hits the brief exactly. Two fixes. |
| 2 | `_cart_folded` | Strong. EMPTY is the best new silhouette in the kit. HALF and the wheel need work. |
| 3 | `suoyi` | Right idea, wrong values. The cape-only outline is genuinely excellent — and the pole carry is destroying it. |
| 4 | `_sweeper` | Reads, but wrong body idiom and the pile is the 2nd-brightest object on a sunrise street. |
| 5 | `winter` set | The coat isn't a new silhouette (IoU 0.839 vs a shipped ped). Breath puffs are invisible. |
| 6 | 8-rib umbrella | **Measurable regression vs the shipped canopy.** Re-roll the construction. |

---

## Your four questions, answered with numbers

**Q1 — straw retint rate. Neither 34% nor 55%. The lever is wrong.**

Measured in a real storm frame at GROUND_Y−1, contrast against the pixels each figure replaces:

```
suoyi pole          mean|ΔL| 67.3   (piece mean L 94.7, max 139.8)
suoyi crate         mean|ΔL| 76.8
SHIPPED pole vendor mean|ΔL| 88.3   (piece mean L 72.7)
SHIPPED umbrella ped mean|ΔL| 80.6
```

Your signature storm silhouette is currently **the least contrasty figure on the storm street.** Holding warmth as implemented parks the straw at L 120–140, which is a dead zone: ΔL 53 against the bright far band, ΔL 64 against the dark near deck — never crisp in either lane.

The warm hue is right and worth keeping — `_straw` holds R−B = 34 at night where cloth holds 10, and that's a real second channel that survives colourblind viewing. So keep the hue, **kill the value.** Retint the straw toward a warm dark — mix toward `(58, 46, 38)` at ~0.45 instead of toward `(54, 64, 96)` at 0.34 — landing the cape body at **L 85–95 with the tan hue intact.** Warm *and* dark: hue separation from the cool street, value separation from the bright band behind it. Target mean|ΔL| ≥ 85 to sit with the shipped cast.

**Q2 — umbrella panel alternation. It isn't reaching the screen at all, so 16 vs 24 is moot.**

Canopy at r=8, colour idx0 (base L 116.7, panel_b 100.7, rib 82.7, dark 70.7). Rendered pixel census:

```
83 (rib tone) ...... 49 px
71 (dark outline) .. 51 px
101 (panel_b) ...... 21 px
117 (BASE COLOUR) .. 14 px
```

The base colour is 10% of the canopy. A horizontal scan 4px below the apex is a flat run of eight identical 82.7 pixels — zero alternation. Cause: 9 rib lines converge on one apex over an 8px radius and are drawn *after* the panel fills, so they overwrite them. Net effect across all five colours: **the new canopy is 27% larger in area and 4–5 luma DARKER in mean than the shipped one** (84.7 vs 89.6 on idx0), i.e. bigger and muddier against a dusk sky. The umbrellas are the colour confetti of the rain chapter; this desaturates them.

You already had the correct instinct on the cart — *"three, not eight: at 8px across, eight spokes fill the interior solid."* Apply it here. 8 ribs in a 17px canopy is 2.1px per panel at the hem and 0 at the apex; it is not renderable.

**Q3 — HALF vs EMPTY. They're distinct as masses, but HALF fails for a different reason.**

```
IoU loaded/half  0.276     envelopes: loaded 36×25, half 41×24, empty 37×17
IoU loaded/empty 0.415
IoU half/empty   0.444
```

EMPTY is the best silhouette in the kit — a clean 3px×27px bar at wheel-top height, handle running down to the deck, mat leaning. Flat, low, parked. Positive read, exactly as you argued. Ship it.

HALF's problem: its distinguishing feature is a **1–2px wide diagonal hairline** running from y+13 to y+23, over a lower mass that reads as a generic 20–24px blob. At 1× on a day street with foliage behind it, that thread disappears and you're left with the blob. Also the basket sits 3px clear of the cart at most rows and inflates the envelope to 41px — at 1× it reads as a separate prop.

**Q4 — tarp pitch. 13.3° (13px rise over 55px span = 4.3 sheet-thicknesses) is enough. Keep it.**

It reads as deliberate because nothing else on the street tilts that way. The actual risk is the opposite of what you asked: the sheet's day luma is 131.8 against a 159-mean day deck, so the *lower half of the slope loses its edge* against the paving it's heading toward. That's a value problem, not an angle problem.

---

## Per piece — KEEP / FIX

### 1 · `_stall_tarp` — the best piece in the round

**KEEP.** Everything about the storytelling. Pitched sheet, rope turns, one guy line, the shadow cave, the runoff dashes (measured: 3px dashes at L 119 with 3px gaps over a 27px fall — that will read as moving water), and above all **the steam and the brazier still going.** The piece says "open despite rain" in one glance, which is the whole point. The `_clamp_surface_luma` routing through the shipped `props_cast` contract is exactly right — measured composite 145.8 against a coin max of 229.5, so the coin stays clearly brightest. This is disciplined work.

**FIX.**
1. Sheet is 3px with a 1px `tarp_hi` line directly above a 1px `tarp_dk` outline — they fight. Go to **4px: 1px `tarp_hi` top / 2px `tarp` body / 1px `_shade(tarp,-40)` bottom.** A hard 3-band ramp reads as a taut plane at any phase and gives the low corner an edge against the deck.
2. Runoff dashes are all identical (L 119, opaque, uniform 3px). Water accelerates — taper the lower dashes to 1px height and drop their alpha ~30% so the thread reads as falling rather than as a dashed line.
3. Answer to your open (b): **one sheet for all five stall kinds.** Variants here buy nothing at 1× and cost you the "the whole street agrees about the weather" read.

### 2 · `_cart_folded`

**KEEP.** Three genuinely different constructions — this is the model for how load states should be authored. EMPTY's bare slats as a *positive* read is the smartest single idea in the round. The `props_cast.draw_dressing` echo on crate/roll/basket/mat is the right instinct for identity fit. And you're correct that `draw_kiosk` has no wheel — the plan text is wrong, flag stands.

**FIX.**
1. **LOADED's load floats.** Rows y+22–23 contain only 6px of content — there's a visible gap band between the pole bundle/crate and the bed on the right side. Drop the bundle and crate 2px so they rest on the bed line.
2. **Wheel spin is unmotivated and will strobe.** `spin = t*1.8` rad/s on a 6-fold-symmetric 8px wheel repeats every 0.58s — at that size it's sparkle, not rotation. Worse, the cart is pinned to a deck that scrolls with it, so a spinning wheel is a lie the eye catches. Either (a) kill the spin entirely, or (b) give the LOADED cart a real ~15px/s drift relative to the deck and derive `spin = v/r`. I'd take (a) for round 2 and revisit if the vendor pose lands.
3. **The hub is your brightest cart pixel at L 154** — a 2×2 block, brighter than anything else on the cart, on the least important feature. Drop the hub to the wood tone and put your one bright value on the bed's top edge instead.
4. HALF: steepen the bed to ~28–30° (`bl=8, br=-6`), thicken the raised handle to 2px with a dark keyline so it's mass not line, and **attach the basket to the low bed end** so the envelope comes back to ~30px.
5. Answer to your open question: **keep it a pure prop.** The scene composes the vendor. But per the plan, the HALF state's vendor should be *lifting the raised handle* — that's what converts the hairline into a readable shape.

### 3 · `suoyi`

**KEEP.** The cape-only silhouette is the strongest new outline in the kit and the data backs your thesis completely. Row profile, cape-only vs a shipped tunic ped:

```
             y+8  y+6  y+4  y+2
suoyi cape:   13   13   13   13     <- a bell, all the way down
shipped ped:   8    4    4    3     <- tapers to a stalk
```

That flare-where-everyone-tapers is a genuinely unique class read. It works.

**FIX — and these are the round's most important notes.**

1. **The figure has no head.** Traced at night=1.0, the rows go: cone (97/131) → brim (97) → brim shadow (85) → neck notch (81) → cape (85/120/140). **Zero skin pixels.** It's a cone sitting on a bell — a mushroom, not a person. Drop `sh_y` 2px and pull the neck notch up so **2–3 rows of face show between brim and cape.** Non-negotiable for identity fit; every other member of the cast reads as a person at 18px.

2. **The cape interior is a 1px checkerboard and it will crawl.** The bottom cape rows measure literally `120 85 120 85 120 85 120 85 120` — a 55-luma amplitude, 1px-frequency vertical dither inside a 13px shape. At 160px/s scroll that is textbook temporal aliasing; it will shimmer and it actively fights the silhouette. Cut `straw_hi` out of the interior entirely. Use **two values, ≤22 luma apart**, and put your single bright value as a **2px shoulder catch-light across the cape top** — so the value structure is bright shoulder / mid body / dark fringe comb. Three bands, not vertical noise.

3. **Focal hierarchy is inverted.** Your brightest pixels (140) are in the middle of the cape; the hat tops out at 131. Bright value belongs on the hat's lit cone slope, which is where a viewer reads "person." Flip them.

4. **The walk cycle is dead.** Cape hem + 3px fringe reaches y+2 with the ground at y+0 — **2px of visible leg.** `_legs` swings inside 2 pixels, which is nothing. Cut `cape_h` from 10 to 8 and the fringe teeth from 1–3px to 1–2px, so the hem lands at ~y+6 and you get 5–6px of stride. You keep the entire flare read — it's the *waist* that has to not taper, not the shin.

5. **The pole carry is cannibalising the piece.** With the pole, max IoU vs the 50 shipped peds is 0.580 against the shipped carrying-pole vendor — and the existing widest cast members are already 24px pole carriers, so your 26px envelope buys 2px of novelty. The hanging bundles at ±10 with 6×5 ellipses **occupy the exact rows the cape flare lives in** and overwrite the left silhouette entirely (profile at y+5 is `[-13, 6]` — that's all bundle, no cape). Answer to your open (b): **make the crate the primary carry** (the cape reads clean at 13px wide down to y+2) and keep the pole as a ~30% secondary with the pole pulled back to ±8 and the bundles raised so they hang **above** the cape hem. Both hands still free; story intact; silhouette survives.

6. **Brim is narrower than the cape** (11px vs 13px). Push `brim_w` to `head_r * 3` so the douli overhangs the shoulders. A wide flat cone over a bell is a two-triangle outline shared with nothing in the game — that's the "unmistakable" the plan promised.

7. Answer to your open (a): **its own `arch` key,** not an accessory flag. The cape changes the torso, the hem line, the leg exposure and the carry constraint simultaneously — that's an archetype, not an overlay.

### 4 · `_sweeper`

**KEEP.** The besom is the right call and the twig fan is well-constructed. Twigs clamped to flatten along the deck rather than punch through it is a lovely piece of observation. Asymmetric push/recover easing is right. Head pinned to the paving is right.

**FIX.**
1. **The pile is the 2nd-brightest object on the sunrise street** and directly contradicts your own stated intent. Measured: pile crest **L 211**, pile body **L 201**, against a sunrise deck mean of 164 and a gold coin max of 229.5. You wrote "held a step under the paving's own value" — the code does the opposite. Bring the pile to **L 130–145** (below the deck mean) and delete the `_shade(pale, +10)` crest line entirely. Swept slush should be a dull mound.
2. **The pile is also eating the broom.** Fan (L 118/171) and pile (L 201/211) overlap in x, and the pile draws last and brighter — at 1× they merge into one blob and the besom read you're banking on is gone. Move the pile **3px further left**, clear of the twigs.
3. **Wrong body idiom.** `_draw_bench_person` is a *seated* construction; the sweeper renders as an 11px hunched blob with 1px legs, against a standing cast at PED_H 18. He's the first inhabitant of the morning on an empty street — a hero moment. Build him on `ped_cast._draw_one` with a `sweep` accessory so he stands at cast scale.
4. **The stroke is too small and too slow to read as work.** Broom head travels ~6px over 1.8s. Push to **9–10px of travel over ~1.3s**, and add a **1px vertical body bob on the push** — the weight shift is what makes sweeping legible at this size.
5. Answer to your open question: **give him a guaranteed slot,** like the storm holdouts. One per two blocks from 363s is thin enough that leaving him to a personality budget risks him not appearing in a run at all, and he's the beat that says "6 a.m."

### 5 · `winter` overlay set

**KEEP.** The two-construction scarf is genuinely correct — STREAM and DRAPE are different axes with different terminal details, which is the distinct-variants rule properly applied. And blitting `weather._snow_flake` from the live cache is excellent engineering: one blit, zero new art, alpha quantised in the same 16-step buckets as the falling snow.

**FIX.**
1. **The breath puffs are invisible.** Measured: peak α 109 on a 3px white disc, over a snow-phase far band of **211 luma.** Effective ΔL ≈ 9. White VFX on a bright background is nothing. Three changes: raise peak α to ~150; **spawn the puff at `hx`, over the dark hat/collar, not at `hx + head_r + 1` in open background** — it needs contrast for its first frames and can fade as it drifts clear; and give it a 1px cool-dark rim so it holds an edge on light *and* dark ground (standard casual-game keyline treatment for white VFX). Also, radius currently *grows* to 2 as alpha drops to 34 — peak the radius earlier and shrink into the fade.
2. **The coat is not a new silhouette.** Max IoU vs the 50 shipped peds: **DRAPE 0.839, STREAM 0.739.** The 14px torso is wider, but the hem line is in the same place as a shipped tunic, so the outline class doesn't change. Fix historically and structurally: **extend the coat hem 2–3px below `torso_bot`, over the thigh, with a squared-off bottom edge and a 1px lighter hem band.** That moves the figure's taper point *down*, which is a genuine class change against every shipped ped — and it's what a padded mianao actually does.
3. **No face here either** — the cap ellipse, fur line and collar squeeze the head down to 2 skin pixels. Same note as the suoyi: keep 2–3 rows of face.
4. The three stitch bands are 6 horizontal 1px lines in a ~10px torso — that's a stripe fill, not quilting; the base colour barely survives. **Drop to two bands** and let the base tone hold the middle.
5. Answers: **(a) latch the scarf at slot entry** — no exception. §5G is right and a morphing scarf would be the one thing on the street that visibly changes state mid-traversal. **(b) expose a single `cold` scalar from `biome`.** Deriving it locally in the promenade means the next system that needs it derives it again, differently.

### 6 · 8-rib umbrella — re-roll this piece

**KEEP.** Only the hem scallops. The silhouette *can* carry a rib count the interior can't — that instinct is sound and it's the part worth building on.

**FIX (rebuild).**
1. **6 ribs maximum, 4 visible rib lines.** 8 in a 17px canopy is physically unrenderable.
2. **Draw ribs before the panel fills,** or only on alternate boundaries. Right now they're painted last over everything.
3. **Base colour must be the dominant tone.** Target ≥40% of canopy pixels at base value with `panel_b` at −18 to −22. Right now base is 10%.
4. **Do not regress mean luma.** Round-2 canopy mean must be ≥ the shipped canopy's on all five colours (idx0 89.6 / idx1 89.2 / idx2 150.0 / idx3 107.9 / idx4 101.6). These are the rain chapter's colour accents; a darker umbrella is a worse umbrella.
5. Keep the 2px finial and the `crooked` kid variant — tilting off the pole axis rather than shrinking is the right kind of variation.

---

## Prioritised punch list for round 2

1. **Suoyi: give it a head.** 2–3 face rows between brim and cape. (Blocking for identity fit.)
2. **Suoyi: kill the 1px interior checkerboard.** Two values ≤22 luma apart + a 2px shoulder catch-light. (Blocking for 1× legibility.)
3. **Umbrella: rebuild at 6 ribs, ribs under panels, base colour dominant, mean luma ≥ shipped.**
4. **Suoyi: retint toward warm-dark `(58,46,38)` @0.45 → cape body L 85–95;** target mean|ΔL| ≥ 85 in a storm frame.
5. **Sweeper: pile down to L 130–145,** delete the +10 crest, move it 3px left of the twigs.
6. **Breath puffs: α→150, spawn over the dark collar, add a 1px cool rim.**
7. **Suoyi: `cape_h` 10→8, fringe 1–2px** → 5–6px of visible stride.
8. **Suoyi: crate becomes the primary carry;** pole to ±8 with bundles raised above the hem.
9. **Winter coat: hem 2–3px below `torso_bot`, squared edge, 1px hem band;** stitch bands 3→2.
10. **Cart LOADED: drop the load 2px onto the bed.** Cart wheel: kill the spin.
11. **Cart HALF: bed to 28–30°, 2px handle with keyline, basket attached to the low end.**
12. **Tarp: 4px sheet, hard 3-band value ramp;** taper the lower runoff dashes.
13. **Sweeper: rebuild on `ped_cast._draw_one` body;** stroke to 9–10px over ~1.3s with a 1px body bob.
14. **Suoyi: `brim_w = head_r * 3`.**

**Round-2 sheet must add one thing:** every 1× context strip currently shows the far lane only. Show each piece **in both lanes** — far deck at GROUND_Y 595 (backdrop L 173–228) *and* near deck at 638 (backdrop L 56–160). The 117-luma swing between them is the single biggest legibility variable on this street and this round didn't test it.

---

## Already ship-ready — don't touch

- The tarp's whole storytelling stack: pitch direction agreeing with the umbrella lean, rope turns, guy line, shadow cave, seated arms-folded vendor, steam + brazier still running.
- `_clamp_surface_luma` routing for the lit piece. Measured 145.8 under a 229.5 coin — the contract holds.
- Cart EMPTY state, unchanged.
- The STREAM / DRAPE two-construction scarf.
- The `_snow_flake` cache reuse for breath (values wrong, plumbing right).
- The besom construction and the deck-pinned broom head.

---

**Files reviewed:**
- `/home/user/skybit/docs/sidewalk_overhaul/art/weekend_kit/round_1.png`
- `/home/user/skybit/docs/sidewalk_overhaul/art/weekend_kit/round_1.md`
- `/home/user/skybit/tools/_weekend_kit_round1.py`
- `/home/user/skybit/docs/sidewalk_overhaul/DAY_PLAN_WEEKEND.md` (§8, §14)
- `/home/user/skybit/game/ped_cast.py`, `/home/user/skybit/game/foreground_promenade.py`, `/home/user/skybit/game/food_stalls.py`, `/home/user/skybit/game/props_cast.py`

**Method note:** per the project's hard rule I did not `Read` the PNG. All figures above come from re-rendering the round-1 drawers against real game frames (`biome.palette_for_phase` → `draw.get_sky_surface_biome` → `foreground.draw_foreground_floor` → `draw_ground_weather`) and measuring pixels directly — silhouette masks, row profiles, IoU against all 50 shipped pedestrian variants, per-pixel luma censuses, and piece-vs-background contrast. No files were edited.