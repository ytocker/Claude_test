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


# Day gameplay proves the dark-chitin outline separates the beetle from pale
# sky; a night hero panel proves the gold specular streak keeps the dome from
# reading as a flat black blob on a dark sky.
gameplay = ninja_render.gameplay_panel(build, 220, 320)
hero = ninja_render.hero_panel(build, 220, bg=(10, 10, 18))

# 40px NEAREST truth on both a light day-sky plate and a dark night-sky plate —
# the horn tell must poke above the head at size on either.
truth_src = build(3, 10.0)   # frame 3 = down-stroke, elytra cracked open
tw, th = truth_src.get_size()
scale = 40 / tw
truth40 = pygame.transform.scale(truth_src, (40, max(1, int(th * scale))))
truth40x3 = pygame.transform.scale(
    truth40, (truth40.get_width() * 3, truth40.get_height() * 3))

# 4-frame filmstrip on a dark strip so the elytra crack / hindwing fan reads.
frames = [build(i, 0.0) for i in range(4)]
fw = max(f.get_width() for f in frames)
fh = max(f.get_height() for f in frames)

top_h = max(gameplay.get_height(), hero.get_height(), 200) + LABEL_H
strip_w = len(frames) * (fw + 12)
sheet_w = PAD * 5 + gameplay.get_width() + hero.get_width() + 260
sheet_w = max(sheet_w, PAD * 2 + strip_w)
sheet_h = PAD * 3 + top_h + LABEL_H + fh + LABEL_H + 30

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((24, 22, 26))

label(sheet, "design_3  IRONHORN  -  Rhinoceros / Hercules beetle (skin_bee)",
      PAD, 4)

x = PAD
y = PAD + 8
label(sheet, "GAMEPLAY (day)", x, y)
sheet.blit(gameplay, (x, y + LABEL_H))
x += gameplay.get_width() + PAD

label(sheet, "HERO (night)", x, y)
sheet.blit(hero, (x, y + LABEL_H))
x += hero.get_width() + PAD

label(sheet, "40px truth: day / night", x, y)
plate = pygame.Rect(x, y + LABEL_H, truth40.get_width() * 2 + 30,
                    truth40.get_height() + 20)
pygame.draw.rect(sheet, (150, 170, 195), plate)          # day-sky value
night = pygame.Rect(x + plate.width // 2, y + LABEL_H,
                    plate.width // 2, plate.height)
pygame.draw.rect(sheet, (12, 12, 26), night)             # night-sky value
sheet.blit(truth40, (x + 15, y + LABEL_H + 10))
sheet.blit(truth40, (x + plate.width // 2 + 15, y + LABEL_H + 10))

# 3x magnified truth read beneath so the horn tell is judgeable up close.
ty2 = y + LABEL_H + plate.height + 14
label(sheet, "40px @3x (horn tell)", x, ty2, small, (200, 200, 200))
day3 = pygame.Rect(x, ty2 + 18, truth40x3.get_width() + 12,
                   truth40x3.get_height() + 12)
pygame.draw.rect(sheet, (150, 170, 195), day3)
sheet.blit(truth40x3, (x + 6, ty2 + 24))
nx3 = x + day3.width + 8
n3 = pygame.Rect(nx3, ty2 + 18, truth40x3.get_width() + 12,
                 truth40x3.get_height() + 12)
pygame.draw.rect(sheet, (12, 12, 26), n3)
sheet.blit(truth40x3, (nx3 + 6, ty2 + 24))

sy = PAD * 2 + top_h + 8
label(sheet, "4-FRAME FILMSTRIP  (down-stroke: elytra crack + hindwings fan -> tuck shut)",
      PAD, sy)
flabels = ["f0 up (50)", "f1 mid (20)", "f2 level (-10)", "f3 down (-40)"]
fx = PAD
fy = sy + LABEL_H
for i, f in enumerate(frames):
    pygame.draw.rect(sheet, (14, 13, 24),
                     pygame.Rect(fx, fy, fw + 8, fh + 8))
    sheet.blit(f, (fx + 4 + (fw - f.get_width()) // 2,
                   fy + 4 + (fh - f.get_height()) // 2))
    label(sheet, flabels[i], fx, fy + fh + 12, small, (200, 200, 200))
    fx += fw + 12

out = "/home/user/skybit/docs/store_redesign/animal/bee/design_3/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out)
