# PUFFERFISH — Round 1 (5 takes)

Concept: a near-perfect spiky sphere with tiny fins and a pouty face. The
signature 40px tell across all five is the **radial spike-halo silhouette** —
instantly "a ball of spikes," which no current ANIMALS creature owns. The flap
is reinterpreted as a comedic **inflate PULSE**: the down-pose (frame 0, wing
angle 50) puffs the body bigger and flares the spikes out long; the up-pose
(frame 3, angle -40) deflates a touch and pulls the spikes in. Body mass stays
anchored at (32,44) so the fixed 14px collision circle stays fair — the gag is
read through the halo + a small radius wobble, never an oversized creature.

Shared kit: `_spike_ring()` (two-tone triangular halo with a cheap drop-shadow
flank), `_fin()` (tiny waving pectoral/tail fin), `_inflate()` (1.0 puffed on
the down-stroke → 0.0 deflated on the up-stroke).

## V1 · CLASSIC YELLOW
The canonical golden balloon everyone pictures: dense medium spikes all round,
round body, big friendly eyes, a pouty **O**-mouth, tiny blush. The safe
default.
- **40px tell:** dense spike halo + the dark pouty O on a golden ball.
- **Weak spots:** most "expected" / least surprising; the O can read as a
  single dark dot at the smallest scale if the face crowds.

## V2 · GRUMPY PORCUPINE
True porcupinefish: brown, **fewer but much LONGER** spikes, a slightly
teardrop body, heavy angled brows + a frown. Dangerous-but-cute.
- **40px tell:** long sparse spikes + the angry scowl; the brown reads as a
  distinct species vs the yellow puffs.
- **Weak spots:** the long spikes are the most likely to tangle visually with
  pillars in motion; brown is lower-contrast against warm sandstone than the
  yellows (still fine on day/night sky).

## V3 · SPOTTED TROPICAL
Guineafowl-puffer palette: teal body, **short stubby bump** spikes so the
scattered **white spots** carry the read, plus a happy closed-eye face.
- **40px tell:** teal ball, white spots + a bumpy (not starburst) rim.
- **Weak spots:** the spike halo is the weakest of the five here — it leans on
  colour + spots more than silhouette, so it least satisfies the "ball of
  spikes" brief; the closed-eye arcs can blur to nothing at 40px.

## V4 · STAR-BURST
Maximum drama: two staggered rings of **sharp needle** spikes radiating like a
sea-urchin star, bright-tipped, on a vivid yellow ball with startled dot eyes.
The flap genuinely PULSES the whole star bigger/smaller (largest pulse range).
- **40px tell:** the symmetric urchin needle-star — the boldest, most legible
  silhouette of the set; the tiny face barely matters.
- **Weak spots:** face is almost vestigial (less personality / charm); needle
  tips are the finest detail, so the bright tip-dots are doing real work to
  survive the downscale.

## V5 · KISSY BLOWFISH
Gag-forward: an asymmetric puffed **cheek bulge** toward the face so it reads
as mid-blow, softer spikes, **huge pouty kissy lips**, sleepy half-lidded eyes.
The personality pick.
- **40px tell:** asymmetric cheek bulge + the big red kissy lips breaking the
  yellow.
- **Weak spots:** the asymmetry slightly weakens the perfect-sphere silhouette;
  the lips add a non-yellow colour that must not read as a wound/error — needs
  the art-director's eye on whether the gag lands or looks off-model at speed.

## Cross-cutting notes
- No frame clips the 64×84 canvas, even fully inflated (verified) — outline
  pass has room.
- All five hold the spike-halo read in the NEAREST x3 truth column at both
  level and dive tilt, and against the split day|night hero backdrop.
- Spread of the brief's axes: density (V3 dense-short → V2 sparse-long),
  shape (round V1/V4 → teardrop V2 → asymmetric V5), expression (cute V1,
  grumpy V2, happy V3, startled V4, sleepy-kissy V5), colour (yellow V1/V4/V5,
  brown V2, teal-spotted V3).
