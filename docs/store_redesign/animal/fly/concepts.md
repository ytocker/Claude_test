# FLY — Animal Skin Concepts

New "animal" group skin (`skin_fly`), premium tier (~500–700 coins). Five
distinct, buildable concepts for the procedural graphics-designer.

**Canvas & anchors (shared):** 64×84 px. Body centre `BCX=32, BCY=44`. Head
centre `HCX=44, HCY=34`. 4 wing-pose frames, baked to ~40px at gameplay scale.

**The 40px read — every concept MUST land these five tells:**
1. **Two huge bulging compound eyes** dominating the head (`HCX=44, HCY=34`),
   each a domed hemisphere ~14–18px wide — the #1 fly tell, far bigger than a
   mosquito's. Faceted/mottled shading, glossy top highlight.
2. **Chunky round barrel body** at `BCX=32, BCY=44` — a fat plump thorax+abdomen
   blob, NOT a long tapered tube.
3. **Two short WIDE rounded wings** fanning up-and-back from the thorax
   (~`(28,30)` anchor), membranous with a few thick veins — not narrow blades.
4. **Spongy labellum** — a short round sponge pad hanging below the head/face
   (~`(46,44)`), NEVER a needle.
5. **Bristly thorax hump** — a few setae/bristle flicks off the top of the
   thorax (~`(26,32)`).

**Shared flap read:** the 4 poses drive the two wide wings up→down as a fast
buzz-blur. Frames 1&4 wings-up (crisp), frames 2&3 wings-down/mid (motion
smear + faint translucent trail arc behind each wing) to sell the flicker of a
real fly's wingbeat. Body bobs ~1–2px; eyes stay locked as the stable read.

---

## 1. BLOWFLY BARON · `skin_fly` — **[LEGENDARY]**

*Ref: metallic blowfly (Chrysomya/Calliphora) macro — jewel-red eyes, oil-slick
green-blue chitin.*

- **Hero silhouette:** a fat gleaming barrel of a body crowned by two enormous
  ruby domes; the whole creature glints like spilled oil in sunlight. Reads as
  "the shiny bottle-fly" instantly.
- **Signature feature:** an **animated oil-slick sheen** — a diagonal
  iridescent highlight band (green→cyan→violet ramp) that slides across the
  thorax/abdomen each frame, plus deep jewel-red eyes with a hot white
  specular dot. This is the flex: it should out-shine the dragon's gloss.
- **Object list + placement:**
  - Body barrel `BCX=32,BCY=44`, ~26×24px oval, filled with a vertical
    metallic ramp (dark teal base → bright green midtone → cyan rim-light top).
  - Moving sheen band: a soft-edged diagonal stripe of `#7CF6C8→#5AD1FF→#B98CFF`
    that shifts ~4px per frame across the body (bake per-frame offset).
  - Abdomen segmentation: 2 faint darker chevron seams across the lower body
    for the "banded metal" read.
  - Two compound eyes at `(38,32)` and `(50,32)`, ~15px domes, deep
    garnet-red radial gradient with a single `#FFFFFF` specular at upper-left.
  - Wings from `(28,30)`, wide teardrop, translucent `#CFEFE8` at ~55% alpha
    with a thin pearlescent green edge and 3 dark veins.
  - Labellum sponge pad `(46,45)`, small `#2A5148` rounded lobe, two grooves.
  - Bristles: 3 short dark setae off the thorax top `(26,30)`.
- **Palette:** `#123B34` (deep base) · `#2FA872` (green body) · `#7CF6C8`
  (cyan rim/sheen) · `#8B0E23` (garnet eye) · `#B98CFF` (violet sheen tail).
  *Glow note: bake the sheen band + eye specular; add a faint 1px green
  rim-glow so it pops on night skies.*
- **Distinctness:** the only photoreal-metallic, iridescent one — sells on
  shimmer and jewel-red eyes, no cartoon outline, no gimmick theme.

---

## 2. BUZZ THE HOUSEFLY · `skin_fly` — **[late-game]**

*Ref: classic housefly + chibi mascot big-eyes.*

- **Hero silhouette:** the platonic "fly everyone draws" — round grey dumpling
  body, two massive friendly eyes eating 60%+ of an oversized head, stubby
  clear wings. Wholesome and huggable.
- **Signature feature:** **enormous glossy cartoon eyes** with big white
  catch-lights and a tiny visible pupil — instant charm, instant fly-read even
  at 30px. The face is the whole sell.
