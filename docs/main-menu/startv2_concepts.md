# START v2 — five premium button concepts (brainstorm, no renders)

## Measurements that shaped the set

Backdrop under START, measured on `VARIANT=B`:

| region | day | night |
|---|---|---|
| ground under START (x20-200, y545-625) | **L38.6**, H120, S0.12 | **L21.7**, H170, S0.26 |
| right sky (x240-352, y300-470) | L81.5, H196 | L19.4, H230 |

The corner is a **near-neutral dark green-teal at both poles** — not very
saturated, just dark. That refines the camouflage diagnosis.

**Why the shipped board only converts ~55% of its box to bright mass**
(orchestrator-verified): `_SCARLET_BOT (148,20,20)` is **L58.3** and
`_SCARLET_BOT_DIM (110,22,10)` is **L46.9** — both **below the L70 floor**. The
shipped gradient's whole lower half is disqualified mass by construction.
**Every concept below keeps every gradient stop above L77.**

Type widths, measured live via the real `_tracked_label` path (track=2):
START 30px->108, 34px->123, **38px->133**, 42px->148. PLAY 38px->106.

Targets to beat: **title 12,351 bright px**; **3x a plank = 12,420 px**.

---

## 1 `sunburst-medallion`
**Thesis.** START is a struck arcade token — the only circle on a screen of
planks, minted, laurelled, floating clear of everything.

**Stack.** `drop_shadow`(:255) blur m(6) a120 dy m(3) -> `smooth_aura`(:250)
R+16 `_GOLD_BRIGHT` peak 40 (replaces the max-alpha-11 halo) ->
**`achievement_icons._draw_rim`(:544)** hi(255,234,168)/mid(236,186,72)/
lo(150,102,20), 48 directional arcs + one hot specular arc -> `_draw_step`(:597)
fr=R*0.80 -> `_draw_face`(:577) fr=R*0.74 top(255,222,132) L222 bot(246,186,72)
L190 — **inverted from the shipped dark medallions because the corner is dark**
-> 16 tapered sunburst wedges @a60 -> `plain_text`+`_stamp_bold` m(1.0) track
m(2), START 34px (123 in a 152 face), **(96,40,10) dark type on a bright plate**
-> wing chevron via `_engraved`(:335) -> **`facet_gem`(:330)** r7 at 12 o'clock,
base `_SCARLET_TOP` — Pip's scarlet quoted as a *jewel*, not the plate ->
`_draw_laurel`(:606) -> `_draw_sparkle_ring`(:654) -> 1px (46,28,6) contact circle.

**Colour.** plate (255,222,132)->(246,186,72) L222->190 H44; frame L234/188/106;
type (96,40,10); gem (240,55,55). **Hue sep from ground 76** (failed board: 25.9).

**Dominance — lifted hero disc.** R=76 at (266,548), bbox x190-342 y472-624.
Clears SETTINGS x13-187 by 3px; touches y624 exactly. Tap 152x152.
**Bright mass ~16,900 = 1.37x title, 4.1x plank.**

**Risk.** 3px clearance from SETTINGS is tight; touches the y624 floor exactly.

---

## 2 `marquee-hoarding`
**Thesis.** A theatre marquee — ivory porcelain plate in a heavy gilt cartouche,
studded with real bulbs, spanning the full width so it becomes the composition's
missing floor.

**Stack.** `drop_shadow`(:255) m(12) blur m(6) a120 dy m(3) -> bulb halos UNDER
the plate: `smooth_aura`(:250) at 10 seats r11 (255,226,150) peak 34 ->
**`stall_fronts._cartouche_points`(:537)** stepped 12-point marquee silhouette
filled with `vgrad_stops`(:176) on `GOLD_A_STOPS`(:130) via BLEND_RGBA_MIN ->
**`make_rim_shine_frame(s=1.3)`(:88)** + `bevel_rim`(:478) per step -> inset
plate `vgrad_stops` (250,243,222)->(232,220,192) L243->222 -> `top_sheen`(:499)
h m(16) peak 58 -> `contact_shadow`(:516) m(4) a78 -> `_inner_keyline`(:388) ->
`plain_text`+`_stamp_bold` m(1.2) START **42px (148)** in **(30,64,120) cobalt
ink** — a cool dark ink on warm ivory, the maximum-contrast pairing on this
screen -> `_swash_underline`(:374) with its centre `_micro_gem`(:368) -> 10 bulbs
built like `draw_sign`'s six (:600-616), seat(120,84,30) glass(255,240,196) L238
-> 4x `_bolt_dot`(:270) at the corners -> 2px (56,36,10) bottom contact keyline.

