# PAPER PLANE redesign — concept CLASSIC DART · Round 1

Candidate redesign for Skybit's secret paper-plane skin (`dart_classic`). The
current production paper plane is a green folded-dollar-bill dart
(`game/animal_paper_plane.py`). This concept goes the opposite way: the iconic
crisp WHITE printer-paper dart — sharp needle nose, deep central keel fold,
clean facets. Timeless and minimal. The paper stays white / cream on purpose.

**Sheet:** `docs/animals/paper_plane_redesign/dart_classic/round_1.png`

## Contract held
- `build_dart_classic_v1..v5(wing_angle_deg) -> Surface` on a 64×84 SRCALPHA
  canvas, craft mass centred at (32, 44).
- **Nose points RIGHT (forward)** — drawn as-is, no host flip.
- No wings: the 4 base poses (`_WING_ANGLES=(50,20,-10,-40)`) drive a gentle
  bank-roll + nose-bob via `_flutter`/`_bank`. Roll clamped at ±5.5° so the
  dart never flattens to a sliver.
- Each build wrapped in a local `_make_prebuilt_skin`; label→getter dict +
  `BUILDERS` registry. Procedural only; both targets green; WHY-only comments.
- Every take bakes a 1px self-rim from its alpha mask so the white silhouette
  holds on day AND night without leaning on the host outline.

## The 5 takes (genuinely different FORM + SHADING of a white dart)
- **v1 · clean side profile** — textbook dead-on side dart. One long isosceles
  silhouette, single keel, cool-grey under-fold, one hard central crease. No
  accents. The purest read.
- **v2 · slight 3/4 view** — seen from above-behind: a bright far-wing facet, a
  half-stop-darker near-wing facet, and a raised keel spine ridge between them
  with a bright top highlight. Wider silhouette, neutral paper.
- **v3 · deep-keel razor** — extreme needle nose reaching far past centre + a
  tall dramatic deep keel dropping below the wing line. Maximum value contrast
  (white wing vs near-charcoal keel); cool steel-paper, fast & sharp.
- **v4 · nakamura double-fold** — the 3/4 view with the Nakamura signature: an
  inner crease splits each wing into an inner darker band + outer bright band.
  Two creases — reads more "engineered". Soft cool-grey shadows.
- **v5 · dog-ear accent** — minimal V1 form, warm cream paper, with ONE
  restrained tell: a faint blue pencil stripe along the keel + a folded-corner
  dog-ear at the tail catching shadow. Still predominantly clean white.

The set deliberately spans view angle (side vs 3/4), nose sharpness, keel depth,
fold count (single vs double), facet contrast, and paper temperature (cool grey
↔ neutral ↔ warm cream), with one optional subtle-accent take.

## Render
Headless SDL-dummy. Each take shown at hero 130px (night) and at the 40px
gameplay truth-test (level + dive), smooth AND NEAREST x3, over BOTH a day sky
and a night sky so the white-on-bright / white-on-dark legibility of the baked
self-rim is honest.

```
python docs/animals/paper_plane_redesign/dart_classic/_render_sheet.py
# wrote .../round_1.png (792, 1160)
```

Not wired into `game/`. Awaiting art-director critique.
