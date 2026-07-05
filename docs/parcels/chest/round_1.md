# TREASURE CHEST — Parcel cosmetic (HIGH tier) — Round 1

A gold-banded pirate chest: Pip's aspirational "loot" parcel. Domed-lid trunk
with metal corner bands, a centre lock plate, and coin glints under the lid.

## 22px read
The glyph is **arched lid + band-cross + lock**: a rounded-top wood trunk, a
horizontal gold lid-band across the dome's base, two thick vertical gold corner
bands, and a single bright centre LOCK plate with a dark keyhole. Three coin
glints sit just under the lid seam to sell "loot inside". Even smoothscaled to
22 and re-tiled at ~26px in the tilt row, the dome + the gold cross + the lock
hold. Deliberately 2 vertical bands + 1 horizontal — a third vertical mushes at
this size.

## Palette
- DAY — wood `#7A4A22` (trunk) shading to `#523014`, dome lit `#A06C3A`; gold
  bands/lock `#E8B23C` with highlight `#FBE08A` and shadow seam `#A87A1E`;
  coin-glint `#FFE9A0`. Dark outline `#241208` for day legibility against the
  pale sky (sky_bot ≈ 170,220,245).
- NIGHT — gold self-pops against the deep sky; the lock carries a subtle glow
  `#FFD659` so it reads warm without a separate night build (mode-agnostic).

## Tilt survival (−25/0/30/60/90°)
Verified on the DAY/NIGHT/GRAYSCALE tilt rows. The lock stays dead-centre and
the band-cross is rotation-symmetric enough that the chest reads as a chest at
every bank, including the 90° nose-dive. No element relies on a fixed "up", so
the loot read never inverts or smears.

## Carry-occlusion handling
All identity is packed into the LOWER/visible half: the lid-band, both vertical
bands, the lock, and the coin glints sit on or below the trunk front, which is
the part of the parcel Pip does NOT cover. The dome TOP — the part Pip's red
body overlaps in carry (see HERO/ZOOM crop) — is plain wood, never red, so it
doesn't melt into Pip. The zoom crop confirms the gold + lock stay fully read
below the bird.

## 22px risk
The keyhole detail on the lock is the smallest feature and can blur toward a
dark dot at the tiniest reads; it's backed by the lock plate's bright gold so
the lock still registers even when the keyhole softens. The two vertical bands
sit close to the trunk edges — if a critique wants more separation they can be
nudged inward, at the cost of a slightly narrower lock gap.
