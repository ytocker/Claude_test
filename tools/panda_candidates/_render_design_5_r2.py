"""Render the round_2 review sheet for CELESTIAL PANDA design_5.

Night panel renders at the TRUE-dark biome phase (~0.64) — phase 1.0 in the
cycle wraps back to bright day, so the darkest sky (where the cosmic palette is
meant to be judged) is at the night keyframe, not at 1.0.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import importlib.util
import pygame
pygame.init()

spec = importlib.util.spec_from_file_location(
    "panda_design_5", "/home/user/skybit/tools/panda_candidates/design_5.py")
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

NIGHT_PHASE = 0.64     # darkest sky in the biome cycle (true night)

sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill((28, 26, 36))

font = pygame.font.SysFont("Arial", 16, bold=True)
small = pygame.font.SysFont("Arial", 12)


def label(text, x, y, col=(235, 235, 240)):
    sheet.blit(font.render(text, True, col), (x, y))


def _night_gameplay_panel(w, h):
    """A true-dark night-biome variant of ninja_render.gameplay_panel. The crop
    is lifted to sit the bird against the dark UPPER sky (~RGB 10,18,53) and
    exclude the lit horizon band at the bottom — the cosmic palette is meant to
    be judged on a genuinely dark background, not the dusk-blue glow."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(NIGHT_PHASE)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=210, gap_h=185).draw(scene, palette)
    Pipe(x=210, gap_y=260, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 210
    frame = _frame(source, 2, -5.0)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.62)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 24)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


label("CELESTIAL PANDA  ·  design_5  ·  round_2  (legendary)", PAD, 8)

cols = [
    ("day gameplay", gameplay_panel(source, PANEL_W, PANEL_H)),
    ("TRUE night gameplay (phase 0.64)", _night_gameplay_panel(PANEL_W, PANEL_H)),
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
label("40px NEAREST truth read — 4 wing frames", PAD, ty - 4)
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
    # Two backdrops per frame — blue day sky + dark night sky — so the halo
    # float and the body rim-light are judged against both contexts at 40px.
    cell = pygame.Surface((64, 56), pygame.SRCALPHA)
    pygame.draw.rect(cell, (70, 150, 215), pygame.Rect(0, 0, 32, 56), border_radius=6)
    pygame.draw.rect(cell, (8, 10, 30), pygame.Rect(32, 0, 32, 56), border_radius=6)
    cell.blit(small_frame, small_frame.get_rect(center=(32, 28)))
    sheet.blit(cell, (fx, ty + 14))
    sheet.blit(small.render(f"f{fi}", True, (220, 220, 230)), (fx + 4, ty + 14))
    fx += 74

out_dir = "/home/user/skybit/docs/store_redesign/animal/panda/design_5"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path)
