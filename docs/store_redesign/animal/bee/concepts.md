# `skin_bee` redesign — 5 bug/insect concepts

Full from-scratch redesigns of the 400-coin `skin_bee` slot. The creature no
longer has to be a bee — each concept below is a distinct insect **order,
silhouette, and palette**, chosen so five sprites never blur together and none
falls back on the generic yellow-and-black cartoon bee.

**Canvas:** 64×84 SRCALPHA, procedural only. Body thorax centered near
`BCX=32,BCY=44`; head near `HCX=44,HCY=34`; antennae reach up to `CROWN_Y=24`.
Insect body axis runs upper-right (head) → center (thorax) → lower-left
(trailing abdomen). Wings mount off the thorax onto the existing 4-frame
parrot flap rig (up-sweep → mid → down-sweep → mid). Everything must read at
40px on both bright-day and night skies.

Ranked 1 (most premium) → 5.

---

## 1. AZUREWING — design_1
**Species / archetype:** Blue morpho butterfly (Lepidoptera) — the headline
iridescent showpiece.

**Hero silhouette:** A pair of huge, rounded, wall-to-wall wings that fill the
canvas — the body is almost hidden behind two great shimmering sails.

**Objects + placement:**
- **Head/antennae:** small dark bead head upper-right; two thin clubbed
  antennae curving up to `CROWN_Y`, tips flicked apart.
- **Body:** slim furred thorax + short tapering abdomen down the center axis,
  deliberately understated so the wings dominate.
