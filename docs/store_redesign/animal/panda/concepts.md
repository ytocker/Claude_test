# Panda Animal Skin — Pip → Giant Panda — 5 Concept Brief

**Goal:** Re-skin the player bird (Pip) as a giant panda that reads UNMISTAKABLY
as a panda at ~40px in motion. The panda read is one of the strongest in nature:
**round white face + two black eye patches + two round black ears + black-and-white
body block**. Every concept must *layer multiple themed objects* across the bird
(head + back + body + limbs) so the silhouette breaks the bird's outline from
several directions — never one lonely accessory.

**Build target:** procedural pygame draw (circles, ellipses, polygons, gradients,
glow caches) layered over the existing 4-frame macaw, exactly like the KFC / ghost
/ hat variants in `game/parrot.py`. No PNG sprites. Body mass stays near `(32, 44)`
on the 64×84 canvas; collision circle is 14px at body centre, so the panda's white
torso + black limb mass sits over that centre and the signature objects push **up
past the crown** (ears) and **out past the back/wings** (limbs / props).

**Base read rule (every concept):** at 40px the player must clock TWO tells instantly —
(1) the **black-patch-on-white round face with two round black ears**, and (2) a
single high-contrast signature object that distinguishes THIS panda from the other
four. Everything else is flavor filling the silhouette.

**Shared build kit reusable across all 5:** round white face disc, two teardrop
black eye patches, two round black ears on the crown, black "arm" mass over each
wing root, black leg stubs under the body, white belly disc. Each concept swaps the
hero prop + palette + posture on top of that kit.

Concepts are numbered in recommended build priority (design_1 … design_5).

---

## 1. CLASSIC PANDA — The Definitive Giant Panda  `skin_panda`

The can't-miss baseline. If only one ships, it's this. Pure storybook panda — the
universally legible black-and-white read with nothing fighting it, so the archetype
lands before the player thinks.

- **Hero silhouette (40px read):** a **round white face disc topped by two big round
  black ears**, with two **black teardrop eye patches** angled inward — the single
  most recognizable animal mask on Earth. Below it a chunky white torso framed by
  black arm/leg masses.
