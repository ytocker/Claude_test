# MESSAGE BOTTLE — Round 1

MID-tier PARCELS cosmetic. A corked bottle laid HORIZONTALLY with a rolled
cream scroll inside — adventure mail. The one wide-not-tall object in the tab.

## 22px read
- **Left → right silhouette:** round sea-glass belly, a tapering shoulder that
  pinches into a beefed-up neck, then a warm cork nub at the tip. The
  neck-and-cork profile is the iconic tell.
- **Contents:** a cream rolled scroll fills the belly — a horizontal capsule
  with two concentric coil end-caps (sells "rolled paper") and two faint
  writing ticks for "a message". Cream is the highest value on the sprite, so
  it carries the read both day and night.
- Single bold dark outline as one closed polygon; glass is one colour family
  (green wall → lighter core), cork is the only warm accent.

## Palette
- DAY glass wall `#5FA88C` over lighter translucent core `#9FD3BC`, drawn at
  ~92% alpha so it reads translucent on the bright sky.
- Cork `#C9A368` with a `#E3C695` lit top edge.
- Scroll cream `#F2E7C8` (lit half) over `#CEBD93` roll-shading.
- Outline `#163229` — dark, high-value, holds the silhouette on sky_bot≈(170,220,245).
- One diagonal glass-highlight streak high on the belly (off-white, the glass
  specular cue), plus a short bright dab at its start.

## Tilt survival (−25 / 0 / 30 / 60 / 90°)
Bottles read on their side, so rotation reinforces rather than fights the
glyph. Across the row the belly+neck+cork mass stays one recognisable
silhouette; at 90° it reads as an upright bottle. The cream scroll keeps a
visible warm core at every angle on DAY, NIGHT, and grayscale swatches.

## 22px risk (esp. the neck)
- **Neck** is the fragile zone: beefed up to 5px half-height at 2× (~2.5px at
  22) and reinforced with a dark cork-seam line so it doesn't vanish in the
  smoothscale. Watch that it doesn't read as a second bulge rather than a pinch.
- **Cork** is small; the warm hue separates it from the green glass, but at the
  smallest read it can blur toward the neck — the seam line is what keeps them
  distinct.
- **Scroll coils** are 2px detail; they survive at hero/zoom but soften at true
  22px to a cream bar — still on-message, just less obviously "rolled".
- Translucent alpha is tuned for DAY; on NIGHT the glass darkens, so the cream
  scroll + outline do the legibility work as intended.
