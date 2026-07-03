# PAPER LANTERN — Round 1

HIGH-tier parcel cosmetic. The first GLOWING parcel: a red festival paper
lantern carried below Pip.

## 22px read
A round vermilion BODY between two flat GOLD CAPS (top + bottom), with a short
dark TASSEL hanging below and a tiny gold hanger loop on top — a glowing orb
pinched between two gold discs. The gold caps are the high-contrast keyline that
names the shape at tiny size; the orb is deliberately simple so it survives the
smoothscale to 22.

## Palette
- DAY — body vermilion #D63A2E shading to #A8261E at the rounded walls with a
  hotter #F26E52 lit spine; gold caps #E8B23C (sheen #FBDF8E, rim shadow
  #B08322); tassel dark maroon #7A2018; outline #3A100C.
- NIGHT — a baked ADDITIVE radial glow #FF7A55→#FFD08A blooming from the body,
  drawn UNDER everything so the lantern emits light.
- Ribbing: 4 faint vertical seams arced to the barrel + one bright catch-light
  sheen near the spine. Subtle by design — the glow does the work.

## Night glow
A stack of thin additive circles with a quadratic falloff (faint skirt, bright
heart) baked under the body. Reads as a faint warm halo in daylight and BLOOMS
against the dark night sky — its showpiece moment. Mode-agnostic single surface,
so the same baked glow serves both day and night scenes.

## Tilt survival
The body is a near-symmetric orb with no "up", so it rotates cleanly across the
full bank row (−25 / 0 / 30 / 60 / 90°). Caps + tassel are centred and narrow so
nothing smears into a tail when the sprite banks. Verified on the day, night,
and grayscale tilt strips.

## Carry-occlusion
Pip's red body/wing occludes the TOP, so identity is weighted to the LOWER/
visible half — bottom gold cap + tassel carry the read. The lantern's own red is
close to Pip's red, so separation leans on the GOLD CAPS and the warm glow bloom
rather than the red body.

## 22px risk
- The lantern red sits close to Pip's red in the carry crop; the gold caps are
  doing the separation work and could need more weight/contrast.
- The night bloom currently reads modest rather than dramatic; the showpiece
  glow could be pushed brighter/wider.
- Ribbing seams are near the threshold of visibility after smoothscale — they
  may read as texture noise rather than panels at true size.
