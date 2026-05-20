"""Render 5 simple-line mouth variants for the skateboard icon.
Each is a single black horizontal bar at jaw_y = 0.78 of skull
height (the L2 lower-mouth pick); the variants only differ in
the bar's WIDTH (span) and STROKE thickness so the user can
pick the weight that reads cleanest at game scale.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_skateboard_line_mouth_variants.py
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


# Live-icon base.
SK_W = 27
SK_H = 22
DECK_W = 46
DECK_H = 9
JAW_FRAC = 0.78

# 5 line variants: (label, span_SS, stroke_SS, caption).
LINE_VARIANTS = [
    ("B1_short_thin",    10, 1.0,
     "B1: 10 SS span × 1.0 SS stroke — short + thin"),
    ("B2_medium",        12, 1.4,
     "B2: 12 SS span × 1.4 SS stroke — medium (default)"),
    ("B3_wide_thick",    14, 2.0,
     "B3: 14 SS span × 2.0 SS stroke — wide + thick"),
    ("B4_short_chunky",  10, 2.2,
     "B4: 10 SS span × 2.2 SS stroke — short + chunky"),
    ("B5_wide_thin",     15, 1.0,
     "B5: 15 SS span × 1.0 SS stroke — wide + thin"),
]


def _paint(span_SS, stroke_SS):
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

    # Eyes.
    eye_r = int(SK_W * SS * 0.108)
    eye_x_off = int(SK_W * SS * 0.20)
    eye_y = sk.top + int(SK_H * SS * 0.36)
    for ex in (sk.centerx - eye_x_off, sk.centerx + eye_x_off):
        pygame.draw.circle(big, DOME, (ex, eye_y), eye_r)

    # Nose.
    nose_top_y = sk.top + int(SK_H * SS * 0.55)
    nose_bot_y = nose_top_y + int(2.5 * SS)
    pygame.draw.polygon(big, DOME, [
        (sk.centerx - SS, nose_top_y),
        (sk.centerx + SS, nose_top_y),
        (sk.centerx,      nose_bot_y),
    ])

    # Single black horizontal mouth bar.
    jaw_y = sk.top + int(SK_H * SS * JAW_FRAC)
    span = span_SS * SS
    pygame.draw.line(big, DOME,
                     (sk.centerx - span // 2, jaw_y),
                     (sk.centerx + span // 2, jaw_y),
                     max(1, int(stroke_SS * SS)))

    return pygame.transform.smoothscale(big, (NATIVE_W, NATIVE_H))


def main():
    cells = []
    for name, span_SS, stroke_SS, caption in LINE_VARIANTS:
        icon = _paint(span_SS, stroke_SS)
        zoom = pygame.transform.scale(icon,
                                       (NATIVE_W * 6, NATIVE_H * 6))
        pygame.draw.rect(zoom, (255, 215, 0), zoom.get_rect(), 2)
        path = os.path.join(_OUT,
                             f"skate_line_mouth_{name}.png")
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
                               "skate_line_mouth_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/skateboard_mouth_variants")
    print()
    print(f"{base}/skate_line_mouth_sheet.png")
    for name, caption, _ in cells:
        print(f"{base}/skate_line_mouth_{name}.png  -- {caption}")


if __name__ == "__main__":
    main()
