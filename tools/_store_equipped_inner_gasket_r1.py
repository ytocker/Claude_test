"""Round-1 review sheet for the `inner-gasket` equipped-card concept.

The gasket is a CONTAINED interior light-pipe: an emerald pipe traced just
inside the body rim, a hotter filament inside it, and a few inner falloff
rings bleeding toward the card center. It is composited via BLEND_ADD so it
only ADDS light onto the dark body and never blooms outside the rect — the
card reads as energized from within rather than haloed from without.
"""
import os
import sys

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

# Derive geometry from the live card constants so the sheet can't drift.
PANEL_W = sc.CARD_W * sc.SS          # 324
PANEL_H = sc.CARD_H * sc.SS          # 200
ri = sc.m(sc._INSET)                 # 8
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)   # 8,8,308,184
rad = sc.m(sc.CARD_RAD)              # 34

# Emerald "power-on" gasket palette.
EQ_PIPE = (60, 210, 130)
EQ_PIPE_HOT = (150, 245, 190)


def _card(equipped):
    surf = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    sc.draw_card(surf, "skin_mummy", rect, equipped=equipped, secret=False)
    sc._card_cache.clear()
    return surf


# Panel 1 — UNEQUIPPED (force affordability so the base art, not a lock, shows).
orig_bal = sd.balance
sd.balance = lambda: 99999
p1 = _card(equipped=False)
sd.balance = orig_bal
sc._card_cache.clear()

# Panel 2 — BASE EQUIPPED (the current in-game equipped treatment).
p2 = _card(equipped=True)

# Panel 3 — INNER-GASKET concept over the equipped card.
p3 = _card(equipped=True)

layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
# Gasket ring sits inset from the body rim so its glow stays fully contained.
g = pygame.Rect(rect.x + sc.m(6), rect.y + sc.m(6),
                rect.w - 2 * sc.m(6), rect.h - 2 * sc.m(6))
grad = rad - sc.m(3)

# 1. Primary pipe.
pygame.draw.rect(layer, (*EQ_PIPE, 200), g, width=max(1, sc.m(1.4)),
                 border_radius=grad)
# 2. Hot filament threaded inside the pipe.
g2 = g.inflate(-sc.m(1.2), -sc.m(1.2))
pygame.draw.rect(layer, (*EQ_PIPE_HOT, 150), g2, width=max(1, sc.m(0.8)),
                 border_radius=max(1, grad - 1))
# 3. Inner falloff rings fading toward the card center.
for inset_px, alpha in [(sc.m(2), 40), (sc.m(4), 22), (sc.m(6), 10)]:
    gi = g.inflate(-2 * inset_px, -2 * inset_px)
    if gi.width > 0 and gi.height > 0:
        pygame.draw.rect(layer, (40, 180, 110, alpha), gi, width=max(1, sc.m(1)),
                         border_radius=max(1, grad - inset_px))

p3.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

# --- Compose the labeled review sheet ---
BG = (8, 8, 20)
PAD, GAP, HDR_H, LBL_H = 20, 16, 48, 34
GREY = (170, 176, 190)
GOLD = (240, 205, 120)

sheet_w = PAD + 3 * PANEL_W + 2 * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(30)
label_f = hud_font(20)

title = title_f.render("equipped card — inner-gasket · skin_mummy", True, GOLD)
sheet.blit(title, (PAD, PAD + (HDR_H - title.get_height()) // 2))

panels = [
    (p1, "UNEQUIPPED", GREY),
    (p2, "BASE EQUIPPED", GREY),
    (p3, "INNER-GASKET", EQ_PIPE),
]
for i, (panel, label, col) in enumerate(panels):
    px = PAD + i * (PANEL_W + GAP)
    ly = PAD + HDR_H
    lbl = label_f.render(label, True, col)
    sheet.blit(lbl, (px + (PANEL_W - lbl.get_width()) // 2,
                     ly + (LBL_H - lbl.get_height()) // 2))
    sheet.blit(panel, (px, ly + LBL_H))

out = os.path.join(os.path.dirname(__file__), "..", "docs", "store_equipped",
                   "inner_gasket", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
