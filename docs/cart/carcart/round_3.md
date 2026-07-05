# KIDDIE CAR-CART — Round 3

Round 2 got `VERDICT: ITERATE`: RED leads and Pip's parcel separates (KEPT),
but the rear still didn't read as a BASKET — the fine wire cross-hatch was
sub-pixel at 40px so it blobbed into a dark grey cargo block — and the bounce
SQUASH broke the silhouette (the cabin bubble nearly vanished on the squash
frame). Round 3 fixes both without touching the wins.

## What changed (against the punch list)

1. **Rear reads as an HONEST open-topped basket in the car's colour family.**
   I took both halves of option (a)+(b): the fine cross-hatch is gone (it could
   never survive 40px), and the rear is now an OPEN-TOPPED container drawn with
   the cues that actually carry at play size —
   - a **lighter warm interior pocket** (`#D6A08A`) inset from the walls, with
     an elliptical mouth at the rim, so it reads as HOLLOW, not a slab;
   - **three BOLD 2px vertical staves** (instead of 1px hairlines that vanished);
   - a **bright top-rail keyline that ARCS over the open mouth** — the single
     cue that sells "basket" — plus a flat rim line under it.
   The whole basket is now **desaturated terracotta** (`#B0604A` wall,
   `#7E4032` shade) — IN the car's warm-red family, NOT grey. It stays smaller
   and dimmer than the candy-red hull, so RED still leads, but it no longer
   reads as a foreign cargo block.

2. **Squash tamed — the silhouette survives every frame.** HULL-WIDTH squash is
   capped at **+2px** (was +4) and the cabin bubble is now PROTECTED: its dome
   radius is near-constant across all four frames (at most a 1px flatten on the
   deepest squash, via `9 - min(sq_v, 1)`), so it never collapses. The bounce is
   now carried by **vertical travel (+4 drop / −3 lift)** against the fixed
   ground line plus a new **wheel-spread on the squash beat** (front wheel
   forward, rear wheel back) for the "springs compressed" read — not by crushing
   the hull. PASS TEST met: all 4 play-size frames read instantly as the same
   toy car, bubble dome intact on each.

3. **Parcel-brown vs rear-brown separated by hue + value.** The rear's warm
   terracotta is lighter and more orange-red than Pip's cool, darker brown
   parcel, so on the night frame's lower-right the parcel keeps clean value and
   hue separation from the basket above it — and the basket no longer competes
   with the candy-red hull either.

## KEPT (untouched)

- Candy-red hull value win + red-leads hierarchy.
- Clean lower-centre red shelf (parcel separates below an unbroken red car).
- Night cabin glint + white wheel-rim keylines.
- The REST-frame toy-car silhouette (bubble cabin, hood scoop, chrome bumper,
  fat hubcap wheels).
- No parcel drawn here — Pip's parcel is composited by the game.

## 40px verdict

`round_3.png` rendered via the shared helper on DAY and NIGHT gameplay frames:

- **Rear reads as a basket** — open-topped warm container with a visible lighter
  interior, bold staves, and a bright arcing top-rail; it is in the car's red
  family, not a grey cargo block.
- **All 4 bounce frames read as the SAME car** — the play-size strip shows the
  bubble dome preserved on every frame; squash sits low with spread wheels +
  headlight blink, stretch lifts and narrows a hair, both without breaking the
  silhouette.
- **RED still leads** on both skies; the terracotta basket recedes.
- **Parcel separates at night** — the warm terracotta basket keeps hue/value
  distance from Pip's cool-brown parcel on the lower-right.
