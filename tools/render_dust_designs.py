"""Render 5 candidate MAGIC-DUST poof designs (based on the white
granular poof) — each more colourful and with many more particles —
so we can pick one for the genie appear / vanish / offer-vanish.

Output: docs/screenshots/genie_offers/dust_designs.png
        — 5 full-res frames side by side, dust burst centred.

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_dust_designs
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import random
import pygame
pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H
from game.entities import PoofGrain
from tools.render_genie_sizes import render_world, setup_world

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie_offers")
os.makedirs(OUT_DIR, exist_ok=True)

CX, CY = 180, 300

# Each design: (label, palette, count, size_choices, speed_max).
# All use far more particles than the live ~180 and a colourful palette.
DESIGNS = [
    ("1  Pastel sparkle",
     [(255, 255, 255), (255, 255, 255), (255, 210, 225),
      (210, 245, 230), (205, 230, 255), (255, 245, 200)],
     420, (1, 1, 1, 2), 205),
    ("2  Gold magic",
     [(255, 255, 255), (255, 245, 215), (255, 225, 150),
      (255, 200, 95), (255, 250, 230)],
     430, (1, 1, 1, 2), 200),
    ("3  Arcane violet/cyan",
     [(255, 255, 255), (200, 180, 255), (165, 135, 255),
      (140, 220, 255), (220, 200, 255), (255, 200, 240)],
     450, (1, 1, 1, 2), 210),
    ("4  Rainbow confetti",
     [(255, 180, 190), (255, 225, 170), (255, 250, 180),
      (190, 240, 200), (180, 225, 255), (215, 190, 255), (255, 255, 255)],
     450, (1, 1, 2, 2), 215),
    ("5  Genie gold+violet",
     [(255, 255, 255), (255, 235, 180), (255, 215, 120),
      (210, 185, 255), (175, 150, 255)],
     470, (1, 1, 1, 2), 205),
]


def spawn_dust(w, x, y, palette, n, sizes, vmax):
    for _ in range(n):
        ang = random.uniform(0, math.tau)
        sp  = random.uniform(10, vmax) * math.sqrt(random.random())
        vx  = math.cos(ang) * sp
        vy  = math.sin(ang) * sp - random.uniform(6, 40)
        life = random.uniform(0.40, 0.90)
        size = random.choice(sizes)
        w.particles.append(
            PoofGrain(x, y, vx, vy, life, size, random.choice(palette)))


def _label(surf, text):
    f = pygame.font.SysFont("Arial", 15, bold=True)
    t = f.render(text, True, (255, 255, 255))
    bg = pygame.Surface((t.get_width() + 14, t.get_height() + 8),
                        pygame.SRCALPHA)
    bg.fill((0, 0, 0, 175))
    surf.blit(bg, (6, H - 32))
    surf.blit(t, (13, H - 28))


def render_design(label, palette, n, sizes, vmax):
    w = setup_world()
    spawn_dust(w, CX, CY, palette, n, sizes, vmax)
    for _ in range(8):                 # bloom to mid-burst
        for p in w.particles:
            p.update(1 / 60.0)
    s = pygame.Surface((W, H))
    render_world(w, s)
    _label(s, label)
    return s


def main():
    random.seed(5)
    frames = [render_design(*d) for d in DESIGNS]
    margin = 12
    cols = len(frames)
    sheet = pygame.Surface((W * cols + margin * (cols + 1), H + margin * 2))
    sheet.fill((20, 22, 30))
    for i, fr in enumerate(frames):       # full-res so the fine dust stays crisp
        sheet.blit(fr, (margin + i * (W + margin), margin))
    out = os.path.join(OUT_DIR, "dust_designs.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
