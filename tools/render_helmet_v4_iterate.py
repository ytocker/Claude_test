"""Re-runnable anchor iterator for V4 (`punk_mohawk_side`).

Edit CANDIDATES below, re-run, inspect the produced contact sheet,
critique, edit again. Final pick gets committed to
game/entities.py:Bird._draw_helmet in a follow-up.

Usage:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_helmet_v4_iterate.py
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

from tools.render_helmet_side_view_variants import (
    build_world, render_zoom, _label_band,
)
from tools.render_helmet_v4_anchor_candidates import (
    make_variant_with_anchor,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_variants", "side_view_v2",
                    "v4_iterate")
os.makedirs(_OUT, exist_ok=True)


# Edit this list, re-run, look at 00_iterate.png, decide.
# (label, x_offset, y_offset, caption)
CANDIDATES = [
    ("r3_18x", 18, -20, "(+18, -20) — back"),
    ("r3_19x", 19, -20, "(+19, -20)"),
    ("r3_20x", 20, -20, "(+20, -20)"),
    ("r3_21x", 21, -20, "(+21, -20)"),
    ("r3_22x", 22, -20, "(+22, -20) — forward"),
]


def main():
    saved = []
    for label, ax, ay, caption in CANDIDATES:
        world = build_world()
        fn = make_variant_with_anchor(ax, ay)
        world.bird._draw_helmet = (
            lambda surf, cx, cy, flipped, b=world.bird, _fn=fn:
                _fn(b, surf, cx, cy, flipped)
        )
        zoom = render_zoom(world, zoom=6, crop=60)
        path = os.path.join(_OUT, f"iter_{label}.png")
        pygame.image.save(zoom, path)
        saved.append((label, caption, zoom))
        print(f"saved {path}")

    # Horizontal contact sheet for quick comparison.
    zoom_w, zoom_h = saved[0][2].get_size()
    band_h = 56
    gap = 12
    sheet_w = len(saved) * zoom_w + (len(saved) - 1) * gap + 24
    sheet_h = zoom_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, caption, zoom) in enumerate(saved):
        x = 12 + idx * (zoom_w + gap)
        y = 12
        sheet.blit(zoom, (x, y))
        band = _label_band(zoom_w, label, caption, height=band_h)
        sheet.blit(band, (x, y + zoom_h))
    sheet_path = os.path.join(_OUT, "00_iterate.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")


if __name__ == "__main__":
    main()
