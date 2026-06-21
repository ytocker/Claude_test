# CACTUS PIÑATA — round 1

A prickly saguaro piñata in a tiny sombrero. One of 5 independent piñata
concepts; this one owns the **tall top-heavy vertical** silhouette of the set.

## The read (40px verdict)

- **Silhouette:** a tall vertical trunk + two THICK upturned side-arms (a "U" of
  arms) + a small tilted straw-sombrero nub on top. The only top-heavy vertical
  in the set, so it reads "cactus" before colour resolves.
- **DAY (sky_bot ≈ (170,220,245)):** green trunk + straw hat hold against the
  bright band; the house dark outline keeps the edge crisp.
- **NIGHT (phase 0.52):** the straw sombrero + pink/white flower dots pop against
  the dark; the cream crepe fringe (#FBF3DD) + pale spine ticks keyline the green
  so the body doesn't sink into the night sky.

## Palette

| role | colour |
| --- | --- |
| lit green band | `#3CA845` |
| shadow green band | `#2E7D38` |
| trunk edge / rib shade | `#226 0 2C` darks for roundness |
| straw sombrero | `#E7C56A` (+ shadow / highlight straw) |
| cream crepe fringe + keyline | `#FBF3DD` |
| flower petals | pink `#F48AB8` |
| flower core | white `#FFF6FA` |

Bands cycle hi/lo down the trunk so the stacked papier-mâché crepe rings read at
small size.

## Sway frame map (the 4-frame tell — NO wings, NO particles)

Driven by `parrot._WING_ANGLES = (50, 20, -10, -40)` → `_phase` → 0..3. The
trunk stays PLANTED; only the horizontal crepe fringe bands + the sombrero lean.

| phase | _WING_ANGLES | fringe lean (px) | sombrero tilt | pose |
| --- | --- | --- | --- | --- |
| 0 | 50 | −2.4 | −9° | lean LEFT |
| 1 | 20 | 0.0 | 0° | CENTRE (rest) |
| 2 | −10 | +2.4 | +9° | lean RIGHT |
| 3 | −40 | 0.0 | 0° | CENTRE (rest) |

The lean ripples down the body — top bands sway most (`lean * (1 − 0.7t)`), the
base barely moves — so it reads as a fringe FLUTTER, not a rigid slide or a
full-body rotation (velocity tilt is applied later by the engine; nothing is
baked here). Survives grayscale: the silhouette tilts and the pale fringe + spine
edges shift, a readable wobble carried by value, not hue.

## Contract

64×84 SRCALPHA; dominant trunk mass centred at (BCX,BCY)=(32,44); trunk extends
~22px up/down of centre but the visual mass sits at 44; collision intent = 14px
circle at (32,44). `build(wing_angle_deg) -> Surface`; cached getter via the
`game.animal_ufo._make_prebuilt_skin` pattern. Reuses `parrot._add_outline` /
`parrot._aaellipse`. Procedural pygame only — no raster assets, both targets.

## 40px risk to watch

- The upturned arms are short; at the very smallest scale they could compress
  toward the trunk shoulders and the "U of arms" could blur into the sombrero
  brim (the widest top mass). If the arms read as part of the hat, push them
  wider / lower or add a touch more gap between arm tips and brim.
- Six crepe bands down a 9px-half-width trunk is dense; if the fringe ticks turn
  to noise at play-size, drop to 4–5 bands.
- Flower dots are 1px features — they survive as colour pops but not as shapes at
  40px; they're carried as night-pop accents, not silhouette.
