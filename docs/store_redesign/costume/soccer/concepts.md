# Soccer Jersey Concepts — Pip the Scarlet Macaw (real-team kits)

Five globally-recognizable football-kit re-plumages for Pip's body oval. Anatomy is
LOCKED and untouched: the jersey IS the body oval re-plumaged through the palette
system; head stays macaw red (`#F03737`), wings macaw blue (`#2864FF`), beak gold
(`#FFB900`); shorts are a small ellipse below the body, socks two thin vertical
lines, cleats dark boots at the bottom. Only the jersey **visual** changes across the
five — base colour, stripe/pattern, collar, crest badge, shorts, socks.

All five are mutually distinct in base colour and/or pattern (no two plain solids, no
two identical stripe styles), and each base is collision-checked against the fixed red
head / blue wings / gold beak.

Numbers map directly to `design_1.py` … `design_5.py`.

---

## 1. LA ALBICELESTE — Argentina (national team)

- **Team inspiration:** Argentina national team — the iconic sky-blue-and-white
  vertical stripes, three World Cup stars.
- **Jersey base colour:** `#FFFFFF` white body, overlaid with sky-blue stripes.
- **Stripe / pattern:** **vertical stripes.** ~4 sky-blue (`#75AADB`) stripes on
  white, each ~5px wide at 40px scale (so roughly 4 blue + 3 white bands read cleanly
  across the oval). Bold, evenly spaced, top to bottom.
- **Collar style:** V-neck, sky-blue (`#75AADB`) trim.
- **Crest badge:** small ~5px **gold sun** — a filled gold (`#FFB900`) circle with a
  few short triangular rays (the Sol de Mayo motif), left chest. Survives downscale as
  a warm gold dot.
- **Shorts colour:** `#0B1B4D` deep navy.
- **Sock colours:** white base (`#FFFFFF`) with a single sky-blue (`#75AADB`) hoop.
- **Colour-collision check:** PASS. Sky-blue `#75AADB` is pale and desaturated,
  clearly separated from the vivid macaw wing blue `#2864FF`; the white base reads
  apart from the red head; navy shorts sit well below the gold beak.

---

## 2. CANARINHO — Brazil (national team)

- **Team inspiration:** Brazil national team — the 1970 canary-yellow shirt with
  green trim, the most recognizable colour combination in world football.
- **Jersey base colour:** `#FFCB05` canary yellow (solid).
- **Stripe / pattern:** **plain with trim panel.** No stripes — a bold green
  (`#009C3B`) collar + shoulder/sleeve edge accent (~2–3px band) frames the yellow,
  keeping the solid-yellow silhouette intact.
- **Collar style:** V-neck, green (`#009C3B`) band.
- **Crest badge:** small ~5px **green diamond/lozenge** (echoing the flag's central
  rhombus) in `#009C3B`, left chest — a clean green shape against the yellow field.
- **Shorts colour:** `#1E3A8A` royal blue.
- **Sock colours:** white base (`#FFFFFF`) with a green (`#009C3B`) hoop.
- **Colour-collision check:** PASS. Canary yellow `#FFCB05` is a cooler, lighter
  yellow than the amber gold beak `#FFB900`; the crest is deliberately **green**, not
  gold, so nothing echoes the beak. Yellow body reads strongly against red head and
  blue wings.

---

## 3. LA VECCHIA SIGNORA — Juventus (Italy, club)

- **Team inspiration:** Juventus FC — the classic bianconeri black-and-white vertical
  stripes.
- **Jersey base colour:** `#FFFFFF` white, striped with black.
- **Stripe / pattern:** **vertical stripes.** Alternating black (`#0A0A0A`) and white
  bands, each ~5px wide at 40px (≈3–4 black + 3 white across the oval). High-contrast,
  unmistakably Juve. Distinct from concept 1 by being black/white (not sky/white) and
  denser.
- **Collar style:** crew neck, black (`#0A0A0A`) band.
- **Crest badge:** small ~5px **white oval shield** with a thin black rim, left chest
  — reads as a pale patch inside the striping at 40px.
- **Shorts colour:** `#0A0A0A` black.
- **Sock colours:** black base (`#0A0A0A`) with a white (`#FFFFFF`) hoop.
- **Colour-collision check:** PASS. Pure black/white has no hue overlap with red head,
  blue wings, or gold beak. Keep the black stripes visually separated from the dark
  cleats by the shorts ellipse gap.

---

## 4. ORANJE — Netherlands (national team)

