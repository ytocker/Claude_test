# PARROTS — Wave 2 concept brief (rarity-spectrum extension)

Wave 1 carried the tab from rare → legendary across the *elemental* axis
(STORM / PRISM / MAGMA / AURORA / SOLAR) plus the six real-species recolours.
Wave 2 extends the rarity spectrum with **2 epic + 2 legendary + the tab's
FIRST secret** — and deliberately steps off the elemental axis so nothing
collides with wave 1.

Every skin stays recognisably **Pip the macaw wearing his signature aviator
sunglasses, just "ascended"** — an equippable cosmetic recolour of the player
bird, NOT a from-scratch ANIMALS-tab creature. Build path is the established
one: body = `dollar_parrot_ghost._build_parrot_with_palette` + a `_pal` palette
dict; signature = a `paint_fn` overlay (cockatoo-crest model) **or** a custom
back-layer getter when a halo/aura/tail must paint BEHIND the body (aurora /
viking-axe model). Wrapped by `store_skins._make_skin`; **never** registered in
`store_skins.BUILDERS`.

**North star — lives or dies at 40px in motion.** Every signature shape is
pushed up past the crown or out past the tail to break the egg silhouette; held
to ≥2px so it survives downscale; kept off near-black so it reads on the navy
store card; and checked on BOTH day and night sky. Aviators always stay, tinted
to suit.

**Tier rule (same escalation as wave 1):**
- **Epic** = recoloured body + ONE bold signature effect-zone that breaks the
  silhouette and carries the read.
- **Legendary** = FULL re-plumage + a halo/aura AND a dramatic silhouette-
  breaking tail or crest — a genuine showpiece, a clear tier above the epics.
- **Secret** = masked "???" until bought; a premium, surprising "whoa" parrot —
  absurd/unexpected but still parrot-SHAPED and still wearing the aviators.

Numbers map to `design_1..5` under `tools/parrot_wave2_candidates/` and
`docs/store_redesign/parrot/wave2/design_<N>/`.

Order below: epic, epic, legendary, legendary, secret.

---

## design_1 · GLACIER MACAW — EPIC (~1200)

*Inspiration: glacier ice + luna-moth frost; a cold, crystalline counterpart to
wave 1's hot MAGMA. The "winter" parrot.*

- **Hero silhouette:** pale ice-blue body crowned with a fan of **sharp icicle
  spikes** jutting up off the crown — a jagged frozen outline, frost-rimed tail.
- **Layered signature (paint_fn over a frost recolour):**
  - *Head/crown:* a 3–4 prong **icicle crest** — translucent blue-white spikes
    rising above CROWN_Y, brightest at the tips, with a thin white frost edge.
  - *Body/wing:* **frost-rime crackle** along the wing leading edge and back —
    fine white branching frost lines + a cool blue rim-light; 2–3 hard facet
    glints on the chest like ice catching light.
  - *Tail:* tail feather tips dipped in pale frost (white→ice-blue gradient),
    with 2–3 drifting **snow-sparkle** dots above the back.
- **Body recolour:** glacier ice-blue body, deep cyan-slate shadows, near-white
  frosted belly.
- **Palette:** `#A9D8E8` glacier ice body · `#5F93B0` cyan-slate shadow ·
  `#EAF6FF` frost white · `#C7ECFF` ice glint · aviators tinted **pale cyan**.
- **Distinctness:** the only **cold/frozen** parrot — icicle crest + frost rime
  is unmistakable vs PRISM's rainbow facets (this is single-hue ice, no
  spectrum) and is the literal opposite of MAGMA's hot internal glow.

## design_2 · KOI MACAW — EPIC (~1600)

*Inspiration: Japanese koi + urushi lacquerware; warm "lucky carp" energy, a
cultural recolour with a watery signature where the elemental tab has none.*

- **Hero silhouette:** lacquer-white body marbled with bold **koi-orange
  blotches**, finished by long trailing **fin-like tail streamers** that ripple
  out past the tail — reads like a carp swimming through air.
- **Layered signature (paint_fn over a lacquer recolour; tail likely a small
  back-layer so streamers sit behind the body):**
  - *Head/crown:* a swept **koi-fin crest** — two flowing orange-and-white
    finned plumes arcing up past the crown (soft, not spikes).
  - *Body/wing:* hand-painted **koi blotch pattern** — 3–4 bold orange/black
    marbled patches over a white lacquer body, edged with a thin gold sumi line;
    wing tipped orange.
  - *Tail/aura:* long **trailing fin streamers** (white→orange, translucent
    edges) rippling out behind, plus 3–4 small **water-bubble** dots drifting up.
