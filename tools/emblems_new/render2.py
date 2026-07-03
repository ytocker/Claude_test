"""Headless candidate-sheet renderer for BATCH 2 of the Hall-of-Fame emblems.

Patches the nine batch-2 glyphs into the live glyph table, renders each as a
200px HERO plus a 44px row-size chip (both inside the real gold olive-laurel
wreath, unlocked/gold), and tiles them in a labelled 3x3 grid so the design loop
can judge read + crispness at both scales.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python tools/emblems_new/render2.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.font.init()

import game.achievement_icons as ai
from tools.emblems_new.batch2 import GLYPHS

ai._GLYPHS.update(GLYPHS)

# id → (title, one-line desc) for the sheet captions.
META = [
    ("overloaded", "Overloaded", "3 power-ups active at once"),
    ("bullet_time", "Bullet Time", "10 pillars in one Slow-Mo"),
    ("ghost_rider", "Ghost Rider", "phase 8 pillars in one Ghost"),
    ("regifted", "Regifted", "Surprise Box repeats a roll"),
    ("read_fine_print", "Read the Fine Print", "scroll to the very bottom"),
    ("morbid_curiosity", "Morbid Curiosity", "visit the Hall of Shame"),
    ("are_you_still_there", "Are You Still There?", "idle 5 min on the menu"),
    ("lucky_sevens", "Lucky Sevens", "end a run on exactly 777"),
    ("palindrome", "Palindrome", "end on a palindromic score"),
]

HERO, CHIP = 200, 44
COLS = 3
PAD = 22
CELL_W = HERO + 74
CELL_H = HERO + 74
title_f = pygame.font.SysFont(None, 34, bold=True)
id_f = pygame.font.SysFont(None, 24, bold=True)
desc_f = pygame.font.SysFont(None, 19)
tag_f = pygame.font.SysFont(None, 17, bold=True)

rows = (len(META) + COLS - 1) // COLS
banner_h = 52
W = COLS * CELL_W + PAD
H = banner_h + rows * CELL_H + PAD

sheet = pygame.Surface((W, H))
# match the achievements screen's deep navy so the gold reads true.
for yy in range(H):
    t = yy / max(1, H - 1)
    pygame.draw.line(sheet, (int(9 + 9 * t), int(7 + 6 * t), int(26 + 16 * t)),
                     (0, yy), (W, yy))

cap = title_f.render("Hall of Fame — BATCH 2 emblems  ·  round 1", True, (236, 200, 120))
sheet.blit(cap, (PAD, 14))

for idx, (key, title, desc) in enumerate(META):
    r, c = divmod(idx, COLS)
    x0 = PAD + c * CELL_W
    y0 = banner_h + r * CELL_H

    hero = ai.get_badge(key, HERO, True, False, "gold")
    sheet.blit(hero, (x0, y0))

    # 44px chip parked in the hero's lower-right, on a subtle plate, with a
    # "44px" tag so the row-size read is judged beside the hero.
    chip = ai.get_badge(key, CHIP, True, False, "gold")
    chx, chy = x0 + HERO - CHIP - 2, y0 + HERO - CHIP - 2
    plate = pygame.Surface((CHIP + 8, CHIP + 8), pygame.SRCALPHA)
    plate.fill((0, 0, 0, 90))
    sheet.blit(plate, (chx - 4, chy - 4))
    sheet.blit(chip, (chx, chy))
    tag = tag_f.render("44px", True, (210, 210, 230))
    sheet.blit(tag, (chx + CHIP // 2 - tag.get_width() // 2, chy - 16))

    # captions under the hero.
    it = id_f.render(title, True, (240, 214, 140))
    sheet.blit(it, (x0 + HERO // 2 - it.get_width() // 2, y0 + HERO + 6))
    dt = desc_f.render(desc, True, (196, 198, 218))
    sheet.blit(dt, (x0 + HERO // 2 - dt.get_width() // 2, y0 + HERO + 32))
    kt = tag_f.render(key, True, (150, 150, 172))
    sheet.blit(kt, (x0 + HERO // 2 - kt.get_width() // 2, y0 + HERO + 52))

out = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "docs", "emblems_new", "batch2", "sheet.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
