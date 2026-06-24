"""Final comparison for the SKELETON v3 round — faithful skeletons of Pip.

Four columns, each Pip mid-flight over the same real gameplay biome scene:
  ORIGINAL PARROT (live default macaw — the silhouette reference)
  BONEWHITE-MACAW (v2 design_1 — the prior winner this round is rooted in)
  DESIGN A · CLEAN (v3_design_1 — iconic, sparse)
  DESIGN B · X-RAY (v3_design_2 — full anatomy)

Pure capture; touches no production art. Run headless from repo root:
``SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/render_skeleton_v3_compare.py``.
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

# (tag, name, source) — source is a registered sid string OR a build callable.
COLUMNS = [
    ("ORIGINAL", "PIP (reference)", "default"),
    ("PRIOR WINNER", "BONEWHITE-MACAW", "v2_design_1"),
    ("DESIGN A", "CLEAN", "v3_design_1"),
    ("DESIGN B", "X-RAY", "v3_design_2"),
]


def _source(spec):
    if spec == "default":
        return "default"
    return importlib.import_module(f"tools.skeleton_candidates.{spec}").build


PANEL_W, PANEL_H = 230, 400
PAD, GUTTER = 26, 18
TITLE_H, CAP_H = 78, 56
n = len(COLUMNS)

sheet_w = PAD * 2 + n * PANEL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + PANEL_H + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(30, True).render(
    "SKELETON v3 — faithful skeleton of the ORIGINAL Pip (CLEAN vs X-RAY, in gameplay)",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 22)))

name_font = _font(17, True)
tag_font = _font(13, True)

for i, (tag, name, spec) in enumerate(COLUMNS):
    x = PAD + i * (PANEL_W + GUTTER)
    y = TITLE_H
    panel = nr.gameplay_panel(_source(spec), PANEL_W, PANEL_H)
    border = (210, 80, 80) if spec == "default" else (
        (120, 170, 210) if spec == "v2_design_1" else (*_GOLD_DEEP,))
    pygame.draw.rect(sheet, border, pygame.Rect(x - 2, y - 2, PANEL_W + 4, PANEL_H + 4), width=2)
    sheet.blit(panel, (x, y))
    cy = y + PANEL_H + 8
    sheet.blit(tag_font.render(tag, True, (170, 162, 190)), (x + 2, cy))
    sheet.blit(name_font.render(name, True, _GOLD_PALE), (x + 2, cy + 18))

out = os.path.join("docs", "store_redesign", "costume", "skeleton", "v3", "final_comparison.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
