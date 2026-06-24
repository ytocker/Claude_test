# LAGOON STILT-MARKET — store bazaar landing (round 2)

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
- `round_2.png` — 360×640 ship-scale target (current)
- `round_2@2x.png` — 720×1280 (review zoom)
- `round_1.png` / `round_1@2x.png` — prior round, kept for comparison

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
