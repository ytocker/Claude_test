# Coin Store redesign — concepts_v2 (selection sheet)

Five brand-new, genuinely distinct high-end store concepts, each a complete
look that could ship and each unmistakably loyal to Skybit's established visual
language (tropical macaw, warm-gold coins, day/night biome sky, sandstone
pillars, casual-arcade joy). This is a SELECTION sheet — no convergence, no
integration. The art-director / user picks one.

These five are deliberately NEW directions versus the prior three rounds
(Gem Vitrine / Foil Cards / Tropical Ticket / **Obsidian & Gold (shipped)** /
Aurora Shelf): none of them is a dark-obsidian re-tread.

- Harness: `docs/store_redesign/concepts_v2/render.py` (headless,
  `SDL_VIDEODRIVER=dummy`, repo root on `sys.path`) + `concepts.py` (the five
  concept classes).
- Combined sheet: `docs/store_redesign/concepts_v2/concepts.png` — 5 columns
  (one concept each), every column stacking that concept's **(a)** full
  360×640 store, **(b)** buy-confirmation modal, **(c)** 2–3 card detail zoom,
  under a concept NAME + one-line descriptor.
- Real catalog items, the real price→rarity ladder, real procedural thumbnails
  (`parrot.get_skin_icon` / `get_skin_frame`), real equipped / secret /
  can't-afford states. The 8-card grid spans all four tiers + an EQUIPPED card
  (OWL) + a masked SECRET card (UFO ???).

Shared, kept loyal across all five (so the store still feels like one family
with the rest of the game):
- the **flat-gold `$` coin** (single diagonal bevel + stamped `$`) drawn the
  same in the price chip, the balance capsule, and the modal;
- the **faceted rarity gem** (4-value diamond cut + specular pip, dark keyline
  well) as the SECONDARY tier marker;
- the **gold balance capsule** (recessed gold body, glowing coin, gold-gradient
  digits) as the brightest element on screen;
- the **unified pill chip** silhouette for price / equip / equipped /
  can't-afford (each concept recolours it to its palette);
- a **soft gold gradient rule**, **drop shadows**, and **diagonal-split inner
  bevels** for depth;
- rarity reads by **HUE *and* VALUE** within each concept's own world
  (colourblind-safe), with the neutral-silver MYSTERY state reserved for
  secrets so it claims no tier.

All primitives are standard pygame surface ops (gradients, polygons,
`BLEND_ADD` / `BLEND_RGBA_MIN` / `BLEND_RGBA_MULT`, smoothscale) — nothing
numpy / desktop-only / browser-only — so any chosen concept ports straight into
the live store draw path on both build targets.

---

## 1. LAGOON BOUTIQUE
*Tropical dusk · brass & teak · palm-shaded vitrine*

- **Loyalty:** the biome SUNSET / GOLDEN-HOUR sky (indigo→rose→amber horizon
  band), warm sandstone-adjacent woods, warm gold coins, the macaw's home
  lagoon. Palm silhouettes at the base echo the in-world tropics.
- **Structural motif:** a dusk boutique shelf. Each card is a warm **cream
  "menu plaque"** inset on a **teak board** with a **brass top-rail**, sitting
  under a screen-wide brass rail header.
- **Palette:** teak `(96,58,34)→(60,34,20)`; cream plaque
  `(250,236,206)→(228,200,158)`; brass gold `(255,206,120)`; dusk-lagoon
  background `(46,28,78)→(120,52,96)→(214,96,92)→(255,168,96)`.
- **Rarity language:** warm-sand common / **lagoon-teal** rare / **orchid**
  epic / sunset-gold legendary, expressed as a hot-centred brass **rail strip**
  across the plaque top (PRIMARY) + the gem badge (SECONDARY). Thumbnails sit
  on a **teal lagoon shelf disc**. Legendary cards get a tiny gold **palm
  sprig**.
- **Typography:** dark warm ink names on the cream plaque (high contrast,
  boutique-menu feel); tracked gold display title.
- **Signature high-end detail:** the warm cream plaque-on-teak with a brass
  rail — the only **light-card-on-warm-frame** treatment in the set; reads like
  a hand-lettered boutique menu, instantly different from the dark family.

## 2. NIGHT AVIARY
*Indigo jewel-box · gold filigree · glass cabochon*

- **Loyalty:** the NIGHT biome (deep indigo, twinkling star field), the menu's
  gold-on-red title, the established gem ladder.
- **Structural motif:** a velvet jewel-box drawer. Each card is a **translucent
  glass cabochon panel** with a top glass sheen, **gold filigree scroll
  corners**, and a faint **constellation line** linking the corner gem to the
  item — as if each cosmetic is a mounted jewel.
- **Palette:** glass `(40,36,70)→(18,16,40)` on an indigo
  `(6,6,28)→(30,18,72)` sky; full warm gold accents (`_GOLD_BRIGHT`).
