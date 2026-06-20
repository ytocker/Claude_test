# GRIFFIN skin — Round 1

Top of the late-game ANIMALS tier: an eagle-headed forebody fused to a tawny
lion hindquarter with a tufted tail. The whole design problem is twofold:

1. **Read as a mythic HYBRID at 40px in motion** — the feather→fur material
   split is the chimera tell.
2. **Read clearly DISTINCT from the shipping bald-eagle skin.** The eagle is
   "white head + hooked beak." The griffin must add the second material: a
   furred lion rear, a tufted lion tail, and a visible feather|fur seam — so
   the back half is unmistakably lion, not just a browner eagle.

Palette anchored on the brief: `#E8C24A` lion fur, `#8A5A1E` wing feathers,
`#F4E4B8` pale head feathers, `#3A2A12` beak/eye, `#C9A23A` rim — varied per
variant. Sheet shows each at hero 130px plus the honest 40px NEAREST-x3
gameplay read, over both night and bright-day backdrops.

## The five takes (genuinely different, not tweaks)

**V1 · HERALDIC REGAL** — the textbook griffin. White eagle head, a CLEAN
diagonal feather→fur seam slicing across the body (pale feathered chest over a
tawny lion rear), modest ear-tufts, a large dark-tipped lion tail tuft.
- 40px tell: pale-head + white feathered front vs tawny lion rear, split by a
  crisp diagonal seam; the tuft hangs off the low rear.
- Weak spot: the diagonal seam is the most eagle-adjacent of the five — the
  front-half whiteness risks reading like "eagle with a gold butt" if the seam
  doesn't survive the downscale. The lion haunch swirl + tail carry the
  distinction.

**V2 · FIERCE GOLDEN RAPTOR** — pure predator. All-gold head (no white), a
heavy angled brow, a WIDE aggressive wing-span that opens further on the
powerful upstroke, a tighter compact lion body, a small flicking tail tuft.
- 40px tell: rich-gold raptor front over a darker tawny rear with splayed open
  wings — the most menacing, top-tier-feeling read.
- Weak spot: dropping the white head loses the cheapest two-tone signal; the
  whole front is gold-on-gold, so the feather|fur split leans entirely on the
  brow + beak + the rear-body value drop. Most monochrome of the set.

**V3 · MANED TWO-TONE STACK** — the boldest split. A near-VERTICAL feather|fur
seam down the middle (pale feathered front half / tawny furred rear half),
joined by a dark LION MANE ruff collar at the neck — the literal eagle-meets-
lion join. White head, a big bushy tail curling UP behind.
- 40px tell: the vertical feather|fur seam + the dark mane ruff where the two
  creatures fuse — the most explicitly "two animals stitched together" read.
- Weak spot: the mane ruff is fine radiating strokes that can clump into a dark
  blob at 40px; if it reads as a shadow rather than fur it weakens. The upcurl
  tail is the safety net.

**V4 · SOARING WIDE-WING** — the flight read. ENORMOUS swept raptor wings
dominate the silhouette with a big slow beat (deep-down to high-up); a compact
lion rear is tucked low between them; the white head thrusts forward; the
tail-tuft flicks UP on the up-pose (per the brief's "tuft flicks on the
up-pose").
- 40px tell: the huge wingspan + the tucked two-tone body and head between the
  wing roots — the most dynamic, in-flight read.
- Weak spot: the wings are so large they can eclipse the small lion body at
  40px on the down-pose, momentarily costing the hybrid read; the body must
  stay legible between beats. Most reliant on motion.

**V5 · CUB CHIBI GRIFFIN** — casual-arcade charm. A round big-headed warm-gold
cub: creamy fluffy head feathers, tiny round ear-tufts, a short stubby beak,
big friendly eyes, and an OVERSIZED fluffy tail tuft that bobs with the flap.
The split is soft (creamy feathered belly / golden fur rear).
- 40px tell: big pale head + the giant fluffy tuft on a round golden body —
  the friendliest, most collectible read; fits Skybit's playful identity.
- Weak spot: the cute treatment softens the "fierce mythic apex" framing the
  late-game tier may want; the beak is short so the raptor signal is the
  weakest of the five. Trades majesty for charm.

## Cross-cutting notes

- All five keep the lion body mass anchored at (32,44) for the fixed 14px
  collision circle; wings/head/tail break the silhouette around it.
- The tail tuft is drawn as a chunky blob + radiating strokes specifically so
  the back-end lion tell survives the 40px downscale (thin whips vanish).
- Day vs night: the pale heads (V1/V3/V4/V5) pop against night but flatten
  against bright day; the gold of V2 does the reverse. The house outline pass
  (`_add_outline`) helps both — worth confirming which variant the
  art-director finds most robust on the brighter sky.
- Procedural-only, no PNGs; both build targets unaffected (pure Pygame draw
  calls + the shared prebuilt-skin factory).
