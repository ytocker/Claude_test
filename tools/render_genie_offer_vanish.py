"""Demo the genie offer mechanic: the genie conjures 3 powerups; when
Pip takes one, the other two vanish in a magical poof.

Output: docs/screenshots/genie_offers/offer_vanish.png — a 2-up sheet:
  left  = the 3 conjured offers floating ahead of Pip
  right = moment after Pip takes one — the other two poof away

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_genie_offer_vanish
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H
from game.entities import PowerUp
# Reuse the gameplay-frame painter + world setup from the size tool.
from tools.render_genie_sizes import render_world, setup_world

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie_offers")
os.makedirs(OUT_DIR, exist_ok=True)


def _label(surf, text):
    font = pygame.font.SysFont("Arial", 14, bold=True)
    txt = font.render(text, True, (255, 255, 255))
    bg = pygame.Surface((txt.get_width() + 12, txt.get_height() + 6),
                        pygame.SRCALPHA)
    bg.fill((0, 0, 0, 165))
    surf.blit(bg, (6, H - 30))
    surf.blit(txt, (12, H - 27))


def _frame(world):
    s = pygame.Surface((W, H))
    render_world(world, s)
    return s


def main():
    BIRD_Y = H * 0.42
    w = setup_world()
    w._activate_genie(PowerUp(w.bird.x, w.bird.y, kind="genie"))
    # Tick past the cast beat (1.10 s) AND let the lavender "wish
    # materialises" reveal cloud fully fade (~0.65 s life), so the
    # frames below show the offers cleanly — exactly as in real play,
    # where the player takes one a second or two after they appear.
    for _ in range(int(60 * 1.95)):
        w.bird.y = BIRD_Y; w.bird.vy = 0
        w.update(1 / 60.0)

    left = _frame(w)
    _label(left, "Genie conjures 3 offers")

    # Pip takes one → the other two vanish with the KFC transformation
    # poof (clean white cloud, no leftover reveal haze).
    offers = [p for p in w.powerups
              if getattr(p, "is_genie_offer", False) and not p.collected]
    if len(offers) >= 1:
        w._cull_genie_offers_except(offers[0])
    for _ in range(6):                     # let the poofs bloom
        w.bird.y = BIRD_Y; w.bird.vy = 0
        w.update(1 / 60.0)
    right = _frame(w)
    _label(right, "Take 1 -> other 2 poof (granular)")

    margin = 12
    sheet = pygame.Surface((W * 2 + margin * 3, H + margin * 2))
    sheet.fill((20, 22, 30))
    sheet.blit(left, (margin, margin))
    sheet.blit(right, (margin * 2 + W, margin))
    out = os.path.join(OUT_DIR, "offer_vanish.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
