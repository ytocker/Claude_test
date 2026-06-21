# JET FIGHTER redesign — NAVAL INTERCEPTOR (`naval`) · Round 1

**Concept:** an F-14 Tomcat / Top Gun-style carrier interceptor. The identity
that separates it from the current gunmetal "Steel Raptor" single-look raptor:
**variable-sweep WINGS + TWIN canted tail fins + a long tandem (two-seat)
fuselage + wide-spaced engine nacelles with a twin afterburner.**

Sheet: `docs/animals/jet_redesign/naval/round_1.png` (5 takes, each on a DAY
sky and a NIGHT sky; hero 130px + 40px smooth + 40px NEAREST x3 level/dive —
the honest gameplay read).

## Contract held
- `build_naval_vN(wing_angle_deg) -> 64×84 SRCALPHA`, fuselage mass centred at
  **(32,44)** (fixed 14px collision circle there; wings/stabs span wider).
- Drawn **nose-RIGHT, upright, level** — **no baked rotation/flip**; the game
  applies the inverted nose-up presentation later.
- 4 base poses `_WING_ANGLES=(50,20,-10,-40)` animate as an **afterburner
  pulse** (+ ±1px nose pitch): the baked twin exhaust flares/shrinks; glow is
  baked into the frames, no live particles.
- Getter via local `_make_prebuilt_skin`; lead build keys
  `BUILDERS = {"skin_naval": get_naval}` (production-shaped).
- Procedural only; both targets green; WHY-only comments.

## The 5 sub-takes (genuinely different, exploring the brief's variables)

| # | Name | Sweep | Tail | Nose | Livery |
|---|------|-------|------|------|--------|
| v1 (LEAD) | **LOW-VIS PROWLER** | forward (soar) | twin | long radar | low-vis TPS greys (value-only) |
| v2 | **FLEET DEFENDER** | swept back (fast) | twin | blunt | Light-Gull-Gray over white + bold red squadron stripe + modex/tail caps |
| v3 | **JOLLY ROGERS** | mid-sweep | twin | long | sea-black + small white skull motif + gold tail caps |
| v4 | **GOLD ACE** | fwd-mid | **single tall tail** | blunt | navy-blue + gold spine + gold leading-edge chevrons |
| v5 | **SWING-WING STRIKE** | hard-back (max dash) | twin | long radar | gunship-grey + one bold hi-vis diagonal stripe + hottest burner |

Twin-tail + swing-wing is the constant identity (except v4, which deliberately
shows the single-tail variable). Liveries are drawn as **structure** (bold
value/stripe bars), not fussy decals, so they survive the 40px downscale.

## Shared design choices
- One `_naval_airframe` helper draws the skeleton so all five read as the SAME
  jet wearing five paint jobs; sweep / nose / tail are knobs.
- Burner colour temperature is constant across liveries (warm core → orange →
  ember) so the afterburner tell is consistent; only the airframe changes.
- Tandem canopy is the cool CONSTANT anchor across all 4 frames,
  colourblind-distinct from the warm burner.

## Render
`python docs/animals/jet_redesign/naval/_render_sheet.py` → wrote `round_1.png`
(752×1140), headless SDL-dummy. No errors.

Not wired into `game/`. Awaiting art-director critique.
