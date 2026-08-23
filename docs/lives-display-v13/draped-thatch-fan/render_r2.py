import os, sys
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
import game.parrot as parrot_mod
import game.hud as hud_module
from game.scenes import App

PANEL_DARK  = (12, 8, 38)
GOLD_BRIGHT = (240, 192, 64)
TWIG_BRIGHT = (160, 110, 55)
TWIG_MID    = (110, 75, 35)
TWIG_DARK   = (70, 45, 18)
HOLLOW_COL  = (50, 35, 14)

CX       = 31
CY_ALIVE = 73
CY_SPENT = 113

_src  = parrot_mod._get_frames()[1]
_ih   = 34
_iw   = max(1, int(_src.get_width() * _ih / _src.get_height()))
_bird = pygame.transform.smoothscale(_src, (_iw, _ih))

ROOT = "/home/user/skybit"
OUT  = f"{ROOT}/docs/lives-display-v13/draped-thatch-fan/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# 12 strands (down from 20) for legible weave at icon scale
N       = 12
RIM_H   = 18   # ±18px at rim (narrowed from ±23 to clear keyline walls)
BASE_H  = 3    # ±3px at base
RIM_OFF = -3   # rim y above cy
BASE_OFF = 16  # base y below cy; bird belly sits here


def draw_slot(surf, cx, cy, alive):
    rim_y  = cy + RIM_OFF
    base_y = cy + BASE_OFF

    # Bird in alive slot is raised so head/shoulders clear the rim
    bird_y = cy - _ih//2 - 3

    rim_xs  = [round(cx - RIM_H  + 2*RIM_H  * i/(N-1)) for i in range(N)]
    base_xs = [round(cx - BASE_H + 2*BASE_H * i/(N-1)) for i in range(N)]

    def strand_color(i):
        # Alternate dark/mid for legible weave; outer edges get TWIG_DARK
        if i % 2 == 0:
            return TWIG_DARK
        return TWIG_MID

    back  = range(N // 2)
    front = range(N // 2, N)

    # Rear strands
    for i in back:
        pygame.draw.line(surf, strand_color(i),
                         (rim_xs[i], rim_y), (base_xs[i], base_y), 2)

    # Bird blit (alive only)
    if alive:
        surf.blit(_bird, (cx - _iw//2, bird_y))

    # Front strands
    for i in front:
        pygame.draw.line(surf, strand_color(i),
                         (rim_xs[i], rim_y), (base_xs[i], base_y), 2)

    # Base knot — nudged up 2px from base_y
    knot_y = base_y - 2
    pygame.draw.ellipse(surf, TWIG_DARK,   (cx - 6, knot_y - 3, 12, 8))
    pygame.draw.ellipse(surf, TWIG_BRIGHT, (cx - 5, knot_y - 2, 10, 6), 1)

    # Rim binding band — narrower (±18px), 2px stripe + bright highlight row
    pygame.draw.rect(surf, TWIG_DARK,   (cx - RIM_H, rim_y,     2*RIM_H, 2))
    pygame.draw.rect(surf, TWIG_BRIGHT, (cx - RIM_H, rim_y - 1, 2*RIM_H, 1))

    if not alive:
        # Spent: dark hollow inside the bowl (strands still present but empty)
        pygame.draw.ellipse(surf, HOLLOW_COL,
                            (cx - 12, rim_y + 6, 24, base_y - rim_y - 8))
        pygame.draw.ellipse(surf, TWIG_DARK,
                            (cx - 9, rim_y + 8, 18, base_y - rim_y - 12))


def _draw(surf, lives_remaining, lives_total, cy=106):
    pygame.draw.rect(surf, PANEL_DARK,  (2, 57, 58, 80), border_radius=5)
    pygame.draw.rect(surf, GOLD_BRIGHT, (2, 57, 58, 80), width=1, border_radius=5)
    draw_slot(surf, CX, CY_ALIVE, True)
    draw_slot(surf, CX, CY_SPENT, False)


hud_module._draw_pip_lives_row = _draw
hud_module._PIP_ICON_ALIVE = None
hud_module._PIP_ICON_SPENT = None

app = App()
app._start_play()
app.world.lives_remaining = 1
app._render()
pygame.image.save(app.screen, OUT)
print(f"Saved: {OUT}")

from PIL import Image
img   = Image.open(OUT)
pix   = img.load()
count = sum(1 for y in range(58, 92) for x in range(0, 63)
            if pix[x, y][0] > 150 and pix[x, y][1] < 110)
print(f"Bird-red pixels: {count} (need >20)")
assert count > 20, f"FAIL: only {count} red pixels"
print("PASS")
