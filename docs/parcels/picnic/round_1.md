# PICNIC BASKET — parcel cosmetic (MID tier) — Round 1

The tiny gift Pip carries below him (~22px), rotates with the bird's tilt.

## 22px read
A wide rounded WICKER body with a tall DOUBLE-ARCH handle springing from the
rim and a cream-and-red CHECK CLOTH bulging over the rim. The combined glyph
is handle-arch-over-fat-rounded-body, with the bright check lump breaking the
rim line — that spill gives it the "full" cosy-domestic personality the takeout
pail and the gift boxes lack. Body is one warm colour + the red/cream check;
weave is only suggested so nothing muddies at 22px.

## Palette
- Wicker body: gradient `#C59658` (lit) → `#B98A4A` base → `#926836` (shaded belly).
- Weave hatch: `#7E5A2A`, used for the rim band + two thin courses + short rim ticks.
- Cloth: red check `#D9433A`, cream ground `#F4ECE0`, plus a `(255,252,246)` crest catch.
- Outline / keyline: dark high-value `#34200F` baked behind body, handle, and cloth lobe so it reads on the bright day sky (`sky_bot≈(170,220,245)`).
- Night: the warm wicker + dark keyline carry the silhouette on the dark sky; the cream/red cloth stays bright. No separate night surface — mode-agnostic single sprite.

## Tilt survival (−25 / 0 / 30 / 60 / 90°)
- The handle arch is the rotation anchor: a 5px dark keyline under a 3px cane
  (≈2.5px / 1.5px at 22px) survives both the smoothscale and the bank.
- −25° / 0° / 30°: reads cleanly as basket + handle + cloth.
- 60°: handle arch tips but still reads as a handled vessel; cloth check
  still visible.
- 90° (extreme bank, brief end of arc): compresses to a warm rounded lump
  with the handle edge-on — reads as "object with a handle," consistent with
  how the takeout pail behaves at the same angle. Acceptable for the rare
  full-vertical frame.
- Grayscale row confirms value separation: the glyph holds without relying on
  hue.

## 22px risks
- The double-arch twin-band tell is subtle at 22px — at the smallest read it
  can flatten toward a single arch (silhouette still correct). If the
  art-director wants the "double" more explicit, widen the gap between the two
  handle legs or split the cane into two distinct lines.
- The check pattern resolves as a few red blocks on cream rather than a true
  grid (intentional — a fine grid dies at this size). Could push one more red
  block if it needs to read as "tablecloth" harder.
- At 90° the cloth bulge can crowd the handle feet; if flagged, trim the lobe
  width by ~2px.

## Contract
`build(mode="normal") -> 22×22 SRCALPHA`, built at 44×44 then smoothscaled to
22. Procedural pygame only, mode-agnostic static surface, reuses
`game.parrot._lerp_color`.
