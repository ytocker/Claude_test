# CACTUS PIÑATA — round 2

Round 1 got `VERDICT: ITERATE`: in grayscale it read as a BOLT (round cap on a
ribbed shaft) and the trunk fused into Pip's parcel. Round 2 fixes the read by
SHAPE, not colour. Kept: the top-heavy vertical concept, the sombrero charm, the
green/straw palette + flower dots.

## What changed (punch list)

1. **Carved NEGATIVE SPACE between trunk and arms (#1).** Arms are now drawn as
   an L (low horizontal stub → tall vertical riser) starting OUTSIDE the trunk
   wall by a `NOTCH` (4px). After the trunk + bands are drawn, `_carve_notch`
   punches a TRANSPARENT vertical slot between each trunk wall and its arm riser,
   so the gap is guaranteed alpha — the house outline traces both edges and the
   "trunk + two raised arms" survives pure black. Arms dropped LOW (stub at
   BCY+4) with an air gap between the riser tops and the hat brim.
2. **Separated the cactus from the parcel.** The trunk now TERMINATES in a
   defined rounded BASE band (`is_base`: wider, fully rounded, no fringe) at
   BCY+18, leaving ~12px of clear air above the canvas floor where the game
   composites the parcel — so the player reads "cactus, THEN gift". The trunk
   green was pushed cooler + more saturated (`#4ABA56` / `#267032`) to pull it
   away from the parcel's warm brown so they don't fuse.
3. **Pulled the arms out from under a NARROWER brim.** Sombrero brim radius
   dropped 17 → 11; arms reach `ARM_SPAN`=15 from trunk centre. The widest point
   of the silhouette is now the ARM SPAN, not the hat (confirmed in grayscale).
4. **Sway is a FRINGE FLUTTER, not a top-block lean.** `_band_flutter` is a
   travelling sine whose argument mixes band row and the phase clock, so bands
   ALTERNATE direction and a wave runs down the trunk. The sombrero tilt is kept
   small (±8°/±3°). Phases 1 and 3 carry OPPOSITE micro-leans, hat tilts, and
   band-flutter signs, so frame 1 ≠ frame 3 and the loop reads
   left → mid-right → right → mid-left (a continuous orbit, not a 2-pose blink).
5. **Reduced to 4 CHUNKY crepe bands** (was 6 thin), with stronger hi/lo value
   contrast (`#4ABA56` vs `#267032`) so the bands read as stacked papier-mâché
   rings, not screw threads.

## Verdict checks

- **GRAYSCALE silhouette reads as a two-armed saguaro, NOT a bolt.** The
  play-size grayscale strip shows a central trunk with two raised arms flanked
  by dark notch gaps, a small hat narrower than the arm span, and a defined dark
  rounded base. No round-cap-on-ribbed-shaft read.
- **Cactus is visually separate from the parcel.** Rounded base + air gap +
  cool-green vs warm-brown hue split → two distinct objects, not a mushroom on a
  stick.
- **Frame 1 ≠ frame 3.** Verified: phase 1 lean +0.9 / hat +3° / flutter
  `[1.7, 1.06, -0.39, -1.54]` vs phase 3 lean −0.9 / hat −3° / flutter
  `[-1.7, -1.06, 0.39, 1.54]` — exact opposites; 733 pixels differ between the
  two frames.

## Contract (unchanged)

64×84 SRCALPHA; dominant trunk mass centred at (BCX,BCY)=(32,44); rounded base at
BCY+18 leaving ~12px air for the composited parcel. `build(wing_angle_deg) ->
Surface`; cached getter via `game.animal_ufo._make_prebuilt_skin`. Reuses
`parrot._add_outline` / `parrot._aaellipse`. Procedural pygame only — no raster
assets, both targets.

## Render

`SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python docs/pinata/cactus/render.py`
→ `docs/pinata/cactus/round_2.png` (DAY + NIGHT gameplay frames + 3x / play-size
/ grayscale reference column).
