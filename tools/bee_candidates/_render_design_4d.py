"""Compose the PAINTED LADY (design_4d) review sheet.

Headless: SDL_VIDEODRIVER=dummy python tools/bee_candidates/_render_design_4d.py
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pygame
pygame.init()

import tools.ninja_render as ninja_render
from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.bee_candidates.design_4d import build

OUT = "docs/store_redesign/animal/bee/design_4d/round_2.png"
TITLE = "DESIGN 4d — PAINTED LADY  R2  (Vanessa cardui: salmon-tawny + cream hindwing + black apex patch)"
NIGHT_PHASE = 0.64375

def _label(surf, text, x, y, size=18, color=(236, 238, 246)):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf.blit(font.render(text, True, color), (x, y))

def _gameplay_panel_phase(source, w, h, phase):
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0, palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = source(ninja_render.FRAME_IDX, ninja_render.TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78); crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))

def _flap_strip(box):
    panel = pygame.Surface((box, box // 4 + 10))
    panel.fill((26, 30, 34))
    cell = box // 4
    for i in range(4):
        frame = build(i, 6.0)
        bb = frame.get_bounding_rect(); frame = frame.subsurface(bb).copy()
        sw, sh = frame.get_size(); scale = (cell * 0.86) / max(sw, sh)
        frame = pygame.transform.smoothscale(frame, (max(1, int(sw*scale)), max(1, int(sh*scale))))
        panel.blit(frame, frame.get_rect(center=(cell//2 + i*cell, (box//4+10)//2)))
    return panel

def _truth_read(box):
    frames = [build(fi, t) for fi, t in ((ninja_render.FRAME_IDX, ninja_render.TILT), (0, -8.0), (3, 22.0))]
    smalls = []
    for frame in frames:
        bb = frame.get_bounding_rect(); frame = frame.subsurface(bb).copy()
        sw, sh = frame.get_size(); scale = 40.0 / max(sw, sh)
        smalls.append(pygame.transform.scale(frame, (max(1,int(sw*scale)), max(1,int(sh*scale)))))
    panel = pygame.Surface((box, box)); half = box // 2
    pygame.draw.rect(panel, (150, 200, 235), (0, 0, half, box))
    pygame.draw.rect(panel, (16, 18, 34), (half, 0, box-half, box))
    for row, small in enumerate(smalls):
        tile = pygame.Surface((48,48), pygame.SRCALPHA)
        tile.blit(small, small.get_rect(center=(24,24)))
        big = pygame.transform.scale(tile, (144,144))
        ry = 20 + row*(box-30)//3
        for cx in (half//2, half+half//2):
            panel.blit(big, big.get_rect(center=(cx, ry+60)))
    return panel

def main():
    box = 320; gw = int(box*9/16); pad = 18; head = 54
    hero = ninja_render.hero_panel(build, box)
    day = _gameplay_panel_phase(build, gw, box, 0.0)
    night = _gameplay_panel_phase(build, gw, box, NIGHT_PHASE)
    truth = _truth_read(box); strip = _flap_strip(box)
    panels = (hero, day, night, truth)
    captions = ("HERO PRODUCT SHOT", "IN-GAMEPLAY (day)", "IN-GAMEPLAY (night)", "40px TRUTH READ")
    W = pad*(len(panels)+1) + sum(p.get_width() for p in panels)
    H = head + box + 28 + strip.get_height() + 40 + pad
    sheet = pygame.Surface((W, H)); sheet.fill((18, 17, 26))
    _label(sheet, TITLE, pad, 16, size=20)
    x = pad
    for panel, cap in zip(panels, captions):
        sheet.blit(panel, (x, head))
        _label(sheet, cap, x, head+box+4, size=13, color=(190,194,210))
        x += panel.get_width() + pad
    sy = head + box + 28
    _label(sheet, "FLAP STRIP  (frames 0-3)", pad, sy-2, size=13, color=(190,194,210))
    sheet.blit(strip, (pad, sy+18))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())

if __name__ == "__main__":
    main()
