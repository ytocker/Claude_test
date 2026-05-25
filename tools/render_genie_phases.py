"""Render the genie magic-dust effect across all FOUR phases —
  1. Genie appears   2. Powerups appear
  3. Powerups vanish  4. Genie vanishes
for the 3 shortlisted dust designs (#3 arcane, #4 rainbow, #5 genie),
so we can compare them in real context. One figure: rows = designs,
columns = phases.

Output: docs/screenshots/genie_offers/genie_phases.png

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_genie_phases
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import random
import types
import pygame
pygame.init()
pygame.display.set_mode((360, 640))

from game.config import H
from game.entities import PoofGrain, PowerUp
from tools.render_genie_sizes import render_world, setup_world

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie_offers")
os.makedirs(OUT_DIR, exist_ok=True)

W = 360

# (design tag, palette, count) for the 3 shortlisted designs.
DESIGNS = [
    ("#3 arcane",
     [(255, 255, 255), (200, 180, 255), (165, 135, 255),
      (140, 220, 255), (220, 200, 255), (255, 200, 240)], 450),
    ("#4 rainbow",
     [(255, 180, 190), (255, 225, 170), (255, 250, 180), (190, 240, 200),
      (180, 225, 255), (215, 190, 255), (255, 255, 255)], 450),
    ("#5 genie",
     [(255, 255, 255), (255, 235, 180), (255, 215, 120),
      (210, 185, 255), (175, 150, 255)], 470),
]
PHASES = ["1 genie appears", "2 powerups appear",
          "3 powerups vanish", "4 genie vanishes"]


def _patch_palette(w, palette, n):
    """Force every genie poof on this world to use `palette`/`n`."""
    def _poof(self, x, y, palette_arg=None, n_arg=None):
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            sp  = random.uniform(10, 205) * math.sqrt(random.random())
            vx  = math.cos(ang) * sp
            vy  = math.sin(ang) * sp - random.uniform(6, 40)
            life = random.uniform(0.40, 0.90)
            size = random.choice((1, 1, 1, 2))
            self.particles.append(
                PoofGrain(x, y, vx, vy, life, size, random.choice(palette)))
    w._spawn_grainy_poof = types.MethodType(_poof, w)


def _chip(surf, tag, phase):
    f1 = pygame.font.SysFont("Arial", 15, bold=True)
    f2 = pygame.font.SysFont("Arial", 13, bold=True)
    t1 = f1.render(tag, True, (255, 240, 180))
    bg = pygame.Surface((t1.get_width() + 12, t1.get_height() + 6),
                        pygame.SRCALPHA)
    bg.fill((0, 0, 0, 175)); surf.blit(bg, (6, 6)); surf.blit(t1, (12, 9))
    t2 = f2.render(phase, True, (255, 255, 255))
    bg2 = pygame.Surface((t2.get_width() + 12, t2.get_height() + 6),
                         pygame.SRCALPHA)
    bg2.fill((0, 0, 0, 175))
    surf.blit(bg2, (6, H - 28)); surf.blit(t2, (12, H - 25))


def _build_world(palette, n):
    w = setup_world()
    _patch_palette(w, palette, n)        # patch BEFORE the genie spawns
    w._activate_genie(PowerUp(w.bird.x, w.bird.y, kind="genie"))
    return w


def _tick(w, frames):
    BIRD_Y = H * 0.42
    for _ in range(frames):
        w.bird.y = BIRD_Y; w.bird.vy = 0
        w.update(1 / 60.0)


def _frame(w, tag, phase):
    s = pygame.Surface((W, H))
    render_world(w, s)
    _chip(s, tag, phase)
    return s


def render_phase(palette, n, phase_idx, tag):
    """Fresh world per phase (timings differ + the vanish-cull kills
    the genie), captured at the moment that phase's dust is fresh."""
    if phase_idx == 0:                      # genie appears
        w = _build_world(palette, n)
        _tick(w, 5)
    elif phase_idx == 1:                    # powerups appear (cast ~1.10)
        w = _build_world(palette, n)
        _tick(w, int(60 * 1.16))
    elif phase_idx == 2:                    # powerups vanish (take one)
        w = _build_world(palette, n)
        _tick(w, int(60 * 1.95))            # let the reveal dust fade
        offers = [p for p in w.powerups
                  if getattr(p, "is_genie_offer", False) and not p.collected]
        if offers:
            w._cull_genie_offers_except(offers[0])
        _tick(w, 6)
    else:                                   # genie vanishes (~2.60)
        w = _build_world(palette, n)
        _tick(w, int(60 * 2.70))
    return _frame(w, tag, PHASES[phase_idx])


def main():
    margin = 10
    cols, rows = len(PHASES), len(DESIGNS)
    sheet = pygame.Surface((W * cols + margin * (cols + 1),
                            H * rows + margin * (rows + 1)))
    sheet.fill((18, 20, 28))
    for r, (tag, palette, n) in enumerate(DESIGNS):
        random.seed(5)
        for c in range(cols):
            fr = render_phase(palette, n, c, tag)
            sheet.blit(fr, (margin + c * (W + margin),
                            margin + r * (H + margin)))
    out = os.path.join(OUT_DIR, "genie_phases.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