**Colour.** plate ivory L243->222 H45 S0.11; frame GOLD_A L230->130; type cobalt
(30,64,120); bulbs L238. **Wins on luma — 6.3x the ground** rather than hue.

**Dominance — full-width hero bar.** x16-344 (328) x y538-618 (80). 1.9x a
plank's width, the only element touching both margins; gives the hanging chain
the floor it has never had. Tap 328x80.
**Bright mass ~20,800 = 1.68x title, 5.0x plank — the largest of the five.**

**Risk.** Heaviest build (10 auras + polygon-masked gradient). The cartouche is
the game's own shape from `stall_fronts`, so it must be clearly porcelain-and-
gilt rather than lacquer-and-wood-edge or it drifts back toward scenery.

---

## 3 `go-lozenge`  *(the deliberate control)*
**Thesis.** No ornament at all — one enormous slab of go-green candy enamel,
winning purely on saturated mass and gloss in the thumb corner.

The other four all answer "coloured plate in an ornate frame". **One option has
to test whether the screen's problem is ornament or mass.** The last round failed
by adding the *wrong* jewellery; this one structurally cannot.

**Stack.** Follow `_dark_chip_body`(:683): `drop_shadow` m(30) blur m(7) a130
dy m(4) -> `smooth_aura` r30 (150,255,120) peak 30 -> `vgrad_stops` radius m(30)
stops [(0,(176,236,104)),(0.45,(126,206,66)),(1,(74,166,52))] = **L214/179/138,
every stop far above the floor**, gamma 1.05 -> **`_gloss_corrected`(:669)** peak
110, explicitly NOT `gloss_sweep`(:618) -> `top_sheen` h m(20) peak 52 ->
`contact_shadow` m(4) a85 -> dark keyline (20,58,18) w m(2) then `bevel_rim`
deep(20,58,18) bright(232,255,214,240) L248 -> chrome collar: second `bevel_rim`
inset m(7) deep(96,110,96) bright(232,236,244) L236 — one cool ring in a warm
screen -> two-line lockup START 38px (133) over "TAP TO FLY" 13px, (14,48,14) ->
one big `facet_gem` r13 at top, base (255,202,104) gold-on-green.

**Colour.** lime L214/179/138 H94; chrome L236; type (14,48,14); gem (255,202,104).

**Honest flag from the designer.** H94 is only **26 from the day ground's H120 —
the smallest separation of the five.** It wins on chroma (S0.68 vs 0.12) and luma
(4.6x), not hue. But it is the one hue on the wheel that means *go*, and the menu
has zero of it.

**Dominance — enlarged bottom-right mass.** x192-348 (156) x y498-620 (122), a
near-square block, the largest unbroken area of one colour on screen, in the
thumb corner. Clears SETTINGS by 5px. Tap 156x122.
**Bright mass ~16,600 = 1.35x title, 4.0x plank.**

**Feasibility: highest of the five.** Six helper calls, one cached surface, no
polygon masking, no per-frame cost. Give it a 3px press-down — tactility is its
whole thesis.

---

## 4 `boarding-pass`
**Thesis.** A die-cut admission ticket — the chain finally lands on something,
and it is perforated printed paper, so it reads as something you *present*.

**Stack.** `drop_shadow` m(6) blur m(5) a115 dy m(3), then rotate the composite
-3 deg with one build-time `rotozoom` -> body `vgrad_stops` radius m(6)
[(0,(255,192,104)),(0.5,(252,158,66)),(1,(234,120,44))] L198/168/141 -> die-cut:
two semicircular punches at the mid-edges, **through a mask + BLEND_RGBA_MIN,
because `pygame.draw` WRITES alpha rather than compositing** -> perforation:
dashed 1px (180,72,20) + 1px (255,214,160) highlight, separating a 46px stub ->
stub field magenta (236,86,152)->(190,44,110) L118->77 (small area, contained) ->
cream print panel (250,238,214) L235 + `top_sheen` peak 44 — **this is where the
mass lives and it is near-white** -> `contact_shadow` m(3) a70 -> `bevel_rim`
deep(140,52,12) bright(255,232,190,235) -> START 38px (133) in (150,26,70) on the
cream panel; `_engraved` rule; "ADMIT ONE - SKY LINE" 11px -> "No 0001" 11px
rotated 90 in the stub -> `facet_gem` r6 as the validated star in the punch ->
the chain's `_tails` terminate in `_iron_ring` on the ticket's top edge.

**Colour.** tangerine L198->141 H34; print panel L235; stub magenta L118; type
(150,26,70). **Hue sep 86.** Scarlet survives as the *print* family, never the plate.

