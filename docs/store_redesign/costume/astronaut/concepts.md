# Astronaut Costume Redesign — Pip the Macaw — 5 Concept Brief

**Goal:** Replace the weak current astronaut (just a glass helmet on the head of an
otherwise-scarlet macaw) with skins that read UNMISTAKABLY as an astronaut at
~40px in motion, by **layering multiple space objects ALL OVER the bird** —
head + back + body + limbs — the way the ninja and viking redesigns layer their
themed objects so the silhouette breaks from several directions. A lone helmet is
exactly what we're replacing; "all over" is the point.

**Build target:** procedural pygame draw (polygons, circles, lines, ellipses,
gradients, glows) layered over the existing 4-frame macaw, like the KFC / ghost /
hat variants in `game/parrot.py`. Full-body suit **recolors** (white / orange /
black / silver / cosmic body) are available via the palette system. Signature
objects push **up past the crown** and **out past the back/body** so they survive
shrinking. No PNG sprites.

**Base read rule:** at 40px the player must clock TWO tells instantly — almost
always (1) a **helmet** (bubble dome or angular visor) breaking the head outline,
and (2) a **back element** (PLSS life-support backpack or rocket/jetpack) breaking
the back/tail outline — plus a recolored **suited torso** with a chest detail so
the body isn't bare scarlet. Everything else is flavor that fills the silhouette.

**Face decision per concept:** a helmet hides the face, so each concept states
whether the **visor is UP** (Pip's eye + a peek of beak visible inside a clear
dome — friendliest, keeps charm) or **DOWN** (a solid reflective/gold visor with a
single bright sweep highlight — more iconic, must stay a clean shape not a muddy
blob). We favor visor-up on the friendly everyday skins and visor-down on the
showpiece tiers.

Concepts are numbered in recommended build priority (design_1 … design_5).

---

## 1. MOONWALKER — Classic NASA White EVA Spacewalker  `skin_astronaut`

The definitive, can't-miss astronaut. If only one ships, it's this — the iconic
white Apollo/EMU moon-walker everyone pictures when they hear "astronaut." Pure
white suit so the bird reads as a bright marshmallow blob, lifted by the gold
visor and the chunky backpack.

- **Silhouette / hero shape:** a **rounded white puffy blob bird** with a **boxy
  PLSS life-support backpack jutting up past the crown and out past the back**
  (the single hardest-edged tell — a fat rectangle on the back instantly says
  "spacewalker"), topped by a **round bubble helmet** with a **gold visor**.
- **Layered objects & placement:**
  - Head: round **bubble helmet** (clear dome) with the iconic **gold reflective
    visor DOWN** — a curved gold shape filling the lower-front of the dome with a
    single diagonal white sweep highlight; a thin white **helmet rim ring** at the
    neck. (Gold visor = the postcard read; keep it a clean curved shape.)
  - Back: chunky **white PLSS backpack** as a rounded rectangle rising above the
    crown and bulging past the back, with a small **antenna nub** on top.
  - Body: full **white EVA suit recolor** — soft puffy torso with a couple of
    horizontal **joint/segment seam lines** at the belly to read as fabric rings.
  - Chest: **DCM control panel** — a small rounded rectangle with 2–3 colored
    button dots (red/green) and a thin gauge line, centered on the chest.
  - Chest/back: a curved **oxygen hose** looping from the backpack around to the
    chest panel.
  - Limbs: **blue arm stripes** on the wing root; thick rounded **white gloves**
    at the wingtips and chunky **white moon boots** on the feet.
- **Palette:** `#F2F4F8` (suit white), `#C7CDD8` (suit shadow / seam),
  `#E8A12C` (gold visor), `#2C6BD6` (blue arm/leg stripes + button), `#3A3F4A`
  (backpack/helmet rim dark accent).
- **Distinct + memorable:** the archetype done right — fat white blob, gold face,
  brick of a backpack. Reads "ASTRONAUT" before the player thinks. Safest, broadest
  appeal, and the one casual players will expect to exist.

---

## 2. PUMPKIN SUIT — Orange Apollo / Launch-Entry Astronaut  `skin_astronaut_orange`

The bold high-saturation counterpart to #1 and the most COLOR-distinct of the set
— the orange "pumpkin suit" worn at launch. Pops hard against a blue daytime sky
and reads instantly different from the white EVA without changing the silhouette
family. Visor UP here so we get a friendly face inside the dome.

- **Silhouette / hero shape:** a **bright-orange suited bird** with a **clear
  fishbowl helmet UP showing Pip's face**, a **white parachute/survival pack on
  the back**, and a fat **white neck ring** separating the orange body from the
  clear dome.
- **Layered objects & placement:**
  - Head: clear **bubble helmet, visor UP** — a clean glass dome over the head so
    Pip's eye + beak read clearly inside (one curved white reflection arc on the
    glass for shine), seated on a thick **white pressure-neck ring**.
  - Back: **white survival/parachute pack** (rounded squarish bulge) above and
    behind the shoulders, smaller and softer than #1's hard backpack so it stays
    distinct.
  - Body: full **orange suit recolor** with **white vertical zip line** down the
    chest center and **gray segment rings** at the belly.
  - Chest: small **NASA-ish mission patch** — a round badge with a tiny star, on
    the upper chest; plus a short silver **comms connector** dot.
  - Limbs: **gray/silver gloves** at wingtips, **black boots** on feet, thin
    **gray stripe** on the wing root.
