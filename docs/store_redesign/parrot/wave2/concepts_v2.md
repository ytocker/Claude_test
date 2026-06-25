# PARROTS — Wave 2.1 replacement concepts (concepts_v2)

Replaces the four rejected wave-2 designs (GLACIER / KOI / BIOLUMEN /
STAINED-GLASS) with **2 epic + 2 legendary**. The 5th wave-2 slot — the SECRET
**CHROME MACAW** — is already approved and is NOT re-done here; everything below
is deliberately steered clear of chrome/mirror-metal/oil-slick.

Every skin stays recognisably **Pip the macaw in his signature aviator
sunglasses, just "ascended"** — an equippable cosmetic recolour of the player
bird, NOT a from-scratch ANIMALS-tab creature. Build path is the established
one: body = `dollar_parrot_ghost._build_parrot_with_palette` + a `_pal` palette
dict; signature = a `paint_fn` overlay (cockatoo-crest / PRISM model) **or** a
custom back-layer getter when a halo/aura/tail must paint BEHIND the body
(AURORA / viking-axe model). Wrapped by `store_skins._make_skin`; **never**
registered in `store_skins.BUILDERS`.

**North star — lives or dies at 40px in motion.** Every signature shape is
pushed up past the crown or out past the tail to break the egg silhouette; held
≥2px so it survives downscale; kept off near-black so it reads on the navy store
card; checked on BOTH day and night sky. Aviators always stay, tinted to suit.

**Tier rule (same escalation as wave 1):**
- **Epic** = recoloured body + ONE bold signature effect-zone that breaks the
  silhouette and carries the read. → `_make_skin(paint_fn, base_fn=…)`.
- **Legendary** = FULL re-plumage + a halo/aura AND a dramatic silhouette-
  breaking tail or crest — a genuine showpiece a clear tier above the epics. →
  custom back-aura getter (AURORA pattern: back-aura → body → front overlay →
  outline → rotation cache).

**Stepping OFF the taken axes.** Wave-1 elemental (STORM / PRISM / MAGMA /
AURORA / SOLAR), the rejected aquatic/glass four, and the locked CHROME secret
are all avoided. New territory mined here: **flora/botanical**, **cultural
carved-stone craft**, **cosmic-constellation (hard gold star-line, NOT soft
ribbons)**, and **luminous night-flora**.

Numbers map to `design_1..4` under `tools/parrot_wave2_candidates/` and
`docs/store_redesign/parrot/wave2/design_<N>/`. Order: epic, epic, legendary,
legendary.

---

## design_1 · THORNCREST MACAW — EPIC

*Inspiration: bramble-rose / wild-rose thicket + heraldic rose. The "wild
garden" parrot — pure flora axis, nothing the tab has touched.*

- **Hero silhouette:** a deep rose-red body crowned by an arching **briar-vine
  crest** — a single curved bramble cane springing up-and-back past the crown,
  studded with **2–3 hard ivory thorns** and tipped by one bold **bloomed rose**
  that juts past the silhouette. Reads instantly as "the bird with a rose
  growing out of its head."
- **Single signature effect-zone (`paint_fn` over a rose recolour):**
  - *Head/crest (the read):* one **dark-green briar cane** curving up past
    `CROWN_Y`, with sharp ivory thorn-spikes breaking the outline and a
    **3–4-petal rose blossom** (crimson→blush, a bright highlight petal) capping
    the tip — the hero shape.
  - *Body/wing accent:* the cane wraps the shoulder with **2 small leaf
    pairs** + one bud, and a thin thorn-line tics along the wing leading edge —
    kept to one accent per zone so it never busies the 40px read.
  - *Aviators:* tinted **warm rose-amber** with a tiny leaf glint.
- **Body recolour:** deep rose-red body, wine shadow, blush belly, brier-green
  line work so the vine reads as part of the bird.
- **Palette:** `#B5294A` rose-red body · `#7A1730` wine shadow · `#F2B6C4` blush
  belly/petal hi · `#2F6B3A` briar green · `#EFE7D2` ivory thorn · aviators
  **rose-amber**.
