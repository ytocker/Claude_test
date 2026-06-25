"""Render the design_3 (JESTER CAP) review sheet — round 2 (SCRATCH ONLY).

Judged on-bird at 40px FIRST: gameplay DAY + gameplay NIGHT strips, then hero,
store icon, and a hard 40px NEAREST truth read. The two horns + two bells must
read against day AND night sky at the worn size.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game import biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud,
)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import gameplay_panel, hero_panel
from tools.partyhat_candidates import design_3 as d

FONT = pygame.font.SysFont("sans", 16, bold=True)
SMALL = pygame.font.SysFont("sans", 13)


def label(surf, text, x, y, col=(235, 232, 245)):
    surf.blit(SMALL.render(text, True, col), (x, y))


def gameplay_panel_phase(source, w, h, phase, frame_idx=2, tilt=10.0):
    """Same composite as tools.ninja_render.gameplay_panel but at an arbitrary
    biome phase so we can show the worn read against night sky."""
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
    frame = source(frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def checker_bg(box):
    bg = pygame.Surface((box, box))
    a, b = (210, 210, 216), (188, 188, 196)
    s = 8
    for j in range(0, box, s):
        for i in range(0, box, s):
            bg.fill(a if (i // s + j // s) % 2 == 0 else b, (i, j, s, s))
    return bg


def truth_chip(source, bg_col, box=200):
    """Hard 40px worn read on a flat sky colour: shrink an in-game frame to 40px
    longest side, blow it back up 4x, plus the actual 40px chip 1:1."""
    frame = source(2, 10.0)
    bb = frame.get_bounding_rect()
    fr = frame.subsurface(bb).copy() if bb.width else frame
    sw, sh = fr.get_size()
    sc = 40 / max(sw, sh)
    small = pygame.transform.smoothscale(fr, (max(1, int(sw * sc)), max(1, int(sh * sc))))
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    panel.fill(bg_col)
    up = pygame.transform.scale(small, (small.get_width() * 4, small.get_height() * 4))
    panel.blit(up, up.get_rect(center=(box // 2, box // 2)))
    panel.blit(small, (8, 8))
    return panel


# Panels.
GP_W, GP_H = 230, 330
gp_day = gameplay_panel(d.build, GP_W, GP_H)
gp_night = gameplay_panel_phase(d.build, GP_W, GP_H, 0.64375)

HERO = 300
hero = hero_panel(d.build, HERO)

# Truth reads on flat day-sky and night-sky colours (mid-sky tones).
truth_day = truth_chip(d.build, (90, 170, 230))
truth_night = truth_chip(d.build, (15, 25, 70))

# Store icon.
icon = d.icon
ib = icon.get_bounding_rect()
icon_c = icon.subsurface(ib).copy() if ib.width else icon
ibox_w, ibox_h = 240, 200
icon_panel = pygame.Surface((ibox_w, ibox_h), pygame.SRCALPHA)
pygame.draw.rect(icon_panel, (28, 26, 40), icon_panel.get_rect(), border_radius=12)
isc = min((ibox_w * 0.84) / icon_c.get_width(), (ibox_h * 0.84) / icon_c.get_height())
icon_s = pygame.transform.smoothscale(
    icon_c, (int(icon_c.get_width() * isc), int(icon_c.get_height() * isc)))
icon_panel.blit(icon_s, icon_s.get_rect(center=(ibox_w // 2, ibox_h // 2)))

# Compose sheet.
PAD = 18
title_h = 40
row1_h = GP_H
truth_box = 200
sheet_w = PAD * 5 + GP_W * 2 + HERO
sheet_h = title_h + PAD * 4 + row1_h + max(truth_box, ibox_h)
sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
sheet.fill((24, 22, 34))

sheet.blit(FONT.render("PARTY HAT redesign — DESIGN 3: JESTER CAP  (round 2)",
                       True, (255, 233, 120)), (PAD, 12))

# Row 1: gameplay DAY, gameplay NIGHT, hero.
x = PAD
y = title_h + PAD
sheet.blit(gp_day, (x, y))
label(sheet, "gameplay DAY (40px-class worn read)", x, y + GP_H + 2)

x2 = PAD * 2 + GP_W
sheet.blit(gp_night, (x2, y))
label(sheet, "gameplay NIGHT (worn read)", x2, y + GP_H + 2)

x3 = PAD * 3 + GP_W * 2
sheet.blit(hero, (x3, y))
label(sheet, "hero product shot", x3, y + HERO + 2)

# Row 2: truth-day, truth-night, store icon.
ry = y + GP_H + 26
sheet.blit(truth_day, (x, ry))
label(sheet, "40px truth read — DAY sky", x, ry + truth_box + 2)

sheet.blit(truth_night, (x2, ry))
label(sheet, "40px truth read — NIGHT sky", x2, ry + truth_box + 2)

sheet.blit(icon_panel, (x3, ry))
label(sheet, "store icon (full harlequin)", x3, ry + ibox_h + 2)

out = "docs/store_redesign/hats/partyhat/design_3/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("WROTE", out, sheet.get_size())
