# MANTIS SHRIMP skin — Round 1

Brief: ONE new procedural creature skin (`skin_mantis_shrimp`) for the ANIMALS
store. Concept: segmented armoured torpedo with raised boxing-club forelimbs and
periscope stalk-eyes; the flap reinterpreted as a **strike** — clubs cock back on
the down-pose (`wing=50`) and **punch forward** on the up-pose (`wing=-40`). This
is the most colour-saturated, alien-bodied pick in the roster.

Five genuinely different takes (not five tweaks): they diverge on carapace
banding scheme, club size/raised-ness, eye-stalk length + spread, segment count,
and the level of hard armour-plating detail.

Contract honoured: 64×84 SRCALPHA, body mass at (32,44), head/eye-stalks near
(44,34) and up into the headroom, 4 base wing poses, `_make_prebuilt_skin` getter,
procedural only, WHY-only comments. Shared `_strike()` maps wing angle to a
0..1 punch; `_club_arm()` swings the raptorial club from cocked→punched;
`_jewel_eye()` draws the iridescent periscope eye with its midband.

## The variants

**v1 · PEACOCK CLASSIC** — the textbook peacock mantis shrimp, dialled cute.
Teal carapace, leopard-spotted pale plates, hot-orange swimmeret fringe, two
periscope eye-stalks spread wide, medium red-orange club.
- 40px tell: jewel eyes + teal/orange spotted shell.
- Weak spots: spotting may dissolve at 40px into mush; most "expected" / least
  fresh of the set.

**v2 · RAINBOW SEGMENTS** — every abdominal plate a different spectrum hue
(red→violet down the body), clean rounded shapes, one BIG club, short close
stalks. The literal "kaleidoscope" read.
- 40px tell: full-spectrum banded abdomen reads as a kaleidoscope even tiny.
- Weak spots: rainbow tail could pull the eye away from the head/club hero; risk
  of reading "candy" rather than "armoured predator".

**v3 · DUOTONE BRUISER** — stripped teal/orange duotone shield with two bold
orange banding stripes and OVERSIZED twin clubs dominating the silhouette like a
heavyweight's gloves; long wide eye-stalks.
- 40px tell: giant orange double-fist + stripe.
- Weak spots: the huge near club can crowd / occlude the snout in the punch pose;
  fewer colours = less "technicolor" than the brief's saturation ask.

**v4 · ARMOURED PLATING** — heavy hard-surface "mech-crustacean": overlapping
plates with rim-light edges, gold seams, riveted studs, and amethyst-violet +
gold JEWEL-TONE banding instead of teal.
- 40px tell: faceted plates + violet/gold jewel banding.
- Weak spots: most detail-dense — rivets/seams may vanish at 40px leaving a flat
  blue blob; reads less obviously "shrimp", more generic armour.

**v5 · NEON DEEP-SEA** — bioluminescent abyssal take: dark indigo carapace lit by
neon cyan/magenta edge-wireframe banding, glowing lamp-eyes on long thin stalks,
an electric-blue plasma club. Built to glow on night skies while the dark body
stays bold on bright days.
- 40px tell: neon wireframe + lamp eyes + plasma club.
- Weak spots: thin 1px neon lines are the riskiest at downscale; the cool palette
  drops the brief's hot-orange club entirely (deliberate, but a divergence).

## Cross-cutting weak spots to watch

- Club arm legibility as a *forward punch* (vs a generic blob near the face) at
  40px in the dive pose — the strike is the freshness, it must read.
- Eye-stalk thinness: 3–4px stalks survive 130px but thin out at 40px; the jewel
  tip is doing most of the work.
- Far/near club overlap on the level (cocked) pose — keep both fists from merging
  into one shape.

Sheet: `docs/animals/mantis_shrimp/round_1.png` (hero 130px on day+night,
40px smooth + NEAREST x3 honest gameplay read, cock + punch poses).
