import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()

from tools import ninja_render
from tools.thunderbird_candidates.design_1 import build

PAD = 20
LABEL_H = 26
font = pygame.font.SysFont("dejavusans", 16, bold=True)
title_font = pygame.font.SysFont("dejavusans", 18, bold=True)


def label(surf, text, x, y, f=font):
    surf.blit(f.render(text, True, (240, 240, 240)), (x, y))


gameplay = ninja_render.gameplay_panel(build, 220, 320)
hero = ninja_render.hero_panel(build, 220)

# 40px NEAREST truth (canonical mid-flight pose).
truth_src = build(2, 10.0)
tw, th = truth_src.get_size()
truth40 = pygame.transform.scale(truth_src, (40, max(1, int(th * 40 / tw))))

frames = [build(i, 0.0) for i in range(4)]
fw = max(f.get_width() for f in frames)
fh = max(f.get_height() for f in frames)

TITLE_H = 26
top_h = max(gameplay.get_height(), hero.get_height(), 200) + LABEL_H
strip_w = len(frames) * (fw + 12)
sheet_w = PAD * 4 + gameplay.get_width() + hero.get_width() + 220
sheet_w = max(sheet_w, PAD * 2 + strip_w)
sheet_h = TITLE_H + PAD * 3 + top_h + LABEL_H + fh + LABEL_H

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((24, 24, 30))

label(sheet, "STORM HERALD  -  thunderbird design_1  round_2", PAD, 6, title_font)

x = PAD
y = TITLE_H + PAD
label(sheet, "GAMEPLAY (day)", x, y)
sheet.blit(gameplay, (x, y + LABEL_H))
x += gameplay.get_width() + PAD

label(sheet, "HERO", x, y)
sheet.blit(hero, (x, y + LABEL_H))
x += hero.get_width() + PAD

label(sheet, "40px NEAREST truth", x, y)
plate = pygame.Rect(x, y + LABEL_H, 60, 60 + truth40.get_height())
pygame.draw.rect(sheet, (40, 40, 50), plate)
sheet.blit(truth40, (x + 10, y + LABEL_H + 10))

sy = TITLE_H + PAD * 2 + top_h
labels = ("f0 power-flap", "f1", "f2", "f3 thunderclap")
label(sheet, "4-FRAME FILMSTRIP", PAD, sy)
fx = PAD
fy = sy + LABEL_H
for i, f in enumerate(frames):
    pygame.draw.rect(sheet, (36, 36, 44), pygame.Rect(fx, fy, fw + 8, fh + 8))
    sheet.blit(f, (fx + 4 + (fw - f.get_width()) // 2,
                   fy + 4 + (fh - f.get_height()) // 2))
    label(sheet, labels[i], fx + 4, fy + fh + 10)
    fx += fw + 12

out = "/home/user/skybit/docs/store_redesign/animal/thunderbird/design_1/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out)
