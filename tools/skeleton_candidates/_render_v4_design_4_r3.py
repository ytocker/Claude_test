"""Compose the v4 design_4 (IVORY ANATOMICAL · cloak) round_3 sheet (scratch).

R3 brief: the dark back mass is now a hooded open-front CLOAK over the ivory
skeleton, with a bone-cord throat clasp; skull + dominant beak still peer out of
the hood and the open front shows ribcage + spine. Judged DAY + NIGHT in real
gameplay scenes plus a 40px nearest truth read.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render as NR
from tools.skeleton_candidates.v4_design_4 import build
from game import biome
from game.draw import get_sky_surface_biome, draw_ground, draw_mountains, draw_cloud
from game.entities import Pipe


def gameplay_panel_phase(source, w, h, phase):
    """Same crop/scene as NR.gameplay_panel but at an arbitrary biome phase so a
    genuine NIGHT scene (not a flat navy fill) judges the cloak after dark."""
    GW, GH, GROUND_Y = NR.GW, NR.GH, NR.GROUND_Y
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
    frame = NR._frame(source, NR.FRAME_IDX, NR.TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


OUT = "docs/store_redesign/costume/skeleton/v4/design_4/round_3.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

font = pygame.font.SysFont("dejavusans", 16, bold=True)
small = pygame.font.SysFont("dejavusans", 13)


def label(surf, text, x, y, col=(245, 240, 225)):
    surf.blit(small.render(text, True, (10, 10, 14)), (x + 1, y + 1))
    surf.blit(small.render(text, True, col), (x, y))


# Panels.
hero = NR.hero_panel(build, 360)
day = gameplay_panel_phase(build, 220, 392, 0.0)
night = gameplay_panel_phase(build, 220, 392, 0.6)


def truth_read(scale=40, up=6):
    src = build(2, 10.0)
    bb = src.get_bounding_rect()
    src = src.subsurface(bb).copy() if bb.width else src
    sw, sh = src.get_size()
    t = pygame.transform.scale(src, (scale, max(1, int(scale * sh / sw))))
    tw, th = t.get_size()
    return pygame.transform.scale(t, (tw * up, th * up))   # nearest upscale


truth = truth_read()

# ── compose sheet ────────────────────────────────────────────────────────────
SW, SH = 900, 580
sheet = pygame.Surface((SW, SH))
sheet.fill((30, 26, 22))   # warm museum-plate background

sheet.blit(font.render("v4 SKELETON · design_4 — IVORY ANATOMICAL · CLOAK",
                       True, (244, 234, 206)), (16, 12))
label(sheet, "R3 · dark back mass redrawn as a hooded open-front aged-brown cloak · "
             "bone-cord throat clasp · skull + HERO beak peer from the hood · ribcage + "
             "spine show through the open front", 16, 36)

# Hero (large product shot).
sheet.blit(hero, (16, 64))
label(sheet, "HERO — cloak hood + clasp + ivory bones", 16, 64 + 360 + 4)

# Day + night gameplay.
sheet.blit(day, (392, 64))
label(sheet, "DAY gameplay", 392, 64 + 392 + 4)

sheet.blit(night, (624, 64))
label(sheet, "NIGHT gameplay (phase 0.6)", 624, 64 + 392 + 4)

# Truth read under the hero panel (left column) — the at-scale legibility check.
ty = 64 + 360 + 24
sheet.blit(truth, (16, ty))
label(sheet, "40px TRUTH READ (x6) — cloak + skull/beak hero at scale",
      16 + truth.get_width() + 10, ty + truth.get_height() // 2 - 6)

pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
