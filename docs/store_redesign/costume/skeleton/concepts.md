# Skeleton Costume Redesign — Pip the Macaw — 5 Concept Brief

**Goal:** Replace the muted current `skin_skeleton` (warm ivory bone tracing
`#F5F0DC` on a deep-navy `#26283E` flesh body — Day-of-the-Dead-ish, subtle,
washed out) with 5 skins that each read UNMISTAKABLY as a SKELETON at ~40px in
motion, are CLEARLY DISTINCT from that muted navy/ivory look, and are clearly
distinct from EACH OTHER. The fix for the original: bones must become the
**brightest, highest-contrast element** on the bird, full-body (skull + ribs +
spine + wing bones + leg bones), each design carrying ONE strong themed layer
(clean white, sugar-skull paint, spectral fire-aura, pirate gear, frost/flame,
gold/lich) that gives it its own silhouette and color identity.

**Build target:** procedural pygame draw (polys, ellipses, arcs, lines, additive
bloom for glow) layered over the existing 4-frame macaw, like the KFC / ghost /
hat variants and the current `_paint_skeleton` in `game/store_skins.py`. Body
recolors (charred-black, frost-pale, void-black flesh) come via the palette
system. No PNG sprites. 2px minimum line weight on every bone so nothing
vanishes at 40px.

**Base read rule (the "truth read"):** at 40px in motion the player must clock
(1) a **skull with hollow eye sockets** at the head anchor and (2) a **ribcage
of arcs across the chest with a spine** — bones being the brightest element.
Each concept's themed layer is the third tell that makes it distinct. The wing
bones must trace the 4 flap poses (so the flap reads as a clattering skeletal
wing), and leg bones must show below the body.

Concepts are numbered in recommended build priority (design_1 … design_5).

---

## 1. BONEWHITE — The Classic, Done Right  `skin_skeleton` (design_1)

The definitive, can't-miss skeleton. If only one ships, it's this — pure
high-contrast bright-white bone on a near-black body, the "default skeleton"
the muted original failed to be. Direct fix for the washed-out ivory-on-navy:
crank bone to true white, drop the flesh to near-black, add a hard dark
keyline so it survives the day sky.

- **Hero silhouette / tell:** a **stark white bone-bird** — a clean rounded
  **skull** with two big hollow black eye sockets, a **bold ladder of white
  rib-arcs** down the chest, and a **white-boned wing** that clatters as it
  flaps. The white-on-black value split is the whole read; no theme color to
  distract.
- **Bone layout + themed objects:**
  - Skull: rounded cranium at the head anchor, **two large round-to-teardrop
    eye sockets** (pure black holes), a small triangular nose hollow, a
    **stitched/blocky tooth grin**.
  - Ribs: **5–6 paired rib-arcs** sweeping down from a central sternum line.
  - Spine: a short **vertebra-bead column** from skull base into the ribcage.
  - Back/wing: **wing rendered as radiating finger-bones** (phalanges) from a
    bone "wrist," tracing all 4 flap poses.
  - Legs: **two thin bone-pair legs** with knob knee-joints and 3-claw bone
    feet below the body.
- **Palette:**
  - `#FFFFFF` — bone (BRIGHTEST element, pure white).
  - `#E6E9F0` — bone shadow / under-edge for roundness.
  - `#15161C` — body "flesh" (near-black, the value floor + the dark behind
    the eye sockets).
  - `#3A3D47` — keyline / soft rim so white bone reads on a bright sky.
- **Distinctness:** the ONLY pure white-on-black, theme-free skeleton in the
  set; vs. the original it is far brighter and higher-contrast (true white, not
  ivory; near-black, not navy). Differs from #2 (no paint/color), #3 (no glow),
  #4 (no gear), #5 (no gold).
- **Day + night read:** white bone pops hard on night sky; on bright day the
  `#3A3D47` keyline + near-black body keep the silhouette from washing out.

---

