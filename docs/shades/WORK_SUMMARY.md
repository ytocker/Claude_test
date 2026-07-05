# Shades On-Pip Seating Fix — Work Summary

**Branch:** `v5_store_shades`  
**Scope:** All 11 drawn eyewear styles (`game/shades_*.py`) + shared in-game anchor (`game/glasses_skins.py`)

---

## Problem

Several shades styles blocked Pip's beak or sat unnaturally when worn in-game. The root cause: the compositor (`store_skins._compose`) blits the full bare parrot (beak included) first, then calls `paint_fn` — so shades always paint *on top of* the beak. Any lens art extending forward (x > ~52) and downward (y ≥ 41) in composite space lands on the beak.

Worst offenders: 3D GLASSES, PIXEL, SKI GOGGLES, CYBER VISOR (very high overlap); MONOCLE, STAR, WHITE RETRO (moderate).

---

## What Changed

### Round 1 — Beak clearance (commit `6b9482b`)

`graphics-designer` repositioned all 11 `draw_shades` functions so lenses sat above/behind the beak. Art-director verdict: `ITERATE` — monocle gold ring was fusing with the orange beak; round/heart lenses could tighten.

### Round 2 — Natural forward seat (commit `26fda7a`)

User feedback overrode R1: glasses pulled too far back. Real sunglasses should *lap the beak base* slightly — beak tip and hook stay visible, near lens grazes/overlaps the beak base. Designer nudged all 11 styles forward to achieve this natural overlap, plus applied the monocle fix:

- **Monocle**: added a dark arc on the beak-facing edge of the gold ring to read as glass-over-eye rather than a gold blob; added a visible pupil inside the lens.
- All other styles: proportional forward nudge via `eye_w` multipliers in each `draw_shades`.

Files changed: all 11 `game/shades_*.py`, 67 insertions / 50 deletions.

### Rightward seat nudge — cx 51 → 53 → 55

After R2 the user asked all styles to move further right (toward the beak). The shared in-game anchor `_EYE_CX` in `game/glasses_skins.py` controls all 11 styles without touching any `draw_shades`. Steps:

1. `_shades_nudge_compare.py` — before/after at +2 px (cx 51 → 53). Written to `docs/shades/nudge_right.png`.
2. `_shades_nudge_options.py` — option strip at cx = 53, 55, 57, 59. Written to `docs/shades/nudge_options.png`.
3. User picked **cx = 55**. Changed `_EYE_CX, _EYE_CY = 55, 40` (commit `7a22a60`).

Product-shot ICONs are unaffected — they use their own canvas center (`_ICON_CX = 110`), not `_EYE_CX`.

---

## Files Modified

| File | Change |
|---|---|
| `game/glasses_skins.py` | `_EYE_CX` 51 → 55 (two increments) |
| `game/shades_nerd.py` | Proportional repositioning (R1 + R2) |
| `game/shades_round.py` | Proportional repositioning (R1 + R2) |
| `game/shades_heart.py` | Proportional repositioning (R1 + R2) |
| `game/shades_star.py` | Proportional repositioning (R1 + R2) |
| `game/shades_black.py` | Proportional repositioning (R1 + R2) |
| `game/shades_white.py` | Proportional repositioning (R1 + R2) |
| `game/shades_3d.py` | Proportional repositioning + span reduction (R1 + R2) |
| `game/shades_pixel.py` | Proportional repositioning + forward block trim (R1 + R2) |
| `game/shades_ski.py` | Proportional repositioning + span reduction (R1 + R2) |
| `game/shades_monocle.py` | Repositioning + dark beak-edge arc + pupil (R1 + R2) |
| `game/shades_cyber.py` | Proportional repositioning + rake reduction (R1 + R2) |
| `.claude/skills/item-design/SKILL.md` | Design loop cap: ≤3 designer/≤2 critic → ≤2 designer/≤1 critic |

---

## Files Added

| File | Description |
|---|---|
| `docs/shades/round_2.png` | Before/after review sheet: OLD (R0 baseline, cx=51) vs NEW (R2, cx=55) for all 11 styles + bare-eyed reference |
| `docs/shades/nudge_right.png` | Before/after of +2 px rightward nudge (cx 51 → 53) |
| `docs/shades/nudge_options.png` | Option strip: all 11 styles at cx = 53, 55, 57, 59 |
| `tools/_shades_round2_compare.py` | Harness that produced `round_2.png` (OLD via `SK_OLD_SHADES` env var) |
| `tools/_shades_nudge_compare.py` | Harness that produced `nudge_right.png` |
| `tools/_shades_nudge_options.py` | Harness that produced `nudge_options.png` |
| `tools/capture_shades_figures.py` | Produces the two store-category figures below |
| `docs/store_redesign/shades/store_overview.png` | Pixel-faithful renders of the SHADES store tab (both pages) |
| `docs/store_redesign/shades/gameplay_items.png` | All 12 shades items on Pip mid-flight in a real biome scene |

---

## Key Coordinates (reference)

```
Composite canvas:  64 × 100 px  (COMPOSITE_W × COMPOSITE_H)
Parrot blitted at: y = 20       (PARROT_DY)
In-game eye anchor: cx=55, cy=40, eye_w=22  (_EYE_CX, _EYE_CY, _EYE_W)
Beak (approx):      x ≈ 52–61, y ≈ 41–48   (in composite space)
Icon eye anchor:    cx=110, cy=72, eye_w=92  (_ICON_CX, _ICON_CY, _ICON_EYE_W)
```

---

## Verification (passing throughout)

```bash
SDL_VIDEODRIVER=dummy python -c "
import pygame; pygame.init(); pygame.display.set_mode((1,1))
from game import glasses_skins
[g(0,0) for g in glasses_skins.BUILDERS.values()]
print('ok', len(glasses_skins.ICONS), 'anchor', glasses_skins._EYE_CX)
"
# → ok 11 anchor 55

SDL_VIDEODRIVER=dummy python -m pytest tests/ -q
# → 61 passed
```