- **Object list + placement:**
  - Head: **round white face disc** centered over the bird's head.
  - Head: **two round black ears** sitting up past the crown (the silhouette-breakers up top).
  - Face: **two black teardrop eye patches**, angled down-inward, each holding a small
    white eye-glint dot so it stays friendly not sleepy.
  - Face: **little black nose triangle** + a soft black mouth line under it.
  - Face: **two soft pink-grey cheek blushes** low on the white face for charm.
  - Wings/arms: **black arm masses** over each wing root so the flap reads as panda arms.
  - Body: **white torso/belly disc** over the collision centre.
  - Body: **black shoulder band** wrapping from arms across the upper back (the real
    panda's dark shoulder yoke) — ties the two arms together so the body block reads black-over-white.
  - Feet: **two black leg stubs** hanging under the body.
- **Palette:** `#1A1A1A` (panda black), `#F5F5F5` (panda white), `#E8E8EA` (white
  shadow / value step), `#3A3A40` (soft black highlight on ears/arms), `#E7A9A9`
  (pink cheek/nose-tip accent).
- **Distinctness:** the *pure* panda — no costume, no accessory theme. It's the
  reference point; every other concept is a deliberate departure from this one.

---

## 2. BAMBOO MUNCHER — Panda With Bamboo Gear  `skin_panda_bamboo`

The "panda doing panda things" build. Same classic face, but loaded with bamboo
props so the silhouette breaks outward with green — the nature/forest tier. Adds a
second strong color (bamboo green) the others don't have low on the body.

- **Hero silhouette (40px read):** classic black-ears-and-eye-patches panda **clutching
  a thick green bamboo stalk diagonally across the body**, with a couple of bright
  green leaf sprigs poking up past the crown beside the ears (the green diagonal +
  leaf tufts are the instant "bamboo panda" tell).
- **Object list + placement:**
  - Head: classic **white face disc + two round black ears + two black eye patches +
    nose** (shared kit).
  - Head: **two bamboo leaf sprigs** tucked behind/between the ears, poking up past the crown.
  - Arms/body: **thick bamboo stalk** held diagonally corner-to-corner — segmented with
    darker node rings, one end up past the shoulder, other end past the hip.
  - Mouth: **a single chewed bamboo leaf** sticking out of the mouth (cheeky detail that
    survives if legible at size).
  - Wings/arms: **black arm masses** wrapping the stalk (hands suggested as darker mitts).
  - Body: **white belly disc** + **black shoulder yoke**.
  - Back: **a small woven leaf/bamboo backpack or bundle** strapped on, breaking the
    back outline (one more themed object so it isn't a lone stalk).
  - Feet: **black leg stubs**.
- **Palette:** `#1A1A1A` (black), `#F5F5F5` (white), `#5FA63A` (bamboo green),
  `#3C7A22` (bamboo shadow / node rings), `#C9E29A` (leaf highlight).
- **Distinctness:** the only concept with a strong **green** signature and a held prop
  crossing the body — reads "forest panda," tonally opposite the bare Classic.

---

## 3. CHUBBY DUMPLING — Round Baby Panda  `skin_panda_baby`

The maximum-cute, maximum-round build. Visually opposite the others: oversized head,
tiny stubby limbs, a near-circular silhouette — the "aww" pick. Inspired by mochi /
dumpling panda mascots and Po-style exaggerated roundness.

- **Hero silhouette (40px read):** an **almost perfectly round panda ball** — a giant
  round head merging into a round body with hardly any neck, tiny stub limbs, and
  **oversized round black ears + huge round black eye patches** that take up most of
  the face (baby proportions = bigger patches, bigger ears, lower features).
- **Object list + placement:**
  - Head: **extra-large round white face**, lower jaw rounded into the body so head and
    torso read as one circle.
  - Head: **oversized round black ears** (bigger than Classic) up past the crown.
  - Face: **huge round black eye patches**, more circular than teardrop, set low and wide,
    each with a **big white sparkle glint** (baby eyes).
  - Face: **tiny black nose + tiny mouth**, set low — exaggerated baby spacing.
  - Face: **rosy round cheek blushes**, larger and brighter than Classic.
  - Body: **fat white belly** that's nearly the same circle as the head.
  - Wings/arms: **tiny black stub arms** (short, rounded — the flap reads as little
    excited paddles, not full arms).
  - Feet: **two tiny black foot pads** peeking out at the very bottom.
  - Optional: **a single tiny tuft/cowlick** of fur on the crown between the ears (one
    extra object for charm).
- **Palette:** `#1A1A1A` (black), `#F8F8F8` (extra-bright white), `#EAEAEC` (white
  shadow), `#FF9DB0` (bright baby-pink cheeks), `#4A4A52` (soft ear/arm highlight).
- **Distinctness:** the only **round-ball baby-proportioned** silhouette — defined by
  shape (one circle) and cuteness, not by an added prop or theme.

---

## 4. KUNG-FU PANDA — Martial-Arts Warrior Panda  `skin_panda_kungfu`

The action/hero build. Same panda face, armored up with martial-arts gear so the
silhouette breaks with a hard red diagonal + a wide stance — the "warrior" tier.
Inspired by Po / kung-fu panda imagery and ninja-panda fan designs.

- **Hero silhouette (40px read):** a panda with a **red martial-arts headband whose two
  tails stream back off the skull**, a **wide black belt/sash knotted at the belly**, and
  **arms thrown into an open martial pose** so the wing-arms read as fists ready to
  strike (headband ribbons + belt are the instant "warrior panda" tell).
- **Object list + placement:**
  - Head: classic **white face disc + round black ears + black eye patches + nose** (shared kit).
  - Head: **red headband** across the brow with **two trailing tails** flicking back off
    the head (animate slightly with the flap).
  - Wings/arms: **black panda arms ending in suggested fists/paws**, posed wide/open — the
    4-pose flap reads as throwing punches.
  - Wrists: **two cloth wrist wraps** (red or gold) banding each forearm — extra themed objects.
  - Body: **wide belt/obi sash** wrapped around the white belly, **knotted at the front**
    with a short hanging end.
  - Chest: **a small round emblem / medallion** on the chest (a dragon-scroll dot or
    yin-yang) breaking the white belly.
  - Body: **black shoulder yoke** under the sash.
  - Feet: **black leg stubs** in a braced stance.
- **Palette:** `#1A1A1A` (black), `#F5F5F5` (white), `#C8102E` (kung-fu red:
  headband, sash, wraps), `#E3B23C` (gold emblem + wrap trim), `#7A0C1E` (red shadow).
- **Distinctness:** the only **action-posed, gear-loaded** panda — red ribbons + belt +
  fighting stance give it dynamic, hero-tier energy no other concept has.

---

## 5. CELESTIAL PANDA — Cosmic Spirit Panda  `skin_panda_celestial`  (LEGENDARY-tier showpiece)

The spectacle / flex build. Leans on an **animated glow + shimmer** baked into the
art — the dragon/phoenix-style legendary move. A mythic "spirit guardian" panda where
the black fur becomes a star-flecked night-sky and the white glows with aurora light.

- **Hero silhouette (40px read):** the unmistakable panda mask — **round ears + eye
  patches** — but the black areas are a **deep galaxy speckled with tiny stars**, the
  white glows with a soft **aurora rim-light**, and a **ring of orbiting glowing
  particles / a halo arcs up past the crown** (the glowing halo + starfield-black is
  the signature; nothing else in the set emits light).
- **Object list + placement:**
  - Head: classic **panda mask geometry** — round ears, eye patches, nose — but rendered
    as **galaxy-black** (deep indigo-black flecked with white star dots, a few twinkling).
  - Crown: **a glowing halo / ring of orbiting star particles** arcing above the ears
    (animated soft pulse — the legendary flex).
  - Face: **glowing eye-patches' rim** + eyes that read as small bright stars.
  - Wings/arms: **galaxy-black arm masses** with a **violet/cyan aurora rim-light** on
    their edges (animated shimmer).
  - Body: **white belly that glows**, with a faint **aurora gradient** (teal→violet)
    washing across it instead of flat white.
  - Back/tail: **a short trailing comet/aurora wisp** streaming off the lower body
    past the tail (animates with the flap — sells motion + spectacle).
  - Floating: **2–3 small drifting sparkle particles** around the body.
  - Feet: **galaxy-black leg stubs** with glowing toe-glints.
- **Palette:** `#0D0D1A` (galaxy black body), `#F5F5F5` (glowing white), `#7B3FE4`
  (violet aurora glow — animated), `#19E0FF` (cyan aurora highlight — animated),
  `#FFF3C4` (warm star / halo core glint).
- **Distinctness:** the only **light-emitting, animated** panda — starfield-black fur +
  aurora belly + orbiting halo make it the legendary showpiece, hardest-popping against
  the night sky.

---

## Ranking rationale & build notes

1. **CLASSIC PANDA (#1)** — ship first. The canonical, bulletproof panda read; lowest
   risk, broadest appeal, the reference the other four play against. Round face + ears +
   eye patches = guaranteed 40px read.
2. **CHUBBY DUMPLING (#3 → recommend #2 priority)** — the cuteness hook that sells the
   theme; defined purely by silhouette (one round ball), so it differs from Classic by
   *shape* with zero prop risk. Strong store-thumbnail appeal.
3. **BAMBOO MUNCHER (#2)** — the essential second *color* (green) + a held prop, so the
   set isn't all monochrome. Clear "forest panda" identity.
4. **KUNG-FU PANDA (#4)** — the action/hero tier; red ribbons + belt + stance give the
   set its dynamic, gear-loaded entry, distinct from the calmer three above.
5. **CELESTIAL PANDA (#5)** — best **legendary showpiece**: starfield fur + aurora glow +
   orbiting halo earn the flex tier and give the store top-end range.

**Tier mix:** #1–#4 standard unlockables; **#5 legendary** (animated glow/shimmer baked
into the art, dragon/phoenix-style).

**Distinctness check (all 5 differ in hero shape / signature):** #1 = pure black-white
mask, no prop; #2 = green bamboo stalk across body + leaf tufts; #3 = round baby-ball
proportions, oversized ears/patches; #4 = red headband ribbons + belt + fighting stance;
#5 = galaxy-black starfield fur + aurora belly + glowing halo. No two share a hero read.

---

### Sources
- [Giant panda — Wikipedia (markings: black ears, eye patches, limbs, shoulders vs white torso/face)](https://en.wikipedia.org/wiki/Giant_panda)
- [Giant panda — Smithsonian's National Zoo (round face, coloration purpose)](https://nationalzoo.si.edu/animals/giant-panda)
- [Why Are Pandas Black and White? — Live Science (black markings communicate; eye patches signal identity)](https://www.livescience.com/58206-why-pandas-are-black-and-white.html)
- [5 Tips Experts Use to Identify Giant Pandas — Google Arts & Culture (eye-patch & ear shape variation)](https://artsandculture.google.com/story/5-tips-experts-use-to-identify-giant-pandas-ipanda/wAUhDtqFm14k3Q?hl=en)
- [Art of Kung Fu Panda — Character Design References (Po's exaggerated round-cartoon proportions)](https://characterdesignreferences.com/art-of-animation-7/art-of-kung-fu-panda-trilogy)
- [Researching Character Development in Kung Fu Panda (round head + torso + simple shapes)](https://tbatleyresearchdevelopment.wordpress.com/2013/12/18/researching-character-development-in-kung-fu-panda/)
- [Cute Ninja Panda references — Pinterest (warrior/headband panda fan designs)](https://www.pinterest.com/ideas/cute-ninja-panda/923964800096/)
</content>
</invoke>
