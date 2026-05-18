"""Smoke-test the eased shrink transition.

Renders Pip at several points across the SHRINK_TRANSITION window so
reviewers can see the eased scale-down + scale-back-up in a single
strip image. Run headless:

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_shrink_transition_strip.py

Writes docs/shrink_pickup_variants/transition_strip.png.
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

from game.config import SHRINK_TRANSITION, SHRINK_SCALE
from game.entities import Bird

CELL_W, CELL_H = 90, 110
PAD = 6
BG = (28, 38, 60)
LBL = (220, 230, 250)

# Sample t in [0, 1] across the transition, with a few extra "after"
# frames at full SHRINK_SCALE, then a scale-back-up.
samples = [
    ("activate\nt=0.00", 0.00, True),
    ("t=0.05",  0.05, True),
    ("t=0.10",  0.10, True),
    ("t=0.15",  0.15, True),
    ("t=0.20\n(locked)", 0.20, True),
    ("expire\nt=0.00",   0.00, False),
    ("t=0.10",  0.10, False),
    ("t=0.20\n(restored)", 0.20, False),
]


def _cell(label, t, activating):
    """Render one frame: Pip after `t` seconds of update() with
    shrink_active=activating, starting from the opposite scale."""
    bird = Bird()
    bird.x, bird.y = CELL_W // 2, CELL_H // 2 + 6
    bird.frame_t = 0.4
    bird.shrink_active = activating
    bird.shrink_scale = 1.0 if activating else SHRINK_SCALE
    # Tick the bird by `t` seconds in a single update call. We feed
    # gravity_sign=0 so the bird's y position doesn't drift down across
    # the strip (we only care about the scale here).
    bird.vy = 0
    bird.update(t, gravity_sign=0)
    bird.y = CELL_H // 2 + 6                # restore after tick

    cell = pygame.Surface((CELL_W, CELL_H)).convert()
    cell.fill(BG)
    bird.draw(cell)
    font = pygame.font.SysFont(None, 14)
    for i, line in enumerate(label.split("\n")):
        txt = font.render(line, True, LBL)
        cell.blit(txt, (CELL_W // 2 - txt.get_width() // 2,
                        CELL_H - 26 + i * 12))
    return cell


def main():
    out_dir = os.path.join(_REPO, "docs", "shrink_pickup_variants")
    os.makedirs(out_dir, exist_ok=True)
    strip_w = CELL_W * len(samples) + PAD * (len(samples) + 1)
    strip = pygame.Surface((strip_w, CELL_H + PAD * 2)).convert()
    strip.fill((14, 18, 32))
    for i, (label, t, activating) in enumerate(samples):
        cell = _cell(label, t, activating)
        x = PAD + i * (CELL_W + PAD)
        strip.blit(cell, (x, PAD))
    path = os.path.join(out_dir, "transition_strip.png")
    pygame.image.save(strip, path)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
