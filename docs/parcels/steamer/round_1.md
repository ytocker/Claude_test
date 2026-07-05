# BAMBOO STEAMER — Round 1

A stacked dim-sum bamboo steamer carried below Pip (~22px), MID tier.

## 22px read
A TALL ringed-drum tower: two shallow stacked bamboo cylinders capped by a
domed lid with a small knob, and a faint steam puff blooming above. The read is
carried by the horizontal banding — each drum has a dark band-shadow seam at its
base, so the silhouette is unmistakably "stacked steamer" rather than a smooth
tube. The proportion (narrow, tall, ringed) sets it apart from every box / bag /
jar in the parcel set, which are all squat. Built at 2× (44×44) then
smoothscaled to 22 so the outline and band seams stay crisp.

## Palette
- DAY: pale woven bamboo `#D8B877`, band shadows `#A07C3C`, lid rim `#7A5A28`,
  dome sheen / highlight `#EFDFB4`.
- NIGHT: same warm bamboo body holds on the dark sky via the dark keyline; the
  steam puff is the warm `#EFE6D2` glow that blooms above the lid.
- OUTLINE `#2C1C0E` — dark, high-value edge baked all around so the silhouette
  holds on the bright day sky (sky_bot ≈ 170,220,245).

## Tilt survival
Steam is kept tiny and centred on top of the lid (three stacked alpha puffs),
so when the sprite banks at −25/0/30/60/90° it stays attached and reads as a
short bloom rather than smearing into a tail. The ringed drums + dome carry the
read on their own at every angle; grayscale confirms it survives on value alone.

## 22px risk
- The lid dome is only ~12px tall at 2×; at the smallest read it can flatten
  toward looking like a third ring. The knob + sheen arc are there to keep it
  reading as a lid — worth checking the art-director agrees it separates.
- Band seams are 2–3px at 2×; if smoothscale softens them too much the "stacked"
  cue could weaken. Could push band-shadow contrast if needed.
- Steam puff is faint by design (low alpha) so it doesn't dominate or smear on
  tilt — it may read as nearly invisible on the brightest day patches.
