"""Round-1 review sheet for thunderbird TESLA CROWN (design_9)."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

import sys
sys.path.insert(0, "/home/user/skybit")

from tools import ninja_render
from tools.thunderbird_candidates.design_9 import build

OUT = "/home/user/skybit/docs/store_redesign/animal/thunderbird/design_9/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

pad = 16
label_h = 22
font = pygame.font.SysFont("dejavusans", 15, bold=True)
small = pygame.font.SysFont("dejavusans", 12)

# --- Panels ---
gp = ninja_render.gameplay_panel(build, 220, 320)
hero = ninja_render.hero_panel(build, 220, bg=(14, 15, 20))

# 40px NEAREST truth — the crown-of-sparks read is judged here.
truth_src = build(0, 10.0)   # down-stroke frame: arcs at full bloom
tw = 40
th = int(truth_src.get_height() * tw / truth_src.get_width())
truth = pygame.transform.scale(truth_src, (tw, th))

# Filmstrip natural size.
strip = [build(i, 0.0) for i in range(4)]
fw = max(f.get_width() for f in strip)
fh = max(f.get_height() for f in strip)

# --- Layout ---
top_h = max(gp.get_height(), hero.get_height()) + label_h
truth_panel_h = 160
strip_h = fh + label_h + pad
sheet_w = pad * 3 + gp.get_width() + hero.get_width()
sheet_w = max(sheet_w, pad * 2 + 4 * (fw + 8))
sheet_w = max(sheet_w, 560)
sheet_h = pad + 40 + top_h + pad + truth_panel_h + pad + strip_h + pad

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 19, 24))

title = pygame.font.SysFont("dejavusans", 18, bold=True).render(
    "THUNDERBIRD  —  Design 9: TESLA CROWN  (Round 1)", True, (255, 232, 26))
sheet.blit(title, (pad, pad))

y = pad + 40


def caption(x, yy, text, w):
    surf = font.render(text, True, (210, 210, 220))
    sheet.blit(surf, (x + (w - surf.get_width()) // 2, yy))


# Row 1: gameplay + hero
x = pad
caption(x, y, "In-gameplay (day)", gp.get_width())
sheet.blit(gp, (x, y + label_h))
x += gp.get_width() + pad
caption(x, y, "Hero (charcoal)", hero.get_width())
sheet.blit(hero, (x, y + label_h))
y += top_h + pad

# Row 2: 40px truth chips on bright + dark backgrounds.
caption(pad, y, "40px NEAREST truth  —  build(0, 10)  on bright-day + night sky", sheet_w - pad * 2)
cy = y + label_h + 20
chip = 120
bright = pygame.Surface((chip, chip))
bright.fill((150, 205, 235))
bright.blit(truth, truth.get_rect(center=(chip // 2, chip // 2)))
sheet.blit(bright, (pad, cy))
sheet.blit(small.render("bright day", True, (40, 40, 50)), (pad + 6, cy + chip - 18))
dark = pygame.Surface((chip, chip))
dark.fill((10, 14, 26))
dark.blit(truth, truth.get_rect(center=(chip // 2, chip // 2)))
sheet.blit(dark, (pad + chip + pad, cy))
sheet.blit(small.render("night", True, (200, 210, 220)), (pad + chip + pad + 6, cy + chip - 18))
sheet.blit(small.render("(shown 40px wide, native)", True, (170, 180, 190)),
           (pad + chip * 2 + pad * 2 + 10, cy + chip // 2))
y = cy + truth_panel_h - 10

# Row 3: filmstrip — watch the crown bloom on the down-stroke (f0).
caption(pad, y, "4-frame flap cycle  —  frames 0 1 2 3 (natural size)", sheet_w - pad * 2)
fy = y + label_h
fx = pad
for i, f in enumerate(strip):
    cell = pygame.Surface((fw + 6, fh + 6))
    cell.fill((16, 17, 22))
    cell.blit(f, f.get_rect(center=((fw + 6) // 2, (fh + 6) // 2)))
    sheet.blit(cell, (fx, fy))
    sheet.blit(small.render(f"f{i}", True, (200, 210, 220)), (fx + 4, fy + 2))
    fx += fw + 12

pygame.image.save(sheet, OUT)
print("saved", OUT, sheet.get_size())
