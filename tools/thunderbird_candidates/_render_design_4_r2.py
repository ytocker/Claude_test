"""Stitch the Design 4 (NIGHT THUNDER) round-2 review sheet."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

import sys
sys.path.insert(0, "/home/user/skybit")

import importlib
from tools import ninja_render
from tools.thunderbird_candidates import design_4 as d4
importlib.reload(d4)

build = d4.build

PAD = 16
BG = (18, 16, 26)
LABEL = (220, 214, 240)
font = pygame.font.SysFont("arial", 15, bold=True)
small = pygame.font.SysFont("arial", 12)


def label(surf, text, x, y):
    surf.blit(font.render(text, True, LABEL), (x, y))


# --- Panels ---
gp = ninja_render.gameplay_panel(build, 220, 320)
hero = ninja_render.hero_panel(build, 220)

# 40px NEAREST truth
truth_src = build(2, 10.0)
tw, th = truth_src.get_size()
scale40 = 40 / tw
truth40 = pygame.transform.scale(
    truth_src, (40, max(1, int(th * scale40))))
# Up-res the 40px for visibility (nearest, so the pixels stay honest).
truth_big = pygame.transform.scale_by(truth40, 4)

# 4-frame filmstrip at natural size
frames = [build(i, 0) for i in range(4)]
fw = sum(f.get_width() for f in frames) + PAD * 3
fh = max(f.get_height() for f in frames)

# --- Layout ---
top_h = max(gp.get_height(), hero.get_height(), truth_big.get_height() + 40)
sheet_w = gp.get_width() + hero.get_width() + truth_big.get_width() + PAD * 4
sheet_w = max(sheet_w, fw + PAD * 2)
sheet_h = 40 + top_h + 60 + fh + PAD * 2
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title = pygame.font.SysFont("arial", 22, bold=True).render(
    "THUNDERBIRD — Design 4: NIGHT THUNDER (Round 2)", True, (200, 180, 255))
sheet.blit(title, (PAD, 8))

y0 = 44
x = PAD
sheet.blit(gp, (x, y0))
label(sheet, "Gameplay (day)", x, y0 + gp.get_height() + 4)
x += gp.get_width() + PAD

sheet.blit(hero, (x, y0))
label(sheet, "Hero (dark)", x, y0 + hero.get_height() + 4)
x += hero.get_width() + PAD

sheet.blit(truth_big, (x, y0))
label(sheet, "40px NEAREST truth", x, y0 + truth_big.get_height() + 4)
sheet.blit(small.render("(4x zoom, nearest)", True, LABEL),
           (x, y0 + truth_big.get_height() + 22))

# Filmstrip row
fy = y0 + top_h + 40
label(sheet, "4-frame filmstrip  (frame 0 = power-flap scar flash)", PAD, fy - 20)
fx = PAD
for i, f in enumerate(frames):
    sheet.blit(f, (fx, fy))
    sheet.blit(small.render(f"f{i} a={ [50,20,-10,-40][i] }", True, LABEL),
               (fx, fy + f.get_height() + 2))
    fx += f.get_width() + PAD

out = "/home/user/skybit/docs/store_redesign/animal/thunderbird/design_4/round_2.png"
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
