# Skybit Store — CONSTELLATION theme spec (shared anchor for all element loops)

Every store element is designed in its own parallel design loop, but they MUST
all read as one screen. This is the single source of truth: palette, materials,
lighting, type, edges, spacing. The art-director enforces it — any element that
drifts from this spec is sent back regardless of how nice it looks alone.

Reference implementation of the pipeline + primitives:
`docs/store_redesign/constellation_hi/render_hi.py` (reuse it).

## Non-negotiables (cohesion rules)
- **Resolution:** author everything resolution-independently and render at
  **SS = 4** (1440×2560), one `smoothscale` down to 360×640. No raw 1px shapes.
  Type at `size*SS`. This is THE crispness lever — keep it.
- **One light source:** top-left. Every surface: bright top-left bevel + gloss
  sheen on top, dark contact/AO shadow bottom-right. Consistent everywhere.
- **Every element has a DEFINED EDGE** (explicit user note): a dark OUTER keyline
  drawn UNDER a bright top-left bevel, authored ~1.6–2px pre-downscale so the
  edge survives. Nothing floats/melts into the background.
- **Type is THICK + crisp** (explicit user note): project bold font, faux-bold
  stamp for added weight, a tight dark keyline around labels for contrast.
  Heavier and sharper than a plain render. Sizes generous, never cramped.
- **Corner radius language:** cards ~17 logical px; pills/chips fully rounded
  (h/2); modal ~20. Keep radii consistent across siblings.
- **Strict grid, generous padding.** No unintended overlaps, ever. Three-band
  card: cabochon → name → chip, each in its own clear lane.

## Palette (locked)
- **Night sky / nebula bg stops:** (6,7,24)→(11,11,40)→(18,16,58)→(26,20,72)→
  (14,12,46), with a soft central violet bloom `NEBULA_GLOW (70,60,150)` +
  vignette. Three-strata starfield + tapered gold constellation hairlines w/ node stars.
- **Gold family:** `_GOLD_BRIGHT` / `_GOLD_PALE` / `_GOLD_DEEP` (from game.hud).
  Title gradient (255,246,200)→(242,182,70), red-outline `_RED_OUTLINE`.
- **Card body:** top (28,30,70) → bottom (12,13,38). Cabochon well (22,24,50)→(6,7,20).
  Card gold ring deep (58,48,22) / bright (236,202,116). Name (246,240,216).
- **Rarity (hue AND value distinct, colourblind-safe) — gem/glow/deep:**
  - common  gem(214,206,230) glow(180,174,214) deep(78,74,112)  — pale lilac-silver
  - rare    gem(108,188,252) glow(74,158,248)  deep(24,78,142)   — cyan-blue
  - epic    gem(194,122,248) glow(172,94,244)  deep(80,34,126)   — violet
  - legendary gem(255,202,104) glow(255,168,58) deep(150,92,22)  — warm gold-orange (standout)
  - MYSTERY gem(226,232,244) glow(196,214,236) deep(90,98,124)   — neutral silver, claims NO tier

## Materials (recipes — keep identical across elements)
- **Glass cabochon:** dark domed well (CABO_LO→CABO_HI), the skin set INSIDE the
  well rim-lit (punch contrast + top-left rim light so the silhouette pops — the
  content must out-pop its frame), a true top-left crescent specular (disc minus
  offset disc, not a full ring), a faint bottom-right refraction arc, inner
  vignette, thin warm-gold bezel.
- **Rarity gem:** real multi-facet cut (crown facets + table + girdle keyline),
  dark seat well, one hot specular pip. Survives at grid-corner size. Seated in
  the card corner with margin — never crowds the cabochon or bezel.
- **Constellation thread:** a deliberate tapered gold hairline from the gem to a
  small node star near the cabochon. Intentional, not a stray line.

## Price chip (explicit user directive)
- The cost chip is a **SINGLE SMOOTH GOLD GRADIENT** (a gradual bright-crown →
  deep-amber ramp). **Do NOT split it into two different colours / two-tone.**
- Dark deep-brown numerals for punch, a clean beveled coin in its own cell with a
  clear gap before the digits, crisp double gold rim, a single gloss sweep.
- EQUIP / EQUIPPED (green state) / can't-afford (cool slate, light legible
  numerals) share the same pill silhouette + edge finish — one family.

## Element workstreams (each its own loop; all obey the above)
1. **atmosphere** — nebula bg + starfield + constellation field (the canvas).
2. **header** — "STORE" wordmark (clean gold bevel, NO chunky extrude) + the
   recessed gold balance capsule (coin clear of a LOUD gradient-gold number).
3. **tabs** — tab bar: ONE active state (filled gold pill, dark bold text) +
   muted inactive + chevrons; even spacing.
