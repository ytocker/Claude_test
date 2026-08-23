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
OUT  = f"{ROOT}/docs/lives-display-v13/radial-splay-weave/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

N_STRANDS = 18
RIM_HALF  = 23   # ±23px at rim → 46px wide cup
RIM_Y_OFF = -3   # rim top relative to cy
BASE_Y_OFF = 32  # convergence point below nest, within the 80px panel slot


def draw_slot(surf, cx, cy, alive):
    rim_y  = cy + RIM_Y_OFF
    base_y = cy + BASE_Y_OFF   # convergence (hidden, below nest body)

    # Strand rim x-positions spread across full rim width
    xs = [round(cx - RIM_HALF + 2 * RIM_HALF * i / (N_STRANDS - 1))
          for i in range(N_STRANDS)]

    back  = xs[:N_STRANDS // 2]
    front = xs[N_STRANDS // 2:]

    def _twig(rx):
        return TWIG_BRIGHT if xs.index(rx) % 3 == 0 else TWIG_MID

    # Back half of strands (drawn under bird)
    for rx in back:
        pygame.draw.line(surf, _twig(rx), (rx, rim_y), (cx, base_y), 2)

    # Bird (alive only)
    if alive:
        surf.blit(_bird, (cx - _iw // 2, cy - _ih // 2))

    # Front half of strands (overlap lower body of bird)
    for rx in front:
        pygame.draw.line(surf, _twig(rx), (rx, rim_y), (cx, base_y), 2)

    # 5 horizontal rim ticks at the cup top
    for k in range(5):
        tx = cx - 18 + k * 9
        pygame.draw.line(surf, TWIG_DARK, (tx, rim_y), (tx + 6, rim_y + 2), 2)

    if not alive:
        # Spent: dark hollow at convergence base
        pygame.draw.ellipse(surf, TWIG_DARK, (cx - 9, base_y - 3, 18, 7))


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
img  = Image.open(OUT)
pix  = img.load()
count = sum(1 for y in range(58, 92) for x in range(0, 63)
            if pix[x, y][0] > 150 and pix[x, y][1] < 110)
print(f"Bird-red pixels: {count} (need >20)")
assert count > 20, f"FAIL: only {count} red pixels"
print("PASS")
