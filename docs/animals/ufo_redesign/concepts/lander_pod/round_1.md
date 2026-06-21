# LANDER POD — round 1

## The read
A stout three-legged Apollo descent capsule hovering on stubby splayed struts.
The silhouette is a **rounded trapezoid** (wide flat top, narrower base) sitting
on **three short chunky A-frame legs with round footpads** that poke out below.
The legs + the negative space under the body ARE the identity — nothing else in
the UFO set has feet, so even at 40px it can't be confused with a domed saucer.
Legs are drawn FIRST and the body overlaps their hips, so the pod reads as
"sitting on its feet" rather than legs glued to a blob.

## Palette
- Body: warm brushed metal, vertical gradient `#C9CDD6` lit top → `#7A8290`
  shaded base, with a dark base lip so the body visually rests on the legs.
- Legs/footpads: near-black `#2B3038` struts (≥3px, footpads r=4) + a darker
  `#1A1B21` core seam — these dark feet carry the read against the bright day
  band and stay solid at night.
- Porthole: `#FFD24A` amber → `#FFF3B0` hot centre, in a constant dark `#3A3E48`
  bezel ring.
- Baked high-value keyline `#EEF2FA` on the flat top edge + upper-corner
  chamfers so the metal silhouette survives the brightest day sky.

## Porthole-dilation tell across the 4 frames
The single round porthole "eye" sits AT/above body centre (kept high because
Pip's parcel hangs just below centre in play, so the tell never gets buried).
It DILATES + BRIGHTENS one notch per pose (`_WING_ANGLES` 50→-40 maps to phase
0→3), legs STATIC throughout:

- **Frame 0 (50°):** closed — a small dark pupil (2px) in the bezel. The "off"
  state.
- **Frame 1 (20°):** aperture opens to ~r3, amber core, faint additive halo.
- **Frame 2 (-10°):** ~r4, core warms toward hot white, halo grows.
- **Frame 3 (-40°):** full dilation ~r5, hot `#FFF3B0` centre, widest additive
  bloom (strongest at night) — "powering up to lift off."

It's a **value pop** (dark dot ↔ bright bloom), not a hue shift, so it survives
grayscale (see grayscale strip). Legs/body geometry is identical in all four
frames, so the silhouette never wobbles — only the eye breathes.

## 40px risk
- Body is deliberately compact so the legs + footpad negative space dominate the
  read at play size; the trapezoid taper is subtle at 40px but the flat-top /
  splayed-feet contrast still reads as "lander," not "saucer."
- At full dilation the porthole bloom nearly spans the hull width; that's the
  intended "spun-up" peak, but if the art-director wants the metal hull to stay
  more present at frame 3, the bloom radius can be dialed back.
- Centre leg sits close to the two outer legs at this scale — could splay it a
  touch more if the tripod tripod-stance needs to read harder at 40px.
