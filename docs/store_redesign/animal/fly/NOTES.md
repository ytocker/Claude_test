# Fly skin exploration — archived

Not shipped. Kept for future reference.

## What was built

### Round 1 — five concept directions (`tools/fly_candidates/design_1..5.py`)

| ID | Name | Palette |
|----|------|---------|
| design_1 | Realistic Housefly | grey/black/iridescent |
| design_2 | Hairy Metallic | dark-green sheen |
| design_3 | Cartoon Friendly | bright teal/orange |
| design_4 | Creepy Crawler | red-eye horror |
| **design_5** | **POP FLY** | **red thorax + yellow abdomen (Lichtenstein)** |

Design 5 won the first round. Re-render: `tools/render_fly_compare.py`
→ `docs/store_redesign/animal/fly/final_comparison.png`

### Round 2 — five pop-art colour variants (`tools/fly_candidates/pop_v1..5.py`)

Design 5 used as the reference baseline. Same pop-art grammar (flat colour
blocks, 2px comic ink loop on every element, Ben-Day halftone dot fills).

| ID | Name | Palette |
|----|------|---------|
| pop_v1 | Electric Zapper | electric-blue thorax + neon-lime abdomen |
| pop_v2 | Midnight Noir | monochrome jet-black + white eyes |
| pop_v3 | Velvet Venom | hot-pink thorax + deep-purple abdomen |
| pop_v4 | Golden Royale | deep-navy thorax + rich-gold abdomen |
| pop_v5 | Cherry Bomb | chalk-white thorax + deep-red abdomen |

Re-render: `SDL_VIDEODRIVER=dummy python tools/render_pop_compare.py`
→ `docs/store_redesign/animal/fly/pop_final_comparison.png`

## Known geometry

Wing membrane: 22×16px ellipse centred at (19,16) in a 40×32 surface.
Root pivot `_WING_ROOT = (8, 16)`. Canvas pivots: right wing (31,31),
left wing (29,31). SPAN=24px — fits the 64px canvas with 9px right /
5px left margin at the most horizontal flap frame.

This was a bug fix applied late in the session: the original membrane was
36px wide (SPAN≈38px), clipping both arcs badly at the canvas edge. All
six builders (design_5 + pop_v1-v5) carry the corrected geometry.

## Concepts brief

`docs/store_redesign/animal/fly/concepts.md` — first-round directions
`docs/store_redesign/animal/fly/pop_concepts.md` — colour-variant directions
