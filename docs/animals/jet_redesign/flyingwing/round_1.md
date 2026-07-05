# JET redesign — FLYING-WING STEALTH — Round 1

**Concept (`flyingwing`):** a tailless stealth flying wing (B-2 Spirit /
YF-23 vibe) to replace the production Steel Raptor's pointy gunmetal dart.
The identity is the **WIDE TAILLESS WING** — it must read as clearly NOT a
dart/raptor even at 40px. Buried engines → subtle embedded exhaust glow, no
plume. Every take leans on a hard **top-facet vs shadow** chordwise split so
the wide dark wing keeps internal structure at gameplay size, plus a faint
edge tell so it holds on day AND night.

**Sheet:** `docs/animals/jet_redesign/flyingwing/round_1.png`
Current Steel Raptor leads as the silhouette-contrast baseline; then 5
candidates, each at hero 130px + 40px NEAREST x3 (level / dive) over BOTH a
day stone sky and a night sky.

## The 5 sub-takes (genuinely different planforms + finishes)

- **v1 · B-2 CRESCENT** — smooth swept crescent, B-2 "double-W" sawtooth
  trailing edge, matte charcoal, centre-spine canopy bulge, twin buried
  burners in the trailing notches.
- **v2 · YF-23 DIAMOND** — angular four-corner diamond kite (Black Widow II),
  hard chordwise facet split, gunmetal with a faint **cool-blue edge-glow**
  tracing the leading edges; single central buried burner.
- **v3 · ARROWHEAD WING** — narrow sharply-swept arrowhead span, **two-tone
  panel facets** tiling the surface, premium tell is a single thin **amber
  cockpit slit**; twin buried burners.
- **v4 · SWEPT MANTA** — the widest take: manta/boomerang span swept far back,
  **deep aggressive sawtooth**, gunmetal + blue edge-glow + twin embedded
  burner cores. Maximum tailless-wing identity.
- **v5 · OBSIDIAN SPLIT** — matte-black low-vis pushed to the limit: no blue
  glow, minimal sawtooth — the entire read is the hard cold-graphite-vs-near-
  black value split + a crisp cold rim + one amber slit. The value-structure
  stress test.

## Contract held

- `build_flyingwing_vN(wing_angle_deg) -> Surface`, 64×84 SRCALPHA, mass
  centred (32,44). Drawn nose-right, upright, level (clean top-down planform);
  no baked rotation/flip.
- 4 poses = subtle engine-glow pulse + ±1px pitch, baked per frame (no live
  particles); `_make_prebuilt_skin` getter; label→getter `BUILDERS`.
- Procedural only; reuses `parrot._add_outline` / `_aaellipse`; no new assets.

## Self-notes for the critic (not self-judgement)

- v1 / v4 / v5 read most decisively as flying wings at 40px; v2's diamond is
  the cleanest facet split; v3's amber slit is the strongest single premium
  tell. Open question for the art-director: which finish (matte charcoal vs
  blue edge-glow vs amber slit) best sells "most expensive secret skin," and
  whether the buried burner cores read as embedded vs slightly blobby at 40px.

Render: `python docs/animals/jet_redesign/flyingwing/_render_sheet.py`
