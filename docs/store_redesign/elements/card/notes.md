# Store — ITEM CARD CHASSIS (round 1)

Element 4 of 8 in the CONSTELLATION store redesign. Scope is the **card chassis
only** — the rounded panel that holds an item. The cabochon dome, rarity gem, and
price/equip chip are owned by other loops, so here they are drawn as **labelled
dashed placeholder boxes** to prove the internal layout, never as finished art.

Render: `render.py` → `round_1.png`. Pipeline reused verbatim from
`constellation_hi/render_hi.py` — author resolution-independent, render at **SS=4**,
ONE smoothscale down (kept at ~1.7× logical here so the cards read large + crisp for
inspection). Pure pygame, both build targets safe.

## What every chassis carries (the brief, all five visible)
- **Lit body gradient** — top (28,30,70) → bottom (12,13,38), gamma-lifted so the
  panel reads as a lit surface, never a flat dark rectangle.
- **DEFINED EDGE** — a dark outer keyline (≈2px pre-downscale, authored wide so it
  survives) drawn UNDER a bright warm-gold top-left bevel. The edge clearly reads
  against the nebula; nothing melts into the bg.
- **Top gloss sheen** — white highlight clipped to the rounded top, one light source
  top-left.
- **Bottom-right contact / AO shadow** — inner occlusion hugging the bottom + right
  inner edges, masked to that corner only.
- **Soft outer drop shadow** — multi-layer, offset down, so the card floats above
  the bg as a tactile object.
- **EQUIPPED state** — a clean gold frame (beveled: deep under-stroke + bright lip)
  plus an additive gold edge halo around the WHOLE card.
- **Strict three-band layout** — CABOCHON lane → NAME lane → CHIP lane, each a
  disjoint rect inset by a uniform pad (`_lanes()`), with a reserved corner-gem
  marker. Generous padding; lanes can never overlap whatever content drops in.

## Variants
- **A · CLASSIC** — the THEME baseline: indigo body, dark keyline under a warm-gold bevel, top gloss, bottom-right AO. The house look the other loops assume.
- **B · INNER TRAY** — same body plus an inset gold hairline frame inside the bevel, reading as a routed tray the content sits down INTO; strongest floating-object edge.
- **C · WARM GLOW** — richer violet-lifted body with a restrained lit top-left corner bloom and a two-step dark keyline (near-black + faint cool rim) for the deepest edge and highest body luminosity.

Each variant is shown as a NORMAL card (top row) and its EQUIPPED treatment (bottom
row) on the shared night-sky bg.
