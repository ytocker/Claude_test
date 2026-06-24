"""Comparison figure for the SKELETON v2 (parrot-anatomy) exploration.

Seven columns — the two PICKED v1 references (BONEWHITE, DEADMAN'S FLAG, shown
UNCHANGED) plus the five new parrot-skeleton designs — each Pip mid-flight over
the same real gameplay biome scene. Pure capture; no production art touched (all
columns are scratch builders under tools/skeleton_candidates/).

Run headless from repo root:
``SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/render_skeleton_v2_compare.py``.
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

# (tag, name, module-under-tools.skeleton_candidates)
COLUMNS = [
    ("REF · v1", "BONEWHITE", "design_1"),
    ("REF · v1", "DEADMAN'S FLAG", "design_4"),
    ("DESIGN 1", "BONEWHITE-MACAW", "v2_design_1"),
    ("DESIGN 2", "PIRATE-MACAW", "v2_design_2"),
    ("DESIGN 3", "CALAVERA-MACAW", "v2_design_3"),
    ("DESIGN 4", "WISP-MACAW", "v2_design_4"),
    ("DESIGN 5", "AUREX-MACAW", "v2_design_5"),
]

PANEL_W, PANEL_H = 210, 384
PAD, GUTTER = 24, 16
TITLE_H, CAP_H = 76, 56
n = len(COLUMNS)

sheet_w = PAD * 2 + n * PANEL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + PANEL_H + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(30, True).render(
    "SKELETON v2 — 2 picked references + 5 PARROT-skeleton designs (in gameplay)",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 22)))

name_font = _font(16, True)
tag_font = _font(13, True)

for i, (tag, name, spec) in enumerate(COLUMNS):
    x = PAD + i * (PANEL_W + GUTTER)
    y = TITLE_H
    build = importlib.import_module(f"tools.skeleton_candidates.{spec}").build
    panel = nr.gameplay_panel(build, PANEL_W, PANEL_H)
    border = (120, 170, 210) if tag.startswith("REF") else (*_GOLD_DEEP,)
    pygame.draw.rect(sheet, border, pygame.Rect(x - 2, y - 2, PANEL_W + 4, PANEL_H + 4), width=2)
    sheet.blit(panel, (x, y))
    cy = y + PANEL_H + 8
    sheet.blit(tag_font.render(tag, True, (170, 162, 190)), (x + 2, cy))
    sheet.blit(name_font.render(name, True, _GOLD_PALE), (x + 2, cy + 18))

out = os.path.join("docs", "store_redesign", "costume", "skeleton", "v2", "final_comparison.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
