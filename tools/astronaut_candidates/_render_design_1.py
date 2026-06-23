"""Render design_1 MOONWALKER into a single labeled review sheet:
hero product-shot + in-gameplay (day) + 40px NEAREST truth read (day + night).
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools.ninja_render import hero_panel, _frame
from tools.astronaut_candidates.design_1 import build
from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

OUT = "docs/store_redesign/costume/astronaut/design_1/round_2.png"
TITLE = "ASTRONAUT  design_1  MOONWALKER  (R2)"


def _gameplay_phase(phase):
    """Full biome scene with Pip mid-flight, at the given day/night phase,
    returned as a full GW×GH surface (so we can also derive a 40px read)."""
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
    frame = _frame(build, 2, 10.0)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    return scene, (pip_cx, pip_cy)


def _gameplay_crop(phase, w, h):
    """Pip mid-flight at the given phase, cropped to a panel and scaled —
    mirrors ninja_render.gameplay_panel but parameterised by day/night phase."""
    scene, (cx, cy) = _gameplay_phase(phase)
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (cx + 34, cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _truth_read(phase, px=40):
    """Shrink the gameplay frame to ~40px then NEAREST-upscale ×3 — the brutal
    'does it still read at thumbnail size' test, day and night."""
    scene, (cx, cy) = _gameplay_phase(phase)
    crop = pygame.Rect(0, 0, 64, 64)
    crop.center = (cx, cy)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    sub = scene.subsurface(crop).copy()
    small = pygame.transform.smoothscale(sub, (px, px))
    return pygame.transform.scale(small, (px * 3, px * 3))   # NEAREST upscale


def main():
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 18, bold=True)
    small = pygame.font.SysFont("Arial", 13)

    hero = hero_panel(build, 300)
    play_day = _gameplay_crop(0.0, 200, 345)
    play_night = _gameplay_crop(0.5, 200, 345)
    read_day = _truth_read(0.0)
    read_night = _truth_read(0.5)

    pad = 18
    label_h = 26
    top = 56
    body_h = 345
    sheet_w = pad + 300 + pad + 200 + pad + 200 + pad + 120 + pad
    sheet_h = top + label_h + body_h + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((28, 30, 40))
    sheet.blit(font.render(TITLE, True, (240, 242, 248)), (pad, 18))

    x = pad
    y = top
    # Hero
    sheet.blit(small.render("hero", True, (180, 186, 200)), (x, y))
    sheet.blit(hero, (x, y + label_h))
    x += 300 + pad
    # Gameplay — day
    sheet.blit(small.render("in-gameplay (day)", True, (180, 186, 200)), (x, y))
    sheet.blit(play_day, (x, y + label_h))
    x += 200 + pad
    # Gameplay — night
    sheet.blit(small.render("in-gameplay (night)", True, (180, 186, 200)), (x, y))
    sheet.blit(play_night, (x, y + label_h))
    x += 200 + pad
    # 40px truth reads, stacked
    sheet.blit(small.render("40px read  day / night", True, (180, 186, 200)), (x, y))
    sheet.blit(read_day, (x, y + label_h))
    sheet.blit(read_night, (x, y + label_h + 120 + 14))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
