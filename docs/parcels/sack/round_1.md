# BURLAP SACK — LOW tier — round 1

## The 22px read
A cinched-neck burlap loot sack: a fat onion/teardrop body bulging at the
BOTTOM, pinched to a small tied NECK with a chunky knot nub on top. The
bottom-heavy bulge + pinched neck is the universal "stuff inside a tied bag"
silhouette and the only soft, organic, non-boxy shape in the low tier (the
boxes are all hard rectangles). Built at 2× (44×44) and smoothscaled to 22 so
the curved onion outline stays crisp.

## Palette
- Body gradient: lit tan `#C9A36B` at the top → darker base shadow `#8C6A3A`
  at the bottom bulge, giving the bag visual weight.
- Tie-cord band + knot dot: dark cord `#5A4424`.
- Warm keyline `#E8C98A` along the lit upper-left belly + the neck cinch, so
  the brown body separates from the dark NIGHT sky instead of disappearing.
- Outline: dark high-value `#261A0C` baked as a fattened polygon under the
  fill — one bold edge that carries the read on the bright DAY sky.
- Two faint pucker folds gathering from the neck (cloth, not stitching) for
  just enough burlap texture without dying at 22px.

## How it survives the tilt rotation (−25 / 0 / 30 / 60 / 90°)
The silhouette is profile-robust: a rounded bulb with a single distinct nub
poking out one end. That bulb-plus-nub reads as a tied sack from any bank
angle — there is no "correct upright" detail it depends on. The chunky neck
nub and cord band are deliberately fat so they stay legible even when the bag
is rotated to 90°. Grayscale tilt row confirms the value contrast (dark
outline vs tan body vs dark cord) holds without colour.

## 22px risk
- The neck/nub region is the smallest feature; it was sized chunky on purpose,
  but at extreme tilt the cord band and nub can read as a single dark cap —
  acceptable, still "tied," but a candidate to push if the art-director wants
  the knot crisper.
- The two pucker folds are near the resolution floor and may blur to faint
  shading after the downscale — they are intentionally non-load-bearing so the
  read does not depend on them.
