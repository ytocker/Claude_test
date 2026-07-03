# AURORA STAG — Round 2 (v4 LYRE BEAMS → single production build)

**Verdict addressed:** ITERATE on v4 LYRE BEAMS. Round 2 converges to ONE
ship-ready design exposed as `build_aurora_stag` / `get_aurora_stag` /
`BUILDERS = {"skin_aurora_stag": ...}` (liftable into `game/animal_skins.py`).

Sheet: `docs/animals/aurora_stag/round_2.png` — the single build composited on
the game's BRIGHT-DAY gradient (sky bottom ~(170,220,245)) **and** night, at
hero 130px + 40px level/dive (smooth and NEAREST-neighbor x3).

## Punch list — every item

1. **Chroma-first day read.** The beam MASS is now saturated aurora, never
   near-white: `_aurora_ribbon` fills the core by blending violet `#7A5CFF`
   ↔ green `#3DF2C0` only. Pure white is reserved for the two tip-stars and a
   single 1px hot centerline (`hot=True`, drawn only where the core is ≥3px).
   Verified on the 40px frames over the bright-day gradient panel — the crown
   keeps a violet/green read, not a white smear.

2. **Deep-navy contrast halo.** Every ribbon segment first lays down a
   `#1E2A3A` navy line 3px wider than the core (`w + 3`) before the chroma
   core. This dark rim separates the glow from a light sky in every biome —
   the day-sky insurance — and is baked into the frame.

3. **One forward brow-tine per beam (stag, not lyre).** Exactly one short tine
   low on each arc (off `beam[2]`), jutting forward/up off the outer face of
   the beam so it reads as an antler tine rather than more of the arc. One
   each, no more.

4. **Tip-stars protected as the signature.** `_star` rebuilt as a crisp 4-point
   star: tight white arms + a hot white core, a 1px colored bloom one pixel
   out from each arm, on a small colored halo. Crown tips are size-4. They
   survive the rotated dive frame (checked in the NEAREST x3 dive read).

5. **Held negative gap.** The first cut's inward sweep closed into a ring. The
   inward lean is now CAPPED (`inward = 4.5 * max(0, t-0.6)/0.4`) so each tip
   ends ~4px off the midline — the two beams splay apart at the crown with a
   clear ≥2px gap and two distinct tip-stars.

6. **Canvas-clip safe.** Belly pulled to 13px and the arc apex shape adjusted;
   all 4 base frames have content bbox right=64 / left=15 (symmetric, inside
   the 64px width) and bottom=66 inside the 84 headroom. Rotozoom on the dive
   frame expands the surface, so the tips never clip.

7. **Coherent ripple.** The shimmer is a smooth `0.5 - 0.5*cos` violet↔green
   phase that slides up each beam by `phase = f * 0.5` across the 4 frames — a
   chroma wave travelling the beam, not per-pixel jitter — plus the existing
   ear-flick on the up-pose.

8. **Stayed cool full-spectrum.** Palette is violet↔green only; the pink/gold
   accents from the round-1 v3/v4 tip-stars are gone, so it never collides
   with the phoenix.

**Spectacle constraint:** no live particles — aurora + star-points baked into
each of the 4 frames.

**Contract:** 64×84 canvas, body (32,44), rack into the top headroom, 4 poses,
procedural-only, WHY-only comments — unchanged.
