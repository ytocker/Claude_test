import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()

from tools import ninja_render
from tools.bee_candidates.design_3 import build

PAD = 20
LABEL_H = 26
font = pygame.font.SysFont("dejavusans", 16, bold=True)
small = pygame.font.SysFont("dejavusans", 12)


def label(surf, text, x, y, f=font, c=(240, 240, 240)):
    surf.blit(f.render(text, True, c), (x, y))


# Day gameplay proves the pale-lime wing + dark outline separate from bright
# sky; a night hero panel proves the green moonlit bloom keeps the ghost-pale
# moth from vanishing on a dark plate.
gameplay = ninja_render.gameplay_panel(build, 220, 320)
hero = ninja_render.hero_panel(build, 220, bg=(9, 12, 20))

# 40px NEAREST truth on a light day plate and a dark night plate — the two
# trailing tails are the ID and must still read at size on either.
def truth40(frame_idx):
    src = build(frame_idx, 8.0)
    tw, th = src.get_size()
    sc = 40 / tw
    return pygame.transform.scale(src, (40, max(1, int(th * sc))))


poses = [(0, "f0 up"), (2, "f2 level"), (3, "f3 down")]
truths = [(truth40(i), lbl) for i, lbl in poses]
t40w = truths[0][0].get_width()
t40h = truths[0][0].get_height()

# 4-frame filmstrip on a dark strip so the tails + moonlit pulse read.
frames = [build(i, 0.0) for i in range(4)]
fw = max(f.get_width() for f in frames)
fh = max(f.get_height() for f in frames)

top_h = max(gameplay.get_height(), hero.get_height(), 200) + LABEL_H
sheet_w = PAD * 5 + gameplay.get_width() + hero.get_width() + 320
sheet_h = PAD * 3 + top_h + LABEL_H + fh + LABEL_H + 30

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((22, 24, 22))

label(sheet, "design_3  LUNAWING  -  Luna moth (Actias luna)  (skin_bee)",
      PAD, 4)

x = PAD
y = PAD + 8
label(sheet, "GAMEPLAY (day)", x, y)
sheet.blit(gameplay, (x, y + LABEL_H))
x += gameplay.get_width() + PAD

label(sheet, "HERO (night bloom)", x, y)
sheet.blit(hero, (x, y + LABEL_H))
x += hero.get_width() + PAD

label(sheet, "40px truth: day | night (3 poses)", x, y)
cell_w = t40w + 12
row_h = t40h + 8
gy = y + LABEL_H
# day column then night column, 3 poses each
day_plate = pygame.Rect(x, gy, cell_w, row_h * 3 + 6)
night_plate = pygame.Rect(x + cell_w + 8, gy, cell_w, row_h * 3 + 6)
pygame.draw.rect(sheet, (150, 170, 195), day_plate)
pygame.draw.rect(sheet, (11, 12, 24), night_plate)
for r, (t, lbl) in enumerate(truths):
    yy = gy + 4 + r * row_h
    sheet.blit(t, (x + 6, yy))
    sheet.blit(t, (x + cell_w + 8 + 6, yy))
    label(sheet, lbl, x + cell_w * 2 + 22, yy + t40h // 2 - 6, small,
          (210, 210, 210))

# 3x magnified truth (down-stroke pose) so the tail read is judgeable up close.
big = pygame.transform.scale(truths[2][0],
                             (t40w * 3, t40h * 3))
bx = x
by = gy + row_h * 3 + 18
label(sheet, "40px @3x  (tail tell, f3)", bx, by, small, (210, 210, 210))
d3 = pygame.Rect(bx, by + 18, big.get_width() + 12, big.get_height() + 12)
pygame.draw.rect(sheet, (150, 170, 195), d3)
sheet.blit(big, (bx + 6, by + 24))
n3x = bx + d3.width + 8
n3 = pygame.Rect(n3x, by + 18, big.get_width() + 12, big.get_height() + 12)
pygame.draw.rect(sheet, (11, 12, 24), n3)
sheet.blit(big, (n3x + 6, by + 24))

sy = PAD * 2 + top_h + 8
label(sheet, "4-FRAME FILMSTRIP  (glow pulses brightest on f3 down-stroke)",
      PAD, sy)
flabels = ["f0 up (50)", "f1 mid (20)", "f2 level (-10)", "f3 down (-40)"]
fx = PAD
fy = sy + LABEL_H
for i, f in enumerate(frames):
    pygame.draw.rect(sheet, (13, 15, 13),
                     pygame.Rect(fx, fy, fw + 8, fh + 8))
    sheet.blit(f, (fx + 4 + (fw - f.get_width()) // 2,
                   fy + 4 + (fh - f.get_height()) // 2))
    label(sheet, flabels[i], fx, fy + fh + 12, small, (200, 200, 200))
    fx += fw + 12

out = "/home/user/skybit/docs/store_redesign/animal/bee/design_3/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out)