- **Palette:** `#F26A1B` (suit orange), `#C24E0F` (orange shadow), `#F2F4F8`
  (neck ring + pack white), `#9AA1AD` (gray gloves/segments), `#1E2330` (visor
  glass tint + boots).
- **Distinct + memorable:** the only warm/orange skin — maximum sky contrast and
  a friendly visible parrot face inside a fishbowl. Reads as the "ready for launch"
  rookie; cheerful and unmistakably a different astronaut from #1.

---

## 3. STARFARER — Cosmic / Galaxy Deep-Space Explorer  `skin_astronaut_cosmic` *(LEGENDARY showpiece)*

The flex. A deep-space explorer whose suit is a living starfield with a glowing
visor and an aura — the dragon/phoenix-tier spectacle of the astronaut line. This
is the one players chase. Visor DOWN and glowing so the helmet is a beacon.

- **Silhouette / hero shape:** a **dark cosmic-blue/purple suited bird** with a
  **glowing helmet** breaking the crown and a **back-mounted glowing thruster /
  star-trail** streaming off the back-tail (animated shimmer), wrapped in a faint
  **aura halo**.
- **Layered objects & placement:**
  - Head: round helmet with a **DOWN visor that glows** — a deep indigo curved
    visor with a **cyan-to-magenta rim glow** and a couple of tiny **star sparkles**
    twinkling on the glass; soft outer glow ring around the whole dome.
  - Back: **energy thruster pack** instead of a metal backpack — a small dark unit
    with a **comet-trail of star particles / gradient streak** flowing out past the
    tail (reuse the existing particle/shimmer style; this is the legendary tell).
  - Body: full **cosmic suit recolor** — deep navy-to-violet gradient torso
    speckled with tiny **white star dots** (a baked starfield), with faint
    **nebula wisps** (a soft magenta/teal gradient patch) on the chest.
  - Chest: a glowing **constellation panel** — 3–4 star dots joined by thin glowing
    lines (a mini constellation) in place of a button panel.
  - Limbs: **cyan glow seams** along the wing root and a thin glow line down each
    leg; small star-twinkle at the wingtips (gloves implied by the glow caps).
- **Palette:** `#12102A` (deep cosmic body), `#2A2160` (violet mid),
  `#3FE0FF` (cyan glow), `#FF4FD8` (magenta nebula glow), `#FFFFFF` (stars +
  visor highlight). *Glow/shimmer: pulse the visor rim + animate the back
  star-trail with the flap; bake a subtle nebula gradient into the torso.*
- **Distinct + memorable:** the spectacle pick — a walking galaxy with a glowing
  face and a comet tail. Survives both day and night sky because the glow self-
  contrasts. The justified legendary flex of the astronaut roster.

---

## 4. ROCKETEER — Retro 1950s Silver Raygun-Gothic Spaceman  `skin_astronaut_retro`

The charm/novelty pick — pulp sci-fi "Spaceman Spiff" energy: shiny silver suit,
fishbowl dome, fins, and a literal rocket on the back. The funniest, most
characterful entry and visually the furthest from the realistic suits, so it earns
its slot on distinctness. Visor UP for maximum cartoon face.

- **Silhouette / hero shape:** a **chrome-silver bird** with a **fishbowl bubble
  dome (face visible) topped by a tall antenna**, and a **finned retro rocket
  jetpack** with **fins flaring out past the tail** and a little **flame** below —
  the fins + antenna are the unmistakable raygun-gothic tell.
- **Layered objects & placement:**
  - Head: tall clear **fishbowl helmet, visor UP** — Pip's face fully visible; a
    bright **chrome rim ring** at the base and a single bold reflection streak on
    the glass; a **bobbing antenna with a glowing ball tip** sticking up past the
    dome (animate the wobble with the flap).
  - Back: **retro rocket-pack** — a rounded silver cylinder/torpedo with **two red
    tail fins** flaring out past the body, and a small **orange/yellow flame** or
    glow puffing from the nozzle at the bottom (tie a tiny flicker to the flap).
  - Body: full **silver/chrome suit recolor** with a **vertical row of big round
    buttons** down the chest and a **wide belt** with a square buckle at the waist.
  - Chest: a small **circular gauge dial** (retro instrument) beside the buttons.
  - Limbs: **red ringed cuffs** at the wing roots and **chunky silver boots** with
    a red sole stripe.
- **Palette:** `#C9D0DA` (chrome silver), `#8A93A3` (chrome shadow),
  `#E23B3B` (red fins/cuffs/buttons), `#F2C233` (antenna tip + flame),
  `#2A2F3C` (helmet rim + dark accents).
