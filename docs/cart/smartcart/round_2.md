# SMART CART — round 2

Round 1 got `VERDICT: ITERATE`: strong distinct silhouette, but the night
BLOOM was absent, the tell was a scan-bar POSITION (not a value pulse, so it
failed grayscale), and the screen read as a flush "helmet" rather than a
tablet-on-a-stick. Round 2 keeps the smart-cart identity and addresses every
note.

## What changed (punch list)

1. **Night bloom — BUILT.** `_glow_bloom` is reworked into a six-ring additive
   teal halo (pad 18, outer rings +32px) stamped BEFORE the bezel so the spill
   lands on the upper steel body and a few px into the sky. Against a dark dusk
   it BLOOMS dramatically (the legendary moment); against the pale day sky the
   same additive light has nowhere to go, so it stays restrained — no biome
   branch needed. Strength scales with the glass level so the bloom pulses with
   the beat. **Confirmed firing** in the NIGHT gameplay frame and in the 4-frame
   night strip.

2. **Whole-screen VALUE PULSE — the tell.** `_GLASS_LEVEL = (1.0, 0.40, 0.80,
   0.0)` now drives the GLASS's overall luminosity: f0 hot (near-white
   `#D8FFFA`), f1 dim mid-teal, f2 hot, f3 dark teal floor (`#104E4C`, never
   black). The grayscale strip shows an obvious **light → dark → light → dark**
   beat. The sweeping scan bar is demoted to a faint secondary accent
   (`_BAR_LEVEL`) and is no longer the tell.

3. **Frame 3 fixed.** The diagonal glare-streak is gone. The off pose is the
   SAME screen at the dark floor — pure dimming, **no new internal shapes**. The
   silhouette is identical frame-to-frame (verified across the 4-frame strip).

4. **Post / juts-forward.** The screen is lifted clear of the basket on a slim
   two-tone POST and cantilevered FORWARD (leftward) so it overhangs the front
   of the basket. A stubby mounting neck links post → screen's back corner, and
   an air gap with a visible sliver of post beneath the screen makes it read as
   a self-checkout TERMINAL ("tablet on a stick"), not a helmet/robot head.

5. **Day read preserved.** The dark teal bezel + a fixed inner top-edge
   highlight carry the screen edge on EVERY frame, so the screen never goes flat
   or flashlight-glitchy when the bloom is dialled down. Restrained by day, it
   earns its keep at night.

## Kept from round 1
- Squared (non-flared) basket + bold near-black wheels with bright keyline ring.
- Day colour hierarchy: white steel (`#E8F0F5`→`#8FA3B2`) + teal screen pop.
- Low teal-tinted cargo (`#60C4D2`), nudged lower so it never fights the screen.

## Verdict checks
- **Night bloom fires:** yes — clear teal halo spilling onto steel + dusk on the
  hot poses (f0/f2), restrained on day.
- **Grayscale pulse:** yes — light-dark-light-dark across f0→f1→f2→f3.
- **f3 no new shapes:** yes — pure dim of the same screen, silhouette unchanged.
- **Tablet-on-a-stick:** yes — screen lifted off the body, cantilevered forward,
  post sliver visible beneath.

## Render
`docs/cart/smartcart/round_2.png` rendered via the shared helper. The DAY+NIGHT
gameplay frames at ~40px are the verdict; the reference column carries the
4-frame 3x view, the play-size day/night strips, and the grayscale pulse strip.
