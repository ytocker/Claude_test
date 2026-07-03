# UFO Store Skin — Round 1 (5 variants)

Secret ultra-premium **non-creature** flyer: the player's flapping bird becomes
a domed alien saucer. There are NO wings — the four base poses (`_WING_ANGLES =
50,20,-10,-40`) are reinterpreted as a **chasing rim-light cycle**: two adjacent
rim lights glow bright and advance one notch per pose, while the tractor beam
**pulses** (widens on even phases, narrows on odd). All glow is baked into the 4
frames; no live particle system.

Shared contract: one flat frame on a **64×84 SRCALPHA** canvas, saucer body mass
centred at **(32,44)** (the fixed 14px collision circle), dome above it, beam
extending below the collision body. Rim halos are stamped to a scratch surface
and blitted additive so they bloom at night without punching holes in the disc.

Sheet: `round_1.png` — each card shows hero 130px on a DAY and a NIGHT sky, plus
all four chase frames + a dive read at the honest **40px NEAREST×3** scale, on
both skies.

---

## V1 · Classic Chrome (cyan / green) — the archetype
- **Look:** bright chrome-silver shallow disc with a hot specular top band, a
  green glass dome housing a tiny grey big-eyed alien, 8 cyan rim lights, a
  green tractor beam.
- **40px tell:** silver disc + green dome cap + the cyan light chasing the front
  lip + the green cone below. The green-on-silver value split survives downscale.
- **Why fresh:** the textbook flying saucer everyone pictures — instantly "UFO".
- **Weak spots:** the most expected take (least surprising of the five); the
  alien is barely legible below ~50px (it just reads as a dark dome pupil).

## V2 · Brushed Steel (magenta) · no beam
- **Look:** widest, flattest disc; cool brushed-steel litho with vertical
  striations and a smoky violet dome (no alien); 11 dense magenta rim lights;
  deliberately **no tractor beam** for a sleeker, more menacing read.
- **40px tell:** the wide flat ellipse + the dense magenta chase ringing the
  front. The magenta pops hardest of all five against a blue day sky.
- **Why fresh:** "high-tech recon craft" register — restraint vs. V1's spectacle.
- **Weak spots:** without a beam it's the least premium-spectacular; the wide
  flat profile is the closest of the five to reading like a plane wing in a fast
  dive tilt.

## V3 · Matte Stealth (amber) — night-ops abductor
- **Look:** matte near-black egg-deep disc, a tall amber glass dome with a
  big-eyed alien, amber rim chase, and the **widest tractor beam** (strength
  1.2). Built to own the dark sky.
- **40px tell:** the warm amber dome + amber beam glowing out of a black hull —
  the strongest value contrast of the set, unmistakable at night.
- **Why fresh:** leans fully into the premium-glow brief; the abduction beam is
  the spectacle.
- **Weak spots:** matte black hull nearly disappears on a bright day sky (the
  glow carries it, but the silhouette goes quiet); tallest footprint, so the
  disc proper is a touch smaller to fit the dome + beam in 84px.

## V4 · Oil-Slick Iridescent — flashiest premium
- **Look:** anodised disc banded in oil-slick colour (teal→blue→violet→pink→
  gold) whose bands **shift by phase** so the metal shimmers as the lights
  chase; a clear bluish crystal dome with faint prismatic facet lines; rim
  lights whose **lit colour rotates** through the prism each phase; thin violet
  beam.
- **40px tell:** the rainbow shimmer + the colour-cycling rim — no other Skybit
  flyer shifts hue frame-to-frame, so it's unmistakably "alien tech."
- **Why fresh:** the only skin whose body finish animates; maximum gacha sparkle.
- **Weak spots:** the busiest of the five — the rainbow banding can muddy into
  grey-ish at 40px on a bright sky; risks looking "soap bubble" rather than
  "metal" if the bands aren't dark enough.

## V5 · Retro Tin-Toy (Saturn) — charming + day-friendly
- **Look:** 1950s litho tin-toy saucer — cream enamel disc with a red belly
  stripe and rivets, a **Saturn ring** sticking out past the hull, a red-capped
  blue-glass porthole dome, primary-colour **carnival bulb** rim lights
  (red/yellow/blue/green), a little antenna ball on top. No beam.
- **40px tell:** the Saturn ring breaking the silhouette + the multicolour bulb
  chase + the red/cream toy palette — the only warm, light-valued saucer, so it
  reads best of all five on a bright day sky.
- **Why fresh:** zero menace, full charm; a different emotional register that
  widens the store's range and shares no palette with the other four.
- **Weak spots:** the antenna ball + Saturn ring are thin features that thin out
  at 40px; the lowest-tech, least "ultra-premium" feel of the set; multicolour
  bulbs read busy if the dim/lit contrast slips.

---

### Cross-cutting notes for the next round
- The chase + beam-pulse motion reads on all five; V3/V1's beam pulse is the
  clearest "alive" signal, V4's hue-cycle the most novel.
- Day-sky legibility ranking: **V5 > V2 > V1 > V4 > V3**. Night-sky spectacle
  ranking (the brief's north star): **V3 > V1 > V4 > V2 > V5**.
- If a single winner is wanted, V1 and V3 are the safest "obviously a UFO"
  reads; V4 is the boldest premium swing; a V1-silhouette + V3-beam hybrid is an
  obvious merge candidate.
- Nothing is wired into `game/`; this is exploration only.
