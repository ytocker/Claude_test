# Skybit — `skin_bee` (400-coin animal) — Butterfly Roster

Theme locked by the user: **all butterflies / Lepidoptera.**
Reference execution = **Design 1 AZUREWING** (blue morpho): wall-to-wall
rounded wings, tiny dark body behind the wings, dark scalloped ink margin with
white eye-flecks, bright structural-blue inner field + per-frame iridescent
cyan shimmer, black head with two thin clubbed antennae.

These five are **design_2 … design_6** for `tools/bee_candidates/`. None reuse
the blue/cyan family (AZUREWING owns it). Each is a different family with a
distinct wing SHAPE and a distinct dominant hue. Ranked most → least
premium/dramatic.

Shared rig: 64×84 SRCALPHA, procedural. Thorax `BCX=32,BCY=44`; head
`HCX=44,HCY=34`; antennae reach `CROWN_Y=24`; body axis runs upper-right (head)
→ lower-left (abdomen). Wings mount on the 4-frame parrot flap; the flap reads
as a wingbeat (wings sweep up on the open pose, dip/tuck on the closed pose).

---

## Rank 1 — SUNSET MOTH  ·  `design_2`

- **Species / archetype:** Madagascan sunset moth (*Chrysiridia rhipheus*),
  Uraniidae — the day-flying "rainbow" moth. The legendary showpiece of the set.
- **Hero silhouette:** broad wings on a jet-black base **crossed by curved
  bands of molten rainbow iridescence**, hindwings ending in a short row of
  little scalloped tails + a pale fringe.
