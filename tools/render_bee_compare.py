"""Final comparison figure for the bug/insect bee-slot redesign.

Six columns: ORIGINAL live skin_bee + five new insect designs, each Pip
mid-flight over the same real gameplay biome scene.

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_bee_compare.py``
"""
from __future__ import annotations
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib
import pygame
pygame.init()

import tools.ninja_render as nr
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP

COLUMNS = [
    ("ORIGINAL",  "CURRENT BEE",    "skin_bee"),
    ("DESIGN 1",  "AZUREWING",      "design_1"),
    ("DESIGN 2",  "EMBERGLOW",      "design_2"),
    ("DESIGN 3",  "IRONHORN",       "design_3"),
    ("DESIGN 4",  "GLINTWING",      "design_4"),
    ("DESIGN 5",  "STINGREEL",      "design_5"),
]


def _source(spec):
    if spec == "skin_bee":
        return "skin_bee"
    mod = importlib.import_module(f"tools.bee_candidates.{spec}")
    return mod.build


PANEL_W, PANEL_H = 220, 392
PAD, GUTTER = 26, 18
TITLE_H, CAP_H = 80, 56
n = len(COLUMNS)

sheet_w = PAD * 2 + n * PANEL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + PANEL_H + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(24, True).render(
    "BUG/INSECT REDESIGN  ·  ORIGINAL vs. 5 NEW DESIGNS",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 16)))

subtitle = _font(13).render(
    "Azurewing · Emberglow · Ironhorn · Glintwing · Stingreel  ·  R2 finals",
    True, (200, 195, 230))
sheet.blit(subtitle, subtitle.get_rect(midtop=(sheet_w // 2, 50)))

name_font = _font(15, True)
tag_font  = _font(12, True)

for i, (tag, name, spec) in enumerate(COLUMNS):
    x = PAD + i * (PANEL_W + GUTTER)
    y = TITLE_H
    panel = nr.gameplay_panel(_source(spec), PANEL_W, PANEL_H)
    border = (210, 80, 80) if spec == "skin_bee" else (*_GOLD_DEEP,)
    pygame.draw.rect(sheet, border,
                     pygame.Rect(x - 2, y - 2, PANEL_W + 4, PANEL_H + 4), width=2)
    sheet.blit(panel, (x, y))
    cy = y + PANEL_H + 8
    tagimg = tag_font.render(tag, True, (170, 162, 190))
    sheet.blit(tagimg, (x + 2, cy))
    nameimg = name_font.render(name, True, _GOLD_PALE)
    sheet.blit(nameimg, (x + 2, cy + 18))

out = os.path.join("docs", "store_redesign", "animal", "bee",
                   "final_comparison.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
