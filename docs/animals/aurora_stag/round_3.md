# AURORA STAG — Round 3 (final pass · minimal must-fix)

**Verdict addressed:** ITERATE — apply ONLY the art-director's minimal must-fix
list; keep palette / halo / gap / clip FROZEN, then stop. Round 3 stays the ONE
ship build exposed as `build_aurora_stag` / `get_aurora_stag` /
`BUILDERS = {"skin_aurora_stag": ...}` (liftable into `game/animal_skins.py`).
Contract unchanged: 64×84 canvas, body (32,44), rack into the top headroom, 4
poses, procedural-only, WHY-only comments, no live particles.

Sheet: `docs/animals/aurora_stag/round_3.png` — single build on the game's
BRIGHT-DAY gradient (sky bottom ~(170,220,245)) **and** night, at hero 130px +
40px smooth (level/dive) + 40px NEAREST-neighbor x3 (level + **three** dive
angles −24/−32/−40 for the post-rotation re-check).

## FROZEN (left untouched)

- Chroma-first violet `#7A5CFF` → green `#3DF2C0` saturated beam cores.
- Deep-navy `#1E2A3A` baked halo around every ribbon (day-sky separation).
- The ≥2px negative crown gap between the two beams (inward lean still capped).
- Clip-safe dive: raw build bbox `rect(17, 0, 47, 66)` — left 17 / right 64 /
  bottom 66, inside the 64×84 canvas; rotozoom expands the surface on the dive.
- Cool-spectrum-only palette (violet↔green; no pink/gold).

## Must-fix — every item

1. **Brow-tine re-aimed → horns flip to antlers.** The old pair pointed
   inward/down toward the centre knot and read as a lyre/wishbone. Each tine is
   now a discrete stubby fork (~7px) thrown FORWARD (toward the nose, +x) and
   UP off the OUTER face of its beam — both leaning the same forward way, never
   mirrored inward — with its own navy rim + chroma fill (`_aurora_ribbon(...,
   3, phase, hot=False)`) and a small 2px end-star. That outward forward fork is
   the "stag" tell.

2. **Tip-stars survive 1×.** `_star` rebuilt from a rounded blob to a true 4px
   N/S/E/W cross: single-pixel spokes off a 2px hot-white core, ringed by the
   1px chroma bloom and the soft halo. A hard 2px **navy NOTCH** (`notch_from`)
   is punched on the segment between each star and the beam tip, so the star
   reads as a discrete DETACHED point at 1× instead of fusing into the beam.

3. **Dive legibility re-check.** The tine base anchor was biased higher on the
   arc (`beam[4]`, was `beam[3]`) so the dive rotation swings the lower tine
   clear of the body instead of burying it. The crown star is seated a hair
   down the final segment (`tipy + 5`) so its north arm clears the canvas top.
   Verified on the NEAREST x3 dive at −24/−32/−40: the forward tine and BOTH
   tip-stars stay individually legible through the rotation.

**Spectacle constraint:** no live particles — aurora glow + star-points baked
into each of the 4 frames.

**API:** single production surface — `build_aurora_stag(wing_angle_deg)`,
`get_aurora_stag` (cached `(frame_idx, tilt_deg)` getter), and
`BUILDERS = {"skin_aurora_stag": get_aurora_stag}` — unchanged.
