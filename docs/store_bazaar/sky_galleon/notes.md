# SKY-GALLEON MARKET — store bazaar landing

A fresh take in the **FLOATING SKY-BAZAAR** direction: the shop is a flying
merchant's **sky-galleon** — a wooden trading vessel cruising a golden-hour ->
indigo twilight sky, held aloft by a gored gold-rimmed canvas envelope above and
trailing cloud-wisps below. The 7 category stalls are striped market booths
arrayed along the deck + rigging; Pip is the captain at the helm. Tapping a
stall is meant to dissolve up into the indigo apex where the stars emerge — the
existing constellation jewel store.

## Files
- `render.py` — headless SS=4 renderer (run below).
- `round_2.png` / `round_2@2x.png` — current revision (360×640 / 720×1280).
- `round_1.png` / `round_1@2x.png` — first pass, kept for diff.

```
cd /home/user/skybit && SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  python docs/store_bazaar/sky_galleon/render.py
```

## Round 2 — addressed the art-director ITERATE punch list (one pass)

1. **Rebuilt the envelope (biggest premium gain).**
   - Narrowed ~11% (half-width 140→124) so it reads as a dirigible, not a wide
     tan blob.
   - **Real gored panels**: per-pixel the body maps x to a row-normalised gore
     position; each gore gets a warm crown at centre fading to a darker valley
     at its two seams, with crisp gold stitch lines between gores — cross-section
     curvature now reads. (The round-1 horizontal-band artefact is gone.)
   - **Killed the white specular sticker**: replaced with a restrained upper-left
     curve-following sheen arc + a slim warm SUNSET bounce hugging the
     lower-right rim (no central white window).
   - **Intentional livery**: two slim macaw-red accent hoops encircling the nose
     + tail (curvature-following, not bold umbrella stripes) and a gold coin
     **cartouche medallion** on the flank.

2. **Preview legibility.** Previews now size so their LONGER axis fills ~86% of
   the dome (was a timid big-letterbox contain). Genuinely-flat goods are angled
   in-plane (SHOES ~-24°, SHADES ~-20°) so they claim 2D area instead of reading
   as a 1px smear / tiny rectangle. SHOES + SHADES are identifiable at 1×.

3. **Re-floored the cabochons** to the jewel store's near-black navy
   (`CABO_LO/CABO_HI` imported from `constellation_hi/render_hi.py`) so the
   sunset no longer bleeds through behind previews, **plus** a soft radial
   value-lift at each dome's centre so dark previews don't vanish.

4. **Differentiated PARCELS.** No longer a 7th striped twin: a wax-sealed
   **treasure crate** (iron-banded corners, gold studs, red wax seal + `?` —
   surprise-box `_draw_qmark` reused so it reads as loot, not an inbox envelope)
   on a **rope-lashed brass-cornered cargo dais**, with a DEFINED red glow ring
   over a dark vignette so the hero punches out of the sunset.

5. **Decluttered the foredeck.** Grid kept tight in two clean rows; PARCELS hero
   lifted so its nameboard clears the gunwale; Pip raised so his whole
   silhouette clears the gunwale (no longer half-cut); the helm commits to a
   visible brass ship's-wheel with spokes + studs.

6. **Polish.** Hull plank seams deepened one value step (darker valley under a
   brighter lip); faint gold star-glints added on the upper rigging band to
   foreshadow the star-store; the PARROTS centre awning rod no longer kisses the
   balloon rim.

**Kept as-is (already premium):** the golden-hour→indigo sky grade, the hull +
gunwale + brass portholes, the STORE wordmark + balance capsule, and
captain-Pip-with-no-dome.

## Pipeline / reuse (locked requirements met)
- **SS=4 supersample**: authored at logical 360×640, rendered at 1440×2560, one
  `smoothscale` down.
- Imports the constellation store's locked kit + palette anchors from
  `docs/store_redesign/constellation_hi/render_hi.py` (incl. `CABO_LO/CABO_HI`)
  and the surprise-box `_draw_qmark` — so the landing and the jewel store are
  visibly ONE product.
- Both build targets safe: pure pygame, no numpy, no desktop/browser-only API.

## The 7 stalls (real previews, locked)
Each booth = striped macaw-red/cream awning + a navy glass cabochon dome showing
the category's REAL preview thumbnail via `store_catalog.ids_of_group(group)[0]`
-> `parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)`:

| Booth | group | preview id |
|-------|-------|-----------|
| COSTUMES | costume | skin_tophat |
| PARROTS | parrot | skin_bluegold |
| ANIMALS | animal | skin_bee |
| SHOES | shoes | skin_shoe_flipflops (icon, angled) |
| HATS | hats | skin_hat_partyhat (icon) |
| SHADES | shades | skin_shades_black (icon, angled) |
| PARCELS | parcels | wax-sealed treasure crate (mystery hero) |

- **SHADES fallback**: the group head `skin_shades_none` is the bare-eyed look
  with no icon, so `_preview_id` steps to the first id that owns a real shades
  icon (`skin_shades_black`) — never a bare base parrot.
- **Tap targets**: every booth backboard / the hero dais is ≥88px on its short
  axis with generous padding; nothing overlaps at 360px (verified 1× + 2×).

## Pip + header (kept)
- **Captain**: `parrot.get_parrot(1, 0.0)` scaled onto a stern poop-deck shelf,
  a brass ship's-wheel to his right, a restrained warm key-light, and a coin he
  presents — no glass dome, so he never reads as another booth.
- **Header**: gold-on-red `title_wordmark("STORE")`, a recessed gold balance
  capsule with the REAL in-game `coin_glyph` + gradient-gold number, and a
  "TAP A STALL" hint.

## Atmosphere (all procedural, kept)
Golden-hour warm low (low sun + light shafts + warm cloud-isles) grading up
through rose/violet to an indigo apex with a gold-flecked nebula bloom and
emerging stars — the bridge into the constellation jewel store.

## Small residual to watch next round
- "TAP A STALL" hint sits on the balloon's upper canvas (legible via its dark
  keyline, but could earn a hair more clearance).
