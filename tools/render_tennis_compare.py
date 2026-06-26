"""Final comparison figure for the higher-fidelity TENNIS exploration.

Six columns — the live shipped ``skin_tennis`` as ORIGINAL plus the five
higher-fidelity candidates — each Pip mid-flight over the same real gameplay
biome scene, so the user can judge the set in context and pick a winner. Pure
capture; touches no production art (all five candidates are scratch builders
under tools/tennis_candidates/).

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_tennis_compare.py``.
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
    ("ORIGINAL", "SHIPPED TENNIS", "skin_tennis"),
    ("DESIGN 1", "WIMBLEDON WHITES", "design_1"),
    ("DESIGN 2", "CLAY COURT", "design_2"),
    ("DESIGN 3", "NEON BASELINER", "design_3"),
    ("DESIGN 4", "RETRO '70s", "design_4"),
    ("DESIGN 5", "NIGHT MATCH", "design_5"),
]


def _source(spec):
    # The ORIGINAL is the live registered skin id (str); candidates are scratch
    # builders. nr resolves either through the same harness.
    if spec.startswith("skin_"):
        return spec
    return importlib.import_module(f"tools.tennis_candidates.{spec}").build


PANEL_W, PANEL_H = 200, 360
PAD, GUTTER = 26, 16
TITLE_H, CAP_H = 76, 56
n = len(COLUMNS)

sheet_w = PAD * 2 + n * PANEL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + PANEL_H + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(32, True).render(
    "TENNIS — ORIGINAL vs 5 HIGHER-FIDELITY VERSIONS (in gameplay)", True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 22)))

name_font = _font(16, True)
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

out = os.path.join("docs", "store_redesign", "costume", "tennis", "final_comparison.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
