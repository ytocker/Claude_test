"""Render the POWER PLAYER emblem review sheet.

Patches the bespoke glyphs into ``ai._GLYPHS`` then composes a hero (220px) +
row-size (44px) sheet, labeled, on a dark ground — the engrave at the scale the
medal actually ships AND the scale a glance reads it. Review-only; writes to
docs/, never game/assets/.
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()
pygame.font.init()

import game.achievement_icons as ai
from tools.emblems.power_player import GLYPHS

ai._GLYPHS.update(GLYPHS)

ORDER = [
    ("first_powerup", "Power Up!"),
    ("powerup_sampler", "Buffet"),
    ("magnet_life", "Animal Magnetism"),
    ("powerup_collector", "Gotta Grab 'Em All"),
    ("greasy_fingers", "Finger Lickin'"),
    ("power_hungry", "Power Hungry"),
    ("power_addict", "Power Addict"),
]

HERO = 220
ROW = 44
PAD = 28
COL_W = HERO + PAD * 2
LABEL_H = 34
ROW_BLOCK = ROW + 14
CELL_H = HERO + LABEL_H + ROW_BLOCK + PAD

BG = (22, 24, 32)
INK = (228, 224, 210)
SUB = (150, 150, 160)

cols = 4
rows = (len(ORDER) + cols - 1) // cols
W = cols * COL_W
H = 64 + rows * CELL_H

sheet = pygame.Surface((W, H), pygame.SRCALPHA)
sheet.fill(BG)

title_f = pygame.font.SysFont(None, 40, bold=True)
label_f = pygame.font.SysFont(None, 26, bold=True)
small_f = pygame.font.SysFont(None, 20)

t = title_f.render("POWER PLAYER  ·  engraved center glyphs (gold)", True, INK)
sheet.blit(t, (PAD, 18))

for idx, (key, name) in enumerate(ORDER):
    c = idx % cols
    rrow = idx // cols
    x0 = c * COL_W
    y0 = 64 + rrow * CELL_H

    # Hero 220px, unlocked gold.
    hero = ai.get_badge(key, HERO, True, False, "gold")
    sheet.blit(hero, (x0 + PAD, y0))

    # Label.
    lbl = label_f.render(name, True, INK)
    sheet.blit(lbl, lbl.get_rect(centerx=x0 + COL_W // 2, top=y0 + HERO + 4))
    kid = small_f.render(key, True, SUB)
    sheet.blit(kid, kid.get_rect(centerx=x0 + COL_W // 2, top=y0 + HERO + 4 + 18))

    # Row-size 44px trio: dormant, unlocked, unlocked — shows the glyph reads at
    # ship size and the accent-on-unlock behaviour.
    ry = y0 + HERO + LABEL_H + 8
    states = [
        (False, "lock"),
        (True, "gold"),
    ]
    bx = x0 + COL_W // 2 - (ROW + 8)
    for i, (unlocked, _tag) in enumerate(states):
        b = ai.get_badge(key, ROW, unlocked, False, "gold")
        sheet.blit(b, (bx + i * (ROW + 16), ry))

out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "docs",
                       "emblems", "power_player")
out_dir = os.path.abspath(out_dir)
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "sheet.png")
pygame.image.save(sheet, out)
print("wrote", out, sheet.get_size())