- **Distinct + memorable:** pure retro-futurist fun — fins, fishbowl, antenna,
  rocket flame. The "shouldn't be real" delight pick; instantly reads as old-
  comic-book spaceman and nothing like the modern suits. Big charm-per-pixel.

---

## 5. STARLINER — Modern SpaceX-Style Sleek Black-and-White Pilot  `skin_astronaut_modern`

The clean, premium "near-future" look — the white-tuxedo-with-black-trim SpaceX
IVA flightsuit and its small angular visor. The most minimal/sleek of the set,
which is exactly its distinctness: smooth shapes, sharp two-tone, no chunky
backpack. Visor DOWN with a hard black faceplate.

- **Silhouette / hero shape:** a **smooth white bird** with a **small angular
  black-visor helmet** (oval, not bubble — flatter, more aggressive) and a **slim
  black flight-pack / harness on the back** rather than a fat PLSS — sleek, not
  puffy. The crisp black-on-white two-tone is the read.
- **Layered objects & placement:**
  - Head: **oval helmet** with a **DOWN angular black visor** — a hard-edged dark
    faceplate (slightly hexagonal) with one sharp diagonal white glint; thin white
    helmet shell around it; a small **black chin/comms wedge**.
  - Back: **slim black flight-pack / umbilical harness** — a low-profile dark unit
    with a single **gray umbilical hose** curving to the hip (intentionally smaller
    than #1's backpack to stay sleek and distinct).
  - Body: full **white suit recolor** with **black accent panels** — black across
    the **collarbone/shoulders** and a black stripe down each side; clean, glossy.
  - Chest: a minimalist **rectangular black chest module** with a single thin
    **cyan status line / dot** (modern HUD look).
  - Limbs: **black gloves** at the wingtips, **black boots**, and a thin black
    seam line up the wing root — sharp two-tone throughout.
- **Palette:** `#F4F6FA` (suit white), `#15171C` (black visor / accent panels),
  `#5A6170` (gray umbilical / shadow), `#2BC6E0` (cyan status accent),
  `#C8CDD6` (suit shadow).
- **Distinct + memorable:** the sleek "stormtrooper-tuxedo" modern astronaut —
  sharp black visor and crisp two-tone instead of puffy white. The premium
  near-future counterpoint that makes the set feel complete across eras (Apollo →
  retro → modern → cosmic).

---

## Ranking & call-outs

1. **MOONWALKER** (white EVA) — ship-first must-have; the archetype, broadest
   appeal, the skin players expect to exist.
2. **PUMPKIN SUIT** (orange) — best color contrast against the rest of the set;
   friendly visible face; instantly distinct from #1.
3. **STARFARER** (cosmic) — **the legendary showpiece**; glowing galaxy suit with a
   comet-trail back, the dragon/phoenix-tier flex of the line.
4. **ROCKETEER** (retro silver) — strongest charm/novelty; furthest visual distance
   from the realistic suits, pure raygun-gothic fun.
5. **STARLINER** (modern SpaceX) — sleek minimal premium; rounds the set across
   space-suit eras with crisp black-on-white.

**Spread check (distinct from each other):** white / orange / cosmic-navy / chrome-
silver / black-and-white — five different value+hue families; bubble-down-gold vs
bubble-up-clear vs glowing-down vs fishbowl-up vs angular-black-down visors; chunky
PLSS vs survival pack vs star-thruster vs finned rocket vs slim flight-harness on
the back. No two are "another white EVA suit."

**Strongest single pick:** MOONWALKER. **Best legendary showpiece:** STARFARER.

---

### Research sources

- [Extravehicular Mobility Unit — Wikipedia](https://en.wikipedia.org/wiki/Extravehicular_Mobility_Unit)
- [NASA EMU — ISS Spacewalk Suit (Orbital Radar)](https://orbitalradar.com/spacesuits/emu)
- [Apollo/Skylab spacesuit — Wikipedia](https://en.wikipedia.org/wiki/Apollo/Skylab_spacesuit)
- [Launch Entry Suit — Wikipedia](https://en.wikipedia.org/wiki/Launch_Entry_Suit)
- [Advanced Crew Escape Suit (ACES) — Wikipedia](https://en.wikipedia.org/wiki/Advanced_Crew_Escape_Suit)
- [Why Are Astronauts' Spacesuits Orange? — Live Science](https://www.livescience.com/32618-why-are-astronauts-spacesuits-orange.html)
- [Orlan space suit — Wikipedia](https://en.wikipedia.org/wiki/Orlan_space_suit)
- [SpaceX IVA Suit — Crew Dragon Flight Suit (Orbital Radar)](https://orbitalradar.com/spacesuits/spacex-iva-suit)
- [How SpaceX's sleek spacesuit changes astronaut fashion — Space.com](https://www.space.com/spacex-crew-dragon-spacesuits-explained.html)
- [Raygun Gothic — TV Tropes](https://tvtropes.org/pmwiki/pmwiki.php/Main/RaygunGothic)
- [Raygun Gothic — Aesthetics Wiki](https://aesthetics.fandom.com/wiki/Raygun_Gothic)
