"""BATCH 1 review sheet — render each new Hall-of-Fame emblem at hero (200px)
and row (44px) size inside the live GOLD laurel wreath, labelled with its title.

Run headless: PYTHONPATH=. SDL_VIDEODRIVER=dummy python tools/emblems_new/render1.py
"""
import os

import pygame

pygame.init()
pygame.font.init()

import game.achievement_icons as ai
from tools.emblems_new.batch1 import GLYPHS

ai._GLYPHS.update(GLYPHS)

# id, title
EMBLEMS = [
    ("sky_legend", "Sky Legend", "Pass 250 pillars in one run"),
    ("quad_digits", "Quadruple Digits", "Reach a score of 1,000"),
    ("weeklong_bender", "Weeklong Bender", "Survive seven day cycles"),
    ("purist", "Purist", "100 pillars, no power-up"),
    ("millionaire", "Millionaire", "Collect 1,000,000 coins"),
    ("power_overwhelming", "Power Overwhelming", "Collect 2,500 power-ups"),
    ("overachiever", "Overachiever", "20 power-ups in one run"),
    ("kitchen_sink", "Kitchen Sink", "Use all six power-ups"),
    ("endless", "Endless", "Ten minutes airborne"),
]

HERO = 200
ROW = 44
COLS = 3
CELL_W = 300
CELL_H = 268
PAD = 26

title_f = pygame.font.SysFont(None, 26, bold=True)
desc_f = pygame.font.SysFont(None, 20)
tag_f = pygame.font.SysFont(None, 18)

rows = (len(EMBLEMS) + COLS - 1) // COLS
W = COLS * CELL_W + PAD
H = rows * CELL_H + PAD + 46

surf = pygame.Surface((W, H))
surf.fill((18, 15, 32))

head = pygame.font.SysFont(None, 34, bold=True).render(
    "Hall of Fame — BATCH 1 (round 1)", True, (236, 206, 128))
surf.blit(head, (PAD, 14))

for i, (eid, title, desc) in enumerate(EMBLEMS):
    col = i % COLS
    row = i // COLS
    x = PAD + col * CELL_W
    y = 56 + row * CELL_H

    hero = ai.get_badge(eid, HERO, True, False, "gold")
    surf.blit(hero, (x, y))
    # row-size badge sitting to the hero's lower-right, on its own dark chip so
    # the 44px legibility read is honest.
    small = ai.get_badge(eid, ROW, True, False, "gold")
    sx = x + HERO + 12
    sy = y + HERO - ROW - 26
    pygame.draw.rect(surf, (30, 26, 48), (sx - 6, sy - 6, ROW + 12, ROW + 12),
                     border_radius=6)
    surf.blit(small, (sx, sy))
    tag = tag_f.render("44px", True, (150, 150, 172))
    surf.blit(tag, (sx + (ROW - tag.get_width()) // 2, sy + ROW + 8))

    t = title_f.render(title, True, (240, 224, 170))
    surf.blit(t, (x, y + HERO + 4))
    d = desc_f.render(desc, True, (176, 176, 198))
    surf.blit(d, (x, y + HERO + 30))

out = "docs/emblems_new/batch1/sheet.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(surf, out)
print("wrote", out, surf.get_size())
