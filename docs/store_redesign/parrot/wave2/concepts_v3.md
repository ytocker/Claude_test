# Wave 2 — Parrot Skin Concepts v3

Two replacement concepts. Every skin is an ascended, recoloured **Pip the macaw**;
aviators always stay (tinted to suit). North star: lives or dies at 40px in motion —
each signature shape is pushed past the crown or out past the tail to break the egg
silhouette; hard ≥2px features only; reads on BOTH day (bright blue) and night (navy).

Taken/avoided axes: storm-lightning, prism-crystal, magma-lava, aurora-ribbon,
solar-sun, briar/rose flora, moonflower/moon-halo, chrome/liquid-metal, ice/glacier,
koi/scales, deep-sea bio-lume, stained-glass, gold star-chart cosmic, carved jade.

---

## design_3 · EMBERMOTH MACAW — EPIC

- **Hero silhouette:** Pip with a single broad, swept **moth-antenna plume** rising and
  forking back past the crown — two feathered fronds (not symmetric horns) that fan
  like a luna-moth feeler, breaking the egg at the top-rear corner.
- **Signature effect-zone (crest only):**
  - One forked antenna-plume swept up-and-back past the crown; each frond is a flat
    feathered comb-edge (hard ≥3px teeth) so it survives downscale as a ragged fan.
  - A single bold **eyespot disc** sits at the base of the plume where it meets the
    crown — dark ring + warm-cream pupil — the one high-contrast tell that carries 40px.
  - No tail change, no halo. Recoloured body + this one hero shape is the whole kit.
- **Body recolour:** Dusky charcoal-mauve plumage with a warm dusty-rose breast wash,
  giving a velvety "night-moth" body that reads dark-on-bright-day and warm-on-navy.
- **Palette:** `#2B2230` (charcoal-mauve base) · `#6E4A55` (dusty-rose breast) ·
  `#E8C58A` (cream eyespot pupil / plume tips) · `#3A2C40` (plume body / dark ring) ·
  `#C77A5A` (warm ember accent on wing edge). Aviator tint: smoked amber `#A86A3C`.
- **Distinctness:** New axis = entomology/moth, not bird/flora/mineral/cosmic. The
  eyespot tell and forked feeler-plume share zero shape language with any rose crest,
  crystal facet, or lightning bolt; warm-on-dark velvet value structure is unused
  (keepers are pearl-white, rose-red, or gold).
- **Buildable?** Yes — `_make_skin(paint_fn, base_fn=_build_parrot_with_palette)`:
  body recolour via palette swap, then a flat polygon plume + comb-edge teeth + a
  two-ring eyespot disc drawn in `paint_fn` over the crown. No back layer.

---

## design_4 · TEMPEST CONDOR MACAW — LEGENDARY

- **Hero silhouette:** A storm-grey raptor-scaled Pip wearing a **swept-back twin
  storm-quill crest** AND trailing a long forked **vapour-streamer tail**, set against
  a soft circular **squall-halo** behind the head — two silhouette-breakers plus the
  legendary halo tell.
- **Layered signature:**
  - **Back-aura (halo):** a circular dark slate-blue storm-disc behind the head, rimmed
    with a hard pale-cyan opaque ring (day read) and an additive cyan under-glow (night
    read) — a contained "eye of the storm" that reads on both skies.
  - **Crest (top-rear breaker):** two long swept storm-quills raked back past the crown,
    each a flat tapered blade with a hard bright-cyan leading edge — bold, ≥3px wide.
  - **Tail (rear breaker):** a long forked **vapour streamer** trailing out past the
    tail, two ribbon-tongues with a bright rim and a few hard wind-streak ticks (not a
    soft mist — hard edges to survive 40px).
  - Front overlay adds a single bright cyan brow-spark above the aviators.
- **Body recolour:** Full re-plumage to brushed storm-grey with deep slate underwing
  and a cool steel-blue sheen, so the cyan crest/tail/halo pops as the only saturated
  colour against an otherwise desaturated body.
- **Palette:** `#3C4654` (storm-grey base) · `#1E2733` (deep slate underwing) ·
  `#7FE3F0` (bright cyan crest/tail/halo rim) · `#C8D6DE` (pale steel sheen / highlight)
  · `#0E3A4A` (storm-disc dark fill). Aviator tint: cool steel-cyan `#5FB8C8`.
  Glow note: halo ring + crest edges are HARD opaque pale-cyan for day; an additive
  cyan radial sits beneath them, only visible against navy, for the night under-glow.
- **Distinctness:** Storm here is **monochrome wind/squall** (grey body, single cyan
  accent, contained circular eye-of-storm halo) — not STORM's gold-lightning bolts, not
  AURORA's multi-hue soft ribbon, not SOLAR's warm radial. Raptor-condor body language
  + forked vapour streamer is a new silhouette family vs the flora crests and faceted
  crystal of the keepers. Cool desaturated value structure is unclaimed by any
  legendary so far.
- **Buildable?** Yes — AURORA-pattern custom getter: back-aura (storm-disc + cyan ring
  + additive under-glow) → body (palette re-plumage) → front overlay (twin storm-quill
  crest + forked vapour-streamer tail + brow-spark) → outline → rotation cache.

---

## Ranking & picks

1. **design_4 · TEMPEST CONDOR (legendary)** — strongest showpiece: the contained
   eye-of-storm halo + single-saturated-cyan-on-grey value structure is the most
   premium, most novel, and the cleanest dual-sky read. Best legendary of the pair.
2. **design_3 · EMBERMOTH (epic)** — the freshest *axis* (moth/entomology) with the
   single hardest 40px tell (the eyespot disc), and warm-velvet colour no keeper owns.

Both deliberately sit on untaken axes (monochrome squall-wind; moth) and lean on
hard-edged silhouette-breakers that survive downscale.
