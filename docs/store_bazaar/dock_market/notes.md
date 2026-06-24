# Store bazaar landing — GOLDEN-HOUR DOCK MARKET (round 3 — overwrites round_2.png)

A tropical harbor market at golden hour. Seven category stalls line a wooden
boardwalk in **two tiers** — a larger front row and a smaller back jetty — split
by a strip of **sun-glittering gold water**. Palms frame the left/right edges,
distant boat silhouettes add depth, and **Pip** the scarlet macaw sells from a
dockside cart. **PARCELS** is the **gold-banded crimson mystery CHEST** seated on
the dock lower-right (on a spotlit crimson/gold dais). A coiled mooring rope
anchors the bottom-left. The low golden-hour sun rakes light in from the
top-left; the sky eases UP from the warm horizon to the indigo+gold jewel-store
nebula so entering a stall dissolves cohesively into the constellation store.

> Round 3 is the art-director ITERATE pass on round 2. Per the loop convention
> the final sheet keeps the `round_2.png` / `round_2@2x.png` filenames
> (overwritten in place); this notes file records the round-2 → round-3 deltas.

## Files
- `render.py` — headless SS=4 renderer. Run:
  `cd /home/user/skybit && SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python docs/store_bazaar/dock_market/render.py`
- `round_2.png` — 360×640 ship-scale selection sheet
- `round_2@2x.png` — 720×1280 inspection scale
- `round_1.png` / `round_1@2x.png` — prior round, kept for comparison

## Pipeline (locked)
- SS=4 supersample: authored at logical 360×640, rendered on a 1440×2560 device
  canvas, then ONE `pygame.transform.smoothscale` down. Every plank seam, awning
  scallop, glitter dash, gem dome, crate strap and glyph is drawn oversized so
  the downscale resolves crisp anti-aliased edges.
- Reuses the locked constellation primitives + palette anchors from
  `docs/store_redesign/constellation_hi/render_hi.py`: `m`, `font`, `vgrad`,
  `vgrad_stops`, `gold_a_fill`, `soft_glow`, `drop_shadow`, `gradient_text`,
  `plain_text`, `facet_gem`, `cabochon`, `cabochon_glass`, `coin_glyph`,
  `bevel_rim`, `top_sheen`, `gloss_sweep`, `contact_shadow`, `title_wordmark`,
  GOLD / RARITY / MYSTERY anchors — so the bazaar reads as the same store DNA
  (one gold, one bezel, one glass dome, the REAL in-game coin, the gold-on-red
  wordmark). Palms/water/boardwalk reuse `game/draw.py` cloud + mountain helpers.
- Palette anchored on the real golden-hour biome keyframe
  (`biome.palette_for_phase(0.23125)`).
- Both build targets safe: pure pygame, no numpy, no desktop/browser-only API.

## 7 categories → 6 awning stalls + 1 mystery boat
Each stall maps a store group to its first item's **real preview thumbnail**
inside a glass cabochon: `sid = store_catalog.ids_of_group(group)[0]`, then
`parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)`.

| stall | tier | group | preview (round 3) |
|---|---|---|---|
| COSTUMES | back | costume | TOP HAT costume scaled +18% & lifted so the HAT breaks the dome (the costume reads, not the bird) |
| HATS | back | hats | PARTY HAT icon (letterboxed, contained) |
| SHADES | back | shades | **fallback to first shades id with a real icon** (`skin_shades_round`) — group[0] is `skin_shades_none` (bare parrot, no icon) |
| PARROTS | front | parrot | clean **head-on bust** crop (head + breast) of the BLUE-GOLD MACAW — distinct from COSTUMES |
| ANIMALS | front | animal | BEE frame |
| SHOES | front | shoes | a **crossed PAIR** of flip-flops (one tilted 3/4 + a mirrored second), scaled up so it reads as footwear |
| PARCELS | hero | parcels | gold-banded crimson **mystery CHEST** on a spotlit dais (`?` lock plate) |

- **Back row is ≥80px** (84px tall) so the upper tier is comfortably tappable;
  even spacing at x = {0.205, 0.50, 0.795}, nothing cramped at 360px.
- **Front row** 98px at x = {0.20, 0.50, 0.80}.
- **Aspect-extreme items** (flip-flops, party hat) are **letterboxed** in the
  dome (scale-to-fit on the LONG axis to ~1.55× radius), never clipped at the
  rim.
- Each label sits on a scalloped striped-awning + a **bold gold-keyline plaque**
  (dark keyline under a bright bevel = defined edge), the canonical store gold.

## Round 1 → round 2 changes
- **Boardwalk now reads as solid lit wood.** The round-1 raking-light was a flat
  pale disc behind the front row ("glow mush"); it is replaced with planks that
  carry a top-left light: a left-lit gradient + a directional warm sun-rake
  WEDGE (not a circular spotlight), dark seam grooves, a thin lit plank crown
  below each seam, staggered butt-joints, grain streaks, and a **deck AO ellipse
  under every stall / the cart / the PARCELS boat** so nothing floats.
