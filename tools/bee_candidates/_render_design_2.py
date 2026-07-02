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


# Day gameplay + a hero product-shot on a night panel so the molten rainbow
# bands read against the dark sky the sunset moth is built to own.
gameplay = ninja_render.gameplay_panel(build, 220, 320)
hero = ninja_render.hero_panel(build, 220, bg=(10, 12, 26))

# 40px NEAREST truth over BOTH a day-sky and a night-sky plate, across three
# poses (down-stroke / mid / up-stroke): the obsidian-body + rainbow-band read,
# the scalloped cream fringe, and the hue-sweep all have to survive shrunk to
# game size on both skies.
TRUTH_POSES = [(0, "down"), (1, "mid"), (2, "up")]
truth40 = []
for fi, name in TRUTH_POSES:
    src = build(fi, 10.0)
    tw, th = src.get_size()
    truth40.append((name,
                    pygame.transform.scale(src, (40, max(1, int(th * 40 / tw))))))
t40h = max(t.get_height() for _, t in truth40)
truth_block_w = 96
truth_block_h = t40h + 2 * LABEL_H + 12

# 4-frame filmstrip on a dark strip so the polychrome hue-sweep is visible
# (frame 0 magenta -> 1 emerald -> 2 orange -> 3 back toward magenta).
frames = [build(i, 0.0) for i in range(4)]
fw = max(f.get_width() for f in frames)
fh = max(f.get_height() for f in frames)

top_h = max(gameplay.get_height(), hero.get_height(),
            truth_block_h, 200) + LABEL_H
strip_w = len(frames) * (fw + 12)
sheet_w = PAD * 4 + gameplay.get_width() + hero.get_width() + truth_block_w + 40
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

label(sheet, "40px: day|night", x, y)
small = pygame.font.SysFont("dejavusans", 11)
ty = y + LABEL_H
for name, t in truth40:
    day = pygame.Rect(x, ty, 42, t40h + 14)
    pygame.draw.rect(sheet, (150, 170, 190), day)        # day-sky value
    nite = pygame.Rect(x + 44, ty, 42, t40h + 14)
    pygame.draw.rect(sheet, (10, 12, 24), nite)          # night-sky value
    sheet.blit(t, (x + 1, ty + 7))
    sheet.blit(t, (x + 45, ty + 7))
    sheet.blit(small.render(name, True, (210, 210, 210)),
               (x, ty + t40h + 15))
    ty += t40h + 30

sy = PAD * 2 + top_h
label(sheet, "4-FRAME FILMSTRIP (hue-sweep: magenta -> emerald -> orange)",
      PAD, sy)
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
