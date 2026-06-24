# Floating Sky-Bazaar — Store Landing HUB (concept #3)

Selection-sheet prototype for the Skybit STORE "bazaar" landing screen. Docs
only — NOT wired into the game. A flying game's flying shop: seven category
stalls perched on golden cloud platforms zig-zagging down a twilight portrait,
linked by gold rope-bridges, with Pip hovering mid-frame as the un-grounded
flying vendor.

- Render: `docs/store_bazaar/sky_bazaar/render.py`
- Outputs: `round_3.png` (360×640), `round_3@2x.png` (720×1280) — the current
  sheet. `round_2*.png` is kept as the "before" for the white-aura comparison.
  (round 1: `round_1.png` / `round_1@2x.png`)
- Run: `python docs/store_bazaar/sky_bazaar/render.py`

## Round 3b — the REAL white-aura cause: additive glow saturation (→ `round_3*.png`)

Round 3a (below) recoloured the small glows but the headline complaint did NOT
move: pixel-measured, the cloud BODIES were still 35–61% pure `(255,255,255)`.
The root cause was finally isolated and fixed:

**`render_hi.soft_glow()` composites its feathered rings with `BLEND_ADD`.**
Where rings overlap (every glow centre) the channels SUM past 255 → literal
pure white. Three places did this onto already-bright ground and produced the
"white aura the user is reacting to":

1. **The cloud keel underglow** — `soft_glow(... (236,158,96) ...)` stacked dead-
   centre of every cloud's lower body → a pure-white blob filling the cloud
   middle. THIS was the cloud white, not the crown.
2. **The apex nebula** (3 stacked glows) → the entire top sky behind the header
   blew out to pure white instead of deep indigo.
3. **The PARCELS red MYSTERY aura** → summed red onto the light foot cloud into a
   white core (also killing the red treasure signal).

Fix: a new local `capped_glow()` composites rings with `BLEND_RGBA_MAX` (the
strongest ring wins, never sums), so a glow caps at ONE opaque pass of its own
colour — a violet bloom stays violet, gold stays gold, red stays red, none can
reach white. Applied to the keel kiss, the cloud key-light (also rebuilt as a
single MAX pass), the apex + header nebula, the sun bloom, and the PARCELS aura.

Plus the round-3b craft asks: cloud body anchors capped so the lit cap tops out
at warm cream `(248,234,205)` (~88% luminance, never white); a real top-left→
base value ramp driven through each crown lobe (cream cap → dusk-rose → violet
keel, the upper 60% no longer a white card); a deeper violet AO; and an indigo
rim-shadow on each cloud's shadowed right/lower edge so neighbouring clouds /
Pip / nameplate caps stop merging white-on-white into one blob. The warm-gold
crown rim is the brightest mark on every cloud — gold owns the light.

**Sanity gate (pixel-measured on `round_3@2x.png`):**

- Cloud bodies (isolated): **worst 1.48% pure white** (was 35–61%) — the residual
  is only the thin gold rim-arc specular kisses.
- Full composite: **4,846 pure-white px = 0.53%** (was ~120k ≈ 13%), the residue
  being Pip's beak/coin catch-lights + gold rim kisses (intentional specular).

## Round 3a — kill the small white auras (folded into the same files)

The user liked concept #3 but said it still read like "a basic idea" and, above
all, that "a white aura coming out of many places makes it look really bad."
That was justified: the scene was full of additive near-white glows/sheens that
read cheap and over-lit. Round 3 retunes EVERY cheap white aura to a warm-gold
discipline (recoloured + alpha-tamed, never just deleted — the lighting stays)
and pushes overall craft, keeping the concept and layout intact.

- **Cloud key light (biggest offender).** `cloud_platform()`'s upper-left crown
  wash was a near-white `(255,248,230)` α78 at radius 0.95·rw — a halo bleeding
  across each cloud and onto its neighbours. Recoloured to warm gold
  `(240,200,120)` at **α44**, radius tightened to 0.66·rw, plus a tiny hot
  `(255,226,168)` α40 specular kiss. Clouds now read sun-LIT and voluminous, not
  blown out. The crown anchor was also warmed off pure white (`(255,247,232)` →
  `(255,240,210)`).
- **Cabochon glass.** The constellation `cabochon_glass` paints a pure-white
  crescent (α150) + white edge glint (α120) — plastic on these domes. Overridden
  LOCALLY in this render: the crescent is now warm pale-gold `(255,238,196)`
  **α90** and the rim kiss `(255,234,184)` **α70**, so the glass reads as glass
  set in gold, not shiny plastic. (Refraction arc + gold bezel kept.)
- **Pip.** Inner glow `(255,234,178)` α56 → warm gold `(255,214,138)` **α40**;
  rim light `(255,248,220)` α195 → warm `RIM_WARM (255,224,150)` **α150**. His
  scarlet silhouette is now clean with NO white bloom; the dark back-scrim stays.
- **Top sheens.** Awning gloss `(255,255,255)` α70 → warm `(255,240,206)` **α22**;
  nameplate `top_sheen` peak 44 → **24**; balance-capsule `top_sheen` peak 50 →
  **24**. Surfaces now read matte-premium gold, not toy vinyl.
- **Header sparkle.** The busy 26-dot field + 4 white cross-spikes with
  `(255,236,196)` α90 blooms (cheap glitter) is cut to **13 faint warm-gold dots,
  no spikes, no blooms** — the header is a calm deep-indigo lane with the gold
  wordmark owning the value.
- **Sun + apex stars.** The sun's inner core `(255,238,196)` α56 near-white wash
  → amber-gold `(250,196,120)` α44, radius tightened, outer ring α50 → 44. The
  apex cross-stars warmed (`(255,244,206)`→`(255,226,168)`), shorter spikes,
  tamer blooms (α80→52) — gold twinkle, no pale mid-sky wash.
- **Shades glints.** The pure-white opaque lens dots → warm pale-gold
  `(255,240,206)` / `(255,232,188)` α190, smaller — a lit catch, not a flare.
- **Preview rims.** Every dome thumbnail's top-left rim light was the
  constellation near-white default; now `RIM_WARM`, so dark previews still pop
  their contour but with no cold white edge fighting the warm scene.
- **Craft push — cloud volume.** The crown puff fringe is re-sculpted: each lobe
  now has an OFFSET-centre value ramp (lit cap top-left → dusk base) plus a soft
  violet AO core-shadow crescent clipped inside the lobe and a thin warm-gold cap
  rim arc, so the lobes read as overlapping 3D balls of cloud tied to the gold
  keyline — not flat discs.

Net: a cohesive warm-gold-on-deep-indigo read with no white aura anywhere,
coherent with the constellation jewel store the stalls open into.

## Earlier punch list (folded into `round_2*.png`)

A prior ITERATE pass; seven prioritized notes addressed in one pass, keeping the
round-2 wins (continuous gold cloud rim + under-rim, PARCELS red aura/gem at
centre-foot, 6-stop sky + apex nebula, scalloped awnings, bridges):

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
