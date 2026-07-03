# ZOMBIE PARROT — Costume Redesign Concepts

Brief: make the zombie parrot **unmistakably undead** at 40px. The current
skin (green body + tiny stitches) reads "friendly frog-bird." Every concept
below layers **3+ overlapping zombie tells across head + body + wing + limbs**
so the horror identity survives being shrunk and put in motion.

Design constraints honored throughout:
- Procedural pygame draw calls only (polygons, rects, lines, circles,
  small glow blits) — no PNG texture, no per-pixel raster thinking.
- Tells are **big, high-contrast blocks**, not fine detail — a wound is a
  filled dark rect, a rib is a 2–3px line, an eye-glow is a circle + halo.
- Value structure reads against both bright-day and night skies (dark
  outline + mid corpse-tone body + one hot accent).
- Maps to the standard 4 wing poses; the flap animates each concept's tell
  (dangling flesh sway, ooze drip, jaw chatter, etc.).

Skin id stays `skin_zombie` / display "ZOMBIE" when a winner is wired.

Archetype spread (all 5 distinct): **fresh-turned**, **ancient rot**,
**voodoo**, **lab specimen**, **bloated gas-bag**.

Ranking is by strength of the 40px zombie read (1 = strongest).

---

## 1. ROADKILL FRESH-TURNED — *(fresh-turned)*  `skin_zombie`
**RANK 1 — strongest, recommended default**

**Hero silhouette.** A parrot that looks *recently* mangled: normal bird
shape but visibly split open down one side, one wing hanging a beat lower
than the other, a bright red gash slashing the chest and a single hot-red
pinprick eye against a dead-white eye ring. From 3 feet it reads "this bird
died five minutes ago and got back up."

**Zombie elements (draw calls).**
- **Chest gash (wound):** one filled dark-red `polygon` lens/almond shape
  on the belly, with a thin brighter-red inner `polygon` inset — the "wet"
  center. 2px near-black outline.
- **Exposed ribs (bones):** 3 short bone-white `line` segments (2px) fanning
  out of the top of the gash, arced to follow the belly curve.
- **Glowing eye + dead eye ring:** small hot-red `circle` + one additive
  glow blit for the pupil, sitting inside an oversized off-white `circle`
  ring (the classic milky zombie eye). The head-tilt keeps this the anchor.
- **Torn wing tip (ragged flesh):** the trailing wing edge is a jagged
  `polygon` (saw-tooth of 3 notches) instead of a smooth curve, in a
  darker bruise tone — one flap pose drops it lower for a "broken hinge."
- **Blood drip (ooze):** 1–2 tiny dark-red `ellipse` drips hanging off the
  gash; lowest drip elongates on the down-flap.

**How the flap reads.** The lower/torn wing lags and swings — a broken limb
flopping rather than a clean beat. Sells "damaged" motion.

**Palette.** body `#6E8A5E` (sick green-gray) · shadow/outline `#243021` ·
gash `#7A1414` / hot center `#C7302B` · bone `#E9E4D0` · eye-glow `#FF3A2E`.

**Distinctness.** The only *bright-red, wet, recently-wounded* concept —
saturated fresh blood and intact-but-broken body vs. the dry/desaturated rot
of the others.

---

## 2. ANCIENT CRYPT ROT — *(ancient rot)*  `skin_zombie_crypt`
**RANK 2**

**Hero silhouette.** A gaunt, dried-out husk of a bird — sunken, skeletal,
mummified. Body is desaturated bone-gray, ribs show as a hard ladder down
the flank, the spine erupts in a row of knobby bumps along the back, and
BOTH eyes are hollow black sockets with faint green pinlights deep inside.
Reads as "grave-dug, centuries dead."

**Zombie elements (draw calls).**
- **Rib ladder (bones):** 4–5 parallel bone `line` segments (2px) marching
  down the exposed flank, shortening toward the tail — the single loudest
  40px tell. Drawn over a darkened `polygon` "cavity" patch so they pop.
- **Spine bumps (protruding spine):** a row of 4 small overlapping
  bone-gray `circle`s along the top back edge, each with a dark underside
  arc for shadow — a knobby vertebral ridge.
- **Hollow sockets (missing eyes):** two near-black `circle`s for empty
  sockets, each with a tiny dim-green `circle` + soft glow floating inside
  ("something's still in there"). No white eye ring — sunken, not wet.
