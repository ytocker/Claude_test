"""Headless candidate-sheet renderer for the Achievements visual loop.

Composes (A) the full Achievements screen in a representative state and (B) a
labeled grid of all 18 glyphs in unlocked / dormant-locked / hidden-locked
states into one sheet. Not shipped — lives under tools/, out of the bundle.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.font.init()

from game import achievements as ach
from game.achievements_screen import AchievementsScene
from game.achievement_icons import draw_badge
from game.hud import _font, _outlined_text, _GOLD_PALE, _GOLD_BRIGHT, _GOLD_DEEP, _NIGHT_DEEP

# ── representative store: a spread of unlocked + progress ────────────────────
store = ach._blank()
for i, a in enumerate(ach.ACHIEVEMENTS):
    if i % 3 == 0:
        store["unlocked"][a.id] = 1
# unlock one hidden so a secret medallion appears in the grid + list
store["unlocked"]["made_a_wish"] = 1
store["life"]["total_coins"] = 240
store["life"]["total_flaps"] = 2600
store["life"]["powerups_seen"] = {"magnet": 9}

# (A) screen
scr = pygame.Surface((360, 640), pygame.SRCALPHA)
sc = AchievementsScene()
sc.scroll_offset = 0.0
for _ in range(2):
    sc.render(scr, 1 / 60, store)

# (B) badge grid
keys = ["pillar", "coin", "day", "score", "powerup", "magnet", "kfc", "nerve",
        "clock", "storm", "wing", "skate", "genie", "knight", "treasure",
        "lottery", "rail", "poison"]
hidden_keys = {"genie", "knight", "treasure", "lottery", "rail", "poison"}

cols = 6
rows = 3
cell = 92
label_h = 16
GW = cols * cell
# three state bands: unlocked / locked / hidden-locked
band_titles = ["UNLOCKED", "LOCKED (dormant)", "HIDDEN + LOCKED"]
band_h = rows * (cell + label_h) + 30
GH = band_h * 3 + 40

grid = pygame.Surface((GW, GH), pygame.SRCALPHA)
for yy in range(GH):
    t = yy / (GH - 1)
    c = (int(8 + 8 * t), int(6 + 6 * t), int(26 + 14 * t))
    pygame.draw.line(grid, c, (0, yy), (GW, yy))

BADGE = 56


def draw_band(top, state, title):
    lab = _font(15, True).render(title, True, _GOLD_PALE)
    grid.blit(lab, (10, top))
    y0 = top + 24
    for idx, k in enumerate(keys):
        r, c = divmod(idx, cols)
        cx = c * cell + cell // 2
        cy = y0 + r * (cell + label_h) + cell // 2 - 6
        rect = pygame.Rect(cx - BADGE // 2, cy - BADGE // 2, BADGE, BADGE)
        if state == "unlocked":
            draw_badge(grid, k, rect, True, k in hidden_keys)
        elif state == "locked":
            draw_badge(grid, k, rect, False, False)
        else:  # hidden-locked
            draw_badge(grid, k, rect, False, True)
        tl = _font(11, True).render(k, True, (210, 210, 230))
        grid.blit(tl, tl.get_rect(center=(cx, cy + BADGE // 2 + 8)))


draw_band(14, "unlocked", band_titles[0])
draw_band(14 + band_h, "locked", band_titles[1])
draw_band(14 + band_h * 2, "hidden", band_titles[2])

# ── compose A + B side by side with a caption banner ────────────────────────
pad = 16
cap_h = 38
sheet_w = 360 + pad * 3 + GW
sheet_h = max(640, GH) + cap_h + pad
sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
sheet.fill((5, 4, 16))

cap = _font(18, True).render(
    "ACHIEVEMENTS  ·  Courier's Commendation  ·  round 1", True, _GOLD_BRIGHT)
sheet.blit(cap, (pad, pad - 2))

sheet.blit(scr, (pad, cap_h + pad // 2))
# label A
la = _font(12, True).render("(A) screen", True, _GOLD_DEEP)
sheet.blit(la, (pad, cap_h + pad // 2 + 640 + 2))

gx = pad * 2 + 360
sheet.blit(grid, (gx, cap_h + pad // 2))
lb = _font(12, True).render("(B) all 18 glyphs × 3 states", True, _GOLD_DEEP)
sheet.blit(lb, (gx, cap_h + pad // 2 + GH + 2))

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "docs", "achievements", "round_1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
