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
OUT  = f"{ROOT}/docs/lives-display-v13/bent-rib-contour/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

N_RIBS = 7
# Outermost → innermost: half_width 24→12, depth 18→10
RIB_HW    = [round(24 - 12 * i / (N_RIBS - 1)) for i in range(N_RIBS)]
RIB_DEPTH = [round(18 -  8 * i / (N_RIBS - 1)) for i in range(N_RIBS)]


def _draw_rib(surf, cx, cy, half_w, depth, color, width=3):
    """Parabolic U-arc: flat at ends (cx±half_w, cy), deepest at (cx, cy+depth)."""
    pts = []
    for s in range(33):
        t = s / 32
        u = 2 * t - 1          # −1..+1
        x = round(cx + half_w * u)
        y = round(cy + depth * (1 - u * u))
        pts.append((x, y))
    pygame.draw.lines(surf, color, False, pts, width)


def draw_slot(surf, cx, cy, alive):
    rim_y = cy - 2   # rim-arc baseline at top of nest

    # Rear ribs: innermost first (TWIG_MID, 5 ribs)
    for i in range(N_RIBS - 1, 1, -1):
        _draw_rib(surf, cx, rim_y, RIB_HW[i], RIB_DEPTH[i], TWIG_MID, 3)

    # Faint horizontal contour ties near the rim
    for k in range(3):
        tie_y = rim_y + 3 + k * 3
        pygame.draw.line(surf, TWIG_DARK,
                         (cx - 16, tie_y), (cx - 10, tie_y), 1)
        pygame.draw.line(surf, TWIG_DARK,
                         (cx + 10, tie_y), (cx + 16, tie_y), 1)

    # Bird blit (alive only)
    if alive:
        surf.blit(_bird, (cx - _iw // 2, cy - _ih // 2))

    # Front 2 widest ribs (TWIG_BRIGHT) — overlap lower bird body
    for i in range(2):
        _draw_rib(surf, cx, rim_y, RIB_HW[i], RIB_DEPTH[i], TWIG_BRIGHT, 3)

    if not alive:
        # Spent: dark hollow notch at the parabola floor
        floor_y = rim_y + RIB_DEPTH[-1]
        pygame.draw.ellipse(surf, TWIG_DARK, (cx - 9, floor_y - 2, 18, 6))


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
