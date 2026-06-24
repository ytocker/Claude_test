"""Render the v4 design_1 RADIOGRAPH round_1 review sheet (scratch only)."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render as NR
from tools.skeleton_candidates.v4_design_1 import build

OUT = "docs/store_redesign/costume/skeleton/v4/design_1/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

font = pygame.font.SysFont("dejavusans", 16, bold=True)
small = pygame.font.SysFont("dejavusans", 13)


def label(surf, text, x, y, col=(235, 240, 250)):
    surf.blit(font.render(text, True, col), (x, y))


# Panels.
hero = NR.hero_panel(build, 360)
gameplay = NR.gameplay_panel(build, 220, 392)

# Night check: build(2,10) centred on dark navy.
night = pygame.Surface((220, 260))
night.fill((18, 20, 34))
nf = build(2, 10.0)
night.blit(nf, nf.get_rect(center=(110, 130)))

# 40px truth read: scale to 40 wide (nearest), upscale x5.
truth_src = build(2, 10.0)
sw, sh = truth_src.get_size()
tw = 40
th = max(1, int(sh * tw / sw))
small40 = pygame.transform.scale(truth_src, (tw, th))
big = pygame.transform.scale(small40, (tw * 5, th * 5))
truth = pygame.Surface((tw * 5 + 20, th * 5 + 20))
truth.fill((40, 44, 60))
truth.blit(big, (10, 10))

# Compose sheet.
PAD = 18
TITLE_H = 40
col_w = max(hero.get_width(), gameplay.get_width(),
            night.get_width(), truth.get_width())
sheet_w = hero.get_width() + gameplay.get_width() + PAD * 3
top_row_h = max(hero.get_height(), gameplay.get_height())
bot_row_h = max(night.get_height(), truth.get_height())
sheet_h = TITLE_H + top_row_h + bot_row_h + PAD * 4 + 24 * 2

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((24, 26, 36))

label(sheet, "v4 SKELETON · design_1 · RADIOGRAPH · R2 (thin halo, bone cores cut through)",
      PAD, 12, (170, 200, 255))

y = TITLE_H + PAD
# Top row: hero + gameplay.
sheet.blit(hero, (PAD, y + 24))
label(sheet, "HERO — product shot", PAD, y)
gx = PAD * 2 + hero.get_width()
sheet.blit(gameplay, (gx, y + 24))
label(sheet, "GAMEPLAY — day, mid-flight", gx, y)

y2 = y + top_row_h + 24 + PAD
sheet.blit(night, (PAD, y2 + 24))
label(sheet, "NIGHT — reads on navy", PAD, y2)
tx = PAD * 2 + night.get_width()
sheet.blit(truth, (tx, y2 + 24))
label(sheet, "40px TRUTH READ (x5)", tx, y2)

pygame.image.save(sheet, OUT)
print("saved", OUT, sheet.get_size())
