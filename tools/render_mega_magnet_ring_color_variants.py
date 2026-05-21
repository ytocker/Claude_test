"""Render 5 MEGA MAGNET variants exploring how the RING colors
change from large (outer) to small (inner).

The regular 3-ring magnet ships with a built-in gradient:
  rfac 1.00: (255, 220, 100) — lightest gold
  rfac 0.78: (255, 195,  60) — mid gold
  rfac 0.55: (235, 165,  35) — dark gold

User: extend that "rings get lighter as they get larger" behavior
THROUGH the new outer rings (rfac 1.15 and 1.30) we added.

All five variants use the SOFTER M1-style gradient backdrop
(bell peak 0.85, falloff 0.15, alpha 72) — closer to the regular
magnet's calibration so the field doesn't feel "aggressive". Only
the per-ring colors differ.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_mega_magnet_ring_color_variants.py
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
    build_world, render_play_scene, _label_band,
)
from game.entities import PowerUp, Coin
from game.hud import HUD
from game.config import MAGNET_RADIUS


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "mega_magnet_ring_colors")
os.makedirs(_OUT, exist_ok=True)


# Softer M1-style gradient (peak 0.85, falloff 0.15, alpha 72).
def _gradient_surface(peak=0.85, falloff=0.15, alpha_mult=72,
                      size=200, glow_col=(245, 175, 40)):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size / 2
    max_r = size / 2
    for y in range(size):
        for x in range(size):
            dx = x - cx
            dy = y - cy
            d = math.sqrt(dx * dx + dy * dy)
            if d > max_r:
                continue
            inner_t = d / max_r
            bell = math.exp(-((inner_t - peak) ** 2) / falloff)
            a = int(alpha_mult * bell)
            if a > 0:
                surf.set_at((x, y), (*glow_col, a))
    return surf


_GRADIENT_CACHE = None
def gradient_cached():
    global _GRADIENT_CACHE
    if _GRADIENT_CACHE is None:
        _GRADIENT_CACHE = _gradient_surface()
    return _GRADIENT_CACHE


def render_with_ring_colors(rings, t_phase=0.6):
    import random
    random.seed(7)
    world = build_world()
    world.ready_t = 0
    world.bird.skateboard_active = False
    world.skateboard_timer = 0
    world.skateboard_caption_t = 0
    world.skateboard_caption_overlay = None
    world.skateboard_burst_surface = None
    world._activate_mega_magnet(PowerUp(0, 0, kind="mega_magnet"))
    world.coins.extend([
        Coin(world.bird.x + 120, world.bird.y - 60),
        Coin(world.bird.x - 90, world.bird.y - 40),
        Coin(world.bird.x + 80, world.bird.y + 110),
        Coin(world.bird.x - 130, world.bird.y + 80),
        Coin(world.bird.x + 160, world.bird.y + 30),
    ])
    frame = render_play_scene(world)

    t_pulse = t_phase * 5.5
    rad = int(MAGNET_RADIUS * 1.5)
    outer_r = int(rad * 1.30) + 4
    field = pygame.Surface((outer_r * 2, outer_r * 2),
                            pygame.SRCALPHA)
    lcx, lcy = outer_r, outer_r

    BREATH = 0.30
    outer_ring_amp = BREATH * 0.62
    u_outer_ring = (math.sin(t_pulse + (-0.6)) + 1) / 2
    outer_ring_factor = 1.0 - outer_ring_amp * (1.0 - u_outer_ring)
    glow_rad = rad * 1.30 * outer_ring_factor

    grad_src = gradient_cached()
    target = int(glow_rad * 2)
    scaled = pygame.transform.smoothscale(grad_src, (target, target))
    field.blit(scaled, (lcx - target // 2, lcy - target // 2))

    AA_COL = (255, 240, 180)
    for rfac, phase, alpha, width, breath_scale, ring_col in rings:
        amp = BREATH * breath_scale
        u = (math.sin(t_pulse + phase) + 1) / 2
        rr = int(rad * rfac * (1.0 - amp * (1.0 - u)))
        pygame.draw.circle(field, (*AA_COL, alpha // 3),
                           (lcx, lcy), rr + 1, width)
        pygame.draw.circle(field, (*AA_COL, alpha // 3),
                           (lcx, lcy), rr - 1, width)
        pygame.draw.circle(field, (*ring_col, alpha),
                           (lcx, lcy), rr, width)

    frame.blit(field,
                (int(world.bird.x) - lcx,
                 int(world.bird.y) - lcy))
    HUD().draw_play(frame, world, best=0)
    return frame


# Each variant: 7 ring tuples (rfac, phase, alpha, width, breath_scale, col)
# Only the COLOR (last tuple element) differs across variants.
def _ring(rfac, phase, alpha, breath_scale, col):
    w = 3 if rfac == 1.00 else 2
    return (rfac, phase, alpha, w, breath_scale, col)


VARIANTS = [
    ("C1_subtle_lighten",
     "Subtle continuation: tiny step lighter at outer halos",
     [
         _ring(1.30, -0.6, 130, 0.62, (255, 230, 130)),
         _ring(1.15, -0.3, 150, 0.78, (255, 225, 115)),
         _ring(1.00, 0.0,  180, 1.00, (255, 220, 100)),
         _ring(0.85, 0.3,  165, 0.92, (255, 210,  85)),
         _ring(0.70, 0.6,  150, 0.85, (250, 195,  65)),
         _ring(0.55, 0.9,  130, 0.78, (240, 180,  50)),
         _ring(0.40, 1.2,  110, 0.70, (225, 165,  35)),
     ]),
    ("C2_clear_lighten",
     "Clear step lighter at outer halos — hint of cream",
     [
         _ring(1.30, -0.6, 130, 0.62, (255, 245, 175)),
         _ring(1.15, -0.3, 150, 0.78, (255, 235, 140)),
         _ring(1.00, 0.0,  180, 1.00, (255, 220, 100)),
         _ring(0.85, 0.3,  165, 0.92, (255, 205,  80)),
         _ring(0.70, 0.6,  150, 0.85, (250, 190,  60)),
         _ring(0.55, 0.9,  130, 0.78, (240, 175,  45)),
         _ring(0.40, 1.2,  110, 0.70, (225, 160,  30)),
     ]),
    ("C3_cream_outer",
     "Cream-yellow at the outermost ring, deep amber at innermost",
     [
         _ring(1.30, -0.6, 130, 0.62, (255, 255, 210)),
         _ring(1.15, -0.3, 150, 0.78, (255, 245, 165)),
         _ring(1.00, 0.0,  180, 1.00, (255, 225, 115)),
         _ring(0.85, 0.3,  165, 0.92, (252, 205,  85)),
         _ring(0.70, 0.6,  150, 0.85, (245, 185,  60)),
         _ring(0.55, 0.9,  130, 0.78, (235, 165,  35)),
         _ring(0.40, 1.2,  110, 0.70, (215, 145,  15)),
     ]),
    ("C4_regular_step_extrapolated",
     "Linear extrapolation of the regular magnet's RGB step (R-10,G-25,B-32) outward",
     [
         _ring(1.30, -0.6, 130, 0.62, (255, 255, 164)),
         _ring(1.15, -0.3, 150, 0.78, (255, 245, 132)),
         _ring(1.00, 0.0,  180, 1.00, (255, 220, 100)),
         _ring(0.85, 0.3,  165, 0.92, (245, 195,  75)),
         _ring(0.70, 0.6,  150, 0.85, (235, 170,  50)),
         _ring(0.55, 0.9,  130, 0.78, (225, 145,  25)),
         _ring(0.40, 1.2,  110, 0.70, (215, 120,   0)),
     ]),
    ("C5_white_wash_outer",
     "Near-white at outermost — most dramatic outer halo brightening",
     [
         _ring(1.30, -0.6, 130, 0.62, (255, 252, 230)),
         _ring(1.15, -0.3, 150, 0.78, (255, 245, 180)),
         _ring(1.00, 0.0,  180, 1.00, (255, 225, 115)),
         _ring(0.85, 0.3,  165, 0.92, (255, 205,  85)),
         _ring(0.70, 0.6,  150, 0.85, (250, 185,  55)),
         _ring(0.55, 0.9,  130, 0.78, (235, 165,  35)),
         _ring(0.40, 1.2,  110, 0.70, (220, 150,  20)),
     ]),
]


def main():
    saved = []
    for label, caption, rings in VARIANTS:
        frame = render_with_ring_colors(rings)
        path = os.path.join(_OUT, f"{label}.png")
        pygame.image.save(frame, path)
        saved.append((label, caption, frame))
        print(f"saved {path}")

    cell_w = saved[0][2].get_width() // 2
    cell_h = saved[0][2].get_height() // 2
    band_h = 64
    gap = 12
    cols = len(saved)
    sheet_w = cols * cell_w + (cols - 1) * gap + 24
    sheet_h = cell_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, caption, frame) in enumerate(saved):
        x = 12 + idx * (cell_w + gap)
        small = pygame.transform.smoothscale(frame, (cell_w, cell_h))
        sheet.blit(small, (x, 12))
        band = _label_band(cell_w, label, caption, height=band_h)
        sheet.blit(band, (x, 12 + cell_h))
    sheet_path = os.path.join(_OUT, "00_contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/mega_magnet_ring_colors")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")


if __name__ == "__main__":
    main()
