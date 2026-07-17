#!/usr/bin/env python3
"""
equipped-card corner-seal concept — round 1.

A discrete circular award seal pinned to the top-left corner of the card,
overlapping the rim like a physical medal of ownership. Top-left is the one
layout-safe quadrant (dome centred, gem top-right, ribbon/name/chip in the
lower half), so the badge never collides with existing card content.

Silhouette-carried and drawn LAST (on top of everything): a drop shadow that
lifts it off the rim, a solid deep-green enamel disc, a scalloped edge, a thin
mint keyline ring, and a bold mint checkmark. Scallop is the edge treatment;
the emboss ridge is deliberately dropped so the seal never stacks two competing
edge details.
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

PANEL_W = sc.CARD_W * sc.SS   # 324
PANEL_H = sc.CARD_H * sc.SS   # 200
rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                   PANEL_W - 2 * sc.m(sc._INSET), PANEL_H - 2 * sc.m(sc._INSET))

SID = "skin_mummy"


# ── Panel 1 — UNEQUIPPED ──────────────────────────────────────────────────────
# Force affordability so the price chip reads gold (not the wallet-locked grey).
orig_bal = sd.balance
sd.balance = lambda: 99999
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=False, secret=False)
sd.balance = orig_bal
sc._card_cache.clear()


# ── Panel 2 — BASE EQUIPPED ───────────────────────────────────────────────────
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc._card_cache.clear()


# ── Panel 3 — CORNER-SEAL CONCEPT ─────────────────────────────────────────────
p3 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p3, SID, rect, equipped=True, secret=False)
sc._card_cache.clear()

cx_seal = rect.x + sc.m(20)   # 48
cy_seal = rect.y + sc.m(20)   # 48
R = sc.m(13)                  # 26

# (a) Drop shadow — an offset disc so the seal lifts off the card rim.
shadow_s = pygame.Surface((R * 2 + 8, R * 2 + 8), pygame.SRCALPHA)
shadow_dy = sc.m(1.5)
pygame.draw.circle(shadow_s, (0, 0, 0, 100), (R + 4, R + 4 + shadow_dy), R + sc.m(1.5))
p3.blit(shadow_s, (cx_seal - R - 4, cy_seal - R - 4))

# (b) Solid enamel disc (deep green) — the physical medal body.
pygame.draw.circle(p3, (16, 92, 58), (cx_seal, cy_seal), R)

# (c) Scalloped edge — 16 small circles hugging the circumference.
n_teeth = 16
tooth_r = sc.m(1.6)
for i in range(n_teeth):
    angle = math.pi * 2 * i / n_teeth
    tx = int(cx_seal + math.cos(angle) * (R + tooth_r * 0.5))
    ty = int(cy_seal + math.sin(angle) * (R + tooth_r * 0.5))
    pygame.draw.circle(p3, (16, 92, 58), (tx, ty), int(tooth_r))

# (d) Thin mint keyline ring so the enamel face reads as a struck medal.
pygame.draw.circle(p3, (100, 230, 148), (cx_seal, cy_seal), sc.m(12),
                   width=max(1, sc.m(1)))

# (e) Bold mint checkmark — the unmistakable "owned/equipped" mark.
check_pts = [
    (cx_seal - sc.m(6), cy_seal),
    (cx_seal - sc.m(1.5), cy_seal + sc.m(5)),
    (cx_seal + sc.m(7), cy_seal - sc.m(6)),
]
pygame.draw.lines(p3, (150, 240, 180), False, check_pts, width=max(1, sc.m(3)))


# ── Compose the 3-panel review sheet ──────────────────────────────────────────
BG = (8, 8, 20)
PAD = 20
GAP = 16
HDR_H = 48
LBL_H = 34

sheet_w = PAD + 3 * PANEL_W + 2 * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped card — corner-seal · skin_mummy", True,
                    (236, 202, 116))
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

GREY = (150, 152, 168)
MINT = (100, 230, 148)
labels = [("UNEQUIPPED", GREY), ("BASE EQUIPPED", GREY), ("CORNER-SEAL", MINT)]
panels = [p1, p2, p3]

lbl_f = hud_font(15, True)
panel_y = PAD + HDR_H + LBL_H
for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_equipped", "corner_seal", "round_1.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
