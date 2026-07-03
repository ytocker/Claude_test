"""Review sheet for BATCH 3 of the Hall-of-Fame emblems.

Merges ``batch3.GLYPHS`` into a private copy of the live badge glyph table, then
renders each emblem inside the real gold olive-laurel wreath at hero (200px) +
row (44px) size so legibility is judged exactly as it ships.

Run headless:  PYTHONPATH=. SDL_VIDEODRIVER=dummy python tools/emblems_new/render3.py
Out:           docs/emblems_new/batch3/sheet.png
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pygame

pygame.init()
pygame.font.init()

import game.achievement_icons as ai
from tools.emblems_new.batch3 import GLYPHS

ai._GLYPHS.update(GLYPHS)

SPECS = [
    ("after_hours", "Night Owl", "after midnight"),
    ("early_bird", "Early Bird", "before 6 a.m."),
    ("leap_of_faith", "Leap of Faith", "Feb 29th"),
    ("auld_lang_syne", "Auld Lang Syne", "New Year's Day"),
    ("the_completionist", "The Completionist", "every other badge"),
    ("many_happy_returns", "Many Happy Returns", "a year later"),
    ("creature_of_habit", "Creature of Habit", "seven days"),
    ("the_grind", "The Grind", "100 runs"),
    ("never_say_die", "Never Say Die", "1,000 crashes"),
]

HERO = 200
ROW = 44
COLS = 3
PAD = 26
LBL = 46
CELL_W = HERO + PAD
CELL_H = HERO + LBL + PAD
BG = (16, 14, 30)

f_title = pygame.font.SysFont("dejavusans", 30, bold=True)
f_id = pygame.font.SysFont("dejavusans", 21, bold=True)
f_desc = pygame.font.SysFont("dejavusans", 17)
f_small = pygame.font.SysFont("dejavusans", 15)

rows = (len(SPECS) + COLS - 1) // COLS
W = COLS * CELL_W + PAD
H = 70 + rows * CELL_H + PAD

sheet = pygame.Surface((W, H))
sheet.fill(BG)
sheet.blit(f_title.render("Hall of Fame — Batch 3 emblems (round 1)", True,
                          (240, 224, 160)), (PAD, 22))

for i, (key, title, desc) in enumerate(SPECS):
    col = i % COLS
    row = i // COLS
    x = PAD + col * CELL_W
    y = 70 + row * CELL_H

    hero = ai.get_badge(key, HERO, True, False, "gold")
    sheet.blit(hero, (x, y))

    # 44px chip inset on the hero's lower-right so the true row size is judged
    # against the same wreath — with a soft plate behind it.
    chip = ai.get_badge(key, ROW, True, False, "gold")
    cxp, cyp = x + HERO - ROW - 6, y + HERO - ROW - 6
    pygame.draw.rect(sheet, (30, 26, 48),
                     (cxp - 4, cyp - 4, ROW + 8, ROW + 8), border_radius=6)
    sheet.blit(chip, (cxp, cyp))

    ty = y + HERO + 6
    sheet.blit(f_id.render(title, True, (236, 236, 244)), (x, ty))
    sheet.blit(f_desc.render(desc, True, (176, 176, 200)), (x, ty + 22))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                   "docs", "emblems_new", "batch3", "sheet.png")
out = os.path.abspath(out)
pygame.image.save(sheet, out)
print("wrote", out, sheet.get_size())
