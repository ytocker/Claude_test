# SKY-GALLEON MARKET — store bazaar landing (round 1)

A fresh take in the **FLOATING SKY-BAZAAR** direction: the shop is a flying
merchant's **sky-galleon** — a wooden trading vessel cruising a golden-hour ->
indigo twilight sky, held aloft by a great gold-rimmed canvas envelope above and
trailing cloud-wisps below. The 7 category stalls are striped market booths
arrayed along the deck + rigging; Pip is the captain at the helm. Tapping a
stall is meant to dissolve up into the indigo apex where the stars emerge — the
existing constellation jewel store.

## Files
- `render.py` — headless SS=4 renderer (run below).
- `round_1.png` — 360×640 selection prototype.
- `round_1@2x.png` — 720×1280.

```
cd /home/user/skybit && SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  python docs/store_bazaar/sky_galleon/render.py
```

## Pipeline / reuse (locked requirements met)
- **SS=4 supersample**: authored at logical 360×640, rendered at 1440×2560, one
  `smoothscale` down. Every plank, rope, awning fold, seam + glyph is oversized
  so edges resolve crisp with no per-shape AA.
- Imports the constellation store's locked kit from
  `docs/store_redesign/constellation_hi/render_hi.py`: `m, font, vgrad,
  vgrad_stops, gold_a_fill, soft_glow, drop_shadow, contact_shadow,
  gradient_text, plain_text, coin_glyph, bevel_rim, top_sheen, gold_rule,
  title_wordmark, gloss_sweep, cabochon, cabochon_glass` + the GOLD / GOLD_A
  ramp anchors — so the landing and the jewel store are visibly ONE product.
- Both build targets safe: pure pygame, no numpy, no desktop/browser-only API.

## The 7 stalls (real previews, locked)
Each booth = striped macaw-red/cream awning hung from a mast + a **glass
cabochon dome** showing the category's REAL preview thumbnail via
`store_catalog.ids_of_group(group)[0]` ->
`parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)`:

| Booth | group | preview id |
|-------|-------|-----------|
| COSTUMES | costume | skin_tophat |
| PARROTS | parrot | skin_bluegold |
| ANIMALS | animal | skin_bee |
| SHOES | shoes | skin_shoe_flipflops (icon) |
| HATS | hats | skin_hat_partyhat (icon) |
| SHADES | shades | skin_shades_black (icon) |
| PARCELS | parcels | parcel_envelope (icon) — **glowing red mystery hero** |

- **SHADES fallback**: the group head `skin_shades_none` is the bare-eyed look
  with no icon, so `_preview_id` steps to the first id that owns a real shades
  icon (`skin_shades_black`) — never a bare base parrot.
- **Aspect-extreme containment**: `_preview_surface` *contains* (fits the longer
  axis, letterboxed on the short axis) so flip-flops / party hat sit whole in
  the dome, never clipped.
- **PARCELS hero**: larger booth, red mystery glow ring on the foredeck centre.
- **Tap targets**: every booth backboard is ≥88px on its short axis with
  generous horizontal padding; nothing overlaps at 360px (verified at 1x + 2x).
- Labels are bold gold-keyline (`gradient_text` Ramp-A gold + dark keyline) on
  small wooden nameboards = the canonical "defined edge".

## Pip + header
- **Captain**: `parrot.get_parrot(1, 0.0)` scaled onto a stern poop-deck shelf,
  the ship's wheel (helm) to his right, a restrained warm key-light, and a coin
  he presents — deliberately NO glass dome so he never reads as another booth.
- **Header**: gold-on-red `title_wordmark("STORE")`, a recessed gold balance
  capsule with the REAL in-game `coin_glyph` + gradient-gold number, and a
  "TAP A STALL" hint.

## Ship / atmosphere (all procedural)
- Envelope (balloon), hull, three masts, rigging + suspension ropes, deck
  backboards, portholes, gunwale rail, bowsprit + pennants — all from gradient +
  polygon + line + glow. One light top-left; gold rim-lights; real AO / contact
  shadows; cloud-wisps trailing below the keel so the ship floats.
- Sky: golden-hour warm low (low sun + light shafts + warm cloud-isles)
  grading up through rose/violet to an indigo apex with a gold-flecked nebula
  bloom and **emerging stars** (density biased high, fading toward the bright
  horizon) — the bridge into the constellation jewel store.

## Known soft spots for the next round
- The canvas envelope reads slightly flat/wide; the panel seams are subtle.
  Could narrow it, deepen the panel shading, and strengthen the stitched seams.
- PARROTS' centre awning rod kisses the balloon's lower rim (reads as hung from
  it, but could be tuned).
- Booth backboards are uniform; the hero could earn more distinct framing.
