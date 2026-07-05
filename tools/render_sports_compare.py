"""Comparison figure for the SPORTS pro-athlete costume collection.

Five columns — the five sport candidates — each Pip mid-flight over the same
real gameplay biome scene, so the user can judge the collection in context and
pick which to add as new store costumes. Pure capture; touches no production art
(all five are scratch builders under tools/sports_candidates/).

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_sports_compare.py``.
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
    ("DESIGN 1", "SOCCER", "design_1"),
    ("DESIGN 2", "BASKETBALL", "design_2"),
    ("DESIGN 3", "FOOTBALL", "design_3"),
    ("DESIGN 4", "BASEBALL", "design_4"),
    ("DESIGN 5", "TENNIS", "design_5"),
]


def _source(spec):
    return importlib.import_module(f"tools.sports_candidates.{spec}").build


PANEL_W, PANEL_H = 220, 392
PAD, GUTTER = 26, 18
TITLE_H, CAP_H = 76, 56
n = len(COLUMNS)

sheet_w = PAD * 2 + n * PANEL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + PANEL_H + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(32, True).render(
    "SPORTS COLLECTION — 5 PRO-ATHLETE COSTUMES (in gameplay)", True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 22)))

name_font = _font(17, True)
tag_font = _font(13, True)

for i, (tag, name, spec) in enumerate(COLUMNS):
    x = PAD + i * (PANEL_W + GUTTER)
    y = TITLE_H
    panel = nr.gameplay_panel(_source(spec), PANEL_W, PANEL_H)
    pygame.draw.rect(sheet, (*_GOLD_DEEP,), pygame.Rect(x - 2, y - 2, PANEL_W + 4, PANEL_H + 4), width=2)
    sheet.blit(panel, (x, y))
    cy = y + PANEL_H + 8
    sheet.blit(tag_font.render(tag, True, (170, 162, 190)), (x + 2, cy))
    sheet.blit(name_font.render(name, True, _GOLD_PALE), (x + 2, cy + 18))

out = os.path.join("docs", "store_redesign", "costume", "sports", "final_comparison.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
