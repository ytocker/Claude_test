# Paper Plane redesign — NOTEBOOK PAPER — Round 1

Five genuinely different sub-takes on ONE concept: a dart folded from
blue-ruled schoolyard notebook paper. The signature 40px tell is the RED margin
stripe + one or two BOLD blue rules reading as "lined paper" even small; the
finer rules, holes and doodles are HERO texture that vanishes politely at
gameplay scale.

All five share the contract from `game/animal_paper_plane.py`: a 64×84 SRCALPHA
frame, mass centred at (32,44), **nose pointing RIGHT**, no wings (the 4 poses
become a clamped bank-roll + nose-bob), a baked 1px self-rim, and a hard-value
fold (lit top facet vs darker grey under-fold meeting at a 3px keel crease).

## The 5 sub-takes

- **V1 · CLASSIC RULED** — bright white loose-leaf, straight blue rules running
  flat across the lit facet, RED margin along the KEEL, spiral punch-holes on
  the upper trailing edge. The textbook lined-paper read.
- **V2 · FOLD-FOLLOWING** — rules BEND along the two fold facets (sloping with
  each facet to sell the 3D paper), RED margin along the TOP swept edge, plus
  faint under-facet rules sloping the other way across the fold.
- **V3 · CREAM + BIRO STAR** — warm aged cream tone, fewer bolder rules, RED
  keel margin, and a tiny blue ball-point STAR doodle on the lit facet as the
  personality accent; spiral holes on the keel side.
- **V4 · GRADED A+** — crisp white, dense fine rules + 2 bold rules, RED keel
  margin, a cheeky red "A+" scrawl accent, and a torn tear-fringe along the
  lower trailing edge.
- **V5 · BOLD LOOSE-LEAF** — the minimal 40px-first take: a BOLD red margin
  stripe + just TWO heavy blue rules carry the whole tell (drawn at every scale,
  not gated behind hero), three binder ring-holes punched along the keel edge.
  Built to win where thin rules vanish.

## Concept axes explored (per the brief)

- **Rule density + fold-follow:** sparse straight (V1, V3), bending along facets
  (V2), dense (V4), two heavy rules only (V5).
- **Red margin placement:** along the keel (V1/V3/V4/V5) vs the top swept edge
  (V2).
- **Torn / spiral edge:** spiral punch-holes (V1, V3), tear-fringe notches (V4),
  binder ring-holes (V5).
- **Optional doodle accent:** biro star (V3), red "A+" scrawl (V4).
- **Paper tone:** white loose-leaf (V1/V4/V5) vs warm cream (V3) vs off-white
  (V2/V5).

## How to read the sheet

`docs/animals/paper_plane_redesign/notebook/round_1.png` — one card per variant.
Each card: a 130px hero on a split day|night ground (left), then a DAY truth
block and a NIGHT truth block, each showing smooth-40px level/dive plus the
honest NEAREST-NEIGHBOR x3 magnified 40px reads (the gameplay-pixel truth).

## Render

```
python docs/animals/paper_plane_redesign/notebook/_render_sheet.py
# wrote docs/animals/paper_plane_redesign/notebook/round_1.png (792, 1210)
```

Headless (SDL dummy), procedural-only, both build targets unaffected (no
desktop/web-specific APIs). Nothing wired into `game/`.
