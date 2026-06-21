# JAM JAR — parcel cosmetic (LOW tier) — Round 2

Round 1 got `VERDICT: ITERATE`: at 22px carried under Pip the cap read as a
MUSHROOM — the red cloth cap was occluded by Pip's red body (red-on-red),
leaving an amber dome on a stalk. Round 2 fixes every note.

## What changed

1. **Cap wins on VALUE, not hue.** The cloth cap moved off pure red to
   GINGHAM red checks on a CREAM ground (`CLOTH #F3E6C8`, checks
   `#C8362E`). Cream can't merge with Pip's red body, so the hat survives
   the occlusion. The overhang is widened (cap is `body.w + 14`, a clear
   ledge past the glass) and a **hard dark GAP band** (`#1C0D09`) now sits
   between cap and glass so the cap edge always survives the downscale.

2. **Mushroom read killed.** The glass body is now a squat rounded
   RECTANGLE — wider than tall (28×22), near-vertical walls and flat-ish
   shoulders (corner radius dropped 8→4/5). No dome, no neck: it reads as
   a stout jar, not a cap on a stalk.

3. **Stronger glass at 22px.** Replaced the thin single stripe with a
   2-value glass TURN: a bright upper-left specular wash + crisp specular
   streak (`#FFFFF4`) against a deeper amber lower-right wall
   (`GLASS #E09630`), with the very centre core lightened one more step to
   near-white (`CORE_HI #FFECC2`) so translucency reads. The turn survives
   smoothscale where a 1px stripe was marginal.

4. **Lid lip vs body.** The dark RIM band is kept as the lid LIP, but the
   cloth cap is now TALLER than the band (cap 13px vs band 4px), so the
   band reads as the lip UNDER the cloth, not as the cap itself. A string-
   tie groove + scalloped cream hem lobes sell the tied fabric.

## Carry-crop confirmation (the verdict)

On the DAY and NIGHT gameplay crops (the real occluded carry under Pip):

- The cap **survives Pip's red occlusion** — the cream/red gingham hat is
  clearly distinct from the parrot's red body, separated by the dark gap.
- It **no longer reads as a mushroom** — the squat amber rectangle below
  the cap reads as a glass jar with a translucent lit core, not a dome on
  a stalk.

## KEPT / CARRIED

- Tilt-row read held at all banks (−25/0/30/60/90°): cap-over-body stays
  recognizable; grayscale shows clean value steps (dark gap/outline vs.
  bright cream cap vs. amber glass).
- DAY amber-vs-sky and NIGHT amber-glow palette retained.
- Judged on the GAMEPLAY DAY/NIGHT crops, not the standalone hero.
