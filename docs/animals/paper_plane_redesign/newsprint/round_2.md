# Paper Plane redesign — NEWSPRINT / COMIC · Round 2 (production convergence)

The art-director picked **V3 · SUNDAY COMIC** (halftone + red POW) and asked for
ONE ship-ready production build. Round 2 converges the five round-1 takes down to
a single `build_newsprint` that lifts straight back into
`game/animal_paper_plane.py`.

## Contract (unchanged)

- `build_newsprint(wing_angle_deg) -> 64×84 SRCALPHA`, mass centred (32,44).
- **Nose points RIGHT** (forward).
- No wings — the 4 wing poses drive a clamped bank-roll + nose-bob (`_ROLL_MAX = 5.5`).
- Baked 1px self-rim so the dart holds on day AND night with no host outline.
- Procedural only; both build targets stay green (no platform-specific calls).
- `get_newsprint = _make_prebuilt_skin(build_newsprint)` and
  `BUILDERS = {"skin_newsprint": get_newsprint}`.

## Punch list — how each note was converged

1. **POW to the TRAILING third.** The starburst centre moved from `BCX − 1`
   (mid-body) to `BCX − 6` (trailing third), left of the mass centre. The
   forward nose third is now clean lit paper with a tiny inked tick at the tip,
   so the nose-RIGHT heading reads in a single frame.
2. **Halftone field shrunk ~18% + pulled OFF the nose.** The dot region is a
   tighter trailing quad that stops at `BCX + 5` (was `BCX + 18`, near the nose
   point); the golden dot grid window shrank to `BCX − 12 … BCX + 5`. The clean
   lit nose facet now owns the front point and the field only frames the POW.
3. **Night tail rim verified.** Sampled the wide trailing end on the night sky:
   the baked 1px self-rim (`50,46,40`) sits between the dark under-fold and the
   sky all the way around, so the dark under-fold never kisses the night sky.
4. **Hard value fold.** The crease is now a 2px dark spine (`58,54,46`) plus a
   1px lit lip (`96,90,78`) riding its upper crest — a crisp value STEP, so the
   triangular dart silhouette survives even in pure value (the colourblind read)
   and even if the eye misses the red.
5. **Exactly ONE red + ONE white core.** A single saturated red POW mass
   (`218,44,40`) with one white-hot core dot (`252,246,226`). No second red was
   added; the red is a value-and-shape mark, not hue-only.
6. **CMYK pass capped — no pink mush.** The round-1 magenta-ish second dot pass
   was the salmon risk at 40px. It is replaced by a sparse, small **warm-orange**
   minority pass (`236,132,56`) over the golden majority (`250,204,64`). Sampling
   the downscaled facet confirms the field averages to "warm bright print", not
   pink — verified on the 40px DAY and NIGHT truth panels.

## Review sheet

`round_2.png` (592×484): the single production build at 130px hero + 40px
NEAREST-x3 (level / dive) on a **day** sky and a **night** sky, plus an
annotated punch-list-converged strip.

Render: `python docs/animals/paper_plane_redesign/newsprint/_render_sheet.py`

Nothing wired into `game/` yet — `build_newsprint` is ready to lift into
`game/animal_paper_plane.py` once the orchestrator names the winner.
