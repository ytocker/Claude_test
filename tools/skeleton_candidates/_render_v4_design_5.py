"""Compose the v4 design_5 (ETCHED WOODCUT) round_1 review sheet (scratch)."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render as NR
from tools.skeleton_candidates.v4_design_5 import build

OUT = "docs/store_redesign/costume/skeleton/v4/design_5/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

font = pygame.font.SysFont("dejavusans", 16, bold=True)
small = pygame.font.SysFont("dejavusans", 13)


def label(surf, text, x, y, col=(230, 232, 240)):
    surf.blit(small.render(text, True, (8, 8, 12)), (x + 1, y + 1))
    surf.blit(small.render(text, True, col), (x, y))


# Panels.
hero = NR.hero_panel(build, 360)
day = NR.gameplay_panel(build, 220, 392)

# NIGHT: bird on a dark navy fill.
night = pygame.Surface((220, 240), pygame.SRCALPHA)
night.fill((18, 20, 34))
nf = build(2, 10.0)
night.blit(nf, nf.get_rect(center=(110, 120)))

# 40px TRUTH READ: scale to 40 wide (nearest), upscale x5.
src = build(2, 10.0)
bb = src.get_bounding_rect()
src = src.subsurface(bb).copy() if bb.width else src
sw, sh = src.get_size()
t40 = pygame.transform.scale(src, (40, max(1, int(40 * sh / sw))))
t40w, t40h = t40.get_size()
truth = pygame.transform.scale(t40, (t40w * 5, t40h * 5))   # nearest-neighbour upscale

# ── compose sheet ────────────────────────────────────────────────────────────
SW, SH = 870, 540
sheet = pygame.Surface((SW, SH))
sheet.fill((20, 21, 30))   # ink-plate background

sheet.blit(font.render("v4 SKELETON · design_5 — ETCHED WOODCUT",
                       True, (236, 238, 246)), (16, 12))
label(sheet, "vintage engraving plate of the original Pip · white line-art bones + "
             "parallel hatching tone · doubled-contour hooked beak-bone hero", 16, 36)

# Hero (large product shot).
sheet.blit(hero, (16, 64))
label(sheet, "HERO — judge engraving / hatching texture", 16, 64 + 360 + 4)

# Day gameplay.
sheet.blit(day, (400, 64))
label(sheet, "DAY gameplay", 400, 64 + 392 + 4)

# Night + truth-read column.
sheet.blit(night, (630, 64))
label(sheet, "NIGHT navy fill", 630, 64 + 240 + 4)

sheet.blit(truth, (630, 330))
label(sheet, "40px TRUTH READ (x5) — bone outlines legible", 630, 330 + truth.get_height() + 4)

pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
