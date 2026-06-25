"""Render DESIGN 1 CONFETTI CONE round-2 review sheet.

Tiles: gameplay DAY, gameplay NIGHT, hero product-shot, store icon, and a
40px "truth read" of the in-motion bird (the bar the critique set).
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import gameplay_panel, hero_panel
from tools.partyhat_candidates import design_1


def night_gameplay_panel(source, w, h, frame_idx=2, tilt=10.0):
    """Same composition as ninja_render.gameplay_panel but on the night phase
    palette, to judge the day/night 40px read demanded by the critique."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.5)  # deep night
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


def truth_read(source, bg, label_bg, frame_idx=2, tilt=10.0):
    """The bird scaled so its on-screen footprint is ~40px — the size players
    see in motion. Drawn on a flat sky-ish chip for day and night."""
    chip = 130
    surf = pygame.Surface((chip, chip))
    surf.fill(bg)
    frame = source(frame_idx, tilt)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    target = 40.0
    scale = target / max(sw, sh)
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    # Upscale 2x with nearest so the reviewer sees the actual 40px pixels.
    small = pygame.transform.scale(small, (small.get_width() * 2, small.get_height() * 2))
    surf.blit(small, small.get_rect(center=(chip // 2, chip // 2)))
    return surf


FONT = pygame.font.SysFont("Arial", 16, bold=True)
SMALL = pygame.font.SysFont("Arial", 12)


def labelled(tile, text):
    pad = 24
    w = tile.get_width()
    out = pygame.Surface((w, tile.get_height() + pad), pygame.SRCALPHA)
    out.fill((26, 24, 34))
    out.blit(tile, (0, pad))
    lab = FONT.render(text, True, (240, 240, 248))
    out.blit(lab, (8, 4))
    return out


PANEL_W, PANEL_H = 200, 300
ICON_BOX = 208

day_gp = labelled(gameplay_panel(design_1.build, PANEL_W, PANEL_H), "GAMEPLAY · DAY")
night_gp = labelled(night_gameplay_panel(design_1.build, PANEL_W, PANEL_H), "GAMEPLAY · NIGHT")
hero = labelled(hero_panel(design_1.build, PANEL_H), "HERO")
icon = labelled(design_1.icon, "STORE ICON")

# 40px truth reads, day sky blue + night deep blue
day_chip = labelled(truth_read(design_1.build, (150, 205, 235), None), "40px · DAY")
night_chip = labelled(truth_read(design_1.build, (24, 26, 60), None), "40px · NIGHT")

tiles = [day_gp, night_gp, hero, icon, day_chip, night_chip]
cols = 3
margin = 18
col_w = max(t.get_width() for t in tiles)
row_h = max(t.get_height() for t in tiles)
rows = (len(tiles) + cols - 1) // cols

sheet_w = margin + cols * (col_w + margin)
title_h = 56
sheet_h = title_h + margin + rows * (row_h + margin)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 24))

TITLE = pygame.font.SysFont("Arial", 24, bold=True)
sheet.blit(TITLE.render("DESIGN 1 · CONFETTI CONE — round 2", True, (255, 222, 120)), (margin, 14))
sheet.blit(SMALL.render(
    "ITERATE fixes: dark keyline + indigo shade flank · 40px triad (gold tip+base+magenta) · "
    "2 wider low-freq ribbons · lower seat · flank-aware confetti · centred collar specular",
    True, (180, 180, 195)), (margin, 40))

for i, tile in enumerate(tiles):
    r, c = divmod(i, cols)
    x = margin + c * (col_w + margin)
    y = title_h + margin + r * (row_h + margin)
    sheet.blit(tile, (x, y))

out_dir = "/home/user/skybit/docs/store_redesign/hats/partyhat/design_1"
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "round_2.png")
pygame.image.save(sheet, out)
print("WROTE", out, sheet.get_size())
