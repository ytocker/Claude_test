# CONSTELLATION store — TAB BAR (round 1)

`render.py` → `round_1.png`. Headless SS=4 (1440×2560 → smoothscale to
360×640), reusing `constellation_hi/render_hi.py` wholesale (`vgrad`,
`bevel_rim`, `gloss_sweep`, faux-bold type, the nebula bg + starfield) so the
strip is the same screen DNA as every other element. Pure pygame, both targets
safe.

## Shared language (identical across all three variants)
- **Defined edge per THEME:** a recessed dark gradient **track** with a dark
  outer keyline UNDER a faint gold inner hairline, plus an inner top shadow so
  the well reads sunken. The strip is one delineated object, nothing floats.
- **Inactive tabs:** muted lilac-grey type with a tight dark keyline, no fill —
  clearly on a lower/recessed plane than the active pill.
- **Even spacing:** equal-width cells with a symmetric inner margin; the active
  pill is inset inside its cell. No tab hugs the track edge.
- **Overflow `< >`:** chunky beveled gold chevrons in faintly recessed round
  nubs sitting just OUTSIDE the track (so no tab crowds them). Both lit here —
  PARROTS pages back left, SHOES/HATS/SHADES wait off the right.
- **Lane scrim:** a soft feathered dark band behind each strip (mirrors the
  header's legibility band in render_hi) so pills read against a controlled
  ground over the central nebula bloom.
- A **true-store-scale** row at the bottom proves crispness at the real ship
  size, not just the blown-up previews.

## Variants (only the active-pill finish differs)
- **A · RICH WARM GOLD** — the locked price-chip gold: single bright-crown →
  deep-amber ramp, one gloss sweep, dark contact keyline + bright top-left
  bevel, dark-brown bold text. Safest, most cohesive with the gold furniture.
- **B · CHAMPAGNE CROWN** — a pale champagne band over the top ~46% atop the
  amber base, wider bright bevel; brighter, more festive/candy-premium read.
- **C · RAISED JEWEL** — a soft drop shadow into the track lifts the pill onto a
  higher plane, plus a double gold rim (dark contact + bright inner hairline)
  echoing the coin/balance-capsule language. The most tactile "pressed up" read.
