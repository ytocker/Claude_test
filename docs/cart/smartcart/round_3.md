# SMART CART — Round 3

Verdict to clear: Round 2 = ITERATE. Bloom + whole-screen value-pulse tell +
frame 3 were SOLVED and KEPT untouched. The sole blocker was a geometry
regression — the "tablet-on-a-stick" fix had ballooned the dark bezel into a
large hood/cowl arcing up-and-behind the basket (reading as a hooded robot /
pram canopy at 40px) with the post invisible. Round 3 is a pure geometry pass on
the screen mount.

## What changed (geometry only — mount on the screen)

1. **Killed the cowl — bezel is a SCREEN again.** Removed the diagonal mounting
   "neck" arm entirely (it was the dark mass that wrapped up-and-behind the
   basket) and shrank the bezel back to a thin even border: `screen.inflate(2,2)`
   for the teal frame (was `inflate(3,3)`), glass at `inflate(-3,-3)`. The dark
   teal mass is now a tidy rounded rectangle framing the glass with an even rim —
   no arc, no wrap, no hood.

2. **Post visible + real air gap under the screen at 40px.** The screen now
   sits on a thin 3px two-tone post column (lit front edge / shadow back) that
   runs from the basket top up to a bottom-of-screen line lifted ~5px clear of
   the basket top (`gap_top = basket.top - 5`, `screen.midbottom = (BCX-3,
   gap_top-1)`). At 40px play size the blow-up shows an unambiguous band of
   sky/daylight UNDER the screen with the post bridging it — confirmed on both
   day and night backgrounds.

3. **Cantilever forward.** Screen centre is offset 3px toward the front
   (`BCX - 3`, leftward / the bird's forward) so its leading edge overhangs the
   basket front. The overhang + the gap underneath together sell "terminal on a
   stick".

4. **Bloom re-anchored to the smaller bezel.** The additive `_glow_bloom` is
   stamped on the new (smaller, higher) `screen` rect, so the teal halo re-centres
   on the compact glass and the night spill still lands on the steel below it —
   verified in the night frame: halo blooms around the small screen and washes
   the upper basket steel.

5. **40px silhouette re-checked: cart, not head.** Wheels + squared basket + a
   SMALL lifted screen-on-a-post. The dark shape on top is now clearly a separate
   floating screen (gap + post beneath it), not a helmet bonded to the body. Reads
   as a high-tech cart at 40px on both day and night sky.

## KEPT exactly (untouched)

- The additive night bloom (legendary moment) — only re-anchored to the smaller
  bezel rect, falloff/ring math unchanged.
- The whole-screen value-pulse tell — `_GLASS_LEVEL = (1.0, 0.40, 0.80, 0.0)`
  grayscale light → dim → light → dark ramp, with f3 a dim teal floor (never
  black, no new internal shapes).
- The fixed frame 3 (dark floor pose).
- Squared basket + bold dark wheels + white-steel / teal day hierarchy + the low
  teal cargo. No own parcel drawn.

## Confirmation

- Bezel is compact, a thin even border — NO hood / cowl / arc-behind. Confirmed.
- Visible post + real air gap UNDER the screen at 40px (day + night). Confirmed.
- Screen cantilevers forward (leading edge overhangs the basket front). Confirmed.
- Bloom + value-pulse intact. Confirmed.

Sheet: `docs/cart/smartcart/round_3.png` — the DAY + NIGHT gameplay frames at
40px are the verdict; both read as a cart, not a head.
