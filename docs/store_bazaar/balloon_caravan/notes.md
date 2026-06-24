# Store bazaar landing — BALLOON CARAVAN (round 2)

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
- `round_2.png` / `round_2@2x.png` — current ship-scale + inspection sheets
- `round_1.png` / `round_1@2x.png` — first exploration (kept for the evolution)

## Round 2 — art-director punch list (ITERATE, keeper concept)
The AD signed off the concept and returned a prioritized one-pass fix list; all
six items are folded in:

1. **Deepened the sky (highest impact).** Re-anchored `SKY_STOPS` so the top
   ~58% reads as a genuine near-black indigo/violet jewel-store vault and the
   warm golden-hour glow is reserved for the bottom ~40% (cloud-isles + hero).
   Stars now populate that whole dark band in warmer gold tints and fade out
   before the horizon. This is the daytime-fair-foot → night-vault-apex climb,
   and it lifted contrast on the top two balloons (the round-1 apex wash is gone).
2. **Preview legibility (was failing at 360px).** (a) Dome contents enlarged
   ~28% + a lighter warm-neutral inner backing disc behind each so silhouettes
   pop off the near-black glass; (b) COSTUMES/PARROTS/ANIMALS now crop to the
   **head/shoulders** (the bird faces right → right ~58% × top ~82% of the bbox)
   so a big legible face fills the dome instead of a tiny full body; (c) the
   value-punch on the thumbnail was raised. Verified distinguishable on the
   360px sheet (not just @2x): parrot-head / macaw-head / bee-head /
   flip-flop / party-hat / round-shades / parcel.
3. **Distinguished the hero.** PARCELS' envelope is re-skinned to a distinct
   **crimson-to-gold** gore (deep crimson body + gold stripe gores, not
   red/cream) so it separates from its macaw-red SHADES/HATS neighbours; the red
   `?` glyph + hot mystery aura stay.
4. **Strengthened the caravan.** Heavier **twin-cord gold** pennant swags now
   bind each vertically-adjacent stall pair (0→2, 1→3, 2→4, 3→5, 4→6, 5→6),
   routed down the OUTER columns so they never cross Pip's central lane; each
   swag carries 2–3 drifting coins riding its nodes.
5. **Top-balloon halo.** A gold constellation (thread + node-stars, the
   constellation-store treatment) sits behind COSTUMES/PARROTS so the
   climb-into-the-jewel-store read lands at the dark apex.
6. **Polish.** +4px gap under the wordmark before the balance capsule; one crisp
   warm highlight rim per cloud-isle lobe (no more muddy horizon haze); Pip's
   aura softened + feathered (it read as a hard white puck once the sky went
   dark).

Untouched per the AD: the per-pixel volumetric balloon shading + gore curvature
+ gold rim / dark contact keyline, the scalloped awning labels, the header
lockup, Pip's placement / coin / shadow, and the non-overlapping staggered
zig-zag.

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
- PARCELS is the **crimson-and-gold mystery hero balloon**, anchored
  bottom-center / foreground (largest scale, hot mystery aura, red `?` glyph).
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
- **Atmosphere**: 7-stop near-black-indigo-apex → golden-hour-foot sky, a
  restrained apex violet nebula bloom, a golden horizon glow welling from the
  bottom, gold stars emerging across the dark top band (fading out before the
  warm horizon), a gold constellation behind the top stalls, and three crisp
  warm-lit cloud-isles for depth.
- **Pip** (`parrot.get_parrot(1, 0.0)`) flies the central lane with a soft warm
  aura, a cast shadow and a ferried coin, kept clear of every label and swag.
- **Header**: gold-on-red `title_wordmark("STORE")`, a recessed gold balance
  capsule with the REAL in-game `coin_glyph` + gradient-gold number, and a
  `TAP A STALL` wayfinding hint (with the round-2 +4px wordmark gap).

## Remaining optional polish (designer's note, not blocking)
- The apex violet nebula is dimmed but still a soft band behind the top two
  balloons; it now reads as cloud rather than the round-1 portal wash. Could be
  pushed a hair darker still if the AD wants the upper stalls on cleaner vault.
- Pip's aura is softened to a feathered warm glow; if it should disappear
  entirely into the dark sky it can drop another ~30% alpha.
