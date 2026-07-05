# SMART CART — round 1

**Concept.** The AI self-checkout cart (Caper / Amazon Dash idiom) as a secret
legendary-tier flyer skin. A sleek SQUARED basket on two wheels, topped by a
short handle post carrying a flat rectangular teal SCREEN that juts forward —
the "lollipop screen on a box" profile. Only cart concept with a squared
(non-flared) basket + an emissive screen-on-a-stick, so it reads instantly as
its own distinct, high-tech thing at 40px.

## The read (why it works at 40px)
- **Silhouette:** filled white-steel rectangle (vertical sides, NOT flared) +
  two bold dark wheels + a teal-glow rectangle riding a post ABOVE centre.
  The squared mass separates it from the flared-trolley sibling at a glance;
  the screen-on-a-stick is the "high-tech cart" tell.
- **All filled masses** — no wire. The 3 suggested verticals and mid band are
  heavy hints that may blur at true 40px without costing the silhouette.
- **Day:** white-steel body holds against the bright sky (~(170,220,245)); the
  teal screen is the colour pop.
- **Night:** the baked teal bloom makes the screen luminous against the dusk —
  the legendary moment. Confirmed in the NIGHT gameplay frame.

## Palette
- Body steel: `#E8F0F5` hi → `#DCE6EC` mid → `#8FA3B2` shadow; contour `#4A5C68`.
- Screen: core teal `#23D6C4`, bezel `#0E6E68`, deep glass `#093A38`, hot scan
  bar near-white `#D2FFF8`; baked outer bloom = `#23D6C4` additive at low alpha.
- Wheels: tyre `#2B3138`, bright keyline ring, steel hub plate.
- Cargo: cool teal-tinted (`#60C4D2`) so it reads as the cart's own goods and
  harmonises with Pip's parcel hanging just below centre.

## Signature tell — BLINKING SCANNER (no wings, no live particles)
Driven by `_WING_ANGLES = (50, 20, -10, -40)` → `_phase` → a 4-step value ramp.
Frame map:

| frame | wing° | scan level | screen read | sweep pos |
|-------|-------|-----------|-------------|-----------|
| 0 | 50  | 1.00 (peak) | hot scan bar + scan dot, full teal glow, max bloom | left   |
| 1 | 20  | 0.45 (dim)  | dim teal, faint bar, reduced bloom                 | mid-L  |
| 2 | -10 | 0.85 (peak) | bright bar returns, near-full glow + bloom         | mid-R  |
| 3 | -40 | 0.00 (off)  | bar gone, screen at dim teal floor, min bloom      | right  |

The scan bar's brightness IS the motion (bright → dim → bright → off) and the
baked highlight sweep travels left→right across the glass in lock-step, so the
screen feels alive even on the off pose. It is a PURE VALUE pulse — the
strongest grayscale tell of the cart set (confirmed: grayscale strip frame 0
vs frame 3 shows a clear light/dark swing). The off-pose screen never goes
fully black, so it stays in the silhouette.

## 40px risk
- **Screen-vs-cargo confusion:** the cargo block is also teal. Mitigated by
  keeping cargo low/inside the basket and the screen lifted ABOVE centre on the
  post; the post's vertical gap separates them. Watch that the two teal masses
  stay visually distinct at true 40px — a slightly cooler/desaturated cargo or
  a hair more vertical gap could buy margin if the director flags merge.
- **Post thinness:** the handle post is the only narrow element; it could thin
  out at 40px and let the screen look like it floats. It currently survives,
  but a 1px-bolder post is the cheap fix if the screen detaches.
- **Day bloom:** the additive teal bloom is subtle on the bright sky (correct —
  it should bloom mainly at night). The bezel + scan bar carry the day read so
  the screen never looks flat.
- **Wheels static by design:** all motion lives in the scanner; if the director
  wants a secondary life-signal, a 1px cart bob could be added without touching
  the scanner ramp.