- **Distinctness:** the only **botanical/flora** epic — a living thorn-vine +
  bloom. Not a gem (PRISM), not glass, not ice; warm but matte pigment with NO
  glow so it never reads as MAGMA/SOLAR. Distinct from design_2 (carved stone,
  cool jade) and from both legendaries (no halo, no full re-plumage — it stays a
  red macaw with one wild crest).
- **Buildable?** Yes — `_make_skin(_paint_thorncrest, base_fn=lambda a:
  _build_parrot_with_palette(a, P_THORNCREST))`. Crest/thorns/rose are polygons
  + lines over the body, exactly the PRISM-crest model. No back-layer needed.

## design_2 · JADE-CARVING MACAW — EPIC

*Inspiration: Chinese carved nephrite jade + cinnabar lacquer seal; a cool
museum-object "the bird is a carving" look. Cultural craft / material axis.*

- **Hero silhouette:** a smooth **translucent-jade green body** that reads as
  one polished carved stone, finished by a **scrolling cloud-curl tail** — the
  tail-fan re-cut into a single bold **ruyi cloud spiral** that hooks out past
  the tail silhouette like a jade pendant's carved tip.
- **Single signature effect-zone (`paint_fn` over a jade recolour; the
  cloud-curl is a front overlay sitting on the existing tail, no back-layer):**
  - *Tail (the read):* the **ruyi cloud-scroll** — a fat comma/spiral of jade
    rim-lit pale-mint, edged with one **cinnabar-red lacquer line**, hooking up
    and out past the tail so it breaks the egg.
  - *Body accent:* 2–3 **carved relief grooves** (a darker jade line + a pale
    rim) sweeping along the back/chest so the body reads as sculpted nephrite,
    plus ONE small **cinnabar seal-mark square** stamped on the shoulder as the
    single warm pop.
  - *Aviators:* tinted **smoky jade**, frame relit pale so the carving catches
    light.
- **Body recolour:** milky jade green, deep teal-jade shadow, pale mint sheen
  (the polished-stone highlight), cinnabar accents.
- **Palette:** `#5FB58C` jade body · `#2E6E55` deep jade shadow · `#CFF0DC` mint
  polish hi · `#C8362B` cinnabar accent · `#1A3A30` carve-groove dark · aviators
  **smoky jade**.
- **Distinctness:** the only **carved-stone / cultural-craft** epic — matte
  polished mineral with relief grooves + a scroll tail, the opposite of glass
  (no panes, no lead, no back-light) and of ice (warm-leaning mint, not cold
  blue). Cool where design_1 is warm-red; tail-break where design_1 is
  crest-break, so the two epics can never be confused. No halo / no emission, so
  it stays clearly below the legendaries.
- **Buildable?** Yes — `_make_skin(_paint_jade, base_fn=lambda a:
  _build_parrot_with_palette(a, P_JADE))`. The cloud-scroll paints OVER the
  body's existing tail (it extends, not replaces, so no behind-body layer is
  required); grooves + seal are line/polygon overlays.

## design_3 · CONSTELLATION MACAW — LEGENDARY

*Inspiration: celestial globe / zodiac star-chart engraved in gold on lapis —
hard gold star-LINES, deliberately NOT aurora's soft teal ribbons. Cosmic axis,
re-entered through line-art instead of glow.*

- **Hero silhouette:** a deep **lapis-midnight body** webbed with **gold
  constellation lines + star-nodes**, ringed by a thin **gold orbital halo** and
  trailing a **comet-tail of star-nodes** — and crowned by a hard **gilded
  crescent-moon crest** rising past the crown. Two silhouette-breakers (crescent
  crest + comet tail) plus the halo = legendary.
