# BAMBOO STEAMER — Round 3

Round 2 verdict was ITERATE: the tall stepped-tower silhouette and domed lid
were KEEP, but the steam puff didn't read at 22px — it said "stacked food
container," not "hot steamer." This round rebuilds the steam to sell the read on
both skies and pins it to the lid through rotation; the tower stays as approved.

## What changed (verdict items)

1. **Steam reads at 22px.** The old two-blob warm dab is replaced by ONE bold
   lobed puff sized ~1.3× the lid width (`pw = lid_w * 1.32`), floated a clear
   gap above the dome crown. It is a COOL bluish-white (`#F4F9FF` fill, a
   `#FFFFFF` hot core, a cool `#C4D6E6` shaded underside) so it separates from
   the warm tan tiers in BOTH hue and value and pops on the bright day sky and
   the dark night pillar alike. One billow with a broad belly and two crown
   bumps — not fine wisps.

2. **Night/dark contrast.** A 1px dark micro-halo (`#323C4E`) is drawn under the
   puff as slightly inflated lobes, so a thin dark rim peeks out on every side
   and holds the silhouette on a LIGHT background; on dark backgrounds the bright
   fill itself carries it. The GRAYSCALE tilt row now shows the puff clearly on
   value alone — it does not lean on hue.

3. **Tier seams.** Only the TOPMOST seam (the lid/body break) is deepened
   (`SEAM_TOP #4A3214`, 2px). The two lower inter-tier seams are now a single
   quiet band-shadow line (`#A88442`, 1px) so they read as subtle steps instead
   of three competing dark stripes that turn to noise at 1×.

4. **Tilt 90° — steam pinned to the lid.** The steam is drawn LAST into the SAME
   surface as the tower (anchored to `dome.centerx, dome.y`) before the single
   smoothscale, so the whole sprite — puff included — is what the harness
   rotates. The puff now travels with the lid across `-25/0/30/60/90°` instead of
   detaching or vanishing.

5. **Lit faces lifted ~10%.** `BAMBOO` `#D8B877 → #E3C484`, `BAND_SH`
   `#A07C3C → #A88442`, `HILITE` `#EFDFB4 → #F6E8BE`, so the stepped form stays
   legible when the parcel is carried past a dark night pillar. The stack was
   also shortened by 1px per tier (`tier_h 7→6`) to free headroom for the bolder
   puff while keeping the tall stepped read.

KEPT from Round 2: the tall 3-tier stepped-tower silhouette, the domed lid with
its asymmetric overhang, the day/night dark keyline (`#2C1C0E`), and the warm
bamboo palette.

## Confirmation

`round_3.png` reads as a STEAMING bamboo steamer at 22px:

- **DAY** gameplay + day tilt swatch: the cool puff sits proud above the lid; the
  dark micro-halo holds it against the pale sky.
- **NIGHT** gameplay + night tilt swatch: the bright puff blooms clearly off the
  dark pillar/sky; tiers stay legible thanks to the ~10% lit-face lift.
- **GRAYSCALE** tilt row: the puff reads as a distinct bright billow on value
  alone, separate from the mid-value tower.
- **Tilt row** `-25/0/30/60/90°`: the puff stays attached to the lid and rotates
  with the tower as one piece.
