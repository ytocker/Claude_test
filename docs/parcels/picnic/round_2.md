# PICNIC BASKET — parcel cosmetic (MID tier) — Round 2

Round 1 verdict was ITERATE: basket reads, but the check died in grayscale,
the double-arch handle was invisible/noisy, a gray band pooled between handle
and cloth, and the lobe spilled past the rim. Round 2 addresses each note.

## What changed (against the Round 1 critique)

1. **Bold blocky red CHECK that reads at 22px.** Replaced the scattered thin
   red blocks with a deliberate 2-row checker of ~3px (≈1.5px at 22) SATURATED
   red squares packed edge-to-edge on cream, the rows offset by one square so
   they alternate over/under like a real tablecloth. Red coverage and block
   size are now high enough to survive the smoothscale instead of dissolving
   into a pink smudge.
2. **The red now has a VALUE anchor, not just hue.** Darkened the cloth red
   from `#D9433A` to `#BE2624` (190,38,36) and brightened the cream ground
   slightly. The red is now meaningfully darker than the cream in luminance, so
   the checker still separates in the GRAYSCALE tilt row — the red squares read
   as distinct dark cells against light cream, not one flat gray lump.
3. **Single clean handle arch with an open SKY-HOLE.** Dropped the muddy twin
   band entirely. One arch now: a 5px dark keyline with a 2px cane laid inside
   and a single inner highlight for round-cane volume. Nothing is drawn across
   the area under the crown, so the carry-handle hole stays clear — the
   rotation-survival tell is now a clean arch-over-hole, not noise.
4. **Killed the gray band between handle and cloth.** The cane is narrow (2px)
   where it meets the cloth crown, and no mid-gray fill pools between them, so
   the handle crown meets the cloth cleanly with no phantom third material.
5. **Cloth CONTAINED within the rim.** Lobe half-width trimmed to 10px (< the
   15px rim half-width) so the bulge sits inside the keyline at every bank and
   can no longer spill past it to split the silhouette into two objects.

## Kept from Round 1 (no regression)
Wicker gradient (`#C59658`→`#B98A4A`→`#926836`), the dark `#34200F` keyline,
the restrained weave (rim band + 2 thin courses + short rim ticks, ≤3 lines),
and the strong upright / −25° / +30° reads.

## Confirmation
- **Day + night gameplay (22px):** reads as a picnic basket — handle arch over
  a fat wicker body with a red-check lump breaking the rim. The warm wicker +
  dark keyline carry the silhouette on the dark night sky; the cream/red cloth
  stays bright.
- **Red check reads, incl. grayscale:** the blocky saturated squares hold as a
  checker on cream in the DAY and NIGHT rows, and the darker red keeps distinct
  dark cells in the GRAYSCALE row instead of flattening to a smudge.
- **Single handle arch + sky-hole:** one clean arch with a clear open hole
  under the crown at upright / −25° / +30°; at 60°/90° it tips but still reads
  as a handled vessel. No twin band, no gray band, no spilled lobe.

## Contract
`build(mode="normal") -> 22×22 SRCALPHA`, built at 44×44 then smoothscaled to
22. Procedural pygame only, mode-agnostic static surface, reuses
`game.parrot._lerp_color`.
