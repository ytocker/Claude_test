"""Round-1 exploration sheet for NERD SPECS (shades_nerd).

Three variants, each shown as: product shot (eye_w=96), on-Pip @22px native,
and a ~6x zoom of the on-Pip head (the true in-game read judged big). Headless.

Run:  SDL_VIDEODRIVER=dummy python docs/shades/shades_nerd/render_round.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from game import parrot, store_skins          # noqa: E402
from variants import VARIANTS                  # noqa: E402


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
    font  = pygame.font.SysFont("Arial", 17, bold=True)
    small = pygame.font.SysFont("Arial", 13, bold=True)
    tiny  = pygame.font.SysFont("Arial", 11)

    CELL_W, CELL_H = 470, 220
    MARGIN, TITLE_H = 24, 54
    rows = len(VARIANTS)
    sheet_w = MARGIN * 2 + CELL_W
    sheet_h = TITLE_H + MARGIN + rows * CELL_H + MARGIN

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 34, 48))
    sheet.blit(font.render(
        "SKYBIT — SHADES · NERD SPECS (shades_nerd) · round 1 · "
        "product 96px + on-Pip 22px (native + ~6x)", True, (235, 240, 250)),
        (MARGIN, 18))

    for i, (label, fn) in enumerate(VARIANTS):
        x = MARGIN
        y = TITLE_H + MARGIN + i * CELL_H
        cell = pygame.Rect(x, y, CELL_W, CELL_H - 14)
        pygame.draw.rect(sheet, (40, 45, 62), cell, border_radius=10)
        pygame.draw.rect(sheet, (70, 78, 100), cell, 1, border_radius=10)

        # Product shot (checkered so the clear lens is legible).
        prod = product(fn)
        prod_rect = pygame.Rect(cell.left + 12, cell.top + 12, 176, 176)
        _checker(sheet, prod_rect)
        sheet.blit(prod, prod.get_rect(center=prod_rect.center).topleft)
        sheet.blit(tiny.render("product 96px", True, (190, 198, 216)),
                   (prod_rect.left, prod_rect.bottom + 1))

        pip = on_pip(fn)

        # On-Pip native (22px), small.
        nat_rect = pygame.Rect(prod_rect.right + 14, cell.top + 12, 96, 176)
        _checker(sheet, nat_rect, a=(48, 54, 72), b=(40, 46, 62))
        sheet.blit(pip, pip.get_rect(center=nat_rect.center).topleft)
        sheet.blit(tiny.render("native", True, (190, 198, 216)),
                   (nat_rect.left + 18, nat_rect.bottom + 1))

        # On-Pip ~6x zoom (nearest-neighbour) — judge the true 22px read big.
        # Crop tight on the head (eye anchor ~ (50,40) in composite + 2px
        # outline pad) so the eye-through read is what the reviewer judges.
        Z = 7
        crop = pygame.Rect(38, 28, 28, 28)         # head window in composite+pad
        head = pip.subsurface(crop.clip(pip.get_rect())).copy()
        zoom = pygame.transform.scale(head, (head.get_width() * Z,
                                             head.get_height() * Z))
        zoom_rect = pygame.Rect(nat_rect.right + 14, cell.top + 6, 184, 196)
        _checker(sheet, zoom_rect, a=(50, 56, 74), b=(42, 48, 64))
        sheet.set_clip(zoom_rect)
        sheet.blit(zoom, zoom.get_rect(center=zoom_rect.center).topleft)
        sheet.set_clip(None)
        pygame.draw.rect(sheet, (70, 78, 100), zoom_rect, 1)
        sheet.blit(tiny.render("~7x zoom — eye-through read", True,
                               (190, 198, 216)),
                   (zoom_rect.left, zoom_rect.bottom + 1))

        # Label strip.
        sheet.blit(small.render(label, True, (240, 226, 160)),
                   (cell.left + 12, cell.bottom - 18))

    out_path = os.path.join(_HERE, "round_1.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, sheet.get_size())


if __name__ == "__main__":
    main()
