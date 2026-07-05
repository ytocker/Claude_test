# JET redesign — FLYING-WING STEALTH — Round 2 (converged ship build)

**Concept (`flyingwing`):** a tailless stealth flying wing replacing the
production Steel Raptor's pointy dart. The art-director picked the winner
from round 1 — **v2 · YF-23 DIAMOND** (faceted diamond wing + cool-blue
leading edge) — and round 2 converges it to ONE ship-ready production build.

**Sheet:** `docs/animals/jet_redesign/flyingwing/round_2.png`
Current Steel Raptor leads as the silhouette-contrast baseline; then the
single ship build, each at hero 130px + 40px NEAREST x3 (level / dive) over
three real in-game skies: DAY sunset, a DAY warm-STONE brown-out stress test,
and NIGHT.

## Punch list — addressed

1. **Buried burner (the #1 fix).** The central exhaust is now an embedded
   SLOT sunk into the aft shadow facet, well inboard of the tail apex, drawn
   in shadow-value with only a faint 1-2px ember. No copper marble; the
   diamond silhouette EDGE stays unbroken at 40px (verified — the rear corner
   of the diamond is intact, the ember reads as recessed thrust).
2. **Amber cockpit SLIT stolen from v3.** ONE thin amber slit on the centre
   spine is now the premium signature and the single brightest pixel. There is
   no bright burner competing — **one warm accent total** — paired with the
   cool-blue leading edge for the warm-focal / cool-edge two-accent hierarchy.
3. **Chordwise value gap widened ~15%.** Top facet lifted (`(112,124,144)`),
   shadow facet dropped (`(26,31,44)`); the diamond's central crease stays a
   hard line through the downscale on night.
4. **Day-sky floor cooled.** Gunmetal mid/shadow pushed a hair cooler + darker
   so it doesn't brown out against warm day stone; the top-facet-vs-shadow
   split still reads on both the orange sunset and the warm-stone panel.
5. **Leading-edge blue thinned to a 1px TRACE.** A whisper, not an outline; it
   survives 40px as the day-sky lifeline (clearest on night, present on day).
6. **Accessibility.** Warm amber slit (brightest pixel, centre spine) and cool
   blue edge (darker leading edge) separate by VALUE + POSITION, so both read
   in greyscale / for colourblind players.

## Contract held

- `build_flyingwing(wing_angle_deg) -> Surface`, 64×84 SRCALPHA, mass centred
  (32,44). Drawn nose-RIGHT, upright, level (clean top-down planform); no baked
  rotation/flip. Baked self-rim via the house `_add_outline`.
- 4 poses = subtle buried-ember pulse + ±1px pitch, baked per frame (no live
  particles).
- `get_flyingwing = _make_prebuilt_skin(build_flyingwing)`;
  `BUILDERS = {"skin_flyingwing": get_flyingwing}`.
- Procedural only; reuses `parrot._add_outline` / `_aaellipse`; no new assets.
- Both build targets clean (pure Pygame draw calls, no platform-specific API).

Render: `python docs/animals/jet_redesign/flyingwing/_render_sheet.py`
