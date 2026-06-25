"""Render the design_2 PUMPKIN SUIT review sheet: hero shot + day/night
gameplay panels + a 40px NEAREST truth read (day + night), labeled. Headless."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import (get_sky_surface_biome, draw_mountains, draw_ground,
                       draw_cloud)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

from tools.ninja_render import hero_panel, _frame, FRAME_IDX, TILT
from tools.astronaut_candidates.design_2 import build


def gameplay_panel_phase(source, w, h, phase, *, frame_idx=FRAME_IDX, tilt=TILT):
    """Same crop/scale as ninja_render.gameplay_panel but at an arbitrary biome
    phase so we can show day (0.0) and deep night (0.55)."""
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
    frame = _frame(source, frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def truth_read(source, bg, frame_idx=FRAME_IDX, tilt=TILT):
    """The bird scaled to 40px tall with NEAREST (no smoothing) on a sky-tone
    tile — the 'lives or dies at 40px' read."""
    frame = _frame(source, frame_idx, tilt)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40 / sh
    small = pygame.transform.scale(frame, (max(1, int(sw * scale)), 40))
    tile = pygame.Surface((96, 96))
    tile.fill(bg)
    tile.blit(small, small.get_rect(center=(48, 48)))
    return tile


def main():
    font = pygame.font.SysFont("Arial", 22, bold=True)
    sfont = pygame.font.SysFont("Arial", 15, bold=True)

    hero = hero_panel(build, 260)
    day = gameplay_panel_phase(build, 220, 330, 0.0)
    night = gameplay_panel_phase(build, 220, 330, 0.55)
    day_pal = biome.palette_for_phase(0.0)
    night_pal = biome.palette_for_phase(0.55)
    tr_day = truth_read(build, day_pal['sky_top'])
    tr_night = truth_read(build, night_pal['sky_top'])

    W, H = 920, 480
    sheet = pygame.Surface((W, H))
    sheet.fill((24, 22, 32))

    title = font.render("ASTRONAUT  design_2  -  PUMPKIN SUIT  (round 2)", True, (255, 196, 120))
    sheet.blit(title, (20, 16))
    sub = sfont.render("orange Apollo launch-entry suit  |  clear fishbowl helmet, visor UP  |  friendly face inside  |  white pack + neck ring",
                       True, (190, 190, 200))
    sheet.blit(sub, (20, 46))

    y = 82
    sheet.blit(hero, (20, y))
    sheet.blit(sfont.render("HERO", True, (220, 220, 230)), (20, y + 264))

    sheet.blit(day, (296, y))
    sheet.blit(sfont.render("GAMEPLAY  DAY", True, (220, 220, 230)), (296, y + 334))

    sheet.blit(night, (528, y))
    sheet.blit(sfont.render("GAMEPLAY  NIGHT", True, (220, 220, 230)), (528, y + 334))

    # 40px NEAREST truth reads in a clean far-right column.
    cx = 800
    sheet.blit(tr_day, (cx, y))
    sheet.blit(sfont.render("40px DAY", True, (220, 220, 230)), (cx, y + 98))
    sheet.blit(tr_night, (cx, y + 134))
    sheet.blit(sfont.render("40px NIGHT", True, (220, 220, 230)), (cx, y + 232))

    out_dir = "docs/store_redesign/costume/astronaut/design_2"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out)
    print("saved", out)

    # Build + CHECK the 40px read FIRST: also dump the raw 40px-tall NEAREST
    # frames upscaled 6x so the actual truth read can be inspected pixel-by-pixel
    # before trusting the composited sheet.
    for nm, pal in (("day", day_pal), ("night", night_pal)):
        tile = truth_read(build, pal['sky_top'])
        big = pygame.transform.scale(tile, (tile.get_width() * 6, tile.get_height() * 6))
        pygame.image.save(big, os.path.join(out_dir, f"_check40_{nm}.png"))
    print("saved 40px checks")


if __name__ == "__main__":
    main()
