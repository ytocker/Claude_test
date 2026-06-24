# Floating Sky-Bazaar — Store Landing HUB (concept #3)

Selection-sheet prototype for the Skybit STORE "bazaar" landing screen. Docs
only — NOT wired into the game. A flying game's flying shop: seven category
stalls perched on golden cloud platforms zig-zagging down a twilight portrait,
linked by gold rope-bridges, with Pip hovering mid-frame as the un-grounded
flying vendor.

- Render: `docs/store_bazaar/sky_bazaar/render.py`
- Outputs: `round_2.png` (360×640), `round_2@2x.png` (720×1280) — the latest
  sheet folds in the round-3 punch list below (filenames kept stable)
  (round 1: `round_1.png` / `round_1@2x.png`)
- Run: `python docs/store_bazaar/sky_bazaar/render.py`

## Round 3 — final art-director punch list (overwrites `round_2*.png`)

ITERATE verdict on round 2; all seven prioritized notes addressed in one pass,
keeping the round-2 wins (continuous gold cloud rim + under-rim, PARCELS red
aura/gem at centre-foot, 6-stop sky + apex nebula, scalloped awnings, bridges):

1. **Header on deep indigo, not a grey slab.** The flat grey legibility band is
   replaced by an indigo deepening that **carries the apex nebula UP behind the
   wordmark** (a re-bloomed violet + warm-gold core) plus a scatter of gold
   sparkle stars in the header lane — the STORE wordmark + balance capsule now
   sit on the jewel-store's near-black-indigo sky.
2. **Cabochon preview legibility.** A lifted **cool-violet value FLOOR** pools in
   the lower half of each dome well (`_well_floor`) so dark thumbs — blue macaw,
   black aviators, the envelope — read against a lit ground instead of dying
   dark-on-dark, and every thumb's **top-left rim light is ~25% stronger** to pop
   its contour. PARROTS / SHADES / PARCELS now match COSTUMES / ANIMALS.
3. **Pip clean.** The muddy white outer ring is gone — the aura is a **tight hot
   warm-gold core with a clean falloff**, Pip is **nudged up** (deck-y 362→344),
   and a soft **indigo back-scrim** is laid directly behind him so his scarlet
   silhouette stays 100% unbroken over any cloud crown; his own rim light is
   lifted too.
4. **Nameplate type.** Bigger cap height (+~10%, 11.5→12.7), a **stronger
   near-black keyline** (wider, darker), and a **thinner gold bevel** so the gold
   letters read crisp at 1× (no gold smear) — matched to the jewel-store tabs.
5. **Coins trimmed ~30%.** Bridge leads cut from two-per-bridge to a `[2,1,1,
   2,1,1]` pattern (12→8) plus Pip's drifting coins 3→2, and every floating coin
   is lifted well clear of the ropes so none lands on a nameplate or dome rim.
6. **Tier gem continuity.** The gem set on each dome rim is the jewel-store's own
   `facet_gem` (same 8-facet brilliant cut + single specular pip) for a seamless
   stall → grid read.
7. **SHOES legible.** The ultra-wide flip-flop (2.9:1) is **rotated to a 3/4
   pose** (24°) inside its dome so the footwear silhouette reads as a shoe rather
   than a thin horizontal sliver. (The representative `[0]` shoe id is kept per
   the store-seeding convention; only its angle changes.)

## Round 2 — good → premium

Held the concept; raised the craft:

- **Cloud platforms now read as SOLID LIT VOLUMES**, not flat puffs. ONE
  top-left key drives a continuous body ramp (hot cream crown → dusk-rose mid →
  violet keel → deepest keel), a soft top-left sheen wash on the crown, a
  translucent violet **ambient-occlusion shelf** cupping the lower-right
  underbelly (painted as a normal alpha overlay, not a channel-subtract — the
  round-1 subtract skewed the dusk body toward muddy green), and a fluffy
  round-shaded lit-crown fringe. The signature gold keyline is now **continuous
  all the way round**: a defined full contour, a brighter warm-gold rim on the
  lit upper-left crown, and a **hotter gold under-rim** along the lit lower-left
  foot (golden-hour bounce) so the island never dissolves into the sky.
- **Data fixes on the previews.** SHADES' first catalog item is `skin_shades_none`
  ("NO SHADES", no icon) — round 1 fronted the stall with a bare base parrot.
  Round 2 detects the missing icon and draws a clean **synthetic aviator-shades
  icon** (gold rim / black lens / sky-tint / glint, matching the game's
  eyewear). Aspect-extreme previews (wide flip-flops 2.9:1, tall party hat
  0.6:1) are now **contained on both dims** and **letterboxed** inside the
  cabochon — the box is held inside the dome's inscribed square (≈R·1.30) so
  nothing clips the glass rim.
- **PARCELS is the red MYSTERY hero.** It always wears the red `MYSTERY` gem +
  glow and gets a red aura blooming behind its dome at the foot, instead of the
  round-1 common-grey tile.
- **Pip** carries a clearer, compact **focal spotlight** (warm aura → hot core)
  that crowns him without bleeding onto the neighbouring stall labels.
- **Atmosphere.** The golden-hour sun bloom is tamed (no blown-out white core)
  and pushed to the very lower-right so the centre PARCELS stall keeps its own
  red aura. The apex gains the **indigo-and-gold jewel-store nebula** (soft
  violet bloom + faint warm-gold core) so entering a stall dissolves cohesively
  into the constellation store; the **star bed is densest/brightest at the apex**
  (fade¹·⁵) and gone before the warm band — emerging stars, no mid-sky haze.

