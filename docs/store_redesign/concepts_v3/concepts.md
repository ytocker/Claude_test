# Coin Store — concepts_v3 (Night Aviary evolutions)

Five distinct **evolutions** of the chosen **NIGHT AVIARY** look. Every concept
keeps the Night Aviary core — a deep night world, a round **glass-cabochon**
thumbnail (the macaw/skin under domed glass), a faceted rarity **gem**, the
warm-gold **coin + balance capsule**, the unified **chip**, and the
colourblind-safe **4-tier + mystery** rarity language — and changes only the
**material / motif / palette-accent** so they read as five different luxe night
jewel-boxes.

Sheet: `docs/store_redesign/concepts_v3/concepts.png` (5 columns; each stacks the
full 360×640 STORE screen, the BUY-CONFIRMATION modal, and a 2–3 card DETAIL
zoom). Real catalog items + real procedural thumbnails
(`parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid,1,0.0)`), rarity from
`store_catalog.rarity` + `store_catalog.is_secret`.

## How the 8 layout defects were fixed (applies to all five)

The card was rebuilt as a **strict three-band tile** in `render.Concept`, so
geometry is shared and concepts only paint material into fixed slots:

| # | Defect | Fix |
|---|--------|-----|
| 1 | NAME on top of the cabochon | Disc spans `y+11..y+55`; NAME band centred at `y+73` — an 18px clear lane **below** the disc. Three separated bands: cabochon / name / chip. |
| 2 | Price chip touching the name | Chip band centred at `y+92` (chip h=20 → top at `y+82`), 9px clear of the name baseline. |
| 3 | Corner gem crowding disc/bezel | Gem seated at `(right-15, y+15)`, `r=7` — fully inside the corner with margin, never over the disc or the rim. |
| 4 | Equipped chip + gold ring fighting the name | EQUIPPED chip stays in the price-chip band; the gold ring traces the **bezel only** (`_equipped_ring`) and never reaches the name lane. |
| 5 | Balance coin overlapping digits / title | Balance capsule sized with a dedicated left coin cell + a 12px gap before the digits; header runs three vertical lanes — TITLE (`y=28`) / CAPSULE (`y=66`) / TABS (`y=112`) — all above `GRID_TOP=138`. |
| 6 | Tab underline overlapping the grid | Tab strip + underline finish at `y≈125`; first card row starts at `y=138` — clear gap, even tab spacing via the auto-fit strip. |
| 7 | PAGE n/N clipping back/last row | Grid bottom `y≈575`; PAGE row `y≈589`; BACK pill `y≈618` — three separated rows. |
| 8 | Secret "?" overlapping "???" / gem | "?" drawn inside the cabochon (band A); "???" rendered in the NAME band (band B); rarity gem in its corner. All three separated. |

All draws are pure pygame (`draw`, `Surface`, `smoothscale`, `BLEND_*`) — both
build targets safe.

---

## 1. CONSTELLATION
- **Evolves from Night Aviary:** the purest evolution — same indigo jewel-box,
  but the ground becomes a **star-map** and a hairline **gold constellation
  line** threads from each card's corner gem toward the cabochon.
- **Palette:** deep indigo→violet night (`#05061A → #16164A`); warm gold accents.
- **Rarity:** pearl-violet (common) / sky-blue (rare) / amethyst (epic) /
  amber-gold (legendary); mystery = cool pearl.
- **Typography:** 28px tracked title, 14px name with auto-fit + soft shadow,
  12px tabs.
- **Signature high-end detail:** the per-card constellation thread + a hairline
  gold map-rule that separates the name lane from the chip lane.
- **Defects:** all 8 fixed (shared three-band card + header/footer lanes).

## 2. ABYSSAL
- **Evolves from Night Aviary:** the night world descends underwater —
  indigo→teal depth, caustic light shafts and drifting bioluminescent motes.
  The cabochon becomes a **lit porthole** (brass ring + bolts + aqua inner glow).
- **Palette:** `#080E28 → #0A3A4C` deep-sea gradient; pearl + **abalone**
  iridescent card rims (aqua↔violet↔pearl shimmer).
- **Rarity:** pearl (common) / aqua (rare) / violet-abalone (epic) /
  bioluminescent amber (legendary); mystery = pale pearl.
- **Typography:** aqua-tinted title gradient; pearl-white names for cool legibility.
- **Signature high-end detail:** the porthole cabochon (8 brass bolts + glow) and
  the three-stop abalone rim.
- **Defects:** all 8 fixed.

## 3. ROYAL VELVET
- **Evolves from Night Aviary:** the richest, most opulent reading — a deep
  **plum/sapphire velvet** ground with a soft radial nap sheen, and ornate
  **gold scrollwork** framing every card corner.
- **Palette:** `#1C0A2C → #0E0C32` plum-sapphire velvet; warm gold scrollwork.
- **Rarity:** orchid (common) / royal-blue (rare) / magenta (epic) /
  gold (legendary); mystery = pale orchid.
- **Typography:** warm cream-gold names; scroll flourishes flank the STORE title.
- **Signature high-end detail:** four-corner gold scrollwork + a small hanging
  tassel at the legendary tier, drawn in the safe gap between disc and name.
- **Defects:** all 8 fixed (the top-right corner is reserved for the gem; the
  other three corners carry scrollwork, so nothing crowds the gem).

## 4. MOONLIT FROST
- **Evolves from Night Aviary:** the most **minimal-luxe** — cool moonlight,
  **frosted/etched glass** cards, silver-blue + **platinum** with restrained,
  pale gold. Serene and crisp, with one soft moon glow.
- **Palette:** `#121A30 → #2C3E5E` cool night; platinum-gold accent
  (`#E2D6A8`) instead of bright gold.
- **Rarity:** frost-white (common) / ice-blue (rare) / amethyst (epic) /
  pale gold (legendary); mystery = frost.
- **Typography:** cool-white title gradient + silver names — the highest-contrast,
  calmest hierarchy of the set.
- **Signature high-end detail:** etched-hatch frost streak masked into each card
  + a crisp double etched rim and a thin frost ring around the cabochon.
- **Defects:** all 8 fixed.

## 5. CLOISONNÉ
- **Evolves from Night Aviary:** the most ornate, craft-jewelry reading — fine
  **gold cell-work** (cloisonné wire) over deep **Jingtai-blue enamel** panels,
  with gemstone inlays at the corners.
- **Palette:** `#06122C → #0A224A` peacock/Jingtai enamel blue; gold cell-work
  + a vitreous kiln-fired highlight.
- **Rarity:** white-jade (common) / peacock-blue (rare) / imperial-violet (epic) /
  amber-gold (legendary); mystery = pale jade.
- **Typography:** warm gold names on enamel; full-screen gold cell-border frame.
- **Signature high-end detail:** a petal cell-work ring framing the cabochon +
  a small turquoise **inlay gem** in the left corner (the rarity gem holds the
  right), reading as true enamel cloisonné jewellery.
- **Defects:** all 8 fixed (the cabochon cell-ring stays in the upper safe zone;
  the two corner gems are seated with margin).
