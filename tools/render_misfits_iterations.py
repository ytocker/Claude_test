"""Render the 4 P1 (Misfits) iteration variants side-by-side
so the design progression is reviewable. Iterations were
self-critiqued + tweaked in-place — only v1 (commit 29af998)
and v4 (commit 96fa039) made it into git; v2 + v3 lived only
in the working tree.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_misfits_iterations.py
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


# Each iteration's parameters captured verbatim.
ITERATIONS = [
    {
        "name": "v1_iter1",
        "caption": "v1: skull 27x22, 7 narrow fangs (h=2.4 SS, w=0.55 SS)",
        "sk_w": 27, "sk_h": 22, "deck_w": 46, "deck_h": 9,
        "n": 7, "tooth_h": 2.4, "half_w": 0.55,
        "span": 12, "bar_stroke": 1.2,
    },
    {
        "name": "v2_iter2",
        "caption": "v2: skull 40x32, 5 chunkier fangs (h=3.5 SS, w=1.4 SS)",
        "sk_w": 40, "sk_h": 32, "deck_w": 38, "deck_h": 10,
        "n": 5, "tooth_h": 3.5, "half_w": 1.4,
        "span": 16, "bar_stroke": 1.8,
    },
    {
        "name": "v3_iter3",
        "caption": "v3: skull 40x32, 5 sharper fangs (h=4.2 SS, w=0.95 SS)",
        "sk_w": 40, "sk_h": 32, "deck_w": 38, "deck_h": 10,
        "n": 5, "tooth_h": 4.2, "half_w": 0.95,
        "span": 16, "bar_stroke": 1.8,
    },
    {
        "name": "v4_iter4_final",
        "caption": "v4 FINAL: skull 40x32, 3 big fangs (h=5.0 SS, w=1.8 SS)",
        "sk_w": 40, "sk_h": 32, "deck_w": 38, "deck_h": 10,
        "n": 3, "tooth_h": 5.0, "half_w": 1.8,
        "span": 14, "bar_stroke": 2.0,
    },
]


def _paint(params):
    """Paint a single icon at iteration `params` and return the
    smoothscale-down to NATIVE_W × NATIVE_H."""
    big = pygame.Surface((NATIVE_W * SS, NATIVE_H * SS),
                          pygame.SRCALPHA)
    bx = big.get_width() // 2
    by = big.get_height() // 2

    # Decks.
    for angle in (35, -35):
        sub_w = params["deck_w"] * SS
        sub_h = params["deck_h"] * SS
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
    sk = pygame.Rect(0, 0, params["sk_w"] * SS, params["sk_h"] * SS)
    sk.center = (bx, by - SS)
    pygame.draw.ellipse(big, BONE, sk)
    pygame.draw.ellipse(big, DOME, sk, int(1.2 * SS))

    # Eyes + nose at the standard fractional positions.
    eye_r = int(params["sk_w"] * SS * 0.108)
    eye_x_off = int(params["sk_w"] * SS * 0.20)
    eye_y = sk.top + int(params["sk_h"] * SS * 0.36)
    for ex in (sk.centerx - eye_x_off, sk.centerx + eye_x_off):
        pygame.draw.circle(big, DOME, (ex, eye_y), eye_r)
    nose_top_y = sk.top + int(params["sk_h"] * SS * 0.55)
    nose_bot_y = nose_top_y + int(2.5 * SS)
    pygame.draw.polygon(big, DOME, [
        (sk.centerx - SS, nose_top_y),
        (sk.centerx + SS, nose_top_y),
        (sk.centerx,      nose_bot_y),
    ])

    # P1-Misfits mouth at this iteration's parameters.
    jaw_y = sk.top + int(params["sk_h"] * SS * 0.72)
    span = int(params["span"]) * SS
    upper_y = jaw_y - int(SS * 0.8)
    pygame.draw.line(big, DOME,
                     (sk.centerx - span // 2, upper_y),
                     (sk.centerx + span // 2, upper_y),
                     max(1, int(params["bar_stroke"] * SS)))
    tooth_h = int(params["tooth_h"] * SS)
    half_w = max(1, int(SS * params["half_w"]))
    n = params["n"]
    for i in range(n):
        t = i / (n - 1)
        tx = sk.centerx - span // 2 + int(t * span)
        pygame.draw.polygon(big, DOME, [
            (tx - half_w, upper_y),
            (tx + half_w, upper_y),
            (tx,          upper_y + tooth_h),
        ])

    return pygame.transform.smoothscale(big, (NATIVE_W, NATIVE_H))


def main():
    cells = []
    for params in ITERATIONS:
        icon = _paint(params)
        zoom = pygame.transform.scale(icon,
                                       (NATIVE_W * 6, NATIVE_H * 6))
        pygame.draw.rect(zoom, (255, 215, 0), zoom.get_rect(), 2)
        path = os.path.join(_OUT,
                             f"P1_misfits_{params['name']}.png")
        pygame.image.save(zoom, path)
        cells.append((params["name"], params["caption"], zoom))
        print(f"saved {path}")

    # 4-cell contact sheet — single row.
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
    sheet_path = os.path.join(_OUT, "P1_misfits_iterations.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/skateboard_mouth_variants")
    print()
    print(f"{base}/P1_misfits_iterations.png")
    for name, caption, _ in cells:
        print(f"{base}/P1_misfits_{name}.png  -- {caption}")


if __name__ == "__main__":
    main()
