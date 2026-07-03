"""Render the design_2 BERSERKER round-2 review sheet: for each palette
(IRONCLAD then BLOODAXE) — a hero zoom, an in-gameplay panel, and a 40px NEAREST
truth read. Headless. Saves to
docs/store_redesign/costume/viking/face/design_2/round_2.png.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render as NR
from tools.viking_face_candidates import design_2 as D

OUT = "/home/user/skybit/docs/store_redesign/costume/viking/face/design_2/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

font = pygame.font.SysFont("arial", 18, bold=True)
small = pygame.font.SysFont("arial", 13)

HERO = 220
GAME_W, GAME_H = 160, 240
TRUTH = 40
TRUTH_BOX = 160

ROWS = [
    ("VIKING — BERSERKER", "IRONCLAD", D.build_ironclad),
    ("VIKING — BERSERKER", "BLOODAXE", D.build_bloodaxe),
]

PAD = 18
LABEL_H = 30
cell_h = max(HERO, GAME_H, TRUTH_BOX)
row_h = cell_h + LABEL_H + PAD
col_x = [PAD, PAD + HERO + PAD, PAD + HERO + PAD + GAME_W + PAD]
sheet_w = col_x[2] + TRUTH_BOX + PAD
sheet_h = PAD + len(ROWS) * row_h + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((30, 28, 38))

heads = ["HERO ZOOM", "IN-GAMEPLAY", "40px TRUTH (nearest)"]
for cx, txt in zip(col_x, heads):
    t = small.render(txt, True, (200, 200, 215))
    sheet.blit(t, (cx, PAD - 4))

for ri, (name, pal, build) in enumerate(ROWS):
    y0 = PAD + LABEL_H + ri * row_h
    lab = font.render(f"{name}  [{pal}]", True, (255, 230, 180))
    sheet.blit(lab, (PAD, y0 - LABEL_H + 6))

    hero = NR.hero_panel(build, HERO, frame_idx=2, tilt=0.0)
    sheet.blit(hero, (col_x[0], y0))

    game = NR.gameplay_panel(build, GAME_W, GAME_H, frame_idx=2, tilt=10.0)
    sheet.blit(game, (col_x[1], y0 + (cell_h - GAME_H) // 2))

    raw = build(2, 0.0)
    bb = raw.get_bounding_rect()
    if bb.width and bb.height:
        raw = raw.subsurface(bb).copy()
    sw, sh = raw.get_size()
    sc = TRUTH / max(sw, sh)
    tiny = pygame.transform.smoothscale(raw, (max(1, int(sw * sc)), max(1, int(sh * sc))))
    big = pygame.transform.scale(tiny, (tiny.get_width() * 4, tiny.get_height() * 4))
    tbg = pygame.Surface((TRUTH_BOX, TRUTH_BOX))
    tbg.fill((52, 60, 78))
    tbg.blit(big, big.get_rect(center=(TRUTH_BOX // 2, TRUTH_BOX // 2)))
    pygame.draw.rect(tbg, (90, 100, 120), tbg.get_rect(), 1)
    sheet.blit(tbg, (col_x[2], y0 + (cell_h - TRUTH_BOX) // 2))

pygame.image.save(sheet, OUT)
print("WROTE", OUT, sheet.get_size())
