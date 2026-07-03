# BALLOON BASKET — Round 1

Tiny hot-air-balloon gondola Pip carries below him (MID tier). A fat
candy-striped DOME canopy dominates a small square wicker BASKET, joined
by two short cords — the "lollipop on a box" outline where the dome rules.

## 22px read
- A big round STRIPED DOME (top two-thirds of the glyph) over a compact
  wicker BOX (bottom). The two nearly touch; the thin cords are incidental.
- Candy tell carried by ~5 bold vertical bands (red / cream) — fine stripes
  would mush at 22px, so few wide bands hold the read.
- Each band shaded top→bottom so the dome looks round/inflated; a cream
  crown sheen on the upper-left sells the canopy.
- A short cream SKIRT with a dark underline reads as the balloon's open
  throat and visually separates dome from basket.

## Palette
- DAY: stripes red `#D8443C` / cream `#F3ECDC`; basket `#9A7038` (lit/shade
  gradient). Dark high-value OUTLINE `#2C180E` baked behind dome ellipse and
  basket so both pop on the bright day sky (sky_bot ≈ (170,220,245)).
- NIGHT: the canopy stripes hold their value (red stays saturated, cream
  stays bright); the warm basket keyline keeps the box legible on the dark
  sky. Verified on the NIGHT swatch + gameplay-night frame.

## Tilt survival (−25 / 0 / 30 / 60 / 90°)
- The bold round dome silhouette is rotation-invariant, so the dome/basket
  pairing reads at every bank — including 90° (dome leading) and the near-
  inverted banks. Confirmed across DAY, NIGHT, and GRAYSCALE tilt rows: the
  round-cap-over-box glyph survives even when value-only.
- Cords are short + thin and contribute nothing critical, so losing them in
  the smoothscale/rotation costs no legibility.

## 22px risk
- Stripe count vs. mush: 6px bands smoothscale to ~3px on the 22 sprite —
  the red/cream alternation reads but a denser stripe count would blur into
  pink. Kept deliberately coarse.
- At extreme bank the basket can tuck behind the dome's lower edge; the
  pairing still reads as a balloon, but the "two-part stack" tell softens —
  one to watch in the art-director pass.
- Cream skirt + cream stripes can merge at the dome base; the dark skirt
  underline is what keeps the throat distinct at small size.
