"""Round-2 review sheet for thunderbird DESIGN 9 — TESLA CROWN.

Shows all 4 wing frames in-gameplay (to judge the crown's breathing pulse)
plus a large clean hero shot for costume detail. Headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_thunderbird_design9_round2.py``
"""
from __future__ import annotations
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()

import tools.ninja_render as nr
from tools.thunderbird_candidates.design_9 import build
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP

PANEL_W, PANEL_H = 210, 360
HERO = 360
PAD, GUTTER = 26, 18
TITLE_H, CAP_H = 78, 40

# Four gameplay panels (one per wing frame) + one hero shot.
n_gp = 4
sheet_w = PAD * 2 + n_gp * PANEL_W + (n_gp - 1) * GUTTER + GUTTER + HERO
sheet_h = TITLE_H + max(PANEL_H, HERO) + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(26, True).render(
    "THUNDERBIRD DESIGN 9 — TESLA CROWN  ·  ROUND 2", True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 18)))
sub = _font(14).render(
    "4 wing frames in-gameplay (crown breathes) + hero", True, (170, 162, 190))
sheet.blit(sub, sub.get_rect(midtop=(sheet_w // 2, 52)))

cap_font = _font(13, True)
FRAME_LABELS = ["FRAME 0 (up-stroke)", "FRAME 1", "FRAME 2", "FRAME 3 (down-stroke)"]

y = TITLE_H
for i in range(n_gp):
    x = PAD + i * (PANEL_W + GUTTER)
    panel = nr.gameplay_panel(build, PANEL_W, PANEL_H, frame_idx=i, tilt=10.0)
    pygame.draw.rect(sheet, _GOLD_DEEP,
                     pygame.Rect(x - 2, y - 2, PANEL_W + 4, PANEL_H + 4), width=2)
    sheet.blit(panel, (x, y))
    cap = cap_font.render(FRAME_LABELS[i], True, (185, 178, 205))
    sheet.blit(cap, (x + 2, y + PANEL_H + 10))

hx = PAD + n_gp * (PANEL_W + GUTTER)
hero = nr.hero_panel(build, HERO, frame_idx=3, tilt=0.0)
pygame.draw.rect(sheet, _GOLD_DEEP,
                 pygame.Rect(hx - 2, y - 2, HERO + 4, HERO + 4), width=2)
sheet.blit(hero, (hx, y))
cap = cap_font.render("HERO — crown detail", True, (185, 178, 205))
sheet.blit(cap, (hx + 2, y + HERO + 10))

out = os.path.join("docs", "store_redesign", "animal", "thunderbird",
                   "design_9", "round_2.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
