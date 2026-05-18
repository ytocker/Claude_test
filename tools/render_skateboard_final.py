"""Render the FINAL SKATEBOARD activation mockup.

Selected after 4 iterations: V4.3 (tilted SKATEBOARD! caption on red
plate, matching POW!'s lean), with the halftone Ben-Day dots removed
per user feedback ("remove tiny yellow circles").

Final composition:
  • 14-spike yellow starburst behind Pip with inner red ring
  • 4-corner ink speed slashes
  • SKATEBOARD! gradient caption on red plate, tilted +5°
  • Tilted POW! badge upper-right
  • Pip wearing his helmet + skateboard

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_skateboard_final.py
"""

import math
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

from game.config import W
from tools.render_skateboard_variants import render_base, _gradient_text
from tools.render_skateboard_variants_iter4 import (
    _v2_starburst, _v2_corner_slashes, _v2_pow_badge,
    INK, PLATE_RED,
)


def render_final(base, bird):
    scene = base.copy()
    cx, cy = int(bird.x), int(bird.y)
    rng = random.Random(22)

    _v2_starburst(scene, cx, cy, rng)
    _v2_corner_slashes(scene, cx, cy)   # halftone dots intentionally removed
    bird.draw(scene, 0, 0)

    # Tilted SKATEBOARD! caption on red plate (V4.3 treatment).
    txt = _gradient_text("SKATEBOARD!", 42,
                         top_col=(255, 255, 110),
                         bot_col=(255, 180,  10),
                         outline=INK, outline_w=5)
    bw, bh = txt.get_width() + 30, txt.get_height() + 18
    composite = pygame.Surface((bw + 12, bh + 12), pygame.SRCALPHA)
    cx_c = composite.get_width() // 2
    cy_c = composite.get_height() // 2
    plate_rect = pygame.Rect(0, 0, bw, bh)
    plate_rect.center = (cx_c + 4, cy_c + 4)
    pygame.draw.rect(composite, PLATE_RED, plate_rect, border_radius=10)
    pygame.draw.rect(composite, INK, plate_rect, 4, border_radius=10)
    composite.blit(txt, txt.get_rect(center=(cx_c, cy_c)).topleft)
    rotated = pygame.transform.rotate(composite, 5)
    scene.blit(rotated, rotated.get_rect(center=(W // 2, 75)))

    _v2_pow_badge(scene)
    return scene


def main() -> int:
    out_dir = os.path.join(_REPO, "docs", "screenshots",
                           "skateboard_variants", "final")
    os.makedirs(out_dir, exist_ok=True)
    base, bird = render_base()
    frame = render_final(base, bird)
    out_path = os.path.join(out_dir, "chosen.png")
    pygame.image.save(frame, out_path)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