4. **card** — card chassis: panel, bevel rim, dark keyline, top gloss, equipped
   gold frame + halo, the three-band internal layout.
5. **cabochon** — the glass dome + rim-lit thumbnail (per recipe above).
6. **rarity** — gem + 4-tier+mystery language + constellation thread.
7. **chips** — price (single-gradient, per directive) + EQUIP/EQUIPPED/locked.
8. **controls_modal** — BACK pill, page arrows, and the buy-confirm modal
   (panel + ~70% scrim + BUY gloss CTA + CANCEL one value step apart + seated gem).

## Output contract per element loop
Self-contained headless render under `docs/store_redesign/elements/<name>/`:
`render.py` → `round_N.png` (the element shown at large SS-crisp scale, a few
variants, ON the shared night-sky bg, using REAL items/thumbnails where relevant
via `parrot.get_skin_icon/get_skin_frame` + `store_catalog`) + `notes.md`.
Files only — the orchestrator commits and assembles. Both build targets safe
(pure pygame, no numpy/desktop-only APIs).

---

# COHESION CANON (locked after the round-1 holistic critique)

The element exploration is done. These are the LOCKED winning variants + the
single canonical values every element must converge to in assembly. The
art-director flagged gold-tone drift as the #1 amateur tell — so gold is
unified to ONE ramp, with only the two named exceptions.

## Winning variants
- atmosphere → **B** (deep, low bloom, sparse stars) but pull central bloom
  radius ~15% / peak ~20% so the card-grid band stays dark; constellation
  thread at ~A density with B's taper; darkest bands top/bottom 12%.
- header → **C wordmark** (clean gold bevel, NO extrude) + loud-number capsule.
- tabs → **C** (raised jewel), active pill retoned to the canonical gold ramp.
- card → **B** (inner tray); thicken the EQUIPPED gold frame (2-step bevel + halo).
- cabochon → **C** dome, with the specular FIX below.
- rarity → faceted **8-facet (B)** cut as the ONE gem shape for all 5 tiers.
- chips → price **Ramp A** (royal gold) single gradient.
- controls_modal → dark BACK pill (gold keyline, NOT filled gold) + leftmost modal.

## Canonical GOLD RAMP A — the ONE gold for every gold FILL
Used for: tab active pill, header balance number, price chip, BUY CTA, page
highlights. Single smooth vertical ramp (gamma 1.06):
- stops: 0.00 (255,224,150) · 0.34 (250,198,92) · 0.68 (224,154,44) · 1.00 (176,110,22)
- rim_dark (86,50,8) · rim_bright (255,240,190) · numerals (52,28,4) · coin_rim (120,74,14)
Nothing else invents a gold.

## The 3 locked GOLD LANES (do not cross-harmonize)
1. Gold FILLS → Ramp A (above).
2. Rarity gems → own the COLOURED hue space (their gem/glow/deep triplets).
   Legendary gem gold (255,202,104 / glow 255,168,58 / deep 150,92,22) is
   INTENTIONALLY brighter than Ramp A so legendary stays the standout — never
   harmonize it down.
3. Cabochon bezel + card gold RING → bright (236,202,116) / deep (58,48,22).

## Canonical EDGE (every element, identical)
Dark OUTER keyline ~`m(1.8)` UNDER a bright top-left bevel ~`m(1)`. Applied to:
header capsule, tab pills + chevrons, card chassis, all chips, BACK pill, page
arrows, modal panel. One weight everywhere (chevrons + arrows currently flat — fix).

## Canonical RADIUS family
cards 17 · pills/chips/arrows/BACK fully rounded (h/2) · modal 20. (Re-round the
square page-arrow buttons.)

## Canonical MATERIAL (single top-left light)
Every surface: bright top-left bevel + ONE gloss sheen on top + bottom-right
contact/AO shadow. No extrude (header), no flat (card), no two-tone gold (chips).

## Glow ranking (brightest → restrained)
equipped card halo > legendary gem > BUY CTA gloss > everything else.
The cabochon specular is a **translucent SHEEN, not a glow**: a THIN top-left
crescent at ~50–65% alpha so the skin reads THROUGH it (round-1's opaque white
slab ate the parrot — the single biggest quality fix). After the fix, push the
skin's rim-light contrast ~20% so the content out-pops its frame.

## Other locked fixes
- Mystery gem: half-step brighter/neutral so it clearly claims NO tier (was
  collapsing onto common in grayscale).
- Inactive tab labels: lift to ~55–60% L (legible muted cream/gold).
- Coin glyph (chips + header capsule): same beveled coin, clear gap before digits.
- Modal title stamped to project bold; CANCEL one value step under the panel;
  scrim ~70% (may need +5–10% over the live grid).
