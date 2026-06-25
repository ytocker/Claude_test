"""Render the v4 design_1 RADIOGRAPH round_3 review sheet (scratch only).

R3 swaps the dark back mass for a hooded open-front cloak; this sheet proves the
cloak reads day AND night while the skull/beak/ribcage stay the radiograph hero.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render as NR
from tools.skeleton_candidates.v4_design_1 import build

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

OUT = "docs/store_redesign/costume/skeleton/v4/design_1/round_3.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

font = pygame.font.SysFont("dejavusans", 16, bold=True)
small = pygame.font.SysFont("dejavusans", 13)


def label(surf, text, x, y, col=(235, 240, 250)):
    surf.blit(font.render(text, True, col), (x, y))


def gameplay_at_phase(source, w, h, phase):
    """Same crop/compose as ninja_render.gameplay_panel but at an arbitrary
    biome phase, so we can show a true night scene."""
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
    frame = NR._frame(source, 2, 10.0)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


# Panels: hero, day gameplay, night gameplay.
hero = NR.hero_panel(build, 300)
day = gameplay_at_phase(build, 240, 392, 0.0)
night = gameplay_at_phase(build, 240, 392, 0.6)


def truth_read(phase_bg):
    """40px NEAREST downscale, upscaled x5 on a flat bg — the legibility truth."""
    src = build(2, 10.0)
    sw, sh = src.get_size()
    tw = 40
    th = max(1, int(sh * tw / sw))
    small40 = pygame.transform.scale(src, (tw, th))
    big = pygame.transform.scale(small40, (tw * 5, th * 5))
    pad = pygame.Surface((tw * 5 + 20, th * 5 + 20))
    pad.fill(phase_bg)
    pad.blit(big, (10, 10))
    return pad


truth_day = truth_read((120, 165, 215))
truth_night = truth_read((16, 18, 34))

# Compose sheet.
PAD = 18
TITLE_H = 42
LBL = 24
top_h = max(hero.get_height(), day.get_height(), night.get_height())
bot_h = max(truth_day.get_height(), truth_night.get_height())

sheet_w = PAD * 4 + hero.get_width() + day.get_width() + night.get_width()
sheet_h = TITLE_H + LBL + top_h + PAD + LBL + bot_h + PAD * 2

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((24, 26, 36))

label(sheet, "v4 SKELETON · design_1 · RADIOGRAPH · R3 — dark back mass now a HOODED OPEN-FRONT CLOAK",
      PAD, 12, (170, 200, 255))

y = TITLE_H + LBL
x = PAD
sheet.blit(hero, (x, y))
label(sheet, "HERO — product shot", x, y - LBL)
x += hero.get_width() + PAD
sheet.blit(day, (x, y))
label(sheet, "GAMEPLAY — DAY", x, y - LBL)
x += day.get_width() + PAD
sheet.blit(night, (x, y))
label(sheet, "GAMEPLAY — NIGHT", x, y - LBL)

y2 = y + top_h + PAD + LBL
x = PAD
sheet.blit(truth_day, (x, y2))
label(sheet, "40px TRUTH (x5) — day bg", x, y2 - LBL)
x += truth_day.get_width() + PAD
sheet.blit(truth_night, (x, y2))
label(sheet, "40px TRUTH (x5) — night bg", x, y2 - LBL)

pygame.image.save(sheet, OUT)
print("saved", OUT, sheet.get_size())
