"""Render 5 variants of P1-Misfits v1 (skull 27x22, 7 narrow
fangs) with the MOUTH at progressively lower fractional
positions inside the face. Every other parameter (face size,
decks, fang count + dimensions, eyes, nose) is held identical
to V1 so the user can pick a mouth-height that reads well.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_misfits_v1_mouth_low.py
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

from tools.render_skateboard_mouth_variants import (
    DOME, CHROME, BONE, CREAM, RED, SS, NATIVE_W, NATIVE_H,
)
from tools.render_helmet_side_view_variants import _label_band


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_mouth_variants")
os.makedirs(_OUT, exist_ok=True)


# V1 base parameters (skull 27x22, 7 narrow fangs).
SK_W = 27
SK_H = 22
DECK_W = 46
DECK_H = 9
FANG_N = 7
FANG_TOOTH_H = 2.4
FANG_HALF_W = 0.55
FANG_SPAN = 12
BAR_STROKE = 1.2

# 5 progressively LOWER mouth positions. The original v1 uses
# jaw_y_frac = 0.72; these step down to 0.90 (just above the
# chin). Each step is +0.04 so the progression is even.
MOUTH_FRACS = [
    ("L1_0p74", 0.74, "L1: jaw_y = 0.74 of skull height (+0.02 from v1)"),
    ("L2_0p78", 0.78, "L2: jaw_y = 0.78 of skull height (+0.06 from v1)"),
    ("L3_0p82", 0.82, "L3: jaw_y = 0.82 of skull height (+0.10 from v1)"),
    ("L4_0p86", 0.86, "L4: jaw_y = 0.86 of skull height (+0.14 from v1)"),
    ("L5_0p90", 0.90, "L5: jaw_y = 0.90 of skull height (+0.18 from v1)"),
]


def _paint(jaw_y_frac):
    """Paint V1 with the mouth at the given fractional jaw_y."""
    big = pygame.Surface((NATIVE_W * SS, NATIVE_H * SS),
                          pygame.SRCALPHA)
    bx = big.get_width() // 2
    by = big.get_height() // 2

    # Crossed decks.
    for angle in (35, -35):
        sub_w = DECK_W * SS
        sub_h = DECK_H * SS
        sub = pygame.Surface((sub_w + 4 * SS, sub_h + 4 * SS),
                              pygame.SRCALPHA)
        d = pygame.Rect(0, 0, sub_w, sub_h)
        d.center = (sub.get_width() // 2, sub.get_height() // 2)
        pygame.draw.rect(sub, CHROME, d, border_radius=2 * SS)
        pygame.draw.rect(sub, DOME, d.inflate(-2 * SS, -2 * SS),
                         border_radius=SS)
        for sign in (-1, 1):
            wx = d.centerx + sign * (sub_w // 2 - 3 * SS)
            pygame.draw.circle(sub, CREAM, (wx, d.centery),
                               int(3 * SS))
            pygame.draw.circle(sub, RED, (wx, d.centery),
                               int(1.4 * SS))
        rot = pygame.transform.rotate(sub, angle)
        big.blit(rot, rot.get_rect(center=(bx, by)))

    # Skull.
    sk = pygame.Rect(0, 0, SK_W * SS, SK_H * SS)
    sk.center = (bx, by - SS)
    pygame.draw.ellipse(big, BONE, sk)
    pygame.draw.ellipse(big, DOME, sk, int(1.2 * SS))

    # Eyes + nose (kept at v1's fractional positions).
    eye_r = int(SK_W * SS * 0.108)
    eye_x_off = int(SK_W * SS * 0.20)
    eye_y = sk.top + int(SK_H * SS * 0.36)
    for ex in (sk.centerx - eye_x_off, sk.centerx + eye_x_off):
        pygame.draw.circle(big, DOME, (ex, eye_y), eye_r)
    nose_top_y = sk.top + int(SK_H * SS * 0.55)
    nose_bot_y = nose_top_y + int(2.5 * SS)
    pygame.draw.polygon(big, DOME, [
        (sk.centerx - SS, nose_top_y),
        (sk.centerx + SS, nose_top_y),
        (sk.centerx,      nose_bot_y),
    ])

    # P1-Misfits mouth at the per-variant jaw_y fraction.
    jaw_y = sk.top + int(SK_H * SS * jaw_y_frac)
    span = FANG_SPAN * SS
    upper_y = jaw_y - int(SS * 0.8)
    pygame.draw.line(big, DOME,
                     (sk.centerx - span // 2, upper_y),
                     (sk.centerx + span // 2, upper_y),
                     max(1, int(BAR_STROKE * SS)))
    tooth_h = int(FANG_TOOTH_H * SS)
    half_w = max(1, int(SS * FANG_HALF_W))
    for i in range(FANG_N):
        t = i / (FANG_N - 1)
        tx = sk.centerx - span // 2 + int(t * span)
        pygame.draw.polygon(big, DOME, [
            (tx - half_w, upper_y),
            (tx + half_w, upper_y),
            (tx,          upper_y + tooth_h),
        ])

    return pygame.transform.smoothscale(big, (NATIVE_W, NATIVE_H))


def main():
    cells = []
    for name, frac, caption in MOUTH_FRACS:
        icon = _paint(frac)
        zoom = pygame.transform.scale(icon,
                                       (NATIVE_W * 6, NATIVE_H * 6))
        pygame.draw.rect(zoom, (255, 215, 0), zoom.get_rect(), 2)
        path = os.path.join(_OUT,
                             f"P1_misfits_v1_mouth_{name}.png")
        pygame.image.save(zoom, path)
        cells.append((name, caption, zoom))
        print(f"saved {path}")

    cell_w = cells[0][2].get_width()
    cell_h = cells[0][2].get_height()
    band_h = 56
    gap = 12
    sheet_w = len(cells) * cell_w + (len(cells) - 1) * gap + 24
    sheet_h = cell_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (name, caption, icon) in enumerate(cells):
        x = 12 + idx * (cell_w + gap)
        sheet.blit(icon, (x, 12))
        band = _label_band(cell_w, name, caption, height=band_h)
        sheet.blit(band, (x, 12 + cell_h))
    sheet_path = os.path.join(_OUT,
                               "P1_misfits_v1_mouth_low_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/skateboard_mouth_variants")
    print()
    print(f"{base}/P1_misfits_v1_mouth_low_sheet.png")
    for name, caption, _ in cells:
        print(f"{base}/P1_misfits_v1_mouth_{name}.png  -- {caption}")


if __name__ == "__main__":
    main()