- **Team inspiration:** Netherlands national team — the bold House-of-Orange brilliant
  orange, one of the most instantly identifiable kits in football.
- **Jersey base colour:** `#F36C21` brilliant Dutch orange (solid, punchy).
- **Stripe / pattern:** **plain with a single accent.** A bold solid-orange body for
  max silhouette impact, with one thin black (`#0A0A0A`) horizontal chest band ~2px at
  40px echoing the modern Oranje trim. Its identity is the saturated orange field.
- **Collar style:** crew neck, black (`#0A0A0A`) band.
- **Crest badge:** small ~5px **black lion on a white circle** — at 40px reduces to a
  white dot with a dark core (the KNVB lion), left chest.
- **Shorts colour:** `#0A0A0A` black.
- **Sock colours:** orange base (`#F36C21`) with a black (`#0A0A0A`) hoop.
- **Colour-collision check:** PASS. Orange `#F36C21` sits between the cooler/pinker red
  head (`#F03737`) and the yellower gold beak (`#FFB900`); keep a crisp value break at
  the neck so the orange body doesn't bleed into the red head. Blue wings give strong
  contrast. Distinct base from every other concept.

---

## 5. DIE MANNSCHAFT — Germany (national team)

- **Team inspiration:** Germany national team — the classic white home shirt with
  black trim (Prussian black-and-white heritage) carrying the tricolour flash.
- **Jersey base colour:** `#F2F2F2` clean white (solid).
- **Stripe / pattern:** **diagonal sash / chest flash.** A single bold diagonal sash
  across the chest carrying the German tricolour — three thin diagonal bands black
  (`#0A0A0A`) / red (`#C8102E`) / gold (`#FFCC00`), together ~6–8px wide at 40px,
  shoulder to hip. The only **diagonal** design in the set (1 and 3 are vertical),
  giving it a unique pattern read.
- **Collar style:** V-neck, black (`#0A0A0A`) trim.
- **Crest badge:** small ~5px **black eagle mark on a white shield** — a dark glyph on
  a pale pentagon at 40px, left chest, beside the sash.
- **Shorts colour:** `#0A0A0A` black.
- **Sock colours:** white base (`#F2F2F2`) with a black (`#0A0A0A`) hoop.
- **Colour-collision check:** PASS with a note. White body separates cleanly from red
  head and blue wings. The sash's red band (`#C8102E`) is a deeper, bluer red than the
  macaw head (`#F03737`), and its gold band (`#FFCC00`) is near the beak gold — but
  both are thin diagonal accents mid-body, spatially far from head/beak, reading as
  flag flash, not confusion. Keep sash bands crisp-edged.

---

## Distinctness summary

| # | Team | Base | Pattern |
|---|------|------|---------|
| 1 | Argentina | white | sky-blue **vertical** stripes |
| 2 | Brazil | canary yellow | solid + green trim |
| 3 | Juventus | white | black **vertical** stripes |
| 4 | Netherlands | brilliant orange | solid + black band |
| 5 | Germany | white | tricolour **diagonal** sash |

Three white-ish bases are kept apart by pattern: sky-blue vertical stripes (1), black
vertical stripes (3), and a diagonal tricolour sash (5). The two solid bodies are
different hues (canary yellow 2, orange 4). Every base clears the red head, blue
wings, and gold beak.

## Sources

- [SI — Ranking the 50 Best Soccer Jerseys Of All Time](https://www.si.com/soccer/ranking-the-50-best-soccer-jerseys-of-all-time)
- [Google Arts & Culture — History of the Brazilian yellow jersey](https://artsandculture.google.com/story/history-of-the-brazilian-yellow-jersey-how-the-yellow-gold-became-brazil-s-color-museu-do-futebol/DQWBCiIxN2jqKQ?hl=en)
- [Team Color Codes — Brazil national football team](https://teamcolorcodes.com/brazil-national-football-team-color-codes/)
- [Team Color Codes — Juventus FC](https://teamcolorcodes.com/juventus-color-codes/)
- [Team Color Codes — Inter Milan](https://teamcolorcodes.com/inter-milan-color-codes/)
- [SportBible — Why the Netherlands wear orange](https://www.sportbible.com/football/football-news/fifa-world-cup/why-the-netherlands-wear-orange-flag-reason-explained-965986-20260625)
- [Footy Headlines — 2026 World Cup Kit Overview](https://www.footyheadlines.com/2025/08/2026-world-cup-kit-overview.html)
