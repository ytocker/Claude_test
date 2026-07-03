# THUNDERBIRD — Round 3 (final pass: STORM-RAPTOR)

VERDICT to address: **ITERATE** — apply ONLY the minimal day-legibility +
tip-shape must-fix list, keep the converged concept frozen, then stop.

Sheet: `docs/animals/thunderbird/round_3.png` — the single production design on
BOTH a **bright-day** sky (mandatory legendary proof) and a **night** sky, each
at hero 130px (clap), 40px smooth (clap / dive), and 40px NEAREST x3
(clap / up-dive).

## Frozen (untouched per the KEEP list)

- The asymmetric single under-wing fork concept.
- The frame-stable silhouette mass (body / tail / head / plumes drawn at FIXED
  size every frame; only aura + lightning scale → no flicker).
- Glow restraint (single body aura halo only).
- The night palette.

## Must-fix punch list — what changed (minimal)

1. **Day-sky body value (the #1 blocker).** Added a top-down value ramp so the
   raptor's back/top arc is the LIGHT side instead of a flat dark-navy blob: a
   lifted upper-body cap (`PLUME_TOP`, ~+18% on `PLUME`) over the mid body, plus
   a 1px cool **key-light** edge (`BODY_KEY`) tracing the top-of-back arc. The
   back now separates cleanly from a pale-blue sky (light-top → dark-belly), not
   one mass.

2. **De-conflicted the eye from the belly stripe.** The under-belly electric arc
   was pulled a value-step DOWN and shifted teal (`BELLY` `#4E96A8`, was the full
   `RIM` cyan). The white-cored storm-blue **eye** is again the unambiguous
   single brightest point at 40px on bright day — verified in the x6 day crop:
   they no longer tie/smear into one blue bar.

3. **Talon de-risk on the fork.** (a) Steepened the whole fork's outward lean —
   each segment now drifts more LEFT than it drops, so the bolt clearly leaves
   the body into open sky rather than hanging near-vertical. (b) The terminal is
   now a **single sharp zig-zag point** — the lower Y-split is gone; the one
   crackle branch peels UP-and-out from mid-bolt (kept above the tip) so it can
   never form a two-toe foot. Mid-stroke fork matched to the same read.

4. **Plumes on bright day.** Each back-swept crest plume now gets a 1px brighter
   cool-white tip edge (`BODY_KEY` stroke + tip dot) so the crest still spikes
   against a pale sky where `PLUME_HH` alone nearly dissolved into the body.

## Contract (unchanged)

64×84 canvas, body (32,44), head (44,34), 4 poses, procedural-only, WHY-only
comments. No live particles — all glow/lightning baked into the 4 frames.
Single production API preserved: `build_thunderbird(wing_angle_deg)`,
`get_thunderbird = _make_prebuilt_skin(build_thunderbird)`, and
`BUILDERS = {"skin_thunderbird": get_thunderbird}` — liftable straight into
`game/animal_skins.py`.