- **Cracked dry beak / jaw (ragged):** a thin dark `line` splitting the
  lower beak, one chip removed as a small notch `polygon`.
- **Dust/mottle (rotting palette):** 5–8 scattered darker `ellipse` blotches
  across the body for patchy decay — flat, dry, no shine.

**How the flap reads.** Stiff, brittle, low-amplitude beats — the spine
bumps and rib ladder stay rigid; a mummy that barely holds together.

**Palette.** body `#9A9483` (dry bone-gray) · deep shadow `#2A2822` ·
cavity `#4B4437` · bone highlight `#D8D2BE` · socket-glow `#5FBF6A`.

**Distinctness.** The *dry, skeletal, desaturated* one — no blood, no ooze,
no bright color; carried entirely by bone geometry (ribs + spine + sockets).

---

## 3. VOODOO HEX BIRD — *(voodoo)*  `skin_zombie_voodoo`
**RANK 3 — legendary-leaning showpiece**

**Hero silhouette.** A cursed, stitched-together conjure-bird: coarse
cross-stitches lashing the head, a burlap-sack rag over one shoulder, eyes
sewn shut on one side while the other blazes an unnatural purple, and a
faint sickly-green hex glow rimming the whole body. Reads as "raised by a
witch doctor," not simply diseased.

**Zombie elements (draw calls).**
- **Big cross-stitches (ragged repair):** 3–4 bold X's along the head/neck
  seam, each an `X` of two thick dark `line`s with tiny knot `circle`s —
  much heavier than the current timid stitches (this was the old skin's
  failure).
- **Sewn-shut eye (missing eye):** one eye is a horizontal dark `line`
  crossed by 3 short vertical stitch `line`s; the *other* eye is a hot
  purple `circle` + glow — asymmetry is the horror.
- **Burlap rag (hanging flesh/cloth):** a torn tan `polygon` draped over the
  shoulder with a saw-tooth lower hem `polygon` and 2 vertical fray `line`s.
- **Hex aura (legendary glow):** a soft additive green `circle` halo blitted
  behind the whole sprite, gently pulsing over the 4 poses — the "cursed"
  shimmer that justifies a premium tier.
- **Pin / needle (wound accent):** one small bone `line` with a bead `circle`
  head stuck through the body like a voodoo-doll pin.

**How the flap reads.** The burlap rag sways and the hex aura pulses
brighter on the up-flap — the curse "breathing." Ritual, not roadkill.

**Palette.** body `#5C6E57` (mossy corpse) · outline `#20261E` ·
burlap `#B79A6B` · stitch `#111` · hex-glow `#7CFF8A` · cursed eye `#B24BFF`.

**Distinctness.** The only *supernatural/ritual* zombie — stitched, hexed,
purple-eyed with a green aura; horror comes from sorcery + repair, not gore.

---

## 4. LAB SPECIMEN #7 — *(lab specimen)*  `skin_zombie_lab`
**RANK 4**

**Hero silhouette.** A reanimated experiment: the top of the skull is open
under a small glass dome showing a pink exposed brain, a bolt/electrode
juts from the neck with an arcing spark, and toxic-yellow-green fluid seeps
from a sutured seam down the chest. Reads as "science did this."

**Zombie elements (draw calls).**
- **Exposed brain (open skull):** the crown is a light dome `arc`/`polygon`
  filled with a pink brain — two interlocking pink `polygon` lobes plus a
  darker central `line` fissure. A thin cyan `arc` over it = the glass dome.
- **Neck bolt + spark (wound/tech):** a gray bolt `rect` + `circle` cap on
  the neck; one flap pose adds a 2–3 segment jagged electric-blue `line`
  arc (spark) between bolt and head.
- **Sutured seam (stitched wound):** a vertical dark `line` down the chest
  crossed by short rung `line`s (surgical staples) — cleaner and more
  clinical than the voodoo cross-stitch.
- **Toxic seep (ooze):** yellow-green `ellipse` drips leaking from the seam,
  the lowest stretching on the down-flap; faint glow blit for radioactivity.
- **Number tag (identity):** a tiny pale `rect` band on the leg with a dark
  "7" glyph — the specimen label. (Small; supports the read, not the anchor.)

**How the flap reads.** The spark arcs on alternate poses (a twitch of
reanimation) and the toxic drip elongates — Frankenstein pulse rather than
decay.

