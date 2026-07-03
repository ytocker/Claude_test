# PAPER PLANE — Round 2 (converged to ONE production build)

**Sheet:** `docs/animals/paper_plane/round_2.png`
**Skin:** `skin_paper_plane` — **DOLLAR-BILL DART** (winner from Round 1, V4)
**Status:** single production build; not wired into `game/`.

Round 1 verdict was ITERATE on V4. This round drops the five-way exploration
and converges to one ship build, addressing every art-director directive.

## How each MUST-FIX was addressed

1. **Render-sheet double-image bug — fixed.** Each 40px cell now holds exactly
   ONE pose. The old sheet centred the level sprite at `panel.x + 52` and the
   dive sprite at `panel.x + 118` inside a 168px panel, so two 120px (40×3)
   NEAREST sprites overlapped into a broken double-image. `_render_sheet.py` now
   gives level and dive their own dedicated sub-panels (`DAY 40px lvl`,
   `DAY 40px dive`, and the night pair), each sprite centred in its own cell.

2. **Fold value-split strengthened ~28%.** The lit upper facet was lifted to
   `(138,186,144)` and the under-fold pushed distinctly darker to
   `(58,100,74)` with a deepest wedge at `(42,80,60)`. The central crease is now
   a 3px hard line in `(30,58,44)`, so at 40px the FOLD (a value break), not the
   hue, says "folded paper" — matching V1's crease discipline.

3. **Portrait oval is now a deliberate medallion.** A thin darker-green
   containment ring `(46,84,60)` is drawn first, pale fill inside, so the oval
   holds SHAPE on bright day instead of blooming. Pulled up onto the lit facet,
   clear of the crease, so it reads as its own contained banknote medallion.

4. **Crisp dart point + straight top edge.** The nose is a tight point at
   `(BCX+25, BCY-1)` and the top swept edge runs nose→far_tip as a single
   straight line, so the triangular dart silhouette is unambiguous.

5. **Gold pips cut from the 40px target.** Denomination pips are gated behind a
   `hero` flag (`build_paper_plane_hero`) and appear only in the 130px hero
   panels — invisible noise at gameplay scale, so they're out of the ship path.

6. **Baked 1px self-rim.** A darker-green `(34,64,48)` ring is stamped from the
   painted alpha mask and blitted UNDER the art, hugging the true outer
   silhouette. The dart no longer depends on the sheet's house outline, and
   there is no glow halo — glow restraint kept.

7. **Bank-roll clamped.** Roll is clamped to `±5.5°` (`_ROLL_MAX`) so the
   3/4-view under-fold never collapses edge-on; the dive cells confirm the dart
   + crease stay readable in the banked "flap" pose.

## Truth-test read (40px NEAREST x3)

- Day + night, level + dive: the green dart silhouette + the bright-top /
  dark-under hard fold + the ringed pale medallion all hold. The self-rim
  carries legibility on both skies. No double-image in any cell.

## Contract (unchanged)

- `build_paper_plane(wing_angle_deg) -> Surface` on a 64×84 SRCALPHA canvas;
  mass centre at `(32, 44)`.
- `get_paper_plane = _make_prebuilt_skin(build_paper_plane)`.
- `BUILDERS = {"skin_paper_plane": get_paper_plane}`.
- Procedural-only, WHY-only comments. Verified: build returns `(64, 84)`;
  getter returns `(68, 88)` after the house 2px outline pad.

Lifts straight into a standalone `game/animal_paper_plane.py` when chosen.
