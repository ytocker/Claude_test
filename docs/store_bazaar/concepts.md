# Skybit Store — Bazaar Landing HUB Concepts

Five maximally-distinct opening "bazaar stall" landing screens for the coin
STORE. The player lands here first; tapping a stall enters that category grid.
Ideation only — no drawing, no code.

## Shared constraints (all 5 concepts honor these)
- **7 stalls**, one per group: COSTUMES, PARROTS, ANIMALS, SHOES, HATS, SHADES, PARCELS.
- **Pip** (scarlet macaw, gold aviators) is the merchant/host in-frame.
- **360×640 portrait**, procedural pygame, gorgeous at SS=4. Reuses biome sky,
  sandstone pillars, ground/foliage, clouds, the coin, faceted gems, glass
  cabochons, gold gradients, lanterns/awnings from primitives.
- **Leads into the constellation JEWEL store** (deep indigo nebula + warm gold +
  facets + cabochons) so the transition feels seamless.

## Verified Skybit palette anchors (use these exact tones)
- Constellation/night BG nebula: `#080818 → #18103A` (indigo) deepening to `#0C0918`.
- Gold: bright `#F0C040`, deep `#B48214`, pale highlight `#FFE8A8`, UI cream `#F5E6C8`.
- Scarlet macaw / accents: red outline `#A82010`.
- Gem rarity facets already in store: rare blue `#60C4F0`, epic purple `#BE68EC`,
  legendary amber `#FFA838`, common sandstone `#D0B284`.
- Day sky / golden hour / sunset / night are existing biome interpolations — reuse.

---

# RANKING (best first)

1. **CONSTELLATION GRAND-BAZAAR** — purest fit; the night-souk *is* the jewel
   store's sky, so entry is a literal zoom into the same nebula. Most premium,
   most screenshottable.
2. **LANTERN NIGHT-SOUK STREET** — the classic, warmest, most legible "market
   street" read; safest to build well at 360px, instantly says "bazaar."
3. **FLOATING SKY-BAZAAR (Cloud Platforms)** — most uniquely Skybit (a *flying*
   game's shop should float); strong novelty, slightly higher layout risk.
4. **GOLDEN-HOUR DOCK MARKET** — gorgeous warm light + tropical-macaw fit;
   distinct time-of-day, but the dock motif is the least "jewelled."
5. **DESERT CARAVAN AT DUSK** — strongest narrative/silhouette idea and best
   sandstone-pillar reuse; ranked last only because 7 readable wagons on a phone
   is the tightest layout squeeze.

**Prototype first:** #1 Constellation Grand-Bazaar, #2 Lantern Night-Souk, and
#3 Floating Sky-Bazaar — they cover the three best distinct directions (jewel-
native / warm-classic / flight-native) and de-risk the layout question early.

---

## 1. CONSTELLATION GRAND-BAZAAR  ⭐ top pick
**Pitch:** The whole bazaar is woven from the jewel store's own night sky — seven
stalls are constellations of gold light strung across an indigo nebula, and
tapping one "zooms" into that cluster.

- **Mood / setting / time:** Deepest night. The constellation theme of the jewel
  grids, expanded to a full domed souk-of-stars. Awnings are gem-faceted; signs
  are joined-dot constellations; coins drift like slow sparks.
- **Spatial layout:** A gentle **horseshoe/dome** of 7 stalls hugging the upper
  two-thirds, arranged as a 2-3-2 arc (2 high corners, 3 across the middle band,
  2 lower flanks) so each tap target is a comfy ~150px-tall faceted-awning tile.
  Pip's counter anchors the bottom center. Faint gold "constellation lines"
  connect the stall-signs into one figure, reinforcing the dome.
