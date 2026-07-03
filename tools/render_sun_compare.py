"""Comparison figure for the SUN secret item.

Top row: a hero close-up of the ORIGINAL pufferfish star-burst (the art this item
is born from) + the five sun designs. Bottom row: each Pip mid-flight over the
same real gameplay biome scene. Pure capture; the candidates are scratch builders
under tools/sun_candidates/.

Run: ``PYTHONPATH=. SDL_VIDEODRIVER=dummy python tools/render_sun_compare.py``
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
    ("ORIGIN", "PUFFER STAR-BURST", "_origin"),
    ("DESIGN 1", "CLASSIC SUNFACE", "design_1"),
    ("DESIGN 2", "BLAZING", "design_2"),
    ("DESIGN 3", "SYNTHWAVE", "design_3"),
    ("DESIGN 4", "KAWAII", "design_4"),
    ("DESIGN 5", "SOLAR DEITY", "design_5"),
]

PANEL_W, PANEL_H = 220, 392
HERO_BOX = 220


def _source(spec):
    if spec == "_origin":
        return importlib.import_module(
            "tools.sun_candidates._original_puffer_ref").get_pufferfish
    return importlib.import_module(f"tools.sun_candidates.{spec}").build


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

    _label(sheet, "SUN  ·  secret item  ·  born from the original pufferfish star-burst",
           pad, 14, 24, (242, 238, 252))

    for i, (tag, name, spec) in enumerate(COLUMNS):
        x = pad + i * (PANEL_W + pad)
        src = _source(spec)
        hero = nr.hero_panel(src, HERO_BOX)
        sheet.blit(hero, (x + (PANEL_W - HERO_BOX) // 2, head))
        _label(sheet, tag, x + 6, head + HERO_BOX + 2, 18,
               (255, 224, 130) if tag == "ORIGIN" else (255, 214, 120))
        _label(sheet, name, x + 6, head + HERO_BOX + 23, 14, (236, 236, 244))
        panel = nr.gameplay_panel(src, PANEL_W, PANEL_H)
        sheet.blit(panel, (x, head + HERO_BOX + cap))

    out = "docs/store_redesign/animal/sun/final_comparison.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
