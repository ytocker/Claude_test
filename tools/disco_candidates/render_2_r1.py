"""Render the D2 STARDUST DIVA round-1 review sheet.

Three reads side by side so the costume can be judged the way it ships:
an in-gameplay crop (the true 40px-ish read over a live daytime scene), a
clean hero product-shot, and a hard 40px "truth" downscale to catch anything
that muds out at store-card size.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import tools.ninja_render as nr
from tools.disco_candidates.design_2 import build

pygame.init()

gp = nr.gameplay_panel(build, 220, 392)
hp = nr.hero_panel(build, 320)
frame = nr._frame(build, nr.FRAME_IDX, nr.TILT)
truth = pygame.transform.scale(pygame.transform.scale(frame, (40, 40)), (200, 200))

PAD = 20
TITLE_H = 54
sheet_w = PAD * 4 + 220 + 320 + 200
sheet_h = TITLE_H + PAD * 2 + 392
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 26))

font = pygame.font.SysFont("Arial", 26, bold=True)
sub = pygame.font.SysFont("Arial", 15)
sheet.blit(font.render("D2 STARDUST DIVA — R1", True, (245, 240, 250)),
           (PAD, 16))

x = PAD
y = TITLE_H + PAD
for label, panel in (("gameplay", gp), ("hero", hp), ("40px truth", truth)):
    sheet.blit(panel, (x, y))
    sheet.blit(sub.render(label, True, (170, 165, 185)), (x, y - 18))
    x += panel.get_width() + PAD

out = "docs/store_redesign/costume/disco/design_2/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out)
