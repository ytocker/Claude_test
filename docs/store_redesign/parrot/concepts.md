# PARROTS rarity-spectrum — concept brief

The PARROTS store tab currently stops at *rare*. Its six skins are real-species
full-body recolours of Pip the macaw (BLUE MACAW, AMAZON, SUN CONURE / HYACINTH,
COCKATOO, LORIKEET). This explores **5 new skins that complete the spectrum** —
**3 epic + 2 legendary** — each more spectacular as rarity climbs.

Rarity is price-derived (`game/store_catalog.py`): `epic 800–2499`, `legendary
≥2500`. These skins stay recognisably **Pip-the-macaw with his aviators, just
ascended** — distinct from the ANIMALS-tab PHOENIX / THUNDERBIRD (which are
from-scratch creatures). Build via the palette recolour
(`dollar_parrot_ghost._build_parrot_with_palette` + `_pal`) **plus** a `paint_fn`
signature overlay, wrapped by `store_skins._make_skin` (the cockatoo-crest model).

**Escalation rule (the whole point of the spread):**
- **Epic** = a recoloured body + ONE bold signature effect-zone that breaks the
  silhouette and carries the 40px read (electric crest, gem facets, magma glow).
- **Legendary** = FULL cosmic/radiant re-plumage + a halo/aura ring AND a dramatic
  silhouette-breaking tail/crest — a genuine showpiece, clearly a tier above.

