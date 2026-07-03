# COMET — round 1

PREMIUM, legendary/secret tier. The only parcel with NO container — a captured
shooting star, pure energy. Built at 2× (44px) then smoothscaled to 22.

## 22px read
A bright rounded white-gold STAR/ORB core blazing a tapering orange TAIL — a
glowing comma/tadpole of light. Reads as a streak from any angle: the core is a
tight bright cluster, the tail a smooth gradient stack of shrinking ellipses
that fades to transparent at the wispy tip. Four faint additive star spikes hint
"star" without breaking the round read.

## Palette
- DAY — white-hot centre `#FFFFF4`, white-gold core `#FFF4D0`, amber body
  `#FFC24A`, tail `#FFB052 → #FF8A3C → transparent`. Faint dark sky-side keyline
  `#6E3A10` on the core's upper rim to stop it washing out on bright day.
- NIGHT — warm additive halos baked under the core: inner `#FFD66A`, plasma
  skirt `#FF7A55`. The white-hot heart stays the single brightest cluster.

## Night bloom
Two stacked additive radial halos (quadratic falloff) sit UNDER the core. In
daylight they read as a faint warm aura; on the dark night sky they IGNITE into
a real bloom — the legendary spectacle. The white-hot heart is drawn last and
kept tight (≈0.34× core radius) so the halo can bloom but the core never mushes.

## Tilt survival (−25/0/30/60/90°)
The round core has no "up", so it survives every bank. The tail is drawn
trailing up-and-back from the core; as the parcel rotates with the bird's tilt
the trail swings, which reads as MOTION (intended). Grayscale row confirms the
core is the brightest pixel cluster at every angle.

## Carry-occlusion
The core sits in the LOWER half (≈0.60 down) and the brightest tail mass is in
the visible lower-left, so Pip's red body occluding the TOP never covers the
heart. The hot white-gold core separates cleanly from Pip's red; the tail trails
down-and-back, away from his body.

## 22px risk
- Tail could thin to near-nothing at the smallest read on a busy night sky — the
  bulge near the root and the 210-alpha hot root mitigate this, but it may want
  more mass / a touch more length if the trail reads as a single dot in motion.
- The four star spikes are very subtle at 22px (mostly absorbed by the halo);
  they may read as nothing or, if pushed, fight the round silhouette under
  rotation. Currently dialed to barely-there.
- On bright day the additive halo adds little contrast against light blue sky —
  separation leans on the amber body + dark keyline; worth checking it doesn't
  feel flat next to the night bloom.

## Note
Brief referenced `parrot._glow_dot`, which does not exist in `game/parrot.py`.
Used the real available helpers (`parrot._aaellipse`, `draw.lerp_color`) plus a
local additive `_glow_halo`, matching the lantern parcel's convention.
