"""felted-bowl-mass — V13 pip-lives nest, round 1.

A pure mass-silhouette solve: the nest is a SOLID filled parabolic-U
polygon (not linework), matted with a stippled twig-texture pass so it
reads as densely felted twigs rather than a woven rim of sticks. Alive
slots cradle Pip; the spent slot is the same taper hollowed out to a dark
empty cup.
"""
import os, sys, math, random

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()

import game.parrot as parrot_mod
import game.hud as hud_module
from game.scenes import App

OUT = "/home/user/skybit/docs/lives-display-v13/felted-bowl-mass/round_1.png"

PANEL_DARK   = (12, 8, 38)
GOLD_BRIGHT  = (240, 192, 64)
OUTER_SHADOW = (4, 4, 12)
# Warm sandstone-twig ramp — matches the game's earthy pillar tones so the
# nest sits inside the palette rather than reading as a foreign object.
TWIG_BRIGHT  = (160, 110, 55)
TWIG_MID     = (110, 75, 35)
TWIG_DARK    = (70, 45, 18)
HOLLOW_COL   = (50, 35, 14)

CX = 31
CY_LIST = [73, 113]

# Mid-glide pose reads clearest at icon scale; height-locked so both slots
# and the bird share one measuring stick.
_src = parrot_mod._get_frames()[1]
_ih = 34
_iw = max(1, int(_src.get_width() * _ih / _src.get_height()))
_bird = pygame.transform.smoothscale(_src, (_iw, _ih))


def _parabola_y(cy, depth, t):
    # Peaks (deepest) at the centre; rim height at both lips.
    return cy + depth * 4 * t * (1 - t)


def draw_bowl_mass(surf, cx, cy, half_w=23, depth=18, col=TWIG_MID):
    """Filled parabolic U as a single polygon — the base twig mass."""
    pts = []
    steps = 30
    for i in range(steps + 1):
        t = i / steps
        x = int(cx - half_w + 2 * half_w * t)
        y = int(_parabola_y(cy, depth, t))
        pts.append((x, y))
    pts.append((cx + half_w, cy))
    pts.append((cx - half_w, cy))
    pygame.draw.polygon(surf, col, pts)


def draw_stipple(surf, cx, cy, half_w=23, depth=18, n=150, seed=42):
    """Twig-texture flecks that thin toward the rim and follow the curve, so
    the flat fill reads as matted felted twigs rather than a paint chip."""
    rng = random.Random(seed)
    for _ in range(n):
        t = rng.random()
        y_max = int(_parabola_y(cy, depth, t))
        # Bias speck columns across the full span; jitter for a felted look.
        x = int(cx - half_w + 2 * half_w * t + rng.uniform(-2, 2))
        y = int(rng.uniform(cy + 1, y_max))
        if y <= cy or y >= y_max:
            continue
        col = TWIG_BRIGHT if rng.random() > 0.62 else TWIG_DARK
        size = 1 if rng.random() > 0.32 else 2
        surf.fill(col, (x, y, size, size))


def draw_rim_highlight(surf, cx, cy, half_w=23):
    """Sunlit top lip — a bright line along the rim reads as the caught edge."""
    pygame.draw.line(surf, TWIG_BRIGHT,
                     (cx - half_w + 1, cy), (cx + half_w - 1, cy), 2)


def draw_interior_shadow(surf, cx, cy, half_w=23):
    """Dark crescent just inside the rim hollows the cup out."""
    pygame.draw.arc(surf, TWIG_DARK,
                    (cx - half_w + 4, cy + 1, (half_w - 4) * 2, 9),
                    math.pi, 2 * math.pi, 2)


def draw_hollow(surf, cx, cy, half_w=23, depth=18):
    """Inset dark cup for the spent slot — a vertical hollow gradient inside
    the twig walls so the empty nest reads as a single cupped body."""
    inset = 3
    ih_w = half_w - inset
    for y in range(cy + 2, cy + depth):
        d = (y - cy) / depth
        # Inner parabola half-span at this row (inverted from the silhouette).
        disc = 1 - (y - cy) / max(1, depth)
        if disc <= 0:
            continue
        span = ih_w * math.sqrt(disc)
        xl = int(cx - span)
        xr = int(cx + span)
        # Darkest deep, faint warmth near the lip.
        blend = min(1.0, d * 1.3)
        col = tuple(int(HOLLOW_COL[c] + (TWIG_DARK[c] - HOLLOW_COL[c]) * (1 - blend))
                    for c in range(3))
        if xr > xl:
            surf.fill(col, (xl, y, xr - xl, 1))


def draw_slot(surf, cx, cy, alive):
    half_w, depth = 23, 18
    # Back mass + felted texture + hollowing shadow — the interior wall.
    draw_bowl_mass(surf, cx, cy, half_w, depth)
    draw_stipple(surf, cx, cy, half_w, depth)
    draw_interior_shadow(surf, cx, cy, half_w)

    if alive:
        draw_rim_highlight(surf, cx, cy, half_w)
        # Pip cradled: belly dips below the rim, head pokes above the lip.
        bx = cx - _iw // 2
        by = cy + 9 - _ih
        surf.blit(_bird, (bx, by))
        # Front rim lip drawn OVER the belly so the bird tucks into the cup.
        pygame.draw.line(surf, TWIG_BRIGHT,
                         (cx - half_w + 2, cy + 1), (cx + half_w - 2, cy + 1), 2)
        # A few front flecks lapping over the lower belly seal the illusion.
        rng = random.Random(7)
        for _ in range(18):
            t = rng.random()
            x = int(cx - half_w + 2 * half_w * t + rng.uniform(-1, 1))
            y = int(cy + rng.uniform(1, 5))
            col = TWIG_MID if rng.random() > 0.5 else TWIG_DARK
            surf.fill(col, (x, y, 1, 1))
    else:
        draw_hollow(surf, cx, cy, half_w, depth)
        draw_rim_highlight(surf, cx, cy, half_w)


def _draw(surf, lives_remaining, lives_total, cy=106):
    pygame.draw.rect(surf, OUTER_SHADOW, (1, 56, 60, 82), 1, border_radius=6)
    pygame.draw.rect(surf, PANEL_DARK,   (2, 57, 58, 80),    border_radius=5)
    pygame.draw.rect(surf, GOLD_BRIGHT,  (2, 57, 58, 80), 1, border_radius=5)
    for i, cy_s in enumerate(CY_LIST[:max(lives_total, 2)]):
        draw_slot(surf, CX, cy_s, i < lives_remaining)


hud_module._draw_pip_lives_row = _draw
hud_module._PIP_ICON_ALIVE = None
hud_module._PIP_ICON_SPENT = None

app = App()
app._start_play()
app.world.lives_remaining = 1
app._render()
pygame.image.save(app.screen, OUT)
print("saved", OUT)
