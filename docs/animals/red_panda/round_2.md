# RED PANDA — Store skin · Round 2

Round 1 returned **ITERATE**, winner **v3 BIG-TAIL HERO**. This round drops the
five-way chooser and converges to ONE production build,
`build_red_panda(wing_angle_deg)`, folding in every punch-list note. The
exploration variants (v1/v2/v4/v5) are gone — the module now exposes the single
liftable getter:

```
get_red_panda = _make_prebuilt_skin(build_red_panda)
BUILDERS = {"skin_red_panda": get_red_panda}
```

Contract unchanged: 64×84 SRCALPHA, body mass at (32,44), 4 poses over
`_WING_ANGLES`, procedural-only, WHY-only comments. Sheet: `round_2.png`.

---

## Punch list — every item addressed

1. **Rescue the face.** Head ellipse grown to 13×12 (from 11×10, ~+18%) and
   the mask cheek blobs sized up to 7×8. The head is drawn LAST and lifted
   (`hcy = HCY-1`) so it sits clear of the tail base — the white mask now reads
   as a distinct second element at 40px, not a stripe in the pattern.

2. **Hard dark separation seam.** A `#4A2410` (`SEAM`) under-stroke is now laid
   along the INNER (body-facing) flank of the whole tail arc, plus a 15px
   `SEAM` disc stamped where the back meets the plume. The russet back and the
   russet plume no longer share a value — there's a clean dark break between
   them at 40px.

3. **Lock the ring rhythm.** The tail is redrawn in three passes; the cream
   bands are now **5 clearly separated ring-spots** placed at fixed arc
   fractions (biased toward the tip half), each one dark-ringed (`#7A2A0C`) for
   a crisp edge. At 40px NEAREST they read as discrete spots, not a blur.

4. **Stronger white belly anchor.** The belly is a larger 8×7 cream ellipse
   over a 9×8 `#7A2A0C` disc — a 1-px rust rim that holds the belly edge on
   near-white day skies.

5. **Day-sky keyline.** Relies on the house `parrot._add_outline` 1-px dark
   keyline (applied to every frame by `_make_prebuilt_skin`). Critically, the
   silhouette is kept CONTINUOUS — the tail base overlaps the body, the body
   overlaps nothing detached — so the outline wraps one connected shape and the
   russet edge never vanishes on bright day. Verified on the DAY swatch row.

6. **Pose-invariant reads.** Only the forepaw drop and a few-degrees arc flex
   animate (`leap-and-balance`: tail high on the down-pose, paws tuck on the
   up-pose). The tail-arc geometry and the mask are otherwise identical across
   all four poses — see the "4 poses x2" strip on both swatch rows.

7. **v1 warmth + v5 white tip.** The mask now has a warm `CREAM_D` shade pass
   under the bright cream (the v1 warmth). The tail terminus is a near-pure
   white `CREAM_W` tip ringed in dark — the v5 high-contrast end-punctuation of
   the arc.

8. **Colourblind / value check.** The three tail values are deliberately spread
   (cream ≈ 0.95 luma · russet ≈ 0.40 · seam ≈ 0.18). The desaturated 40px
   strip on the sheet confirms the cream ring-spots and white tip still
   separate cleanly from the fur in grayscale.

---

## Deliverables
- `docs/animals/red_panda/red_panda_skins.py` — single production
  `build_red_panda` + `get_red_panda` + `BUILDERS = {"skin_red_panda": ...}`.
- `docs/animals/red_panda/_render_sheet.py` → `round_2.png`: hero 130px + 40px
  level/dive over NIGHT + DAY with NEAREST x3, the 4-pose strip, and a
  desaturated 40px value test.

No `game/` file was touched; the module lifts straight into a future
`game/animal_skins.py`.
