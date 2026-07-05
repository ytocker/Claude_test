# Concept: THE BIO-JELLYFISH — `skin_ufo` redesign, round 1

A single concept (1 of 5 independent UFO redesigns). The organic, "it's alive"
alien craft — a War-of-the-Worlds deep-sea jelly. The brief required it to read
INSTANTLY as its own distinct thing at ~40px, because the prior attempt died on
indistinct domed saucers.

## The read (what it is at 40px)
A floating space jellyfish: a smooth translucent purple DOME BELL up top with a
fringed lower margin and **3 thick wavy TENDRILS** splaying below it. Nothing
else in the set is soft/organic, so the tendrils + scalloped fringe are the
silhouette tell. The bell mass sits clearly above centre (apex 16px above BCY),
so it dominates the top half and stays the main read; the three tendrils hang
below and cradle/frame Pip's parcel rather than hiding behind it.

## Silhouette + palette
- **Bell:** a translucent vertical-gradient gel dome — bright `#B98CFF` up top
  deepening to a `#5E3AA8` purple core low in the bell, with a near-white
  `#E8D9FF` dome-highlight cap and a hot specular pip on the crown. Drawn a
  little see-through (denser toward the core) so it reads as gelatinous volume.
- **Rim keyline:** a bright `#D4BAFF` arc over the top of the dome + a brighter
  rim line above the fringe. This high-value lip is what holds the translucent
  body's hard shape against a **bright DAY sky** (where a soft purple gel would
  otherwise wash out) — the day read leans on rim-value contrast, the night
  read on the dome + bio bloom.
- **Fringe:** a scalloped lower margin (overlapping soft lobes, `#5E3AA8`), the
  organic edge no saucer concept has. It flares DOWN on the expanded frame and
  tucks UP on the contracted frame.
- **Tendrils:** 3 chunky `#7A4FD0` strands (with a `#54329C` shade side for
  round volume), roots spread wide across the fringe (BCX ±11) so they read as
  three SEPARATE legs; centre strand hangs longest (classic jelly profile).
- **Bioluminescent dots:** `#5EF2D0` core → `#8CFFE0` hot centre, baked as tight
  additive halos. Two on the dome crown (the alive "glands") + one per tendril
  TIP. Night lets these bloom; day keeps them as small high-value pips.

## The motion tell — squash/stretch pulse (the whole point)
No wings, no live particles. The bell PULSES like a real jelly propelling
itself, mapped from `_WING_ANGLES=(50,20,-10,-40)` → phase 0..3 via `_PULSE`
`(rx_mul, ry_mul, fringe_drop)`:

| frame | wing° | bell shape | fringe | meaning |
|-------|-------|-----------------------|--------|------------------------|
| 0 | 50 | **tall-narrow** (0.84×w, 1.18×h) | tucked up | most contracted (the push) |
| 1 | 20 | mid (0.94×w, 1.05×h) | small | relaxing |
| 2 | -10 | **wide-flat** (1.16×w, 0.84×h) | flared down | fully expanded |
| 3 | -40 | mid (1.02×w, 0.96×h) | mid | recovering |

The bell apex stays anchored near the top while the centre + fringe travel, so
the crown holds in place and the body squashes from a fixed point — exactly how
a jelly contracts. The width/height swap is large (0.84→1.16 on width) so it
reads at 40px as a clear SHAPE change. It survives grayscale (see the colorblind
strip): the silhouette alone goes tall→wide→tall, no glow needed.

**Tendril lag:** the strands' sway phase trails the bell pulse by one step
(`_TENDRIL_LAG=1`), so when the bell snaps contracted the tendrils are still
drifting out from the previous expansion — the slight lag that sells organic,
inertial motion. Outer two sway counter-phase to the centre for non-uniform,
lifelike drift.

## Tendril-legibility risk at 40px + how I solved it
The first pass put a ROW of bioluminescent dots along the fringe AND fat tip
dots, all with wide halos. At true play-size those additive halos merged into a
single aqua BAND across the middle that cut the body in half and swallowed the
three tendrils into mush — the exact failure mode the brief warned about.

Fixes:
1. **Killed the fringe bio-band.** Bio-dots now sit only on the crown (2) and
   the tendril TIPS (3) — the tips double as strand-tells so the eye counts
   three legs even when the mid-sections are faint.
2. **Tightened every halo** (`halo` 1.8–2.2, was 3×) so adjacent dots never
   bleed together.
3. **Rebuilt tendrils as stamped graduated round dots** (≈3px fat root → ≈1px
   tip) instead of thin polylines, so each strand stays a solid tapering worm
   that survives the downscale rather than a hairline that vanishes.
4. **Spread the roots wider** (BCX ±11) and lengthened them (30/36/30px) so the
   three legs read as separate at gameplay scale.

## Contract compliance
- 64×84 SRCALPHA, `BCX,BCY=(32,44)`, `DY=12`; bell mass centred and above
  centre; tendrils extend below the 14px collision circle without shifting the
  bell read.
- `build(wing_angle_deg)` returns the upright Surface; 4 squash/stretch frames
  driven by `_WING_ANGLES`; NO baked rotation (velocity tilt applied later).
- Procedural pygame only; reuses `game.parrot._add_outline` / `_aaellipse`;
  mirrors the `_make_prebuilt_skin` getter + additive-glow pattern from
  `game/animal_ufo.py`.

## Files
- `build.py` — `build(wing_angle_deg)` + palette + pulse/tendril/fringe/bio
  helpers.
- `render.py` — boilerplate driving `_gameplay_lib.render_concept_sheet`.
- `round_1.png` — DAY gameplay | NIGHT gameplay | reference (3x / play-size /
  grayscale). The two gameplay frames are the verdict.
