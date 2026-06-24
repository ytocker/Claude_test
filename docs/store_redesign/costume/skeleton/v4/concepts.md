# SKELETON costume — v4 (clean reset)

**Brief (user, verbatim intent):** ignore ALL prior skeleton work (v1/v2/v3, the
CLEAN vs X-RAY pair, every earlier critique). Take the **original Pip macaw** and
make **5 distinctive versions showing how the parrot would look as an X-RAY with a
FULL skeleton** — and a **dominant bone for its beak**.

## Method (shared, identical anatomy across all 5)
`tools/skeleton_candidates/_v4_xray_base.py` holds the foundation so faithfulness
and completeness are guaranteed, not re-litigated each design:
- `bone_parrot(angle)` — the EXACT original sprite geometry recoloured to dark
  "flesh" (`P_FLESH`), so silhouette + beak location + tail location are the real
  Pip automatically.
- `paint_skeleton(surf, angle, style)` — the COMPLETE skeleton (skull, hollow
  eye-socket, **dominant hooked beak bone**, cervical→caudal spine, full ribcage +
  keel, shoulder + wing arm-bones & phalanges that flap in register, pelvis, both
  legs, clawed feet, tail bones). No bone can go missing.

Each design = a STYLE dict (+ optional post-pass) over the same anatomy. The five
differ ONLY in bone material / treatment.

## The 5 styles (→ design_1..5)
1. **RADIOGRAPH** — true medical x-ray: cool blue-white bones glowing through the
   dark translucent body, soft bloom. The classic "x-ray photo" read.
2. **BOLD CARTOON BONE** — thick, chunky, high-contrast white bones, Day-of-the-
   Dead clean; maximum readability at 40px. Big triangular beak bone.
3. **NEON / BIOLUMINESCENT** — bones emit a cyan/green glow against near-black
   flesh; spooky arcade vibe, bones as the light source.
4. **IVORY ANATOMICAL** — warm bone/ivory, naturalist-plate detail: countable
   ribs, vertebrae, full wing phalanges; long curved dominant beak bone.
5. **ETCHED WOODCUT** — crisp white line-art bones with fine hatching shadow over
   a charcoal body; vintage anatomy-illustration feel.

## Process
One critique + one fix (user pick), not the full loop. R1 designers (5 ∥) → C1
critics (5 ∥) → R2 designers apply one fix → ONE comparison figure
`v4/final_comparison.png` (original + 5). Exploration only; production untouched
until the user picks a winner.
