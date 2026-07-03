# HAND-BASKET — round 2

Round 1 got `VERDICT: ITERATE`: the deep red bucket read well, but there was a
STRUCTURAL BLOCKER — the skin's own cargo read as a box on the basket front and
collided with Pip's real (game-composited) parcel, the handles fused into one
hump, and the groceries washed to one pale blob in grayscale. This round fixes
all of that while keeping the bucket silhouette, flare, rim cap, slot ribs, the
night keyline strategy, the day value contrast, and the jostle amplitude.

## What changed (punch list)

1. **Removed the self-drawn gift-box motif (the blocker).** The skin now draws
   NO parcel/box of its own. The grocery trio is re-anchored to the rim TOP so
   every lump pokes OVER the rim line; nothing drops onto the basket front face
   where it would read parcel-shaped. The only parcel in the composited frame is
   Pip's real one, slung below by the game.
2. **Re-opened the twin-handle apex.** Apex base parting widened from ±2 to ±4
   px (plus sway), the loop lean increased to 5px, and a 1px interior shadow gap
   (`BASKET_DEEP`) is carved straight down the centre of the apex — both in the
   first `_handles` pass and re-carved in the `_handles_top` restate. The two
   loops now hold as two distinct loops at 40px instead of fusing into one hump.
3. **Spread the grocery VALUES for grayscale.** Three distinct value rungs,
   dark→mid→light:
   - bottle pushed DARK (`#C4404E` / cap `#362C28`) — the dark rung,
   - green fruit pushed to MID (`#4E8634`, was a pale `#6FB24A`) — the mid rung,
   - bread kept LIGHT (`#F0E8D6`) — the light rung.
   The grayscale strip now shows three separable lumps re-stacking, not one
   pale blob.
4. **Verified basket sits ABOVE Pip's parcel.** In the zoomed day/night flyer
   crops, the only box is the game's brown/pink-ribbon parcel composited below
   the basket centre (`PARCEL_Y_OFFSET = 12`); the basket body and rim sit above
   it. Read = "basket + cargo slung under", not "basket with a box in it". No
   double-parcel.
5. **Pulled the day handle highlight down ~10%.** `HANDLE_HI` softened from the
   bright rim-pink `#F2C9C5` to a muted `#E0968E` so the loop no longer reads as
   a plasticky-glossy rail on the bright day sky. The full pale keyline at night
   is still delivered by the house silhouette outline on the loop, so the
   night-keyline strategy is intact.

## Read confirmation (40px target)
- **No self-drawn parcel:** confirmed — the basket front is clean; only Pip's
  composited parcel appears below the basket centre (visible in both flyer
  crops as the brown box with the pink ribbon).
- **Twin handles = two loops:** confirmed — the dark apex gap keeps the two
  folding loops distinct at 3x and at play size, on both day and night skies.
- **Three grayscale values:** confirmed — the grayscale strip lands the bottle
  (dark), green fruit (mid) and bread (light) on three separate values, so the
  jostle reads as discrete lumps re-stacking rather than one blob.

## KEPT from round 1
Bucket silhouette + flared U walls, rounded base, bold lipped rim cap with the
pale rim highlight (night keyline), low-contrast vertical slot ribs, the deep
red day/night value hold, and the per-phase jostle amplitude (bob + horizontal
shuffle of the trio across the 4 poses).

## Render
`docs/cart/basket/round_2.png` (DAY gameplay | NIGHT gameplay | 3x / play-size /
grayscale reference). Regenerate:

```sh
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python docs/cart/basket/render.py
```
