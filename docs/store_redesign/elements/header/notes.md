# Store HEADER — wordmark + balance capsule (round 1)

Sheet: `docs/store_redesign/elements/header/round_1.png`
Render: `docs/store_redesign/elements/header/render.py`

The header is the store's top chrome: the **"STORE" gold wordmark** and the
**coin-balance capsule** (real value 14,250).

## Pipeline / cohesion
- Imports the locked reference pipeline (`constellation_hi/render_hi.py`) directly
  — same `SS=4`, same palette, fonts, glow caches, and primitives (`vgrad`,
  `bevel_rim`, `top_sheen`, `contact_shadow`, `coin_glyph`, `gradient_text`,
  `_stamp_bold`, the night-sky `draw_bg`). This element can't drift from the theme
  because it draws with the theme's own code.
- Everything authored resolution-independently, rendered oversized, one
  `smoothscale` down. Pure pygame, no numpy / no target-specific API — both build
  targets safe.

## Wordmark treatments (all: clean gold bevel, NO chunky extrude)
- **A — Clean Royal Bevel.** One warm-gold vertical gradient mapped to the glyph's
  true cap→baseline extent, a fine dark keyline (defined edge), a single thin
  cap-edge specular glint, one soft contact shadow. The safe premium baseline.
- **B — Rimmed Emboss + Gloss.** A is deepened: a top-left CONTOUR emboss (lit
  silhouette minus body — lights only the protruding rim, never the flat cap bars,
  so no white blocks), a dim interior bottom shadow for a raised-plate read, and a
  hairline rust outer rim (theme red accent) outside the dark keyline. Glossier,
  slightly more dimensional, still crisp.
- **C — Bevel + Constellation Flourish.** A's clean bevel plus a tasteful tapered
  gold constellation arc with three node stars above the word and two 4-point
  sparkles flanking it — echoes the background constellation language without
  making the type busy.

## Balance capsule (shared across all tiles + a zoom tile)
- Recessed deep-amber jewel well (top-darker so it reads sunken), defined edge =
  dark contact keyline UNDER a bright top-left `GOLD_PALE` bevel, one top gloss
  sheen.
- Beveled `coin_glyph` in its OWN left cell with a soft seat glow; a guaranteed
  device-px gap (`m(18)`) before the first digit, plus a faint warm-gold cell
  divider — the coin never touches the number.
- LOUD gradient-gold number (`14,250`) faux-bolded with a dark keyline for punch —
  it's the money screen, so the number is the prominent element.
- Zoom tile shows the capsule large (judge coin/gap/number/edge) and again at the
  live header size to confirm it holds up.

## Spacing / balance
- Wordmark baseline sits high; capsule centered well below it — clear vertical gap,
  no collision in any tile. Both are horizontally centered as the live header.

## Variant one-liners
- A: clean royal gold bevel — single specular + keyline + soft contact shadow.
- B: rimmed emboss — top-left contour highlight + rust rim + interior shadow, glossier.
- C: A plus a tasteful constellation arc + flanking sparkles flourish.
- Capsule: recessed jewel-gold well, beveled coin in its own cell, clear gap + divider, loud gradient number.
