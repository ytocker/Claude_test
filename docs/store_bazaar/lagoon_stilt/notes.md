# LAGOON STILT-MARKET — store bazaar landing (round 4)

## Round 4 — final polish pass (4 targeted fixes, round_3 kept as the "before")
The round_3 lagoon was loved; this pass lands four specific craft fixes and
saves to NEW files (`round_4.png` / `round_4@2x.png`) — round_3 is untouched.

1. **Pip is now an AIRBORNE distant flyer, not a jetty merchant.** `draw_pip`
   was decoupled from the hut layer entirely — its signature is now
   `draw_pip(surf, px, py)` (sky coords, not `deck_y`) and it's called ONCE from
   `render_device` in the open sky gutter (`0.60, 0.255` of the canvas) between
   the sun and the right palm, below the TAP-A-STALL chip and above the back-row
   roofs. He's the wings-up flap frame (`get_parrot(0, 8.0)`) at a slight upward
   bank, scaled DOWN to `m(30)` so he reads as a far macaw mid-flap. Dropped: the
   on-deck contact shadow, the dark separation halo, and the jetty coin + sparkle
   ticks (they read odd mid-air). The empty front jetty is rebalanced by making
   PARCELS a normal front stall (see #4).
2. **Premium stilt water-contact ripples.** `draw_stilts` previously drew two
   additive `GLITTER (255,232,178)` ellipses (BLEND_ADD, α120/60) — a bright gold
   glitter fleck. Rebuilt as FOUR graduated concentric rings on a cool dusk-water
   tone (`(150,178,196)→(96,130,158)` cooling outward), NORMAL blend, smooth
   alpha falloff (α30→96 inner-brighter), each foreshortened to a flat surface
   ellipse, plus a sunlit meniscus crescent arc on the lit (top-left) edge. Each
   post now reads as genuinely displacing the water surface.
3. **Killed the remaining white aura.** Added the proven `capped_glow` helper
   (vendored from `sky_bazaar/render.py`) — composites rings with
   `BLEND_RGBA_MAX` so the strongest ring wins and a glow caps at one opaque pass
   of its own colour, never summing to white. Pip's two additive auras
   (`SUN_AURA` 10× α56 + `SUN_CORE` 6× α78) are GONE — he gets a single faint
   capped warm rim (α34). The dome glow (was `soft_glow` GOLD α46/34) and the
   balance-coin glow are now `capped_glow`. Pixel sampling confirms zero
   white-bloom blobs around Pip or the domes; the only near-white left is the
   approved sun-glitter column specular on water (count is LOWER than round_3
   since the gold stilt flecks are gone).
4. **PARCELS de-mystified — a normal stall showing its real item.** All hero
   special-casing stripped: `_place_thumb` no longer calls `_draw_mystery_crate`
   (left unused) and routes PARCELS through the SAME `_group_thumb("parcels")` →
   `parrot.get_skin_icon(...)` path as the other six — its first item
   `parcel_envelope` (kraft padded mailer + twine cross + wax seal) now sits in
   the dome with the same contain factor, rim-light and contrast-punch. Hero
   tells normalized in `draw_hut`/`_hut_label`: dropped the gold underglow, dome
   glow back to standard α34, standard glass tint, standard dome size/position,
   and the STANDARD dark-timber name board (no deep-red gold-text board). The
   `hero` flag now only marks it the front/closest stall, treated as a peer.

Kept per the brief: NO red-from-beneath, all 7 stalls read, warm-gold disc sun +
star carve-out, gold-on-red STORE header + balance capsule, palm-framed depth,
cool natural water reflections, and the constellation sky bridge.

---

# LAGOON STILT-MARKET — store bazaar landing (round 3)

A tropical **over-water stilt-village market at golden hour** — the most overtly
scarlet-macaw-island take on the GOLDEN-HOUR DOCK MARKET direction. Seven
thatched-roof market huts on wooden stilts rise out of a glittering gold lagoon,
linked by little boardwalk planks, with palms + distant hazy islets, and Pip
selling from the central jetty. The sky eases UP into the indigo+gold jewel-store
nebula so tapping a stall dissolves cohesively into the existing CONSTELLATION
stall screen.

## Files
- `render.py` — headless generator (run from repo root):
  `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python docs/store_bazaar/lagoon_stilt/render.py`
- `round_3.png` — 360×640 ship-scale target (current)
- `round_3@2x.png` — 720×1280 (review zoom)
- `round_2.png` / `round_2@2x.png` — the "before" for this pass, kept for comparison
- `round_1.png` / `round_1@2x.png` — earliest round, kept for comparison

## Round 3 — "perfect it" craft pass (kill the red, make all 7 stalls read)
The concept was liked but read as "a basic idea". Two concrete complaints drove
this pass, both fixed:

1. **KILLED the red-from-beneath** (core complaint — the "auras like from the
   sun" that "looked bad"). Two sources removed/retuned:
   - The hero PARCELS underglow was an additive RED `MYST_GLOW (236,64,64)` α46
     soft-glow → now a restrained WARM-GOLD seat (`MYST_GOLD (255,206,110)`
     α34), the store's coin hue. No red bleeds onto the water.
   - `hut_reflection()` cast additive AWN_RED / MYST_GLOW columns onto the water
     under every hut → completely rewritten as a NATURAL reflection: cool,
     desaturated tints (`REFL_HUT (52,48,62)` / `REFL_THATCH (78,60,54)`),
     **NORMAL blend** (not additive), low alpha (~46 peak), depth fade, ripple
     gaps + a side-to-side wobble + edge taper so it reads as wet timber on dusk
     water, never a coloured sun-aura.
   - The hero dome glow + glass tint went from mystery-red to GOLD, and the
     PARCELS name board is now **gold-on-deep-red** (echoing the STORE header)
     instead of cream-on-red.
2. **RE-BRANDED the mystery hero by SHAPE + GOLD** (not a red glow): the dome now
   holds a `_draw_mystery_crate` — a dark crate bound by warm GOLD strap bands +
   rivets with a bold gold `?` centred over it. Mystery now reads by shape +
   gold + value contrast (red/green-blind safe), with zero red.
3. **ALL 7 STALLS READ CONFIDENTLY**: every hut enlarged + separated — back row
   scale `0.68→0.80`, mid row `0.84/0.76→0.92/0.86`, outer huts pulled to the
   canvas edges, centre huts lifted so no roof occludes the hut behind it. Each
   category dome (COSTUMES, PARROTS, ANIMALS, SHOES, HATS, SHADES, PARCELS) is
   clearly identifiable at 360px.
4. **Shrank the sun so the village owns the canvas**: disc `m(40)→m(46)` body but
   the whole sun moved upper-left (`0.30,0.355 → 0.26,0.300`) to FRAME rather
   than crowd the back row.
5. **PERFECTED the sun** (the round-2 "white moon-blob"): the additive halo that
   stacked ON TOP of the disc and desaturated it to a white fried-egg ring is
   gone. The sun is now a **self-contained opaque warm-gold radial disc**
   (gold core → amber rim, NORMAL blend) over a **NORMAL-blend translucent amber
   halo** (additive glows whiten as their layers compound near the edge — proven
   by pixel sampling — so the halo is composited by alpha instead). The star
   field is also carved out around the sun so no sparkle speckles the disc.

Kept intact: the concept (thatched stilt-huts over a golden lagoon, reflections,
palms framing, Pip the jetty merchant), the gold-on-red STORE header + balance
capsule + real coin glyph, the golden-hour→indigo CONSTELLATION sky bridge, the
tasteful gold sun-glitter column, the red/cream awnings + carved name boards.

## Round 3 — final ITERATE pass (AD confirmed both big wins; closed 5 beats)
The art-director's review of round_3 confirmed the two big wins are GENUINELY
fixed and must be KEPT — (A) the red-from-beneath is gone (natural cool
reflections, pixel-sample verified) and (B) all 7 stalls read — and returned
VERDICT: ITERATE on five fixable beats. All five landed in this same round_3
(overwritten in place):

1. **SHADES preview legibility** (top priority — the one stall that still
   near-failed): dark sunglasses on a dark parrot collapsed against the near-
   black dome well. FIX: the SHADES dome interior now gets a LIGHTER cool-slate
   backing (`cabochon((96,104,134),(44,50,78))` instead of the deep
   `CABO_LO/HI`), plus an extra GOLD key rim-light (`_rim_light((255,224,150),
   alpha=210)`) on the eyewear. The lenses now read as a positive shape like the
   other previews.
2. **Guttered the hero crate off its flankers**: the lifted PARCELS hero
   overlapped PARROTS (left) + SHOES (right), reading as one central mass. FIX:
   PARROTS `0.180→0.142` and SHOES `0.820→0.858` pulled to the canvas edges, and
   the hero scale shaved `1.00→0.96`, so a clear dark-water gutter separates the
   three central stalls. (COSTUMES/HATS nudged out `0.165/0.835→0.155/0.845` to
   match.)
3. **Separated Pip from the crate**: Pip pushed further front-left + DOWN off the
   deck lip (`cx-m(36)→cx-m(42)`, `+m(7)→+m(13)`), given a thin dark separation
   halo behind his silhouette + a darker/wider contact shadow (α130→175), so the
   read order is crate-first, merchant-second in a clean front-to-back stack.
4. **(polish) Back-row board air**: non-hero name boards lifted `deck_y-m(20)→
   deck_y-m(16)` so they clear the awning/roof-eave shadow above them.
5. **(polish) TAP A STALL rules**: the flanking gold rules were near-invisible
   hairlines → committed to bright `GOLD_PALE` at `peak 160→235`, `thick
   m(1)→m(1.6)` so they read as intentional rules, not render noise.

Preserved per the AD note: the gold-banded `?` crate, the warm-gold disc sun +
star carve-out, the gold-on-red STORE header echo, the palm-framed depth, and
the constellation sky bridge.

## Round 2 — art-director ITERATE pass (one revision)
Verdict was ITERATE: strong concept + real craft, undermined mainly by the
oversized sun. The prioritized punch list, all addressed in this pass:

1. **Tamed the sun** (highest impact): shrunk ~38% (core glow `m(64)→m(40)`,
   halo `m(150)→m(96)`), dropped LOWER behind the rooflines (`0.30→0.355`),
   and killed the blown white core — now a warm saturated gold disc
   (`SUN_CORE (255,210,130)`, centre pip `(255,218,150)`) with a restrained
   halo, so the back row sits against SKY, not glare.
2. **Back-row scrim**: a soft cool dusk band (`(40,38,78)`, sin-feathered
   across `0.36–0.50` of the sky) behind COSTUMES/ANIMALS/HATS so they read
   against atmosphere, not the sun's glow.
3. **Enlarged previews ~22%**: dome radius floored
   (`max(m(24), m(28)*scale)`, hero `m(29)*scale`) so the BACK ROW carries an
   identifiable preview, and the contain box bumped (`1.5→1.84`, letterboxed
   `1.32→1.62`). Glass dome sheen preserved.
4. **Cleared the hero label lane**: hero hut lifted ~14px (`0.870→0.848`),
   Pip pushed front-left + down (`cx-m(24)→cx-m(36)`, `+m(2)→+m(7)`) with the
   coin moved to his upper-LEFT, and the PARCELS name board DEFERRED to draw
   frontmost on the deck front (`deck_y+m(8)`) so nothing crosses it.
5. **Row separation**: back row dropped (`~0.60→~0.62`) and mid row pushed
   down (`~0.79→~0.81`) so no roof ridge clips the eaves of the hut behind it.
6. **Promoted TAP A STALL**: now a faint recessed gold-ruled CHIP (low-alpha
   pill + hairline gold rim + flanking gold rules + gradient-gold type) with
   ~8px more air under the capsule, so it reads as the CTA, not a caption.
7. **Accessibility**: the hero `?` is a bold near-white glyph
   (`(255,250,244)`) with a thick very-dark contour (`(28,6,8)`, `m(3.4)`) so
   the mystery hut reads by SHAPE + VALUE, not red hue alone (red/green-blind
   safe).

Kept intact: the gold-on-red STORE wordmark + balance capsule + real coin
glyph, the golden-hour→indigo gradient + dusk stars + glitter column, the red
awnings + carved name boards, and the staggered village depth.

## Pipeline
SS=4 supersample: authored at logical 360×640, rendered on a 1440×2560 device
surface, ONE `pygame.transform.smoothscale` down — the same lever as
`docs/store_redesign/constellation_hi/render_hi.py`, whose primitives this reuses
verbatim (`m`, `font`, `vgrad`/`vgrad_stops`, `gold_a_fill`, `soft_glow`,
`drop_shadow`, `gradient_text`/`plain_text`, `cabochon`/`cabochon_glass`,
`coin_glyph`, `bevel_rim`, `top_sheen`, `gold_rule`, `title_wordmark`,
`_punch_contrast`/`_rim_light`, `downscale`, plus the GOLD anchors) so the
bazaar shares ONE visual DNA with the stall screen it opens into.

## The 7 stalls → 7 stilt-huts
Tidy staggered arrangement so all seven read at 360px, drawn back-to-front for
real depth:
- **back row** (smaller, deeper): COSTUMES · ANIMALS · HATS
- **mid row**: PARROTS · SHADES (tucked centre) · SHOES
- **hero jetty** (largest, frontmost, glowing red mystery): PARCELS

Each hut = thatched roof (lit ridge → shaded ragged-straw eaves, top-left light)
+ a striped macaw-red/cream scalloped awning + a shaded stall interior carrying a
glass `cabochon` dome with the category's **REAL** in-game preview:
`sid = store_catalog.ids_of_group(group)[0]`, then
`get_skin_icon(sid) or get_skin_frame(sid, 1, 0.0)`.

- **SHADES** falls back to the first shades id that owns a real eyewear icon
  (the catalog's first shades id is NO SHADES = a bare-eyed parrot, which the
  brief forbids) so the dome shows a clear shades graphic, never a bare base
  parrot.
- **Aspect-extreme** previews (flip-flops, party hat) are detected by aspect
  ratio and **letterboxed** (tighter contain factor) so the long axis sits fully
  inside the glass instead of clipping.
- **PARCELS** is the glowing-red mystery hero hut on the central jetty; its dome
  shows the store's `?` mystery mark in the MYSTERY red, not a literal thumbnail.
- Bold category labels are gradient-gold on a carved-timber name board with a
  dark keyline (the canonical defined edge); the hero's board is deep mystery
  red.

## Pip + chrome
- **Pip**: `parrot.get_parrot(1, 0.0)` scaled to the jetty, front-left of the
  hero deck (clear of the PARCELS dome + label), with a warm sun aura, a contact
  shadow on the deck, and a small foreshortened **spinning coin**
  (`entities._get_coin_face` squashed to an ellipse) + sparkle ticks beside him.
- **Header**: gold-on-red `title_wordmark("STORE")`, the recessed gold balance
  capsule with the REAL `coin_glyph` + gradient-gold number, and a gold-ruled
  **TAP A STALL** hint on its own lane under the capsule.

## Materials / atmosphere (all procedural)
- **Sky**: golden-hour multi-stop — hot `(255,196,112)` low band → rose haze →
  violet → indigo `(10,11,40)` apex (the CONSTELLATION anchor), a raked low sun
  with halo, and **emerging dusk stars** confined to the upper indigo band so
  they read as the first stars of dusk.
- **Lagoon**: hot horizon → cool deep trough, a tapering **gold sun-glitter
  column** under the sun, broad wavelet texture, and soft **rippled hut
  reflections** + waterline **contact ripples** at every stilt.
- **Stilts / planks / decks**: lit-top-left timber gradients with seams, AO, and
  submerged reflections; boardwalk planks are foreshortened quads with contact
  shadows linking the village.
- **Palms** framing both edges: curved tapering trunks + drooping bézier fronds,
  rim-lit on the sun side; **hazy violet islets** on the waterline for depth.

Both build targets safe: pure pygame, no numpy, no desktop/browser-only API.

## Known round-1 soft spots (for the art-director pass)
- Hero **PARCELS** name board is slightly crowded by Pip at the very bottom edge;
  could lift the hero hut a touch more or shift the board.
- Back-row and mid-row roofs overlap a little; intentional depth layering but
  could earn more vertical separation.
- TAP A STALL hint sits close to the capsule; consider a touch more gap or a
  brighter hint chip.
