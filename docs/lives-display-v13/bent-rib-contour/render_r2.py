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
HOLLOW_COL  = (50, 35, 14)

CX       = 31
CY_ALIVE = 73
CY_SPENT = 113

_src  = parrot_mod._get_frames()[1]
_ih   = 34
_iw   = max(1, int(_src.get_width() * _ih / _src.get_height()))
_bird = pygame.transform.smoothscale(_src, (_iw, _ih))

ROOT = "/home/user/skybit"
OUT  = f"{ROOT}/docs/lives-display-v13/bent-rib-contour/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# 5 ribs — fewer, wider-spaced so each reads at icon scale
N_RIBS   = 5
RIB_HW   = [24, 21, 18, 15, 12]   # outermost → innermost
RIB_DEPTH= [20, 17, 14, 11,  9]


def _draw_rib(surf, cx, cy, half_w, depth, color, width=3):
    pts = []
    for s in range(33):
        t = s / 32
        u = 2*t - 1
        x = round(cx + half_w * u)
        y = round(cy + depth * (1 - u*u))
        pts.append((x, y))
    pygame.draw.lines(surf, color, False, pts, width)


def draw_slot(surf, cx, cy, alive):
    # Raise rim 5px so walls flank the bird's midline
    rim_y = cy - 7

    if alive:
        # Rear ribs 5→3 (TWIG_MID), drawn first
        for i in range(N_RIBS - 1, 1, -1):
            _draw_rib(surf, cx, rim_y, RIB_HW[i], RIB_DEPTH[i], TWIG_MID, 3)

        # Clean horizontal rim-line (replaces scattered ties)
        pygame.draw.line(surf, TWIG_DARK, (cx - RIB_HW[0], rim_y + 1), (cx + RIB_HW[0], rim_y + 1), 1)

        # Bird shifted down 3px so belly meets bowl floor
        surf.blit(_bird, (cx - _iw//2, cy - _ih//2 + 3))

        # Front 2 widest ribs (TWIG_BRIGHT) overlap lower body
        for i in range(2):
            _draw_rib(surf, cx, rim_y, RIB_HW[i], RIB_DEPTH[i], TWIG_BRIGHT, 3)

    else:
        # Spent: draw ribs as before but filled interior is explicitly dark
        for i in range(N_RIBS - 1, -1, -1):
            _draw_rib(surf, cx, rim_y, RIB_HW[i], RIB_DEPTH[i], TWIG_MID, 3)

        # Dark solid interior fill (clearly empty — not just bird removed)
        floor_y = rim_y + RIB_DEPTH[-1]
        hw_inner = RIB_HW[-1] - 2
        interior_pts = []
        for s in range(17):
            t = s / 16
            u = 2*t - 1
            x = round(cx + hw_inner * u)
            y = round(rim_y + RIB_DEPTH[-1] * (1 - u*u))
            interior_pts.append((x, y))
        if len(interior_pts) >= 3:
            pygame.draw.polygon(surf, HOLLOW_COL, interior_pts)
        # Crescent shadow at the floor
        pygame.draw.ellipse(surf, TWIG_DARK, (cx - 8, floor_y - 2, 16, 5))
        # Front 2 widest ribs on top of hollow
        for i in range(2):
            _draw_rib(surf, cx, rim_y, RIB_HW[i], RIB_DEPTH[i], TWIG_DARK, 3)


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
