# CONSTELLATION store — hi-resolution elevation

A focused single-direction polish of the chosen CONSTELLATION look. The goal
was a massive quality + resolution jump to a Royal Match / Gardenscapes /
Monopoly GO tier, fixing the "high-school final project / low resolution /
poor elements" verdict. DNA kept intact: deep indigo night-sky, round glass
cabochon thumbnails, faceted rarity gems, hairline gold constellation threads,
warm-gold coin + balance capsule, unified chip, the colourblind-safe 4-tier
(common warm-sand / rare cyan / epic violet / legendary orange) + mystery
silver, and the clean three-band card (cabochon → name → chip, no overlaps).

## The #1 lever — true supersampling

`SS = 4`. The entire store is authored resolution-independently: every metric
flows through `m(v) = round(v * SS)` and every font is `_font(size * SS)`. The
whole screen is drawn onto a **1440 × 2560** device canvas, then a single
`pygame.transform.smoothscale` brings it to the **360 × 640** target
(`store.png` / `modal.png`; `*@2x.png` are 720 × 1280 crisp variants;
`detail.png` is a 1.6× logical zoom kept at higher device res).

Why this fixes the amateur look: the aliased edges and chunky 1-px shapes of
the baseline came from drawing at 360×640. Oversized geometry + one high-quality
downscale resolves every curve, bevel, hairline, gem facet, gradient row and
glyph as clean anti-aliased pixels — no per-shape AA hacks needed. Type rendered
at 4× then downscaled is razor sharp with real hierarchy/tracking.

Render pipeline: `multistop_v` nebula → central glow + vignette → constellation
hairlines (ADD) → layered starfield (ADD) → header → 8-card grid → page controls
→ BACK → (modal) → `smoothscale` down.

## Research that set the bar

- Glassmorphism craft — translucent domes, crescent specular, refraction arc,
  1px light edge, inner vignette ("under glass"). (Glassmorphism guides,
  uxpilot / designstudiouiux / medium design-bootcamp.)
- Neumorphism 2.0 / claymorphism 2025 — a consistent top-left light source with a
  paired soft drop shadow + bright lit rim + inner contact shadow on every
  card/button. (ecommercewebdesign.agency, clay.global, justinmind,
  medium claymorphism-vs-glassmorphism guide.)
- Royal Match / casual shop layout language — strict grid, generous padding,
  jewel-grade balance capsule, tactile tab with a clear active pill, polished
  price chips, premium confirm modal. (Game UI Database — Royal Match.)

## Per-element upgrades

- **Background** — flat 4-stop band → a 5-stop indigo→violet **nebula** with a
  soft central violet bloom + a top/bottom vignette for real depth. Starfield
  rebuilt in **three brightness/size strata** plus 14 four-point sparkles with
  glow. Constellation lines are elegant tapered hairlines with glowing **node
  stars**.
- **Glass cabochon** — the biggest single fix. A dark domed glass body (radial,
  many steps) with a gentle inner vignette; the thumbnail sits *inside* the well
  (1.5×R) so it reads under glass; an overlay adds a true **top-left crescent
  specular** (disc-minus-offset-disc so only the lit arc survives, not a ring),
  a broad low sheen bloom, a bottom-right **refraction arc**, a thin warm-gold
  **bezel** (dark contact keyline + gold rim + bright glass kiss on the upper-left
  arc). The earlier "bright ring" was a wide additive tier-glow halo — removed;
  the tier aura is now a whisper-soft tight glow behind the dome.
- **Rarity gem** — upgraded from a flat 4-triangle diamond to a **true cut**:
  4 crown facets + a flat table facet (multiple value steps), facet keylines, a
  crisp girdle, a dark seat well, and a hot specular pip. Tiny, inset, catches
  light at the downscaled size.
- **Cards** — full **depth stack**: multi-layer blurred drop shadow (offset down
  from the top-left source), gradient body (gamma-eased, no banding), glossy top
  sheen, bottom-right inner **contact/AO shadow**, and an embossed **bevel rim**
  (dark outer keyline + top-left-biased bright stroke). Strict three-band grid;
  a faint gold map-rule separates name from chip.
- **Balance capsule** — recessed jewel-grade gold: gradient-gold body, top sheen,
  inner contact rim, lit bevel; coin in a dedicated left cell with a real gap so
  it never touches the **gradient-gold digits**; coin itself rebuilt with a
  radial bevel, directional sheen, crisp rim and $ relief.
- **Tabs** — tactile strip: recessed track with a clear **active pill**
  (gradient + sheen + bright rim, dark text) vs muted inactive labels; even
  spacing, sits clear of the grid.
