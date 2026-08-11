# Confirm-Purchase Popup — LOCKED Final Design Spec

Status: **locked, not yet ported to `game/store.py`**.
Reference renderer: `tools/_confirm_v8_premv1_hybrid2_LOCKED.py`
Reference image: `FINAL_locked.png` (RARE · EPIC · LEGENDARY, 1688×1040)

## Layout (260×442 popup, SS=2)

| Element | Position | Notes |
|---|---|---|
| Hero disc | cx=130, cy=135, r=53 | unchanged from base |
| Item name | zone-centred at y=237 | zone = disc bottom → bar top; 1 line sits at 237; 2-line block keeps centre 237 (line 1 ≈221, line 2 ≈252, spacing 1.15×line height) |
| Price bar | cx=130, cy=300, 168×34 | push-down safety: max(300, 2-line bottom + 10 + 17) — never triggers with the centred zone |
| BUY / CANCEL | cy=360, 99×42 each (B2), cx 76 / 184 | |
| Rarity banner | cy=402, w=140, `_confirm_tier_banner` drawn ABOVE the shelf | base draws it under the shelf at 402 — the port must fix that draw order |
| Bottom gems | cy=402, x 43 / 217 | unchanged, flank the banner |

## Colour system — "two-metals", silver panels

- Price bar: platinum stops `[(0.0,(240,244,252)), (0.35,(214,220,232)), (0.7,(178,186,202)), (1.0,(140,148,168))]`, rims dark `(70,78,98)` / bright `(255,255,255)`, numeral `(30,36,60)`, coin `coin_glyph` r=11 inline left of numeral (font 18)
- Bar finish (S2-clean): `chip_body_stops(..., gloss=0)` + `top_sheen(rect, m(11), m(12), peak=64)` — NO gloss ellipse
- Bolt dots at bar left+13 / right−13 (obsidian-forge style)
- BUY: panel-matched — stops `[(0.0, bar[0]), (0.4, bar[1]), (1.0, darken(bar[3], 0.9))]`, gold-free silver rims same as bar, text T3: cream `(255,248,220)`, font 14, shadow 110, keyline `(8,6,20)` kw 0.9 (identical treatment to CANCEL)
- CANCEL: charcoal-blue `[(0.0,(24,28,44)),(1.0,(12,14,26))]`, text `(140,148,170)`, CARD_RING rims
- LEGENDARY: banner keeps tier gold (bar is silver → hue families differ; no cross-hue needed)

## Background ornament — B5 `constellation-web`

- Injected immediately after the card body (behind gems/name/hero/bar)
- Deep channel `(22,24,56)` alpha 110; glint = silver `(190,200,215)` alpha 100
- 10 star nodes (4-point stars r=5) joined by an 18-edge web, sparkle crosses,
  binding outer ring r=92 centred (130, 229); side nodes at (±88, +26 from
  centre 235) reach the card flanks
- Masked to card body (x 14–246, y 131–337, rounded r=18) — never below y=337

## Provenance of each decision

hybrid-2 layout (price low / banner in shelf) → bar cy=300 over the ornament →
G2→two-metals colourway (gold-on-gold rejected) → matched BUY panel →
B2 button size → T3 text → S2-clean shine → B5 ornament (design run 2) →
zone-centred name. Option strips for every step live in this directory and
`docs/confirm_purchase_v8/premium-v1/`.
