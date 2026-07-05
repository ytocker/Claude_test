"""Comparison figure for the FLAMINGO tail redesign.

Top row: a hero close-up of the ORIGINAL flamingo (detached-triangle tail) + the
five tail variants. Bottom row: each Pip mid-flight over the same gameplay biome
scene. Only the tail differs between columns. Pure capture.

Run: ``PYTHONPATH=. SDL_VIDEODRIVER=dummy python tools/render_flamingo_compare.py``
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
    ("ORIGINAL", "duotone bruiser", "skin_mantis_shrimp"),
    ("DESIGN 1", "PEACOCK PRISM", "design_1"),
    ("DESIGN 2", "ABYSS GLOWER", "design_2"),
    ("DESIGN 3", "KO GLADIATOR", "design_3"),
    ("DESIGN 4", "CHIBI POW", "design_4"),
    ("DESIGN 5", "EMBER FORGE", "design_5"),
]

PANEL_W, PANEL_H = 220, 392
HERO_BOX = 220


def _source(spec):
    if spec == "skin_mantis_shrimp":
        return "skin_mantis_shrimp"
    return importlib.import_module(f"tools.mantis_shrimp_candidates.{spec}").build


def _label(surf, text, x, y, size, color):
    font = pygame.font.SysFont("dejavusans", size, bold=True)
    surf.blit(font.render(text, True, (8, 6, 14)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def main():
    pad = 16
    head = 64
    cap = 44
    n = len(COLUMNS)
    sheet_w = pad + n * (PANEL_W + pad)
    sheet_h = head + HERO_BOX + cap + PANEL_H + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 26))

    _label(sheet, "MANTIS SHRIMP  ·  full redesign  ·  5 complete concepts",
           pad, 14, 24, (242, 238, 252))

    for i, (tag, name, spec) in enumerate(COLUMNS):
        x = pad + i * (PANEL_W + pad)
        src = _source(spec)
        sheet.blit(nr.hero_panel(src, HERO_BOX), (x + (PANEL_W - HERO_BOX) // 2, head))
        hl = (255, 150, 150) if spec == "skin_mantis_shrimp" else (255, 178, 200)
        _label(sheet, tag, x + 6, head + HERO_BOX + 2, 18, hl)
        _label(sheet, name, x + 6, head + HERO_BOX + 23, 14, (236, 236, 244))
        sheet.blit(nr.gameplay_panel(src, PANEL_W, PANEL_H), (x, head + HERO_BOX + cap))

    out = "docs/store_redesign/animal/mantis_shrimp/final_comparison.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
