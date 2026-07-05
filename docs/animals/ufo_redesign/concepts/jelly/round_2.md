# Concept: THE BIO-JELLYFISH — `skin_ufo` redesign, round 2

Round 1 got `VERDICT: ITERATE`: the hero was gorgeous but at 40px it read as a
HUNCHED PURPLE HUMANOID holding a box — the two symmetric crown dots paired as
EYES, the parcel read as a TORSO, the two outer tendrils read as bent LEGS, and
the bright aqua tip-dots read as FEET/SHOES. Round 2 breaks that humanoid
gestalt while keeping the organic-jelly identity, the rim keyline / day value
structure, the night dome + bio bloom, the colour harmony, and the bell
squash/stretch pulse (all of which the critique said were working).

## What changed (the punch list, in priority order)

1. **Broke the face (#1).** The two equal mid-bell crown dots were the eyes.
   They're gone. Bio-dots now sit UP on the dome APEX (above the eye line
   entirely) and are deliberately ASYMMETRIC: a larger one left-of-centre and
   high, a smaller one lower and further right, plus a tiny third gland near the
   crown. Three uneven, offset glints can't resolve into a symmetric pair of
   eyes — they read as bio-glands lighting the top of the bell.

2. **Killed the biped read.** Went from 3 chunky strands to **5 THIN tendrils**
   (≈2px root → 1px tip). Every length is offset (27/35/31/38/24px — no two
   equal) and each carries a signed CURL that grows toward the tip, so the spray
   splays OUTWARD like seaweed and never plants as two posts or crosses into an
   X. Adjacent strands sway in alternating phase for a non-uniform drift.
   **Dropped the bright aqua tip-dots entirely** — those were the feet/shoes.

3. **Unwelded the parcel.** Bell apex pushed HIGHER (`BELL_TOP_DY` 16→19) so the
   dome owns the top ~60% as one mass. The strands hang in front of / around
   Pip's parcel, so the parcel clearly reads as held BELOW a bell rather than
   embedded as a torso. The head/torso/legs vertical rhythm is broken.

4. **Widened the bell vs the tendril span.** Bell half-width 18→21, while the
   tendril roots cluster in a NARROW span (±9, was ±11) well inside the bell
   margin. The bell now OVERHANGS the strand cluster — a real jelly's bell is
   broader than its tendrils — so the lower half no longer reads as body+legs of
   equal width.

5. **Leaned on the scalloped fringe as the silhouette tell.** The fringe lobes
   are FATTER (rr 4/3, was 3/2), hang lower with a deeper baseline sag, reach
   just PAST the bell rim (overhang), and each gets a bright rim cap so the
   scallop reads as the lit lip of the bell. At 40px the bottom edge of the bell
   now has a visibly bumpy organic margin distinct from the thin strands below —
   the one shape no saucer can have.

## Kept (worked in round 1)
- The bright `#D4BAFF` rim keyline + the bell vertical-gradient value structure
  (day legibility was good).
- The night dome highlight + tight bio bloom.
- The purple/aqua colour harmony.
- The squash/stretch pulse tell (`_PULSE`: f0 tall-narrow → f2 wide-flat), which
  survives grayscale — see the colorblind strip going tall→wide→tall.

## Gut-check at 40px (day + night)
Squinting at the DAY and NIGHT gameplay frames and the play-size strip: it reads
as **a domed bell up top with a spray of drifting strands beneath**, NOT a
humanoid. The apex glands no longer pair as eyes (asymmetric, above the eye
line); the parcel reads as held below the bell, not as a torso; the 5 thin
curling strands read as a seaweed spray, not two legs with feet; and the bumpy
scalloped fringe overhang carries the organic jellyfish silhouette. Fixes 1, 2,
and 4 (the must-haves) all landed.

## Contract compliance
- 64×84 SRCALPHA, `BCX,BCY=(32,44)`, `DY=12`; bell mass centred and above
  centre; tendrils extend below the 14px collision circle without shifting the
  bell read.
- `build(wing_angle_deg)` returns the upright Surface; 4 squash/stretch frames
  driven by `_WING_ANGLES`; NO baked rotation (velocity tilt applied later).
- Procedural pygame only; reuses `game.parrot._add_outline` / `_aaellipse`;
  mirrors the `_make_prebuilt_skin` getter + additive-glow pattern from
  `game/animal_ufo.py`.

## Files
- `build.py` — updated `build()` + asymmetric apex glands, 5-strand curling
  spray, wider/higher bell, exaggerated scalloped fringe.
- `render.py` — now outputs `round_2.png`.
- `round_2.png` — DAY gameplay | NIGHT gameplay | reference (3x / play-size /
  grayscale). The two gameplay frames at 40px are the verdict.