- **Objects + placement:**
  - *Head/antennae:* small black head at HCX/HCY, two thin black antennae
    (filamentous, non-clubbed — moth) fanning to CROWN_Y.
  - *Body:* slim dark body, mostly hidden behind wings.
  - *Wings:* rounded-broad forewings, hindwings with a **scalloped tailed
    lower edge** (3–4 short lobes, not the long single luna tail). Wing fill is
    obsidian black with **concentric arced iridescent bands** (magenta → emerald
    → orange) hugging the hindwing curve; cream-dotted fringe on the tail edge.
  - *Special FX:* per-frame **hue-sweep** — the rainbow bands shift position/hue
    across the 4 flap frames (like AZUREWING's shimmer but polychrome), plus a
    faint outer glow so it reads on night sky.
- **Palette:** `#0E0B14` Obsidian (dominant base) · `#E0348A` Sunset Magenta
  (accent) · `#1FB86B` Prism Emerald · `#FF7A1A` Ember Orange · `#F2E4B0`
  Fringe Cream.
- **Distinctness:** the only concept that is **black-with-rainbow-bands**;
  polychrome iridescence + scalloped mini-tails vs everyone else's single hue.

## Rank 2 — LUNAWING  ·  `design_3`

- **Species / archetype:** Luna moth (*Actias luna*), Saturniidae — the
  glowing long-tailed moon moth.
- **Hero silhouette:** pale lime wings with **two long, sweeping, slightly
  twisted hindwing tails** trailing down toward the abdomen — the tails ARE the
  ID at 40px.
- **Objects + placement:**
  - *Head/antennae:* small furry pale head; **feathery/comb antennae** (a hair
    thicker than AZUREWING's clubbed pair) to CROWN_Y.
  - *Body:* short fuzzy cream body.
  - *Wings:* rounded upper wings; hindwings taper into **two elongated ribbon
    tails** curving lower-left with the body axis. One amber-ringed **eyespot**
    per wing; a maroon leading edge stripe on the forewing.
  - *Special FX:* soft green **outer glow / bloom** (moonlit look) that pulses
    subtly across frames — sells "premium" and guarantees the night-sky read.
- **Palette:** `#B8E986` Luna Lime (dominant) · `#E4F7C5` Moonmint (highlight)
  · `#7A2E3B` Plum Edge (accent) · `#E8A13C` Eye Amber · `#F0EAD2` Body Cream.
- **Distinctness:** only concept with **long trailing tails + lime glow**; the
  tailed silhouette can't be mistaken for the rounded morphos or the angular
  atlas.

## Rank 3 — MONARCH  ·  `design_4`

- **Species / archetype:** Monarch (*Danaus plexippus*), Nymphalidae — the
  iconic stained-glass orange butterfly.
- **Hero silhouette:** classic **rounded, playing-card wings** in bright orange
  webbed by heavy black veins, framed by a black border studded with white
  dots — instantly "butterfly" to any player.
- **Objects + placement:**
  - *Head/antennae:* black head, two thin **clubbed** antennae (true
    butterfly) to CROWN_Y; a couple of white specks on the head.
  - *Body:* black body with white flecks, tucked behind wings.
  - *Wings:* broad rounded fore + hind; **radiating black veins** dividing
    orange cells (stained-glass), thick black margin with a **double row of
    white eye-flecks** echoing AZUREWING's margin language but in warm hues.
  - *Special FX:* none heavy — a light warm inner gradient (amber core → deeper
    orange edge). Reads on value alone, so it holds on both skies.
- **Palette:** `#F27A1A` Monarch Orange (dominant) · `#1A130E` Vein Black
  (accent) · `#F5F1E6` Flake White · `#FFB347` Amber Core · `#C4531A` Warm
  Shadow.
- **Distinctness:** the **veined-orange stained-glass** look; warm and
  high-chroma where the others are green, black-rainbow, earthy, or clear.

## Rank 4 — ATLASWING  ·  `design_5`

- **Species / archetype:** Atlas moth (*Attacus atlas*), Saturniidae — one of
  the largest moths; famous **"cobra-head" wingtips**.
- **Hero silhouette:** enormous **angular** wings whose upper corners hook out
  into pointed **snake-head tips**, with big triangular translucent "windows" —
  the only jagged, non-rounded outline in the set.
- **Objects + placement:**
  - *Head/antennae:* small head, broad **feathery antennae**.
  - *Body:* stout banded body.
  - *Wings:* geometric maroon/rust wings with **cream triangular window
    panes** near the center of each wing; forewing apex extends into a hooked
    tan **snake-head tip** (dark eye-dot at the hook sells the mimicry).
  - *Special FX:* the triangular windows are **semi-transparent** (sky bleeds
    faintly through) — cheap, striking, and different from GLASSWING's
    full-pane transparency.
- **Palette:** `#9B4A2A` Atlas Rust (dominant) · `#5E2320` Deep Maroon
  (accent) · `#D89A54` Ochre Band · `#F3E6C8` Window Cream · `#241512`
  Snake-Tip Dark.
- **Distinctness:** the only **angular, hook-tipped** silhouette + earthy
  rust palette; its jagged outline separates it from every rounded/tailed peer.

## Rank 5 — GLASSWING  ·  `design_6`

- **Species / archetype:** Glasswing (*Greta oto*), Nymphalidae/Ithomiini —
  the transparent-winged butterfly.
- **Hero silhouette:** rounded wings that are **mostly see-through**, ringed by
  a dark border with a warm rust band — the sky itself shows through the panes,
  a genuinely novel read among opaque skins.
- **Objects + placement:**
  - *Head/antennae:* slender dark head, thin **clubbed** antennae to CROWN_Y.
  - *Body:* thin dark body — more visible than usual since the wings are clear.
  - *Wings:* rounded fore + hind with **near-transparent membrane** (very low
    alpha, faint iridescent tint), a **dark chocolate outline**, and a
    **rust-red outer margin** band that carries the 40px read.
  - *Special FX:* a whisper of iridescent tint that catches the light per frame;
    on night sky the dark border + rust margin keep it legible against the dark.
- **Palette:** `#3A2A22` Smoke Border (dominant edge) · `#B5462E` Rust Margin
  (accent) · `#C9E8DE` Iris Tint (faint, low-alpha) · `#241C18` Body Dark ·
  `#FFFFFF` Pane (very low alpha).
- **Distinctness:** the only **transparent** skin — defined by absence of
  fill; impossible to confuse with any solid-winged concept.

---

## Ranking rationale

1. **SUNSET MOTH** — the legendary flex: polychrome per-frame shimmer + fringed
   tails on obsidian is the biggest spectacle and the natural sibling to the
   dragon/phoenix tier of drama.
2. **LUNAWING** — glowing lime tails give a second, quieter showpiece with a
   killer silhouette and a built-in night-sky glow.
3. **MONARCH** — the crowd-pleaser everyone recognizes; carries on value alone,
   safest all-conditions read.
4. **ATLASWING** — the only angular outline; big, weird, and memorable via the
   snake-head tips.
5. **GLASSWING** — the clever one: transparency is a fresh trick, but it's the
   least dramatic, so it anchors the bottom.

**Strongest overall pick:** SUNSET MOTH. **Best legendary showpiece:** SUNSET
MOTH, with LUNAWING as the runner-up glow piece.

*References: Wikipedia (Luna moth / Saturniinae), butterflyidentification.com
(glasswing, peacock), Xerces Society & NWF (monarch ID), UVM structural-color
notes (iridescent swallowtail/Uraniidae).*
