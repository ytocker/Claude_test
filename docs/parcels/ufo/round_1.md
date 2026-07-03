# MINI UFO — parcel cosmetic (PREMIUM) — Round 1

## 22px read
A wide flat chrome **saucer disc** capped by a small teal **dome**, with a
glowing teal **beam-cone** spilling straight down beneath it. The silhouette
is the classic "hat-on-a-line-of-light": thin wide ellipse + tiny dome bump +
trapezoid of light. The beam is the unmistakable tell — nothing else in the
parcel set projects a cone of light or has a chrome metal body.

## Palette
- **Day** — chrome body `#B9C2CC` (lit crown `#E0E6EE` → dark underside
  `#5A6470`/`#3A424E`), teal canopy `#48D6C8` (crown `#AAF6EE`, base `#28968E`),
  dark keyline `#18222C` so the bright disc + dome pop on the day sky
  (`sky_bot≈(170,220,245)`).
- **Night** — baked teal **beam glow** `#7CF0E0` fading core→transparent down a
  trapezoid, a hotter inner core stripe `#D2FFF8`, and three tiny rim-light
  pips `#9FFFF0` with soft halos along the disc's leading edge.

## Night beam glow
The beam is baked on its own SRCALPHA layer as a downward additive vertical
gradient clipped to a widening trapezoid (apex hot under the disc belly, mouth
dissolving into air). It is composited with `BLEND_PREMULTIPLIED` so it adds
light rather than flat-fills, reading as a projected cone. On the dark night
sky the cone + rim pips glow; on day the same cone reads as a pale teal shaft.

## Tilt survival (−25 / 0 / 30 / 60 / 90°)
A glowing cone reads as a cone at any angle — when the disc banks the beam just
trails off the saucer instead of pointing at the ground, which is correct for a
carried object. The day / night / grayscale tilt rows all hold the disc+dome+
beam read across the full arc; the wide flat ellipse stays legible even at 90°
because the dark keyline preserves the silhouette.

## Carry-occlusion
The parcel hangs below Pip with its TOP partly hidden by his red body. The disc
sits high in the sprite so the entire beam-cone falls into the lower, visible
half — the wide chrome disc and the bright teal beam carry the identity while
the dome can sit in shadow. Chrome + teal contrast cleanly against Pip's red,
and the zoom crop confirms the disc + beam stay legible in carry context.

## 22px risk
- The beam can read faint against the bright day sky where the teal shaft has
  low contrast vs `#AADCF5` — the disc carries day, the beam carries night.
- The three rim-light pips are near the pixel floor; at 22px they may merge
  into the rim band rather than reading as distinct lights (acceptable — they
  spark the hull, the disc shape does the reading).
- The dome is small; if Pip's body occludes more than expected it leans almost
  entirely on the disc + beam, which is by design.
