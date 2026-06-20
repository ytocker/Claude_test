# Animals expansion — final 11 (curated from brainstorm.md)

Grows the ANIMALS store category 9 → 20. Existing 9 kept as-is. Prices chosen so
the new creatures spread across the cost-sorted store and the 4 legendaries form
a natural "page 3" legendary tier.

## The 11 new creatures

| # | skin id | name | tier | cost | non-winged? |
|---|---------|------|------|------|-------------|
| 1 | `skin_pufferfish`   | PUFFERFISH   | late-game  | 620  | ✓ |
| 2 | `skin_chameleon`    | CHAMELEON    | late-game  | 680  | ✓ |
| 3 | `skin_red_panda`    | RED PANDA    | late-game  | 740  | ✓ |
| 4 | `skin_sugar_glider` | SUGAR GLIDER | late-game  | 820  | ✓ (glide) |
| 5 | `skin_axolotl`      | AXOLOTL      | late-game  | 900  | ✓ |
| 6 | `skin_mantis_shrimp`| MANTIS SHRIMP| late-game  | 980  | ✓ |
| 7 | `skin_griffin`      | GRIFFIN      | late-game  | 1100 |   |
| 8 | `skin_thunderbird`  | THUNDERBIRD  | legendary  | 1800 |   |
| 9 | `skin_cosmic_jelly` | COSMIC JELLY | legendary  | 2200 | ✓ |
| 10| `skin_aurora_stag`  | AURORA STAG  | legendary  | 2800 | ✓ (antlers) |
| 11| `skin_kitsune`      | KITSUNE      | legendary  | 3500 | ✓ (tail-fan) |

## Resulting cost-sorted ANIMALS pages (20 total, 8/8/4)

- **Page 1:** bee 400, owl 480, toucan 480, penguin 520, bat 520, flamingo 560,
  **pufferfish 620, chameleon 680**
- **Page 2:** eagle 700, **red_panda 740, sugar_glider 820, axolotl 900,
  mantis_shrimp 980, griffin 1100**, dragon 1200, phoenix 1500
- **Page 3 (legendary tier):** **thunderbird 1800, cosmic_jelly 2200,
  aurora_stag 2800, kitsune 3500**

## Dropped from the 16

Jellyfish (folded into the legendary Cosmic Jelly), Hummingbird (overlaps Bee),
Quetzal (reads "fancy bird" beside toucan/flamingo), Seahorse (hardest 40px
read), Flying Fish (a second fish alongside Pufferfish).

## Legendary spectacle constraint

A skin getter only receives `(frame_idx, tilt_deg)` and returns one static
sprite per frame — there is no live particle system feeding the skin. So all
"glow / shimmer / lightning / stardust / aurora" spectacle must be **baked into
the 4 sprite frames** (e.g. a glow halo + energy accents drawn on the sprite),
and any "pulse" must be expressed by varying that spectacle across the 4 wing
frames. It must still read cleanly at 40px.