- **Body recolour:** lacquer-white (kohaku) body, warm ivory shadow, bold koi
  orange + ink-black markings.
- **Palette:** `#FFFFFF` lacquer white · `#F2632B` koi orange · `#1C1C22` ink
  black · `#E8C45A` gold sumi edge · `#9FD8E0` water-bubble accent · aviators
  tinted **warm amber**.
- **Distinctness:** the only **organic/aquatic, culturally-themed** parrot — koi
  marbling + finned streamers read as water, totally apart from the energy/gem/
  fire wave-1 set and from GLACIER's cold geometry. Warm but not fiery (it's
  paint + water, no glow), so it never reads as MAGMA or SOLAR.

## design_3 · BIOLUMEN MACAW — LEGENDARY (~2900)

*Inspiration: deep-sea bioluminescence + bioluminescent jungle; an
electric blue-green that actually emits light. First wave-2 showpiece.*

- **Hero silhouette:** a dark abyssal body **lit from within** by glowing
  blue-green veins, a forward-curving **anglerfish lure-stalk** rising off the
  crown with a glowing orb, and a **halo of drifting light-motes** — clearly a
  tier above the epics.
- **Layered signature (back-layer aura behind body + paint_fn front overlay):**
  - *Behind head:* a soft **bioluminescent halo** — a faint additive teal ring
    of glowing plankton motes (the legendary tell).
  - *Head/crown:* a curving **lure-stalk crest** arcing up and forward over the
    head, tipped with a bright glowing orb (cyan core → white hot center) — the
    silhouette-breaking signature.
  - *Body/wing:* **glowing vein networks** (teal→lime, additive) tracing the body
    and wing edges over near-black abyssal plumage; spotted **photophore dots**
    glowing along the belly.
  - *Tail:* a sweeping **lit jelly-frill tail** — translucent glowing membranes
    (teal→deep blue) replacing the feather fan and trailing down-back, with
    drifting light-motes shedding off it.
- **Body recolour:** deep abyssal navy-black body, with all colour coming from
  the emitted light (cool teal/lime).
- **Palette:** `#0E1A2E` abyssal navy body · `#0A0F1A` deep shadow · `#33F0C8`
  biolumen teal · `#A8FF6E` lure lime · `#EAFFFA` core glow-white · aviators
  tinted **glowing teal**.
- **Distinctness:** the only **dark-body + emissive-light** legendary — it's a
  living lantern, not reflected colour. Reads against MAGMA (warm internal glow)
  by being cold/cyan, and against AURORA (cosmic ribbons) by being a creature-of-
  the-deep with a lure-stalk + jelly tail rather than star plumage.

## design_4 · STAINED-GLASS MACAW — LEGENDARY (~3400)

*Inspiration: cathedral stained glass — jewel-tone leaded panes lit from behind;
a sacred, luminous showpiece distinct from any natural recolour.*

- **Hero silhouette:** a radiant bird whose every feather is a **leaded glass
  pane** glowing as if back-lit, crowned by a **rose-window halo** and trailing a
  fan of long **cathedral-tall glass tail panes** — ornate and unmistakable.
- **Layered signature (back-layer halo + glass tail behind body, paint_fn front
  overlay):**
  - *Behind head:* a circular **rose-window halo** — concentric jewel-tone
    segments (ruby/sapphire/amber wedges) with dark lead spokes, softly back-lit
    (the legendary tell).
  - *Head/crown:* a **gothic-arch crest** — 3 tall pointed glass panes (ruby,
    sapphire, emerald) edged in lead, rising past the crown like a window top.
  - *Body/wing:* plumage redrawn as **leaded jewel panes** — each feather a flat
    colour facet separated by thin dark **lead lines**, glowing from within; wing
    panes catch a bright light-shaft glint.
  - *Tail:* long **cathedral tail-panes** — elongated pointed jewel-glass panes
    fanning down well past the body, lead-edged, with a soft coloured light-spill
    glow beneath.
- **Body recolour:** deep jewel mosaic — ruby/sapphire/emerald/amber panes over
  dark lead lines, all back-lit.
- **Palette:** `#D7263D` ruby · `#1F5FC4` sapphire · `#1FA873` emerald · `#F2B23E`
  amber · `#15131A` lead line / dark · aviators tinted **smoky cathedral grey**.
- **Distinctness:** the only **leaded jewel-pane** legendary — hard lead lines +
  back-lit panes are an art-object look, the opposite of feathers. Vs PRISM
  (sharp clear crystal shards, no lead, rainbow refraction) it's flat opaque
  panes bound by black lead and a rose-window halo; nothing else in the tab uses
  the segmented-glass language.