- **Object list + placement:**
  - Head enlarged to ~26px, sitting `HCX=44,HCY=32`, so the two eyes fill it.
  - Two compound eyes `(38,32)` & `(50,32)`, ~16px domes, warm red-brown
    (`#B24A3A`) with subtle facet stipple, a big `#FFFFFF` oval catch-light
    upper-left and a soft second highlight lower-right; hint of a dark pupil.
  - Body oval `BCX=32,BCY=45`, ~24×22px, warm neutral grey vertical ramp
    (`#8C8A88`→`#6E6C6A`) with 2 subtle darker abdominal bands.
  - Fuzzy thorax: dashed fringe of tiny bristles around the top of the body
    hump `(26,32)` for the "hairy" read.
  - Wings from `(28,31)`, wide rounded, `#EDEFF2` at ~60% alpha, 2 soft veins.
  - Labellum: round tan sponge pad `(46,45)`, `#C79A6E`, clearly a soft pad.
  - Optional tiny smile crease under the eyes for warmth (kept subtle).
- **Palette:** `#6E6C6A` (body shadow) · `#9A9896` (body light) · `#B24A3A`
  (eye) · `#FFFFFF` (catch-light) · `#C79A6E` (sponge).
- **Distinctness:** the wholesome default — muted greys + friendly face, no
  metal, no macabre, no comic ink. The "safe favourite" of the set.

---

## 3. VOLT-WING · `skin_fly` — **[LEGENDARY]**

*Ref: cyborg/drone fly — hex-grid sensor eyes, riveted chassis.*

- **Hero silhouette:** a chunky brushed-metal fly-drone; one organic-ish
  translucent wing, one hard mechanical wing-blade; eyes are glowing hex
  sensor arrays. Fat-bodied so it still reads fly, not "spaceship."
- **Signature feature:** **neon hexagonal compound eyes** — a cyan hex grid
  etched over each dome that pulses brightness across the 4 frames, plus tiny
  spark particles flicking off the mechanical wing hinge.
- **Object list + placement:**
  - Body barrel `BCX=32,BCY=44`, ~26×24px, gunmetal ramp
    (`#3A4048`→`#5A626C`) with a bright edge highlight; 3–4 rivet dots down
    each side (`#20242A` with a `#8FA0B0` speck).
  - A thin glowing seam of `#25E0FF` runs vertically down the thorax centre.
  - Two hex-eye domes `(38,32)` & `(50,32)`, ~15px, dark base `#101820`
    overlaid with a neon `#25E0FF` hexagon grid; per-frame the grid brightens
    `#25E0FF`→`#9BF4FF` (scanning pulse).
  - Wings: RIGHT wing translucent `#CFF6FF` at 50% with glowing vein circuitry;
    LEFT wing a solid metal blade `#5A626C` with 3 slot cutouts, from `(28,30)`.
  - Spark FX: 2–3 tiny `#FFE68A` spark dots at the left-wing hinge `(24,30)`,
    offset per frame for a crackle.
  - Labellum: a small mechanical nozzle/pad `(46,45)`, `#3A4048` with a cyan dot.
  - Bristles rendered as 3 tiny antenna-wires with bead tips off `(26,30)`.
- **Palette:** `#20242A` (dark chassis) · `#5A626C` (steel) · `#25E0FF`
  (neon cyan) · `#9BF4FF` (pulse hi) · `#FFE68A` (spark).
  *Glow note: bake cyan bloom on eyes + centre seam + sparks; the mismatched
  wings are the silhouette gag.*
- **Distinctness:** the only hard-tech / asymmetric-wing concept — cold cyan
  glow and rivets vs. everyone else's organic body.

---

## 4. MORTIMER DEATHFLY · `skin_fly` — **[LEGENDARY]**

*Ref: Death's-head hawkmoth skull marking + velvety black bottle-fly.*

- **Hero silhouette:** a plush pitch-black barrel body carrying a pale glowing
  skull on its back, topped by two eerie glowing green eyes. Spooky-cute, not
  gross — a Halloween showpiece.