- **Category → stall:**
  - COSTUMES: cabochon-buttoned wardrobe awning; previews Pip in a mini-cape.
  - PARROTS: perch-ring of star-dots; previews a silhouetted second macaw.
  - ANIMALS: a paw-print constellation sign; previews a tiny critter cabochon.
  - SHOES: a boot traced in gold dots; previews a gem-toed sneaker.
  - HATS: a crown/top-hat constellation; previews a faceted hat icon.
  - SHADES: twin lens-cabochons (mirrors Pip's aviators) glinting as a sign.
  - PARCELS: a wrapped-gift formed of 4 corner stars + ribbon arc; mystery glow.
- **Pip's role:** Star-merchant at a low crescent-moon counter, dead center
  bottom, aviators throwing two gold lens-glints; one wing raised in welcome.
- **Palette:** *Night (primary):* indigo nebula `#080818→#18103A`, gold
  `#F0C040/#FFE8A8`, facet accents `#60C4F0`/`#BE68EC`/`#FFA838`, macaw red
  `#A82010`. *Day variant:* same layout over golden-hour sky `#FFE8A8→#E0A050`
  with the constellation lines reading as bunting instead of stars.
- **Signature element:** The **living constellation web** — thin animated gold
  lines linking the 7 stall-signs into a single sky-figure that subtly twinkles;
  tapping a stall makes its cluster flare and pull the camera in.
- **Buildability:** Pure wins — gradient nebula, dot+line constellations, faceted
  polygons, glass cabochons, soft glows: all already in `store.py`'s toolbox.
  Risk: line-web could get busy at 360px — keep ≤14 link-lines, 1px+glow.

## 2. LANTERN NIGHT-SOUK STREET
**Pitch:** A warm covered market lane at night — two rows of striped-awning
stalls recede toward Pip's lantern-lit counter, hanging lanterns overhead.

- **Mood / setting / time:** Festival night-market. Warm, busy, joyful; the
  cozy classic that instantly reads "bazaar." Night sky peeks above the awnings,
  pre-loading the jewel store's indigo.
- **Spatial layout:** A **central market street in 1-point perspective**: 3
  stalls down the left edge, 3 down the right, angled inward toward a vanishing
  point; the 7th (PARCELS, the "mystery" stall) sits dead-center at the end
  beside Pip. All 7 stall-faces are kept upright and ≥90px tall so taps are easy
  despite perspective; a string of lanterns arcs across the top.
- **Category → stall:** each is a striped awning + hanging wooden sign:
  - COSTUMES: tasselled robe on a hook. PARROTS: brass perch with a macaw.
  - ANIMALS: a little cage/critter. SHOES: shelf of gem-laced sneakers.
  - HATS: a hat-tree. SHADES: aviators on a velvet cushion. PARCELS: a glowing
    gift crate under the brightest lantern at street's end.
- **Pip's role:** Lantern-keeper at the end-of-street counter, holding a glowing
  lantern that lights the whole lane; aviators catch the flame.
- **Palette:** *Night:* warm lamp gold `#F0C040/#FFE8A8` pools over deep indigo
  `#080818`, awning stripes in macaw red `#A82010` + cream `#F5E6C8`. *Day:*
  lanterns off, midday sky, awnings brighter, gem accents pop.
- **Signature element:** The **lantern string** — a swag of glowing procedural
  lanterns arcing over the lane, each a soft radial glow + faceted-glass body,
  casting warm pools onto the stalls.
- **Buildability:** Best-understood build — awnings = quads + stripes, lanterns =
  glow+polygon, perspective = simple trapezoids. Risk: perspective can shrink the
  far stalls — cap recession so the farthest awning stays ≥90px.

## 3. FLOATING SKY-BAZAAR (Cloud Platforms)
**Pitch:** A flying game deserves a flying shop — 7 stalls perch on golden cloud
platforms floating at different heights against a twilight sky, linked by gold
rope-bridges, with Pip hovering between them.

- **Mood / setting / time:** Golden-hour-into-night twilight, high above the
  pillars. Airy, dreamlike, premium. Distant sandstone pillars and clouds far
  below tie it to the play world.
- **Spatial layout:** **Stacked staggered platforms** — 7 cloud islands in a
  loose zig-zag column (left-right-left…) filling the portrait top-to-bottom,
  each platform a ~120px tappable disc holding one stall. Thin gold rope-bridges
  and floating coins connect them, guiding the eye down the screen.
- **Category → stall:** each platform = a small awning-stall on a cloud:
  COSTUMES wardrobe-cloud, PARROTS perch-cloud (a second macaw waves), ANIMALS
  critter-cloud, SHOES a cloud with sneakers on the edge, HATS a hat-stand cloud,
  SHADES an aviators-on-stand cloud, PARCELS a mystery-crate cloud wrapped in
  glow at the bottom as the "treasure" anchor.
- **Pip's role:** **Flying vendor** — Pip hovers mid-frame (his natural flap
  pose!) holding a coin, drifting between platforms; the only un-grounded mascot
  of the five, which sells the flight fantasy.
- **Palette:** *Twilight:* sunset `#E0A050→#A82010` low, indigo `#18103A` up
  top, cloud platforms in gold `#FFE8A8` rim-light. *Night:* full constellation
  indigo with star-fields between platforms and gem-glow stalls.
- **Signature element:** **Pip in flight between floating gold-rimmed clouds** —
  the shop that hovers; gentle parallax drift makes the platforms bob.
