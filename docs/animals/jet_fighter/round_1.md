# JET FIGHTER (`skin_jet_fighter`) — Round 1

The most expensive secret skin: the flapping macaw becomes a sleek
NON-creature war machine. There is **no wing flap**. The 4 base wing poses
(`_WING_ANGLES = 50, 20, -10, -40`) are reinterpreted as an **afterburner
pulse**: a baked exhaust plume + radial halo that flares brightest on the
middle two frames and shrinks toward the ends, plus a ±1px nose **pitch** so
the airframe visibly breathes with the throttle. No live particle system —
the spectacle is baked per frame, so both build targets render identically.

- Canvas **64×84 SRCALPHA**, fuselage mass centred at **(32,44)** (the fixed
  14px collision circle). Wings span wider; the body stays anchored.
- Jet flies LEFT: nose points −x, plume streams +x.
- Shared bake helpers: `_baked_flame` (layered teardrop: outer haze → mid →
  white-hot core + shock-diamond beads), `_glow` (soft radial halo),
  `_pulse`/`_pitch` (frame-driven throttle + nose breathe).
- Each frame outlined with the house silhouette outline via the local
  `_make_prebuilt_skin`.

Sheet: `docs/animals/jet_fighter/round_1.png` — hero 130px on day + night,
plus 40px NEAREST x3 (level / dive) on **both** day and night skies (the
honest gameplay read; the burner must survive on bright stone AND dark sky).

---

## v1 · STEEL RAPTOR
Top-down planform. Gunmetal-steel arrowhead fuselage, sharp swept **delta**
wings with a red leading-edge accent, twin canted tail fins, **twin** hot
afterburner (white→orange→red) with wingtip missile rails and a blue bubble
canopy.
- **40px tell:** the textbook fighter arrowhead + delta sweep + twin hot
  flames aft. The most instantly-legible "fighter jet."
- **Weak spots:** twin flames sit close together at 40px and can read as one
  blob; the red leading-edge line is near-invisible on day stone. Most
  conventional of the five — safe but least surprising for a top-tier secret.

## v2 · TOP GUN NAVY
Aggressive 3/4 view. Navy-blue + white livery, gold trim, **variable swept
wings** staggered near/far for depth, a big prominent bubble canopy (the hero
of a 3/4 jet), white star roundel, and a **single fat cyan-cored** afterburner.
- **40px tell:** the big glassy canopy + the staggered 3/4 wing depth + one
  bold blue body. Feels like a pilot is in it.
- **Weak spots:** the 3/4 depth read softens at 40px (near/far wings can merge
  into the body); cyan burner is unusual on a warm-stone day sky and may read
  cool/odd against KFC-warm biomes. Roundel is tiny at scale.

## v3 · DESERT STRIKE
Top-down. Desert-tan body with olive camo splotches, **forward-swept** wings
(Su-47 flair) sweeping toward the nose, twin stubby tail fins, **twin** warm
burner, underwing missile pylons.
- **40px tell:** the unmistakable forward-swept wing geometry (tips point
  forward, not back) + warm tan-vs-orange contrast. The most distinctive
  *shape*.
- **Weak spots:** tan is low-contrast against day desert stone — silhouette
  can wash out; the forward sweep is so unusual it can read as "broken/
  backwards" to a casual eye. Missile pylons vanish at 40px.

## v4 · STEALTH PHANTOM
Top-down. Matte-black faceted stealth airframe (B-2 / F-117 angular blended
wing-body), twin canted stealth fins, and a **COLD cyan-core** afterburner
with electric edge-lighting tracing the leading edges.
- **40px tell:** the near-black angular diamond saved by the electric-cyan
  glow + edge-light — pure contrast piece, reads strongest at NIGHT.
- **Weak spots:** the dark body risks disappearing on dark night sky if the
  edge-light is too thin; on bright day stone the matte black is a heavy blob.
  The cold burner breaks the "hot afterburner" brief on purpose — director's
  call whether that's premium or off-concept.

## v5 · CHROME ACE
Aggressive 3/4 airshow jet. Polished chrome/silver body (bright spine, dark
belly = metal read) with a bold **red→gold lightning livery** sweep, swept
wings with a gold racing stripe, twin tail with red caps, a big canopy, a
**single hot** afterburner, and a faint **smoke trail** wisp.
- **40px tell:** the chrome sheen + red livery slash down the body + smoke
  trail = the showy crowd-pleaser. Most "premium airshow" energy.
- **Weak spots:** the most detail-dense build — chrome banding + livery + smoke
  can muddy at 40px into a busy mid-grey; smoke wisp competes with the burner
  for the "tell." Highest risk of looking noisy at gameplay scale.

---

### Cross-cutting notes for the director
- View-angle split: v1/v3/v4 top-down planform, v2/v5 aggressive 3/4.
- Wing-shape split: v1 delta, v2 swept-staggered, v3 forward-swept, v4 blended
  faceted, v5 swept.
- Burner-temperature split: v1/v3/v5 hot (white→orange→red), v2/v4 cold (cyan)
  for night contrast.
- Open question for ITERATE: is the priciest secret better as the *cleanest*
  silhouette (v1) or the most *spectacular* glow (v4/v5)? Burner pulse +
  pitch animation is identical across all five and reads at 40px.
