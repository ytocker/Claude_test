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

## Files

- `render_hi.py` — the SS-aware renderer (pure pygame, both-target safe).
- `store.png` / `store@2x.png` — full store at 360×640 and 720×1280.
- `modal.png` / `modal@2x.png` — buy-confirm modal.
- `detail.png` — 3-card detail zoom (glass dome / gem facets / chip / thread).
