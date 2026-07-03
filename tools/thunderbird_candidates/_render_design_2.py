import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()

from tools import ninja_render
from tools.thunderbird_candidates.design_2 import build

PAD = 20
LABEL_H = 26
font = pygame.font.SysFont("dejavusans", 16, bold=True)


def label(surf, text, x, y):
    surf.blit(font.render(text, True, (240, 240, 240)), (x, y))


# Panels
gameplay = ninja_render.gameplay_panel(build, 220, 320)
hero = ninja_render.hero_panel(build, 220)

# 40px NEAREST truth
truth_src = build(2, 10.0)
tw, th = truth_src.get_size()
scale = 40 / tw
truth40 = pygame.transform.scale(
    truth_src, (40, max(1, int(th * scale))))

# 4-frame filmstrip at natural size
frames = [build(i, 0.0) for i in range(4)]
fw = max(f.get_width() for f in frames)
fh = max(f.get_height() for f in frames)

# Layout
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

label(sheet, "HERO", x, y)
sheet.blit(hero, (x, y + LABEL_H))
x += hero.get_width() + PAD

label(sheet, "40px NEAREST truth", x, y)
# checker-ish dark plate behind the tiny truth so alpha reads
plate = pygame.Rect(x, y + LABEL_H, 60, 60 + truth40.get_height())
pygame.draw.rect(sheet, (40, 40, 50), plate)
sheet.blit(truth40, (x + 10, y + LABEL_H + 10))

# Filmstrip row
sy = PAD * 2 + top_h
label(sheet, "4-FRAME FILMSTRIP", PAD, sy)
fx = PAD
fy = sy + LABEL_H
for i, f in enumerate(frames):
    pygame.draw.rect(sheet, (36, 36, 44),
                     pygame.Rect(fx, fy, fw + 8, fh + 8))
    sheet.blit(f, (fx + 4 + (fw - f.get_width()) // 2,
                   fy + 4 + (fh - f.get_height()) // 2))
    fx += fw + 12

out = "/home/user/skybit/docs/store_redesign/animal/thunderbird/design_2/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out)
