# Store bazaar landing — BALLOON CARAVAN (round 1)

A fresh "festival in the sky" concept bridging the two floating / golden-hour
directions: a drifting **caravan of hot-air market balloons** climbs a
golden-hour → indigo twilight sky. Seven striped macaw-red/cream envelopes, each
carrying a hanging wicker market-stall basket, float in a loose staggered
zig-zag column. Gold pennant swags + drifting coins string the caravan together;
far cloud-isles below give depth. Pip flies the central lane as the
caravan-master vendor. Stars emerge at the indigo apex so a stall-tap reads as
climbing into the constellation jewel store. Balloons here are the cousin of the
cloud-platform bazaar's clouds.

## Files
- `render.py` — headless SS=4 renderer. Run:
  `cd /home/user/skybit && SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python docs/store_bazaar/balloon_caravan/render.py`
- `round_1.png` — 360×640 ship-scale selection sheet
- `round_1@2x.png` — 720×1280 inspection scale

## Pipeline (locked)
- SS=4 supersample: authored at logical 360×640, rendered on a 1440×2560 device
  canvas, then ONE `pygame.transform.smoothscale` down. Every gore, rope, basket
  weave, gem dome, pennant and glyph is drawn oversized so the downscale
  resolves crisp anti-aliased edges.
- Reuses the locked constellation primitives + palette anchors from
  `docs/store_redesign/constellation_hi/render_hi.py`: `m`, `font`, `vgrad`,
  `vgrad_stops`, `gold_a_fill`, `soft_glow`, `drop_shadow`, `gradient_text`,
  `plain_text`, `facet_gem`, `cabochon`, `cabochon_glass`, `coin_glyph`,
  `bevel_rim`, `top_sheen`, `gold_rule`, `title_wordmark`, GOLD / RARITY anchors
  — so the bazaar reads as the same store DNA (one gold, one bezel, one glass
  dome, the REAL in-game coin, the gold-on-red wordmark).
- Both build targets safe: pure pygame, no numpy, no desktop/browser-only API.

## 7 stalls → 7 balloons
Each stall maps a store group to its first item's **real preview thumbnail**
inside a glass cabochon: `sid = store_catalog.ids_of_group(group)[0]`, then
`parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)`.

| balloon | group | preview |
|---|---|---|
| COSTUMES | costume | base-parrot frame (group[0] = TOP HAT skin) |
| PARROTS | parrot | base-parrot frame (BLUE MACAW) |
| ANIMALS | animal | base-parrot frame (BEE) |
| SHOES | shoes | FLIP-FLOPS icon (letterboxed in the dome) |
| HATS | hats | PARTY HAT icon (contained, not clipped) |
| SHADES | shades | **fallback to `skin_shades_round`** — group[0] is `skin_shades_none` (bare base parrot), so a clear shades icon is used instead |
| PARCELS | parcels | ENVELOPE preview under a glowing red mystery `?` — the hero |

- Aspect-extreme items (flip-flops, party hat) are **contained / letterboxed**
  in the dome (scale-to-fit on the long axis), never clipped at the rim.
- PARCELS is the **glowing red mystery hero balloon**, anchored bottom-center /
  foreground (largest scale, hottest envelope red, hot mystery aura, `?` glyph).
- Every label sits on a scalloped striped-awning shop sign with a bold
  gold-keyline cap (dark keyline under a bright bevel = defined edge).
- Staggered zig-zag column: all 7 read at 360px, generous padding, no overlap;
  basket+awning tap targets clear ≥88px short-axis at ship scale.

## Craft notes
- **Balloon envelopes** are shaded by a **true per-pixel sphere normal**
  (`z = sqrt(1 − x² − y²)`) lit by one top-left key → real round volumetric
  Lambert shading, not a flat striped lozenge. Gore membership is angular so the
  red/cream seams curve with the surface. A gold rim-light hugs the upper-left
  limb; a dark contact keyline defines the lower-right; a soft elongated crown
  sheen (masked to the bulb) reads as a glossy sky reflection.
- **Wicker baskets**: warm gradient box + woven cross-hatch + rim hoops + dark
  keyline / bright bevel, 4 ropes gathering from the balloon mouth ring, a real
  AO/contact ellipse beneath each load.
- **Atmosphere**: 6-stop golden-hour-low → indigo-apex sky, an apex violet
  nebula bloom, a golden horizon glow welling from the foot, stars that emerge
  only in the indigo top band (fading out before the warm horizon), and three
  hazy warm-lit cloud-isles for depth.
- **Pip** (`parrot.get_parrot(1, 0.0)`) flies the central lane with a warm aura,
  a cast shadow and a ferried coin, kept clear of every label.
- **Header**: gold-on-red `title_wordmark("STORE")`, a recessed gold balance
  capsule with the REAL in-game `coin_glyph` + gradient-gold number, and a
  `TAP A STALL` wayfinding hint.

## Open questions for the art director
- The luminous apex band where the violet nebula meets the rising horizon glow
  frames the top two balloons but reads slightly washed behind them — keep it as
  a halo, or push the apex darker so the upper stalls sit on cleaner sky?
- Hero distinction currently comes from scale + aura + `?` rather than a wildly
  different envelope colour (all balloons share the macaw-red family on purpose).
  Is that enough, or should PARCELS swap to a gold/crimson envelope to separate
  it further from the SHADES/HATS pair flanking it?
- Pennant swags + drifting coins are intentionally restrained so they don't
  clutter the lanes — read as enough "festival connective tissue", or push them?
