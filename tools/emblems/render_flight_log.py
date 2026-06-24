"""
Review harness for the Flight Log bespoke glyphs. Registers the GLYPHS dict into
the live badge builder, then composes a hero (220px) + row-size (44px) pair per
emblem on a dark-navy sheet so the art-director can read both legibility scales.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pygame
pygame.init()
pygame.font.init()

import game.achievement_icons as ai

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from flight_log import GLYPHS

ai._GLYPHS.update(GLYPHS)

# id → display title (from game/achievements.py).
EMBLEMS = [
    ("first_flight", "First Delivery"),
    ("pillar_25", "Courier in Training"),
    ("pillar_50", "Route Veteran"),
    ("pillar_100", "Centurion of the Sky"),
    ("score_100", "Triple Digits"),
    ("score_500", "High Flyer"),
    ("day_complete", "Round the Clock"),
    ("day_three", "Three-Day Weekend"),
    ("frequent_flyer", "Frequent Flyer"),
    ("globetrotter", "Globetrotter"),
]

BG = (16, 20, 38)
PANEL = (24, 30, 54)
INK = (210, 220, 240)
SUB = (150, 162, 196)

HERO = 220
ROW = 44
PAD = 26
LABEL_W = 360
CELL_H = HERO + PAD
COLS = 2

font_t = pygame.font.SysFont("dejavusans", 26, bold=True)
font_id = pygame.font.SysFont("dejavusansmono", 18)
font_h = pygame.font.SysFont("dejavusans", 30, bold=True)


def cell(id_, title):
    w = HERO + PAD * 2 + LABEL_W
    h = CELL_H
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill(PANEL)
    pygame.draw.rect(s, (40, 48, 78), s.get_rect(), 2, border_radius=10)
    hero = ai.get_badge(id_, HERO, True, False, "gold")
    s.blit(hero, (PAD, PAD // 2))
    # row-size badge to the right of the hero, vertically centred against it.
    row = ai.get_badge(id_, ROW, True, False, "gold")
    rx = PAD + HERO + 30
    ry = PAD // 2 + 18
    # a faint plate behind the 44px so it reads at true row scale.
    pygame.draw.rect(s, (18, 22, 40), (rx - 8, ry - 8, ROW + 16, ROW + 16),
                     border_radius=8)
    s.blit(row, (rx, ry))
    s.blit(font_id.render("44px", True, SUB), (rx, ry + ROW + 14))
    # title block under/right.
    tx = rx
    ty = ry + 90
    s.blit(font_t.render(title, True, INK), (tx, ty))
    s.blit(font_id.render(id_, True, SUB), (tx, ty + 34))
    return s


def main():
    cells = [cell(i, t) for i, t in EMBLEMS]
    cw = cells[0].get_width()
    ch = cells[0].get_height()
    rows = (len(cells) + COLS - 1) // COLS
    margin = 40
    head = 88
    W = margin * 2 + cw * COLS + 30
    H = margin + head + rows * (ch + 22)
    sheet = pygame.Surface((W, H))
    sheet.fill(BG)
    sheet.blit(font_h.render("FLIGHT LOG — bespoke engraved glyphs (GOLD)",
                             True, INK), (margin, 34))
    sheet.blit(font_id.render("hero 220px  +  row 44px   |   v2 LOCKED concept",
                              True, SUB), (margin, 70))
    for idx, c in enumerate(cells):
        r = idx // COLS
        col = idx % COLS
        x = margin + col * (cw + 30)
        y = margin + head + r * (ch + 22)
        sheet.blit(c, (x, y))

    out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       "..", "..", "docs", "emblems",
                                       "flight_log", "sheet.png"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print(out)


if __name__ == "__main__":
    main()
