import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()

from tools import ninja_render
from tools.bee_candidates.design_2 import build

PAD = 20
LABEL_H = 26
font = pygame.font.SysFont("dejavusans", 16, bold=True)


def label(surf, text, x, y):
    surf.blit(font.render(text, True, (240, 240, 240)), (x, y))


# Day gameplay + a hero product-shot on a night panel so the bio-green pulse
# reads against the dark sky it is designed to own.
gameplay = ninja_render.gameplay_panel(build, 220, 320)
hero = ninja_render.hero_panel(build, 220, bg=(10, 12, 26))

# 40px NEAREST truth on both a light plate and a dark plate — the two-part
# read (dark beetle + glowing lantern) has to survive on day AND night.
truth_src = build(0, 10.0)   # frame 0 = down-stroke, brightest pulse
tw, th = truth_src.get_size()
scale = 40 / tw
truth40 = pygame.transform.scale(truth_src, (40, max(1, int(th * scale))))

# 4-frame filmstrip on a dark strip so the pulse animation is visible.
frames = [build(i, 0.0) for i in range(4)]
fw = max(f.get_width() for f in frames)
fh = max(f.get_height() for f in frames)

top_h = max(gameplay.get_height(), hero.get_height(), 200) + LABEL_H
strip_w = len(frames) * (fw + 12)
sheet_w = PAD * 4 + gameplay.get_width() + hero.get_width() + 220
sheet_w = max(sheet_w, PAD * 2 + strip_w)
sheet_h = PAD * 3 + top_h + LABEL_H + fh + LABEL_H

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((24, 24, 30))

x = PAD
y = PAD
label(sheet, "GAMEPLAY (day)", x, y)
sheet.blit(gameplay, (x, y + LABEL_H))
x += gameplay.get_width() + PAD

label(sheet, "HERO (night)", x, y)
sheet.blit(hero, (x, y + LABEL_H))
x += hero.get_width() + PAD

label(sheet, "40px truth: day / night", x, y)
plate = pygame.Rect(x, y + LABEL_H, 120, 60 + truth40.get_height())
pygame.draw.rect(sheet, (150, 170, 190), plate)          # day-sky value
night = pygame.Rect(x + 60, y + LABEL_H, 60, plate.height)
pygame.draw.rect(sheet, (12, 14, 30), night)             # night-sky value
sheet.blit(truth40, (x + 10, y + LABEL_H + 10))
sheet.blit(truth40, (x + 70, y + LABEL_H + 10))

sy = PAD * 2 + top_h
label(sheet, "4-FRAME FILMSTRIP (down-stroke pulse -> dim)", PAD, sy)
fx = PAD
fy = sy + LABEL_H
for i, f in enumerate(frames):
    pygame.draw.rect(sheet, (14, 16, 30),
                     pygame.Rect(fx, fy, fw + 8, fh + 8))
    sheet.blit(f, (fx + 4 + (fw - f.get_width()) // 2,
                   fy + 4 + (fh - f.get_height()) // 2))
    fx += fw + 12

out = "/home/user/skybit/docs/store_redesign/animal/bee/design_2/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out)
