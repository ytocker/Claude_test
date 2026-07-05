# PAPER PLANE — Round 1

Secret ultra-premium **non-creature** flyer: the player's flapping bird becomes
a folded paper dart. There are no wings, so the 4 base wing poses
(`_WING_ANGLES = 50, 20, -10, -40`) are reinterpreted as a gentle **bank-roll +
nose-bob** — the whole rigid sheet pivots a few degrees about its mass centre
and the nose lifts as it "catches air." Mass stays anchored at **(32, 44)** so
the fixed 14px collision circle is fair regardless of how far the nose reaches.

Sheet: `round_1.png` — each variant at HERO 130px (day | night) plus the
40px NEAREST-NEIGHBOR x3 truth read (level / dive) on **both** a day sky and a
night sky, because a folded-paper value structure must survive both backdrops.

## The five takes

**V1 · NOTEBOOK (side view)** — the cleanest classic. A long pointed dart in
plain white, split by one dark central crease into a bright upper facet and a
cool-grey under-fold, with the keel fin standing up at the fold.
- *40px tell:* the sharp triangle silhouette + the dark crease line cutting it.
- *Weak spots:* the most "default" of the set; relies entirely on shading
  contrast, so on a very pale day sky the white-on-white top facet leans hard on
  the house outline to hold its edge.

**V2 · LINED-PAPER (3/4 view)** — slightly top-down so both swept wings show;
faint blue notebook rules on the lit wing + a red margin stripe down the fold.
- *40px tell:* the two bright wing-vees + the red centre stripe.
- *Weak spots:* the blue rules are sub-pixel at 40px and mostly vanish in the
  downscale — the red stripe is doing nearly all the paper-type work there.

**V3 · NEWSPRINT (side view)** — warm off-white newsprint with a grey text
speckle column and one bold black headline bar slashing the lit facet.
- *40px tell:* the dark headline bar against the bright fold (highest internal
  contrast of the set).
- *Weak spots:* the grey speckle reads as noise/mud at 40px; the headline bar is
  the only texture beat that truly survives.

**V4 · DOLLAR-BILL (3/4 view)** — folded from a banknote: money-green paper, a
pale portrait medallion at the fold, gold corner pips. Ties into the $-economy.
- *40px tell:* the green craft + the glowing pale portrait oval at its heart —
  the only colour-led variant, so it pops hardest on both skies.
- *Weak spots:* green is darker in value, so the lit/shadow facet split is
  subtler than the white variants; the gold pips are near-invisible at 40px.

**V5 · KRAFT (top-down, slightly crumpled)** — rugged brown kraft arrowhead seen
from above, a hand-drawn doodle star on one wing, soft crumple creases.
- *40px tell:* the warm-brown arrowhead + the deep central V-fold valley.
- *Weak spots:* top-down view makes it read a touch more like an arrow than a
  "plane"; the doodle star is charming at hero but fuzzes at 40px.

## Cross-set notes for the director

- Value structure is the whole craft: every variant uses lit-top / shadow-under
  facets so the fold reads at size. V1/V3/V5 carry it best; V2/V4 lean on a
  colour accent instead.
- Colour-led V4 (and the warm V5) separate from the sky most reliably; the pure
  whites (V1/V3) depend on the outline against pale day skies.
- All texture micro-detail (rules, speckle, gold pips, doodle) is hero-only
  candy — the silhouette + the single fold crease is what ships the 40px read.
