"""Render the 5 V2 bun-style picker variants as full-frame gameplay shots.

For each key in V2_BUN_VARIANTS:
  - install_variant(key) monkey-patches draw_pillar_pair so all pillars
    use the chosen V2 bun treatment.
  - 3 pillars are drawn at fixed seeds + biome phase so frames are
    deterministic and only the bun treatment differs between PNGs.

Output:
  docs/kfc_pillar_variants/v2_bun/v2_bun1..v2_bun5.png
  docs/kfc_pillar_variants/v2_bun/compare.png  (5-column comparison strip)

Run from the repo root:

    PYTHONPATH=. python tools/render_v2_bun_gameplay.py
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, os.path.dirname(__file__))
from render_v2_bun_variants import install_variant, V2_BUN_VARIANTS  # noqa: E402


def draw_bg(surf, scroll=0.0, phase=0.62):
    from game.config import W, H, GROUND_Y
    from game import biome as _biome
    from game.draw import (
        get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
    )
    buckets = _biome.PHASE_BUCKETS
    bf = (phase % 1.0) * buckets
    a = int(bf) % buckets
    b = (a + 1) % buckets
    t = bf - int(bf)
    pal_a = _biome.palette_for_phase(a / buckets)
    pal_b = _biome.palette_for_phase(b / buckets)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)
    sky_a.set_alpha(None); surf.blit(sky_a, (0, 0))
    if t > 0:
        sky_b.set_alpha(int(t * 255)); surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)
    for i, (bx, by, sc, var) in enumerate(
            ((20, 90, 0.9, 0), (180, 140, 1.1, 2), (60, 220, 0.8, 3),
             (230, 60, 0.7, 1), (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(1.2 + i) * 3, sc, variant=var)
    pal = pal_a
    draw_mountains(surf, scroll, GROUND_Y, W, pal['mtn_far'], pal['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                pal['ground_top'], pal['ground_mid'], (60, 40, 25))


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    from game.config import W, H, GAP_START
    from game.entities import Pipe
    from game import biome as _biome

    screen = pygame.display.set_mode((W, H))

    pillars = []
    for x, gap_y, seed in [
        ( 35, 300,  9),
        (150, 360, 13),
        (265, 290, 15),
    ]:
        p = Pipe(float(x), float(gap_y), float(GAP_START))
        p.seed = seed
        pillars.append(p)

    phase = 0.62
    palette = _biome.palette_for_phase(phase)

    out_dir = os.path.join("docs", "kfc_pillar_variants", "v2_bun")
    os.makedirs(out_dir, exist_ok=True)

    full_frames = {}

    for key in V2_BUN_VARIANTS:
        label, _ = V2_BUN_VARIANTS[key]
        with install_variant(key):
            draw_bg(screen, phase=phase)
            for p in pillars:
                p.draw(screen, palette)
            full_frames[key] = screen.copy()
            out_path = os.path.join(out_dir, f"{key}.png")
            pygame.image.save(screen, out_path)
            print(f"saved {out_path}  ({label})")

    # ---- Comparison strip (5 columns, centre-cropped on middle pillar) ----
    crop_x, crop_y, crop_w, crop_h = 95,  50, 220, 500
    cell_w = crop_w
    cell_h = crop_h
    items = list(V2_BUN_VARIANTS.items())
    n = len(items)
    GAP = 14
    LABEL_H = 30
    PAD = 18
    canvas_w = cell_w * n + GAP * (n - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((230, 232, 235))
    font = pygame.font.SysFont(None, 22, bold=True)
    for i, (key, (label, _)) in enumerate(items):
        x = PAD + i * (cell_w + GAP)
        y = PAD
        crop = full_frames[key].subsurface(
            pygame.Rect(crop_x, crop_y, crop_w, crop_h)).copy()
        pygame.draw.rect(canvas, (60, 70, 100),
                         pygame.Rect(x - 1, y - 1, cell_w + 2, cell_h + 2),
                         width=1)
        canvas.blit(crop, (x, y))
        lbl = font.render(label, True, (30, 35, 55))
        canvas.blit(lbl, (x + (cell_w - lbl.get_width()) // 2,
                          y + cell_h + 8))
    out_path = os.path.join(out_dir, "compare.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  {canvas.get_size()}")


if __name__ == "__main__":
    sys.exit(main() or 0)