## 2. MARIGOLD CALAVERA — Sugar-Skull Día de Muertos  `skin_skeleton` (design_2)

The colourful, festive opposite of #1: a painted sugar-skull bird, ivory bone
decorated with vivid floral calavera patterns and a marigold flower-crown. This
is where the original's "Day-of-the-Dead-ish" hint goes LOUD and joyful instead
of muted.

- **Hero silhouette / tell:** a **flower-crowned painted skull** — the crown is
  broken upward past the head by a **ring of marigold/magenta petals**, and the
  skull face carries **bright cyan-rimmed eye sockets** and a **magenta heart
  on the forehead**. The petal-crown + colour-rimmed sockets is the 40px read.
- **Bone layout + themed objects:**
  - Skull: warm ivory cranium; **eye sockets ringed with cyan petal-loops**;
    **magenta heart/flower glyph on the forehead**; a **marigold bloom at the
    chin/nose**; a wide **toothy grin with painted color gaps**.
  - Crown: **arc of orange-marigold + magenta petals** rising past the crown.
  - Ribs: ivory rib-arcs with **tiny cyan dot-and-swirl accents** on alternate
    ribs (kept chunky, 2px+).
  - Spine: vertebra column dotted with small marigold beads.
  - Wing: ivory finger-bones tipped with **small petal accents** at the wrist.
  - Legs: ivory leg-bones with a **single marigold anklet bloom** each.
- **Palette:**
  - `#FBF3DE` — bone (brightest base, warm ivory).
  - `#FF8A1E` — marigold orange (THEME / crown).
  - `#FF2E88` — calavera magenta (forehead heart + accents).
  - `#16C8D8` — cyan socket-rims + swirls.
  - `#221826` — dark body behind so the bone + colors pop.
- **Distinctness:** the only multi-colour PAINTED skeleton; festive, warm,
  decorative. Vs. original it adds saturated marigold/cyan/magenta where the
  original was flat ivory-on-navy. Differs from #1 (white, plain), #3 (eerie
  glow), #4 (pirate), #5 (gold/lich).
- **Day + night read:** the dark `#221826` body frames the bright ivory bone on
  day sky; on night sky the marigold + magenta + cyan are saturated enough to
  carry. Colors sit ON the bone, so the skeleton read never depends on them.

Sources reference: calavera color symbolism (marigold/cyan/magenta, floral
socket rings, forehead flower).

---

## 3. WISP — Spectral Ghost-Fire Skeleton  `skin_skeleton` (design_3) [showpiece]

The eerie, glowing one — semi-transparent ghost-green bones wreathed in an
additive aura, with twin flame-pips burning in the eye sockets. This is the
spectacle pick of the set, the one that looks like a flex at night.

- **Hero silhouette / tell:** a **glowing green spectral skull** with **two
  bright flame-pip eyes** and a **soft additive halo** bleeding off the bones;
  the body fades toward transparent at the edges (wispy tail). The glowing
  socket-flames + aura is the unmistakable 40px tell.
- **Bone layout + themed objects:**
  - Skull: pale eerie-green cranium, **hollow sockets each holding a bright
    cyan-green flame pip** (small additive bloom).
  - Aura: a **soft additive green glow** rendered behind/around the whole
    bone-set; brightest at the skull and rib core.
  - Ribs: glowing rib-arcs with the lower body **dissolving into 2–3 wispy
    tendrils** instead of solid legs-flesh.
  - Spine: a luminous vertebra line, brightest near the skull.
  - Wing: finger-bones that **trail faint glow streaks** on the flap poses.
  - Legs: thin glowing leg-bones fading at the feet into wisp tendrils.
- **Palette:**
  - `#C9FFE3` — bone core highlight (BRIGHTEST, near-white-green).
  - `#54F0A0` — spectral green bone body (THEME).
  - `#19C8A6` — aura mid-glow (additive).
  - `#0B2A24` — dark translucent "flesh" base behind bones.
  - glow note: **additive bloom** layered under bone for the halo + socket
    flames; bone edges 2px solid so they survive even where the glow is faint.