The north star, as always: **a skin lives or dies at 40px in motion.** Every
signature shape is pushed up past the crown to break the bird's outline, kept off
near-black on the navy store card, held to ≥2px so it survives downscale, and
checked on day AND night sky. Aviators stay (Pip's signature), tinted to suit.

Numbers map to `design_1..5` under `tools/parrot_rarity_candidates/` and
`docs/store_redesign/parrot/design_<N>/`.

---

## design_1 · STORM MACAW — EPIC (~1100)

The elemental charge of the set: a storm-petrel macaw crackling with electricity.

- **Hero silhouette:** slate body with a jagged lightning-bolt crest spiking up
  off the crown and glowing charged wingtips — an angular, electric outline.
- **Layered signature (paint_fn over a slate recolour):**
  - *Head/crown:* a 3-prong jagged cyan lightning crest (zig-zag, not feathers)
    rising above CROWN_Y, brightest at the tips.
  - *Wing:* charged electric-cyan wingtip glow + one forked micro-bolt arcing off
    the leading wingtip.
  - *Body:* a faint cyan rim-light along the back edge; 3–4 static spark dots
    orbiting the head.
- **Body recolour:** stormcloud slate-blue, deeper steel shadows, cool pale belly.
- **Palette:** `#46506E` slate body · `#2A3A5A` deep · `#7FE3FF` electric cyan ·
  `#C8F4FF` spark white · `#FFD24A` aviator gold (kept).
- **Distinctness:** the only *energy/elemental* parrot — cool electric cyan
  against slate, the crest reads as a lightning bolt at a glance.

## design_2 · PRISM LORIKEET — EPIC (~1400)

Hard crystalline geometry against the whole tab's soft feathers.

- **Hero silhouette:** angular gem-shard crest of sharp crystal points (not
  plumes) + faceted, hard-edged wing.
- **Layered signature (paint_fn over a crystal recolour):**
  - *Head/crown:* a cluster of 3 angular crystal shards fanning up past the crown,
    each a flat facet with a bright edge highlight.
  - *Body/wing:* prismatic refraction glints — small rainbow facet sparks (teal →
    amethyst → rose) on the chest and wing, hard triangular highlights.
  - *Aura:* 2–3 floating diamond sparkles off the back.
- **Body recolour:** cool crystal-teal body with amethyst undertone, white facet
  highlights.
- **Palette:** `#5ED7D0` crystal teal · `#B98CF0` amethyst · `#FF9AD0` rose
  refraction · `#FFFFFF` facet glint · `#2E6E78` deep teal.
- **Distinctness:** the only *faceted/geometric* parrot — sharp shards + rainbow
  refraction where everything else is soft and single-hued.

## design_3 · MAGMA CONURE — EPIC (~1700)

Lit from within: a charcoal bird veined with molten glow.

- **Hero silhouette:** dark compact body with a smoke-and-ember crest curling up,
  glowing crack-lines tracing the body.
- **Layered signature (paint_fn over a charcoal recolour):**
  - *Head/crown:* a smoke-wisp crest (curling grey plume) tipped with 2–3 bright
    embers above the crown.
  - *Body/wing:* glowing magma crack-lines (orange→yellow gradient) along the
    body and wing leading edge; ember-tipped feather ends.
  - *Aura:* 3–4 rising ember sparks above the back, hottest near the body.
- **Body recolour:** near-black charcoal body, deep shadow, with the cracks as the
  only warm light.
- **Palette:** `#322A2E` charcoal · `#1A1518` deep · `#FF6A1E` magma orange ·
  `#FFC53A` ember yellow · `#8A8A8A` smoke grey.
- **Distinctness:** the only *dark-body, internal-glow* parrot — the contrast of
  black plumage against hot cracks is the read. (Keep cracks ≥2px and off the
  near-black card edge so they don't vanish.)

## design_4 · AURORA MACAW — LEGENDARY (~2800)

Night sky given wings — the first true showpiece. Full re-plumage + halo + ribbon
tail.

- **Hero silhouette:** a haloed bird trailing flowing aurora ribbons where the
  tail was — unmistakable as a tier above the epics.
- **Layered signature (paint_fn over a galaxy recolour):**
  - *Behind head:* a soft luminous **halo ring** (faint, additive) — the legendary
    tell.
  - *Crown:* a nebula crest of glowing wisps (green↔magenta) rising past the crown.
  - *Tail:* flowing **aurora ribbons** (green→magenta light bands) replacing the
    feather fan, sweeping down-back and breaking the lower silhouette.
  - *Body:* midnight galaxy plumage flecked with small white stars; aurora rim
    light along the back.
- **Body recolour:** deep midnight indigo grading to aurora teal/magenta, star
  flecks.
- **Palette:** `#1C1B3A` midnight indigo · `#3FE0A6` aurora green · `#C45CE8`
  aurora magenta · `#6FA8FF` star blue · `#FFFFFF` star glint.
- **Distinctness:** legendary cosmic transformation — halo + ribbon tail + starry
  body. The night counterpart to design_5.

## design_5 · SOLAR QUETZAL — LEGENDARY (~3500)

The apex: a radiant sun-god macaw. Full re-plumage + sun-disc halo + sweeping
quetzal streamers + rays.

- **Hero silhouette:** a sun-disc halo blazing behind the head and long luminous
  tail-streamers sweeping down — the brightest, most ornate outline of the set.
- **Layered signature (paint_fn over a radiant-gold recolour):**
  - *Behind head:* a **sun-disc halo** — golden disc with short radiating rays
    (the legendary tell, hotter/brighter than Aurora's soft ring).
  - *Crown:* a feathered gold crown-crest fanning up.
  - *Tail:* long luminous **quetzal tail-streamers** (gold core, emerald edge)
    trailing well below the body, the dramatic silhouette break.
  - *Body:* radiant gold/white plumage with emerald quetzal accents; white-gold
    core glow rim.
- **Body recolour:** luminous gold body, sun-white chest, emerald accents.
- **Palette:** `#FFD24A` radiant gold · `#FFF3C0` sun white · `#FF9A2E` warm amber
  · `#2FB98A` quetzal emerald · `#FFFFFF` core glow.
- **Distinctness:** the day-star apex — pure radiant light, sun-disc + streamers;
  the warm/gold counterpart to Aurora's cool/night. Priced highest of all parrots.

---

### Build contract (for every design)

- File `tools/parrot_rarity_candidates/design_<N>.py` exposing
  `build = store_skins._make_skin(paint_fn, base_fn=lambda a: _build_parrot_with_palette(a, P_<NAME>))`
  (or a custom compose if draw-order needs the aura BEHIND the body — e.g. halos
  and ribbon tails likely paint a back-layer first, then the body, then the
  front overlay; see `store_skins` viking axe note for the body-first caveat).
- Anchors in COMPOSITE space: `HX`, `HY`, `CROWN_Y`, `COMPOSITE_W/H`, `PARROT_DY`.
- Render in-gameplay via `tools/ninja_render.py` (`gameplay_panel` + `hero_panel`
  + a 40px NEAREST truth-read; legendaries get a 4-frame filmstrip), saving
  `docs/store_redesign/parrot/design_<N>/round_<M>.png`. Self-commit builder +
  sheet. **Never** register in `store_skins.BUILDERS`.
