"""Compose the v4 design_2 (BOLD CARTOON BONE + CLOAK) round_4 review sheet.

Round_4 addresses the art-director's ITERATE note: the cloak FAILED the NIGHT
read (dark-on-dark on navy). The fix lifts the cloak CLOTH to a desaturated
cool grey-violet so the cowl + drape read as a distinct mid-dark mass against
the night sky while staying clearly darker than the white bones.

Shows Pip mid-flight over a real DAY gameplay scene and a NIGHT scene, plus a
40px NEAREST truth read on BOTH skies — the acceptance check for whether the
cloaked back mass (hood + drape + hem) reads as a cloak at thumbnail size on
navy while the skull + dominant beak + ribcage stay the hero.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import (get_sky_surface_biome, draw_mountains, draw_ground,
                       draw_cloud)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools import ninja_render as NR
from tools.skeleton_candidates.v4_design_2 import build

OUT = "docs/store_redesign/costume/skeleton/v4/design_2/round_4.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

font = pygame.font.SysFont("Arial", 16, bold=True)
small = pygame.font.SysFont("Arial", 13)


def label(surf, text, x, y, color=(235, 240, 250)):
    surf.blit(small.render(text, True, color), (x, y))


def night_gameplay_panel(source, w, h):
    """Same scene as ninja_render.gameplay_panel but on the night biome phase so
    the cloak cloth is judged against navy, not only bright day sky."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.5)            # deep-night phase
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = source(2, 10.0)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


# ── panels ───────────────────────────────────────────────────────────────────
hero = NR.hero_panel(build, 360, bg=(16, 18, 30))
day = NR.gameplay_panel(build, 220, 392)
night = night_gameplay_panel(build, 220, 392)

# 40px TRUTH READ — scale build(2,10) to 40px wide (NEAREST), upscale x5.
truth_src = build(2, 10.0)
tw, th = truth_src.get_size()
h40 = max(1, int(40 * th / tw))
truth40 = pygame.transform.scale(truth_src, (40, h40))     # nearest downscale
truth_big = pygame.transform.scale(truth40, (200, h40 * 5))


# ── compose ──────────────────────────────────────────────────────────────────
W, H = 980, 720
sheet = pygame.Surface((W, H))
sheet.fill((10, 11, 18))
sheet.blit(font.render(
    "v4 SKELETON · design_2 R4 — BOLD CARTOON BONE + HOODED CLOAK (night-lift)",
    True, (250, 252, 255)), (16, 12))

# Hero (left).
sheet.blit(hero, (16, 44))
label(sheet, "HERO — cloaked skeleton (hood + open-front ribcage + beak)", 16, 410)

# Day gameplay.
sheet.blit(day, (400, 44))
label(sheet, "DAY gameplay (over biome)", 400, 440)

# Night gameplay.
sheet.blit(night, (632, 44))
label(sheet, "NIGHT gameplay (navy phase) — cloth lifted to read on navy", 632, 440)

# 40px truth reads, both skies.
ty = 470
day_bg = pygame.Surface((216, h40 * 5 + 16)); day_bg.fill((120, 175, 210))
day_bg.blit(truth_big, (8, 8))
sheet.blit(day_bg, (16, ty))
label(sheet, "40px TRUTH READ on day sky (x5, nearest)", 16, ty + h40 * 5 + 20)

night_bg = pygame.Surface((216, h40 * 5 + 16)); night_bg.fill((20, 22, 40))
night_bg.blit(truth_big, (8, 8))
sheet.blit(night_bg, (400, ty))
label(sheet, "40px TRUTH READ on NIGHT navy (x5, nearest) — cloak must read",
      400, ty + h40 * 5 + 20)

pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
