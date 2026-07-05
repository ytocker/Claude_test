# COMET — round 2

Round 1 verdict: ITERATE. The standalone art was legendary-grade, but in the
carry pose the comet vanished under Pip — only a lone sparkle peeked out, reading
as a highlight ON the bird. Round 2 is a pure placement fix; the standalone art
(comma silhouette, value structure, night bloom, grayscale legibility) is
unchanged.

## What changed (build.py only)

1. **Core + tail dropped to the BOTTOM band.** The parcel rides centred 12px
   below Pip, whose drawn body radius exceeds that offset, so the sprite centre
   buries inside his belly and only the lowest rows clear him. The core moved
   from `cy ≈ 0.60` to `cy ≈ 0.84` of the 44px supersample (and `cx 0.62 → 0.55`),
   and grew `r 7.5 → 8.2`, so the whole white-hot heart and the tail root now sit
   in the lowest band that clears Pip's silhouette.
2. **Night bloom enlarged to ESCAPE the occlusion.** Replaced the two-halo stack
   with three: an inner warm-gold bloom (`r 21`, peak 104), a WIDE plasma skirt
   (`r 33`, peak 72) whose soft falloff spills well past Pip's lower edge, and the
   tight inner `CORE→HALO_HOT` halo (`r 14`, peak 155) keeping the heart hot. The
   wide skirt is what announces "legendary" — a warm aura visibly bleeding below
   and around Pip on the night sky.
3. **Core integrity preserved.** The white-hot heart is still drawn last at the
   tight `r * 0.34` cluster, so the bigger bloom never swallows the heart at carry
   scale; the inner `r 14` halo is kept under it.
4. **Tail given more root mass / length.** Root half-width `0.92× → 1.05×` core,
   tip pushed slightly farther up-and-back (`0.16,0.18 → 0.12,0.34`), so on the
   busy night sky the trail reads as a tapering streak rather than a lone dot.

## Carry-crop confirmation (the verdict)

- **DAY carry** — the white-gold core now clears Pip's belly as a distinct point
  of light with a warm aura around it; it reads as a separate light below him, no
  longer a highlight on his body.
- **NIGHT carry** — the warm bloom escapes PAST Pip's lower edge: a soft
  orange/plasma halo emanates from below and around his belly, with the white-hot
  heart as the brightest point. This is the legendary tell, visible at a glance at
  true scale.
- **Tilt row** — the comma still reads as a tapering streak at every bank
  (−25/0/30/60/90°); the grayscale row confirms the core is the brightest pixel
  cluster at every angle.

It reads as a glowing comet at 22px carried day and night: visible below Pip on
both skies, and blooming an escaping aura on the night sky.
