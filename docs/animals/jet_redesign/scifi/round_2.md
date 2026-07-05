# SCI-FI ENERGY FIGHTER jet redesign — Round 2 (final convergence)

Concept: `scifi`. Art-director picked winner **v5 · GOLD SOVEREIGN** (faceted
diamond hull). Round 2 converges to ONE ship-ready production build that lands
the design decisively as cool, hard-edged neon TECH — away from the warm
DRAGON/PHOENIX legendaries.

Sheet: `docs/animals/jet_redesign/scifi/round_2.png`
(single refined build: hero 130px + 40px NEAREST x3 level/dive on DAY **and**
NIGHT skies — the honest gameplay read).

## Contract held (matches game/animal_jet_fighter.py)
- Single production build `build_scifi(wing_angle_deg) -> 64×84 SRCALPHA`,
  hull mass centred (32,44).
- Drawn NOSE-RIGHT, UPRIGHT, LEVEL — no baked rotation/flip (game spins it
  inverted nose-up later).
- 4 poses = baked plasma pulse (`_pulse`) + a 1-frame bright-seam CHARGE sweep
  (`_charge_frame`, on the −10° throttle peak) + ±1px pitch on the plasma only.
  The hull SILHOUETTE verts are frame-stable, so the baked outline is identical
  frame-to-frame and never shimmers into noise.
- All glow baked per frame (tight rim, cyan/gold seams, core bloom) — no live
  particle system, both build targets render identically.
- `get_scifi = _make_prebuilt_skin(build_scifi)`;
  `BUILDERS = {"skin_scifi": get_scifi}`.
- Procedural only; WHY-only comments.

## Punch list — every note addressed
1. **Cooled the palette.** Hull is now PLATINUM / ICY-CYAN as the primary
   (steel-blue cut crystal + `_CYAN` 60,210,255 seam-piping, borrowed from v1).
   Gold is demoted to a SECONDARY accent: only the plasma core and ONE hero
   keel seam carry warm gold. Pulls it decisively to cool neon TECH.
2. **Nose-direction resolved at 40px.** The diamond is now ASYMMETRIC — the
   front point is ~15% longer and narrower, the rear is BLUNTED (cropped corner,
   not a point), AND a single asymmetric COCKPIT facet (with a cyan glint) sits
   forward of the spine. "Forward" reads unambiguously, including in the
   inverted night-dive pose (shown on the sheet).
3. **Full aura → tight rim-glow.** Replaced the soft full aura with a TIGHT 1px
   baked self-rim that HUGS the hull plus a small dense core bloom; seam bloom
   underlays were narrowed to +2px so the faceted edges never soften.
4. **Stronger interior facet value contrast (~20%).** Four-step value ramp
   (`_HULL_LO` → `_MID` → `_HI` → `_PEAK`) so the cut planes read on VALUE alone
   under a bright day sky, carrying the tech read on value, not hue.
5. **Single brightest plasma core.** One white-hot core (white centre inside a
   cyan-hot ring inside a small gold ring + tight gold bloom) is the
   unambiguous brightest pixel cluster by a clear margin; the eye locks at 40px.
6. **Animated baked tell, stable outline.** Core pulse across the 4 frames + a
   1-frame bright-seam CHARGE sweep on the throttle peak; hull outline identical
   every frame.
7. **Cool near-white self-rim.** Baked 1px rim in cool near-white (`_RIM`
   224,244,255 — NOT warm), brightest on the top/leading edges to match the
   shipped art's upper-left light direction (crown highlight + top sheen),
   composited as an outer RING so it never paints over the interior.

## Render notes
- Day panel confirms the geometry survives a bright sky on value (facets stay
  crisp when the neon is washed flat); night panel confirms the neon + core
  tell pops on black. Dive pose on both confirms the forward read.
- NEAREST x3 is the honest gameplay truth test; smooth hero is reference only.

Single converged build, ship-ready, not yet wired into `game/` — that's the
orchestrator's call once the winner is signed off.
