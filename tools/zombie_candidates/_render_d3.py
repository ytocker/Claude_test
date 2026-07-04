"""Render the Design 3 (Voodoo Hex Bird) round-1 review sheet.

Three columns per the brief: an in-gameplay panel, a clean hero box, and a
40px NEAREST truth-read (down to 40x40 then back up 5x) so the shrink read
that decides a costume is judged honestly.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render
from tools.zombie_candidates.design_3 import build

OUT = "docs/store_redesign/costume/zombie/design_3/round_1.png"

MARGIN = 24
TITLE_H = 56
GAP = 24
GP_W, GP_H = 200, 350
HERO = 280
READ = 200

sheet_w = MARGIN * 2 + GP_W + GAP + HERO + GAP + READ
sheet_h = TITLE_H + MARGIN + max(GP_H, HERO, READ) + MARGIN

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 26))

font_big = pygame.font.SysFont("arial", 26, bold=True)
font_sm = pygame.font.SysFont("arial", 15)

title = font_big.render("DESIGN 3 — VOODOO HEX BIRD", True, (196, 255, 206))
sheet.blit(title, (MARGIN, (TITLE_H - title.get_height()) // 2))

y0 = TITLE_H + MARGIN
x = MARGIN

# 1 — gameplay panel
gp = ninja_render.gameplay_panel(build, GP_W, GP_H)
sheet.blit(gp, (x, y0))
sheet.blit(font_sm.render("in gameplay", True, (170, 170, 190)),
           (x, y0 + GP_H + 4))
x += GP_W + GAP

# 2 — hero box
hero = ninja_render.hero_panel(build, HERO, tilt=0.0)
sheet.blit(hero, (x, y0))
sheet.blit(font_sm.render("hero shot", True, (170, 170, 190)),
           (x, y0 + HERO + 4))
x += HERO + GAP

# 3 — 40px truth-read: hero frame down to 40x40 (NEAREST) then up 5x.
frame = build(ninja_render.FRAME_IDX, 0.0)
bb = frame.get_bounding_rect()
if bb.width and bb.height:
    frame = frame.subsurface(bb).copy()
sq = pygame.Surface((40, 40), pygame.SRCALPHA)
sw, sh = frame.get_size()
sc = 38 / max(sw, sh)
fs = pygame.transform.smoothscale(frame, (max(1, int(sw * sc)), max(1, int(sh * sc))))
sq.blit(fs, fs.get_rect(center=(20, 20)))
small = pygame.transform.scale(sq, (40, 40))
big = pygame.transform.scale(small, (READ, READ))
read_bg = pygame.Surface((READ, READ))
read_bg.fill((32, 30, 42))
read_bg.blit(big, (0, 0))
sheet.blit(read_bg, (x, y0))
sheet.blit(font_sm.render("40px read", True, (170, 170, 190)),
           (x, y0 + READ + 4))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
