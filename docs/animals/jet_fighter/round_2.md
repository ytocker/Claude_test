# JET FIGHTER (`skin_jet_fighter`) — Round 2 · STEEL RAPTOR (converged)

**Verdict to address:** ITERATE on round-1 v1 STEEL RAPTOR — top-down planform
is the correct view for 40px. This round converges to ONE production build and
addresses every MUST-FIX. Judged on the **40px dive frame** (rendered at x8 on
day + night during iteration; the sheet shows x3).

Sheet: `docs/animals/jet_fighter/round_2.png`
Build: `docs/animals/jet_fighter/jet_fighter_skins.py`
Contract unchanged: `build_jet_fighter(wing_angle_deg)` +
`get_jet_fighter = _make_prebuilt_skin(build_jet_fighter)` +
`BUILDERS = {"skin_jet_fighter": get_jet_fighter}`. Afterburner glow baked per
frame; no live particles. Same 64×84 canvas, fuselage centre (32,44).

## How each MUST-FIX was resolved

1. **De-blob the twin afterburner.** Decided by testing ONLY the 40px dive
   frame: kept TWIN (the identity needs two flames + twin fins) and **widened
   the nozzle gap to ±8px** (`_NOZ_DY = 8`). The baked plume's white core layer
   is now narrow (`width/5`, was `width/4.2`) so the two white-hot cores stay
   visually separate even when their soft outer hazes kiss on the hottest dive
   frame. At 40px the two cores read as two, not one orange mass.

2. **Cap the burner so it supports, not swallows.** Each nozzle now carries its
   OWN tight halo instead of one shared blob, and the halo radius is **baked
   ~16% smaller** (`(10 + p*5) * 0.84`) so peak glow stays inside the rear third
   of the silhouette. The arrowhead nose + delta are the dominant read at 40px.

3. **Value-based wing accent (killed the invisible red line).** The lone
   low-contrast red leading-edge line is gone. The wing edge now reads by
   LUMINANCE: a **darker gunmetal leading-edge outline** (`_EDGE` 44/48/58,
   darker than body) plus a **brighter top-facet highlight** (`_BODY_H`
   182/190/202). Reads on day stone and dark night alike. Red survives only as
   a small warm accent (nose radar dot, wingtip-rail caps).

4. **ONE premium signature.** A thin **WARM hot rim-light** (`_RIM` 255/196/120,
   tied to the burner's colour temperature) traces the delta leading edges + the
   nose chine, with a hot spark at each leading-edge root. No chrome spine —
   this single tell is the "most expensive" cue AND it rescues the night
   silhouette.

5. **Night read.** Verified at x8 on a dark-blue night sky: the gunmetal body
   lifts cleanly off the background via the value outline + warm rim; the jet
   never sinks into the sky.

6. **Canopy anchor.** The cool **blue bubble canopy** (`_CANOPY` 58/150/200 +
   bright cyan highlight) is drawn identically across all 4 frames at a fixed
   body-relative position; pitch/pulse never wash it out. Colourblind-distinct
   from the warm orange burner (cool-vs-warm + position).

7. **Pulse reads as throttle.** `_pulse()` triangle-wraps so the burner is
   **bright on the middle two frames, dim at the ends**, paired with the ±1px
   `_pitch()` nose move. The 4-frame strip on the sheet shows dim → BRIGHT →
   BRIGHT → dim: perceptible at 40px, not strobing.

8. **Distinct from PAPER PLANE.** Hard-edged delta planform, twin canted tail
   fins, bubble canopy, twin metal nozzles — never a soft folded triangle.

## Sheet layout

- **HERO 130px** — day + night, showing the full premium read.
- **AFTERBURNER PULSE** — all 4 baked frames at 40px x3 on day, so the throttle
  heartbeat + the distinct twin cores are verifiable frame-by-frame.
- **TRUTH TEST** — 40px x3, level + DIVE, on day then night (the judged view).
