"""Compose the v4 design_4 (IVORY ANATOMICAL) round_2 review sheet (scratch)."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render as NR
from tools.skeleton_candidates.v4_design_4 import build

OUT = "docs/store_redesign/costume/skeleton/v4/design_4/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

font = pygame.font.SysFont("dejavusans", 16, bold=True)
small = pygame.font.SysFont("dejavusans", 13)


def label(surf, text, x, y, col=(245, 240, 225)):
    surf.blit(small.render(text, True, (10, 10, 14)), (x + 1, y + 1))
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
sheet.fill((30, 26, 22))   # warm museum-plate background

sheet.blit(font.render("v4 SKELETON · design_4 — IVORY ANATOMICAL",
                       True, (244, 234, 206)), (16, 12))
label(sheet, "R2 · longer/fatter/brightest HERO beak · calm skull anchor · 3-rib cage "
             "over recessed keel · lit-side dark rim · warmer aged-specimen body", 16, 36)

# Hero (large product shot).
sheet.blit(hero, (16, 64))
label(sheet, "HERO — judge anatomical detail", 16, 64 + 360 + 4)

# Day gameplay.
sheet.blit(day, (400, 64))
label(sheet, "DAY gameplay", 400, 64 + 392 + 4)

# Night + truth-read column.
sheet.blit(night, (630, 64))
label(sheet, "NIGHT navy fill", 630, 64 + 240 + 4)

sheet.blit(truth, (630, 330))
label(sheet, "40px TRUTH READ (x5)", 630, 330 + truth.get_height() + 4)

pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