- **Signature feature:** a **bone-white skull crest on the thorax/abdomen** (the
  classic death's-head), paired with **bioluminescent yellow-green eyes** that
  softly pulse. Macabre charm, high value contrast.
- **Object list + placement:**
  - Body barrel `BCX=32,BCY=45`, ~26×24px, deep velvet black ramp
    (`#0A0A0E`→`#1E1E26`) with a soft grey top rim so it isn't a flat blob.
  - Skull motif centred on the upper body/thorax `(32,42)`, ~14×16px:
    `#E8E4D8` domed cranium, two black eye sockets, a short nasal triangle and
    a few teeth hatches. Kept bold/simple so it survives 40px.
  - Two compound eyes `(38,31)` & `(50,31)`, ~15px domes, glowing
    yellow-green radial (`#B6FF3C` core → `#5A7A18` rim) with a pale specular;
    brightness eases up/down across the 4 frames (slow pulse).
  - Wings from `(28,30)`, wide, smoky charcoal `#2A2A32` at ~55% alpha with a
    faint bone-white edge glow and dark veins.
  - Labellum: small dark sponge pad `(46,45)`, `#15150E`, subtly grooved.
  - Bristles: 3 stiff black setae off the thorax `(26,29)` for a spidery feel.
- **Palette:** `#0A0A0E` (velvet black) · `#1E1E26` (body light) · `#E8E4D8`
  (bone skull) · `#B6FF3C` (biolum eye) · `#5A7A18` (eye rim/shadow).
  *Glow note: bake a soft green eye-glow + faint skull rim-light; reads great
  on night skies and still pops (white skull) on bright day.*
- **Distinctness:** the only dark/macabre theme — black-and-bone value slam
  with toxic-green eyes; personality is spooky-fun, opposite of wholesome Buzz.

---

## 5. POP FLY · `skin_fly` — **[late-game]**

*Ref: Lichtenstein / Ben-Day comic pop-art.*

- **Hero silhouette:** a thick-black-outlined comic fly in flat primary blocks —
  red thorax, yellow abdomen — with dotted wings and a `BZZ!`-energy vibe. Bold,
  graphic, unmistakable even tiny because of the heavy ink line.
- **Signature feature:** **fat black comic outlines + Ben-Day dot fills** — a
  regular dot pattern printed across the wings and a halftone shade on the body,
  like a panel ripped from a comic. Loud and irreverent.
- **Object list + placement:**
  - Uniform ~2px black outline on EVERY element — this carries the 40px read.
  - Body in two flat colour zones: upper thorax block red `#E5202B` `(32,40)`,
    lower abdomen block yellow `#FFC21E` `(32,50)`, each ~24px wide, with a
    black divider line and a curved Ben-Day dot halftone on the shadow side.
  - Two compound eyes `(38,32)` & `(50,32)`, ~15px, flat cyan-white
    (`#EAF6FF`) domes filled with evenly-spaced blue Ben-Day dots `#2E5BFF`,
    plus one solid white comic glint wedge.
  - Wings from `(28,30)`, wide, white fill with a full Ben-Day red-dot pattern
    and thick black outline + 2 bold black veins.
  - Labellum: round pad `(46,45)`, flat pink `#FF8FB0` with black outline.
  - Bristles: 3 bold black ticks off the thorax `(26,31)`.
  - Optional: a tiny stylised motion "swoosh" line set (pure black) behind the
    wings on down-frames — pure comic energy, no glow.
- **Palette:** `#111111` (comic ink) · `#E5202B` (thorax red) · `#FFC21E`
  (abdomen yellow) · `#2E5BFF` (dot blue) · `#EAF6FF` (eye/wing white).
- **Distinctness:** the only flat-graphic / outlined / halftone concept — zero
  gradients or glow, pure 2D pop panel; visually the loudest and cheapest to
  read at distance.

---

## Ranking (best-first) + rationale

1. **BLOWFLY BARON (legendary)** — the definitive fly. Iridescent oil-slick +
   jewel-red eyes is the single most iconic, most "premium-feeling" fly look,
   and the moving sheen justifies the legendary tier without a costume gimmick.
   Highest desirability, strongest 40px read, and it's the truest to the "shiny
   real fly" everyone pictures. Ship-anchor of the set.
2. **MORTIMER DEATHFLY (legendary)** — biggest personality and the best value
   contrast (black body / bone skull / toxic-green eyes). Reads on both day and
   night, spooky-cute hooks collectors. The clear #2 legendary and a great
   thematic foil to #1.
3. **BUZZ THE HOUSEFLY (late-game)** — the wholesome default everyone will
   recognise instantly; giant friendly eyes make it the most universally
   likeable and the safest 40px read. Essential as the affordable "core" fly.
4. **VOLT-WING (legendary)** — coolest gimmick (hex eyes, mismatched wings,
   sparks) but the tech theme risks reading as "drone" over "fly" at 40px;
   keep the body fat and eyes dominant. High flex, slightly higher build risk.
5. **POP FLY (late-game)** — strongest pure graphic read and cheapest to draw,
   but the flat pop-art style is the most niche taste and leans novelty. A fun
   variety pick to round out the group, ranked last only on broad appeal.

**Best legendary showpiece:** BLOWFLY BARON — the animated oil-slick sheen +
garnet eyes is the flex that reads as premium at a glance.
**Mix:** 3 legendary (Baron, Deathfly, Volt-Wing) + 2 late-game (Buzz, Pop) —
covers realistic-premium, macabre, tech, wholesome, and graphic tastes with no
two concepts sharing a theme or palette family.

---

*References: blowfly iridescence + ruby eyes ([Dreamstime macro](https://www.dreamstime.com/photos-images/fly-insect-close-up.html)); housefly compound eyes + spongy labellum anatomy ([HowStuffWorks](https://animals.howstuffworks.com/insects/housefly1.htm), [Wikipedia](https://en.wikipedia.org/wiki/Housefly)).*
