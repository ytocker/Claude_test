import os, sys, math
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")
import pygame; pygame.init()
import game.parrot as parrot_mod
import game.hud as hud_module
from game.scenes import App

OUT = "/home/user/skybit/docs/lives-display-v13/spiral-coil-bowl/round_1.png"

PANEL_DARK   = (12, 8, 38)
GOLD_BRIGHT  = (240, 192, 64)
OUTER_SHADOW = (4, 4, 12)
TWIG_BRIGHT  = (160, 110, 55)
TWIG_MID     = (110, 75, 35)
TWIG_DARK    = (70, 45, 18)
HOLLOW_COL   = (50, 35, 14)

CX = 31
CY_LIST = [73, 113]

_src = parrot_mod._get_frames()[1]
_ih = 34
_iw = max(1, int(_src.get_width() * _ih / _src.get_height()))
_bird = pygame.transform.smoothscale(_src, (_iw, _ih))

# Coiled-rope basket read: concentric horizontal ellipses stacked
# bottom(narrow)-to-top(rim wide). Widths ramp monotonically so the taper is
# intrinsic to the geometry rather than faked with shading.
_N_COILS   = 9
_BASE_HALF = 10.0
_RIM_HALF  = 23.0
_COIL_DY   = 3.0    # vertical step; tight enough to weave, loose enough to read
_COIL_RY   = 3.0    # thin ellipses so each coil stays a distinct rope band


def _coils(cx, cy):
    """Rim (widest) sits ~4px above the opening centre; coils descend and
    narrow so the bowl reads as looking slightly down into a basket."""
    rim_y = cy - 4
    out = []
    for i in range(_N_COILS):
        t = i / (_N_COILS - 1)
        half = _RIM_HALF - (_RIM_HALF - _BASE_HALF) * t
        y = rim_y + i * _COIL_DY
        out.append((half, y))
    return out


def _back_wall(surf, cx, coil):
    half, y = coil
    rect = (cx - half, y - _COIL_RY, 2 * half, 2 * _COIL_RY)
    pygame.draw.arc(surf, TWIG_MID, rect, 0, math.pi, 3)
    pygame.draw.arc(surf, TWIG_BRIGHT,
                    (cx - half, y - _COIL_RY - 1, 2 * half, 2 * _COIL_RY),
                    0, math.pi, 1)


def _front_wall(surf, cx, coil):
    half, y = coil
    rect = (cx - half, y - _COIL_RY, 2 * half, 2 * _COIL_RY)
    pygame.draw.arc(surf, TWIG_MID, rect, math.pi, 2 * math.pi, 3)
    pygame.draw.arc(surf, TWIG_DARK,
                    (cx - half, y - _COIL_RY + 1, 2 * half, 2 * _COIL_RY),
                    math.pi, 2 * math.pi, 1)


def _ticks(surf, cx, coils):
    """Diagonal binding marks — only the upper 4 coils, one apiece, sides
    alternating, so the weave reads without silting at icon scale."""
    for i in range(4):
        half, y = coils[i]
        side = -1 if i % 2 == 0 else 1
        tx = cx + side * half * 0.55
        ty = y + _COIL_RY * 0.4
        pygame.draw.line(surf, TWIG_BRIGHT, (tx - 2, ty - 2), (tx + 2, ty + 2), 1)
        pygame.draw.line(surf, TWIG_DARK, (tx - 1, ty), (tx + 3, ty + 4), 1)


def draw_slot(surf, cx, cy, alive):
    coils = _coils(cx, cy)

    # Back walls first: the far rim of every coil, drawn before the bird so the
    # bird nests in front of them.
    for coil in coils:
        _back_wall(surf, cx, coil)

    if alive:
        rect = _bird.get_rect(center=(cx, cy - 3))
        surf.blit(_bird, rect.topleft)
    else:
        # Spent: an empty concave hollow — a dark ellipse at the interior floor.
        rim_half = coils[0][0]
        pygame.draw.ellipse(
            surf, HOLLOW_COL,
            (cx - rim_half * 0.62, cy - 5, rim_half * 1.24, 12))

    # Front walls over the bird / hollow: the near rim occludes the lower body
    # so the bird sits down inside the basket.
    for coil in coils:
        _front_wall(surf, cx, coil)

    _ticks(surf, cx, coils)


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

# Sanity check (printed, never viewed): bird-red pixels in the alive slot.
surf = app.screen
red = 0
for y in range(58, 92):
    for x in range(0, 63):
        r, g, b, *_ = surf.get_at((x, y))
        if r > 150 and g < 110:
            red += 1
print("bird-red pixels:", red)
