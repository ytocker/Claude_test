# ATMOSPHERE — night-sky canvas (round 1)

The backdrop every store card sits on. Authored at SS=4 (1440x2560) and
downscaled once to 360x640 per the THEME crispness lever, so the multi-stop
nebula stays band-free and every hairline / sparkle resolves clean.

## Palette (locked, from THEME)
- **Nebula bg stops:** (6,7,24) -> (11,11,40) -> (18,16,58) -> (26,20,72) ->
  (14,12,46) — the locked indigo->violet multi-stop ramp.
- **Central bloom:** `NEBULA_GLOW (70,60,150)` violet haze, sat ~0.42 of the
  height (over the breathing room above the grid), edge + corner vignette.
- **Constellation gold:** thread tint (208,182,118); node-star core
  (255,234,180) with a hot (255,250,226) pip.
- **Star tints:** warm white (255,252,240), cool blue-white (220,226,255),
  warm amber (255,240,210) — picked per star for subtle colour variety.

## Structure (shared across variants)
- **Nebula:** `multistop_v` gradient + a SINGLE smooth `radial_bloom` field
  (per-radius alpha falloff, alpha-composited) — NOT stacked additive layers,
  which banded into ring-steps and blew the core to white. Result is a calm
  violet haze, no banding, never white.
- **Three-strata starfield:** far dust (tiny/dim) -> mid stars -> near stars
  (larger/brighter, each with a faint halo) for real depth.
- **4-point sparkle stars:** long axis + a fainter diagonal cross + a tight
  glow + hot core — the premium twinkle accents.
- **Constellation field:** two chains + one bridge of tapered gold hairlines
  (each segment alpha-eased bright-at-middle, faint-at-vertices so it reads as
  a drawn-on thread, not a stray line) with a glowing node star at each vertex.

## Variants (the art-director picks the restraint level)
- **A balanced (hero):** bloom 82 / density 1.0 / 14 sparkles / thread 46 —
  the reference balance: luminous heart, readable card lane, calm threads.
- **B deep + calm:** bloom 54, sparse stars (0.78x), thinner faint threads —
  maximum card legibility, deepest/quietest sky.
- **C luminous:** bloom 120, dense stars (1.18x) + 20 sparkles, wider bloom —
  the most atmospheric / show-off backdrop (watch it doesn't fight the cards).
- **D constellation-forward:** brighter, thicker gold threads + stronger node
  stars on a calmer star bed — leans into the CONSTELLATION motif.

## Helpers reused (constellation_hi DNA)
`multistop_v`, `soft_glow` (point lights), the `SS`/`m()` metric pipeline,
`game.draw.lerp_color`, `game.hud._font` + `_GOLD_BRIGHT`, the locked
`BG_STOPS` + `NEBULA_GLOW`. New: `radial_bloom` (smooth single-field bloom).
Pure pygame, both build targets safe.
