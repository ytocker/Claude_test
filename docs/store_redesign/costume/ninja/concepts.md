# Ninja Costume Redesign — Pip the Macaw — 5 Concept Brief

**Goal:** Replace the weak current ninja (dark cowl + crimson headband + eye-slit)
with skins that read as ninja UNMISTAKABLY at ~40px in motion, by **layering
multiple ninja objects** on the base parrot. "More objects" is the point — every
concept stacks a head wrap + a back weapon + a body sash + an extra tool/wrap so
the silhouette breaks the bird's outline from several directions.

**Build target:** procedural pygame draw (polygons, circles, lines, ellipses)
layered over the existing 4-frame macaw, like the existing KFC / ghost / hat
variants in `game/parrot.py`. Signature objects push **up past the crown** and
**out past the back/tail** so they survive shrinking. No PNG sprites.

**Base read rule:** at 40px the player must clock TWO tells instantly — almost
always (1) a wrapped face with a visible **eye-slit band** and (2) a hard
diagonal object crossing the back (sword / scarf / weapon). Everything else is
flavor that fills the silhouette.

Concepts are numbered in recommended build priority (design_1 … design_5).

---

## 1. SHADOWSTRIKE — Classic Black Shadow Shinobi  `skin_ninja`

The definitive, can't-miss ninja. If only one ships, it's this. Pure black
shozoku silhouette so the bird reads as a moving shadow, lifted by ONE crimson
accent line per object so the layering stays legible against night AND day sky.

- **Silhouette / hero shape:** a near-black blob bird with a **katana hilt + scabbard
  jutting diagonally up-right past the crown and out past the tail** (one long
  straight bar crossing the whole back — the single strongest "ninja" read at 40px),
  plus two **headband tails streaming back off the skull**.
- **Layered objects & placement:**
  - Head: full **face wrap (fukumen)** in black covering beak-base to crown, leaving a
    horizontal **eye-slit** showing Pip's eyes.
  - Head: **hachimaki headband** over the wrap, crimson, with **two trailing tails**
    flicking off the back of the head (animate a little with the flap).
  - Back: **ninjato + scabbard** slung corner-to-corner, square guard (tsuba) visible,
    wrapped handle (tsuka) poking above the crown.
  - Body: **obi sash** wrapped around the belly, knotted at the side with a short hanging end.
  - Wing: **forearm wrap** — a few stacked black bands near the wing root.
  - Feet: **tabi** — split-toe look, just darken/cleft the feet.
- **Palette:** `#11131A` (shadow black body), `#1F2430` (cloth highlight), `#C8102E`
  (crimson accents: headband, sash knot, tsuba wrap), `#E8EAF0` (eye-slit + metal glint),
  `#2A2F3C` (wrap shadow).
- **Distinct + memorable:** the archetype done right — a living shadow with a sword on
  its back and ribbons trailing. Reads as "NINJA" before the player thinks. Safest, broadest appeal.

---

## 2. CRIMSON FANG — Blood Assassin Kunoichi  `skin_ninja_crimson`

The aggressive, premium-feeling red counterpart. Inverts #1: crimson cloth body
with black accents and steel. Reads as the "elite assassin" tier.

