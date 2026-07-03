"""All-designs comparison figure for the zombie redesign exploration.

Eleven columns — the ORIGINAL live zombie plus all ten explored designs —
each Pip mid-flight over the same real gameplay biome scene.

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python -m tools.render_zombie_compare_all``.
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
    ("ORIGINAL", "CURRENT ZOMBIE",       "skin_zombie"),
    ("DESIGN 1",  "ROADKILL FRESH",       "design_1"),
    ("DESIGN 2",  "ANCIENT CRYPT ROT",    "design_2"),
    ("DESIGN 3",  "VOODOO HEX BIRD",      "design_3"),
    ("DESIGN 4",  "LAB SPECIMEN #7",      "design_4"),
    ("DESIGN 5",  "BLOATED GAS-BAG",      "design_5"),
    ("DESIGN 6",  "SPORE-BURST FUNGAL",   "design_6"),
    ("DESIGN 7",  "CHARRED EMBER",        "design_7"),
    ("DESIGN 8",  "BARNACLE DROWNED",     "design_8"),
    ("DESIGN 9",  "TRENCH-DEAD SOLDIER",  "design_9"),
    ("DESIGN 10", "GREASEPAINT JESTER",   "design_10"),
]


def _source(spec):
    if spec == "skin_zombie":
        return "skin_zombie"
    mod = importlib.import_module(f"tools.zombie_candidates.{spec}")
    return mod.build


PANEL_W, PANEL_H = 160, 285
PAD, GUTTER = 18, 12
TITLE_H, CAP_H = 68, 48
n = len(COLUMNS)

sheet_w = PAD * 2 + n * PANEL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + PANEL_H + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(26, True).render(
    "ZOMBIE REDESIGN — ORIGINAL + ALL 10 DESIGNS (in gameplay)",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 18)))

name_font = _font(11, True)
tag_font  = _font(10, True)

for i, (tag, name, spec) in enumerate(COLUMNS):
    x = PAD + i * (PANEL_W + GUTTER)
    y = TITLE_H
    panel = nr.gameplay_panel(_source(spec), PANEL_W, PANEL_H)
    border = (210, 80, 80) if spec == "skin_zombie" else (*_GOLD_DEEP,)
    pygame.draw.rect(sheet, border,
                     pygame.Rect(x - 2, y - 2, PANEL_W + 4, PANEL_H + 4), width=2)
    sheet.blit(panel, (x, y))
    cy = y + PANEL_H + 6
    tagimg  = tag_font.render(tag,  True, (170, 162, 190))
    nameimg = name_font.render(name, True, _GOLD_PALE)
    sheet.blit(tagimg,  (x + 2, cy))
    sheet.blit(nameimg, (x + 2, cy + 14))

out = os.path.join("docs", "store_redesign", "costume", "zombie",
                   "final_comparison_all.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
