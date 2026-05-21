"""Render 5 MEGA MAGNET gradient variants for the user to pick from.
The current live version is "too aggressive" — gold is too bold
across too much of the field. Each variant tweaks three parameters:

  * BELL_PEAK     — where the gradient peaks (0.85 = inner-like
                     regular magnet, 1.0 = outermost ring)
  * FALLOFF       — denominator in exp(-((t-peak)^2)/FALLOFF)
                     (smaller = sharper peak, larger = softer
                     spread)
  * ALPHA_MULT    — overall intensity (regular magnet uses 72)

Variants:

  M1 — regular calibration scaled up (peak 0.85, falloff 0.15,
       alpha 72) — minimal, soft halo at mid-outer
  M2 — outer-leaning soft (peak 0.95, falloff 0.20, alpha 80)
  M3 — peak right at the outer ring but gentle (peak 1.0, falloff
       0.25, alpha 90)
  M4 — broad outer wash (peak 1.0, falloff 0.35, alpha 100)
  M5 — currently-live aggressive (peak 1.0, falloff 0.40, alpha 160)
       — kept as the bookend so the user can see how far each
       variant is from the current state

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_mega_magnet_gradient_variants.py
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
                    "mega_magnet_gradient_variants")
os.makedirs(_OUT, exist_ok=True)


GLOW_COL = (245, 175, 40)
MEGA_RINGS = (
    (1.30, -0.6, 130, 2, 0.62, (255, 225, 115)),
    (1.15, -0.3, 150, 2, 0.78, (255, 220, 105)),
    (1.00, 0.0,  180, 3, 1.00, (255, 220, 100)),
    (0.85, 0.3,  165, 2, 0.92, (255, 210,  85)),
    (0.70, 0.6,  150, 2, 0.85, (250, 195,  65)),
    (0.55, 0.9,  130, 2, 0.78, (240, 180,  50)),
    (0.40, 1.2,  110, 2, 0.70, (225, 165,  35)),
)


def _gradient_surface(peak, falloff, alpha_mult, size=200):
    """Build the per-pixel radial gradient on a small surface."""
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
                surf.set_at((x, y), (*GLOW_COL, a))
    return surf


def render_variant(peak, falloff, alpha_mult, t_phase=0.6):
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
    field = pygame.Surface((outer_r * 2, outer_r * 2), pygame.SRCALPHA)
    lcx, lcy = outer_r, outer_r

    BREATH = 0.30
    # Tie gradient outer edge to the outermost ring's pulse.
    outer_ring_amp = BREATH * 0.62
    u_outer_ring = (math.sin(t_pulse + (-0.6)) + 1) / 2
    outer_ring_factor = 1.0 - outer_ring_amp * (1.0 - u_outer_ring)
    glow_rad = rad * 1.30 * outer_ring_factor

    grad_src = _gradient_surface(peak, falloff, alpha_mult)
    target = int(glow_rad * 2)
    scaled = pygame.transform.smoothscale(grad_src, (target, target))
    field.blit(scaled, (lcx - target // 2, lcy - target // 2))

    AA_COL = (255, 240, 180)
    for rfac, phase, alpha, width, breath_scale, ring_col in MEGA_RINGS:
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
               (int(world.bird.x) - lcx, int(world.bird.y) - lcy))
    HUD().draw_play(frame, world, best=0)
    return frame


VARIANTS = [
    ("M1_regular_calibration",
     0.85, 0.15, 72,
     "Regular magnet curve, scaled up — softest, halo at mid-outer"),
    ("M2_outer_leaning_soft",
     0.95, 0.20, 80,
     "Peak near outer + slightly wider falloff — gentle outer rim"),
    ("M3_peak_outer_gentle",
     1.00, 0.25, 90,
     "Peak AT outer ring, moderate spread, moderate alpha"),
    ("M4_broad_outer_wash",
     1.00, 0.35, 100,
     "Broad outer wash, still moderate alpha"),
    ("M5_current_live_aggressive",
     1.00, 0.40, 160,
     "Currently-live aggressive version (for comparison)"),
]


def main():
    saved = []
    for label, peak, falloff, alpha_mult, caption in VARIANTS:
        frame = render_variant(peak, falloff, alpha_mult)
        path = os.path.join(_OUT, f"{label}.png")
        pygame.image.save(frame, path)
        saved.append((label, caption, frame))
        print(f"saved {path}  peak={peak} falloff={falloff} alpha={alpha_mult}")

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
            "v5_powerups/docs/screenshots/mega_magnet_gradient_variants")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")


if __name__ == "__main__":
    main()
