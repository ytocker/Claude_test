"""Render the NEW shrink mushroom pickup in a live gameplay scene so
reviewers can see how the V5-pancake design reads next to pillars,
ground, sky, and Pip — i.e. in the actual context where the player
will see it.

Run headless:

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_shrink_in_world.py

Writes docs/shrink_icon_variants/in_world_preview.png.
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))

from game import biome
from game.config import W, H, GROUND_Y, BIRD_X
from game.draw import draw_mountains, draw_ground
from game.entities import Bird, Coin, Pipe, PowerUp
from game.pillar_variants import _VARIANTS, VARIANT_COUNT, _paint_stone


def _scene():
    pal = biome.palette_for_phase(0.05)
    surf = pygame.Surface((W, H)).convert()
    top, mid, bot = pal["sky_top"], pal["sky_mid"], pal["sky_bot"]
    for y in range(H):
        if y < H * 0.45:
            t = y / (H * 0.45)
            c = tuple(int(top[i] + (mid[i] - top[i]) * t) for i in range(3))
        else:
            t = (y - H * 0.45) / (H * 0.55)
            c = tuple(int(mid[i] + (bot[i] - mid[i]) * t) for i in range(3))
        pygame.draw.line(surf, c, (0, y), (W, y))
    draw_mountains(surf, scroll=120.0, ground_y=GROUND_Y, w=W)
    draw_ground(surf, ground_y=GROUND_Y, w=W, h=H, scroll=120.0)

    pipe_a = Pipe(x=200.0, gap_y=H * 0.48, gap_h=170.0)
    pipe_b = Pipe(x=320.0, gap_y=H * 0.40, gap_h=160.0)
    pipe_a.seed = 7 * VARIANT_COUNT + 2
    pipe_b.seed = 11 * VARIANT_COUNT + 4
    for p in (pipe_a, pipe_b):
        top_sil, bot_sil, decorate = _VARIANTS[p.seed % VARIANT_COUNT]
        _paint_stone(surf, p.top_rect, top_sil, pal, p.seed)
        _paint_stone(surf, p.bot_rect, bot_sil, pal, p.seed + 1)
        decorate(surf, p.top_rect, p.bot_rect, pal, p.seed)

    Coin(x=260.0, y=H * 0.44).draw(surf)
    Coin(x=290.0, y=H * 0.40).draw(surf)

    # The pickup itself — drawn via the actual game render path so the
    # screenshot matches gameplay frame-for-frame.
    shrink = PowerUp(x=150.0, y=H * 0.42, kind="shrink")
    shrink.pulse = 1.2
    shrink.draw(surf)

    # Bird at full size — the player hasn't picked it up yet.
    bird = Bird()
    bird.x, bird.y = BIRD_X, H * 0.52
    bird.frame_t = 0.4
    bird.draw(surf)
    return surf


def main():
    out_dir = os.path.join(_REPO, "docs", "shrink_icon_variants")
    os.makedirs(out_dir, exist_ok=True)
    scene = _scene()
    path = os.path.join(out_dir, "in_world_preview.png")
    pygame.image.save(scene, path)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
