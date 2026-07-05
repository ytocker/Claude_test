# BAMBOO STEAMER — Round 2

Round 1 verdict was ITERATE: at 22px it read as a squat bucket/barrel, and the
hero/zoom appeared to show a different prop than gameplay. This round unifies on
ONE tall stacked steamer and fixes the proportion.

## What changed

1. **ONE unified prop.** The hero, zoom, gameplay and tilt now all render the
   exact same closed stacked bamboo steamer — the harness drives every panel
   from a single `build()`. There is NO handle-arch and NO gingham/checkered
   cloth anywhere in the build (there never was a basket/cloth in the drawing;
   the Round-1 "different prop" was the same sprite losing its silhouette at the
   downscaled gameplay size, which the new stepped/tall read fixes). Verified by
   re-reading the build — only tiers, lid, knob, seams and steam are drawn.

2. **Tall and narrow (~2:3).** The stack now stands ~32px tall in a ~24px-wide
   footprint. Height is biased into the STACK (three 7px tiers), not the lid
   (a thin 4px rim + 9px dome). It no longer reads squat.

3. **Stacked, not one tub.** Three shallow tiers each STEP inward by ~2px per
   side going up, so the silhouette tapers inward as a tower. Each tier has a
   dark `SEAM` (#6A4C20) at its base and a top weave-sheen, so the stack reads
   as separate woven drums rather than a smooth tube. The domed LID is a
   separate cap with its own overhang lip and a dark overhang-shadow seam — not
   a third ring.

4. **Sold steam.** A compact OPAQUE near-white puff (#FBF6EA, two overlapping
   3px/2px blobs + a tiny highlight) sits clearly ABOVE the lid, wrapped in a
   soft warm halo (#F0E4C8) so it blooms at night and stays visible on the
   bright day sky. It's the fastest steamer-vs-barrel cue and survives the tilt
   as a short bloom, not a tail.

5. **90° protected.** The lid rim is nudged off-centre and the dome cap is
   offset so the overhang lip is ASYMMETRIC; at a 90° bank it stays a stepped
   tower with a proud lid rather than flattening into a symmetric crate/door
   slab.

KEPT from Round 1: day/night dark keyline (#2C1C0E) holding the silhouette on
both skies, warm bamboo palette, band-shadow seam contrast, and grayscale value
legibility (the tilt grayscale row still reads as a stepped tower on value
alone).

## Confirmation

`round_2.png` reads as a TALL STACKED bamboo steamer at 22px on both the DAY and
NIGHT gameplay frames and across the full -25/0/30/60/90° tilt row: a stepped,
seam-banded tower under a domed lid with a visible opaque steam puff above. ONE
unified prop — no basket, no cloth, no handle anywhere.
