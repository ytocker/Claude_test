# AURORA STAG — Round 4 (FINAL designer pass · structural rebuild)

**Verdict addressed:** ITERATE — the art-director root-caused that Round 3 still
read as a lyre/wishbone and the dive slung a beam off-body. This was a STRUCTURAL
fix, not a tuning nudge. Round 4 is the last pass in the loop; it ships as-is.

Round 4 stays the ONE ship build exposed as `build_aurora_stag` /
`get_aurora_stag` / `BUILDERS = {"skin_aurora_stag": ...}` (liftable into
`game/animal_skins.py`). Contract unchanged: 64×84 canvas, body (32,44), rack
into the top headroom, 4 poses, procedural-only, WHY-only comments, no live
particles.

Sheet: `docs/animals/aurora_stag/round_4.png` — single build on the game's
BRIGHT-DAY gradient (sky bottom ~(170,220,245)) **and** night, at hero 130px +
40px smooth (level/dive) + 40px NEAREST-neighbor x3 (level + **three** dive
angles −24/−32/−40 for the post-rotation re-check).

## Structural must-fix — every item

1. **Inward V killed entirely.** The old geometry anchored both tines to a low
   inner arc that leaned the beam tips inward toward a shared centre knot — the
   wishbone tell. That arc, its inward late-lean term, and the centre-knot
   anchoring are all gone. No element points inward-down to a midline.

2. **Each antler rebuilt as a SINGLE forward-throwing beam.** `beam_curve(rx,
   ry, fwd, rise)` rises near-vertical off the skull then throws FORWARD over
   the nose (always +x, `fwd * t**1.6` accelerating to the tip) — the forward
   throw is what reads "stag" instead of "lyre". TWO short forward-raked tines
   per beam (branch points `beam[3]` and `beam[5]`) spring off the OUTER/forward
   face and throw the SAME forward+up way (real brow + bez tines), each with its
   own navy rim + chroma fill and a 2px end-star. The two beams are STAGGERED in
   depth — FAR beam roots back/left, stands taller and more upright behind; NEAR
   beam roots forward, sits lower, throws harder over the muzzle — so they read
   as a rack of two distinct beams with a gap of sky between the crowns, not a
   fused plume.

3. **Tip-stars: ≥2px spokes + navy notch.** `_star` rebuilt so each N/S/E/W arm
   is drawn at **2px thickness** off a 3×3 hot-white core, with a 2px hard NAVY
   notch (`notch_from`) on the segment between the star and the beam tip. The
   2px spoke is the survival rule: a 1px spoke collapses under the 40px NEAREST
   downsample and rounds to a blob; a 2px spoke keeps at least one lit pixel per
   arm so the cross still reads as a DETACHED 4-point point after the nearest
   filter and the dive rotation.

4. **Dive fixed.** Geometry re-anchored (NEAR beam rise pulled to 24, root
   forward at `skull_r+3, HCY−3`) so under −24/−32/−40 the beams stay OVER the
   head and the lower beam no longer swings down/right off-body as a loose green
   tail — it terminates in its tip-star, still connected to the skull. Verified
   on the NEAREST x3 dive: both tip-stars and the forward tines stay
   individually legible through the rotation.

## FROZEN (left untouched)

- Chroma-first violet `#7A5CFF` → green `#3DF2C0` saturated beam cores.
- Deep-navy `#1E2A3A` baked halo around every ribbon (day-sky separation).
- Cool-spectrum-only palette (violet↔green; no phoenix pink/gold).
- Clip-safe dive: raw build bbox `rect(17, 0, 47, 66)` across all 4 poses —
  left 17 / right 64 / top 0 / bottom 66, inside the 64×84 canvas (hard star
  cores carry a ≥1px margin off the top/right edges; only the faint glow halo
  kisses the boundary). rotozoom expands the surface on the dive.

**Spectacle constraint:** no live particles — aurora glow + star-points baked
into each of the 4 frames; chroma phase travels the beams across poses, ears
flick on the up-pose.

**API:** single production surface — `build_aurora_stag(wing_angle_deg)`,
`get_aurora_stag` (cached `(frame_idx, tilt_deg)` getter), and
`BUILDERS = {"skin_aurora_stag": get_aurora_stag}` — unchanged.
