"""Smile-revision comparison for the SUN item.

Three columns: the ORIGINAL design 1 (wide grin — read as creepy), design 1 with
design 4's gentler 'tiny' smile grafted on, and design 4 itself for reference.
Hero close-up + Pip mid-flight per column.

Run: ``PYTHONPATH=. SDL_VIDEODRIVER=dummy python tools/render_sun_smile_compare.py``
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib
import pygame
pygame.init()

import tools.ninja_render as nr

COLUMNS = [
    ("ORIGINAL #1", "CLASSIC — wide grin", "design_1b"),
    ("#1 + #4's SMILE", "CLASSIC — tiny smile", "design_1"),
    ("#4", "KAWAII (reference)", "design_4"),
]

PANEL_W, PANEL_H = 240, 392
HERO_BOX = 240


def _src(spec):
    return importlib.import_module(f"tools.sun_candidates.{spec}").build


def _label(surf, text, x, y, size, color):
    font = pygame.font.SysFont("dejavusans", size, bold=True)
    surf.blit(font.render(text, True, (8, 6, 14)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def main():
    pad = 18
    head = 62
    cap = 44
    n = len(COLUMNS)
    sheet_w = pad + n * (PANEL_W + pad)
    sheet_h = head + HERO_BOX + cap + PANEL_H + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 26))

    _label(sheet, "SUN  ·  design 1 smile revision  (grafting design 4's gentle smile)",
           pad, 14, 23, (242, 238, 252))

    for i, (tag, name, spec) in enumerate(COLUMNS):
        x = pad + i * (PANEL_W + pad)
        src = _src(spec)
        sheet.blit(nr.hero_panel(src, HERO_BOX), (x, head))
        hl = (255, 150, 150) if spec == "design_1b" else (150, 230, 160)
        _label(sheet, tag, x + 6, head + HERO_BOX + 2, 18, hl)
        _label(sheet, name, x + 6, head + HERO_BOX + 23, 14, (236, 236, 244))
        sheet.blit(nr.gameplay_panel(src, PANEL_W, PANEL_H), (x, head + HERO_BOX + cap))

    out = "docs/store_redesign/animal/sun/smile_revision.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
