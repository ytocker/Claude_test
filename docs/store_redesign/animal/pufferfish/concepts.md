# PUFFERFISH Redesign — kill the "sun" read, make it clearly a fish

**Problem.** The current `skin_pufferfish` (`animal_pufferfish.py`) is a **golden
ball ringed by a symmetric radial needle-star halo**. That is sun iconography:
a round yellow disc + evenly-spaced radial rays reads as a sun, not a fish. It's
cute, but it's a sun.

**What makes something read as a PUFFERFISH (not a sun):**
1. **Fish anatomy** — a **tail fin** at the back and **pectoral side fins** give
   a front→back axis a sun never has. This is the single biggest fix.
2. **Broken radial symmetry** — real puffer spines are **short, blunt, scattered/
   staggered**, not long even needles fanning out in a perfect circle.
3. **Palette off pure sun-gold** — olive/tan/teal with a pale belly + **dark
   spots** reads aquatic; saturated gold + rays reads solar.
4. **An oriented face** — eyes + a puffer **beak/lips** at the FRONT, not a
   centered sunface.

Every direction below keeps the cute inflated-balloon charm and the inflate gag
(body swells + brightens on the down-puff), but adds a tail + fins + a front face
and tames the spikes so it can never be mistaken for a sun. All must hold the
40px in-motion truth read, day AND night. Numbers map to design_1…design_5.

Shared kit (`tools/pufferfish_candidates/_shared.py`): canvas/anchors + cache
(`_new`, `_make_prebuilt_skin`, `_flap`, `_inflate`, `_shade`), `_radial_body`
(sphere value structure), `_eye`, plus NEW fish parts — `_tail_fin`,
`_side_fin`, `_spots`, and a `_stub_spikes` (short scattered cones, the anti-sun
spike). Each design composes these + its distinctive bit.

---

## 1. FINNED PUFFER — the literal fix  `skin_pufferfish` (keeps the id)
The round inflated body stays, but it's unmistakably a fish: a **fan tail fin**
sweeps off the back-left, **two pectoral fins** flick at the sides, and the
spikes become **short scattered stubs** (not a radial halo).
- **Hero silhouette:** round body + a clear triangular **tail fin** off the back
  + the front face — front-to-back axis kills the sun read instantly.
- **Parts:** tail fin (back-left, fan of 3 ribs), pectoral fins L/R (small, flap
  a touch with the puff), short stubby spines scattered over the upper body only,
  forward face (two eyes + pouty O + blush), a row of belly spots.
- **Palette:** `#E8C24E` warm-sand body, `#F6E6B0` belly, `#C8922E` rim, `#B6781C`
  spine/spot dark, `#6FB7C9` tail/fin teal-edge so fins pop off the body.
- **Distinctness:** keeps the golden ball but defeats the sun with anatomy;
  the safest, most direct "now it's a fish."

## 2. BALLOON SPINES — the iconic puffer  `skin_pufferfish_balloon`
The classic spiky balloonfish: the whole ball **studded with short blunt cone
spines** in a staggered, scattered grid (NOT a clean radial fan), a small wavy
tail nub, big eyes + pouty O.
- **Hero silhouette:** a lumpy bumpy ball (texture all over, not a star) + a tail
  — reads "blowfish," the spines too short/irregular to be sun rays.
- **Parts:** ~18 short cone spines on a jittered grid across the sphere (length
  varies, tips dark→light), small fan tail back-low, tiny pectoral nubs, big
  friendly eyes, pouty O, scattered dark dots between spines.
- **Palette:** `#D9A24A` sandy-brown, `#F3E2B4` belly, `#A6701E` spine/spots,
  `#7C541A` deep rim, `#FFFFFF` spine speculars.
- **Distinctness:** the spines stay (it's a SPIKY puffer) but the staggered short
  studs + tail break the radial-sun pattern decisively.

## 3. FUGU TORPEDO — realistic  `skin_pufferfish_fugu`
A **less-inflated, slightly OVAL** body (longer front-to-back, not a perfect
circle) with full fish fins — the most realistic fugu read.
- **Hero silhouette:** an egg/torpedo body (clearly longer than tall) + tail +
  dorsal fin — the non-circular outline alone says "fish, not sun."
- **Parts:** oval body, fan tail fin (back), small dorsal + anal fins, pectoral
  fins, very small/sparse spines, classic fugu olive back fading to white belly,
  bold dark fugu spots, a beaky little mouth.
- **Palette:** `#8FA24E` olive back, `#C9D29A` flank, `#F4F6EC` belly, `#2E3A22`
  spots/eye, `#E0A24A` fin warm-edge.
- **Distinctness:** the only non-round silhouette + the only olive/realistic
  scheme; can't be a sun because it isn't a circle.

## 4. AQUA PUFFER — palette break  `skin_pufferfish_aqua`
Kill the sun with **colour**: a cute **teal/aqua** balloon puffer with a
**coral-pink belly**, a tail fin, and a couple of rising **bubbles**.
- **Hero silhouette:** round body + tail + bubbles, in a cool aqua no sun owns.
- **Parts:** teal radial body, coral belly, soft rounded short spines (gentle,
  cute), fan tail + pectoral fins in a deeper teal, 2–3 bubble circles drifting
  up off the back, big sparkly eyes + pouty O.
- **Palette:** `#39B6C4` aqua body, `#7FE0E8` light core, `#1E7C8A` rim/fins,
  `#FF9Cae` coral belly, `#EAFBFF` bubble/spec.
- **Distinctness:** the only cool-colour design; aqua + bubbles reads "underwater
  fish" — the strongest pure anti-sun via palette.

## 5. DERPY BEAK PUFFER — character  `skin_pufferfish_derpy`
Maximum charm: **huge eyes** and a prominent **two-tooth puffer beak/lips**, a
swishy little tail, soft irregular spikes — a goofy lovable fish face.
- **Hero silhouette:** big-eyed beaky face on a puffed body + a flicking tail —
  the beak + googly eyes read "fish character," never a sun.
- **Parts:** big oversized eyes (with the puffer's close-set forward look), a
  **beak mouth** (two pale buck-teeth / lips), soft short spikes (sparse, cute),
  a small wavy tail + tiny side fins, a couple cheek freckles.
- **Palette:** `#E6B24E` warm body (kept warm but de-sunned by the strong face +
  tail), `#F6E6B4` belly, `#C2871E` rim/spikes, `#3A2A12` eye/beak-line,
  `#FFF3D6` teeth.
- **Distinctness:** the only design led by an exaggerated beaky-face character;
  charm-forward, and the beak is a hard fish tell.

---

## Distinctness matrix
| # | Name | Anti-sun lever | Silhouette | Palette |
|---|------|----------------|------------|---------|
| 1 | FINNED PUFFER | tail+fins, stub spikes | round + tail | warm gold + teal fins |
| 2 | BALLOON SPINES | scattered short studs + tail | bumpy ball + tail | sandy brown |
| 3 | FUGU TORPEDO | non-round body + full fins | oval + tail/dorsal | olive realistic |
| 4 | AQUA PUFFER | cool colour + bubbles | round + tail + bubbles | teal + coral |
| 5 | DERPY BEAK | beak face + tail | big-face ball + tail | warm + bold face |

All five add a tail + an oriented face, tame the radial halo, and read at 40px
in motion — none can be mistaken for a sun.
