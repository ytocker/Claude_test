"""Render full-frame gameplay screenshots of each KFC pillar sub-variant.

Round 2: 12 sub-variants (3 per design family V2/V3/V4/V5).

For each key in KFC_VARIANTS:
  - install_variant(key) monkey-patches draw_pillar_pair in BOTH
    game.pillar_variants AND game.entities so every pillar in the
    rendered scene is drawn with the chosen sub-variant.
  - 3 pillars are drawn at fixed seeds + biome phase so frames are
    deterministic and only the pillar art differs between PNGs.

Output:
  docs/kfc_pillar_variants/v2a..v5c.png  (12 full 360x640 frames)
  docs/kfc_pillar_variants/compare_v2.png  (3-column strip of V2 sub-variants)
  docs/kfc_pillar_variants/compare_v3.png
  docs/kfc_pillar_variants/compare_v4.png
  docs/kfc_pillar_variants/compare_v5.png
  docs/kfc_pillar_variants/compare_all.png  (4x3 grid of all 12 sub-variants)

Run from the repo root:

    PYTHONPATH=. python tools/render_kfc_pillar_gameplay.py
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, os.path.dirname(__file__))
from render_kfc_pillar_variants import (  # noqa: E402
    install_variant, KFC_VARIANTS, FAMILIES,
)


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


def _build_compare(frames, items, *, cols, label_lookup,
                   crop=(95, 50, 220, 500),
                   scale=1, gap=14, label_h=30, pad=18):
    """Generic side-by-side strip / grid builder.

    `frames` is a {key: pygame.Surface} map.
    `items` is a list of keys in display order.
    `cols` controls grid wrapping.
    `label_lookup(key) -> str` produces the per-cell label.
    """
    crop_x, crop_y, crop_w, crop_h = crop
    cell_w = crop_w * scale
    cell_h = crop_h * scale
    rows = (len(items) + cols - 1) // cols
    canvas_w = cell_w * cols + gap * (cols - 1) + pad * 2
    canvas_h = (cell_h + label_h) * rows + gap * (rows - 1) + pad * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((230, 232, 235))
    font = pygame.font.SysFont(None, 22, bold=True)
    for idx, key in enumerate(items):
        col = idx % cols
        row = idx // cols
        x = pad + col * (cell_w + gap)
        y = pad + row * (cell_h + label_h + gap)
        crop_surf = frames[key].subsurface(
            pygame.Rect(crop_x, crop_y, crop_w, crop_h)).copy()
        scaled = pygame.transform.scale(crop_surf, (cell_w, cell_h))
        pygame.draw.rect(canvas, (60, 70, 100),
                         pygame.Rect(x - 1, y - 1, cell_w + 2, cell_h + 2),
                         width=1)
        canvas.blit(scaled, (x, y))
        lbl = font.render(label_lookup(key), True, (30, 35, 55))
        canvas.blit(lbl, (x + (cell_w - lbl.get_width()) // 2,
                          y + cell_h + 8))
    return canvas


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

    out_dir = os.path.join("docs", "kfc_pillar_variants")
    os.makedirs(out_dir, exist_ok=True)

    full_frames = {}

    for key in KFC_VARIANTS:
        label, _ = KFC_VARIANTS[key]
        with install_variant(key):
            draw_bg(screen, phase=phase)
            for p in pillars:
                p.draw(screen, palette)
            full_frames[key] = screen.copy()
            out_path = os.path.join(out_dir, f"{key}.png")
            pygame.image.save(screen, out_path)
            print(f"saved {out_path}  ({label})")

    # ---- Per-family compare strips (3 sub-variants each, 1 row x 3 cols) ----
    for fkey, (fname, sub_keys) in FAMILIES.items():
        canvas = _build_compare(
            full_frames, sub_keys, cols=3,
            label_lookup=lambda k: KFC_VARIANTS[k][0])
        out_path = os.path.join(out_dir, f"compare_{fkey}.png")
        pygame.image.save(canvas, out_path)
        print(f"saved {out_path}  ({fname})  {canvas.get_size()}")

    # ---- Master compare grid (4 rows x 3 cols, all 12 sub-variants) -------
    all_keys = [k for fkey in ('v2', 'v3', 'v4', 'v5')
                for k in FAMILIES[fkey][1]]
    canvas = _build_compare(
        full_frames, all_keys, cols=3,
        label_lookup=lambda k: KFC_VARIANTS[k][0])
    out_path = os.path.join(out_dir, "compare_all.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  (master grid {canvas.get_size()})")


if __name__ == "__main__":
    sys.exit(main() or 0)
