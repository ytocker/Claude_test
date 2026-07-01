"""Final comparison figure for the soccer costume redesign exploration.

Seven columns — the ORIGINAL sports soccer design plus the five explored
designs — each Pip mid-flight over the same real gameplay biome scene.

Run headless from repo root:
    SDL_VIDEODRIVER=dummy python tools/render_soccer_compare.py
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
    ("ORIGINAL", "OLD SOCCER", "orig"),
    ("DESIGN 1", "THE KIT", "design_1"),
    ("DESIGN 2", "FREE-KICK WALL", "design_2"),
    ("DESIGN 3", "STREET BALLER", "design_3"),
    ("DESIGN 4", "ULTRAS CAPTAIN", "design_4"),
    ("DESIGN 5", "GOLDEN WHISTLE", "design_5"),
]


def _source(spec):
    if spec == "orig":
        return importlib.import_module("tools.sports_candidates.design_1").build
    return importlib.import_module(f"tools.soccer_candidates.{spec}").build


PANEL_W, PANEL_H = 220, 392
PAD, GUTTER = 26, 14
TITLE_H, CAP_H = 80, 56
n = len(COLUMNS)

sheet_w = PAD * 2 + n * PANEL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + PANEL_H + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(28, True).render(
    "SOCCER REDESIGN — ORIGINAL vs. 5 NEW DESIGNS (in gameplay)", True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 24)))

name_font = _font(14, True)
tag_font = _font(12, True)

for i, (tag, name, spec) in enumerate(COLUMNS):
    x = PAD + i * (PANEL_W + GUTTER)
    y = TITLE_H
    panel = nr.gameplay_panel(_source(spec), PANEL_W, PANEL_H)
    border = (110, 160, 90) if spec == "orig" else (*_GOLD_DEEP,)
    pygame.draw.rect(sheet, border, pygame.Rect(x - 2, y - 2, PANEL_W + 4, PANEL_H + 4), width=2)
    sheet.blit(panel, (x, y))
    cy = y + PANEL_H + 8
    sheet.blit(tag_font.render(tag, True, (170, 162, 190)), (x + 2, cy))
    sheet.blit(name_font.render(name, True, _GOLD_PALE), (x + 2, cy + 18))

os.makedirs("docs/store_redesign/costume/soccer", exist_ok=True)
out = "docs/store_redesign/costume/soccer/final_comparison.png"
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
