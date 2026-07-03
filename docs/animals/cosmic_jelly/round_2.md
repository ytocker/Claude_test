# COSMIC JELLY — Round 2 (FINAL)

`skin_cosmic_jelly` · LEGENDARY · non-winged. Round-1 verdict was **ITERATE**,
winner **V4 SOLID VOID-CORE**. Round 2 converges to ONE production build that
folds in every directive. Lead read is the day-sky truth test; night hero is
secondary, per the critique.

- Sheet: `docs/animals/cosmic_jelly/round_2.png`
- Build: `docs/animals/cosmic_jelly/cosmic_jelly_skins.py`
  - `build_cosmic_jelly(wing_angle_deg)` — single primary production build
  - `get_cosmic_jelly = _make_prebuilt_skin(build_cosmic_jelly)`
  - `BUILDERS = {"skin_cosmic_jelly": get_cosmic_jelly}` (liftable into
    `game/animal_skins.py` unchanged)

## What changed, per the punch list

1. **Crisp silhouette under the halo.** A darker-violet rim (`RIM_VIOLET`) is
   stamped as a defined ellipse FIRST, the additive violet halo blooms OUTSIDE
   it, then the rim is re-stamped over the inner halo edge. The bell now keeps a
   hard lip against noon blue — the bloom adds light around the edge instead of
   dissolving it.
2. **Star-diadem crest (stolen from V5).** ONE dominant white-gold spike-star on
   the dome apex + two tiny gold flankers break the top silhouette like a crest.
   Kept to a single high-value point so it never competes with the core; it
   grows/brightens on the billow and shrinks on the contract so it pulses with
   the body.
3. **Jelly, not planet.** The body is now a solid void LOWER mass (darkened
   under-belly) with a brighter, see-through UPPER cap (`CAP_LIGHT`, additive,
   clipped to the dome) — ~18% lighter glass over the void reads as gelatinous,
   not opaque.
4. **Breathing white core.** Core radius 4→7 and peak 170→240 across
   contract→billow; the swirl arms converge on it so it reads as a galactic
   heart pumping. Swirl drifts ~26°/frame.
5. **Five constellation tentacles, joined.** Locked to 5 strands, each a faint
   1px joining star-line with alternating cyan/magenta/white nodes and a brighter
   glowing TIP-NODE. Roots fan wider on the billow (clean separation) and bunch
   tight + short on the contract; they start just below the rim lip so the hard
   edge never swallows the strand roots.
6. **Two-hue cold swirl.** Cyan + a BLUE-biased magenta (`MAGENTA = 190,90,255`)
   over the white core — cold and distinct from the warm phoenix. Verified the
   dark void-core holds value contrast against the noon-sky blue panel.

## Legendary-spectacle constraint

No live particles — nebula glow, swirl, stars, diadem and core are all baked
into the 4 pose frames. The pulse + drift come purely from frame-to-frame
geometry/core/tentacle variation.

## Contract (unchanged)

64×84 SRCALPHA · bell at (32,44) · tentacles trail below · 4 poses
(`_WING_ANGLES` reinterpreted as the jelly pulse) · procedural-only · WHY-only
comments. The day-sky NEAREST x3 truth panel leads the sheet (level + dive,
all 4 frames); night hero + film-strip are secondary.
