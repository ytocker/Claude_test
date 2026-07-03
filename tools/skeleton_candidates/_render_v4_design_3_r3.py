"""Compose the v4 design_3 (NEON / BIOLUMINESCENT · cloaked) round_3 sheet.

Cloak round: the dark back mass is now a hooded open-front cloak. Show it in a
real gameplay scene DAY + NIGHT (so the neon-lit-cloth read is judged on both),
a hero product shot, and a 40px NEAREST truth read on both skies.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

from tools import ninja_render as NR
from tools.skeleton_candidates.v4_design_3 import build

OUT = "docs/store_redesign/costume/skeleton/v4/design_3/round_3.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

font = pygame.font.SysFont("Arial", 16, bold=True)
small = pygame.font.SysFont("Arial", 13)


def label(surf, text, x, y, color=(235, 255, 245)):
    surf.blit(small.render(text, True, color), (x, y))


def gameplay_panel_phase(source, w, h, phase):
    """ninja_render.gameplay_panel, but at an arbitrary biome phase so the same
    cloaked Pip can be judged against the night sky too."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = source(NR.FRAME_IDX, NR.TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


# ── panels ───────────────────────────────────────────────────────────────────
hero = NR.hero_panel(build, 360, bg=(16, 18, 30))
day = gameplay_panel_phase(build, 220, 392, 0.0)          # bright day biome
night = gameplay_panel_phase(build, 220, 392, 0.64375)    # full-night biome

# 40px TRUTH READ — scale build(2,10) to 40px wide (nearest), upscale x5.
truth_src = build(2, 10.0)
tw, th = truth_src.get_size()
h40 = max(1, int(40 * th / tw))
truth40 = pygame.transform.scale(truth_src, (40, h40))
truth_up = pygame.transform.scale(truth40, (200, h40 * 5))


# ── compose ──────────────────────────────────────────────────────────────────
W, H = 760, 760
sheet = pygame.Surface((W, H))
sheet.fill((10, 11, 18))
sheet.blit(font.render("v4 SKELETON · design_3 R3 — NEON / BIOLUMINESCENT (cloaked)",
                       True, (150, 255, 220)), (16, 12))

# Hero (left).
sheet.blit(hero, (16, 44))
label(sheet, "HERO — glowing neon x-ray under a hooded cloak", 16, 410)

# Day gameplay.
sheet.blit(day, (400, 44))
label(sheet, "DAY gameplay (cloak reads as dark lit cloth)", 400, 440)

# Night gameplay.
sheet.blit(night, (632, 44))
label(sheet, "NIGHT gameplay (neon sings)", 632, 440)

# 40px truth reads.
ty = 470
day_bg = pygame.Surface((216, h40 * 5 + 16)); day_bg.fill((120, 175, 210))
day_bg.blit(truth_up, (8, 8))
sheet.blit(day_bg, (16, ty))
label(sheet, "40px TRUTH READ on day sky (x5 nearest)", 16, ty + h40 * 5 + 20)

night_bg = pygame.Surface((216, h40 * 5 + 16)); night_bg.fill((18, 20, 34))
night_bg.blit(truth_up, (8, 8))
sheet.blit(night_bg, (400, ty))
label(sheet, "40px TRUTH READ on night sky (x5 nearest)", 400, ty + h40 * 5 + 20)

pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