- **Rarity language:** the classic casual gem ladder re-seated for night —
  pearl-lavender common / blue rare / violet epic / gold legendary — as a
  **rarity aura bloom** behind the thumbnail disc (PRIMARY) + the corner gem +
  its constellation (SECONDARY).
- **Typography:** gold-pale names with a near-black drop, the shipped
  gold-on-red `STORE` lockup, hairline gold frame around the whole screen.
- **Signature high-end detail:** the **gold filigree corners + constellation**
  glass-cabochon card — the most jeweller-grade, AAA-minimal direction; the
  truest evolution of Skybit's night-sky-and-gold identity.

## 3. SKY TEMPLE
*Sandstone tablets · fluted pillars · carved gold inlay*

- **Loyalty:** the game's own **sandstone pillars** and the biome stone palette,
  rendered as the shop's architecture; warm daylight sky above warm stone.
- **Structural motif:** a carved sky-temple. Each card is a **sandstone tablet**
  with **fluted pillar edges**, a **carved niche** holding the thumbnail, a
  **sunlit inlay band**, and engraved names — set under a carved **stone lintel**
  header. A faint colonnade stands behind the grid.
- **Palette:** stone `(224,196,156)→(120,92,64)` with carve lines; warm gold
  inlay `(255,214,130)`; day-to-stone background
  `(70,120,188)→(196,158,120)→(150,110,78)`.
- **Rarity language:** sand common / stone-teal rare / temple-violet epic /
  hot-gold legendary, as the glowing **sunlit inlay band** (PRIMARY) + the gem
  (SECONDARY); thumbnails sit in a recessed **stone niche**.
- **Typography:** **engraved** names (dark inlay + gold top edge), a tracked
  `SKY STORE` cut into the stone lintel. The modal is a full carved-stone panel.
- **Signature high-end detail:** the **carved-niche + sunlit-inlay sandstone
  tablet** built from the game's actual pillar material — the most
  "this-is-literally-Skybit's-world" direction, warm and tactile.

## 4. CLOUD NINE
*Day-sky clouds · candy-gloss bubbles · airy premium*

- **Loyalty:** the bright DAY biome sky (cyan→pale), warm gold, the airy
  casual-arcade joy — the only **light / daytime** concept, for contrast.
- **Structural motif:** a sky shop. Each card is a **glossy white "cloud
  bubble"** floating on a soft **cloud shelf**, with a candy top-gloss and a
  glossy **rarity ring** around the thumbnail. Soft cloud puffs drift in the
  background.
- **Palette:** bubble `(255,255,255)→(216,232,244)` on a day sky
  `(86,168,230)→(224,240,250)`; warm gold rim `(255,196,70)`.
- **Rarity language:** ivory common / sky-blue rare / candy-violet epic /
  gold legendary, as a **glossy candy ring** around the disc (PRIMARY) + the
  gem (SECONDARY); thumbnails sit on a bright **sky disc**. The can't-afford
  chip goes cool pale-slate so it never reads as the warm gold price.
- **Typography:** soft blue-grey names for readable contrast on white; tracked
  gold title; a bright airy modal with a 3px gold rim.
- **Signature high-end detail:** **candy-gloss white bubbles on cloud shelves**
  — a genuinely bright premium that proves the gold/rarity system survives a
  daytime palette; the freshest, most "casual-joy" break in the set.

## 5. SKYLINER
*Art-deco travel poster · sunburst · teal/coral & gold*

- **Loyalty:** warm gold + the macaw as an airline "mascot" + the sky/sunset
  palette, expressed through 1930s travel-poster Art Deco linework (deep blues,
  golds, jewel tones — the era's actual palette).
- **Structural motif:** a deco travel ticket. Each card is a framed **deco
  ticket** with **stepped (chamfered) gold corners**, a restrained **sunburst
  halo** behind the thumbnail, and twin **deco rule lines** flanking the
  wordmark; a stepped deco header plate with a sunburst sky.
- **Palette:** teal panels `(28,64,74)→(16,42,52)` on a teal-deco background
  `(16,44,58)→(40,120,120)`; deco gold `(240,198,96)`; coral epic accent.
- **Rarity language:** ivory common / teal rare / **coral-rose** epic / gold
  legendary, as the **deco rule** flanking the name + a rarity-tinted sunburst
  (PRIMARY) + the gem (SECONDARY).
- **Typography:** wide-**tracked** deco display title with a flanked-rule
  sub-wordmark; gold-pale names. The chip family + modal carry the stepped
  deco frame.
- **Signature high-end detail:** the **stepped-corner gold deco frame +
  sunburst** — an elegant, era-specific, distinctly non-fantasy take that still
  lives in Skybit's gold-and-sky world; the most graphic-design-forward option.

---

## Files
- `docs/store_redesign/concepts_v2/render.py` — harness + shared primitives +
  store/modal/detail composer + the comparison-sheet builder.
- `docs/store_redesign/concepts_v2/concepts.py` — the five concept classes.
- `docs/store_redesign/concepts_v2/concepts.png` — the combined comparison sheet.
