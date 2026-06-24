"""Headless review-sheet renderer for the six amethyst MYSTERIES glyphs.

Patches the bespoke glyphs from ``mysteries.py`` into the live glyph table and
registers their ids as hidden keys, so ``get_badge`` renders them with the
secret amethyst well + sparkle ring (the exact in-game secret look). Composes a
hero (220px) + 44px row-size pair per emblem, labeled, on a dark ground, to
``docs/emblems/mysteries/sheet.png``. Lives under ``tools/`` — ships nothing.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# Repo root on the path so ``game`` + the sibling module import headless.
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
pygame.init()
pygame.font.init()

import game.achievement_icons as ai
from mysteries import GLYPHS

# Register the bespoke glyphs and mark their ids hidden so the badge builder
# routes them through the amethyst-secret well + sparkle ring.
ai._GLYPHS.update(GLYPHS)
ai._HIDDEN_KEYS = frozenset(set(ai._HIDDEN_KEYS) | set(GLYPHS))

IDS = [
    ("made_a_wish", "Three Wishes"),
    ("poisoned", "Be Careful What You Wish For"),
    ("knighted", "Knighted"),
    ("treasure_hunter", "X Marks the Spot"),
    ("jackpot", "Jackpot!"),
    ("rail_rider", "Off the Rails"),
]

HERO = 220
ROW = 44
PAD = 24
COL_W = HERO + 120
LABEL_H = 70


def _font(px, bold=True):
    return pygame.font.SysFont(None, px, bold=bold)


def _bg(surf):
    w, h = surf.get_size()
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = (int(10 + 10 * t), int(8 + 8 * t), int(24 + 16 * t))
        pygame.draw.line(surf, c, (0, yy), (w, yy))


cols = 3
rows = (len(IDS) + cols - 1) // cols
cell_w = COL_W + PAD
cell_h = HERO + LABEL_H + PAD
sheet_w = cols * cell_w + PAD
sheet_h = rows * cell_h + 70
sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
_bg(sheet)

title = _font(30).render("MYSTERIES  ·  amethyst secret tier", True, (224, 210, 248))
sheet.blit(title, (PAD, 18))
sub = _font(18).render("hero 220px  +  44px row size  ·  unlocked secret look",
                       True, (170, 156, 200))
sheet.blit(sub, (PAD, 48))

for idx, (key, name) in enumerate(IDS):
    rr, cc = divmod(idx, cols)
    ox = PAD + cc * cell_w
    oy = 78 + rr * cell_h

    hero = ai.get_badge(key, HERO, True, False, "gold")
    sheet.blit(hero, (ox, oy))

    # 44px row-size pair to the right of the hero, stacked, to prove crispness.
    small = ai.get_badge(key, ROW, True, False, "gold")
    sx = ox + HERO + 24
    for i in range(2):
        sheet.blit(small, (sx, oy + 30 + i * (ROW + 14)))
    rl = _font(15).render("44px", True, (150, 140, 175))
    sheet.blit(rl, (sx, oy + 30 + 2 * (ROW + 14) + 2))

    kl = _font(20).render(key, True, (220, 208, 244))
    sheet.blit(kl, (ox, oy + HERO + 8))
    nl = _font(16).render(name, True, (168, 156, 196))
    sheet.blit(nl, (ox, oy + HERO + 32))

out = os.path.join(_ROOT, "docs", "emblems", "mysteries", "sheet.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
