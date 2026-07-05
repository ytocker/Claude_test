# MINI UFO — Round 2

Sheet: `docs/parcels/ufo/round_2.png`
Build: `docs/parcels/ufo/build.py` → `render.py` →
`SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python docs/parcels/ufo/render.py`

Round 1 verdict was ITERATE: in carry Pip occluded the whole disc, the
beam-cone vanished, and the wide disc (the best tell) was hidden too high, so
it read as a metallic lump. Every note is addressed below.

## What changed

1. **Disc weighted to the visible lower half.** The whole saucer stack moved
   down (`disc_cy` 19 → 27 on the 44px canvas). The parcel rides ~12px below
   Pip, so the sprite midline (y≈22 / 11-at-22px) is where his belly cuts in.
   The full chrome ellipse now sits BELOW that midline and clears his belly;
   the dome is the only part that pokes up into the occluded zone — exactly the
   part allowed to disappear into his shadow.

2. **Beam survives carry.** The cone's mouth was widened (half-bottom 17 → 19/22)
   and flares all the way to the canvas floor (y=44), with higher core alpha so
   the cone spills clearly past Pip's body in both biomes even though its apex
   is occluded. It's the single most unique tell and it now reads carried.

3. **Hard top-edge break off Pip.** A 1px dark `OUTLINE` gap sits just above the
   disc's top lip with a bright `CHROME_HI` rim 1px below it — a hard
   value/hue edge so the chrome snaps off his red belly instead of fusing into
   his shadow.

4. **Teal in the visible carried portion.** A 2px `TEAL_RIM` glow plus a soft
   alpha bleed runs along the disc's LOWER leading lip — the part that always
   shows in carry — so the carried object keeps the chrome+teal contrast, not
   just bare metal.

5. **Day-carry beam contrast.** The cone gets a faint cool-dark `BEAM_EDGE`
   outline (slightly wider than the glow) plus a bright `#D2FFF8` `BEAM_STRIPE`
   core at high alpha, so the beam holds a defined shape against the bright day
   sky and day no longer relies on the disc alone.

KEPT: the tilt-row construction and the hero dome/disc proportions — the
wide-flat-disc + small-teal-dome silhouette is unchanged; only placement and
occlusion handling were fixed.

## Read confirmation (on the carry crops)

- **Day carry:** the wide chrome ellipse clears Pip's belly with the teal lower
  rim visible, and the cool-cored beam cone spills below his body. Reads as a
  UFO with a beam at 22px.
- **Night carry:** chrome disc + teal dome + teal rim + beam glow all clear Pip
  and read unmistakably as a flying saucer tractor-beaming his cargo at 22px.
- **Tilt row (day/night/grayscale):** the classic saucer silhouette holds across
  the bank arc; at level flight (0°) the beam cone is a clean downward triangle.
