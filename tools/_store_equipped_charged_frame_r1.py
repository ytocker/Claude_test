"""Round-1 review sheet for the `charged-frame` equipped-card concept.

Off-screen only: renders three store cards side by side so the art-director can
read the emerald frame against the unequipped card and the current base-equipped
card. Lives under tools/ so it never ships in the pygbag bundle.
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

# Device-px panel matches draw_card's SS author canvas so the concept reads at
# the same fidelity the live grid caches.
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS
rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                   PANEL_W - 2 * sc.m(sc._INSET), PANEL_H - 2 * sc.m(sc._INSET))
rad = sc.m(17)

# Emerald read is a value step darker + cooler than the gold rim, so the frame
# says "energized" rather than a flat hue swap of the bevel.
EQ_RIM_DEEP = (6, 44, 28)
EQ_RIM_BRIGHT = (96, 206, 140)

SID = "skin_mummy"

# --- Panel 1: UNEQUIPPED (affordable price chip) -----------------------------
# Force a fat balance so the chip reads cream/affordable rather than locked.
orig_bal = sd.balance
sd.balance = lambda: 99999
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=False, secret=False)
sd.balance = orig_bal
sc._card_cache.clear()

# --- Panel 2: BASE EQUIPPED (current behaviour) ------------------------------
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc._card_cache.clear()

# --- Panel 3: CHARGED-FRAME concept ------------------------------------------
p3 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p3, SID, rect, equipped=True, secret=False)
sc._card_cache.clear()
# One emerald bevel over the gold one — single bevel keeps the edge crisp; a
# second stacked stroke would muddy it.
sc.bevel_rim(p3, rect, rad, EQ_RIM_DEEP, (*EQ_RIM_BRIGHT, 235), w=max(1, sc.m(2.45)))
# Cool the inner tray ring to emerald at low alpha so the frame reads as a
# double band without fighting the gem/thumbnail.
tray = rect.inflate(-sc.m(7), -sc.m(7))
trad = rad - sc.m(4)
pygame.draw.rect(p3, (*EQ_RIM_BRIGHT, 70), tray,
                 width=max(1, sc.m(1)), border_radius=trad)
# Single top-left corner accent — a charged spark catching the lit rim.
pygame.draw.polygon(p3, EQ_RIM_BRIGHT, [
    (rect.x + sc.m(4), rect.y + sc.m(4)),
    (rect.x + sc.m(13), rect.y + sc.m(4)),
    (rect.x + sc.m(4), rect.y + sc.m(13)),
])

# --- Compose the sheet -------------------------------------------------------
BG = (8, 8, 20)
PAD, GAP, HDR_H, LBL_H = 20, 16, 48, 34
sheet_w = PAD + 3 * PANEL_W + 2 * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(26)
lbl_f = hud_font(18)
GOLD = (236, 202, 116)
GREY = (150, 150, 168)
MINT = EQ_RIM_BRIGHT

title = title_f.render("equipped card — charged-frame · skin_mummy", True, GOLD)
sheet.blit(title, (PAD, PAD + (HDR_H - title.get_height()) // 2))

panels = [
    (p1, "UNEQUIPPED", GREY),
    (p2, "BASE EQUIPPED", GREY),
    (p3, "CHARGED-FRAME", MINT),
]
for i, (panel, label, col) in enumerate(panels):
    px = PAD + i * (PANEL_W + GAP)
    ly = PAD + HDR_H
    lbl = lbl_f.render(label, True, col)
    sheet.blit(lbl, (px + (PANEL_W - lbl.get_width()) // 2,
                     ly + (LBL_H - lbl.get_height()) // 2))
    # SRCALPHA panels alpha-composite onto the dark sheet fill directly.
    sheet.blit(panel, (px, ly + LBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_equipped", "charged_frame", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved:", out, os.path.getsize(out), "bytes")