- **Water is now a tasteful sparse specular shimmer.** Round 1's reflection
  column was a hard diagonal-hatched white slab and the bright glints sat on
  round white "bubble" glows. Round 2: a soft warm vertical sun-path smear (no
  hatching, no white), clean horizontal gold glint dashes brightest in the sun
  column and thinning to the flanks, a thin ELONGATED underglow (never a round
  bubble), and a 4-point star kiss only on the very brightest glints.
- **Atmosphere reworked.** A single smooth sky ramp from the indigo jewel-store
  ceiling → warm dusk → golden-hour low `(255,196,112)`; the central violet
  nebula bloom is pushed HIGH + restrained so it no longer rings into a rainbow
  halo behind the wordmark; clouds dimmed + pushed to the upper corners off the
  title. The round-1 white wash above the stalls was the auto-tinted pale back
  layer of `draw_mountains`; islands are now drawn onto a SHORT clipped strip
  just above the waterline with warm silhouette colours.
- **PARCELS is now clearly a glowing-red mystery hero on a moored boat.** Round 1
  treated it as a 7th indigo stall; round 2 makes it its own zone lower-right — a
  moored boat (raised bow/stern posts, crates seated in the hull) crowned by a
  deep-crimson mystery crate with a bold `?`, a warm red bloom (not white), and a
  gold PARCELS plaque beneath. No longer overlaps the SHADES stall.
- **Header wordmark fixed to `STORE`** (round 1 read "BAZAAR"); recessed gold
  balance capsule with the REAL `coin_glyph` + gradient-gold number + a
  `TAP A STALL TO BROWSE` hint.
- **Pip** moved to lower-LEFT of centre (clear of the PARCELS boat); his aura is
  retuned warm + restrained so it no longer reads as a white oval behind him;
  warm top-left rim light; a spinning coin with a soft gold aura above the cart.
- **Depth added without clutter:** two distant moored sailboats (slim warm sails,
  kept off the bright sun column so they read as silhouettes) + hazy back-edge
  palms behind the jetty.

## Round 2 → round 3 changes (art-director ITERATE punch list)
1. **PARCELS HERO re-skinned + de-glitched.** Dropped the half-drawn boat (clutter,
   not depth) and seated a **gold-banded crimson treasure chest** on the dock like
   Pip's cart (`draw_parcels_chest`): a domed crimson lid, two gold horizontal
   straps + a central vertical strap, four gold corner bosses, and a big gold `?`
   on a dark lock plate — so it separates from the awning-reds AND echoes the
   jewel-store gold. Pulled ~40px LEFT off the right edge. The white-blowing
   additive halo is replaced by a **NON-additive crimson dais** (a darkened warm
   seat the chest sits in) + a single thin gold accent ring — reads as "prize on
   a spotlit dais", never a white disc. The PARCELS plaque now sits cleanly BELOW
   the chest (un-collided).
2. **White killed / value hierarchy fixed.** The sun disc is dimmed (−~30% peak),
   shrunk, and biased UP + LEFT (the rake direction) off `SUN_X = 0.20`, so it no
   longer sits behind the capsule or blows the horizon white — the STORE gold now
   owns the brightest value on screen. The water's pale "block" (an additive
   per-row sun column that whitened) is rebuilt as ONE translucent normal-blit
   bell overlay.
3. **Preview legibility.** SHOES is now a **crossed pair** of flip-flops (tilt +
   mirror + scale-up) instead of a flat beige stick; PARROTS is a **head-on bust**
   crop so the macaw's face — not its flying body — fills the dome, making it
   distinct from COSTUMES, which scales the HAT up + lifts it to break the dome.
4. **Back-row separation.** A cooler indigo **contact-AO shelf** is laid behind +
   under the back jetty so the upper tier reads as further back + in lower light,
   not floating in the warm horizon haze.
5. **Cabochon glint varied.** Each dome's specular kiss is nudged in position +
   size off a per-stall `glint` index (all still top-left lit) so the row no
   longer shares one stamped highlight.
6. **Water strip.** +15px taller (`WATER_BOT` m(268)→m(283)) with a clear dark
   waterline edge TOP **and** bottom so the channel-of-water idea lands; the two
   distant boats are now **readable dark silhouettes** (deep-umber hull + a proper
   triangular sail) kept right of the sun path.
7. **Foreground.** One **coiled mooring rope** anchors the bottom-left to balance
   the PARCELS chest on the right; prop contact shadows are flat/straight-edged so
   they don't fight the plank grid.

**Protected (kept, per the AD):** the gold-on-red `title_wordmark("STORE")` +
recessed gold balance capsule + REAL `coin_glyph` (header DNA, pixel-match
cohesion), the solid lit boardwalk planks, the sparse gold glint dashes, the
palms, and the Pip-on-cart concept. The header's restrained-gold-on-dark
discipline is carried into the body (chest straps, dais ring, water edges).

## Open questions for the art director
- The indigo→gold sky still carries a faint violet arc at the upper corners
  (the nebula limb meeting the darker frame). Read as intentional jewel-store
  nebula, or push the corners cleaner?
- COSTUMES now scales the costumed bird up so the hat breaks the dome; it reads
  distinct from the PARROTS bust, but the bird is still present under the hat —
  push to a hat-only silhouette, or is "parrot wearing the costume" the clearer
  category tell?
