"""Round-1 review sheet for the 'emerald-weave' equipped-card concept.

Ownership is felt in the card's SUBSTANCE: only the body material shifts —
dark indigo -> deep emerald-teal -> near-black (a value + temperature swing) —
while gold frame, dome, gem, ribbon, name and EQUIPPED chip stay untouched. A
very-faint additive sunburst watermark behind the dome gives the material a
woven-light texture without competing with the crest.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

PANEL_W, PANEL_H = 324, 200
rect = pygame.Rect(8, 8, 308, 184)

# --- Panel 1 — UNEQUIPPED --------------------------------------------------
# Stub the wallet high so the price chip reads a clean affordable state and the
# unequipped body is the honest indigo baseline for the value comparison.
orig_bal = sd.balance
sd.balance = lambda: 99999
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, "skin_mummy", rect, equipped=False, secret=False)
sd.balance = orig_bal
sc._card_cache.clear()

# --- Panel 2 — BASE EQUIPPED (current shipped equipped look) ---------------
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, "skin_mummy", rect, equipped=True, secret=False)
sc._card_cache.clear()

# --- Panel 3 — EMERALD-WEAVE concept ---------------------------------------
CARD_T = sc.CARD_T   # (28, 30, 70) indigo top
CARD_B = sc.CARD_B   # (12, 13, 38) indigo bottom
EMERALD_STOPS = [(0.0, (20, 40, 52)), (0.45, (12, 58, 50)),
                 (0.78, (8, 40, 34)), (1.0, (5, 16, 16))]

# Intercept ONLY the body-fill gradient (the one call keyed on CARD_T/CARD_B);
# every other vgrad user (none on this card, but be exact) falls through so the
# gold frame path is provably untouched.
_orig_vgrad = sc.vgrad
def patched_vgrad(w, h, radius, top, bot, alpha=255, gamma=1.0):
    if top == CARD_T and bot == CARD_B:
        return sc.vgrad_stops(w, h, radius, EMERALD_STOPS, 252, 1.15)
    return _orig_vgrad(w, h, radius, top, bot, alpha, gamma)
sc.vgrad = patched_vgrad
sc._card_cache.clear()

p3 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p3, "skin_mummy", rect, equipped=True, secret=False)
sc._card_cache.clear()
sc.vgrad = _orig_vgrad

# Sunburst watermark — additive so it only ever brightens the emerald weave,
# never darkens it; radiates from the dome center and fades before the rim so
# it reads as material texture, not a graphic element.
dome_cx, dome_cy = rect.centerx, rect.y + sc.m(34) + 10   # (162, 86)
watermark = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
for i in range(24):
    if i % 2 == 0:                      # every other spoke = 12 spokes
        angle = math.pi * 2 * i / 24
        pts = [
            (dome_cx + int(math.cos(angle - 0.06) * sc.m(28)),
             dome_cy + int(math.sin(angle - 0.06) * sc.m(28))),
            (dome_cx + int(math.cos(angle + 0.06) * sc.m(28)),
             dome_cy + int(math.sin(angle + 0.06) * sc.m(28))),
            (int(dome_cx + math.cos(angle + 0.04) * sc.m(52)),
             int(dome_cy + math.sin(angle + 0.04) * sc.m(52))),
            (int(dome_cx + math.cos(angle - 0.04) * sc.m(52)),
             int(dome_cy + math.sin(angle - 0.04) * sc.m(52))),
        ]
        pygame.draw.polygon(watermark, (60, 150, 120, 18), pts)
p3.blit(watermark, (0, 0), special_flags=pygame.BLEND_ADD)

# --- Compose the review sheet ----------------------------------------------
BG = (8, 8, 20)
PAD, GAP, HDR_H, LBL_H = 20, 16, 48, 34
GOLD = (222, 184, 92)
GREY = (150, 152, 168)
EMER = (60, 180, 120)

sheet_w = PAD + 3 * PANEL_W + 2 * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
sheet.fill(BG)

title_f = hud_font(30, True)
lbl_f = hud_font(20, True)

title = title_f.render("equipped card — emerald-weave · skin_mummy", True, GOLD)
sheet.blit(title, (PAD, PAD + (HDR_H - title.get_height()) // 2))

panels = [(p1, "UNEQUIPPED", GREY),
          (p2, "BASE EQUIPPED", GREY),
          (p3, "EMERALD-WEAVE", EMER)]
row_y = PAD + HDR_H
for idx, (panel, label, col) in enumerate(panels):
    x = PAD + idx * (PANEL_W + GAP)
    lbl = lbl_f.render(label, True, col)
    sheet.blit(lbl, (x + (PANEL_W - lbl.get_width()) // 2,
                     row_y + (LBL_H - lbl.get_height()) // 2))
    sheet.blit(panel, (x, row_y + LBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_equipped", "emerald_weave", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
assert os.path.exists(out), "render did not save"
print("saved", out, sheet.get_size())
