"""Render 5 V1-Simple-Train variants with the REAR wheel at
different x positions. Front wheel stays at boiler.left +
0.72*width; only the rear wheel's `rear_frac` changes. Each
variant is at least 2 native pixels apart in rear-wheel x so the
user can pick the gap that looks right.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_rail_wheel_gap_variants.py
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

from tools.render_helmet_side_view_variants import _label_band
from tools.render_rail_train_variants import (
    _paint_ticket_chassis, _spoked_wheel, _cowcatcher,
    INK, CREAM, NEAR_BLACK, SS, NATIVE_W, NATIVE_H,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "rail_train_variants")


# 5 rear-wheel-x fractions of boiler.width. Front wheel is fixed
# at 0.72. The fractions are picked so each variant's rear wheel
# is at least 2 native pixels (= 2 SS = 12 paint px) further
# right than the previous. The "under cab" placement was already
# shipped and judged "too rear", so we start INSIDE the boiler.
REAR_FRACS = [
    ("G1_far_left", 0.05, "G1: rear-frac 0.05 (gap ~9.4 px)"),
    ("G2_back",     0.22, "G2: rear-frac 0.22 (gap ~7.0 px)"),
    ("G3_mid_back", 0.38, "G3: rear-frac 0.38 (gap ~4.8 px)"),
    ("G4_mid",      0.52, "G4: rear-frac 0.52 (gap ~2.8 px)"),
    ("G5_close",    0.62, "G5: rear-frac 0.62 (gap ~1.4 px)"),
]


def _paint_loco(big, scale, cx, cy, rear_frac):
    """Mirror of `_paint_train_v1_classic_steam` from the train-
    variants tool, but with the rear-wheel fraction parameterised."""
    boiler_w = int(SS * 18 * scale)
    boiler_h = int(SS * 6.5 * scale)
    boiler = pygame.Rect(0, 0, boiler_w, boiler_h)
    boiler.midright = (cx + int(SS * 8 * scale), cy)
    pygame.draw.rect(big, INK, boiler,
                     border_radius=max(1, int(SS * 0.8 * scale)))
    # Cab on the left.
    cab_w = int(SS * 6 * scale)
    cab_h = int(SS * 8 * scale)
    cab = pygame.Rect(0, 0, cab_w, cab_h)
    cab.midright = (boiler.left, cy)
    pygame.draw.rect(big, INK, cab,
                     border_radius=max(1, int(SS * 0.6 * scale)))
    roof = pygame.Rect(0, 0, cab_w + int(SS * 1.2 * scale),
                        max(1, int(SS * 0.8 * scale)))
    roof.midbottom = (cab.centerx, cab.top + max(1, SS // 3))
    pygame.draw.rect(big, INK, roof)
    # Smokestack with flared cap.
    stack_w = max(2, int(SS * 1.8 * scale))
    stack_h = max(3, int(SS * 3.5 * scale))
    stack_x = boiler.right - int(SS * 4 * scale) - stack_w // 2
    stack = pygame.Rect(stack_x, boiler.top - stack_h,
                         stack_w, stack_h)
    pygame.draw.rect(big, INK, stack)
    flare = pygame.Rect(0, 0, int(stack_w * 1.8),
                         max(1, int(SS * 0.7 * scale)))
    flare.midbottom = (stack.centerx, stack.top)
    pygame.draw.rect(big, INK, flare)
    # Wheels — varied rear position.
    wheel_r = max(3, int(SS * 2.4 * scale))
    gap = max(1, int(SS * 0.4 * scale))
    wheel_cy = boiler.bottom + wheel_r + gap
    ground_y = wheel_cy + wheel_r
    drive_xs = (
        boiler.left + int(boiler.width * rear_frac),
        boiler.left + int(boiler.width * 0.72),
    )
    rod_h = max(2, int(SS * 0.9 * scale))
    rod_y = wheel_cy - int(wheel_r * 0.30) - rod_h // 2
    pygame.draw.rect(big, INK,
                     (drive_xs[0], rod_y,
                      drive_xs[1] - drive_xs[0], rod_h))
    for wx in drive_xs:
        _spoked_wheel(big, wx, wheel_cy, wheel_r, scale)
        pygame.draw.circle(big, CREAM, (wx, rod_y + rod_h // 2),
                           max(1, int(SS * 0.5 * scale)))
    _cowcatcher(big,
                (boiler.right, boiler.bottom - SS // 3),
                ground_y, scale)


def _build_icon(rear_frac):
    sw, sh = NATIVE_W * SS, NATIVE_H * SS
    big = pygame.Surface((sw, sh), pygame.SRCALPHA)
    card = _paint_ticket_chassis(big)
    _paint_loco(big, 1.0, card.centerx, card.centery + int(SS * 2),
                rear_frac)
    return pygame.transform.smoothscale(big, (NATIVE_W, NATIVE_H))


def _zoom(icon, factor=8):
    big = pygame.transform.scale(icon,
                                  (NATIVE_W * factor, NATIVE_H * factor))
    pygame.draw.rect(big, (255, 215, 0), big.get_rect(), 2)
    return big


def main():
    saved = []
    for label, rfrac, caption in REAR_FRACS:
        icon = _build_icon(rfrac)
        path = os.path.join(_OUT, f"{label}.png")
        pygame.image.save(_zoom(icon), path)
        saved.append((label, caption, _zoom(icon, factor=6)))
        print(f"saved {path}")

    cell_w = saved[0][2].get_width()
    cell_h = saved[0][2].get_height()
    band_h = 56
    gap = 12
    sheet_w = len(saved) * cell_w + (len(saved) - 1) * gap + 24
    sheet_h = cell_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, caption, icon) in enumerate(saved):
        x = 12 + idx * (cell_w + gap)
        sheet.blit(icon, (x, 12))
        band = _label_band(cell_w, label, caption, height=band_h)
        sheet.blit(band, (x, 12 + cell_h))
    sheet_path = os.path.join(_OUT, "00_wheel_gap_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")
    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/rail_train_variants")
    print()
    print(f"{base}/00_wheel_gap_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")


if __name__ == "__main__":
    main()
