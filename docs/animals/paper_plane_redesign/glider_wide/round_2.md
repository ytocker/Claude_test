# PAPER PLANE redesign — WIDE GLIDER — Round 2 (final convergence)

Converged to ONE ship-ready production build, **KEEL GLIDER**, from the Round-1
winner V5 (the only glider take with a correct forward-right nose; the flat
deltas read backward/blobby). The keel is the hero: a tall, chunky lit ridge
against a hard-darkened shadow shelf, flanked by two wide flat wing shelves and
pinned by two crisp rear points so it reads as a deliberate WIDE wing, never a
narrow dart and never a backward kite.

Sheet: `round_2.png` — the single build at hero 130px on day AND night, then the
honest 40px NEAREST x3 gameplay read (level + dive) on day, night, and a pale
sandstone pillar (the day value-guard check). Current dollar dart leads for the
"different silhouette" contrast.

Deliverable: `glider_wide_skins.py` now exposes a SINGLE production build —
`build_glider_wide(wing_angle_deg)`, `get_glider_wide = _make_prebuilt_skin(...)`,
`BUILDERS = {"skin_glider_wide": get_glider_wide}` — liftable straight into
`game/animal_paper_plane.py`. Nose-RIGHT, 64x84, mass (32,44), baked self-rim,
procedural-only, WHY-only comments.

## Punch list — how each note was addressed

1. **Forward-RIGHT nose LOCKED.** Nose at `BCX+23` is the rightmost, narrowest
   pixel cluster; the wide trailing span sits at `BCX-19` (left/behind). Roll is
   clamped tighter (`_ROLL_MAX 4.0`, `f*3.6`) so no pose — including dive —
   rotates the keel off its forward-right spine into a backward-kite read.
2. **Keel value split widened ~15%.** Shadow wing shelf pushed darker
   (`_WING_D 138,116,78` vs R1 `160,138,98`) with a deepest under-keel wedge
   (`_WING_DD`), so the central ridge pops as a hard 3D crease at 40px, not a
   soft gradient.
3. **Two crisp rear points.** Trailing corners pulled to sharp points and
   splayed wider (`±19` from centre) so the silhouette is a deliberate WIDE
   wing, not a frayed/rounded blob.
4. **Tightened self-rim.** `_self_rim` uses 4-neighbour (no diagonal) stamping
   for a consistent 1px lip; on night the lower shadow-shelf rim carries the
   rear-corner legibility where the shape softens.
5. **Day value guard.** Brightest manila held a notch below white
   (`_KEEL_L 238,222,184`; nose catch-light `_KEEL_LH 250,240,214`, not full
   white) — verified it does not flare against bright day sky or the pale
   pillar strip.
6. **Keel is the hero.** Ridge built taller/wider as a dual-facet box (lit top
   + hard-shadow side, capped by a hard crease and a shoulder crease) so the
   lit-spine-vs-shadow-shelf ridge dominates at 40px — the 3D structure flat
   deltas lack.
7. **Dive pose sane.** At frame 1 / -32deg the keel still reads as a
   forward-right spine; the clamped pitch sway never rotates it into a kite.

## Read check

The keel ridge, two rear points, and forward-right nose all hold at 40px
NEAREST on day, night, and a pale pillar. Single production build — no further
exploration; converged per the brief.
