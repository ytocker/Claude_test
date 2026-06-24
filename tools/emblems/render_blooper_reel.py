"""Headless review-sheet renderer for the BLOOPER REEL (Wall of Shame) glyphs.

Monkeypatches the bespoke tarnished glyphs into the live achievement-icons
module, then stamps each through the REAL medallion frame in its earned-
tarnished state (the only state that shows the glyph — an unearned tarnished
medal shows the masked bronze ✕). Renders a hero badge (220px) + a row-size
badge (44px) per id so legibility against the cracked pewter is testable.

Not shipped — lives under tools/, out of the bundle.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.font.init()

import game.achievement_icons as ai
from tools.emblems.blooper_reel import GLYPHS

# Inject the bespoke glyphs so get_badge stamps them through the real frame.
ai._GLYPHS.update(GLYPHS)

IDS = [
    ("goose_egg", "The Goose Egg"),
    ("icarus", "The Icarus Award"),
    ("hummingbird", "The Hummingbird"),
    ("denial", "Denial"),
    ("kfc_incident", "The KFC Incident"),
    ("so_close", "So Close, So Far"),
    ("lottery_loser", "The Lottery Loser"),
    ("the_49er", "The 49er"),
    ("night_owl", "Night Owl's Revenge"),
]

HERO = 220
ROW = 44
COLS = 3
CELL_W = HERO + 60
CELL_H = HERO + 90
PAD = 24
TITLE_H = 54


def _font(px, bold=False):
    return pygame.font.SysFont(None, px, bold=bold)


def _bg(surf):
    w, h = surf.get_size()
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = (int(10 + 10 * t), int(11 + 10 * t), int(20 + 16 * t))
        pygame.draw.line(surf, c, (0, yy), (w, yy))


rows = (len(IDS) + COLS - 1) // COLS
sheet_w = COLS * CELL_W + PAD * 2
sheet_h = TITLE_H + rows * CELL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
_bg(sheet)

cap = _font(30, True).render(
    "BLOOPER REEL  ·  tarnished anti-trophies  ·  hero + 44px row size",
    True, (210, 178, 150))
sheet.blit(cap, (PAD, 14))

for idx, (key, name) in enumerate(IDS):
    r, c = divmod(idx, COLS)
    x0 = PAD + c * CELL_W
    y0 = TITLE_H + r * CELL_H

    hero = ai.get_badge(key, HERO, True, False, "tarnished")
    hx = x0 + (CELL_W - HERO) // 2
    sheet.blit(hero, (hx, y0))

    # 44px row-size badge tucked at lower-right of the hero
    row = ai.get_badge(key, ROW, True, False, "tarnished")
    rx = x0 + CELL_W - ROW - 18
    ry = y0 + HERO - ROW
    # a faint plate behind the row badge so it reads against the gradient
    pygame.draw.rect(sheet, (6, 7, 14), (rx - 6, ry - 6, ROW + 12, ROW + 12),
                     border_radius=6)
    sheet.blit(row, (rx, ry))
    rl = _font(18, True).render("44px", True, (150, 158, 172))
    sheet.blit(rl, (rx + ROW + 2, ry + ROW // 2 - 8))

    lab = _font(26, True).render(name, True, (224, 220, 230))
    sheet.blit(lab, lab.get_rect(center=(x0 + CELL_W // 2, y0 + HERO + 22)))
    kl = _font(20, False).render(key, True, (140, 146, 160))
    sheet.blit(kl, kl.get_rect(center=(x0 + CELL_W // 2, y0 + HERO + 46)))

out = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "docs", "emblems", "blooper_reel", "sheet.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
