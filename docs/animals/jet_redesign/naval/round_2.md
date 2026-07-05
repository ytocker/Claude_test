# JET FIGHTER redesign — NAVAL INTERCEPTOR (`naval`) · Round 2 (production)

**Winner converged:** v3 · **JOLLY ROGERS**. Round 1's five takes collapsed
to ONE ship-ready production build. Sheet:
`docs/animals/jet_redesign/naval/round_2.png` (hero 130px + 40px smooth +
40px NEAREST x3 level/dive, on DAY · NIGHT · DAY-WARM-PILLAR, plus a 4-frame
afterburner-pulse strip).

## Punch list — every note addressed

1. **Continuous gold leading-edge rail (was 2-3 disconnected dots).** The
   gold is now a single unbroken 1px rim traced along the FULL leading edge
   of each wing AND the top of each tail fin. The wing-leading-edge and
   tail-top coordinates are captured during airframe draw, then the rail is
   drawn over them, so the gold literally describes the planform shape at
   40px instead of capping the tips. One brighter pixel at each wing root is
   the only catch-light.
2. **Strengthened baked self-rim, proven on a DAY warm-sandstone pillar.** A
   1px cool light-grey (`176,188,206`) edge runs the top/nose contour of the
   fuselage, INSIDE the house dark outline. The sheet's third panel puts the
   jet over the actual game DAY sandstone palette
   (`stone_light/mid/dark/accent` from `game/biome.py`) so the dark airframe
   is shown overlapping warm stone — it holds as one crisp mass and never
   melts in. `/tmp` magnified 40px-on-stone read confirms the top edge stays
   keyed-light against the warm column.
3. **Cool canopy is the single non-gold cool accent.** One cyan
   (`78,150,196`) bubble, drawn identically every frame — colourblind-clean
   against the warm burner + the gold rail (three separable hue/value
   accents). Constant across all 4 frames (proven in the pulse strip).
4. **Twin tails held WIDE; swing-wing never occludes them.** Fins spread to
   ±13px; wings sit at mid-sweep (0.45) so the wingtip tucks well forward of
   the fins. At every pose the two tails read as two — verified across the
   4-frame strip.
5. **Afterburner pulse changes the burner footprint legibly.** Flame length
   swings 13→24px on the 84px canvas (adjacent frames 13→20px = pulse
   0→0.67), i.e. **~3.3px** footprint change between adjacent frames at the
   40px gameplay scale — comfortably over the 2px legibility floor on the
   dark body.
6. **Restraint.** ONE dark mass, ONE gold structural rail, ONE cool canopy,
   ONE warm twin burner. No modex, no chevrons, no skull decal — all removed.
7. **NAVY base (not pure sea-black).** Deep naval blue (`32,38,58`). Pure
   black crushed to a featureless hole on night and swallowed its own dark
   outline; navy holds the silhouette on night while staying dark enough to
   sit as one mass against warm day sandstone — the two hardest backgrounds.

## Contract held (lifts into `game/animal_jet_fighter.py`)
- `build_naval(wing_angle_deg) -> 64×84 SRCALPHA`, fuselage mass centred at
  **(32,44)** (fixed 14px collision circle there; wings/stabs span wider).
- Drawn **nose-RIGHT, upright, level** — **no baked rotation/flip**; the game
  applies the inverted nose-up presentation later.
- 4 base poses `_WING_ANGLES=(50,20,-10,-40)` animate as an **afterburner
  pulse** (+ ±1px nose pitch); glow baked into the frames, no live particles.
- `get_naval = _make_prebuilt_skin(build_naval)`;
  `BUILDERS = {"skin_naval": get_naval}` (single production build, one key).
- Procedural only; baked self-rim; both targets green; WHY-only comments.

## Render
`python docs/animals/jet_redesign/naval/_render_sheet.py` → wrote
`round_2.png` (1024×418), headless SDL-dummy. No errors.

Not wired into `game/`. Converged single production build — STOP.
