# BURRO PIÑATA — Round 1

A flying donkey piñata flyer skin: candy on legs. One of 5 independent piñata
concepts. It owns the one job no other piñata in the set can take — being the
**only legged creature**, a side-profile 4-legged quadruped that reads as a
"little donkey party animal" at 40px.

Sheet: `docs/pinata/burro/round_1.png` (GAMEPLAY — DAY | GAMEPLAY — NIGHT |
REFERENCE 3x / play-size / grayscale).

## Read at 40px
- **Silhouette:** boxy barrel body (wide, fairly flat — a creature's barrel,
  not a ball) + stubby upright neck/head on the front shoulder + **two ear
  nubs** + **four short tassel-tipped legs** dangling below. The legged-animal
  outline is the whole point and it is the only one in the set.
- **Donkey tells that survive downscale:** head-up upright posture, the two ear
  nubs, the cream mane crest up the back of the neck, and the paired front/back
  legs. Legs are deliberately SHORT, PAIRED, and end in fat tassel knots so
  they stay legible nubs instead of hairline mush.
- Body mass + head sit at/above centre (32,44); the legs dangle below to frame
  and cradle Pip's parcel (the contract's 14px hit circle stays on the body).

## Palette (crepe-paper fringe bands)
- Top band hot-pink `#F2497E` (PINK / PINK_D shadow).
- Middle band orange `#F58B1F` (ORANGE / ORANGE_D).
- Lower band turquoise `#23C2A8` (TURQ / TURQ_D).
- Cream mane + leg fringe + keyline `#FFF1D6` (CREAM / CREAM_D).
- Accents: pale snout `#FAE8CA`, warm inner-ear `#FF9E78`, tassel-knot hoof
  `#785646`, dark eye/nostril, white glint.
- **Night survival:** the pale cream mane, the cream leg stubs, and the baked
  cream keyline arcs on the body top + head top keyline the dark crepe so the
  silhouette glows out of the night sky (see NIGHT frame — the mane + legs +
  top rim hold the shape against `(18,22,48)`).
- Each of the four legs carries a different festival tassel hue (pink / turq /
  orange / pink) so the dangling feet sparkle the full palette even tiny.

## Trot-sway frame map (NO wings, NO particles)
Driven by `_WING_ANGLES=(50,20,-10,-40)` → `_phase` → `_TROT`. The whole body
**bobs** on its rope and all four legs **swing out → tucked → out**; the
front pair and back pair swing opposite so it reads as a gait. The delta is a
pure silhouette change (leg position + body height), so it survives grayscale
(see the grayscale strip — the leg splay reads frame-to-frame in mono).

| Phase | `_WING_ANGLES` | body bob | legs        |
|-------|----------------|----------|-------------|
| 0     | 50             | +1 (low) | OUT (splayed) |
| 1     | 20             | -1       | mid         |
| 2     | -10            | -2 (high)| TUCKED      |
| 3     | -40            |  0       | mid         |

The bounce (low→high→low) and the leg out→tuck→out cycle together sell a
festive trot/dangle on the rope without a single wing or particle.

## 40px risk
- **Leg legibility at the very smallest size.** At the true play-size strip the
  four tassel feet read as a fringed lower edge but the individual legs start to
  merge; the trot delta is still visible as the lower silhouette shifting, but
  if the art-director wants the four legs to count distinctly at 40px I'd
  thicken the tassel knots and widen the front/back leg-pair gap.
- **Head-vs-body band clutter.** Three fringe bands + neck + mane + head is a
  lot of elements in 64px; at play size the head can read slightly busy against
  the pink top band. Candidate fix: push the head colour to pure pink with a
  stronger cream keyline so head/body separate by value, not just by tier line.
- **Front/back orientation.** The head is on +x; need to confirm that matches
  the bird's facing in live gameplay so the burro trots forward, not backward.
