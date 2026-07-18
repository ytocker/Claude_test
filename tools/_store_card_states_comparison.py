"""Three-state card comparison: FOR SALE | OWNED (not equipped) | EQUIPPED."""
import os, sys
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

SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324×200
ri   = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)

BG   = (8, 8, 20)
GOLD = (236, 202, 116)
GREY = (150, 152, 168)
CREAM_LBL = (250, 246, 232)

# ── Three panels ──────────────────────────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=False, secret=False, owned=True)

sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=True)

panels = [
    ("FOR SALE",    GREY,      p0),
    ("OWNED",       CREAM_LBL, p1),
    ("EQUIPPED",    GOLD,      p2),
]

# ── Layout ────────────────────────────────────────────────────────────────────
PAD, GAP  = 20, 16
HDR_H     = 48
LBL_H     = 34
SGAP      = 20
SLBL_H    = 24
ONE_W, ONE_H   = sc.CARD_W, sc.CARD_H           # 162×100
ZOOM_W, ZOOM_H = ONE_W * 2, ONE_H * 2

N = len(panels)
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + SGAP + SLBL_H + ZOOM_H + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("store card — three states · v3.2 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

lbl_f  = hud_font(15, True)
zlbl_f = hud_font(13, True)
panel_y = PAD + HDR_H + LBL_H
zlbl_y  = panel_y + PANEL_H + SGAP
zoom_y  = zlbl_y + SLBL_H

for i, (label, col, panel) in enumerate(panels):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))
    card1x = pygame.transform.smoothscale(panel, (ONE_W, ONE_H))
    zoom   = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
    zt = zlbl_f.render("@1× (162×100, 2× nearest)", True, GREY)
    sheet.blit(zt, zt.get_rect(midbottom=(px + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
    sheet.blit(zoom, (px + (PANEL_W - ZOOM_W) // 2, zoom_y))

OUT = "docs/store_equipped_v3_2/comparison.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print(f"saved {sheet_w}×{sheet_h} → {OUT}")
