"""Render the STAR SHADES round-1 exploration sheet.

For each of the 3 variants, draws a big product shot (eye_w=96), an on-Pip
overlay at native 22px, and a ~6x zoom of that overlay so the tiny in-game
read is judgeable. One column also shows the CURRENT shipped star shade for
comparison. Headless (SDL dummy) so it runs under agents/CI.

Run:  SDL_VIDEODRIVER=dummy python docs/shades/shades_star/render_sheet.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game import parrot, store_skins        # noqa: E402
from game import shades_star as current      # noqa: E402
import explore                               # noqa: E402

# Variant to implement into draw.py (mark it on the sheet).
CHOSEN = "v1 GOLD MIRROR"


def on_pip(draw_shades, angle=-10):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                          pygame.SRCALPHA)
    comp.blit(parrot._build_frame_bare(angle), (0, store_skins.PARROT_DY))
    draw_shades(comp, 50, 40, 22, 1)
    return parrot._add_outline(comp)


def product(draw_shades, c=160):
    s = pygame.Surface((c, c), pygame.SRCALPHA)
    draw_shades(s, c // 2, c // 2, 96, 1)
    return parrot._add_outline(s)


def _checker(surf, rect, a=(54, 60, 78), b=(44, 50, 66), s=8):
    for y in range(rect.top, rect.bottom, s):
        for x in range(rect.left, rect.right, s):
            c = a if ((x // s + y // s) % 2 == 0) else b
            surf.fill(c, (x, y, min(s, rect.right - x), min(s, rect.bottom - y)))


def main():
    pygame.font.init()
    title_f = pygame.font.SysFont("Arial", 22, bold=True)
    label_f = pygame.font.SysFont("Arial", 17, bold=True)
    small_f = pygame.font.SysFont("Arial", 13)

    items = list(explore.VARIANTS) + [("CURRENT (shipped)", current.draw_shades)]

    CELL_W, CELL_H = 340, 240
    COLS = 2
    rows = (len(items) + COLS - 1) // COLS
    MARGIN = 26
    TITLE_H = 64
    sheet_w = MARGIN * 2 + COLS * CELL_W
    sheet_h = TITLE_H + MARGIN + rows * CELL_H + MARGIN

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((28, 32, 46))
    sheet.blit(title_f.render(
        "SKYBIT — STAR SHADES (shades_star)  ·  round 1  ·  3 variants  ·  "
        "product @96 + on-Pip @22px (native + ~6x)", True, (236, 242, 252)),
        (MARGIN, 22))

    def draw_cell(idx, label, prod, pip, chosen=False):
        col = idx % COLS
        row = idx // COLS
        x = MARGIN + col * CELL_W
        y = TITLE_H + MARGIN + row * CELL_H
        cell = pygame.Rect(x, y, CELL_W - 14, CELL_H - 14)
        bg = (44, 50, 68) if not chosen else (40, 58, 50)
        pygame.draw.rect(sheet, bg, cell, border_radius=12)
        edge = (255, 214, 90) if chosen else (74, 82, 104)
        pygame.draw.rect(sheet, edge, cell, 2 if chosen else 1, border_radius=12)

        # Product shot (checkered).
        prod_rect = pygame.Rect(cell.left + 12, cell.top + 12, 176, 176)
        _checker(sheet, prod_rect)
        sheet.blit(prod, prod.get_rect(center=prod_rect.center).topleft)

        # On-Pip: native top, ~6x head zoom bottom.
        pip_rect = pygame.Rect(prod_rect.right + 10, cell.top + 12,
                               cell.right - prod_rect.right - 22, 176)
        _checker(sheet, pip_rect, a=(48, 54, 72), b=(40, 46, 62))
        nr = pip.get_rect(midtop=(pip_rect.centerx, pip_rect.top + 6))
        sheet.blit(pip, nr.topleft)
        sheet.blit(small_f.render("22px", True, (200, 206, 222)),
                   (pip_rect.left + 4, pip_rect.top + 4))
        # Nearest-neighbour zoom centred on the EYE so the tiny star read is
        # honest. The eye anchor is composite (50,40); _add_outline pads by 3
        # (pad=2 + the bird's own +1 build offset), so it lands at ~(53,43) in
        # the outlined pip surface. Sample a 34px box around it.
        ex, ey = 53, 43
        crop = 34
        head = pygame.Surface((crop, crop), pygame.SRCALPHA)
        head.blit(pip, (-(ex - crop // 2), -(ey - crop // 2)))
        Z = 5
        zoom = pygame.transform.scale(head, (crop * Z, crop * Z))
        zr = zoom.get_rect(midbottom=(pip_rect.centerx, pip_rect.bottom - 4))
        sheet.blit(zoom, zr.topleft)
        pygame.draw.rect(sheet, (70, 78, 100), zr, 1)
        sheet.blit(small_f.render(f"~{Z}x eye", True, (200, 206, 222)),
                   (zr.left + 2, zr.top + 2))

        # Label.
        tag = label + ("   ◀ IMPLEMENTED" if chosen else "")
        sheet.blit(label_f.render(tag, True,
                   (255, 226, 120) if chosen else (224, 230, 244)),
                   (cell.left + 12, cell.bottom - 26))

    for i, (label, fn) in enumerate(items):
        is_chosen = (label == CHOSEN)
        draw_cell(i, label, product(fn), on_pip(fn), chosen=is_chosen)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "round_1.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, sheet.get_size())


if __name__ == "__main__":
    main()
