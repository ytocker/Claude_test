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

## Round 3 — FINAL ASSEMBLY (fold the 8 refined elements + the locked canon)

This pass converges `render_hi.py` to the **COHESION CANON** locked after the
round-1 holistic critique (see `docs/store_redesign/elements/THEME.md`). The #1
rejection was **gold-tone drift**, so every gold FILL is now one ramp, with only
the two named exceptions kept as separate lanes.

### Canon items — each confirmed in the renderer

- **ONE gold-fill ramp (Ramp A).** New `GOLD_A_STOPS` + `gold_a_fill()`
  (stops `255,224,150 · 250,198,92 · 224,154,44 · 176,110,22`, gamma 1.06,
  rim_dark `86,50,8`, rim_bright `255,240,190`, num `52,28,4`,
  coin_rim `120,74,14`). Routed through it: **tab active pill**, **header
  balance number**, **price chip body**, **BUY CTA**, **page-control arrow
  highlights**. The old two-tone champagne price option (PRICE_OPT B) is
  deleted — price is a single smooth Ramp-A gradient.
- **3 gold lanes, not cross-harmonized.** Lane 1 = Ramp-A fills (above).
  Lane 2 = rarity gem hues — legendary gem stays `255,202,104` (deliberately
  brighter than Ramp A; never harmonized down). Lane 3 = cabochon bezel + card
  ring = `236,202,116 / 58,48,22` (the cabochon bezel now draws with
  `CARD_RING_BRIGHT`, so dome + card frame share one gold).
- **ONE edge everywhere.** Dark outer keyline (~`m(1.8)`) under a bright bevel
  (~`m(1)`) on the header capsule, tab pills, card chassis, all chips, BACK
  pill, page arrows, modal panel. Chevrons + arrows are no longer flat: the
  BACK chevron and both page chevrons now draw a dark keyline stroke under a
  bright stroke.
- **ONE radius family.** cards `17`; pills/chips/**arrows**/BACK fully rounded
  (`h/2` — the page arrows were re-rounded from a squarer `m(13)` to `h/2`);
  modal `20`.
- **ONE material.** Single top-left light: bright bevel + one gloss sheen on
  top + bottom-right AO. No extrude (header wordmark stays the clean bevel),
  no flat card (inner-tray variant B), no two-tone gold (single Ramp A).
- **Glow ranking.** equipped card halo > legendary gem > BUY CTA gloss >
  rest. The equipped halo peak was trimmed (22→20) so it stays restrained;
  BUY keeps its outer halo + gloss but the modal scrim guarantees it is the
  brightest gold (below).
- **Cabochon specular FIX (the single biggest quality lift).** The top-left
  specular is now a THIN translucent crescent at `CABO_SPEC_A = 150` (~59%
  alpha), hard-masked to a slim band (larger subtract disc) so the skin reads
  THROUGH it — not the round-1 opaque white slab that ate the parrot. The dome
  is the winning **variant C** body (`30,33,64 → 9,11,30`, airier/crystalline),
  with a faint bottom-right refraction arc and the card-ring-gold bezel. The
  skin's rim-light contrast is pushed ~+20% (`_punch_contrast` boost 28→34,
  `_rim_light` alpha 150→180) so the content out-pops its frame.

### Per-element punch-lists folded

- **atmosphere → B:** central bloom pulled in ~15% (`m(200)→m(170)`) and down
  ~20% in peak (`60→48`) so the card-grid band stays dark; star strata thinned
  to ~0.78× (sparse); darkest vignette bands added at the top/bottom 12%.
- **header → C wordmark** (clean gold bevel, no extrude — unchanged) +
  loud-number capsule now on Ramp A; coin keeps its own cell + gap.
- **tabs → C raised jewel:** active pill = Ramp A + a soft drop into the track;
  inactive labels lifted to a legible muted cream-gold (`190,184,162`, ~58% L)
  with a keyline; chevron edges fixed; even spacing kept.
- **card → B inner tray:** a routed gold hairline inside the bevel; EQUIPPED
  frame thickened to a **2-step bevel** (deep `m(3)` under-frame + bright `m(2)`
  inner lip) + the restrained halo; the 3 bands (cabochon → name → chip) are
  locked.
- **cabochon → C dome + the specular fix** (above).
- **rarity → 8-facet (B):** `facet_gem` rewritten as the octagonal 8-facet
  brilliant (one cut for all 5 tiers), single top-left pip, mystery gem a
  half-step brighter/neutral; tapered thread + node star kept.
- **chips → Ramp A:** single-gradient price; beveled coin + clear gap; LOCKED
  legible numerals; EQUIP/EQUIPPED share the silhouette + edge (EQUIPPED leads
  with a check mark).
- **controls_modal:** dark BACK pill with a gold keyline (NOT filled gold);
  page arrows re-rounded to `h/2` with comfortable tap size; modal scrim bumped
  to ~78%, gem seated on the dome rim, BUY = Ramp A + gloss + larger tap
  (`112×46` vs CANCEL `112×46` but BUY carries glow), CANCEL one value step
  under the panel, title stamped bold.

### Assembly checks (verified by rendering)

- **Cards over the atmosphere-B centre bloom** — bloom was pulled in/down AND
  the card bottom AO was deepened (`m(7)/95 → m(9)/120`) rather than darkening
  the whole sky; card keylines + inner tray survive at vertical centre
  (confirmed in `store@2x.png`, rows 2–3).
- **Equipped frame vs legendary gem** — the equipped sample (OWL) is rare; the
  halo was trimmed restrained so it would not fight a legendary gem if one
  shared a card. Legendary gems (KITSUNE, AURORA STAG) render un-equipped with
  their brighter-than-Ramp-A gold intact.
- **Modal scrim drops the live grid + tab gold** — scrim raised to ~78%
  (`alpha 180→200`); in `modal@2x.png` BUY is unambiguously the brightest gold,
  the grid + tab pill read as dimmed ground.
- **3 card bands fit with padding** — cabochon dome, name and chip sit in
  their lanes with no collisions at true grid scale; the gem seat at the
  top-right corner does not crowd the dome (`detail.png`).
- **Header capsule bottom AO vs tab pills** — capsule bottom (`~m(96)`) clears
  the tab track top (`~m(106)`); no kiss (confirmed in `store@2x.png`).

## Files

- `render_hi.py` — the assembled SS-aware renderer (pure pygame, both-target
  safe).
- `store.png` / `store@2x.png` — full store at 360×640 and 720×1280.
- `modal.png` / `modal@2x.png` — buy-confirm modal.
- `detail.png` — 3 hero cards + the locked chip family (one Ramp-A price chip
  affordable + can't-afford, EQUIP, EQUIPPED — one pill, one edge).
