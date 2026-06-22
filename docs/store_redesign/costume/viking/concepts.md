# Viking Costume Redesign — Pip the Macaw — 5 Concept Brief

**Goal:** Replace the weak current viking (horned iron helmet + a small braided
beard on an otherwise-scarlet macaw) with skins that read as VIKING
UNMISTAKABLY at ~40px in motion, by **layering multiple Viking objects all over
the bird** — head + back + body + limbs. "All over" is the point: every concept
stacks a helmet + a huge braided beard + a fur mantle + a back-slung shield or
weapon + a belt/bracers so the silhouette breaks the bird's outline from several
directions. A helmet alone is what we're replacing.

**Build target:** procedural pygame draw (polygons, circles, lines, ellipses)
layered over the existing 4-frame macaw, like the KFC / ghost / hat variants and
the current `_paint_viking` in `game/store_skins.py`. Signature objects push
**up past the crown** (horns / wings / crest) and **out past the back/body**
(shield boss, axe head, fur ruff) so they survive shrinking. No PNG sprites.
Body recolors (frost-pale, fur-brown) are available via the palette system.

**Base read rule:** at 40px the player must clock TWO tells instantly — almost
always (1) a **big helmet with something breaking past the crown** (horns,
wings, a spangenhelm dome + nasal) and (2) a **round shield or axe crossing the
back/body**. The huge braided beard with metal beard-rings is the third
near-universal tell. Everything else fills the silhouette.

Concepts are numbered in recommended build priority (design_1 … design_5).

---

## 1. STORMBEARD — Classic Raider Berserker  `skin_viking`

The definitive, can't-miss Viking. If only one ships, it's this — the iconic
horned raider, shield on the back, axe in hand, drowning in beard. Direct fix
for the weak original: replaces the "helmet + tiny beard" with a head-to-toe
raider kit.

- **Silhouette / hero shape:** a **horn-crowned, beard-heavy bird** with **two
  bold curved horns sweeping up-and-out past the crown** and a **round wooden
  shield slung across the back** breaking the outline behind the body — the
  horn-pair + back-disc is the single strongest "Viking" read at 40px.
- **Layered objects & placement:**
  - Head: **iron spangenhelm dome** (riveted half-dome) with a short **nasal bar**
    down the brow, and **two big curved horns** rising past the crown.
  - Face: **huge braided beard** ballooning below the beak to the chest, split
    into 2–3 fat braids with **two gold beard-rings** clamping the ends.
  - Shoulders: **fur shoulder mantle** — a thick ruff of triangular fur tufts
    ringing the neck/shoulders, breaking the upper outline.
  - Back: **round wooden shield** behind the body — iron **boss** dome center,
    iron **rim**, planked-wood radial lines, painted in a bright wedge.
  - Hand/wing: a **bearded axe** (hooked single-blade head) held out past one
    wing, haft angled up.
  - Body/legs: **studded leather belt** with a square buckle; **fur boot cuffs**.
- **Palette:** `#7B8794` (iron helm), `#5A4632` (fur mantle + boots),
  `#3A2A1B` (braided beard, cool-dark so it separates from the scarlet body),
  `#C0392B` (shield-paint wedge), `#E3B23C` (gold beard-rings + boss + buckle glint).
- **Distinct + memorable:** the archetype done right — horns up, shield behind,
  axe out, beard everywhere. Reads "VIKING" before the player thinks. Safest,
  broadest appeal; the one that fixes the original brief directly.

---

## 2. JARL GULLHELM — The Golden King-Jarl  `skin_viking_jarl`

The rich, premium-feeling ruler tier. Inverts #1 from rust-iron grit to **gold
and royal fur** — the warlord who hands out arm-rings, not the one who swings the
axe. Reads as the "elite / late-game" Viking.

- **Silhouette / hero shape:** a **gold-helmed bird wrapped in a deep fur cloak**
  whose collar flares **wide past both shoulders**, topped by a **gilded crested
  helm** (low fin-comb running front-to-back over the crown) — the wide fur
  collar + gold crest is a silhouette no other concept shares.