- **Buildability:** Reuses clouds, gold gradients, coins, awnings. Risk: vertical
  stagger must keep all 7 platforms on-screen at 360px without overlap — lock a
  fixed 7-slot zig-zag template; rope-bridges thin (2px) to avoid clutter.

## 4. GOLDEN-HOUR DOCK MARKET
**Pitch:** A tropical harbor market at golden hour — stalls line a wooden boardwalk
with palms and moored boats, Pip selling from a dockside cart as warm light
rakes across the water.

- **Mood / setting / time:** Golden-hour, tropical, sun-on-water warmth — the most
  overtly "scarlet macaw island" of the set.
- **Spatial layout:** A **boardwalk in two tiers** — 4 stalls along a front
  boardwalk row (lower band) + 3 stalls on a back jetty row (upper band),
  separated by a strip of glittering golden water; palms frame the left/right
  edges. All 7 are upright awning-fronts, front row larger.
- **Category → stall:** dockside crates + awnings: COSTUMES on a sail-cloth rack,
  PARROTS on a ship's-wheel perch, ANIMALS in a wicker crate, SHOES on a
  rope-coiled shelf, HATS on barrel-tops, SHADES on a driftwood stand, PARCELS as
  a crate just off a moored boat (glowing).
- **Pip's role:** Dockside cart-merchant lower-center, gold aviators flaring in
  the low sun, a coin spinning above his cart.
- **Palette:** *Golden hour:* sky `#FFE8A8→#E0A050`, water glitter
  `#F0C040`, awnings macaw red `#A82010` + cream. *Night variant:* harbor
  lanterns + indigo `#080818` sky + gold reflections on black water, easing into
  the jewel store.
- **Signature element:** **Sun-glitter on the water** — a procedural shimmering
  gold band across the harbor behind the stalls (animated specular dashes).
- **Buildability:** Palms/boardwalk = polygons, water glitter = additive dashes,
  reuses awnings/coin. Risk: water shimmer can look noisy small — keep sparse,
  large specks; two-tier layout must keep the back row ≥80px.

## 5. DESERT CARAVAN AT DUSK
**Pitch:** A merchant caravan halted among the sandstone pillars at dusk — 7
canopied wagons (and a star-tent) form a market circle, Pip atop the lead wagon,
campfire glow warming the sand.

- **Mood / setting / time:** Dusk over the desert play-world; sandstone pillars
  in silhouette, first stars appearing — a direct bridge from the game terrain to
  the night jewel store.
- **Spatial layout:** A **shallow horseshoe of wagons** facing the player: 3
  wagons across a back arc, 2 mid flanks, 2 front corners (the front pair
  largest), enclosing a central campfire + Pip. Each wagon's canopy is the
  tappable sign; the back-arc wagons are raised slightly so they read over the
  front pair.
- **Category → stall:** canopied wagons with hanging goods: COSTUMES (robes on a
  line), PARROTS (a caged macaw lantern), ANIMALS (critter crates), SHOES (boots
  hung on the wheel), HATS (hat-rack on the tailgate), SHADES (aviators on a
  pillow), PARCELS (a glowing star-tent at the arc's center as the mystery hero).
- **Pip's role:** Caravan-master perched on the lead front wagon, silhouetted
  against dusk, aviators glinting with the campfire.
- **Palette:** *Dusk:* sandstone `#D0B284`, dusk sky `#E0A050→#18103A`, campfire
  gold `#F0C040`, macaw red `#A82010`. *Night:* full indigo `#080818`, lanterns
  + first constellation stars over the wagons.
- **Signature element:** **The central campfire + glowing star-tent** casting warm
  light up onto the wagon canopies, with sandstone pillars looming behind —
  unmistakably Skybit's world after dark.
- **Buildability:** Heavy reuse of sandstone pillars + ground + foliage; wagons =
  wheels(circles)+canopy(quad). Risk: 7 wagons + fire + Pip on 360px is the
  busiest composition — may need to drop wagon detail and lean on silhouette;
  keep front pair ≥100px, simplify wheels.

---

## Cross-concept notes for the design team
- Every concept ends on the **PARCELS stall as the glowing "mystery hero"** —
  good focal anchor and it matches the surprise/gift language already in-game.
- All 7 stalls should share one **awning-tile template** (vary sign + preview
  item only) so the build stays cheap and the grid reads as a set.
- Keep each tap target ≥88px on the short axis (Apple HIG comfort) at 360px.
- Night variants of all five should converge on the **same indigo+gold nebula**
  so the push into the constellation jewel store is a seamless dissolve.
