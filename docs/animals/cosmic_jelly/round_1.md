# COSMIC JELLY — `skin_cosmic_jelly` (LEGENDARY) · Round 1

A legendary spectacle skin and the ANIMALS set's only NON-winged creature: a
galaxy-filled translucent bell trailing star-streamer tentacles — a jellyfish
made of deep space. Five genuinely different takes on the same creature, all on
the production 64×84 contract (bell centred at `(32,44)`, tentacles trailing
down), so the winner lifts straight into `game/animal_skins.py`.

**Non-winged pulse:** the 4 base wing poses (`50,20,-10,-40`, down→up) are
reinterpreted as the JELLY PULSE — the bell CONTRACTS (squashes wide+short,
tentacles bunch) on the down-pose and BILLOWS open (tall+narrow, tentacles
stream long) on the up-pose. A slow nebula DRIFT rotates the internal
swirl/stars across the 4 frames.

**Spectacle is baked, not live:** there is no particle system feeding the
sprite, so the nebula glow, stars and stardust are baked into each of the 4
frames; the only "animation" is the pulse squash + the per-frame swirl/star
offset.

Sheet: `docs/animals/cosmic_jelly/round_1.png` — hero 130px on a split
night|day backdrop (the dark void must survive both), 40px smooth, and the
honest **40px NEAREST x3** gameplay read (level + dive).

---

## V1 · CLASSIC DOME
- **Concept:** the textbook moon-jelly low dome, violet shell over a void core,
  a 2-arm cyan/violet spiral galaxy swirling inside, 5 long constellation-dot
  tentacles, scalloped cyan rim-light.
- **40px tell:** the round violet dome with a bright cyan swirl + dotted
  streamers. The most immediately legible "jellyfish made of space."
- **Weak spots:** mid translucency means the void core can read slightly muddy
  on the day half; the dotted tentacles thin out at 40px and lean on the glow.

## V2 · ONION BULLET
- **Concept:** a tall onion/bullet bell (siphonophore feel), PINK/GOLD scheme, a
  dense gold star-CLUSTER heart instead of a spiral, 3 thick ribbon tentacles
  with gold star-nodes. The most solid, jewel-like bell.
- **40px tell:** the tall pink teardrop silhouette with a glowing gold heart —
  the silhouette alone is unmistakably "not a bird."
- **Weak spots:** the pointed crown is the riskiest read at 40px (can blob into
  the dome); pink/gold drifts toward the phoenix's warm palette, so it leans
  hardest on the tall shape to stay distinct.

## V3 · MUSHROOM AURORA
- **Concept:** a wide, flat mushroom-jelly cap, AURORA scheme (mint/cyan/violet),
  a horizontal rippling aurora BAND across the dome (not a point swirl), 8 fine
  hair tentacles. The most translucent "ghostly veil" read.
- **40px tell:** the wide flat cap with a horizontal green-cyan aurora ribbon — a
  genuinely different silhouette + cosmos motif from the others.
- **Weak spots:** the low alpha + 8 hair tentacles are the most fragile at
  gameplay scale; the veil can wash out on the bright-day half. The boldest
  freshness, the softest 40px read — a deliberate risk to put in front of the
  director.

## V4 · SOLID VOID-CORE
- **Concept:** a near-opaque, rock-solid bell, deep void body with a HARD
  high-contrast cyan/pink swirl, a searing white core, the strongest halo, and 6
  medium constellation tentacles whose dots are JOINED into star-lines.
- **40px tell:** a solid dark bell with one searing swirl + a thick halo — the
  most gameplay-robust read of the five (see the NEAREST x3 strip: the swirl and
  core survive cleanly on both day and night).
- **Weak spots:** the additive halo makes the silhouette outline a touch ragged;
  "solid + hard swirl" is the safe choice and may read less ethereal/jelly-like
  than V1/V3 at hero scale.

## V5 · CROWN COMET
- **Concept:** a domed bell crowned with a bright STAR-DIADEM (3 spike-stars
  breaking the top silhouette), a full violet/cyan/pink TRI-colour 3-arm nebula,
  and 4 long comet-tail tentacles tapering to glowing stardust points.
- **40px tell:** the bright star-crown above a tri-colour swirling dome — the
  most "regal legendary spectacle" read, with a feature that breaks the top
  silhouette the way the dragon's horns and phoenix's crest do.
- **Weak spots:** the crown competes with the swirl for the eye (two heroes);
  the tri-colour swirl + crown is the busiest interior and risks reading noisy at
  40px; comet tails are the most expensive tentacle style per frame.

---

### Cross-cutting notes for the director
- **Day vs night:** the dark void core is the legendary's risk on a bright-day
  sky — V2 (solid pink) and V4 (strong halo) hold best there; V3 is weakest.
- **Distinctness from phoenix/dragon:** V1/V4/V5 (violet/cyan) sit clearly apart
  from the warm gacha pair; V2 (pink/gold) is the closest and relies on the tall
  onion shape to differentiate.
- **Pulse legibility:** the squash/billow is most visible on V2 (tall onion) and
  V3 (flat→taller cap); subtlest on V4 (near-opaque dome) where the swirl drift
  carries more of the motion.
