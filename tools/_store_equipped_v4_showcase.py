#!/usr/bin/env python3
"""
Showcase figure for store_equipped_v4 — 5 equipped-indicator concepts, round 2.
Each concept's primary state (Panel 2 / concept panel) is cropped from its round_2
sheet and arranged in a horizontal row.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from game.hud import _font as hud_font

# ── concept slugs + display names ────────────────────────────────────────────
CONCEPTS = [
    ("top_center_banner",       "TOP-CENTER\nBANNER"),
    ("ribbon_diagonal",         "RIBBON\nDIAGONAL"),
    ("active_frame_illumination","FRAME\nILLUMINATION"),
    ("lower_left_corner",       "LOWER-LEFT\nCORNER"),
    ("wax_seal_medallion",      "WAX SEAL\nMEDALLION"),
]

BASE = os.path.join(os.path.dirname(__file__), "..", "docs", "store_equipped_v4")

# Each round_2 sheet has 3 panels at x=[20,360,700], y=102, each 324×200.
# We crop the concept panel (Panel 2) from each sheet.
PANEL_X, PANEL_Y = 700, 102
PANEL_W, PANEL_H = 324, 200

# Display size per concept in the showcase (scale down to 243×150 = 75% of SS=2)
DISP_W, DISP_H = 243, 150

BG        = (8, 8, 20)
GOLD      = (236, 202, 116)
GREY      = (130, 132, 148)
CREAM     = (246, 242, 224)

PAD   = 24
GAP   = 12
HDR_H = 52
LBL_H = 44   # two-line label area below each panel

sheet_w = PAD * 2 + len(CONCEPTS) * DISP_W + (len(CONCEPTS) - 1) * GAP
panel_y = PAD + HDR_H
sheet_h = panel_y + DISP_H + LBL_H + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

# header
title_f = hud_font(22, True)
tt = title_f.render("equipped v4 — 5 concepts · round 2 showcase", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

lbl_f  = hud_font(13, True)
lbl_f2 = hud_font(12, True)

for i, (slug, label) in enumerate(CONCEPTS):
    path = os.path.join(BASE, slug, "round_2.png")
    src = pygame.image.load(path)

    # crop concept panel
    crop_rect = pygame.Rect(PANEL_X, PANEL_Y, PANEL_W, PANEL_H)
    concept = src.subsurface(crop_rect).copy()

    # scale to display size
    tile = pygame.transform.smoothscale(concept, (DISP_W, DISP_H))

    x = PAD + i * (DISP_W + GAP)
    sheet.blit(tile, (x, panel_y))

    # label (two lines)
    lines = label.split("\n")
    line_h = 18
    total_lbl = len(lines) * line_h
    lbl_top = panel_y + DISP_H + (LBL_H - total_lbl) // 2
    cx = x + DISP_W // 2
    for j, line in enumerate(lines):
        lt = lbl_f.render(line, True, CREAM)
        sheet.blit(lt, lt.get_rect(midtop=(cx, lbl_top + j * line_h)))

OUT = os.path.abspath(os.path.join(BASE, "showcase.png"))
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