- **Layered objects & placement:**
  - Head: **gilded spangenhelm** with a **low gold crest-comb** over the crown
    and an engraved brow band (rune-dot etching).
  - Face: **broad braided beard**, lighter/blonder than #1, with **three gold
    beard-rings** stacked down one braid.
  - Shoulders/back: **luxurious fur cloak** — a deep wolf/bear ruff collar
    flaring past both shoulders, draping down the back as a furred cape edge.
  - Body: **studded wide belt** with an ornate **gold buckle plate**; a
    **drinking horn** with gold-banded rim hanging from the belt at the hip.
  - Wings/legs: **gold arm-rings (torcs)** stacked at the wing-root, a matching
    **ankle ring**.
  - Chest: a small **valknut** (three interlocking triangles) etched as a brooch.
- **Palette:** `#E3B23C` (gold helm/crest/rings), `#A8842A` (gold shadow),
  `#6B5234` (fur cloak), `#3A2A1B` (beard + leather belt), `#F4E3B0` (gold/horn highlight).
- **Distinct + memorable:** the "wealthy warlord." Wide fur collar + gold crest +
  drinking horn + stacked arm-rings make it the most opulent silhouette of the
  set. Strong premium / late-game appeal; clean recolor-plus-props cousin to #1.

---

## 3. SHIELDMAIDEN FREYA — Braided Warrior-Maiden  `skin_viking_maiden`

The shieldmaiden / kunoichi-equivalent. Visually opposite the bulky raiders:
sleeker helm, the read carried by **long flowing battle-braids** and a
**shield held forward**. Gives the set a clearly different body language.

- **Silhouette / hero shape:** a bird framed by **two long thick braids
  streaming back past the tail** (these animate with the flap — the most dynamic
  element) under a **simple iron circlet-helm**, with a **round shield held up
  out front past one wing** (face-on disc, boss center) — braids-back +
  shield-front is a unique left/right break.
- **Layered objects & placement:**
  - Head: **light iron circlet / browband helm** (no horns — a small **single
    winglet or feather tuft** at one side), leaving the face open.
  - Hair: **two long battle-braids** with **metal braid-rings**, trailing back
    past the tail and flicking with the flap.
  - Shoulders: **fur-trimmed leather pauldron** over one shoulder.
  - Wing/front: **round shield held up** out past the wing — bright boss,
    iron rim, a painted **rune or radial chevron** motif on the face.
  - Body: **leather corset-tunic** with cross-lacing down the front; **studded belt**.
  - Wing/leg: **leather bracers/vambraces** with strap lines; a **short seax
    knife** at the belt.
- **Palette:** `#8A9099` (iron circlet + shield rim), `#6B4A2E` (leather tunic +
  pauldron), `#C9A24B` (braid-rings + boss + buckle), `#2C7A6B` (shield-paint teal,
  cool pop vs the warm raiders), `#E8C9A0` (skin/highlight + braid sheen).
- **Distinct + memorable:** the only "agile" build — flowing braids + forward
  shield + corset read as a fast warrior, not a bruiser. Teal shield + open face
  give the store visible variety against the all-brown raiders.

---

## 4. FROSTREAVER — Ice-Raider of the North  `skin_viking_frost`

The frost/ice Viking — a **pale-blue body recolor** turns Pip into a
rime-covered northern raider. Same raider kit as #1 but in a cold palette with
icy accents, so it reads instantly as the "winter" variant. The recolor makes it
the most distinct-at-a-glance member of the set.

- **Silhouette / hero shape:** a **frost-pale bird** under a **frost-rimed horned
  helm** with a **round shield of pale blue ice-wood on the back** and **icicle
  spikes hanging off the beard and shield rim** breaking the lower outline — the
  cold body + jagged ice edges is unmistakable next to the warm raiders.
