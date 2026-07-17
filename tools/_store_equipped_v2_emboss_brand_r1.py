#!/usr/bin/env python3
"""
equipped-card v2 — emboss-brand concept, round 1.

Instead of the green EQUIPPED chip, ownership is stamped into the card like a
maker's hallmark on a certified object: a warm amber wax-seal ring pressed into
the upper-left quadrant, carrying a struck crown glyph, with a debossed shadow
pass so the mark reads as pressed INTO the body. The wax ring is the eye-anchor
(a real high-contrast shape); the deboss is the secondary "authenticated"
texture. Top-left is the one layout-safe quadrant (dome centred at (162,86) in
SS=2, gem top-right, ribbon/name/chip in the lower half), so the brand never
collides with live card content.

Drawn LAST over an equipped card whose green chip is suppressed.
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

SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324×200
ri = sc.m(sc._INSET)                                      # 8
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)


# ── Panel 0 — UNEQUIPPED (price tag visible) ─────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)


# ── Panel 1 — STOCK EQUIPPED (green chip, reference) ─────────────────────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False)


# ── Panel 2 — CONCEPT EQUIPPED (chip suppressed, emboss brand) ───────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None          # suppress the green EQUIPPED chip
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()

# Brand mark centre — upper-left quadrant, clear of the dome at (162,86).
BX, BY = 46, 52


def _crown_pts(cx, cy):
    """Bold 3-peak crown silhouette centred on (cx, cy), fitting radius 16."""
    return [
        (cx - 12, cy + 6),   # base bottom-left
        (cx - 12, cy - 2),   # base top-left
        (cx - 12, cy - 12),  # left peak tip
        (cx - 6, cy - 4),    # left valley
        (cx, cy - 14),       # centre peak tip
        (cx + 6, cy - 4),    # right valley
        (cx + 12, cy - 12),  # right peak tip
        (cx + 12, cy - 2),   # base top-right
        (cx + 12, cy + 6),   # base bottom-right
    ]


# (1) Drop shadow of the whole seal — grounds the disc against the body.
shadow = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.circle(shadow, (4, 4, 16, 140), (BX + 3, BY + 3), 29)
p2.blit(shadow, (0, 0))

# (2) Amber wax discs — outer ring + slightly darker inner well.
pygame.draw.circle(p2, (196, 150, 74), (BX, BY), 28)
pygame.draw.circle(p2, (168, 124, 58), (BX, BY), 22)

# (3) Ring shading — upper-left catchlight arc, lower-right shadow arc, so the
# wax reads as a raised, wet-poured bead rather than a flat coin.
ring = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
arc_box = pygame.Rect(BX - 26, BY - 26, 52, 52)
import math
pygame.draw.arc(ring, (236, 202, 116, 220), arc_box,
                math.radians(120), math.radians(240), 3)
pygame.draw.arc(ring, (58, 48, 22, 180), arc_box,
                math.radians(300), math.radians(360 + 60), 3)
pygame.draw.circle(ring, (250, 240, 200, 180), (BX - 18, BY - 18), 4)
p2.blit(ring, (0, 0))

# (4) Debossed crown — a dark copy shifted down-right and a bright copy shifted
# up-left near-cancel over the fill, faking a mark pressed INTO the wax.
deboss = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.polygon(deboss, (6, 6, 18, 150), _crown_pts(BX + 2, BY - 8))
p2.blit(deboss, (0, 0))
deboss_hi = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.polygon(deboss_hi, (248, 238, 210, 60), _crown_pts(BX - 1, BY - 11))
p2.blit(deboss_hi, (0, 0))

# (5) Struck crown fill — cast/darker amber, the actual glyph face.
pygame.draw.polygon(p2, (128, 96, 50), _crown_pts(BX, BY - 10))


# ── Compose the review sheet ─────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
ONE_W, ONE_H = sc.CARD_W, sc.CARD_H          # 162×100 — true 1× card size
ZOOM_W, ZOOM_H = ONE_W * 2, ONE_H * 2        # nearest-neighbour blow-up of 1×

N = 3
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + SGAP + SLBL_H + ZOOM_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

GOLD = (236, 202, 116)
title_f = hud_font(22, True)
tt = title_f.render("equipped v2 — emboss-brand · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

GREY = (150, 152, 168)
AMBER_LBL = (222, 178, 96)
labels = [("UNEQUIPPED", GREY), ("STOCK EQUIPPED", GREY),
          ("EMBOSS BRAND", AMBER_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)
panel_y = PAD + HDR_H + LBL_H
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

    # 1× read: downscale to true card size, then blow back up nearest-neighbour
    # so the sheet shows how the brand resolves at the size players see.
    card1x = pygame.transform.smoothscale(panel, (ONE_W, ONE_H))
    zoom = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
    zt = zlbl_f.render("@1× (rendered then 2× nearest)", True, GREY)
    sheet.blit(zt, zt.get_rect(midbottom=(px + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
    sheet.blit(zoom, (px + (PANEL_W - ZOOM_W) // 2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v2", "emboss_brand", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
