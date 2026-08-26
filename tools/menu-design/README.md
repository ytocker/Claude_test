# Main-menu design harnesses

Offline render rigs for main-menu exploration. **Nothing here is imported by
the game** — the pygbag CI stages only `main.py`, `inject_theme.py`,
`pyproject.toml` and `game/`, so this directory never reaches the `.apk`.

| file | what it is |
|---|---|
| `render_shipped_menu.py` | Renders the live menu by driving `hud.draw_menu` exactly as `scenes.py:1682-1693` does. The reference every concept is judged against. |
| `launch_perch_start.py` | The `launch-perch` lineage. `VARIANT=A\|B\|C` selects a START placement; **B is `harbour-post`, the accepted design.** |
| `sharp_lamplit.py` | Repaint of B — warm timber staged under one light source. |
| `sharp_bleached.py` | Repaint of B — limewashed boards, figure/ground inverted. |

All honour two env vars: `PHASE` (biome phase, 0.20 = day pole, 0.75 = night
pole) and `OUT` (output path).

```
OUT=/tmp/b_day.png PHASE=0.20 VARIANT=B python3 tools/menu-design/launch_perch_start.py
```

## Why the harness composites a veil

`hud.draw_menu` blits `(6,1,21)` at alpha 110 over the whole screen before any
UI, then the star field, then `_draw_mountain_silhouette(alpha=180)`. An
earlier version of this rig substituted a hand-rolled vignette and skipped that
stack, so every figure it produced showed a sky ~80 luma brighter than the real
screen. Measured through the corrected stack: **day L106, night L20** in the UI
band. Do not remove the veil block.
