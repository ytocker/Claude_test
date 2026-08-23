import os, sys, math
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
OUT  = f"{ROOT}/docs/lives-display-v13/radial-splay-weave/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

N_STRANDS = 18
RIM_HALF  = 22   # ±22px at rim
RIM_OFF   = -3
BASE_HALF = 5    # rounded base (not sharp point)
BASE_OFF  = 14   # cy+14 — within panel for both slots


def draw_slot(surf, cx, cy, alive):
    rim_y  = cy + RIM_OFF
    base_y = cy + BASE_OFF

    rim_xs  = [round(cx - RIM_HALF  + 2*RIM_HALF  * i/(N_STRANDS-1)) for i in range(N_STRANDS)]
    base_xs = [round(cx - BASE_HALF + 2*BASE_HALF * i/(N_STRANDS-1)) for i in range(N_STRANDS)]

    lower_cut_y = cy + 6   # front strands only below here (keeps head clear)

    if alive:
        # Back strands — full height, dark to mid tone, under bird
        for i in range(N_STRANDS // 2):
            col = TWIG_BRIGHT if i % 3 == 0 else TWIG_MID
            pygame.draw.line(surf, col, (rim_xs[i], rim_y), (base_xs[i], base_y), 2)

        # Bird blit
        surf.blit(_bird, (cx - _iw//2, cy - _ih//2))

        # Front strands — lower third only; start at lower_cut_y
        for i in range(N_STRANDS // 2, N_STRANDS):
            col = TWIG_BRIGHT if (i % 3) == 0 else TWIG_MID
            # Interpolate strand position at lower_cut_y
            t = (lower_cut_y - rim_y) / max(1, base_y - rim_y)
            x_start = round(rim_xs[i] + (base_xs[i] - rim_xs[i]) * t)
            pygame.draw.line(surf, col, (x_start, lower_cut_y), (base_xs[i], base_y), 2)

        # Woven rim arc — bright, distinct cup opening
        pygame.draw.arc(surf, TWIG_BRIGHT,
                        (cx - RIM_HALF, rim_y - 1, 2*RIM_HALF, 7),
                        0, math.pi, 2)
        # Rim shadow below arc
        pygame.draw.arc(surf, TWIG_DARK,
                        (cx - RIM_HALF + 2, rim_y + 1, 2*RIM_HALF - 4, 5),
                        0, math.pi, 1)

    else:
        # Spent: shallow collapsed ring + dark hollow inside panel
        r = RIM_HALF - 4
        pygame.draw.arc(surf, TWIG_MID,
                        (cx - r, cy - 2, 2*r, 7), 0, math.pi, 2)
        pygame.draw.arc(surf, TWIG_DARK,
                        (cx - r, cy - 1, 2*r, 5), 0, math.pi, 1)
        # Dark hollow inside the ring
        pygame.draw.ellipse(surf, (50, 35, 14), (cx - 11, cy + 2, 22, 8))
        # A few drooping strands
        for k in range(5):
            rx = round(cx - 14 + 7*k)
            pygame.draw.line(surf, TWIG_DARK, (rx, cy), (cx, cy + 12), 1)


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
