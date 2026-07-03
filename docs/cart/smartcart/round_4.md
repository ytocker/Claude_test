# SMART CART — round 4 (FINAL geometry pass)

Sheet: `docs/cart/smartcart/round_4.png`

## The one blocker, fixed in RENDERED pixels (not just spec)

The screen-mount no longer reads as a hooded head. Verified directly from the
rendered crops in `round_4.png` (the 3x reference, the 1.6x row, and — the real
truth test — the true play-size DAY / NIGHT / GRAYSCALE strips), not from the
description.

### What changed (geometry only)

1. **Bezel is now a TRUE THIN RIM.** The screen footprint is 18x10 and the dark
   teal bezel is just `screen.inflate(3, 3)` — an even ~2px border hugging the
   glass on all four sides. There is no dark mass sitting above, left, or behind
   the glass anymore; every dark pixel is within ~2px of the glass rectangle.
   This removed the overhead/overhang mass that was the hood.
2. **The POST + SKY GAP actually render at play size.** The gap was widened to
   14px and the post was rebuilt as a mostly-BRIGHT column (3px `POST_HI` lit
   front + 1px `POST_LO` shadow back) instead of a thin dark stick. A bright
   stalk against open sky survives the smoothscale to ~44px, where a dark stick
   used to vanish into the gap. The post sits UNDER the flight-rear of the
   screen so the screen genuinely floats ON it, with open sky on BOTH sides.
3. **Floating-on-post silhouette, gap exaggerated.** The screen now sits clearly
   ABOVE a visible band of background, not in the half-bonded state of round 3.
4. **Top corners squared.** The bezel border radius dropped to 1 so the upper
   edge reads "device", not "helmet dome".

### Verified from the rendered 40px DAY + NIGHT crops

- **DAY play-size strip (light-blue swatch):** a bright POST and a clear band of
  light-blue SKY are visible between the bottom of the dark screen and the top
  of the white basket. Sky under the screen is plainly visible — PASS.
- **NIGHT play-size strip (dark swatch):** same separation reads; the bright post
  + glowing visor float above the basket, and the additive teal bloom lights the
  upper steel and spills into the dusk.
- **GRAYSCALE strip:** the screen-on-a-post silhouette and the gap survive in
  pure value — the dark mass is a small rounded screen, not a head-cap; the post
  + gap break the screen away from the basket.
- **3x reference crop:** small teal-rimmed screen, generous checker (sky) gap
  beneath it, bright post bridging down to the squared basket. No hood, no cowl.

### Locked elements — untouched (confirmed intact on the sheet)

- Additive night bloom: still stamped before the bezel, still pulses with
  `_GLASS_LEVEL`; visible on the night gameplay frame and the night strip.
- `_GLASS_LEVEL` whole-screen value-pulse (hot to dim to hot to dark floor) and
  the fixed frame-3 floor (`SCREEN_FLOOR`, never black) — unchanged across the
  4-frame row.
- Squared white-steel basket, bold dark wheels + teal hubs, low teal cargo,
  day teal/white hierarchy, and the glass rectangle itself — unchanged. Only the
  dark mass AROUND the glass was shrunk.