- **Wings:** two broad overlapping rounded forewing+hindwing masses spanning
  the full 64px width. Each wing carries a hard value split — a bright
  structural-blue inner field and a near-black scalloped outer margin dotted
  with tiny white "eye" flecks. On the down-sweep the wing shows its full face
  (max blue); on the up-sweep it edges toward silhouette (the read-at-40px
  tell that it's flapping).
- **Legs:** three pairs of hair-thin legs tucked tight under the thorax, barely
  visible — correct but never busy.
- **Special FX (legendary-tier):** an iridescent gradient that shifts blue →
  cyan → violet across the wing per frame, plus a faint outer glow so the blue
  pops against a bright day sky and glows against night. A few drifting scale
  "sparkles" trail behind on the down-flap.

**Palette:**
- `#1B3A8F` Deep royal (wing base / value anchor)
- `#2F7BFF` Structural blue (main iridescent field)
- `#5FE1FF` Cyan highlight (shimmer edge)
- `#0B0E1A` Ink margin (scalloped outer border + head)
- `#EAF4FF` Scale-white (eye flecks + sparkle)

**Distinctness:** The only broad-winged, full-canvas iridescent flyer — pure
color drama and the widest wingspan of the set. Reads instantly as "butterfly,"
never as a bee; nothing else here is blue.

---

## 2. EMBERGLOW — design_2
**Species / archetype:** Firefly / lightning bug (Coleoptera, Lampyridae) — the
glowing-lantern showpiece, built to own the night sky.

**Hero silhouette:** A compact dark beetle body with a fat, rounded, self-lit
abdomen — a floating warm lantern with fluttering wings.

**Objects + placement:**
- **Head/antennae:** small dark head with a red-orange pronotal "shield" plate
  behind it (the firefly's signature); two short filiform antennae to `CROWN_Y`.
- **Body:** dark charcoal thorax; the abdomen (lower-left, trailing) is the
  swollen glowing lantern — the largest single shape by area.
- **Wings:** short semi-open brown-black elytra over the thorax, with a pair of
  smoky translucent hindwings fluttering fast behind — small blur wings, not a
  broad span, so the glow stays the hero.
- **Legs:** thin dark legs folded up under the thorax.
- **Special FX (legendary-tier):** the abdomen is a layered radial glow
  (white-hot core → amber → soft green-yellow halo) that **pulses in sync with
  the flap** — brightest on the down-beat. A soft bloom blit spills past the
  body outline; tiny sparks drift down on each pulse. Against day sky the
  lantern reads as a saturated amber bulb; against night it blooms like a lamp.

**Palette:**
- `#141013` Charcoal body (value anchor / silhouette)
- `#7A2E12` Ember-brown elytra
- `#FFB020` Amber glow mid
- `#FFF6C8` White-hot core
- `#C8FF6A` Bio-green halo (the "firefly" tell)

**Distinctness:** The only emissive concept — a pulsing light source rather
than reflective color. Unmistakable at 40px by glow alone, and the strongest
night-sky performer of the five.

---

## 3. IRONHORN — design_3
**Species / archetype:** Rhinoceros / Hercules beetle (Coleoptera,
Dynastinae) — the armored bruiser with a hero horn.

**Hero silhouette:** A stout oval tank of a body topped by one big upward-curved
horn — a bold, chunky, unmistakable profile even as a solid shadow.

**Objects + placement:**
- **Head/antennae:** small head upper-right dominated by a single large
  curved cephalic **horn** sweeping up past `CROWN_Y` (the 40px tell); tiny
  clubbed antennae beside it. A smaller thoracic horn can echo below the main
  one for the classic Hercules double-pincer look.
- **Body:** one broad domed oval thorax+elytra mass filling the center —
  glossy, with a hard specular highlight streak across the top to sell the
  hard-shell curve.
- **Wings:** the elytra split down the midline and **crack open** on the
  down-flap, fanning a pair of dark amber membranous hindwings out and back;
  they tuck closed on the up-flap. This makes the flap read as a beetle
  labouring into the air — heavy and characterful.
- **Legs:** three pairs of thick spurred legs gripping outward, chunky enough
  to read as beetle legs, not hairs.
- **Special FX:** a moving metallic sheen band (deep olive → gold) traveling
  across the dome; subtle rim light on the horn so it stays legible against
  both skies. Everyday premium, no full glow.

**Palette:**
- `#2A1A08` Dark chitin (outline / underside)
- `#4E3A12` Bronze-brown shell base
- `#8A6A1E` Warm brass mid
- `#D8B24A` Gold specular highlight
- `#1C120A` Horn shadow

**Distinctness:** The only horned, hard-shell "tank" silhouette — mass and a
single big appendage instead of wingspan or glow. Its flap is elytra cracking
open, unlike any winged flutter in the set.

---

## 4. GLINTWING — design_4
**Species / archetype:** Dragonfly (Odonata) — the jeweled quad-wing speedster.

**Hero silhouette:** A long slender needle-body held horizontal, with four
narrow glassy wings splayed in an X — an elongated cross shape, the opposite of
the round morpho.

**Objects + placement:**
- **Head/antennae:** oversized bulbous head that is almost entirely two huge
  **compound eyes** (the classic dragonfly tell), wrapping the front; antennae
  are negligible bristles.
- **Body:** very long, thin, segmented abdomen trailing far to the lower-left
  in banded jewel tones — the longest, thinnest body of the set.
- **Wings:** two pairs (fore + hind) of long, narrow, transparent membranes
  with a fine vein lattice and a colored `pterostigma` spot near each tip. The
  pairs beat in opposition on the flap rig — forewings up while hindwings down
  — reading as a fast shimmering blur.
- **Legs:** short bristled legs bunched under the thorax near the head.
- **Special FX:** wing membranes carry a faint oil-slick iridescence (teal →
  magenta) and a light motion-blur ghost on the fastest frames; the eyes get a
  small glossy catchlight. Premium but restrained versus the two showpieces.

**Palette:**
- `#0E5C4A` Deep emerald (body anchor)
- `#22C39A` Jewel-green segments
- `#B8FFF0` Glass-teal wing tint
- `#E85AD8` Magenta pterostigma / iridescent flash
- `#08201C` Vein + eye shadow

**Distinctness:** The only horizontal, elongated, four-wing silhouette and the
only design defined by giant compound eyes + needle abdomen. Cross-shape reads
"dragonfly" at a glance; can't be confused with the round or chunky concepts.

---

## 5. STINGREEL — design_5
**Species / archetype:** Giant hornet (Hymenoptera, Vespa) — the menacing,
premium re-imagining of the old bee slot.

**Hero silhouette:** A sharply **pinched-waist** body — big blocky head and
thorax up front, a hard gap, then a fat spindle abdomen tapering to a visible
stinger. Angular and aggressive where the old bee was round and cute.

**Objects + placement:**
- **Head/antennae:** broad angular orange head with two teardrop compound eyes
  and short blade-like mandibles; two elbowed antennae kinked up to `CROWN_Y`.
- **Body:** distinct three-part build — orange thorax, a **narrow wasp-waist
  pinch**, then a boldly banded abdomen ending in a sharp dark stinger tip
  (lower-left).
- **Wings:** two pairs of narrow smoky-amber hyaline wings, swept back and
  folding lengthwise along the body — they buzz in a tight fast arc on the flap
  rig rather than a broad sweep, selling speed and threat.
- **Legs:** long jointed legs trailing behind in flight, angular, not hairy.
- **Special FX:** crisp high-contrast banding and a hard specular line down the
  glossy abdomen; a faint motion-blur on the buzzing wings. No glow — its punch
  is the aggressive value contrast, which holds up on both skies.

**Palette:**
- `#12100C` Ink black (bands / stinger / value anchor)
- `#E8801A` Vespa orange (head + thorax)
- `#F6C63C` Warm amber band highlight
- `#6E4A10` Smoked wing tint
- `#FFE39A` Specular sheen

**Distinctness:** The only pinched-waist, stinger-tipped predator silhouette —
keeps a warm "wasp family" nod to the retired bee but is angular, threatening,
and anatomically a hornet, so it never reads as the round cartoon bee it
replaces.

---

## Ranking rationale

1. **AZUREWING** — biggest, most premium visual: full-canvas iridescent morpho
   wings. The clearest "wow, that's a skin" moment and the marquee pick.
2. **EMBERGLOW** — the legendary night-sky flex; a pulsing living lantern that
   no other skin in the store can match on a dark background.
3. **IRONHORN** — boldest solid silhouette; the horn + cracking-elytra flap
   make it instantly readable and give it a distinct "heavy" animation feel.
4. **GLINTWING** — elegant and jewel-toned, but a thin horizontal body is the
   hardest of the five to keep punchy at 40px, so it ranks below the three
   high-contrast leads.
5. **STINGREEL** — strong and characterful, ranked last only because it sits
   closest in spirit (warm wasp/bee family) to the slot it replaces; still a
   sharp, premium upgrade over the old cartoon bee.

**Best legendary showpiece:** EMBERGLOW (design_2) for its animated pulsing
glow; AZUREWING (design_1) is the co-legendary on pure color spectacle.

**Species/order spread (no duplicates):** Lepidoptera (morpho) · Coleoptera–
Lampyridae (firefly) · Coleoptera–Dynastinae (rhino beetle) · Odonata
(dragonfly) · Hymenoptera (hornet) — five orders/families, five silhouettes
(broad round · glowing lantern · horned tank · elongated cross · pinched
predator).

*Inspiration references: blue morpho & luna-moth structural color, jewel-beetle
iridescence, firefly bioluminescence, dragonfly compound-eye/quad-wing
identification, and hornet pinched-waist wing-fold anatomy.*
