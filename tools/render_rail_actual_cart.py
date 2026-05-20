"""Render the RAIL pickup-icon using the ACTUAL in-world wagon
art that Pip rides during the rail buff. The recipe is copied
verbatim from `Bird._render_wagon_body` and
`Bird._render_wagon_wheels` (`game/entities.py:1029-1091`) but
re-painted at 6x supersample so the icon has clean anti-aliased
edges matching the other late-game pickups.

Two outputs:
  * `actual_cart.png` — icon-only zoom (native 56x36 scaled 6x)
  * `actual_cart_ingame.png` — composited onto a real gameplay
    frame so the user can see the pickup-scale weight

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_rail_actual_cart.py
"""

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))

from tools.render_helmet_side_view_variants import (
    build_world, render_play_scene,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "rail_actual_cart")
os.makedirs(_OUT, exist_ok=True)


# In-world palette — verbatim from Bird._render_wagon_body /
# _render_wagon_wheels.
PINE_DK = ( 70,  45,  25)
PINE    = (135,  90,  50)
PINE_HI = (180, 130,  75)
IRON_DK = ( 40,  35,  30)
IRON    = (110, 100,  95)
IRON_HI = (180, 170, 160)

# Native footprint sized to wrap the in-game wagon snugly:
# body 42 wide + wheels sticking ~5 below the body's bottom row.
NATIVE_W = 56
NATIVE_H = 36
SS = 6


def _render_wagon_body(surf, cx, cy, S):
    """1:1 of `Bird._render_wagon_body`, with every literal pixel
    constant multiplied by S so the same shape paints at higher
    resolution. S=1 -> the in-game art; S=6 -> 6x supersample."""
    W = 42 * S
    H = 18 * S
    body_top = cy + 4 * S
    body_bot = cy + 4 * S + H
    # Outline.
    pygame.draw.rect(surf, PINE_DK,
                     pygame.Rect(cx - W // 2 - S, body_top - S,
                                 W + 2 * S, H + 2 * S))
    # Body.
    pygame.draw.rect(surf, PINE,
                     pygame.Rect(cx - W // 2, body_top, W, H))
    # Plank seams every 6 game-px.
    for i in range(1, (W // S) // 6):
        px = cx - W // 2 + i * 6 * S
        pygame.draw.line(surf, PINE_DK,
                         (px, body_top + S),
                         (px, body_bot - S), max(1, S))
        pygame.draw.line(surf, PINE_HI,
                         (px + S, body_top + S),
                         (px + S, body_bot - S), max(1, S))
    # Iron hoops — top and bottom horizontal bands.
    for band_y in (body_top + 2 * S, body_bot - 5 * S):
        pygame.draw.rect(surf, IRON_DK,
                         pygame.Rect(cx - W // 2 - S, band_y,
                                     W + 2 * S, 3 * S))
        pygame.draw.rect(surf, IRON,
                         pygame.Rect(cx - W // 2 - S, band_y + S,
                                     W + 2 * S, S))
        pygame.draw.line(surf, IRON_HI,
                         (cx - W // 2 - S, band_y),
                         (cx + W // 2 + S, band_y), max(1, S))


def _render_wagon_wheels(surf, cx, cy, S, spin=0.0):
    """1:1 of `Bird._render_wagon_wheels`, S-scaled."""
    WHEEL_R = 5 * S
    DX = 15 * S
    wheel_y = cy + 22 * S
    for dx in (-DX, DX):
        wx = cx + dx
        pygame.draw.circle(surf, IRON_DK, (wx, wheel_y), WHEEL_R)
        pygame.draw.circle(surf, IRON,    (wx, wheel_y), WHEEL_R - S)
        pygame.draw.circle(surf, PINE_DK, (wx, wheel_y), WHEEL_R - 2 * S)
        for i in range(6):
            ang = spin + (i / 6) * math.tau
            ex = wx + int(math.cos(ang) * (WHEEL_R - 2 * S))
            ey = wheel_y + int(math.sin(ang) * (WHEEL_R - 2 * S))
            pygame.draw.line(surf, PINE_DK, (wx, wheel_y),
                             (ex, ey), max(1, S))
        pygame.draw.circle(surf, IRON_DK, (wx, wheel_y), max(1, S))


def draw_actual_cart(surf, cx, cy, pulse):
    """Paint the in-game wagon at 6x SS then smoothscale-down."""
    # 6x supersample paint canvas.
    big = pygame.Surface((NATIVE_W * SS, NATIVE_H * SS),
                          pygame.SRCALPHA)
    bx = big.get_width() // 2
    # Anchor: body_top = by + 4*S, so by should be a bit above
    # centre so the wheels (at by + 22*S) fit inside the canvas.
    by = big.get_height() // 2 - int(8 * SS)
    _render_wagon_body(big, bx, by, SS)
    # Spin the wheels via pulse so the static icon hints at motion.
    spin = pulse * 0.8
    _render_wagon_wheels(big, bx, by, SS, spin=spin)
    icon = pygame.transform.smoothscale(big, (NATIVE_W, NATIVE_H))
    surf.blit(icon, icon.get_rect(center=(cx, cy)))


def main():
    # Native zoom scaled 6x for review.
    base = pygame.Surface((NATIVE_W, NATIVE_H), pygame.SRCALPHA)
    draw_actual_cart(base, NATIVE_W // 2, NATIVE_H // 2, pulse=1.6)
    zoom = pygame.transform.scale(base, (NATIVE_W * 6, NATIVE_H * 6))
    pygame.draw.rect(zoom, (255, 215, 0), zoom.get_rect(), 2)
    zoom_path = os.path.join(_OUT, "actual_cart.png")
    pygame.image.save(zoom, zoom_path)
    print(f"saved {zoom_path}")

    # In-game composite.
    world = build_world()
    frame = render_play_scene(world)
    icon_cx = int(world.bird.x) + 110
    icon_cy = int(world.bird.y)
    base_ig = pygame.Surface((NATIVE_W, NATIVE_H), pygame.SRCALPHA)
    draw_actual_cart(base_ig, NATIVE_W // 2, NATIVE_H // 2,
                     pulse=1.6)
    frame.blit(base_ig, base_ig.get_rect(center=(icon_cx, icon_cy)))
    ingame_path = os.path.join(_OUT, "actual_cart_ingame.png")
    pygame.image.save(frame, ingame_path)
    print(f"saved {ingame_path}")

    base_url = ("https://raw.githubusercontent.com/ytocker/skybit/"
                "v5_powerups/docs/screenshots/rail_actual_cart")
    print()
    print(f"{base_url}/actual_cart.png")
    print(f"{base_url}/actual_cart_ingame.png")


if __name__ == "__main__":
    main()
