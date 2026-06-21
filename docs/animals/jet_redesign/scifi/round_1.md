# SCI-FI ENERGY FIGHTER jet redesign — Round 1

Concept: `scifi` — a futuristic spaceship-fighter to replace/extend the secret
JET skin. Angular FACETED hull + glowing NEON energy trim + a plasma
afterburner. Hard-edged cool neon tech, deliberately distinct from the
warm/organic DRAGON & PHOENIX legendaries.

Sheet: `docs/animals/jet_redesign/scifi/round_1.png`
(hero 130px + 40px NEAREST x3 level/dive on DAY **and** NIGHT skies).

## Contract held (matches game/animal_jet_fighter.py)
- `build_scifi_vN(wing_angle_deg) -> 64×84 SRCALPHA`, hull mass centred (32,44).
- Drawn NOSE-RIGHT, UPRIGHT, LEVEL — no baked rotation/flip (game spins it
  inverted nose-up later).
- 4 poses = a baked PLASMA PULSE (`_pulse`) + ±1px pitch (`_pitch`); all glow
  (energy edges via `_neon_edges`, engine plasma via `_plasma`/`_glow`) baked
  per frame, varied across the 4 — no live particle system.
- Getter via local `_make_prebuilt_skin`; `BUILDERS = {"skin_scifi": ...}`.
- Procedural only; WHY-only comments.

## The 5 sub-takes (genuinely different, one concept)
- **v1 · CYAN INTERCEPTOR** — sleek arrowhead hull, SUBTLE cyan edge-piping
  (one clean chevron), a single big plasma core. The minimal/elegant read.
- **v2 · MAGENTA GUNSHIP** — heavy WIDE blocky hull, FULL magenta energy aura,
  TWIN plasma engines. The aggressive bruiser.
- **v3 · VIOLET STARWING** — a winged-X starship (four splayed prong wings),
  electric-violet trim, twin engines, glowing cannon tips. The most overt
  "spaceship" silhouette.
- **v4 · TOXIC STRIKER** — FORWARD-SWEPT wings (rare alien planform),
  toxic-green neon piping, a single core plus reactor side-vents that breathe.
- **v5 · GOLD SOVEREIGN** — a FACETED diamond gem-cruiser, GOLD trim on every
  facet seam with a full warm aura, one huge gold plasma core. The
  premium/legendary read.

## Axes explored per brief
- energy colour: cyan / magenta / electric-violet / toxic-green / gold.
- hull style: arrowhead / heavy gunship / winged-X / forward-swept / faceted
  diamond.
- glow amount: subtle piping (v1) → full aura (v2, v5).
- engine: single big core (v1, v4, v5) vs twin (v2, v3).

## Render notes
- Both day and night panels render the baked neon; the 1px self-rim
  (`_add_outline`) keeps each hull legible against a bright sky as well as
  black.
- NEAREST x3 is the honest gameplay truth test; smooth hero is reference only.

Not self-critiqued and not wired into `game/` — handing to the art-director.