- **Distinctness:** the only glowing / semi-transparent / aura'd concept;
  ethereal, cold, magical. Vs. original it is luminous instead of muted-flat.
  Differs from #1 (solid white, no glow), #2 (warm paint), #4 (pirate gear),
  #5 (gold). Green keeps it distinct from #5's lich (which is gold/violet).
- **Day + night read:** dazzles on night sky (additive glow blooms on dark).
  On bright day, the solid 2px `#19C8A6`→`#54F0A0` bone edges and the dark
  `#0B2A24` core keep the skeleton legible even as the glow flattens out.

---

## 4. DEADMAN'S FLAG — Pirate Jolly-Roger Skeleton  `skin_skeleton` (design_4)

The characterful, funny one — a swashbuckling skeleton in a red bandana with an
eyepatch, a gold hoop earring, and a cutlass slung across the back, with a
crossbones motif. Bone stays the bright base; pirate gear is the strong themed
layer.

- **Hero silhouette / tell:** a **bandana'd skull with an eyepatch** and a
  **cutlass crossing the back**; one socket is a black eyepatch, the other a
  hollow bone socket. Bandana-knot past the crown + back-blade is the 40px
  read.
- **Bone layout + themed objects:**
  - Head: ivory skull; **red bandana wrapping the cranium with a knot-tail
    flicking past the crown**; **black eyepatch + strap over one socket**, the
    other socket hollow; **gold hoop earring** at the jaw; **bone grin**.
  - Back: a **cutlass (curved blade + crossguard) slung diagonally across the
    back**, breaking the outline; a small **crossed-bone (Jolly Roger) motif**
    on the chest below the sternum.
  - Ribs: bright bone rib-arcs.
  - Spine: vertebra column.
  - Wing: bone finger-bones; wrist wrapped with a **scrap of bandana-red cloth**
    so the wing reads pirate too.
  - Legs: bone legs; one foot a **bone peg-leg stub** for character.
- **Palette:**
  - `#F4EFE0` — bone (BRIGHTEST base, warm white).
  - `#C8202B` — bandana / cloth red (THEME).
  - `#1A1410` — body + eyepatch black.
  - `#E8B23A` — gold earring + cutlass guard accent.
  - `#B9C0C9` — steel cutlass blade.
- **Distinctness:** the only GEAR-driven skeleton (cloth + blade + props),
  warm and comedic. Vs. original it's bright bone + bold red, not muted ivory.
  Differs from #1 (plain), #2 (paint), #3 (glow), #5 (gold/lich) — its red
  bandana + steel keep its palette unique.
- **Day + night read:** bright bone + dark `#1A1410` body and eyepatch hold the
  silhouette on day sky; the saturated red bandana and gold earring give it
  punch on night sky. Bone is the value anchor regardless.

Sources reference: classic Jolly Roger iconography — eyepatch, bandana, gold
hoop earring, crossbones, cutlass.

---

## 5. AUREX — Cursed Gold-Lich Skeleton  `skin_skeleton` (design_5) [showpiece]

The premium, sinister one — a gilded cursed-treasure skeleton crossed with a
lich: **gold bones** dripping with menace, a **dark tattered mantle** behind
the shoulders, and **violet rune-fire burning in the eye sockets**. The
high-tier flex of the set, distinct from #3's green ghost by being gold +
violet and solid (no transparency).

- **Hero silhouette / tell:** a **golden skull with violet glowing sockets**
  framed by a **dark hood/mantle** that breaks the outline behind the head and
  shoulders. Gold bone + violet rune-eyes + dark mantle is the 40px read.
