import os, sys, random
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
OUTER_DARK  = (55, 38, 16)   # bottom silhouette edge
HOLLOW_COL  = (50, 35, 14)

CX       = 31
CY_ALIVE = 73
CY_SPENT = 113

_src  = parrot_mod._get_frames()[1]
_ih   = 34
_iw   = max(1, int(_src.get_width() * _ih / _src.get_height()))
_bird = pygame.transform.smoothscale(_src, (_iw, _ih))

ROOT = "/home/user/skybit"
OUT  = f"{ROOT}/docs/lives-display-v13/felted-bowl-mass/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# Parabola bowl: half_w=20, depth=18, flat base 7px wide
HW    = 20
DEPTH = 18
RIM_Y_OFF = -2    # rim top above cy
BIRD_DROP  = 5    # drop bird so belly sinks into bowl
BASE_FLAT  = 7    # flat base half-width (avoids ice-cream-cone point)

rng = random.Random(42)


def _bowl_pts(cx, cy_rim, hw, depth, flat=BASE_FLAT, n=32):
    """Filled parabolic-U polygon, flat base."""
    pts = []
    for s in range(n + 1):
        t  = s / n
        u  = 2*t - 1   # -1..+1
        x  = round(cx + hw * u)
        raw_y = depth * (1 - u*u)
        # Flatten within ±flat of cx (rounded base)
        if abs(x - cx) < flat:
            raw_y = depth  # pinned to max depth
        y = round(cy_rim + raw_y)
        pts.append((x, y))
    return pts


def draw_slot(surf, cx, cy, alive):
    rim_y = cy + RIM_Y_OFF

    # Base mass polygon
    pts = _bowl_pts(cx, rim_y, HW, DEPTH)
    pygame.draw.polygon(surf, TWIG_MID, pts)

    # Interior shadow crescent (back inner wall)
    inner_pts = _bowl_pts(cx, rim_y + 3, HW - 5, DEPTH - 4, flat=4)
    if len(inner_pts) >= 3:
        pygame.draw.polygon(surf, TWIG_DARK, inner_pts)

    # Stipple texture — ~70 curved specks along parabola direction
    for _ in range(70):
        rx = rng.randint(cx - HW + 2, cx + HW - 2)
        t  = (rx - cx) / HW
        base_y_at_x = rim_y + round(DEPTH * (1 - t*t))
        ry = rng.randint(max(rim_y + 2, base_y_at_x - 6), base_y_at_x)
        col = TWIG_BRIGHT if rng.random() < 0.4 else TWIG_DARK
        sz  = rng.randint(1, 2)
        # Horizontal stroke following the curvature
        pygame.draw.line(surf, col, (rx, ry), (rx + rng.randint(2, 5), ry), sz)

    if alive:
        # Bird dropped 5px so belly sinks below front lip
        surf.blit(_bird, (cx - _iw//2, cy - _ih//2 + BIRD_DROP))

        # Front rim arc — ellipse (not flat ruler line)
        pygame.draw.arc(surf, TWIG_BRIGHT,
                        (cx - HW, rim_y - 1, 2*HW, 7), 0, 3.14159, 2)
        pygame.draw.arc(surf, TWIG_DARK,
                        (cx - HW + 2, rim_y + 1, 2*HW - 4, 5), 0, 3.14159, 1)

        # Bottom dark keyline so base reads against panel
        base_y = rim_y + DEPTH
        pygame.draw.line(surf, OUTER_DARK, (cx - BASE_FLAT, base_y), (cx + BASE_FLAT, base_y), 1)

    else:
        # Spent: same outer mass but with dark hollow pit inside
        hollow_pts = _bowl_pts(cx, rim_y + 6, HW - 6, DEPTH - 8, flat=3)
        if len(hollow_pts) >= 3:
            pygame.draw.polygon(surf, HOLLOW_COL, hollow_pts)
            # Deeper shadow at very bottom
            pygame.draw.ellipse(surf, TWIG_DARK,
                                (cx - 7, rim_y + DEPTH - 5, 14, 7))

        # Front rim arc same shape as alive slot
        pygame.draw.arc(surf, TWIG_DARK,
                        (cx - HW, rim_y - 1, 2*HW, 7), 0, 3.14159, 2)


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
