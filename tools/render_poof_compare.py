"""Side-by-side of the TWO genie cloud effects so it's clear which is
which:

  LEFT  — the lavender "wish reveal" cloud (_spawn_genie_reveal_poof):
          purple/cream/gold, fires when the 3 offers FIRST APPEAR.
  RIGHT — the white KFC poof (_spawn_poof): the same cloud Pip gets
          when KFC mode ends. Now used for the genie appear/disappear
          AND for the two unchosen offers vanishing.

Output: docs/screenshots/genie_offers/poof_compare.png

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_poof_compare
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H
from tools.render_genie_sizes import render_world, setup_world

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie_offers")
os.makedirs(OUT_DIR, exist_ok=True)

CX, CY = 180, 300        # centre the poof in open sky


def _label(surf, line1, line2):
    f1 = pygame.font.SysFont("Arial", 16, bold=True)
    f2 = pygame.font.SysFont("Arial", 13)
    t1 = f1.render(line1, True, (255, 255, 255))
    t2 = f2.render(line2, True, (230, 230, 230))
    h = t1.get_height() + t2.get_height() + 10
    bg = pygame.Surface((max(t1.get_width(), t2.get_width()) + 16, h),
                        pygame.SRCALPHA)
    bg.fill((0, 0, 0, 170))
    surf.blit(bg, (6, H - h - 8))
    surf.blit(t1, (12, H - h - 4))
    surf.blit(t2, (12, H - h - 4 + t1.get_height() + 4))


def _poof_frame(spawn_fn, line1, line2):
    """Fresh world, fire one poof at centre, bloom it, render."""
    w = setup_world()
    spawn_fn(w, CX, CY)
    for _ in range(8):                 # let the cloud expand to mid-bloom
        for p in w.particles:
            p.update(1 / 60.0)
    s = pygame.Surface((W, H))
    render_world(w, s)
    _label(s, line1, line2)
    return s


def main():
    left = _poof_frame(
        lambda w, x, y: w._spawn_genie_reveal_poof(x, y),
        "Lavender granular reveal",
        "shown when the 3 offers APPEAR")
    right = _poof_frame(
        lambda w, x, y: w._spawn_grainy_poof(x, y),
        "White granular poof",
        "genie appear/vanish + offers vanish")

    margin = 12
    sheet = pygame.Surface((W * 2 + margin * 3, H + margin * 2))
    sheet.fill((20, 22, 30))
    sheet.blit(left, (margin, margin))
    sheet.blit(right, (margin * 2 + W, margin))
    out = os.path.join(OUT_DIR, "poof_compare.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
