"""Comparison figure for the astronaut v2 sibling round.

Five columns — the two picked inspirations (MOONWALKER, STARLINER) plus the three
new siblings (ARTEMIS, TRAILBLAZER, NOVA DRIFTER) — each Pip mid-flight over the
same real gameplay biome scene. Pure capture; no production art touched (all are
scratch builders under tools/astronaut_candidates/).

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_astronaut_v2_compare.py``.
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

# (tag, name, design module)
COLUMNS = [
    ("INSPIRATION", "MOONWALKER", "design_1"),
    ("INSPIRATION", "STARLINER", "design_5"),
    ("NEW · 6", "ARTEMIS", "design_6"),
    ("NEW · 7", "TRAILBLAZER", "design_7"),
    ("NEW · 8", "NOVA DRIFTER", "design_8"),
]

PANEL_W, PANEL_H = 230, 410
PAD, GUTTER = 26, 18
TITLE_H, CAP_H = 76, 56
n = len(COLUMNS)

sheet_w = PAD * 2 + n * PANEL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + PANEL_H + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(30, True).render(
    "ASTRONAUT v2 — 2 picked inspirations + 3 new siblings (in gameplay)",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 22)))

name_font = _font(17, True)
tag_font = _font(13, True)

for i, (tag, name, spec) in enumerate(COLUMNS):
    x = PAD + i * (PANEL_W + GUTTER)
    y = TITLE_H
    build = importlib.import_module(f"tools.astronaut_candidates.{spec}").build
    panel = nr.gameplay_panel(build, PANEL_W, PANEL_H)
    border = (120, 170, 210) if tag == "INSPIRATION" else (*_GOLD_DEEP,)
    pygame.draw.rect(sheet, border, pygame.Rect(x - 2, y - 2, PANEL_W + 4, PANEL_H + 4), width=2)
    sheet.blit(panel, (x, y))
    cy = y + PANEL_H + 8
    sheet.blit(tag_font.render(tag, True, (170, 162, 190)), (x + 2, cy))
    sheet.blit(name_font.render(name, True, _GOLD_PALE), (x + 2, cy + 18))

out = os.path.join("docs", "store_redesign", "costume", "astronaut", "v2_comparison.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
