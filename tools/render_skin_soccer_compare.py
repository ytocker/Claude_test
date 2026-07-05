"""Final comparison figure for the soccer player costume exploration.

Six columns side by side — the ORIGINAL base parrot plus the five explored
designs — each Pip mid-flight over the same real gameplay biome scene. Pure
capture; touches no production art (the five candidates are scratch builders
under tools/skin_soccer_candidates/, the original is the live default skin).

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_skin_soccer_compare.py``.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib
import pygame
pygame.init()

import tools.ninja_render as nr
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP

COLUMNS = [
    ("ORIGINAL", "BASE PARROT",    "original"),
    ("DESIGN 1", "THE STRIKER",    "design_1"),
    ("DESIGN 2", "THE GOALKEEPER", "design_2"),
    ("DESIGN 3", "EL CAPITAN",     "design_3"),
    ("DESIGN 4", "FLYING DUTCHMAN","design_4"),
    ("DESIGN 5", "THE DEFENDER",   "design_5"),
]


def _source(spec):
    if spec == "original":
        return "base"          # live default parrot skin
    mod = importlib.import_module(f"tools.skin_soccer_candidates.{spec}")
    return mod.build


PANEL_W, PANEL_H = 220, 392
PAD, GUTTER = 26, 18
TITLE_H, CAP_H = 76, 56
n = len(COLUMNS)

sheet_w = PAD * 2 + n * PANEL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + PANEL_H + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(28, True).render(
    "SOCCER PLAYER — ORIGINAL vs. 5 DESIGNS (in gameplay)",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 22)))

name_font = _font(17, True)
tag_font  = _font(13, True)

for i, (tag, name, spec) in enumerate(COLUMNS):
    x = PAD + i * (PANEL_W + GUTTER)
    y = TITLE_H
    panel = nr.gameplay_panel(_source(spec), PANEL_W, PANEL_H)
    border = (210, 80, 80) if spec == "original" else (*_GOLD_DEEP,)
    pygame.draw.rect(sheet, border,
                     pygame.Rect(x - 2, y - 2, PANEL_W + 4, PANEL_H + 4), width=2)
    sheet.blit(panel, (x, y))
    cy = y + PANEL_H + 8
    tagimg  = tag_font.render(tag,  True, (170, 162, 190))
    nameimg = name_font.render(name, True, _GOLD_PALE)
    sheet.blit(tagimg,  (x + 2, cy))
    sheet.blit(nameimg, (x + 2, cy + 18))

out = os.path.join("docs", "store_redesign", "costume", "skin_soccer",
                   "final_comparison.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
