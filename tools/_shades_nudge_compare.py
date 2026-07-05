"""Scratch before/after for a uniform rightward seat nudge of all 11 shades.

Renders each style's on-Pip head crop at the CURRENT anchor (cx=51) beside the
NUDGED anchor (cx=51+DX) so the few-pixel move toward the beak is obvious. The
product ICON is unaffected by the anchor, so it isn't shown. Headless.

Run:  SDL_VIDEODRIVER=dummy python tools/_shades_nudge_compare.py [DX]
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from game import parrot, store_skins  # noqa: E402
from game import (  # noqa: E402
    shades_nerd, shades_round, shades_heart, shades_star, shades_black,
    shades_white, shades_3d, shades_pixel, shades_ski, shades_monocle,
    shades_cyber,
)

STYLES = [
    ("nerd", shades_nerd), ("round", shades_round), ("heart", shades_heart),
    ("star", shades_star), ("black", shades_black), ("white", shades_white),
    ("3d", shades_3d), ("pixel", shades_pixel), ("ski", shades_ski),
    ("monocle", shades_monocle), ("cyber", shades_cyber),
]

BASE_CX = 51


def head_crop(fn, cx, zoom=6):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                          pygame.SRCALPHA)
    comp.blit(parrot._build_frame_bare(-8), (0, store_skins.PARROT_DY))
    if fn:
        fn(comp, cx, 40, 22, 1)
    pip = parrot._add_outline(comp)
    crop = pip.subsurface(pygame.Rect(28, 20, 36, 42)).copy()
    return pygame.transform.scale(crop, (36 * zoom, 42 * zoom))


def _checker(surf, rect, a=(54, 60, 78), b=(44, 50, 66), s=12):
    for y in range(rect.top, rect.bottom, s):
        for x in range(rect.left, rect.right, s):
            c = a if ((x // s + y // s) % 2 == 0) else b
            surf.fill(c, (x, y, min(s, rect.right - x), min(s, rect.bottom - y)))


def main():
    dx = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    pygame.font.init()
    title_f = pygame.font.SysFont("Arial", 20, bold=True)
    lab_f = pygame.font.SysFont("Arial", 15, bold=True)
    sub_f = pygame.font.SysFont("Arial", 12)

    ZOOM = 6
    cw, ch = 36 * ZOOM, 42 * ZOOM
    CELL_W = cw * 2 + 48
    CELL_H = ch + 40
    COLS = 3
    rows = (len(STYLES) + COLS - 1) // COLS
    MARGIN = 24
    TITLE_H = 60
    W = MARGIN * 2 + COLS * CELL_W + (COLS - 1) * MARGIN
    H = TITLE_H + MARGIN + rows * (CELL_H + MARGIN)

    sheet = pygame.Surface((W, H))
    sheet.fill((28, 32, 46))
    sheet.blit(title_f.render(
        f"SKYBIT — SHADES  ·  uniform rightward seat nudge  ·  +{dx}px toward the beak",
        True, (235, 240, 250)), (MARGIN, 18))

    for i, (name, mod) in enumerate(STYLES):
        col, row = i % COLS, i // COLS
        x = MARGIN + col * (CELL_W + MARGIN)
        y = TITLE_H + MARGIN + row * (CELL_H + MARGIN)
        cell = pygame.Rect(x, y, CELL_W, CELL_H)
        pygame.draw.rect(sheet, (40, 45, 62), cell, border_radius=10)
        pygame.draw.rect(sheet, (70, 78, 100), cell, 1, border_radius=10)

        sheet.blit(lab_f.render(name, True, (235, 240, 250)),
                   (cell.left + 16, cell.top + 4))

        ox, ny = cell.left + 16, cell.top + 24
        r_old = pygame.Rect(ox, ny, cw, ch)
        _checker(sheet, r_old)
        sheet.blit(head_crop(mod.draw_shades, BASE_CX, ZOOM), r_old.topleft)
        sheet.blit(sub_f.render(f"NOW (cx={BASE_CX})", True, (255, 180, 150)),
                   (ox, ny + ch + 2))

        nx = ox + cw + 12
        r_new = pygame.Rect(nx, ny, cw, ch)
        _checker(sheet, r_new)
        sheet.blit(head_crop(mod.draw_shades, BASE_CX + dx, ZOOM), r_new.topleft)
        sheet.blit(sub_f.render(f"NUDGED (cx={BASE_CX + dx})", True, (150, 235, 160)),
                   (nx, ny + ch + 2))

    out = os.path.join(_ROOT, "docs", "shades", "nudge_right.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