- **Layered objects & placement:**
  - Body recolor: **pale frost-blue** plumage (replacing scarlet) with white
    frost-dusting on the wing edges.
  - Head: **steel-blue horned helm** (spangenhelm dome + nasal), horns rimed with
    **white frost tips**, a few **icicle drips** off the brim.
  - Face: **frosted braided beard** — pale grey-blue braids with **icicle ends**
    instead of beard-rings, glittering with ice flecks.
  - Shoulders: **white winter-wolf fur mantle** (snowy ruff) ringing the neck.
  - Back: **round shield**, pale ice-blue planks, iron boss, **jagged frost
    crystals** growing off the rim.
  - Hand/wing: a **frost-bladed bearded axe** (pale steel head with a faint
    cold-blue rim glint); **fur boot cuffs**.
- **Palette:** `#BFE0F2` (frost-pale body), `#7FA8C9` (cold helm + shield wood),
  `#3E5B72` (cold shadow + beard), `#F2FAFF` (icicles + frost glint + fur),
  `#C7E9FF` (pale ice highlight). Optional faint cold-blue rim-glow on the axe.
- **Distinct + memorable:** the body recolor makes it pop hardest of the
  standard tier — a literal frost-raider. Icicle-tipped beard + frost-spiked
  shield are geometry no other concept has. Reads great against a bright-day sky.

---

## 5. ODINWING — Allfather Valkyrie Helm  `skin_viking_odin`  (LEGENDARY-tier showpiece)

The spectacle build — the mythic Odin / Valkyrie winged-helm. Leans on **animated
gold glow + winged crest** baked into the art, the dragon/phoenix-style flex.
Pip looks like a war-god ascending. Anchors the legendary tier.

- **Silhouette / hero shape:** a bird crowned by a **pair of great golden wings
  sweeping up-and-out past the crown** off a glowing winged helm, with a **raven
  perched/launching off one shoulder** and a **softly glowing valknut/runic halo**
  — the winged helm + wide gold span is the boldest, most unmistakable silhouette
  in the set, and the only light-emitting one.
- **Layered objects & placement:**
  - Head: **golden winged helm** — ornate dome + nasal, with **two large feathered
    wings** flaring up past the crown (animate a soft gold shimmer along the
    feather edges with the flap).
  - Face: **regal braided beard** with **gold beard-rings**, faintly lit from the
    helm glow.
  - Shoulders/back: **deep fur+cape mantle** with a **glowing valknut brooch**
    (three interlocking triangles, pulsing soft gold) at the throat.
  - Shoulder: a small **raven (Huginn/Muninn)** perched at the wing-root, wings
    half-open as if about to launch (silhouette accent, not detail-dependent).
  - Hand/wing: **Gungnir** — a slender **glowing spear** held diagonally past the
    wing, tip catching a hot gold-white glint, crossing the body like #1's axe
    but luminous.
  - Aura: a faint **runic ring halo** of drifting gold rune-marks orbiting the
    head (particle shimmer); **gold arm-rings** at the wing-root.
- **Palette:** `#E9C24A` (gold helm/wings/spear — animated shimmer),
  `#B8862B` (gold shadow), `#4A3A6B` (royal-violet fur cape, regal contrast),
  `#FFF4C2` (hot glow core / spear tip / valknut pulse), `#2A2030` (raven + beard shadow).
- **Distinct + memorable:** the doubled gold wings + glowing spear + raven +
  pulsing valknut make it the "war-god" — pure flex. Animated gold glow and the
  winged crest justify a **legendary** tier; it's the showpiece silhouette of the
  whole Viking set.

---

## Ranking rationale & build notes

