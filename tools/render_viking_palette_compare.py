"""Comparison figure for the plain-Viking palette recolors of design_4.

Columns: the FROSTREAVER base (design_4) plus the five de-frosted plain-Viking
palette variants, each Pip mid-flight over the same real gameplay biome scene.
Pure capture; no production art touched — all builders are scratch modules
under tools/.

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_viking_palette_compare.py``.
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
    ("BASE", "FROSTREAVER", "tools.viking_candidates.design_4"),
    ("V1", "IRONCLAD", "tools.viking_palette_candidates.v1"),
    ("V2", "BLOODAXE", "tools.viking_palette_candidates.v2"),
    ("V3", "STORMGREY", "tools.viking_palette_candidates.v3"),
    ("V4", "WOADGREEN", "tools.viking_palette_candidates.v4"),
    ("V5", "GOLDMANE", "tools.viking_palette_candidates.v5"),
]

PANEL_W, PANEL_H = 220, 392
PAD, GUTTER = 26, 18
TITLE_H, CAP_H = 76, 56
n = len(COLUMNS)

sheet_w = PAD * 2 + n * PANEL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + PANEL_H + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(30, True).render(
    "VIKING (design 4) — FROST BASE vs. 5 PLAIN PALETTES (in gameplay)",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 22)))

name_font = _font(17, True)
tag_font = _font(13, True)

for i, (tag, name, modname) in enumerate(COLUMNS):
    x = PAD + i * (PANEL_W + GUTTER)
    y = TITLE_H
    build = importlib.import_module(modname).build
    panel = nr.gameplay_panel(build, PANEL_W, PANEL_H)
    border = (120, 170, 210) if tag == "BASE" else (*_GOLD_DEEP,)
    pygame.draw.rect(sheet, border, pygame.Rect(x - 2, y - 2, PANEL_W + 4, PANEL_H + 4), width=2)
    sheet.blit(panel, (x, y))
    cy = y + PANEL_H + 8
    sheet.blit(tag_font.render(tag, True, (170, 162, 190)), (x + 2, cy))
    sheet.blit(name_font.render(name, True, _GOLD_PALE), (x + 2, cy + 18))

out = os.path.join("docs", "store_redesign", "costume", "viking", "palette", "final_comparison.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
