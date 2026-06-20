# CHAMELEON — Round 1 exploration

ONE new procedural ANIMALS-store creature, five genuinely different takes.
Sheet: `docs/animals/chameleon/round_1.png` (hero 130px on DAY + NIGHT swatches;
40px smooth across all 4 flap frames to show the colour-shift; 40px NEAREST x3
honest read for down-pose / up-pose-with-tongue / dive).

Shared chameleon language across all five (the brief's canonical silhouette):
spiral-coiled prehensile tail, a head-casque, and an independent swivel turret
eye whose pupil aims per pose. The "flap" has no wings — it is reinterpreted as
the **mood-shift colour shimmer** (the body's colour band/scheme slides across
the 4 `_WING_ANGLES` frames) plus a **tongue flick** that snaps out on the
up-pose as the flap accent. Body mass stays anchored at (32,44); casque only
uses the top headroom.

## The 40px tell (all versions)
Coiled comma-tail off the rear + one bright swivel-turret cone on the head.
Those two shapes are what break the silhouette and survive the downscale; the
colour-shift is the secondary "this skin is alive" read once you watch it move.

---

### v1 · Rainbow Prism
The showpiece colour-changer. A full ROYGBIV band runs vertically across the
body and **slides one stop per frame**, so in motion it visibly cycles hue. Tall
scalloped casque, classic tight coil, big turret looking up on the up-pose.
- **Why:** maximal "magic colour-shift" payoff — the cheap procedural win the
  brief calls out, made literal. Most premium / eye-catching of the set.
- **40px tell:** rainbow gradient + casque fin + coil all survive (verified).
- **Weak spot:** rainbow risks looking generic/"pride flag" rather than reptile;
  on bright-day the lighter bands (yellow/green) lose contrast against sky.

### v2 · Neon Flush
The brief palette used literally as a **two-tone gradient that rotates**: green
base flushes through hot-pink into cool blue as it tilts. Sleek low casque
(sail along the skull), slim looser coil, white lateral mid-stripe (a real
chameleon trait), compact cone turret.
- **Why:** the most "designed"/on-brand colour story; the flush reads as an
  emotional mood-shift, not a rainbow gimmick.
- **40px tell:** strong — clean two-tone keeps high contrast at size.
- **Weak spot:** lower casque means the head-silhouette break is the weakest of
  the five; leans hardest on the coil to carry the read.

### v3 · Spotted Panther
Panther-chameleon texture: a teal base with **blocky mood-SPOTS that cycle
colour per frame** (not a smooth gradient) and white vertical bars. The chunkiest,
tightest coil and the biggest, most characterful turret.
- **Why:** the most reptile-authentic skin; spots-changing-colour is a fresh
  alternate take on the shimmer that smooth gradients don't give.
- **40px tell:** excellent — teal body + white bars + huge turret read instantly
  on both backdrops.
- **Weak spot:** the per-spot colour change is subtle at 40px (the spots are
  small); the shimmer is more felt than seen in motion.

### v4 · Veiled Casque
The Yemen/veiled chameleon, where the **dramatically tall helmet casque is the
hero**, not the coil. Diagonal candy-stripe banding (green/gold) scrolls per
frame for the shift; modest turret.
- **Why:** a top-heavy regal silhouette — a different dominant tell from the
  other four (casque-led vs coil-led). Distinct shape at the gallery level.
- **40px tell:** the tall helmet is the standout break-the-sky shape; bright
  leading edge keeps it alive downscaled.
- **Weak spot:** per-pixel scroll loop is the heaviest build of the set (a
  nested set_at loop); top-heaviness fights the (32,44) body anchor a little.

### v5 · Chibi Bubble
Baby-cute economy: a near-circular body, **ONE oversized turret eye dominating
the face** (Pascal-from-Tangled energy), a stub casque, a rosy cheek, and a
loose single-loop tail. Body does a soft mint↔coral **pulse** per frame.
- **Why:** maximal silhouette economy — the giant single eye + curl-tail is the
  boldest, most instantly-legible read in the set; most "casual-arcade adorable."
- **40px tell:** best-in-set — the giant turret and comma-tail are unmistakable
  on both day and night (verified).
- **Weak spot:** least "chameleon-textured" (no bands/spots); the pulse is the
  gentlest shimmer, so it sells character over the colour-change gimmick.

---

## Spread rationale
- **Colour-shift schemes:** rainbow slide (v1) / two-tone gradient rotate (v2) /
  cycling spots (v3) / scrolling stripes (v4) / soft pulse (v5) — five different
  procedural mechanisms, not one tweaked.
- **Casque:** tall scalloped (v1) / low sleek sail (v2) / tall triangular (v3) /
  dramatic tall helmet HERO (v4) / tiny stub (v5).
- **Coil:** tight (v1) / slim loose (v2) / fat very-tight 3-turn (v3) /
  moderate (v4) / single open loop (v5).
- **Turret:** big (v1) / compact (v2) / huge (v3) / modest (v4) / oversized
  dominant (v5).
- **Tongue flick** fires on the up-pose in every version as the flap accent.

No PNGs; both desktop + WASM use the same `pygame.draw` / `_aaellipse` path;
WHY-only comments. Winner lifts straight into `game/animal_skins.py` as
`build_chameleon` / `get_chameleon` / `"skin_chameleon"`.