- **Bone layout + themed objects:**
  - Head: **gilded gold skull**; **eye sockets filled with violet rune-fire**
    (additive bloom + 1–2 tiny rune glyphs); a small **gold crown-band or
    coin** across the brow; gold-tooth grin.
  - Mantle: a **dark tattered hood/collar** rising past the crown and draping
    behind the shoulders — the lich silhouette layer.
  - Ribs: **gold rib-arcs** with a faint violet inner glow between them.
  - Spine: gold vertebra column.
  - Back/wing: gold finger-bones; faint **violet rune-glow** trailing the wing
    on flap poses.
  - Legs: gold leg-bones; **a couple of gold coins / a small treasure clink**
    at the feet for the cursed-hoard note.
- **Palette:**
  - `#FFE27A` — gold bone highlight (BRIGHTEST element).
  - `#E0A21E` — gold bone body (THEME metal).
  - `#7A4DE0` → `#B388FF` — violet rune-fire socket glow (additive).
  - `#16121F` — dark mantle / body (deep void-violet-black).
- **Distinctness:** the only METALLIC / lich concept — gold bone + violet
  necromantic glow + dark mantle. Vs. original it's gilded and ominous, not
  muted ivory. Differs from #1 (white), #2 (warm paint), #3 (green ghost — this
  is gold/violet and solid, not transparent), #4 (pirate steel/red).
- **Day + night read:** warm gold bone sits brightly against the dark mantle
  and `#16121F` body on a day sky; on night sky the gold reads as luxe and the
  violet rune-eyes + glow blaze. Mantle gives a dark silhouette anchor in both.

---

## Ranking & picks

1. **BONEWHITE (#1)** — the must-have. The single clearest fix for the muted
   original and the "default skeleton done right"; ship this first.
2. **MARIGOLD CALAVERA (#2)** — strongest character/colour identity; festive,
   recognizable, mass-appeal.
3. **WISP (#3)** — **best legendary-tier showpiece** (additive glow + flame
   sockets + wispy dissolve); the night-sky flex.
4. **DEADMAN'S FLAG (#4)** — most fun/characterful; gear read is buildable and
   instantly legible.
5. **AUREX (#5)** — the premium second showpiece; gold + violet lich, distinct
   from #3's green ghost.

**Spread check:** plain white (#1), painted multicolor (#2), green glow/ghost
(#3), pirate gear/red (#4), gold/violet lich (#5) — five clearly different
directions, all different from the muted navy/ivory original, all buildable
from procedural polys/arcs/lines + additive bloom on the 4-frame macaw.
**Two showpieces (#3, #5) carry glow; the other three are solid-bone reads.**

---

## Sources

- [Día de los Muertos skull colors — meaning](https://www.12news.com/article/life/heres-what-the-colors-of-the-dia-de-los-muertos-skulls-mean/75-342391928)
- [Traditional Calavera floral & marigold design](https://cults3d.com/en/3d-model/art/traditional-calavera-skull-intricate-floral-marigold-design)
- [Skull Day of the Dead calavera colour palette — ColorsWall](https://colorswall.com/palette/9011)
- [Jolly Roger — Wikipedia](https://en.wikipedia.org/wiki/Jolly_Roger)
- [Pirate skull / Jolly Roger iconography — bandana, eyepatch, earring, crossbones, cutlass (Alamy)](https://www.alamy.com/pirate-skull-with-crossbones-icons-jolly-roger-pirate-flag-symbol-of-skeleton-wearing-hat-eyepatch-bandana-and-earring-with-crossed-sword-and-knife-image404671960.html)
- [Lich design — glowing eye sockets, dark mantle (TV Tropes: Glowing Eyelights of Undeath)](https://tvtropes.org/pmwiki/pmwiki.php/Main/GlowingEyelightsOfUndeath)
- [Lich lore — skeletal, dark robes, glowing-socket energy (D&D Lore Wiki)](https://dungeonsdragons.fandom.com/wiki/Lich)
- [Spectral/glowing skeleton aura art reference (Dreamstime)](https://www.dreamstime.com/illustration/glowing-skeleton.html)
