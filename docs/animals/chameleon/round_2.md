# CHAMELEON · Round 2 (converged on v3 SPOTTED PANTHER)

Art-director verdict on round 1 was **ITERATE**, winner **v3 SPOTTED PANTHER**.
Round 2 collapses to the single production build `build_chameleon` and addresses
every punch-list directive. Sheet: `round_2.png` (hero 130px DAY+NIGHT, all 4
mood frames at 40px NEAREST x4 on DAY and NIGHT, plus a dive read and a smooth
silhouette strip).

## Punch list → what changed

1. **Mood-shift visible at 40px.** The colour-shift is no longer scattered 1px
   dots. The three vertical bars AND the 5-spot cluster now flush to the SAME
   frame hue together as one ~7px band, walking **one stop per frame**:
   `teal(f0) → violet(f1) → coral(f2) → amber(f3)` (`_MOOD`). Bar cores carry
   the mood hue (dominant at 40px) with a thin white panther-edge so the band
   reads as colour, not bleach. The hue is keyed to the discrete frame ordinal
   (`_frame_index`) so there are no in-between blends that smear the band.

2. **Constant teal anchor.** Body fill, dark rim, head, snout, feet and casque
   shadow use a fixed teal (`_BASE`/`_BASE_D`) on every frame, so the
   silhouette never washes out mid-cycle. `_MOOD[0]` is a teal-leaning cyan
   (coolest/lightest pose still anchors cool); the warmest amber (f3) is a
   mid-light value that clears bright-day, and none of the four stops go near
   black, so the darkest still clears night.

3. **Casque crest.** Widened base (~HCX-7 → HCX+8) and a small scallop notch on
   the trailing edge with a second lobe, plus a bright top-left leading edge, so
   it reads as a head-crest helmet ridge rather than a dorsal fin.

4. **Turret catchlight guaranteed.** `_turret_eye` always stamps a 1px pure
   white catchlight on the top-left of the aperture (not the pupil), so a
   dive-aimed pupil can never push it off the white. Pupil is aimed per pose
   (`look_x`/`look_y`): up/forward on the up-poses, down on the low poses.

5. **Tongue flick.** A clear horizontal coral dart (2px line + tip dot, ~11px
   long) on the **up-pose (f3) only** — the single warm accent. Longer and
   flatter than round 1 so it survives the downscale.

6. **Tail coil negative space.** `_coil_tail` stops one ring short of the centre
   (`inner_cut`), leaving one pixel of open core so it reads as a coil, not a
   blob, even at 40px.

7. **Key light.** Top-left throughout: belly sheen pushed up-left
   `(BCX-6, BCY-6)`, casque bright edge on the front-left, eye catchlight at
   `(-1,-1)` — matching the roster.

## Deliverables

- `chameleon_skins.py` — single `build_chameleon(wing_angle_deg)` +
  `get_chameleon = _make_prebuilt_skin(build_chameleon)` +
  `BUILDERS = {"skin_chameleon": get_chameleon}` (liftable into
  `game/animal_skins.py`). Mood-shift encoded inside `build_chameleon` by
  branching on the frame ordinal. Contract unchanged: 64×84, body (32,44),
  4 poses, procedural-only, WHY-only comments.
- `_render_sheet.py` → `round_2.png`.
