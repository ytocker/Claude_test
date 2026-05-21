"""Render 5 MEGA MAGNET variants extending the BOLD-OUTWARD pattern
through the 2 new outer rings (rfac 1.15 and 1.30).

The regular magnet ramps alpha + stroke width as rings grow:
  rfac 0.55: alpha 100, width 2  (faintest, thinnest)
  rfac 0.78: alpha 140, width 2
  rfac 1.00: alpha 180, width 3  (boldest of the 3)

User: "the color gets more bold in its style as the circles get
larger. But the two circles you added don't have this behavior, so
you need to extend it."

So the 2 new outer rings need to be BOLDER (higher alpha, wider
stroke) than rfac=1.00, continuing the ramp outward. The previous
runs had them at alpha 130/150 (LOWER than 1.00's 180) — the exact
opposite of the regular's pattern.

All 5 variants keep the 5 existing inner rings (rfac 0.40 → 1.00)
verbatim — only the 2 NEW outer rings change. The gradient
backdrop uses the softer M1-style calibration so the field stays
non-aggressive.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_mega_magnet_bold_outer_variants.py
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
                    "mega_magnet_bold_outer")
os.makedirs(_OUT, exist_ok=True)


# The 5 inner rings stay verbatim across all variants — same colours
# and widths as the original mega stack inside rfac=1.00.
INNER_RINGS = (
    # (rfac, phase, alpha, width, breath_scale, color)
    (1.00, 0.0,  180, 3, 1.00, (255, 220, 100)),
    (0.85, 0.3,  165, 2, 0.92, (255, 210,  85)),
    (0.70, 0.6,  150, 2, 0.85, (250, 195,  65)),
    (0.55, 0.9,  130, 2, 0.78, (240, 180,  50)),
    (0.40, 1.2,  110, 2, 0.70, (225, 165,  35)),
)


# Soft M1-style gradient backdrop, cached.
_GRAD_CACHE = None
def gradient_cached():
    global _GRAD_CACHE
    if _GRAD_CACHE is not None:
        return _GRAD_CACHE
    GLOW_COL = (245, 175, 40)
    sz = 200
    s = pygame.Surface((sz, sz), pygame.SRCALPHA)
    cx = cy = sz / 2
    max_r = sz / 2
    for y in range(sz):
        for x in range(sz):
            dx, dy = x - cx, y - cy
            d = math.sqrt(dx * dx + dy * dy)
            if d > max_r:
                continue
            inner_t = d / max_r
            bell = math.exp(-((inner_t - 0.85) ** 2) / 0.15)
            a = int(72 * bell)
            if a > 0:
                s.set_at((x, y), (*GLOW_COL, a))
    _GRAD_CACHE = s
    return s


def render_with_outer(outer_rings, t_phase=0.6):
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
    all_rings = list(outer_rings) + list(INNER_RINGS)
    for rfac, phase, alpha, width, breath_scale, ring_col in all_rings:
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


# Each variant: list of 2 outer rings (rfac, phase, alpha, width,
# breath_scale, color). rfac 1.15 first then 1.30 so they draw in
# the same order as the rest of the stack (largest last).
VARIANTS = [
    ("B1_subtle_bolder",
     "Subtle bolder: 1.15 alpha=200/w3, 1.30 alpha=220/w3",
     [
         (1.15, -0.3, 200, 3, 0.78, (255, 225, 110)),
         (1.30, -0.6, 220, 3, 0.62, (255, 230, 120)),
     ]),
    ("B2_strong_bolder",
     "Strong bolder: 1.15 alpha=210/w3, 1.30 alpha=240/w4",
     [
         (1.15, -0.3, 210, 3, 0.78, (255, 230, 120)),
         (1.30, -0.6, 240, 4, 0.62, (255, 235, 135)),
     ]),
    ("B3_max_bold",
     "Max bold: 1.15 alpha=220/w4, 1.30 alpha=255/w5",
     [
         (1.15, -0.3, 220, 4, 0.78, (255, 235, 130)),
         (1.30, -0.6, 255, 5, 0.62, (255, 240, 145)),
     ]),
    ("B4_bold_plus_color",
     "Bold + cream colour extension (1.30 (255,245,175))",
     [
         (1.15, -0.3, 210, 3, 0.78, (255, 235, 140)),
         (1.30, -0.6, 235, 4, 0.62, (255, 245, 175)),
     ]),
    ("B5_uniform_outer_width3",
     "Uniform width-3 outer halos, alpha 195 / 220",
     [
         (1.15, -0.3, 195, 3, 0.78, (255, 225, 115)),
         (1.30, -0.6, 220, 3, 0.62, (255, 230, 125)),
     ]),
]


def main():
    saved = []
    for label, caption, outer_rings in VARIANTS:
        frame = render_with_outer(outer_rings)
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
            "v5_powerups/docs/screenshots/mega_magnet_bold_outer")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")


if __name__ == "__main__":
    main()
