# PENGUIN Animal-Skin Redesign — 5 Concept Brief

**Goal:** Replace the flat current `skin_penguin` — a navy-back / off-white-belly
egg body with a tiny orange triangle beak, one rosy cheek dot, two stubby
flippers and orange webbed feet. It reads as default "penguin clip-art": no
crest, no signature silhouette-breaker, no memorable hook, and it does NOT earn
its 520-coin slot next to toucan, bat, flamingo, bald eagle, owl and bee.

**The fix:** every concept layers **multiple distinguishing features across
head + crown + back + belly + flippers + feet** so the silhouette breaks the
plain egg from several directions. Each must still read **unmistakably as a
penguin** and survive the 40px in-motion "truth read" — at that size only the
hero shape + the dark/light two-tone split + one bold colour pop survive, so
every concept leads with a crown/head silhouette-breaker that pushes **up past
the crown (~y=24)** plus a strong head-colour tell.

**Build target:** procedural pygame draw (ellipses, polygons, circles, lines)
layered on the existing 4-frame flipper flap (wing angles 50 / 10 / -30 / -40,
rotated ~`angle*0.7`). Like the existing animal skins and the parrot KFC/ghost/
hat variants. No PNG sprites. 2px-minimum detail so it survives downscale.

**Anchors (confirmed in `game/animal_skins.py`, 64×84 canvas):** body centre
BCX/BCY ≈ **(32, 44)**, head centre HCX/HCY ≈ **(44, 34)**, crown top ≈
**y=24**, beak tip extends to ~x=55. Feet sit at ~y=BCY+16…20.

**Base read rule:** at 40px the player must clock TWO tells instantly — (1) the
**dark-back / light-belly split** (kept in every concept, never broken), and (2)
the **crown silhouette-breaker** (spiky crest / orange ear-patch / bobble beanie
/ snorkel mask / aurora ice-crown). Everything else fills the shape.

Concepts are numbered in recommended build priority (design_1 … design_5).

---

## 1. ROCKHOPPER — Spiky-Crest Punk  `skin_penguin` (keeps the id)

The most iconic *penguin-as-penguin* upgrade. A real species with the single
strongest silhouette in the whole genus — fixes the original brief directly by
adding the exact thing it lacks: a crown-breaking crest.

- **Hero silhouette:** a **fan of spiky upswept golden-yellow brow plumes
  exploding up-and-out past the crown** off a black head, paired with **bold red
  eyes**. The yellow spike-fan against the dark head is unmistakable at 40px and
  is the truest "that's a penguin with attitude" read.
- **Objects & placement:**
  - Head (HCX,HCY): black dome merging into the body (keep the little-neck look);
    white face mask kept but slightly narrowed so the brow reads.
  - Crown (y≈24): **5–6 spiky yellow eyebrow plumes** sweeping up and back from
    above each eye — a jagged triangular fan, thicker at the brow, tapering to
    points; a couple stray flicks past the silhouette so it never reads as a
    smooth cap.
  - Eyes: **fiery red-orange iris dots** (the species tell) with a tiny white
    catch-light.
  - Beak: a **thicker stubby orange beak** (slightly fatter than the current thin
    triangle) for the chunky rockhopper bill.
  - Back/belly: existing navy-back / white-belly split, unchanged hero contrast.
  - Flippers: the standard stubby flap, dark with a thin pale leading edge.
  - Feet: **pink-orange webbed feet** (rockhoppers run on rock — keep them set
    apart so they read as "hopping" stance).
- **Palette:** `#1E2233` (near-black head/back), `#F7F4EC` (white belly/face),
  `#FFD21E` (yellow crest plumes), `#FF8A1E` (orange beak/feet), `#E23B2E`
  (red eye). High contrast, holds day and night.
- **Distinctness:** the only concept whose hero breaker is a **spiky yellow
  crest + red eyes**; it's the punk/attitude penguin, where #2 is regal-smooth,
  #3–4 are gear-themed and #5 is luminous. Adds the crest the flat original
  never had.

---

## 2. EMPEROR — Regal Gradient Royal  `skin_penguin_emperor`

