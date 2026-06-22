# CONSTELLATION store — CHIP FAMILY (round 1)

Element 7 of 8. The pill-chip product line: the cost (PRICE) chip plus its
sibling states — EQUIP, EQUIPPED, and can't-afford / LOCKED. Rendered headless
at SS=4 then one smoothscale down, per the THEME crispness lever. Pure pygame,
both build targets safe (no numpy, no desktop/browser-only API).

- **Render:** `docs/store_redesign/elements/chips/render.py`
- **Output:** `docs/store_redesign/elements/chips/round_1.png`

## What the sheet shows
- Three **single-gradient gold PRICE ramps** (A / B / C), each at the three
  target values **280 / 1,500 / 7,000**, so the ramps are compared like-for-like.
- The matching **STATES** row: EQUIP, EQUIPPED, LOCKED — all on the exact same
  pill silhouette (fully rounded, h/2) and the same DOUBLE-rim edge finish.
- A large **DEFAULT (ramp A)** showcase row of the price chip at all three
  values, at ship size, so the gold + dark numerals are judged at scale.

## Honoring the locked directive (PRICE chip)
- The price body is **ONE continuous gold gradient**, bright-crown -> deep-amber.
  Authored as an N-stop ramp sampled per row (`vgrad_stops`) — still a single
  smooth ramp, **no two-tone split, no spliced champagne band** (the prior
  two-tone option is gone).
- **Dark deep-brown numerals** (~`(52,28,4)`) for punch, no keyline needed on
  gold.
- A **clean beveled coin** in its own left cell with a **clear gap** (`gapc`)
  before the first digit.
- **Crisp DOUBLE gold rim** (THEME defined edge): dark outer contact keyline
  drawn UNDER a bright top-left bevel.
- **One** diagonal gloss sweep across the upper third.

## Shared finish = one family
`chip_body_stops()` is the single body recipe every chip flows through (drop
shadow, gradient fill, gloss sweep, bottom-right AO, double rim). The states
only change the fill stops + rim colours:
- **EQUIP** — neutral cream-gold (owned, not active).
- **EQUIPPED** — a clean, distinct green with a leading check mark in its own
  cell, so the active state is unmistakable.
- **LOCKED** — cool slate body, light legible numerals, a small padlock in the
  coin cell; same pill + double rim, just dimmed.

## Variants (for the art-director to pick the most premium)
- **Ramp A — Royal Gold:** luminous champagne-touched crown easing to a rich
  saturated amber. Balanced; the safe default.
- **Ramp B — Honey Gold:** tighter hot crown, warmer/deeper foot — the most
  molten-metal read.
- **Ramp C — Burnished Gold:** paler/cooler start ramping to the deepest bronze
  foot; maximum top-to-bottom value travel, most sculpted/dimensional.
