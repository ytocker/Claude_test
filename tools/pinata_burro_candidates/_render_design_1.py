"""Round-2 review sheet for burro piñata DESIGN 1 (TASSEL TAIL).

Three in-context columns (day gameplay | night gameplay | hero product shot)
plus a strip of the four raw wing frames at 40px NEAREST scale so the at-size
in-motion read of the new tassel tail can be judged directly.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import importlib.util
import pygame
pygame.init()

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

spec = importlib.util.spec_from_file_location(
    "design_1", "/home/user/skybit/tools/pinata_burro_candidates/design_1.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
build = mod.build

from tools.ninja_render import gameplay_panel, hero_panel

FONT = pygame.font.SysFont("Arial", 16, bold=True)
SMALL = pygame.font.SysFont("Arial", 12)


def _night_panel(source, w, h):
    """Same composition as gameplay_panel but on the night phase of the biome
    cycle, to confirm the cream/orange tassel still reads after dark."""
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
    frame = source(2, 10.0)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def main():
    SHEET_W, SHEET_H = 900, 400
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((30, 28, 38))

    title = FONT.render(
        "BURRO PIÑATA — DESIGN 1: TASSEL TAIL  (round 2)", True, (235, 235, 240))
    sheet.blit(title, (16, 10))

    PW, PH = 210, 300
    y0 = 40
    cols = [
        ("DAY GAMEPLAY", gameplay_panel(build, PW, PH)),
        ("NIGHT GAMEPLAY", _night_panel(build, PW, PH)),
        ("HERO", hero_panel(build, PH)),
    ]
    x = 16
    for label, panel in cols:
        pw = panel.get_width()
        sheet.blit(panel, (x, y0))
        pygame.draw.rect(sheet, (70, 66, 84), (x, y0, pw, PH), 1)
        lab = SMALL.render(label, True, (200, 200, 210))
        sheet.blit(lab, (x + 4, y0 + PH + 4))
        x += pw + 16

    # 40px NEAREST frame strip across the bottom.
    strip_y = y0 + PH + 22
    fx = 16
    strip_lab = SMALL.render("4 FRAMES @ 40px (NEAREST)", True, (200, 200, 210))
    sheet.blit(strip_lab, (fx, strip_y - 2))
    fx0 = 260
    for i in range(4):
        frame = build(i, 0.0)
        bb = frame.get_bounding_rect()
        if bb.width and bb.height:
            frame = frame.subsurface(bb).copy()
        sw, sh = frame.get_size()
        scale = 40.0 / max(sw, sh)
        scaled = pygame.transform.scale(
            frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
        cell = pygame.Surface((48, 48), pygame.SRCALPHA)
        cell.fill((46, 44, 56))
        cell.blit(scaled, scaled.get_rect(center=(24, 24)))
        sheet.blit(cell, (fx0 + i * 56, strip_y - 6))

    out = "/home/user/skybit/docs/store_redesign/animal/pinata_burro/design_1/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
