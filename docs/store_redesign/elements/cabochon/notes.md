# Glass cabochon — round 1

The domed glass well that showcases each item's procedural thumbnail, built per
the locked `THEME.md` recipe and the `constellation_hi/render_hi.py` pipeline
(SS=4 author canvas, one `smoothscale` down, shared palette + `draw_bg` +
`soft_glow` + the `_punch_contrast` / `_rim_light` skin treatment). Pure pygame,
both build targets safe.

Recipe checklist, all present:
- Dark domed glass body, `CABO_LO -> CABO_HI`, radial dome (lit centre, near-black
  rim) so it reads as a real dome, not a flat disc.
- Skin set INSIDE the well, contrast-punched + top-left **rim-lit** so the
  silhouette out-pops the dome — fixing the prior inverted hierarchy. Clipped to
  the well so nothing spills past the bezel.
- TRUE top-left crescent specular (lit disc MINUS an offset disc) — only the lit
  arc survives, never a false full ring.
- Faint bottom-right refraction arc (curved interior shadow).
- Inner vignette so content settles into the well.
- Thin warm-gold bezel with a DEFINED edge: dark contact keyline outermost, fine
  warm-gold rim, inner pale glint, and a bright glass kiss on the upper-left arc.

Sheet layout: a hero row of the 3 dome/specular/rim variants on `skin_bluegold`,
a proof grid of variant A across 4 very different skins (macaw / phoenix / dragon
/ owl), and a card-scale-vs-hero pair on `skin_phoenix` to confirm it survives at
the real grid size (`R_DISC=23`).

## Variants
- **A  balanced glass** — moderate dome depth, mid rim light + crescent; the
  even, dependable read intended as the grid default.
- **B  deep dome + hot rim** — deepest near-black glass, strongest rim light and
  vignette; maximum "under glass" depth and silhouette pop for hero/legendary use.
- **C  bright crystal** — lighter glass body, hottest broad specular, softer rim;
  airier, more crystalline, lets pale skins (owl) read without crushing.

Saved: `docs/store_redesign/elements/cabochon/round_1.png`