**Dominance — chain terminus + diagonal.** 250x76 at (182,580) rotated -3, bbox
x55-309 y536-624. Entirely below SETTINGS; lands on the y624 floor. **The only
non-orthogonal mass on screen** — a different kind of grab from size.
**Bright mass ~15,700 = 1.27x title, 3.8x plank.**

**Risk.** Rotated tap rect needs an inverse-rotation hit-test or an accepted
bbox. `_iron_ring` punches its centre with (0,0,0,0) which paints black on an
opaque surface — composite off a scratch SRCALPHA layer.

---

## 5 `signal-pylon`
**Thesis.** A tall lit pylon down the right edge — the only vertical on a screen
of horizontals — with the word running down it and a beacon gem on top.

**Stack.** `drop_shadow` m(14) blur m(6) a120 dy m(3) -> `smooth_aura` r26
(200,150,255) peak 38 -> casing `vgrad_stops` radius m(14) platinum
[(0,(232,236,244)),(0.4,(196,202,214)),(1,(126,132,148))] L236/202/132 — a cool
metal the warm screen has none of -> `make_rim_shine_frame(s=1.1)` recoloured to
platinum, or `bevel_rim` deep(70,74,88) bright(244,248,255,240) + `top_sheen` ->
three stepped collars via `bevel_rim` on short inset rects at y-fractions
0.12/0.5/0.88, so 270px of height reads as a stepped pylon not a bar -> light-box
core `vgrad_stops` amethyst [(0,(216,168,255)),(0.5,(178,116,238)),
(1,(128,70,190))] L185/138/**89** — every stop above the floor ->
`contact_shadow` m(4) a80 so the core sits recessed -> five stacked glyphs 30px,
40px leading, `plain_text`(:291) (255,248,232) L249 with `_stamp_bold` m(1.2) and
a (48,18,80) keyline via plain_text's keyline/kw args -> lantern head:
`cabochon`(:397) well + `cabochon_glass`(:424) dome r22 containing `facet_gem`
r14 base(216,168,255) — **`cabochon_glass` ships its own gold bezel, the one warm
note tying it to the menu** -> four `_bolt_dot` rivets -> foot:
**`hud._na_plate`(:1316)** cut-corner octagon 96x26 so the pylon visibly *stands*
-> 2px (48,52,64) contact keyline.

**Colour.** casing L236/202/132 H220 neutral; core L185/138/89 **H270**; type
cream L249. **Hue sep 150 — the largest of the five.**

**Dominance — tall portrait.** x244-344 (100) x y350-620 (270). Simultaneously
the tallest and the lowest object; the eye cannot stack it with the horizontal
boards because it is rotated 90 in aspect. Clears SETTINGS by 57px, the planks'
right edges by 48px. Head starts y350 not y332 so it never reads as *propping up*
Pip's cloud (base y~321) — that would be scenery again. Tap 100x270.
**Bright mass ~17,500 = 1.42x title, 4.2x plank.**

**Why violet is Skybit.** Violet appears in the game only as the **epic rarity**
colour (194,122,248) — already a Skybit signal for *the good thing*.

**Risk, stated by the designer.** A 270px column may crowd the right sky and
**fight the SKYBIT title's vertical axis.** That is the thing to test.

---

## Summary

| # | slug | palette | H sep | dominance | footprint | bright px | vs title |
|---|---|---|---|---|---|---|---|
| 1 | sunburst-medallion | brass + sun-gold enamel | 76 | lifted hero disc | R76 | 16,900 | 1.37x |
| 2 | marquee-hoarding | ivory porcelain + gilt + bulbs | luma 6.3x | full-width bar | 328x80 | **20,800** | **1.68x** |
| 3 | go-lozenge | lime enamel + chrome | 26 (chroma/luma) | bottom-right block | 156x122 | 16,600 | 1.35x |
| 4 | boarding-pass | tangerine + magenta + manila | 86 | chain terminus, diagonal | 250x76 @-3 | 15,700 | 1.27x |
| 5 | signal-pylon | amethyst + platinum | **150** | tall portrait | 100x270 | 17,500 | 1.42x |

All five clear the 12,351 title and the 12,420 (3x plank) bar. All keep every
gradient stop above L77.

## Designer's picks
1. **sunburst-medallion** — differentiates on *silhouette*, the one axis the last
   round never touched: five horizontal rectangles, then a circle. Unlocks
   `_draw_rim`, the best-struck metal in the codebase, never used on the menu.
2. **marquee-hoarding** — biggest, and fixes a *composition* problem not just a
   contrast one: the hanging chain currently just stops; a full-bleed bar gives
   the screen a floor. Most literal answer to the genre pattern.
3. **go-lozenge** — the necessary control. Don't skip it: if the ornate concepts
   are still drifting toward scenery, this is the one that structurally cannot.
