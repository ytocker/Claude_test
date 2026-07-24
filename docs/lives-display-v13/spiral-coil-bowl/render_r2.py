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
TWIG_RIM    = (185, 135, 75)  # lifted bright for rim highlight
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
OUT  = f"{ROOT}/docs/lives-display-v13/spiral-coil-bowl/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# 7 coils: top (widest) to bottom (narrowest), 4px vertical spacing
N_COILS  = 7
COIL_H   = 5    # ellipse arc height per coil
COIL_DY  = 4    # vertical spacing between coil centres

def _coil_rect(cx, cy_coil, hw):
    return (cx - hw, cy_coil - COIL_H//2, 2*hw, COIL_H)


def draw_slot(surf, cx, cy, alive):
    # Coil centres from top-rim downward; widest at top
    top_y = cy - 2
    coil_ys  = [top_y + i * COIL_DY for i in range(N_COILS)]
    coil_hws = [round(23 - 13 * i / (N_COILS - 1)) for i in range(N_COILS)]

    # Step 1: back/upper half of ALL coils
    for i in range(N_COILS):
        col = TWIG_RIM if i == 0 else TWIG_BRIGHT if i == 1 else TWIG_MID
        rect = _coil_rect(cx, coil_ys[i], coil_hws[i])
        pygame.draw.arc(surf, col, rect, 0, math.pi, 3)
        # Bright top-edge highlight
        pygame.draw.arc(surf, TWIG_RIM if i <= 1 else TWIG_BRIGHT, rect, math.pi*0.2, math.pi*0.8, 1)

    # Step 2: bird blit (alive slot, raised 5px so head clears rim)
    if alive:
        surf.blit(_bird, (cx - _iw//2, cy - _ih//2 - 5))

    # Step 3: front/lower half of BOTTOM 3 coils only (narrow base)
    for i in range(N_COILS - 3, N_COILS):
        rect = _coil_rect(cx, coil_ys[i], coil_hws[i])
        pygame.draw.arc(surf, TWIG_MID, rect, math.pi, 2*math.pi, 3)
        # Dark lower shadow on front arcs
        pygame.draw.arc(surf, TWIG_DARK, rect, math.pi*1.2, math.pi*1.8, 1)

    # Step 4: spent hollow or alive rim ticks
    if not alive:
        # Dark hollow ellipse drawn OVER interior — clearly empty
        mid_coil_hw = coil_hws[N_COILS // 2] - 4
        mid_coil_y  = coil_ys[N_COILS // 2]
        pygame.draw.ellipse(surf, HOLLOW_COL,
                            (cx - mid_coil_hw, mid_coil_y - 3, 2*mid_coil_hw, 10))
        pygame.draw.ellipse(surf, TWIG_DARK,
                            (cx - mid_coil_hw + 2, mid_coil_y - 1, 2*mid_coil_hw - 4, 6))
    else:
        # 3 diagonal ticks on rim band
        for k in range(3):
            tx = cx - 12 + k * 12
            pygame.draw.line(surf, TWIG_DARK, (tx, top_y), (tx + 4, top_y + 3), 1)


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
