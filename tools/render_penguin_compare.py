"""Final comparison figure for the PENGUIN redesign exploration.

Six columns — the ORIGINAL live penguin (the flat ``skin_penguin``) plus the
five explored designs — each Pip mid-flight over the same real gameplay biome
scene. Pure capture; touches no production art (the five candidates are scratch
builders under tools/penguin_candidates/, the original is the live
``skin_penguin``).

Run headless from repo root:
``PYTHONPATH=. SDL_VIDEODRIVER=dummy python tools/render_penguin_compare.py``.
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
    ("ORIGINAL", "PENGUIN", "skin_penguin"),
    ("DESIGN 1", "ADÉLIE", "design_1"),
    ("DESIGN 2", "GENTOO", "design_2"),
    ("DESIGN 3", "EMPEROR", "design_3"),
    ("DESIGN 4", "ROCKHOPPER", "design_4"),
    ("DESIGN 5", "BABY CHICK", "design_5"),
]

PANEL_W, PANEL_H = 220, 392


def _source(spec):
    if spec == "skin_penguin":
        return "skin_penguin"
    return importlib.import_module(f"tools.penguin_candidates.{spec}").build


def _label(surf, text, x, y, size, color):
    font = pygame.font.SysFont("dejavusans", size, bold=True)
    surf.blit(font.render(text, True, (8, 6, 14)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


HERO_BOX = 220


def main():
    pad = 16
    head = 64
    cap = 44                      # caption strip under each hero
    n = len(COLUMNS)
    sheet_w = pad + n * (PANEL_W + pad)
    sheet_h = head + HERO_BOX + cap + PANEL_H + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 26))

    _label(sheet, "PENGUIN  ·  redesign comparison  ·  hero close-up + Pip mid-flight",
           pad, 14, 24, (242, 238, 252))

    for i, (tag, name, spec) in enumerate(COLUMNS):
        x = pad + i * (PANEL_W + pad)
        src = _source(spec)
        # Row 1 — large hero close-up so the craft reads.
        hero = nr.hero_panel(src, HERO_BOX)
        sheet.blit(hero, (x + (PANEL_W - HERO_BOX) // 2, head))
        # captions
        _label(sheet, tag, x + 6, head + HERO_BOX + 2, 18,
               (255, 224, 130) if tag == "ORIGINAL" else (190, 220, 255))
        _label(sheet, name, x + 6, head + HERO_BOX + 23, 16, (236, 236, 244))
        # Row 2 — Pip mid-flight in a real gameplay scene.
        panel = nr.gameplay_panel(src, PANEL_W, PANEL_H)
        sheet.blit(panel, (x, head + HERO_BOX + cap))

    out = "docs/store_redesign/animal/penguin/final_comparison.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
