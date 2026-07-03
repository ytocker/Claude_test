"""Focused comparison: base parrot vs. D1 Captain (R3) vs. D2 Ace (R3).

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python -m tools.render_pilot_compare_r3``.
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
    ("ORIGINAL",  "BASE PARROT",   "skin_base"),
    ("DESIGN 1",  "THE CAPTAIN",   "design_1"),
    ("DESIGN 2",  "ACE",           "design_2"),
]


def _source(spec):
    if spec == "skin_base":
        return "skin_base"
    mod = importlib.import_module(f"tools.pilot_candidates.{spec}")
    return mod.build


PANEL_W, PANEL_H = 280, 498
HERO_BOX = 280
HERO_GAP = 12
PAD, GUTTER = 26, 18
TITLE_H, CAP_H = 72, 54
n = len(COLUMNS)

sheet_w = PAD * 2 + n * PANEL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + PANEL_H + HERO_GAP + HERO_BOX + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(28, True).render(
    "PILOT COSTUME R3 — PARROT IN COSTUME (no recolor)",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 20)))

name_font = _font(14, True)
tag_font  = _font(12, True)

for i, (tag, name, spec) in enumerate(COLUMNS):
    src = _source(spec)
    x = PAD + i * (PANEL_W + GUTTER)

    y = TITLE_H
    panel = nr.gameplay_panel(src, PANEL_W, PANEL_H)
    border = (170, 170, 170) if spec == "skin_base" else (*_GOLD_DEEP,)
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
    sheet.blit(nameimg, (x + 2, cy + 18))

out = os.path.join("docs", "store_redesign", "costume", "pilot",
                   "comparison_r3.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
