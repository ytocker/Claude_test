"""Round review-sheet renderer for the 5 pufferfish candidates.

For each design: a 4-frame flap filmstrip (the inflate gag), a day gameplay
panel, a night gameplay panel, a clean hero shot, and a 40px NEAREST truth read
— one labeled sheet under docs/store_redesign/animal/sun/.

Run: ``PYTHONPATH=. SDL_VIDEODRIVER=dummy python tools/sun_candidates/_render_all.py [round_tag]``
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib
import sys
import pygame
pygame.init()

ROUND = sys.argv[1] if len(sys.argv) > 1 else "round_1"

import tools.ninja_render as nr
from game import biome
from game.draw import (get_sky_surface_biome, draw_mountains, draw_ground,
                       draw_cloud)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

DESIGNS = [
    ("design_1", "CLASSIC SUNFACE"),
    ("design_2", "BLAZING"),
    ("design_3", "SYNTHWAVE"),
    ("design_4", "KAWAII"),
    ("design_5", "SOLAR DEITY"),
]

OUT_DIR = "docs/store_redesign/animal/sun"


def _night_gameplay_panel(source, w, h, *, frame_idx=2, tilt=10.0):
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.64)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = nr._frame(source, frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _filmstrip(build, cell=80):
    strip = pygame.Surface((cell * 4, cell), pygame.SRCALPHA)
    strip.fill((26, 24, 36))
    for i in range(4):
        fr = build(i, 6.0)
        bb = fr.get_bounding_rect()
        if bb.width and bb.height:
            fr = fr.subsurface(bb).copy()
        sw, sh = fr.get_size()
        sc = (cell * 0.82) / max(sw, sh)
        fr = pygame.transform.smoothscale(
            fr, (max(1, int(sw * sc)), max(1, int(sh * sc))))
        strip.blit(fr, fr.get_rect(center=(i * cell + cell // 2, cell // 2)))
        pygame.draw.rect(strip, (60, 56, 74), (i * cell, 0, cell, cell), 1)
    return strip


def _truth_read(build):
    panel = pygame.Surface((120, 120), pygame.SRCALPHA)
    panel.fill((26, 24, 36))
    fr = build(2, 10.0)
    bb = fr.get_bounding_rect()
    if bb.width and bb.height:
        fr = fr.subsurface(bb).copy()
    sw, sh = fr.get_size()
    sc = 40 / max(sw, sh)
    small = pygame.transform.scale(
        fr, (max(1, int(sw * sc)), max(1, int(sh * sc))))
    panel.blit(small, small.get_rect(center=(34, 60)))
    big = pygame.transform.scale(small,
                                 (small.get_width() * 2, small.get_height() * 2))
    panel.blit(big, big.get_rect(center=(84, 60)))
    return panel


def _label(surf, text, x, y, size=22, color=(240, 236, 250)):
    font = pygame.font.SysFont("dejavusans", size, bold=True)
    surf.blit(font.render(text, True, (10, 8, 16)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def render_design(slug, name):
    build = importlib.import_module(
        f"tools.sun_candidates.{slug}").build
    film = _filmstrip(build)
    day = nr.gameplay_panel(build, 300, 440)
    night = _night_gameplay_panel(build, 300, 440)
    hero = nr.hero_panel(build, 240)
    truth = _truth_read(build)

    pad = 24
    sheet_w = pad + 300 + pad + 300 + pad + 240 + pad
    sheet_h = 60 + 440 + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 26))
    _label(sheet, f"SUN  ·  {name}  ·  {ROUND.replace('_', ' ')}",
           pad, 16, size=26)

    y0 = 56
    sheet.blit(day, (pad, y0))
    _label(sheet, "DAY", pad + 4, y0 + 4, size=16)
    sheet.blit(night, (pad + 300 + pad, y0))
    _label(sheet, "NIGHT", pad + 300 + pad + 4, y0 + 4, size=16)
    col3 = pad + 300 + pad + 300 + pad
    sheet.blit(hero, (col3, y0))
    _label(sheet, "HERO", col3 + 4, y0 + 4, size=16)
    sheet.blit(film, (col3, y0 + 248))
    _label(sheet, "SHINE (pulse)", col3 + 4, y0 + 250, size=14)
    sheet.blit(truth, (col3, y0 + 340))
    _label(sheet, "40px", col3 + 4, y0 + 342, size=14)

    out = f"{OUT_DIR}/{slug}/{ROUND}.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    return out


if __name__ == "__main__":
    for slug, name in DESIGNS:
        print("wrote", render_design(slug, name))
