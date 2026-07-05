# BURRO PINATA — Round 2

Sheet: `docs/pinata/burro/round_2.png`
Build: `docs/pinata/burro/build.py`

Round 1 verdict was ITERATE: reads as a quadruped piñata, but the rear-leg
pair collapsed, the trot was masked by the parcel, the head read fox/corgi,
and the night lower-body faded. This round addresses all four punch-list
notes. KEPT: barrel-not-ball body, upright neck, two-ear-nub head, cream top
keyline, festive crepe bands/tassels.

## What changed

**1. Rear-leg pair rescued.**
- Widened the front-pair↔back-pair gap: front pair now reaches `+3/+7` px and
  the back pair `-3/-7` px from their hips, leaving a clear empty gap between
  the two pairs so they never merge into a single rear peg.
- Recoloured the BACK tassels from dark brown (`HOOF`) to BRIGHT festival
  hues — `back-far = ORANGE`, `back-near = PINK`. The dark hoof is now just a
  tiny 2px nub *under* a fat bright bulb. All four tassels (orange/pink front,
  orange/pink back) read as distinct light blobs.
- Each tassel bulb got a 1px cream keyline rim so the rear nubs glow off the
  night sky as well as the day sky.

**2. Trot tell moved to the OUTER leg edges + body bob.**
- The OUTER legs (frontmost `front-near`, rearmost `back-near`) now swing
  `×4` while the inner legs swing `×1.5`, so on the OUT frame the outer legs
  splay noticeably PAST the body half-width and on the TUCK frame pull under.
  Because Pip's parcel hangs over the body centre (PARCEL_Y_OFFSET = 12px,
  centred on the bird), the swing now happens at the body edges where the
  parcel cannot mask it.
- Body bob widened to ±2px (was effectively −2..+1), so the head visibly
  rises and falls above the parcel across the 4-frame cycle.
- Verified against the LIVE frames (parcel composited), not the clean strip —
  see day/night gameplay panels.

**3. Head pushed toward DONKEY.**
- Lengthened + bluntened the muzzle: a pale `SNOUT` muzzle barrel plus a
  blunt nose cap extends ~2px further forward in +x, with a cream nose
  keyline. Confirmed the head faces +x (forward / direction of travel).
- Raked both ear nubs BACK (lean toward −x, `-4`/`-3`) instead of
  forward-perky — the round-1 fox/corgi tell.
- Shrank the pink cheek block (6×5 from 8×6) so the long pale muzzle, not the
  pink cheek, dominates the head read.

**4. Night lower-body lifted.**
- Added a thin cream keyline arc along the BOTTOM edge of the turquoise band
  (same trick already saving the top edge), plus the cream-rimmed bright rear
  tassels. The lower body no longer vanishes into the night sky.

## Verification (round_2.png)

- **Four distinct legs in grayscale:** the bottom grayscale strip shows four
  separate light leg blobs per frame with a visible gap between the front and
  back pairs — no "3 legs / sitting dog" collapse.
- **Four distinct legs at night:** the NIGHT play-size strip and the live
  NIGHT gameplay panel both show four bright tassel nubs (the cream rims +
  bright hues hold them off the dark sky).
- **Trot reads with the parcel composited:** in the live DAY and NIGHT panels
  the parcel sits over the body centre and the outer legs splay past it; the
  head rises/falls over the parcel across frames.
- **Head reads donkey:** long pale blunt muzzle facing +x, two back-raked ear
  nubs, small pink cheek — no longer fox/corgi.

The DAY+NIGHT gameplay frames at ~40px are the verdict; both render the burro
as a four-legged festival donkey piñata carrying Pip's parcel.
