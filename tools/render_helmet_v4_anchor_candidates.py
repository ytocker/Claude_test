"""Render the chosen variant 4 (`punk_mohawk_side`) at 3 candidate
anchor offsets so the user can pick how far right + up to nudge it
relative to the current (+15, -11).

Usage:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_helmet_v4_anchor_candidates.py
"""

import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, PIPE_W
from game.world import World
from game.entities import PowerUp, Pipe

# Reuse helpers + the V4 painter from the variant renderer.
from tools.render_helmet_side_view_variants import (
    _new_helm, _half_dome, _chinstrap,
    build_world, render_play_scene, render_zoom, _label_band,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_variants", "side_view_v2",
                    "v4_anchor_candidates")
os.makedirs(_OUT, exist_ok=True)


def _paint_v4(helm, hw, hh, pad, drop, s):
    """V4 punk_mohawk_side painting — copied so the file is
    self-contained against future renderer churn."""
    import math
    _half_dome(helm, hw, hh, pad, (10, 10, 18), (50, 50, 60))
    fin = [
        (pad + 3,           pad + 1),
        (pad + hw // 2 - 2, pad - 3),
        (pad + hw // 2 + 3, pad - 2),
        (pad + hw - 4,      pad + 2),
    ]
    pygame.draw.polygon(helm, (240, 240, 230), fin)
    pygame.draw.polygon(helm, (10, 10, 18), fin, 1)
    for sx in (pad + hw // 2 - 3, pad + hw // 2 + 2):
        spike = [(sx, pad - 2), (sx + 1, pad - 5), (sx + 2, pad - 2)]
        pygame.draw.polygon(helm, (240, 240, 230), spike)
        pygame.draw.polygon(helm, (10, 10, 18), spike, 1)
    pygame.draw.line(helm, (10, 10, 18),
                     (pad + hw // 2 - 2, pad + hh - 3),
                     (pad + hw // 2 + 2, pad + hh - 3), 1)
    pygame.draw.rect(helm, (200, 200, 210),
                     pygame.Rect(pad - 1, pad + hh - 1, hw + 2, 2))
    sk_w = max(3, int(5 * s))
    sk_h = max(2, int(4 * s))
    sk = pygame.Rect(0, 0, sk_w, sk_h)
    sk.center = (pad + hw // 2 - 5, pad + hh - 4)
    pygame.draw.ellipse(helm, (240, 240, 230), sk)
    pygame.draw.ellipse(helm, (10, 10, 18), sk, 1)
    _chinstrap(helm, hw, hh, pad, drop)


def make_variant_with_anchor(anchor_x, anchor_y):
    """Returns a draw function with the per-anchor offset baked in."""
    def variant(bird, surf, cx, cy, flipped):
        helm, hw, hh, pad, drop = _new_helm(bird.shrink_scale)
        _paint_v4(helm, hw, hh, pad, drop, bird.shrink_scale)
        s = bird.shrink_scale
        tilt = -bird.tilt_deg if flipped else bird.tilt_deg
        y_off = -anchor_y * s if flipped else anchor_y * s
        offset = pygame.math.Vector2(anchor_x * s, y_off).rotate(-tilt)
        rotated = pygame.transform.rotate(helm, tilt)
        if flipped:
            rotated = pygame.transform.flip(rotated, False, True)
        r = rotated.get_rect(center=(int(cx + offset.x),
                                     int(cy + offset.y)))
        surf.blit(rotated, r.topleft)
    return variant


ANCHOR_CANDIDATES = [
    ("A_small",  18, -14, "Anchor (+18, -14) — 3 px right, 3 px up"),
    ("B_medium", 20, -16, "Anchor (+20, -16) — 5 px right, 5 px up"),
    ("C_large",  22, -18, "Anchor (+22, -18) — 7 px right, 7 px up"),
]


def main():
    saved = []
    for label, ax, ay, caption in ANCHOR_CANDIDATES:
        world = build_world()
        fn = make_variant_with_anchor(ax, ay)
        world.bird._draw_helmet = (
            lambda surf, cx, cy, flipped, b=world.bird, _fn=fn:
                _fn(b, surf, cx, cy, flipped)
        )
        zoom = render_zoom(world, zoom=6, crop=60)
        path = os.path.join(_OUT, f"v4_anchor_{label}.png")
        pygame.image.save(zoom, path)
        saved.append((label, caption, zoom))
        print(f"saved {path}")

    # Contact sheet — all 3 zooms side by side with labels.
    zoom_w, zoom_h = saved[0][2].get_size()
    band_h = 56
    gap = 12
    sheet_w = 3 * zoom_w + 2 * gap + 24
    sheet_h = zoom_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, caption, zoom) in enumerate(saved):
        x = 12 + idx * (zoom_w + gap)
        y = 12
        sheet.blit(zoom, (x, y))
        band = _label_band(zoom_w, label, caption, height=band_h)
        sheet.blit(band, (x, y + zoom_h))
    sheet_path = os.path.join(_OUT, "00_anchor_compare.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/skateboard_variants/"
            "side_view_v2/v4_anchor_candidates")
    print()
    print(f"{base}/00_anchor_compare.png")
    for label, caption, _ in saved:
        print(f"{base}/v4_anchor_{label}.png  -- {caption}")


if __name__ == "__main__":
    main()
