"""Render the round_3 review sheet for KUNG-FU PANDA design_4."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import importlib.util
import pygame
pygame.init()

spec = importlib.util.spec_from_file_location(
    "panda_design_4", "/home/user/skybit/tools/panda_candidates/design_4.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

from tools.ninja_render import gameplay_panel, hero_panel, _frame
from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

source = mod.get_skin

SHEET_W, SHEET_H = 880, 470
PANEL_W, PANEL_H = 240, 340
HERO_BOX = 240
PAD = 18
TOP = 34

sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill((28, 26, 36))

font = pygame.font.SysFont("Arial", 16, bold=True)
small = pygame.font.SysFont("Arial", 12)


def label(text, x, y, col=(235, 235, 240)):
    sheet.blit(font.render(text, True, col), (x, y))


def _night_gameplay_panel(w, h):
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.5)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = _frame(source, 2, -5.0)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


label("KUNG-FU PANDA  ·  design_4  ·  round_3", PAD, 8)

cols = [
    ("day gameplay", gameplay_panel(source, PANEL_W, PANEL_H)),
    ("night gameplay", _night_gameplay_panel(PANEL_W, PANEL_H)),
    ("hero", hero_panel(source, HERO_BOX)),
]
x = PAD
for name, panel in cols:
    bx = x + (PANEL_W - panel.get_width()) // 2
    by = TOP + (PANEL_H - panel.get_height()) // 2
    sheet.blit(panel, (bx, by))
    label(name, x, TOP + PANEL_H + 4, (200, 200, 210))
    x += PANEL_W + PAD

ty = TOP + PANEL_H + 30
label("40px NEAREST truth read — 4 wing frames (ribbon must persist)", PAD, ty - 4)
fx = PAD
for fi in range(4):
    frame = source(fi, 0.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    fw, fh = frame.get_size()
    scale = 40 / fh
    small_frame = pygame.transform.scale(
        frame, (max(1, int(fw * scale)), 40))
    cell = pygame.Surface((64, 56), pygame.SRCALPHA)
    pygame.draw.rect(cell, (54, 52, 64), cell.get_rect(), border_radius=6)
    cell.blit(small_frame, small_frame.get_rect(center=(32, 28)))
    sheet.blit(cell, (fx, ty + 14))
    sheet.blit(small.render(f"f{fi}", True, (180, 180, 190)), (fx + 4, ty + 14))
    fx += 74

out_dir = "/home/user/skybit/docs/store_redesign/animal/panda/design_4"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "round_3.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path)