## design_5 · CHROME MACAW — SECRET (~6000, masked "???")

*Inspiration: liquid-chrome / Y2K mecha + flying-toaster-secret energy; the
"whoa" — a polished metal Pip that looks injection-moulded, still a parrot, still
in aviators. The tab's first secret.*

- **Hero silhouette:** a mirror-polished **liquid-chrome parrot** — every curve a
  hard specular reflection, with a swept **chrome fin-crest** and a fanned set of
  **bladed metal tail-vanes**, plus a thin **holographic halo ring** orbiting it.
  Reads instantly as "the metal one."
- **Layered signature (back-layer holo ring + metal tail-vanes behind body,
  paint_fn front overlay):**
  - *Behind head:* a thin **holographic halo ring** — an oil-slick iridescent
    band (cyan↔magenta↔gold shift) hovering behind the head (the secret tell).
  - *Head/crown:* a swept-back **chrome fin-crest** — 2–3 polished metal blades
    rising past the crown, each with a hard white spec-highlight streak and a deep
    reflection shadow.
  - *Body/wing:* **liquid-chrome plumage** — body rendered as polished steel with
    a sharp environment-reflection gradient (dark steel base → bright sky-blue
    sheen band → white hotspot), seam/panel lines suggesting a moulded shell;
    bolt/rivet dots at the shoulder.
  - *Tail:* a fan of **bladed chrome tail-vanes** — angular metal feathers, each a
    mirror gradient with a razor highlight edge, splaying down-back.
  - *Aviators:* upgraded to **mirror-chrome lenses** with an iridescent oil-slick
    glint — the "still Pip" anchor that sells the joke.
- **Body recolour:** polished chrome — there is no local hue, only a steel→
  sky-sheen→white reflection ramp, with one iridescent accent band.
- **Palette:** `#3A4250` steel shadow · `#8FA6BE` mid chrome · `#E8F2FA` chrome
  hotspot · `#FFFFFF` spec highlight · `#7CF0E0`/`#FF8AD8` oil-slick iridescent
  accents · aviators tinted **mirror-chrome / oil-slick**.
- **Distinctness:** the only **non-organic, fully reflective** skin in the whole
  tab — a manufactured-metal parrot is the surprise. It avoids every elemental
  hue (its "colour" is reflection, not pigment), is hard/specular where everything
  else is feathered or glowing, and earns the secret slot the way PAPER PLANE /
  FLYING TOASTER do on the animals tab — a "they made Pip out of *chrome*?" reveal,
  yet unmistakably still Pip in his aviators.

---

### Build contract (for every design)

- File `tools/parrot_wave2_candidates/design_<N>.py` exposing
  `build = store_skins._make_skin(paint_fn,
   base_fn=lambda a: _build_parrot_with_palette(a, P_<NAME>))`,
  or a custom compose when an aura/halo/tail must paint BEHIND the body
  (back-layer first → body → front overlay; see the `store_skins` viking-axe
  body-first caveat). Designs 2–5 all need a back-layer for tail/halo.
- Anchors in COMPOSITE space: `HX`, `HY`, `CROWN_Y`, `COMPOSITE_W/H`, `PARROT_DY`.
- Render in-gameplay via `tools/ninja_render.py` (`gameplay_panel` + `hero_panel`
  + a 40px NEAREST truth-read; legendaries + the secret get a 4-frame filmstrip),
  saving `docs/store_redesign/parrot/wave2/design_<N>/round_<M>.png`. Self-commit
  builder + sheet. **Never** register in `store_skins.BUILDERS`.

### Ranking & picks

1. **CHROME MACAW (secret)** — the headline. Biggest "whoa", cleanest 40px read
   (pure value contrast, no hue dependence), perfectly on-brief for the tab's
   first secret. Strongest single pick.
2. **STAINED-GLASS MACAW (legendary)** — most ornate showpiece; rose-window halo
   + lead-line language is the most premium, novel look and screams legendary.
3. **BIOLUMEN MACAW (legendary)** — best night-sky performer; emissive light +
   lure-stalk is a striking, distinct showpiece.
4. **GLACIER MACAW (epic)** — cleanest, most readable epic; the obvious cold
   counterpart the tab is missing.
5. **KOI MACAW (epic)** — warmest, most charming; bold blotch pattern reads well,
   slightly busier than GLACIER so ranked last but still strong.

**Best legendary showpiece:** STAINED-GLASS MACAW (with BIOLUMEN as the night-
sky-leaning alternative). **Tier mix delivered:** 2 epic, 2 legendary, 1 secret.
