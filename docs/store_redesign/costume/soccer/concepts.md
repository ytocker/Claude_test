# Soccer Costume Concepts — Pip the Scarlet Macaw (v6 — FULL KIT, anatomy-fitted)

User confirmed THE KIT direction: jersey → shorts → socks → cleats, all four
layers visible. v6 fixes anatomy: garments follow Pip's parrot body contours
(proven jersey polygon from baseball/tennis, two-leg crotch notch in shorts,
socks centred on real foot positions, cleats matching baseball cleat approach).

Canvas 64×100; must read at ~40px tall in gameplay. Numbers map to design_1…5.
Branch: claude/stoic-noether-iedzke

## Anatomy reference (from tools/sports_candidates/design_4.py + tools/tennis_candidates/design_5.py)

- Jersey polygon (PROVEN): [(HX-13,HY+8),(HX-14,HY+18),(HX-10,HY+23),(HX+8,HY+23),(HX+11,HY+18),(HX+9,HY+8)]
- Jersey zone: y49–64 (HY+8 to HY+23). NOTHING above HY+8 (no forehead bands).
- Leg foot positions: HX-11=36 and HX-1=46 (from baseball cleats). Use these for sock/cleat centering.
- Shorts: show crotch notch between legs. Span HY+23 to HY+29, notch at HX-1 centre.
- Socks: 4px wide at x≈36 and x≈46, from HY+29 to HY+37 with a hoop at the top.
- Cleats: rect at (36-4, HY+33, 10, 5) and (46-4, HY+33, 10, 5) — matching baseball.

---

## 1. THE STRIKER

- **Jersey**: white (#F0F0F5), bold squad "9" in royal-blue at chest centre,
  diagonal shoulder sash in royal blue, 1px blue garment outline, V-collar.
- **Shorts**: royal blue (#1A3EA0) short shorts, crotch notch visible.
- **Socks**: white with red hoop at top + navy secondary hoop.
- **Cleats**: near-black with a bright orange side stripe.
- **Palette**: #F0F0F5 white · #1A3EA0 blue · #C0392B red · #1C1C24 black.

---

## 2. THE GOALKEEPER

- **Jersey**: HV neon green (#39D353), 1px dark-green garment outline, goalkeeper logo on chest.
- **Shorts**: dark charcoal (#2A2A2A) short shorts.
- **Socks**: neon green matching jersey, dark hoop.
- **Cleats**: yellow (#E8C020) — bright accent pop.
- **Hero prop (drawn LAST)**: oversized GOALKEEPER GLOVES on both wings —
  bright orange (#F57C00) padded mitts with a dark knuckle strap, each mitt ~12×10px,
  the biggest brightest shape on the sprite.
- **Palette**: #39D353 HV green · #2A2A2A charcoal · #F57C00 orange gloves · #E8C020 yellow cleats.

---

## 3. THE CAPTAIN

- **Jersey**: deep navy (#0D2048) with a white club crest patch on the left chest,
  thin white horizontal piping stripe near the collar, 1px lighter-navy outline.
- **Shorts**: same navy — dark lower-body block.
- **Socks**: white with a navy double-hoop at the top.
- **Cleats**: near-black with silver sole stripe.
- **Hero prop (drawn LAST)**: wide CAPTAIN'S ARMBAND on the near-wing arm —
  bold 5px white band at HY+20 with gold edge so it reads as a distinct ring.
- **Palette**: #0D2048 navy · #FFFFFF white · #CFB53B gold armband edge · #1C1C24 black.

---

## 4. THE REFEREE

- **Jersey**: all-black (#101010) with two thin white collar-piping lines at top of jersey,
  thin white piping down each sleeve edge.
- **Shorts**: all-black.
- **Socks**: black with a white hoop.
- **Cleats**: black with a white sole stripe.
- **Hero prop (drawn LAST)**: YELLOW CARD brandished high in the near wing —
  bright 10×14px rectangle (#F4D719) with 1px dark outline, the single brightest element.
  Whistle on a cord at the throat.
- **Palette**: #101010 black · #FFFFFF white piping · #F4D719 card yellow · #BFC4C9 silver whistle.

---

## 5. THE ULTRA FAN

- **Jersey**: bold HORIZONTAL STRIPES — 3 alternating bands of red (#C0392B) and white,
  each ~4px tall, covering the jersey zone. 1px dark outline.
- **Shorts**: deep red (#8B1E10).
- **Socks**: white with a red hoop.
- **Cleats**: near-black.
- **Head**: bobble hat on the crown (dome at CROWN_Y with a pompom).
- **Hero prop (drawn LAST)**: NECK SCARF looped once at the throat with TWO staggered
  hanging tails dropping past the shorts — one tail at HX-8, one at HX+4, staggered
  lengths (one reaches HY+32, the other HY+38). Gold/red two-tone scarf.
- **Palette**: #C0392B red · #FFFFFF white · #F4D03F gold scarf · #8B1E10 deep red.

---

### Ranking (by distinctness of silhouette)

1. **THE GOALKEEPER** — neon green + oversized orange gloves = unmistakable.
2. **THE ULTRA FAN** — horizontal stripes + waving scarf + bobble hat = loudest.
3. **THE REFEREE** — all-black + brandished yellow card = authority read.
4. **THE CAPTAIN** — bold armband + navy block = clean, classic authority.
5. **THE STRIKER** — white jersey + diagonal sash + squad number = most kit-like.
