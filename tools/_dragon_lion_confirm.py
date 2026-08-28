"""A legible, isolated confirmation render of the dragon and lion parade acts —
NOT a full game frame. The earlier full-scene screenshot was too busy to read
at a glance; this crops tight to the act itself on a plain backdrop, at high
zoom, with a baked-on label, purely so the design can be confirmed before any
further change.

    SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/_dragon_lion_confirm.py
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import biome as _biome                             # noqa: E402
from game import foreground_near_lane as _near                # noqa: E402
from tools._family_showcase import _font                      # noqa: E402

NIGHT_PHASE = 0.80  # deep festival night — matches the marquee beat's lighting
ZOOM = 4


def _render(draw_fn, label, sub, sx, crop, t):
    """Draw one act onto a plain backdrop, crop to the act, zoom, label."""
    pal = _biome.palette_for_phase(NIGHT_PHASE)
    canvas = pygame.Surface((360, 700))
    canvas.fill((20, 18, 30))  # plain dark backdrop — no sky, no street
    for _ in range(2):  # settle any slot-latch state before the real draw
        draw_fn(canvas, sx, pal, t)
    canvas.fill((20, 18, 30))
    draw_fn(canvas, sx, pal, t)

    cx0, cy0, cw, ch = crop
    crop_surf = canvas.subsurface(pygame.Rect(cx0, cy0, cw, ch)).copy()
    big = pygame.transform.scale(crop_surf, (cw * ZOOM, ch * ZOOM))

    out = pygame.Surface((big.get_width(), big.get_height() + 60))
    out.fill((12, 11, 20))
    out.blit(big, (0, 44))
    f = _font(22, bold=True)
    lf = _font(14)
    out.blit(f.render(label, True, (255, 220, 150)), (14, 8))
    out.blit(lf.render(sub, True, (200, 200, 210)), (14, 32))
    return out


def main():
    out_dir = "docs/sidewalk_overhaul/festival"
    os.makedirs(out_dir, exist_ok=True)

    # Dragon: 7-segment spine centred on sx, span 156 -> roughly sx-78..sx+78,
    # plus the flanking crowd (kids sx-80, old man sx+70) and the head/antlers
    # rising above the body. sx=180 puts the whole act inside a 360-wide canvas.
    dragon = _render(_near.perf_dragon_dance,
                      "THE DRAGON", "perf_dragon_dance — 7 carriers, segmented body",
                      sx=180, crop=(20, 470, 320, 190), t=2.0)
    pygame.image.save(dragon, os.path.join(out_dir, "dragon_confirm.png"))
    print("saved dragon_confirm.png", dragon.get_size())

    # Lion: two dancers under one costume, drummer to the right, flanking crowd.
    lion = _render(_near.perf_lion_dance,
                    "THE LION", "perf_lion_dance — 2 dancers, one costume",
                    sx=180, crop=(20, 470, 320, 190), t=1.0)
    pygame.image.save(lion, os.path.join(out_dir, "lion_confirm.png"))
    print("saved lion_confirm.png", lion.get_size())


if __name__ == "__main__":
    main()