1. **STORMBEARD (#1)** — ship first. The canonical "obvious Viking"; lowest risk,
   broadest appeal, the one that fixes the original brief directly. Horns up +
   back shield + axe + giant beard = bulletproof 40px read.
2. **JARL GULLHELM (#2)** — strongest *premium* read (gold crest + wide fur
   collar + drinking horn + arm-rings). Clean gold recolor-plus-props relationship
   to #1; the "wealthy warlord" tier.
3. **SHIELDMAIDEN FREYA (#3)** — the essential "agile/different body language"
   contrast so the set isn't all bulky bruisers. Flowing braids + forward shield
   + teal accent give the store visible variety.
4. **FROSTREAVER (#4)** — the body-recolor outlier; pops hardest at a glance
   (frost-pale plumage) and adds a "winter" theme with unique icicle geometry.
5. **ODINWING (#5)** — best **legendary showpiece**: winged gold helm + glowing
   spear + raven + pulsing valknut is the most spectacular idea here and the
   animated gold glow earns the flex tier.

**Tier mix:** #1–#4 standard unlockables; **#5 legendary** (animated gold glow /
shimmer / winged crest baked into the art, dragon/phoenix-style).

**Distinctness check (all 5 differ in silhouette-breaker):** #1 = horn-pair +
back round-shield + axe; #2 = wide gold crest + flaring fur cloak collar + horn
at hip; #3 = long trailing braids + forward-held shield + open face; #4 =
frost-pale body recolor + icicle-spiked beard/shield; #5 = great gold winged
helm + glowing spear + raven + halo. No two share a hero shape, and #4 is the
only body recolor, #5 the only luminous build.

**Shared build kit a graphics-designer can reuse across all 5:** a helmet dome
with a brow/nasal band, a big braided beard with metal rings, a fur shoulder
mantle/ruff, a round shield (planks + iron boss + rim), a studded belt, and
forearm/leg bracers. Each concept swaps the hero element (horn-pair vs gold
crest vs braids vs ice vs wings), the weapon (axe / horn / seax / frost-axe /
spear), and the palette on top of that kit.

---

### Sources
- [Viking Age arms and armour (Wikipedia)](https://en.wikipedia.org/wiki/Viking_Age_arms_and_armour)
- [Did Viking helmets really have horns ... or wings? (History Skills)](https://www.historyskills.com/classroom/year-8/viking-helmets/)
- [Viking horns and shields: functional reality and popular myth (Todomedieval)](https://todomedieval.com/en/blogs/tienda-medieval-blog/cuernos-y-escudos-vikingos-entre-la-realidad-funcional-y-el-mito-popular)
- [Authentic Viking Armory: axes, shields, helmets (Tales of Valhalla)](https://talesofvalhalla.com/blogs/tales-of-valhalla-norse-mythology/authentic-viking-armory-viking-axes-shields-and-helmets)
- [Viking Costume for Halloween: what farmers and kings wore (Odin's Treasures)](https://odinstreasures.com/blogs/norse-tales/viking-costume-for-halloween-what-farmers-and-kings-wore-in-the-viking-age)
- [What Jewelry Did the Vikings Wear? — arm rings, torcs (Norse Spirit)](https://norsespirit.com/blogs/norse_viking_blog/viking-jewelry-facts-what-jewelry-did-the-vikings-wear)
- [Valknut Meaning: the most powerful symbol in Norse mythology (VarVar Jewelry)](https://varvar.jewelry/blogs/mythology/valknut-meaning-the-most-powerful-symbol-in-norse-mythology)
- [Viking Costume: A Complete Guide to Dressing Like a Norse Warrior (Creed Leather)](https://creedleather.com/blogs/costume-guide/viking-costume-a-complete-guide-to-dressing-like-a-norse-warrior)
- [25 Viking Braids for Women / Shieldmaiden hair (Snazzy Lair)](https://snazzylair.com/viking-braids-for-women/)
- [Valkyrie (World History Encyclopedia)](https://www.worldhistory.org/Valkyrie/)
- [Huginn and Muninn: Odin's ravens (NorseMythologist)](https://norsemythologist.com/huginn-and-muninn/)
- [The Myth Behind Viking Helmets with Wings (Viking Style)](https://viking.style/the-myth-behind-viking-helmets-with-wings-fact-or-fiction/)