**Palette.** body `#7E9B86` (embalmed gray-green) · outline `#1E2723` ·
brain-pink `#E58AA0` / fissure `#9B4E63` · toxic ooze `#C6F53A` ·
bolt/dome `#AEB8BE` + spark `#4FE3FF`.

**Distinctness.** The only *sci-fi/reanimation* concept — glass-dome brain,
bolt, staples, glowing spark and toxic ooze; clinical horror, not natural rot.

---

## 5. BLOATED GAS-BAG — *(bloated)*  `skin_zombie_bloat`
**RANK 5**

**Hero silhouette.** A grotesquely swollen, over-round parrot — belly
ballooned taut and shiny, mottled with methane blisters, skin split along
the pressure seams to show dark gut, one tiny eye lost in the swelling.
Reads as "about to pop." A deliberately *different body shape* from the
other four.

**Zombie elements (draw calls).**
- **Bloated body (silhouette):** the base body `ellipse` is scaled ~1.25×
  wider/rounder with a lighter taut-skin highlight `arc` on top for the
  drum-tight sheen.
- **Blisters (festering):** 4–6 raised `circle`s of pale sickly yellow with
  a darker rim and a tiny white specular dot each — pressurized methane
  boils clustered on the belly.
- **Pressure splits (wounds):** 2 vertical dark `polygon` gashes where the
  skin has torn, showing a deep maroon `polygon` gut layer beneath — the
  bloat straining open.
- **Sunken tiny eye (asymmetry):** one normal dim eye, the other a barely
  visible dark `circle` half-swallowed by a swollen flesh `arc` — puffed
  shut.
- **Ooze drips (ooze):** thick greenish-brown `ellipse` drips oozing from
  the splits, sluggish and heavy on the down-flap.

**How the flap reads.** The bloated belly *jiggles* — a subtle vertical
squash-and-stretch of the body ellipse across poses, and blisters wobble.
Gross, heavy, gas-filled motion.

**Palette.** body `#8FA06A` (jaundiced green) · outline `#242B1B` ·
blister `#D8D66A` · split/gut `#5A1E22` · ooze `#6E7A35`.

**Distinctness.** The only concept that changes the **body shape** (fat and
round) — bloat + blisters + pressure-splits give a bulbous silhouette none
of the gaunt/normal-build others share.

---

## Ranking rationale (best 40px zombie read → weakest)

1. **ROADKILL FRESH-TURNED** — highest instant contrast: bright wet gash +
   ribs + hollow-ringed glowing eye on a normal-but-broken shape. Fastest
   "that's a zombie" at 40px and the safest default re-skin.
2. **ANCIENT CRYPT ROT** — the rib-ladder + spine-bumps + hollow sockets are
   pure bold geometry that shrinks beautifully; loses only for lacking a
   single hot accent color.
3. **VOODOO HEX BIRD** — most characterful and the natural **legendary /
   premium** pick thanks to the pulsing hex aura; slightly softer read than
   #1–2 because its horror is thematic (ritual) more than gory.
4. **LAB SPECIMEN #7** — very distinct and fun, but the brain-dome + bolt +
   staples + tag risk crowding at 40px; needs the tightest layout discipline.
5. **BLOATED GAS-BAG** — strong gag and unique silhouette, ranked last only
   because "swollen + gross" reads *sick* faster than it reads *undead*
   without the split-open gut carrying the zombie tell.

**Top pick:** #1 Roadkill Fresh-Turned.
**Best legendary showpiece:** #3 Voodoo Hex Bird (animated aura + asymmetric
sewn/blazing eyes).

---

### Sources / inspiration
- Zombie pixel-sprite shorthand — exposed bones, glaring/empty sockets,
  claw silhouette, green/gray/brown + purple-bruise palette:
  [CraftPix zombie sprites](https://craftpix.net/categorys/zombie-character-sprites/),
  [PixelArtGG zombie gallery](https://www.pixelartgg.com/gallery/zombie).
- Archetype split (voodoo / bloated-exploder / Romero fresh-turned):
  [TV Tropes — Our Zombies Are Different](https://tvtropes.org/pmwiki/pmwiki.php/Main/OurZombiesAreDifferent),
  [TV Tropes — Voodoo Zombie](https://tvtropes.org/pmwiki/pmwiki.php/Main/VoodooZombie),
  [Zombiepedia — Types of Zombies](https://zombie.fandom.com/wiki/Types_of_Zombies).
