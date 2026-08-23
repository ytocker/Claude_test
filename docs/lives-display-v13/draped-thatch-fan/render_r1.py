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

CX       = 31
CY_ALIVE = 73
CY_SPENT = 113

_src  = parrot_mod._get_frames()[1]
_ih   = 34
_iw   = max(1, int(_src.get_width() * _ih / _src.get_height()))
_bird = pygame.transform.smoothscale(_src, (_iw, _ih))

ROOT = "/home/user/skybit"
OUT  = f"{ROOT}/docs/lives-display-v13/draped-thatch-fan/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

N       = 20
RIM_H   = 23   # ±23px at rim
BASE_H  = 3    # ±3px at base (tight knot)
RIM_OFF = -3   # rim y offset from cy
BASE_OFF = 18  # base y offset from cy


def draw_slot(surf, cx, cy, alive):
    rim_y  = cy + RIM_OFF
    base_y = cy + BASE_OFF

    rim_xs  = [round(cx - RIM_H  + 2 * RIM_H  * i / (N - 1)) for i in range(N)]
    base_xs = [round(cx - BASE_H + 2 * BASE_H * i / (N - 1)) for i in range(N)]

    def strand_color(i):
        # Outer strands (i near 0 or N-1) are TWIG_DARK; center TWIG_MID
        t = abs(i - (N - 1) / 2) / ((N - 1) / 2)
        return TWIG_DARK if t > 0.65 else TWIG_MID

    back  = range(N // 2)
    front = range(N // 2, N)

    # Rear strands
    for i in back:
        pygame.draw.line(surf, strand_color(i),
                         (rim_xs[i], rim_y), (base_xs[i], base_y), 2)

    # Bird blit (alive only)
    if alive:
        surf.blit(_bird, (cx - _iw // 2, cy - _ih // 2))

    # Front strands (over bird's lower body)
    for i in front:
        pygame.draw.line(surf, strand_color(i),
                         (rim_xs[i], rim_y), (base_xs[i], base_y), 2)

    # Base knot — distinct TWIG_DARK oval where strands converge
    pygame.draw.ellipse(surf, TWIG_DARK,   (cx - 6, base_y - 4, 12, 8))
    pygame.draw.ellipse(surf, TWIG_BRIGHT, (cx - 5, base_y - 3, 10, 6), 1)

    # Rim binding band — bold 3px horizontal TWIG_DARK stripe
    pygame.draw.rect(surf, TWIG_DARK,
                     (cx - RIM_H, rim_y - 1, 2 * RIM_H, 3))

    if not alive:
        # Spent: hollow at base
        pygame.draw.ellipse(surf, (50, 35, 14),
                            (cx - 9, base_y - 3, 18, 7))


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
