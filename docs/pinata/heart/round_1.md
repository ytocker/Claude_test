# HEART PIÑATA — round 1

Secret flyer skin concept: a flying candy-heart piñata that replaces the bird.
One of 5 independent piñata concepts. Goal: read INSTANTLY as a heart piñata at
~40px in the real gameplay frame, on both day and night skies.

## Read (the verdict frames)

`round_1.png` columns: GAMEPLAY — DAY | GAMEPLAY — NIGHT | REFERENCE.

- **40px DAY** (sky_bot ≈ (170,220,245)): the saturated red→coral→white crepe
  fringe holds against the pale sky; the cream rim keylines the silhouette and
  the gold seam glow sits dead-centre. Reads "heart" immediately.
- **40px NIGHT** (deep-night biome keyframe): the pale cream rim + white top
  fringe band keyline the top lobes so the red never dissolves into the dark
  sky; the warm gold seam-glow is the bright anchor at the centre.
- **Silhouette:** a bold TWO-LOBE heart with a pronounced top cleft and a single
  pointed bottom — a pure symbol shape, zero appendages (no wings, no tassels
  poking the outline). The cleft is kept deep so it never reads as a round blob.

## Palette

| role | hex | use |
|------|-----|-----|
| fringe red | `#E22A48` | bottom crepe bands (the heart's dominant value) |
| fringe coral | `#F2607A` | mid crepe bands |
| fringe white | `#FFFFFF` | top crepe band — keylines the lobes at night |
| seam gold | `#FFD56A` | sugary seam glow (the night bright-anchor) |
| rim cream | `#FFF4E6` | 1px keyline rimming the whole heart |
| candy pink | `#FFA8C0` | the peeking heart-candy at full spill |
| sugar white | `#FFFCF4` | hot core of the seam + spill highlight |

Bands stack RED (bottom) → CORAL (mid) → WHITE (top), the real crepe-piñata
layering order, each with a 1px lower-edge shade + tiny fringe teeth so the
cut-paper depth survives shrink-down.

## Seam-split frame map (the signature tell — NO wings, NO live particles)

Driven from `parrot._WING_ANGLES = (50, 20, -10, -40)` → phase 0..3. A SINGLE
VERTICAL split runs down the centre cleft (deliberately not a radial crack, so
it can't be confused with a cracked egg/shell concept):

| phase | wing° | seam half-gape | glow radius | candy peek | read |
|-------|-------|----------------|-------------|------------|------|
| 0 | 50 | 0.6px | 3.0 | — | sealed; hairline seam, faint inner glow |
| 1 | 20 | 1.8px | 4.6 | — | seam parts, gold sugar-glow widens |
| 2 | −10 | 3.0px | 6.2 | full | full gape; one heart-candy peeks out (the SPILL) |
| 3 | −40 | 1.2px | 3.8 | — | reseals to a thin warm line, back toward sealed |

The cream split edges peel apart by `half_gape`; an additive gold glow column
(brightest at night) tapers from the cleft to the point with a hot sugar-white
core down dead-centre. **Grayscale survives as a clean centre-line value bloom**
— the seam is the brightest pixel column on the sprite, exactly centred (verified
on the grayscale strip).

## Contract compliance

- 64×84 SRCALPHA canvas; `COMPOSITE_W/H=64/84`, `DY=12`, `BCX,BCY=32,44`.
- Dominant heart mass + seam tell centred on / above (32,44); the candy peek
  rides just below centre at the cleft. Sits cleanly over the 14px collision
  circle at (32,44).
- `build(wing_angle_deg) -> Surface`; frames built lazily + outlined via the
  `game/animal_ufo._make_prebuilt_skin` getter pattern (used by render.py).
- Drawn UPRIGHT — no rotation baked; velocity tilt is applied later by the getter.
- Procedural pygame only; reuses `game.parrot._add_outline` / `_aaellipse`.

## 40px risk notes (for the art-director)

- **Seam-vs-"T" read:** the white top fringe band crosses the vertical seam, so
  at the smallest size the glow + top band can momentarily suggest a "T". The
  vertical split still dominates; a candidate fix is to dim/skip the top band
  directly over the seam channel, or push the candy-peek higher so the centre
  cue stays unmistakably vertical.
- **Candy peek at 40px:** the phase-2 heart-candy is ~3px and reads as a bright
  pink dab more than a discrete heart at true scale — it still functions as the
  "spill" beat. Could enlarge slightly if the art-director wants it legible as a
  candy.
- **Lobe cleft depth:** holds as a heart at 40px on both skies in the gameplay
  frames; worth confirming it doesn't round off when velocity tilt rotates it.
