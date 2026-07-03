# JET redesign — AEROBATIC TEAM JET · Round 2 (SHIP convergence)

**Winner:** v1 · BLUE ANGEL (solid near-black navy body + ONE dominant gold
spear). This round converges the five round-1 explorations down to a SINGLE
production build per the art-director punch list.

## Punch list — how each note was addressed

1. **Gold spear is the single dominant graphic.** The spear is now ONE
   uninterrupted tapering wedge polygon — nose-cap → spine → tail — drawn as a
   single filled shape (no thin spine *line* plus separate nose/tail bits).
   It is widened ~50-70% over round 1 (a 10px-wide nose shoulder tapering to a
   point at the tail) so it resolves as ONE bold diagonal at 40px.
2. **Gold wing leading-edges dropped.** The competing second gold mass on the
   delta is gone. The wings carry value-only shading (dark underside, lit top
   facet, dark leading-edge line). The body is now almost pure navy — the spear
   is the only gold tell.
3. **Baked cool self-rim on the navy body.** A thin cool light edge
   (`_BA_RIM`) traces the upper fuselage chine and the TOP wing leading edge
   (top-right per the skin light direction); the bottom wing gets a fainter
   hint so the light stays directional, not a full outline. The silhouette now
   holds on the night sky without relying on the gold.
4. **Burner cool and small.** `_burner` pulls flame length, halo radius, and
   glow alpha down ~20% from the fighter burner, and the plume is cooled to
   blue (`outer=(56,104,224)`). Gold owns the focal hierarchy.
5. **40px NEAREST read = 2 values + 1 accent.** Dark navy body, cool light rim,
   gold spear — confirmed in the truth-row (day/night × level/dive). The livery
   names itself in well under a second.
6. **Sharp DELTA planform kept** — `_delta_wings`, no drift to swept.
7. **Accessibility.** Navy/gold separates on VALUE alone (near-black body vs
   bright gold); the rim and shading are luminance-based. No red/blue
   distinction is relied upon — colourblind-safe.

## Contract held

`build_aerobatic(wing_angle_deg)` returns ONE flat 64×84 SRCALPHA frame,
fuselage mass centred (32,44), NOSE-RIGHT / UPRIGHT / LEVEL, no baked
rotation/flip (the sheet applies the production 205° secret-skin spin only to
preview the in-game inverted nose-high attitude). 4 poses = afterburner pulse +
±1px nose pitch; glow + flame baked, no live particles. Procedural-only,
WHY-only comments. `get_aerobatic = _make_prebuilt_skin(build_aerobatic)` and
`BUILDERS = {"skin_aerobatic": get_aerobatic}` for the production registry.

## Sheet

`docs/animals/jet_redesign/aerobatic/round_2.png` — refined design HERO 130px on
a DAY sky and a NIGHT sky, 40px level/dive NEAREST x3 on a DAY card and a NIGHT
card, plus a large 40px truth-row (DAY then NIGHT, level + dive) so the spear's
downscale survival and the night-sky rim hold are honest.
