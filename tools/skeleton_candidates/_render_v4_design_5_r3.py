"""Compose the v4 design_5 (ETCHED WOODCUT · CLOAK) round_3 review sheet (scratch).

round_3 folds in the user note "make the black BACK part of the parrot be like a
cloak": the dark body+tail mass is now a hooded open-front cloak (shared cloak
base) struck in the woodcut idiom — etched diagonal fold hatching across the
drape, a crisp engraved keyline on the hood rim + tattered hem. The sheet shows
Pip mid-flight in a real biome scene DAY *and* NIGHT (so the cloak reads as cloth
on both skies) plus a 40px NEAREST truth read (the hood + hatched drape must
still clock as a cloak, skull + beak the hero, ribcage in the open front).
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud,
)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

from tools import ninja_render as NR
from tools.skeleton_candidates.v4_design_5 import build

OUT = "docs/store_redesign/costume/skeleton/v4/design_5/round_3.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

font = pygame.font.SysFont("dejavusans", 16, bold=True)
small = pygame.font.SysFont("dejavusans", 13)

FRAME_IDX = 2
TILT = 10.0


def label(surf, text, x, y, col=(230, 232, 240)):
    surf.blit(small.render(text, True, (8, 8, 12)), (x + 1, y + 1))
    surf.blit(small.render(text, True, col), (x, y))


def gameplay_panel(w, h, phase):
    """Pip mid-flight over a real biome scene at a given day-cycle phase, so the
    night panel renders under a dark sky and the cloak reads on both skies."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    bucket = int(round(phase * 64))
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, bucket), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = build(FRAME_IDX, TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop_w = min(crop_w, GW)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def truth40():
    """Mid-flight frame at 40px wide (nearest), upscaled x5 — the honest read."""
    src = build(FRAME_IDX, TILT)
    bb = src.get_bounding_rect()
    src = src.subsurface(bb).copy() if bb.width else src
    sw, sh = src.get_size()
    t40 = pygame.transform.scale(src, (40, max(1, int(40 * sh / sw))))
    tw, th = t40.get_size()
    return pygame.transform.scale(t40, (tw * 5, th * 5))


# ── panels ────────────────────────────────────────────────────────────────────
hero = NR.hero_panel(build, 360, bg=(20, 16, 26))
day = gameplay_panel(220, 392, 0.0)
night = gameplay_panel(220, 392, 0.64375)
truth = truth40()

# ── compose sheet ─────────────────────────────────────────────────────────────
SW, SH = 1100, 540
sheet = pygame.Surface((SW, SH))
sheet.fill((20, 21, 30))   # ink-plate background

sheet.blit(font.render(
    "v4 SKELETON · design_5 — ETCHED WOODCUT · CLOAK (round 3)",
    True, (236, 238, 246)), (16, 12))
label(sheet, "dark back mass now a HOODED OPEN-FRONT CLOAK · etched diagonal fold "
             "hatching + engraved keyline hem/hood · skull + 3px hooked beak still "
             "the hero · open chest shows ribcage/spine", 16, 36)

# Hero (large product shot).
sheet.blit(hero, (16, 64))
label(sheet, "HERO — hatched woodcut cape, x-ray hero through the open front",
      16, 64 + 360 + 4)

# Day gameplay.
sheet.blit(day, (400, 64))
label(sheet, "DAY sky — cloak reads as cloth over clouds", 400, 64 + 392 + 4)

# Night gameplay.
sheet.blit(night, (632, 64))
label(sheet, "NIGHT sky — hood + hem keyline hold", 632, 64 + 392 + 4)

# 40px truth read.
tx = 632 + 230
sheet.blit(truth, (tx, 64))
label(sheet, "40px truth (x5) — cloak + hero", tx, 64 + truth.get_height() + 2)

pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
