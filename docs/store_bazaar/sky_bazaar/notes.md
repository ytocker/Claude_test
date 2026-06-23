# Floating Sky-Bazaar — Store Landing HUB (concept #3)

Selection-sheet prototype for the Skybit STORE "bazaar" landing screen. Docs
only — NOT wired into the game. A flying game's flying shop: seven category
stalls perched on golden cloud platforms zig-zagging down a twilight portrait,
linked by gold rope-bridges, with Pip hovering mid-frame as the un-grounded
flying vendor.

- Render: `docs/store_bazaar/sky_bazaar/render.py`
- Outputs: `round_1.png` (360×640), `round_1@2x.png` (720×1280)
- Run: `python docs/store_bazaar/sky_bazaar/render.py`

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
SHOES→FLIP-FLOPS, HATS→PARTY HAT, SHADES→shades item, PARCELS→ENVELOPE.

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
