"""Scratch render harness for the SHADES exploration sheet (round N).

Draws, for each of the 11 eyewear styles, a big product shot beside the
on-Pip overlay, plus a bare-eyed Pip cell, onto one labelled grid surface and
saves it under docs/shades/. Headless (SDL dummy) so it runs in CI/agents.

Run:  SDL_VIDEODRIVER=dummy python docs/shades/render_sheet.py [round_N]
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

# Allow running from anywhere: add repo root to the path.
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from game import parrot, store_skins  # noqa: E402
from game import (  # noqa: E402
    shades_nerd, shades_round, shades_heart, shades_star, shades_black,
    shades_white, shades_3d, shades_pixel, shades_ski, shades_monocle,
    shades_cyber,
)

STYLES = [
    ("shades_nerd",    shades_nerd.draw_shades),
    ("shades_round",   shades_round.draw_shades),
    ("shades_heart",   shades_heart.draw_shades),
    ("shades_star",    shades_star.draw_shades),
    ("shades_black",   shades_black.draw_shades),
    ("shades_white",   shades_white.draw_shades),
    ("shades_3d",      shades_3d.draw_shades),
    ("shades_pixel",   shades_pixel.draw_shades),
    ("shades_ski",     shades_ski.draw_shades),
    ("shades_monocle", shades_monocle.draw_shades),
    ("shades_cyber",   shades_cyber.draw_shades),
]


def on_pip(draw_shades, angle=-10):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                          pygame.SRCALPHA)
    comp.blit(parrot._build_frame_bare(angle), (0, store_skins.PARROT_DY))
    draw_shades(comp, 50, 40, 22, 1)
    return parrot._add_outline(comp)


def bare_pip(angle=-10):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                          pygame.SRCALPHA)
    comp.blit(parrot._build_frame_bare(angle), (0, store_skins.PARROT_DY))
    return parrot._add_outline(comp)


def product_shot(draw_shades, canvas=160):
    surf = pygame.Surface((canvas, canvas), pygame.SRCALPHA)
    draw_shades(surf, canvas // 2, canvas // 2, 96, 1)
    return parrot._add_outline(surf)


def _checker(surf, rect, a=(54, 60, 78), b=(44, 50, 66), s=8):
    """Soft checker so transparent eyewear regions are still legible."""
    for y in range(rect.top, rect.bottom, s):
        for x in range(rect.left, rect.right, s):
            c = a if ((x // s + y // s) % 2 == 0) else b
            surf.fill(c, (x, y, min(s, rect.right - x), min(s, rect.bottom - y)))


def main():
    out_name = sys.argv[1] if len(sys.argv) > 1 else "round_1"
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 16, bold=True)
    small = pygame.font.SysFont("Arial", 13)

    # Layout: 3 columns of cells, each cell = product shot (left) + on-Pip
    # overlay (right), with a label strip below. 12 cells (11 + bare).
    CELL_W, CELL_H = 300, 210
    COLS = 3
    items = list(STYLES)
    total = len(items) + 1                      # + bare-eyed cell
    rows = (total + COLS - 1) // COLS
    MARGIN = 24
    TITLE_H = 56
    sheet_w = MARGIN * 2 + COLS * CELL_W
    sheet_h = TITLE_H + MARGIN + rows * CELL_H + MARGIN

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 34, 48))
    title = font.render("SKYBIT — SHADES (eyewear) store  ·  round 1  ·  product shot + on-Pip @22px",
                        True, (235, 240, 250))
    sheet.blit(title, (MARGIN, 20))

    def draw_cell(idx, label, prod, pip):
        col = idx % COLS
        row = idx // COLS
        x = MARGIN + col * CELL_W
        y = TITLE_H + MARGIN + row * CELL_H
        cell = pygame.Rect(x, y, CELL_W - 12, CELL_H - 12)
        pygame.draw.rect(sheet, (40, 45, 62), cell, border_radius=10)
        pygame.draw.rect(sheet, (70, 78, 100), cell, 1, border_radius=10)

        # Product shot region (checkered).
        prod_rect = pygame.Rect(cell.left + 10, cell.top + 10, 170, 170)
        _checker(sheet, prod_rect)
        pr = prod.get_rect(center=prod_rect.center)
        sheet.blit(prod, pr.topleft)

        # On-Pip region: show the bird at native + a 2x zoom for the 22px read.
        pip_rect = pygame.Rect(prod_rect.right + 8, cell.top + 10, 92, 170)
        _checker(sheet, pip_rect, a=(48, 54, 72), b=(40, 46, 62))
        # native size, top
        nr = pip.get_rect(midtop=(pip_rect.centerx, pip_rect.top + 6))
        sheet.blit(pip, nr.topleft)
        # 1.6x zoom of the head, bottom — the true in-game scale judged big
        zoom = pygame.transform.rotozoom(pip, 0, 1.7)
        zr = zoom.get_rect(midbottom=(pip_rect.centerx, pip_rect.bottom - 4))
        sheet.blit(zoom, zr.topleft)

        # Label strip.
        lab = small.render(label, True, (220, 226, 240))
        sheet.blit(lab, (cell.left + 10, cell.bottom - 22))

    for i, (sid, fn) in enumerate(items):
        draw_cell(i, sid, product_shot(fn), on_pip(fn))

    # Bare-eyed Pip cell (no product shot — just the base eye, repeated).
    bp = bare_pip()
    draw_cell(len(items), "(bare eye — NO SHADES)", bp, bp)

    out_dir = os.path.join(_ROOT, "docs", "shades")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{out_name}.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, sheet.get_size())


if __name__ == "__main__":
    main()
