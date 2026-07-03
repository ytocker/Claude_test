# HAND-BASKET — Round 3

Sheet: `docs/cart/basket/round_3.png`

## The one blocker from round 2 (parcel composite) — FIXED

Round 2's only `ITERATE` note: in the live composited gameplay frame, Pip's
parcel rendered ON the basket front face, recreating the double-cargo read. The
parcel is composited by the GAME at a FIXED position — centred, hanging
`PARCEL_Y_OFFSET = 12`px below the bird centre. Mapped onto the 64×84 skin
canvas, the bird centre is `(32, 44)`, so the parcel centre lands at canvas
y≈56 and the 22px parcel sprite's TOP edge reaches up to canvas y≈45.

I could not move the parcel, so I adapted the BASKET: the bucket is no longer
anchored to the bird centre — it is pinned to its OWN base line and raised into
the upper half of the canvas. New geometry:

- `BOT_Y = 35` → the rounded base ellipse reaches its lowest pixel at canvas
  y≈41 (outlined frame bottom row = 43), which sits ABOVE the parcel top at
  y≈45.
- `RIM_Y = BOT_Y - 18 = 17` → an 18px bucket wall (shallower than r2's 30px so
  the base clears the parcel), still unmistakably a flared bucket.
- Handle rise dropped from 22px to 14px so the twin-loop apex crowns near the
  canvas top without clipping (outlined content top row = 1; ~1–2px headroom).

## What I see in the COMPOSITED gameplay frames at play size

DAY frame (`GAMEPLAY — DAY`) and NIGHT frame (`GAMEPLAY — NIGHT`), the actual
staged frames with Pip's real parcel composited:

- The basket sits clearly in the UPPER part of the flyer, and Pip's parcel
  hangs as a separate object BENEATH it. There is an unmistakable band of
  SKY (~4px at native scale, day blue / night purple) between the basket's
  rounded base and the parcel's top edge — they do not touch and do not
  overlap. The double-cargo read is gone: it reads as "basket up top, parcel
  dangling beneath on the sling," NOT parcel-on-body.
- This holds on BOTH skies. At night the pale rim keyline still holds the
  basket silhouette against the purple, and the sky gap is just as legible.

## Minor check — rounded base still reads

The basket's lower silhouette is still a soft rounded bucket base, not cramped
or sheared flat against the parcel: the base ellipse curves cleanly and the
flared walls + bold rim cap keep the bucket read. The shallower 18px wall did
not squash it into a card — the flare and the rim cap carry the "bucket".

## KEEP items (untouched)

- Twin-loop apex geometry + the 1px dark interior gap between the loops.
- 3-value grocery grayscale spread (dark bottle / mid green / light bread) —
  confirmed still distinct on the grayscale reference strip.
- Bucket silhouette / flare / rim cap / slot ribs.
- Deep-red day/night value hold.
- Softened day handle highlight + night keyline.
- No skin-drawn parcel/gift box (the only box in the frame is the GAME's real
  parcel, now cleanly separated below).
