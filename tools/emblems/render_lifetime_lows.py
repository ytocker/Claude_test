"""
Review-sheet harness for the Lifetime Lows (Wall of Shame) emblems.

Renders each tarnished badge at hero (220px) + row (44px) size against a dark
ground and labels them, so the cracked-pewter frame + engraved glyph can be
judged for legibility. Writes ONLY to docs/emblems/lifetime_lows/sheet.png —
never touches game/ (it merges GLYPHS into a private copy of the badge table).
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pygame
pygame.init()
pygame.font.init()

import game.achievement_icons as ai
from tools.emblems.lifetime_lows import GLYPHS

# Merge bespoke glyphs into the badge glyph table (private to this process).
ai._GLYPHS.update(GLYPHS)

EMBLEMS = [
    ("the_scrooge", "THE SCROOGE"),
    ("early_checkout", "EARLY CHECKOUT"),
]

HERO = 220
ROW = 44
BG = (24, 26, 34)
PANEL = (32, 35, 46)
INK = (206, 212, 224)
SUB = (150, 156, 170)

PAD = 28
COL_W = HERO + 120
ROW_H = HERO + 110
GRID_COLS = len(EMBLEMS)

W = PAD * 2 + COL_W * GRID_COLS
H = PAD * 2 + ROW_H + 60

sheet = pygame.Surface((W, H))
sheet.fill(BG)

title_f = pygame.font.SysFont(None, 40, bold=True)
label_f = pygame.font.SysFont(None, 30, bold=True)
sub_f = pygame.font.SysFont(None, 22)

t = title_f.render("LIFETIME LOWS  —  tarnished anti-trophies", True, INK)
sheet.blit(t, (PAD, PAD - 6))

y0 = PAD + 48
for i, (key, label) in enumerate(EMBLEMS):
    cx = PAD + COL_W * i + COL_W // 2

    # Panel behind each emblem column.
    panel = pygame.Rect(PAD + COL_W * i + 8, y0, COL_W - 16, ROW_H + 8)
    pygame.draw.rect(sheet, PANEL, panel, border_radius=14)

    # Hero badge (unlocked, tarnished).
    hero = ai.get_badge(key, HERO, True, False, "tarnished")
    sheet.blit(hero, hero.get_rect(center=(cx, y0 + 30 + HERO // 2)))

    # 44px row badge to its lower-right, plus the locked ✕ variant for contrast.
    row_unlocked = ai.get_badge(key, ROW, True, False, "tarnished")
    row_locked = ai.get_badge(key, ROW, False, False, "tarnished")
    ry = y0 + 30 + HERO + 18
    sheet.blit(row_unlocked, row_unlocked.get_rect(center=(cx - 70, ry)))
    sheet.blit(row_locked, row_locked.get_rect(center=(cx + 70, ry)))
    s1 = sub_f.render("44px earned", True, SUB)
    s2 = sub_f.render("44px locked", True, SUB)
    sheet.blit(s1, s1.get_rect(center=(cx - 70, ry + 34)))
    sheet.blit(s2, s2.get_rect(center=(cx + 70, ry + 34)))

    lbl = label_f.render(label, True, INK)
    sheet.blit(lbl, lbl.get_rect(center=(cx, y0 + ROW_H + 28)))

out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "emblems", "lifetime_lows")
out_dir = os.path.abspath(out_dir)
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "sheet.png")
pygame.image.save(sheet, out_path)
print(out_path)