- **Silhouette / hero shape:** a **deep-crimson wrapped bird** with an **X of two crossed
  kunai strapped high on the back** (the crossed-blades X is an instant ninja/assassin tell
  and breaks the outline differently from #1's single sword), plus a **long scarf streaming
  back off the neck** well past the tail.
- **Layered objects & placement:**
  - Head: **crimson face wrap** with a black **eye-slit band**; a small **metal forehead
    plate (steel diamond)** centered on the brow catching a glint.
  - Neck: **long flowing scarf**, charcoal, trailing past the tail — animates with the flap
    (the most dynamic element, sells motion).
  - Back: **two crossed kunai** (ringed-pommel daggers) forming an X above the shoulders,
    handles up past the crown.
  - Body: **black obi** with a crimson **lacing/cross-tie** pattern down the front.
  - Wing/leg: **black wrist & shin wraps**, a couple of bands each.
  - Body: one **shuriken** tucked at the hip / sash as a small star detail.
- **Palette:** `#8B0A1A` (blood crimson body), `#B71C2B` (crimson highlight),
  `#16181E` (charcoal scarf + wraps + obi), `#D9DCE3` (steel plate + kunai + eye-slit),
  `#5E0710` (crimson shadow).
- **Distinct + memorable:** the "feared assassin." Crossed kunai + trailing scarf +
  forehead steel make it the boldest silhouette of the set. Strong premium / late-game appeal.

---

## 3. IRON RONIN — Armored Samurai-Ninja  `skin_ninja_armor`

The bulky, chunky-armor variant — visually opposite the sleek wraps of #1/#2. Adds
plate geometry so the bird reads heavier and more "boss." Inspired by Sanada red-lacquer
armor + menpo masks with fangs.

- **Silhouette / hero shape:** a **broad-shouldered armored bird** — the outline is
  widened by **two rectangular shoulder plates (sode)** flaring out past each wing, and
  topped by a **crescent-moon helmet crest (maedate)** arcing up past the crown (the
  crescent is a unique, unmistakable samurai tell at 40px).
- **Layered objects & placement:**
  - Head: **kabuto helmet brow** band with the **crescent maedate** rising above it.
  - Face: **menpo half-mask** over the lower beak with a **fanged/snarl edge** and a small
    throat guard (tare) of stacked lacquer slats.
  - Shoulders: **two sode plates** (layered horizontal lacquer slats) flaring past the wings.
  - Body: **do (chest cuirass)** — 3–4 stacked horizontal lacquer rows with bright lacing dots.
  - Back: **katana** slung lower-diagonal (shorter than #1's so it reads "armored," not "shadow").
  - Body: **obi** under the cuirass with a hanging tassel.
- **Palette:** `#A11B2E` (red lacquer plates), `#7A1322` (lacquer shadow), `#11131A`
  (under-cloth + helmet iron), `#E3B23C` (gold crescent crest + lacing dots + menpo trim),
  `#D9DCE3` (blade glint).
- **Distinct + memorable:** the only "heavy" build — plates + crescent crest + fanged
  mask give it a mini-boss presence. Gold-on-red lacquer pops hard against any sky.

---

## 4. SMOKE PHANTOM — Mystic Shadow-Clone Ninja  `skin_ninja_smoke`  (LEGENDARY-tier showpiece)

The spectacle build. Instead of relying on hard props, it leans on an **animated
smoke / shadow-clone effect** baked into the art — the kind of glow/shimmer flex the
existing dragon/phoenix skins do. Pip looks like he's mid-teleport.

- **Silhouette / hero shape:** a black shinobi whose **lower body and tail dissolve into
  a curling purple smoke plume**, with **two faint offset "after-image" clone outlines**
  trailing behind the bird (the clone echo is the signature — nothing else in the roster
  has a doubled silhouette). A **glowing eye-slit** carries the read up top.
- **Layered objects & placement:**
  - Head: **black face wrap** + headband with **glowing violet eye-slit** (animated soft glow).
  - Body: minimal black shozoku so the smoke reads cleanly.
  - Back: **single ninjato**, its blade edge catching a **violet rim-light**.
  - Tail/body base: **smoke plume** — stacked semi-transparent curling lobes, drifting/pulsing.
  - Behind bird: **1–2 ghost clone silhouettes**, offset and low-alpha, fading per frame.
  - Floating: **2–3 small shuriken** orbiting in the smoke as particles.
  - Hands/wing: a **hand-sign gesture** hint (crossed wing tips) if legible.
- **Palette:** `#0C0D14` (shadow body), `#2B1840` (smoke base), `#7B3FE4` (violet glow /
  eye-slit / blade rim — animated), `#B98CFF` (smoke highlight), `#E9DDFF` (hot core glint).
- **Distinct + memorable:** the doubled clone outline + living smoke makes it the
  "magic ninja." Animated glow justifies a **legendary** tier — a genuine flex skin.

---

## 5. NEON SEVER — Cyber-Kunoichi  `skin_ninja_cyber`  (LEGENDARY-tier showpiece)

The modern neo-Tokyo take — the visual opposite of #1's feudal black. Carbon-black
body with **electric neon edge-lighting** and a **glowing energy blade**. Second
legendary; ensures the set spans feudal → mystic → future.

- **Silhouette / hero shape:** a sleek black bird **outlined in glowing cyan neon piping**,
  with a **holographic energy katana on the back glowing hot from hilt to tip** (the only
  light-emitting straight bar in the set) and a **single bright neon visor band** across the eyes.
- **Layered objects & placement:**
  - Head: **tech face mask** (matte black) with a **horizontal neon visor slit** (cyan,
    animated pulse) replacing the cloth eye-slit.
  - Head: thin **headband with a small glowing emblem chip**.
  - Back: **energy ninjato** — straight beam blade, magenta-to-cyan gradient, glow halo,
    hilt up past the crown.
  - Body: **black bodysuit** with **neon seam lines** tracing the chest and wing edges.
  - Wing/leg: **neon-banded wraps** (thin glowing rings on forearm + shin).
  - Floating: **one holographic shuriken** spinning at the hip, drawn as a glowing ring-star.
- **Palette:** `#0A0B10` (carbon body), `#15171F` (panel shade), `#19E0FF` (cyan neon
  piping / visor — animated), `#FF2D9B` (magenta accent + blade core), `#EAFBFF` (hot glow core).
- **Distinct + memorable:** the futurist outlier — neon edge-glow + energy blade make it
  pop hardest against the night sky. Cyber/feudal contrast gives the store visible range.
  Animated neon justifies **legendary** tier.

---

## Ranking rationale & build notes

1. **SHADOWSTRIKE (#1)** — ship first. The canonical "obvious ninja"; lowest risk,
   broadest appeal, the one that fixes the original brief directly. Single sword + headband
   tails = bulletproof 40px read.
2. **CRIMSON FANG (#2)** — strongest *silhouette* of the set (crossed kunai X + trailing
   scarf). Premium feel, clean recolor-plus-new-props relationship to #1.
3. **IRON RONIN (#3)** — the essential "heavy/armored" contrast so the set isn't all sleek
   wraps. Crescent crest + sode plates + fanged menpo are unique geometry.
4. **SMOKE PHANTOM (#4)** — best **legendary showpiece**: the shadow-clone double outline is
   the most original idea here and the animated smoke/glow earns the flex tier.
5. **NEON SEVER (#5)** — second legendary, the future-facing outlier that gives the store
   tonal range (feudal → mystic → cyber).

**Tier mix:** #1–#3 standard unlockables; **#4 and #5 legendary** (animated glow/shimmer/
energy baked into the art, dragon/phoenix-style).

**Distinctness check (all 5 differ in silhouette-breaker):** #1 = single back sword +
ribbon tails; #2 = crossed-kunai X + scarf; #3 = wide shoulder plates + crescent crest;
#4 = doubled clone outline + smoke plume; #5 = neon edge-glow + energy beam blade. No two
share a hero shape.

**Shared build kit a graphics-designer can reuse across all 5:** face wrap with eye-slit,
headband, a back-slung straight weapon, an obi sash, forearm/shin wraps. Each concept
swaps the hero prop + palette on top of that kit.

---

### Sources
- [Shinobi Shōzoku — traditional ninja uniform parts (NinjutsuShop)](https://www.ninjutsushop.com/en/ninjutsu-equipment/ninjutsu-guide/shinobi-shozoku/how-to-choose-your-traditional-ninja-uniform-shinobi-shozoku.html)
- [6 Types of Shinobi Shozoku (Kobudo Mart)](https://kobudomart.com/blog/6-types-of-shinobi-shozoku/)
- [Ninja Warrior Clothing & Costume (Warriors and Legends)](https://www.warriorsandlegends.com/japanese-warriors/ninja-warriors/ninja-warrior-clothing-and-costume/)
- [Cyber Kunoichi: The Modern Ninja Assassin (1500all, DeviantArt)](https://www.deviantart.com/1500all/art/Cyber-Kunoichi-The-Modern-Ninja-Assassin-1094691713)
- [Kunoichi character design (Games Artist)](https://gamesartist.co.uk/kunoichi/)
- [Samurai Armor Glossary — kabuto, menpo, sode, maedate (Romance of Men)](https://romanceofmen.com/blogs/armor-knowledge/samurai-armor-glossary)
- [Samurai Armor: 15 Parts (Japan Clothing)](https://japan-clothing.com/blogs/japan/samurai-armor-15-parts-of-a-japanese-warrior-outfit-history-types-real-examples)
- [Shuriken Shadow Clone Technique (Narutopedia)](https://naruto.fandom.com/wiki/Shuriken_Shadow_Clone_Technique)
- [Ninja Throwing Star — design history (MoMA Design and Violence)](https://www.moma.org/interactives/exhibitions/2013/designandviolence/ninja-throwing-star-various-designers/)