- **Chips** — one family (price / EQUIPPED / can't-afford-locked): gradient body,
  top sheen, contact shadow, drop shadow, hairline rim, beveled coin or lock.
- **Page controls + BACK** — beveled gradient arrow buttons; the PAGE label and
  arrows sit on their own row with a clear gap above the **premium BACK pill**
  (gradient body, sheen, contact shadow, lit bevel, chevron + label). Card height
  was tightened so nothing overlaps at the bottom.
- **Modal** — premium confirm: deep gradient panel with the full depth stack,
  soft **gold rule** under the heading, a large connected cabochon **stage** with
  the gem seated in its corner, centered name/rarity/price grid, glowing gradient
  **BUY** + neutral **CANCEL**.

## Round 2 — user feedback (top priority) + art-director punch list

### User demand 1 — FONT must be thicker + crisper

Every UI string now runs through a faux-bold + keyline pipeline authored at SS:

- `_stamp_bold(base, weight)` composites the SS glyph onto itself at a small
  8-point ring (≈1–2 device px) so strokes grow evenly without filling counters
  — a real weight bump from the single shipped Bold ttf.
- `gradient_text` / `plain_text` gained `weight` + `keyline` (a tight dark
  contour stamped at 8 angles). Body labels (item names, BACK, PAGE, modal text,
  tab labels) get a near-black keyline for strong contrast on the dark sky;
  titles/numerals get heavier weight + their own keyline.
- Sizes lifted where they read small: item name 14→16 (auto-fit), balance number
  20→25, modal name 18→20, BACK 17→18, arrows 15→16.

### User demand 2 — OUTLINES on every element

Introduced a shared **dark-keyline-under-bright-bevel** treatment so each object
is a clearly delineated tactile shape, authored ~1.6–2 px PRE-downscale:

- `chip_body()` (new) = gradient + gloss sweep + dark outer keyline + bright
  top-left bevel; used by the whole chip family.
- Cards, balance capsule, tab pill, page arrows, BACK, modal panel + both modal
  buttons all gained an explicit dark outer keyline drawn under the bevel rim.
- Card top sheen widened/brightened (m20→m30, peak46→62) + bevel rim m1.6→m2.0
  so the GRID cards carry the detail.png finish (verified at 1:1).

### User demand 3 — PRICE chip palette redesigned

New `price_chip()` replaces the old muddy gold chip:

- Rich, well-separated gold body (bright gold crown → deep amber base), crisp
  double rim, a diagonal gloss sweep, a clean beveled coin in its own cell, and
  **dark deep-brown numerals** for punch (faux-bold).
- **Two colour options rendered in detail.png** for the user to pick:
  Option A = single rich warm gold (the default in the store screen,
  `PRICE_VARIANT = 1`); Option B = brighter champagne two-tone (champagne crown
  over saturated amber). Both shown affordable + locked.
- Can't-afford chips share the family: a lighter cool-slate body with LIGHT
  legible numerals + a dimmed coin (no colliding lock glyph).
- EQUIP / EQUIPPED use the same `chip_body` finish (one product line).

### Art-director punch list

1. **STORE title rebuilt** — killed the chunky faux-3D extrude. `title_wordmark()`
   is now a single clean gold bevel: warm-gold vertical gradient mapped over the
   glyph's true extent, one thin specular glint on the cap, a dark keyline, and a
   single soft contact shadow. Consistent stroke weight, legible.
2. **Header spacing** — title baseline raised + balance capsule dropped (gap
   ~+50%); coin sits in its own cell with an enforced gap to the first digit;
   balance number enlarged + bolded (the money screen).
3. **Grid material finish** — sheen + bevel propagated to grid cards (above).
4. **Thumbnail contrast + rim light** — `_punch_contrast` lifts the skin's value
   off the dark dome (additive, alpha untouched, no invented detail) and
   `_rim_light` adds a crisp top-left contour so the silhouette pops.
5. **One tab active state** — a filled gold pill with dark bold text + gloss +
   bevel; inactive tabs muted (cool grey, lighter weight); equal-width cells so
   PARCELS no longer hugs the edge.
6. **Constellation thread** — now a deliberate brighter **tapered** thread
   (stacked decreasing-width lines) with a glowing node star.
7. **Modal** — BUY CTA gained a gloss sweep + a subtle inner top glow + outer
   halo; scrim flattened to a clean ~70%; CANCEL lifted one value step off the
   panel; corner gem seated deliberately on the dome rim at 45°.
8. **Bottom row** — BACK raised for more bottom margin; page-arrow tap targets
   +15% (34×24 → 39×28).
9. **Gem + rarity at downscale** — verified epic-violet vs mystery-silver read
   distinctly at grid-corner size on dark cards.

## Files

- `render_hi.py` — the SS-aware renderer (pure pygame, both-target safe).
- `store.png` / `store@2x.png` — full store at 360×640 and 720×1280.
- `modal.png` / `modal@2x.png` — buy-confirm modal.
- `detail.png` — 3 hero cards + the price-chip colour-options bay (A vs B,
  affordable + locked, shared EQUIPPED finish).