## Pipeline

Authored resolution-independently at **SS=4** (1440×2560 device canvas) with
ONE `pygame.transform.smoothscale` down to 360×640 — identical to the
constellation hi-res store. Every curve, rim, gradient row and glyph is drawn
oversized; the downscale is what yields razor-crisp anti-aliased edges. All
metrics flow through `m()`. Both build targets safe: pure pygame, no numpy, no
desktop/browser-only API.

## Layout — locked 7-slot zig-zag

A fixed `SLOTS` template (logical-px cx, deck-centre-y, platform-half-width,
scale) marches the seven platforms down the portrait in an alternating
left/right zig-zag so all seven stay on-screen at 360px without overlap and
every hit target stays generous (~120–150px wide cloud decks):

1. COSTUMES — upper-left
2. PARROTS — upper-right
3. ANIMALS — mid-left
4. SHOES — mid-right
5. HATS — lower-left
6. SHADES — lower-right
7. PARCELS — **centre foot**, larger + with its own gold aura as the glowing
   "treasure" anchor that every concept ends on.

Gold rope-bridges sling between consecutive platforms (sagging twin gold ropes +
plank rungs + a darker keyline), each carrying a couple of floating coins to
lead the eye down the zig-zag.

## 7 stalls + real previews

Each stall is one shared storefront template (vary sign + preview only): a
striped scalloped macaw-red/cream **awning** on two gold-edged posts, a glass
**cabochon dome** holding the category's REAL preview thumbnail, a tier **facet
gem** set on the dome rim, and a recessed **gold nameplate** carrying the
category name in thick gold-keyline type.

Preview thumbnail per category is the group's representative paid item, seeded
exactly as the live store would: `sid = store_catalog.ids_of_group(group)[0]`
→ `parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)`, contrast-
lifted + top-left rim-lit inside the dome (mirrors the store's `blit_thumb`).
Resolved previews: COSTUMES→TOP HAT, PARROTS→BLUE MACAW, ANIMALS→BEE,
SHOES→FLIP-FLOPS (letterboxed), HATS→PARTY HAT (letterboxed), SHADES→synthetic
aviator-shades icon (the catalog's first SHADES item is NO-SHADES, which has no
icon), PARCELS→ENVELOPE on the red MYSTERY aura.

## Pip — the flying vendor

`parrot.get_parrot(1, 0.0)` (his real flap pose), bounding-box trimmed, scaled
up and hovering **dead-centre mid-frame** between the two columns. Sells the
flight fantasy as the only un-grounded mascot: a warm updraft/hover glow beneath
him, a soft drifting hover shadow, a top-left rim light so he pops off the sky,
and a few drifting vendor coins around him.

## Header

- **Skybit gold-on-red wordmark** via `title_wordmark` (solid gold fill + red
  outline + soft drop shadow — the standard menu wordmark).
- **Recessed gold balance capsule**: the REAL in-game coin (`coin_glyph`,
  `entities._get_coin_face`) in its own cell + a loud gradient-gold number
  (Ramp-A) with a dark keyline + bevel rim — identical to the jewel store so the
  wallet reads the same everywhere.
- A subtle **"TAP A STALL TO SHOP"** hint on a slim dark scrim pill under the
  capsule.

## Palette + signature

Twilight that converges toward the night-jewel store: a 6-stop sky gradient from
golden-hour foot glow `(255,196,112)` up through rose/dusk-plum to the jewel
nebula's indigo apex `(20,18,58)`. A low golden-hour sun bloom is pushed to the
lower-right so it rakes top-left light across the islands without flooding the
centre PARCELS stall. Cloud platforms are warm cream-lit crowns over violet
keels wrapped in a continuous **warm-gold rim-light** — the signature element:
*Pip in flight between floating gold-rimmed clouds*. A sparse star bed emerges
only in the indigo apex (the night-jewel hand-off); far parallax clouds drift
low for depth. Real depth throughout via multi-layer drop shadows under every
platform.

## Primitives reused (from `docs/store_redesign/constellation_hi/render_hi.py`)

`m`, `mf`, `font`, `vgrad`, `vgrad_stops`, `gold_a_fill`, `soft_glow`,
`drop_shadow`, `gradient_text`, `plain_text`, `facet_gem`, `cabochon`,
`cabochon_glass`, `coin_glyph`, `bevel_rim`, `top_sheen`, `gold_rule`,
`title_wordmark`, `multistop_v`, `gloss_sweep`, `contact_shadow`,
`_glyph_base`, `downscale`, `_rim_light`, plus the palette anchors `GOLD`,
`GOLD_PALE`, `GOLD_DEEP`, `RARITY`, `NEAR_BLACK`, `WHITE`, `CREAM`, the Ramp-A
gold lane and the card-ring gold lane.

New world art (cloud platforms, the cloud-island silhouette/shading, rope-
bridges, striped awning, twilight sky bed) is drawn entirely from gradient +
glow + polygon + line primitives — no new raster assets.

## Notes for the critique loop

- Single combined landing sheet (no variant grid) per the brief: a high-end
  mockup of concept #3 to judge layout, depth and the flight fantasy.
- Reuses live catalog + parrot APIs so every preview + the coin + Pip are the
  exact in-game art the player will see.
