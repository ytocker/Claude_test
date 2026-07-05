"""Snapshot of every skin in the costume group as it exists in production today.

5 columns × 3 rows grid, each Pip mid-flight over a real gameplay biome scene.
Titles show the display name and coin cost from the catalog.

Run headless from repo root:
  SDL_VIDEODRIVER=dummy python tools/render_costumes_all.py
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

import tools.ninja_render as nr
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP
from game.store_catalog import CATALOG

COSTUME_ITEMS = [
    (sid, CATALOG[sid]["name"], CATALOG[sid]["cost"])
    for sid in CATALOG
    if CATALOG[sid].get("group") == "costume"
]

COLS = 5
ROWS = (len(COSTUME_ITEMS) + COLS - 1) // COLS

PANEL_W, PANEL_H = 200, 358
PAD, GUTTER = 24, 16
TITLE_H, CAP_H = 72, 52

sheet_w = PAD * 2 + COLS * PANEL_W + (COLS - 1) * GUTTER
sheet_h = TITLE_H + ROWS * (PANEL_H + CAP_H) + (ROWS - 1) * GUTTER + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title_surf = _font(28, True).render(
    f"ALL COSTUME SKINS — {len(COSTUME_ITEMS)} items (current production)",
    True, _GOLD_PALE)
sheet.blit(title_surf, title_surf.get_rect(midtop=(sheet_w // 2, 20)))

name_font = _font(15, True)
tag_font  = _font(12, True)

for idx, (sid, name, cost) in enumerate(COSTUME_ITEMS):
    col = idx % COLS
    row = idx // COLS
    x = PAD + col * (PANEL_W + GUTTER)
    y = TITLE_H + row * (PANEL_H + CAP_H + GUTTER)

    panel = nr.gameplay_panel(sid, PANEL_W, PANEL_H)
    pygame.draw.rect(sheet, _GOLD_DEEP,
                     pygame.Rect(x - 2, y - 2, PANEL_W + 4, PANEL_H + 4), width=2)
    sheet.blit(panel, (x, y))

    cy = y + PANEL_H + 6
    sheet.blit(tag_font.render(f"{cost} coins", True, (150, 142, 170)), (x + 2, cy))
    sheet.blit(name_font.render(name, True, _GOLD_PALE), (x + 2, cy + 17))

out = os.path.join("docs", "store_redesign", "all_costumes.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
