"""Scratch render for CYBER VISOR round 1 — 3 variants, product + on-Pip.

Each row: product shot (eye_w~96) | on-Pip @22px native | ~6x zoom of the
head so the 22px slit read is judged big. Headless (SDL dummy).

Run:  SDL_VIDEODRIVER=dummy python docs/shades/shades_cyber/render.py
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

from game import parrot, store_skins  # noqa: E402
import variants  # noqa: E402

VARIANTS = [
    ("V1  GVISOR  (cyan)  ** IMPLEMENTED **", variants.draw_v1),
    ("V2  PULSE  (magenta · segmented LED)",  variants.draw_v2),
    ("V3  HUD  (amber · wrap + reticle)",     variants.draw_v3),
]


def on_pip(draw_shades, angle=-10):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                          pygame.SRCALPHA)
    comp.blit(parrot._build_frame_bare(angle), (0, store_skins.PARROT_DY))
    draw_shades(comp, 50, 40, 22, 1)
    return parrot._add_outline(comp)


def product_shot(draw_shades, canvas=160):
    surf = pygame.Surface((canvas, canvas), pygame.SRCALPHA)
    draw_shades(surf, canvas // 2, canvas // 2, 96, 1)
    return parrot._add_outline(surf)


def _checker(surf, rect, a=(54, 60, 78), b=(44, 50, 66), s=8):
    for y in range(rect.top, rect.bottom, s):
        for x in range(rect.left, rect.right, s):
            c = a if ((x // s + y // s) % 2 == 0) else b
            surf.fill(c, (x, y, min(s, rect.right - x), min(s, rect.bottom - y)))


def main():
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 18, bold=True)
    small = pygame.font.SysFont("Arial", 14, bold=True)
    tiny = pygame.font.SysFont("Arial", 11)

    CELL_W, CELL_H = 560, 200
    MARGIN = 24
    TITLE_H = 54
    rows = len(VARIANTS)
    sheet_w = MARGIN * 2 + CELL_W
    sheet_h = TITLE_H + MARGIN + rows * CELL_H + MARGIN

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((28, 32, 46))
    sheet.blit(font.render(
        "SKYBIT — CYBER VISOR (shades_cyber)  ·  round 1  ·  product @96  +  on-Pip @22px  (native + 6x)",
        True, (236, 242, 252)), (MARGIN, 18))

    for i, (label, fn) in enumerate(VARIANTS):
        x = MARGIN
        y = TITLE_H + MARGIN + i * CELL_H
        cell = pygame.Rect(x, y, CELL_W, CELL_H - 14)
        pygame.draw.rect(sheet, (40, 45, 62), cell, border_radius=10)
        pygame.draw.rect(sheet, (70, 78, 100), cell, 1, border_radius=10)

        # Product shot.
        prod = product_shot(fn)
        prod_rect = pygame.Rect(cell.left + 12, cell.top + 12, 170, 150)
        _checker(sheet, prod_rect)
        sheet.blit(prod, prod.get_rect(center=prod_rect.center).topleft)
        sheet.blit(tiny.render("product @ eye_w 96", True, (200, 208, 226)),
                   (prod_rect.left, prod_rect.bottom + 2))

        # On-Pip native.
        pip = on_pip(fn)
        pip_rect = pygame.Rect(prod_rect.right + 14, cell.top + 12, 110, 150)
        _checker(sheet, pip_rect, a=(48, 54, 72), b=(40, 46, 62))
        sheet.blit(pip, pip.get_rect(center=pip_rect.center).topleft)
        sheet.blit(tiny.render("on-Pip @22px (native)", True, (200, 208, 226)),
                   (pip_rect.left, pip_rect.bottom + 2))

        # On-Pip 6x zoom — true in-game read judged large.
        zoom = pygame.transform.scale(pip, (pip.get_width() * 6,
                                            pip.get_height() * 6))
        zr = pygame.Rect(pip_rect.right + 14, cell.top + 12, 240, 150)
        _checker(sheet, zr, a=(50, 56, 74), b=(42, 48, 64))
        # Centre the head region (head sits upper-right of the sprite).
        crop = zoom.subsurface(pygame.Rect(
            min(zoom.get_width() - zr.w, int(zoom.get_width() * 0.42)),
            0, min(zr.w, zoom.get_width()), min(zr.h, zoom.get_height())))
        sheet.blit(crop, zr.topleft)
        sheet.blit(tiny.render("6x zoom — slit read at 22px", True,
                               (200, 208, 226)), (zr.left, zr.bottom + 2))

        sheet.blit(small.render(label, True, (255, 235, 180) if "IMPLEMENTED"
                                in label else (220, 226, 240)),
                   (cell.left + 12, cell.bottom - 30))

    out = os.path.join(_HERE, "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
