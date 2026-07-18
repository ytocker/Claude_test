"""Showcase: 5 checkmark concept panels side by side from round_2.png crops."""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game.hud import _font as hud_font

# ── Config ────────────────────────────────────────────────────────────────────
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS  # 324×200
HDR_H  = 48
FTR_H  = 32
GAP    = 8
PAD    = 20
BG     = (8, 8, 20)
GOLD   = (236, 202, 116)
CREAM  = (250, 246, 232)

SLUGS  = ["swift-slash", "calligraphic", "chunky-brush", "double-strike", "looped-entry"]
# Concept panel sits at x=360, y=102 in each r2 sheet (PAD+PANEL_W+GAP = 20+324+16 = 360)
CROP_X, CROP_Y = PAD + PANEL_W + GAP, PAD + HDR_H + FTR_H  # = 360, 102

# ── Load concept crops ────────────────────────────────────────────────────────
panels = []
for slug in SLUGS:
    path = f"docs/store_equipped_v3_2_checkmarks/{slug}/round_2.png"
    raw = pygame.image.load(path)
    # Crop concept panel (panel 1 in the r2 sheet)
    sub = raw.subsurface(pygame.Rect(CROP_X, CROP_Y, PANEL_W, PANEL_H))
    panels.append(sub.copy())

# ── Canvas ────────────────────────────────────────────────────────────────────
N      = len(panels)
width  = PAD + N * PANEL_W + (N - 1) * GAP + PAD
height = PAD + HDR_H + FTR_H + PANEL_H + FTR_H + PAD

canvas = pygame.Surface((width, height))
canvas.fill(BG)

# Header
title_f = hud_font(22, True)
tt = title_f.render("checkmark variants · equipped card tag · r2 showcase", True, GOLD)
canvas.blit(tt, tt.get_rect(midtop=(width // 2, PAD // 2 + 4)))

lbl_f  = hud_font(14, True)
panel_y = PAD + HDR_H + FTR_H

for i, (slug, panel) in enumerate(zip(SLUGS, panels)):
    px = PAD + i * (PANEL_W + GAP)
    # Slug label above panel
    lt = lbl_f.render(slug, True, GOLD)
    canvas.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 4)))
    # Panel
    canvas.blit(panel, (px, panel_y))
    # Footer label below panel
    ft = lbl_f.render("FINAL", True, CREAM)
    canvas.blit(ft, ft.get_rect(midtop=(px + PANEL_W // 2, panel_y + PANEL_H + 4)))

OUT = "docs/store_equipped_v3_2_checkmarks/showcase.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
print(f"saved {width}×{height} → {OUT}")
