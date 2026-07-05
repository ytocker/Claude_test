"""Compose the v4 design_3 (NEON / BIOLUMINESCENT) round_1 review sheet."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render as NR
from tools.skeleton_candidates.v4_design_3 import build

OUT = "docs/store_redesign/costume/skeleton/v4/design_3/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

font = pygame.font.SysFont("Arial", 16, bold=True)
small = pygame.font.SysFont("Arial", 13)


def label(surf, text, x, y, color=(235, 255, 245)):
    surf.blit(small.render(text, True, color), (x, y))


# ── panels ───────────────────────────────────────────────────────────────────
hero = NR.hero_panel(build, 360, bg=(16, 18, 30))
day = NR.gameplay_panel(build, 220, 392)

# NIGHT check — neon over dark navy.
night = pygame.Surface((220, 392))
night.fill((18, 20, 34))
nf = build(2, 10.0)
night.blit(nf, nf.get_rect(center=(110, 196)))

# 40px TRUTH READ — scale build(2,10) to 40px wide (nearest), upscale ×5.
truth_src = build(2, 10.0)
tw, th = truth_src.get_size()
h40 = max(1, int(40 * th / tw))
truth40 = pygame.transform.scale(truth_src, (40, h40))
truth_day = pygame.transform.scale(truth40, (200, h40 * 5))
truth_night = truth_day.copy()


# ── compose ──────────────────────────────────────────────────────────────────
W, H = 760, 720
sheet = pygame.Surface((W, H))
sheet.fill((10, 11, 18))
sheet.blit(font.render("v4 SKELETON · design_3 R2 — NEON / BIOLUMINESCENT", True,
                       (150, 255, 220)), (16, 12))

# Hero (left).
sheet.blit(hero, (16, 44))
label(sheet, "HERO — product shot (glowing neon x-ray)", 16, 410)

# Day gameplay.
sheet.blit(day, (400, 44))
label(sheet, "DAY gameplay (over biome)", 400, 440)

# Night check.
sheet.blit(night, (632, 44))
label(sheet, "NIGHT (dark navy)", 632, 440)

# 40px truth read.
ty = 470
day_bg = pygame.Surface((216, h40 * 5 + 16)); day_bg.fill((120, 175, 210))
day_bg.blit(truth_day, (8, 8))
sheet.blit(day_bg, (16, ty))
label(sheet, "40px TRUTH READ on day sky (x5)", 16, ty + h40 * 5 + 20)

night_bg = pygame.Surface((216, h40 * 5 + 16)); night_bg.fill((18, 20, 34))
night_bg.blit(truth_night, (8, 8))
sheet.blit(night_bg, (400, ty))
label(sheet, "40px TRUTH READ on night sky (x5)", 400, ty + h40 * 5 + 20)

pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