The premium, grown-up penguin: tall and stately, carried by a **gradient** the
flat build can't show. The "elegant" tier of the set.

- **Hero silhouette:** a **taller, more upright slate body** with a **bright
  orange ear-patch that melts down into a golden-yellow throat-bib** — the
  "headphones into a glowing collar" gradient is the king/emperor signature and
  reads as warmth bleeding onto a cool body even at 40px.
- **Objects & placement:**
  - Body: slightly **taller egg** (stretch the back ellipse up) for the regal
    stance; back painted as a **vertical slate gradient** (cooler/darker up top,
    lighter steel toward the belly join) — a richness the flat fill lacks.
  - Head (HCX,HCY): smooth black-grey head, **no crest** (deliberate contrast to
    #1) — the elegance comes from colour, not spikes.
  - Cheeks/ears: a **teardrop orange ear-patch** on each side of the head that
    **fades orange→amber→pale-yellow** as it runs down into the throat.
  - Belly: white belly with a soft **yellow-washed upper-chest bib** under the
    throat gradient (the king-penguin glow).
  - Beak: a **long slender beak with a coral-pink lower mandible stripe** (the
    king/emperor mandible plate) — more refined than the blunt orange triangle.
  - Flippers: slate, edged with a thin pale-blue rim so they catch light against
    the gradient body.
  - Feet: dark slate-grey webbed feet (cooler than #1's, to stay regal).
- **Palette:** `#2C3550` (slate back, top of gradient), `#5A6A86` (steel, lower
  gradient), `#FFFDF6` (white belly), `#FF7A18` (ear-patch orange) →
  `#FFD24A` (throat-bib yellow), with `#FF9CB0` (coral mandible stripe).
- **Distinctness:** the only **gradient** concept (slate body + orange→yellow
  ear-to-throat melt) and the only crest-less, "elegant by colour" read; clearly
  the upscale royal vs #1's punk and #3–4's gear.

---

## 3. POLAR EXPLORER — Bobble-Beanie Adventurer  `skin_penguin_explorer`

The character/charm pick: a penguin bundled up for its own habitat. Maximum
layered gear, maximum "aww" — the most personality-forward of the set.

- **Hero silhouette:** a **chunky knitted bobble-beanie pushing up past the
  crown** (pom-pom on top) over the black head, with a **fat striped scarf
  flaring out off the neck** — beanie-up + scarf-out breaks the egg from both
  the top and the side, instantly "cozy explorer" at 40px.
- **Objects & placement:**
  - Crown (y≈24): **ribbed knit beanie** as a rounded cap with a **folded brim
    band** and a **round pom-pom bobble** sitting above the crown line; 2–3 knit
    ridge lines so it doesn't read as a bald dome.
  - Head: black head + white face mask kept; **two small round snow-goggles** (or
    a single tinted band) resting on the brow under the beanie for a second tell.
  - Neck/back: a **chunky striped scarf** wrapping the neck with **one tail-end
    flicking out past the back/body outline** (animates subtly with the flap).
  - Belly: white belly kept; optional tiny **wooden toggle/button** row hint where
    the scarf crosses the chest.
  - Beak: standard small orange beak, rosy cold-nipped cheek kept (sells "chilly").
  - Flippers: dark, with **little knit mitten cuffs** at the tips (third gear tell).
  - Feet: orange webbed feet, optionally with **tiny snow-boot toe caps**.
- **Palette:** `#1E2233` (head/back), `#F7F4EC` (belly/face), `#D24B4B` +
  `#3B7DD8` (red/blue scarf + beanie stripes — bold complementary pop),
  `#F5E6C8` (cream pom-pom / knit highlight), `#FF8A1E` (beak/feet).
- **Distinctness:** the only **clothed/winter-gear** concept (beanie + bobble +
  striped scarf + goggles + mitten cuffs) — stacked accessories, not one lonely
  hat; reads "adventurer," where #4 is underwater and #1/#2/#5 are bare-bird.

---

## 4. SCUBA DIVER — Snorkel Goof  `skin_penguin_diver`

The funny one, and a clever in-joke: a flightless swimmer kitted out to do the
thing it already does. Different body language from the rest — clearly aquatic.

- **Hero silhouette:** a **domed snorkel mask across the eyes with a curved
  snorkel tube hooking up past the crown**, and the **flippers reading as wide
  swim-fins** — mask + up-hooked tube is a goofy, unmistakable break against the
  round head even tiny.
- **Objects & placement:**
  - Head (HCX,HCY): black head kept; a **rounded glass dive-mask** sits over the
    eye zone — a pale-cyan oval lens with a dark rubber rim, **eyes visible
    through it** enlarged and happy (lens magnifies = extra charm).
  - Crown (y≈24): a **J-curved snorkel tube** rising from the mask strap up past
    the crown, with a small mouthpiece elbow — the top silhouette-breaker.
  - Belly: white belly kept; optional **two-strap dive-mask band** crossing the
    side of the head.
  - Flippers: redrawn a touch **broader and more paddle-like** to read as swim
    fins on the flap (still the 4-pose stubby flap, just wider tips).
  - Feet: **bright fin-style webbed feet**, slightly elongated, to echo the
    diver theme.
  - Accent: **2–3 small round bubbles** drifting up off the snorkel tip (tiny
    circles) for a moving aquatic tell — cheap particle-style charm.
  - Beak: small orange beak peeking below the mask.
- **Palette:** `#1E2233` (head/back), `#F7F4EC` (belly/face), `#19B6C4`
  (cyan mask lens + fin accents), `#222A33` (mask/snorkel rubber), `#FF8A1E`
  (beak/feet), with `#CFF6FB` bubble glints.
- **Distinctness:** the only **underwater-gear / aquatic** concept (dive mask +
  up-hooked snorkel + paddle fins + bubbles); cyan is a colour no other concept
  uses, and it's the comedic counterweight to #2's elegance.

---

## 5. AURORA KING — Frost-Crowned Showpiece  `skin_penguin_aurora`  *(LEGENDARY-tier)*

The flex. The spectacle build that justifies a premium price — the only
**luminous** penguin, leaning on animated glow + crystal sheen baked into the
art the way dragon/phoenix do.

- **Hero silhouette:** a **crown of faceted ice-crystal spikes** rising past the
  crown, wreathed in a **ribbon of glowing aurora light arcing over the head**,
  on a frost-pale body with a **crystalline sheen** — the glowing crest + ice-
  crown is the boldest, brightest silhouette of the set and the only light-
  emitting one.
- **Objects & placement:**
  - Crown (y≈24): **3–5 faceted ice spikes** (pale-blue/white triangular crystals
    with a bright inner highlight) fanning up past the crown like a frozen tiara.
  - Aura: a **soft aurora ribbon** (green→cyan→violet gradient sweep) arcing above
    the head, with a faint **shimmer/glow that animates** along its length with
    the flap — the legendary tell.
  - Head/back: **frost-pale slate-blue plumage** (a body recolor — the cool
    outlier of the set) with the dark/light split preserved as deep-ice-blue back
    vs near-white belly.
  - Belly: near-white belly with a faint **crystalline facet sheen** (a few thin
    pale highlight lines suggesting ice).
  - Eyes: cool **icy-cyan glowing eyes** with a soft bloom.
  - Beak: a **pale frost-blue beak with a cold rim-glint** (not warm orange — the
    only non-orange beak, sells "frozen royalty").
  - Flippers: ice-pale with **frost-crystal tips** and a faint cold rim-glow.
  - Feet: pale blue webbed feet with frost-white toe glints.
- **Palette:** `#BFE0F2` (frost-pale body), `#3E5B72` (deep-ice back/shadow),
  `#F2FAFF` (white belly / ice highlights / crystal cores), aurora sweep
  `#4FE3A0` → `#39B6FF` → `#A06BFF`, with `#DFFBFF` glow-core. Animated aurora
  shimmer + soft eye/crystal bloom.
- **Distinctness:** the only **legendary / luminous / body-recolor** concept
  (glowing aurora ribbon + faceted ice-crown + frost-blue plumage + frost beak);
  nothing else emits light or recolors the body, making it the unmistakable
  showpiece next to dragon and phoenix.

---

## Ranking rationale

1. **ROCKHOPPER (#1)** — ship first. The canonical "penguin with a signature,"
   lowest risk, broadest appeal, and the most direct fix for the flat original:
   it adds exactly the crown-breaking crest the brief calls out as missing.
   Spiky yellow crest + red eyes = bulletproof 40px read, and it can keep the
   `skin_penguin` id outright.
2. **EMPEROR (#2)** — the strongest **premium / elegant** read (slate gradient
   body + orange-to-yellow ear-to-throat melt). The grown-up royal tier; a clean
   colour-driven cousin that earns the 520-coin feel without any worn props.
3. **POLAR EXPLORER (#3)** — the essential **character/charm** contrast so the
   set isn't all bare birds. Stacked winter gear (beanie + bobble + striped scarf
   + goggles + mitten cuffs) gives the store the most personality and an
   instantly different silhouette.
4. **SCUBA DIVER (#4)** — the **comedic, aquatic** outlier; different body
   language and a cyan palette no one else uses, plus the in-joke of a flightless
   swimmer geared up to swim. Great variety pick.
5. **AURORA KING (#5)** — the best **legendary showpiece**: glowing aurora crest
   + faceted ice-crown + frost-blue recolor is the most spectacular idea here,
   and the animated glow earns the flex tier alongside dragon/phoenix.

**Tier mix:** #1–#4 standard unlockables; **#5 legendary** (animated aurora
glow / crystal sheen / body recolor baked into the art).

---

## Distinctness matrix (each has a unique crown silhouette-breaker)

| # | Name | Crown breaker | Head colour tell | Body | Palette pop |
|---|------|---------------|------------------|------|-------------|
| 1 | ROCKHOPPER | spiky yellow crest fan | red eyes | navy/white | yellow + red |
| 2 | EMPEROR | (none — smooth, by design) | orange→yellow ear-to-throat gradient | slate gradient | orange-amber-coral |
| 3 | POLAR EXPLORER | bobble beanie + pom-pom | goggles + scarf flare | navy/white | red+blue stripes |
| 4 | SCUBA DIVER | up-hooked snorkel tube | cyan dive-mask lens | navy/white | cyan |
| 5 | AURORA KING | faceted ice-crown + aurora ribbon | glowing cyan eyes | frost-blue recolor | green→blue→violet glow |

No two share a hero shape. #2 is the only gradient build, #4 the only aquatic /
cyan build, #5 the only luminous build + only body recolor + only non-orange
beak. All five preserve the dark-back / light-belly split (#5 as ice-blue vs
near-white) and all read at 40px.

---

## Shared build kit a graphics-designer can reuse across all 5

A common penguin chassis the designer can layer onto: (a) the **egg body** with
the **dark back / light belly two-tone split** (the one constant — never break
it); (b) the **little-neck head** merging into the body at HCX/HCY; (c) the
**4-pose stubby flipper flap** (`angle*0.7` rotation), widened only for #4; (d)
**webbed feet** at the body base; (e) a **beak** at the head front (small orange
triangle by default, restyled per concept — fatter #1, slender coral-striped #2,
frost-blue #5).

Per concept, swap only: the **crown breaker** (yellow crest / nothing / beanie+
bobble / snorkel tube / ice-crown+aurora), the **head colour tell** (red eyes /
orange-yellow ear gradient / goggles+scarf / cyan mask lens / glowing eyes), the
**body treatment** (flat navy / slate gradient / flat navy / flat navy / frost-
blue recolor + sheen) and the **palette**. #5 adds the only animated glow layer.

---

### Sources
- [SeaWorld — Penguin physical characteristics](https://seaworld.org/animals/all-about/penguin/physical-characteristics/)
- [HX Expeditions — Meet the penguins of Antarctica](https://www.travelhx.com/en-us/stories/meet-the-penguins-of-antarctica/)
- [PenguinWorld — Rockhopper penguin](http://www.penguinworld.com/types/rockhopper.html)
- [ASOC — Macaroni penguins](https://www.asoc.org/learn/macaroni-penguins/)
- [Antarctica Cruises — The 7 penguin species](https://www.antarcticacruises.com/guide/antarctic-penguins)
