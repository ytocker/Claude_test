"""Disco costume redesign comparison — ORIGINAL vs 5 candidates (R2 finals).

Run headless from repo root:
  SDL_VIDEODRIVER=dummy python -m tools.render_disco_compare
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
    ("ORIGINAL",  "DISCO",          "skin_disco"),
    ("DESIGN 1",  "BOOGIE NIGHTS",  "design_1"),
    ("DESIGN 2",  "STARDUST DIVA",  "design_2"),
    ("DESIGN 3",  "ROLLER GROOVE",  "design_3"),
    ("DESIGN 4",  "THE SELECTOR",   "design_4"),
    ("DESIGN 5",  "MIRRORBALL",     "design_5"),
]


def _source(spec):
    if spec == "skin_disco":
        return spec
    mod = importlib.import_module(f"tools.disco_candidates.{spec}")
    return mod.build


PANEL_W, PANEL_H = 200, 360
HERO_BOX = 200
HERO_GAP = 10
PAD, GUTTER = 20, 14
TITLE_H, CAP_H = 64, 48
n = len(COLUMNS)

sheet_w = PAD * 2 + n * PANEL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + PANEL_H + HERO_GAP + HERO_BOX + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(22, True).render(
    "DISCO REDESIGN — ORIGINAL vs DESIGNS 1–5 (R2 FINALS)",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 18)))

name_font = _font(13, True)
tag_font  = _font(11, True)

for i, (tag, name, spec) in enumerate(COLUMNS):
    src = _source(spec)
    x = PAD + i * (PANEL_W + GUTTER)

    y = TITLE_H
    panel = nr.gameplay_panel(src, PANEL_W, PANEL_H)
    border = (170, 170, 170) if spec == "skin_disco" else (*_GOLD_DEEP,)
    pygame.draw.rect(sheet, border,
                     pygame.Rect(x - 2, y - 2, PANEL_W + 4, PANEL_H + 4), width=2)
    sheet.blit(panel, (x, y))

    hy = y + PANEL_H + HERO_GAP
    hero = nr.hero_panel(src, HERO_BOX, tilt=0.0)
    pygame.draw.rect(sheet, border,
                     pygame.Rect(x - 2, hy - 2, HERO_BOX + 4, HERO_BOX + 4), width=2)
    sheet.blit(hero, (x, hy))

    cy = hy + HERO_BOX + 6
    tagimg  = tag_font.render(tag,  True, (170, 162, 190))
    nameimg = name_font.render(name, True, _GOLD_PALE)
    sheet.blit(tagimg,  (x + 2, cy))
    sheet.blit(nameimg, (x + 2, cy + 16))

out = os.path.join("docs", "store_redesign", "costume", "disco", "final_comparison.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