- **Layered signature (back-aura getter: gold halo + comet-tail behind body →
  lapis body → front star-line overlay):**
  - *Behind head (halo — the legendary tell):* a thin **gold orbital ring**
    (a clean 2px gold band over a faint ink backing) sitting OUTSIDE the skull on
    the flanks, with 3–4 tiny star-glints pinned on it.
  - *Head/crest (silhouette-break #1):* a **gilded crescent moon** rising past
    `CROWN_Y`, a hard gold sliver with a pale inner rim and one white star tucked
    in its hollow.
  - *Body/wing:* **constellation join-the-dots** — gold star-NODES on the
    back/wing/chest connected by thin gold lines (a fixed, hand-placed pattern,
    NOT random), so the whole bird reads as an engraved star-chart. Wing leading
    edge gets one bright gold rim.
  - *Tail (silhouette-break #2):* a **comet trail** replacing the soft feather
    fan — a tapering line of gold star-nodes (big→small) streaming down-back into
    open sky, brightest node at the root.
  - *Aviators:* tinted **deep-sapphire** with a single gold top-rim glint.
- **Body recolour:** lapis midnight-blue, indigo shadow, with ALL accent value
  coming from hard metallic gold (no teal/green — the deliberate split from
  AURORA).
- **Palette:** `#15224A` lapis body · `#0C1430` indigo shadow · `#E8C25A` star
  gold · `#FFF3C8` gold glint/white star · `#3A5AA8` sapphire mid · aviators
  **deep sapphire**. *(Glow note: gold nodes get a small additive bloom in the
  back-aura pass so the chart twinkles on night sky; the gold LINES stay opaque
  so they survive day sky — same two-pass trick as AURORA.)*
- **Distinctness:** the only **gold-star-LINE celestial** skin. It reads cosmic
  like AURORA but is unmistakably different: AURORA is soft teal/green/magenta
  RIBBONS + a teal crescent halo; CONSTELLATION is hard metallic GOLD linework,
  a gold crescent-MOON crest, and a comet-NODE tail on lapis — a star-chart, not
  a sky-glow. No rainbow (vs PRISM), no fire (vs MAGMA/SOLAR). Gold-on-blue keeps
  it clear of design_4's warm pink/cream bloom.
- **Buildable?** Yes — custom getter on the AURORA pattern: `_constellation_back`
  (gold halo ring + comet-node trail, two-pass) → `_constellation_base`
  (`_build_parrot_with_palette(a, P_CONSTELLATION)`) → `_constellation_front`
  (crescent crest, star-line chart, rim) → `_add_outline` → rotation cache.

## design_4 · MOONBLOOM MACAW — LEGENDARY

*Inspiration: night-blooming moonflower / lotus + luna moth — soft pearl-white
petals that open at night, lit by a pale moon-glow. Luminous night-FLORA axis,
kept clear of deep-sea biolumen (this is a flower in moonlight, not an
anglerfish in the abyss).*

- **Hero silhouette:** a **pearl-white / lilac body** wearing a full **opened
  moonflower bloom** as a crest (broad rounded petals fanning past the crown),
  haloed by a soft **pale-gold moon-disc** behind the head, and trailing a
  **petal-and-pollen tail** — long luna-pale petal streamers shedding drifting
  pollen-motes. Full re-plumage + halo + petal crest + petal tail = a clear
  showpiece.
- **Layered signature (back-aura getter: moon-disc halo + petal-streamer tail
  behind body → pearl body → front petal-crest overlay):**
  - *Behind head (halo — the legendary tell):* a **soft pale-gold full-moon
    disc** glowing behind the skull (additive bloom in back-pass + an opaque pale
    rim so it survives day), larger than the head so it clears the silhouette on
    the flanks.
  - *Head/crest (silhouette-break #1):* an **opened moonflower** — 5 broad
    rounded white→lilac petals fanning up past `CROWN_Y`, each with a pale-gold
    inner rim, and a small **luminous yellow pollen-heart** at the centre.
  - *Body/wing:* pearl plumage washed with a **lilac-to-mint moon-sheen** and a
    scatter of fine **petal-vein lines**; wing edge catches a cool moon rim. Soft
    and luminous, never neon.
  - *Tail (silhouette-break #2):* **petal streamers** replacing the feather fan
    — 3 long translucent white→lilac petals rippling down-back, shedding 3–4
    drifting **pollen-glow motes** into open sky.
  - *Aviators:* tinted **pale moon-violet** with a soft white glint.
- **Body recolour:** luminous pearl-white body, cool lilac shadow, mint-pearl
  sheen — all value lifted so it reads as moonlit petals, not a flat void.
- **Palette:** `#F3EEF8` pearl body · `#B9A8D6` lilac shadow · `#D9F0E2` mint
  sheen · `#F6E6A8` moon-gold halo/pollen · `#8E7CB8` deep lilac line · aviators
  **moon-violet**. *(Glow note: moon-disc + pollen-motes use the additive
  back-pass; petals/veins stay opaque.)*
- **Distinctness:** the only **luminous night-flora** skin — a moonlit flower
  given wings. It's soft-pearl-and-gold where CONSTELLATION is hard-gold-on-blue,
  so the two legendaries split cleanly on both hue and value (bright bird vs dark
  bird). It is NOT deep-sea biolumen (warm moon-gold + petals + pollen, no
  abyssal navy, no lure-stalk, no teal photophores) and NOT ice (lilac/gold warm
  cast, organic petals not crystal spikes). No ribbons (vs AURORA), no fire,
  no facets.
- **Buildable?** Yes — custom getter on the AURORA pattern: `_moonbloom_back`
  (moon-disc halo + petal-streamer tail + pollen-motes, two-pass) →
  `_moonbloom_base` (`_build_parrot_with_palette(a, P_MOONBLOOM)`) →
  `_moonbloom_front` (opened-petal crest, veins, rim) → `_add_outline` →
  rotation cache.

---

### Build contract (for every design)

- File `tools/parrot_wave2_candidates/design_<N>.py` exposing `build`.
  - **Epics (1, 2):** `build = store_skins._make_skin(paint_fn,
    base_fn=lambda a: _build_parrot_with_palette(a, P_<NAME>))`.
  - **Legendaries (3, 4):** a custom getter mirroring `store_skins`'
    `_aurora_getter` — back-aura (halo + tail, two-pass additive/opaque) → body →
    front overlay → `_add_outline` → per-(frame, 3°-bucket) rotation cache, with
    the aura laid UNDER the outlined bird (padded to the outline grow) so the
    soft glow isn't boxed by the house outline.
- Anchors in COMPOSITE space: `HX`, `HY`, `CROWN_Y`, `COMPOSITE_W/H`, `PARROT_DY`.
- Render in-gameplay via `tools/ninja_render.py` (`gameplay_panel` + `hero_panel`
  + a 40px NEAREST truth-read; legendaries get a 4-frame filmstrip), saving
  `docs/store_redesign/parrot/wave2/design_<N>/round_<M>.png`. Self-commit
  builder + sheet. **Never** register in `store_skins.BUILDERS`.

### Ranking & picks

1. **CONSTELLATION MACAW (legendary)** — strongest showpiece and cleanest 40px
   read: hard gold-on-lapis has built-in value contrast, the gold crescent crest
   + comet tail are unmistakable silhouette-breaks, and it re-enters the cosmic
   theme through engraved line-art so it never collides with AURORA's ribbons.
   Best legendary of the set.
2. **MOONBLOOM MACAW (legendary)** — best bright-bird / day-sky performer and the
   most charming; opened-flower crest + moon halo is a premium, novel look and
   the perfect tonal counterweight to CONSTELLATION (bright vs dark). Slightly
   riskier (soft pearls must stay crisp at 40px) so ranked 2nd.
3. **THORNCREST MACAW (epic)** — boldest epic read: one rose + thorns off the
   crown is a single hero shape that survives downscale, and flora is wholly
   fresh territory for the tab.
4. **JADE-CARVING MACAW (epic)** — most premium-feeling epic; the carved cool
   "museum object" with a cloud-scroll tail is distinct and elegant, but the
   relief-groove detail is a touch busier than THORNCREST's single bloom, so it
   ranks last while still being a strong, clearly-distinct pick.

**Best legendary showpiece:** CONSTELLATION MACAW (with MOONBLOOM as the
bright-sky / charm-leaning alternative). **Tier mix delivered:** 2 epic
(THORNCREST, JADE-CARVING) + 2 legendary (CONSTELLATION, MOONBLOOM).

Sources that sparked the picks:
- [Klimt gold leaf / ornament](https://mymodernmet.com/gustav-klimt-golden-phase/)
  (gold-on-dark material language → CONSTELLATION's engraved gold).
- [Pavo / Phoenix celestial bird constellations](https://www.constellation-guide.com/constellation-list/pavo-constellation/)
  (star-chart-as-bird → CONSTELLATION).
- [Cherry-blossom vs autumn-maple palettes](https://www.schemecolor.com/autumn-maple-leaf.php)
  (flora colour structure → THORNCREST / MOONBLOOM).
