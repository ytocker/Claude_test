"""Render the RICHES emblem review sheet: each of the six gold wealth-ladder
glyphs at hero size (220px) plus its 44px row-size sibling, labelled on a dark
field. Reads-at-row-size is the whole point, so both scales sit side by side.

Run headless: ``SDL_VIDEODRIVER=dummy python tools/emblems/render_riches.py``.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pygame

pygame.init()
pygame.font.init()

import game.achievement_icons as ai
import tools.emblems.riches as riches

# Wire the host module's real engrave hooks into the standalone glyph file so the
# inset-shadow tone, font cache and dormant-accent resolver match the rest of the
# medallion family exactly, then register the six glyphs.
riches._GLYPH_SH = ai._GLYPH_SH
riches._glyph_font = ai._glyph_font
riches._accent = ai._accent
ai._GLYPHS.update(riches.GLYPHS)

ORDER = [
    ("coin_25_run", "coin_25_run  ·  Pocket Change"),
    ("coin_100_run", "coin_100_run  ·  Coin Run"),
    ("coins_500_life", "coins_500_life  ·  Coin Collector"),
    ("coins_5000_life", "coins_5000_life  ·  Coin Vault"),
    ("coin_tycoon", "coin_tycoon  ·  Coin Tycoon"),
    ("midas", "midas  ·  Midas Touch"),
]

HERO = 220
ROW = 44
PAD = 28
LABEL_H = 34
COL_W = HERO + PAD + ROW + PAD + 250
ROW_H = HERO + LABEL_H + PAD
COLS = 2
ROWS = 3

BG = (22, 24, 34)
TITLE = (236, 210, 150)
TXT = (210, 214, 226)

W = PAD + COLS * COL_W
H = 70 + ROWS * ROW_H + PAD

sheet = pygame.Surface((W, H))
sheet.fill(BG)

title_f = pygame.font.SysFont(None, 40, bold=True)
lab_f = pygame.font.SysFont(None, 26, bold=True)
sub_f = pygame.font.SysFont(None, 22)

t = title_f.render("RICHES — gold wealth ladder  (hero 220px + row 44px)", True, TITLE)
sheet.blit(t, (PAD, 24))
sub = sub_f.render("coin -> 3-stack -> pouch -> tall safe -> crowned hoard -> Midas hand",
                   True, TXT)
sheet.blit(sub, (PAD, 52))

for idx, (key, label) in enumerate(ORDER):
    c = idx % COLS
    rr = idx // COLS
    ox = PAD + c * COL_W
    oy = 70 + rr * ROW_H

    hero = ai.get_badge(key, HERO, True, False, "gold")
    sheet.blit(hero, (ox, oy))

    small = ai.get_badge(key, ROW, True, False, "gold")
    sx = ox + HERO + PAD
    sy = oy + (HERO - ROW) // 2 - 20
    # a faint chip behind the 44px badge so its dark areas don't vanish on BG
    pygame.draw.rect(sheet, (34, 36, 48),
                     (sx - 6, sy - 6, ROW + 12, ROW + 12), border_radius=6)
    sheet.blit(small, (sx, sy))
    cap = sub_f.render("44px", True, TXT)
    sheet.blit(cap, (sx + (ROW - cap.get_width()) // 2, sy + ROW + 8))

    lab = lab_f.render(label, True, TXT)
    sheet.blit(lab, (ox, oy + HERO + 6))

out = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   "..", "..", "docs", "emblems", "riches", "sheet.png"))
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
