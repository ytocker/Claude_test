"""Showcase all 4 picked KFC pillar variants together.

Locked-in picks across the per-design picker rounds:
  V2-bun1 Classic Side       hot dog with side buns + mustard zigzag
                             + ketchup dots (no chicken-wing accents)
  V3-stack1 Mini Flag        KFC bucket stack with a single small red
                             pennant planted in the chicken pile +
                             drumstick / wing / nuggets / popcorn
  V4-corn1 Classic Golden    golden corn-dog rod, honey-mustard drips,
                             plain wooden skewer at gap, top pillar
                             flat against the ceiling
  V5-stack1 Classic Combo    bun_top / fillet / cheese / lettuce /
                             fillet / bun_bot tower, red toothpick
                             frill at the gap, top bun flat against
                             the ceiling

Output:
  docs/kfc_pillar_variants/final_picks/v2_bun1.png
  docs/kfc_pillar_variants/final_picks/v3_stack1.png
  docs/kfc_pillar_variants/final_picks/v4_corn1.png
  docs/kfc_pillar_variants/final_picks/v5_stack1.png
  docs/kfc_pillar_variants/final_picks/compare.png       (4-column strip)
  docs/kfc_pillar_variants/final_picks/in_game_mix.png   (3 pillars, each
                                                          drawn with a
                                                          different variant
                                                          via seed % 4 -
                                                          previews the
                                                          planned in-game
                                                          random rotation)

Picker only - does NOT modify any game/ file. Once the in-game integration
ships, all picker artefacts (tools/render_v?_*_*.py + docs/kfc_pillar_variants/)
get cleaned up per the standard workflow.

Run from the repo root:

    PYTHONPATH=. python tools/render_final_picks.py
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, os.path.dirname(__file__))

from render_v2_bun_variants import draw_v2_bun1     # noqa: E402
from render_v3_stack_variants import draw_v3_stack1  # noqa: E402
from render_v4_corn_variants import draw_v4_corn1    # noqa: E402
from render_v5_stack_variants import draw_v5_stack1  # noqa: E402

from game import entities as gent  # noqa: E402
from game import pillar_variants as gpv  # noqa: E402


PICKS = [
    ('v2_bun1',   "V2-bun1 Classic Side",    draw_v2_bun1),
    ('v3_stack1', "V3-stack1 Mini Flag",     draw_v3_stack1),
    ('v4_corn1',  "V4-corn1 Classic Golden", draw_v4_corn1),
    ('v5_stack1', "V5-stack1 Classic Combo", draw_v5_stack1),
]


def _patch(fn):
    saved = [
        (gpv,  'draw_pillar_pair', gpv.draw_pillar_pair),
        (gent, 'draw_pillar_pair', gent.draw_pillar_pair),
    ]
    gpv.draw_pillar_pair = fn
    gent.draw_pillar_pair = fn
    return saved


def _restore(saved):
    for module, attr, orig in reversed(saved):
        setattr(module, attr, orig)


def _mixed(surf, top_rect, bot_rect, palette, seed):
    """seed % 4 routes each pillar to one of the 4 picked variants -
    matches the planned in-game random rotation."""
    funcs = [fn for (_, _, fn) in PICKS]
    funcs[seed % len(funcs)](surf, top_rect, bot_rect, palette, seed)


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


def _make_pillars(triplets, GAP_START, Pipe):
    pillars = []
    for x, gap_y, seed in triplets:
        p = Pipe(float(x), float(gap_y), float(GAP_START))
        p.seed = seed
        pillars.append(p)
    return pillars


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    from game.config import W, H, GAP_START
    from game.entities import Pipe
    from game import biome as _biome

    screen = pygame.display.set_mode((W, H))

    # Standard 3-pillar setup - same seeds used across all per-variant
    # pickers so the final showcase matches what you've been judging.
    pillar_setup = [(35, 300, 9), (150, 360, 13), (265, 290, 15)]
    pillars = _make_pillars(pillar_setup, GAP_START, Pipe)

    phase = 0.62
    palette = _biome.palette_for_phase(phase)

    out_dir = os.path.join("docs", "kfc_pillar_variants", "final_picks")
    os.makedirs(out_dir, exist_ok=True)

    # ---- Each pick rendered individually ----
    full_frames = {}
    for key, label, fn in PICKS:
        saved = _patch(fn)
        try:
            draw_bg(screen, phase=phase)
            for p in pillars:
                p.draw(screen, palette)
            full_frames[key] = screen.copy()
            out_path = os.path.join(out_dir, f"{key}.png")
            pygame.image.save(screen, out_path)
            print(f"saved {out_path}  ({label})")
        finally:
            _restore(saved)

    # ---- In-game mix: 3 pillars with seeds 0/1/2 → variants 0/1/2.
    # (V5-stack1 doesn't appear at seed 3 here - it shows up across the
    # full compare strip and would naturally rotate in during gameplay
    # as new pillars spawn with different seeds.)
    mix_setup = [
        (35,  300, 0),   # 0 % 4 → V2-bun1
        (150, 360, 1),   # 1 % 4 → V3-stack1
        (265, 290, 2),   # 2 % 4 → V4-corn1
    ]
    mix_pillars = _make_pillars(mix_setup, GAP_START, Pipe)
    saved = _patch(_mixed)
    try:
        draw_bg(screen, phase=phase)
        for p in mix_pillars:
            p.draw(screen, palette)
        out_path = os.path.join(out_dir, "in_game_mix_a.png")
        pygame.image.save(screen, out_path)
        print(f"saved {out_path}  (mix a - V2/V3/V4)")
    finally:
        _restore(saved)

    # Second mix frame to show V5 in context (seeds 1/2/3 → V3/V4/V5)
    mix_setup_b = [
        (35,  300, 1),   # 1 % 4 → V3-stack1
        (150, 360, 2),   # 2 % 4 → V4-corn1
        (265, 290, 3),   # 3 % 4 → V5-stack1
    ]
    mix_pillars_b = _make_pillars(mix_setup_b, GAP_START, Pipe)
    saved = _patch(_mixed)
    try:
        draw_bg(screen, phase=phase)
        for p in mix_pillars_b:
            p.draw(screen, palette)
        out_path = os.path.join(out_dir, "in_game_mix_b.png")
        pygame.image.save(screen, out_path)
        print(f"saved {out_path}  (mix b - V3/V4/V5)")
    finally:
        _restore(saved)

    # ---- 4-column compare strip ----
    crop_x, crop_y, crop_w, crop_h = 95, 50, 220, 500
    cell_w, cell_h = crop_w, crop_h
    n = len(PICKS)
    GAP, LABEL_H, PAD = 14, 30, 18
    canvas_w = cell_w * n + GAP * (n - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((230, 232, 235))
    font = pygame.font.SysFont(None, 22, bold=True)
    for i, (key, label, _) in enumerate(PICKS):
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
