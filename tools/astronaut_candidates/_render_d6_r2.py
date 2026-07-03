"""Render the design_6 ARTEMIS review sheet: hero + gameplay (day) + a 40px
NEAREST truth read on both day and night. Exploration only."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import hero_panel, gameplay_panel, _frame
from tools.astronaut_candidates.design_6 import build

FONT = pygame.font.SysFont("dejavusans", 16, bold=True)
SMALL = pygame.font.SysFont("dejavusans", 12)


def _gameplay_night(source, w, h):
    """Same crop as ninja_render.gameplay_panel but on the NIGHT palette."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.644)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = _frame(source, 2, 10.0)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _truth40(source, day):
    """The honest 40px NEAREST read on the actual sky behind the bird."""
    frame = _frame(source, 2, 10.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    sc = 40 / max(sw, sh)
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * sc)), max(1, int(sh * sc))))
    palette = biome.palette_for_phase(0.0 if day else 0.644)
    sky = palette['sky_mid'] if day else palette['sky_top']
    tile = pygame.Surface((56, 56))
    tile.fill(sky)
    tile.blit(small, small.get_rect(center=(28, 28)))
    return pygame.transform.scale(tile, (140, 140))   # NEAREST upscale


def main():
    W, H = 760, 560
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 18, 24))

    title = FONT.render("DESIGN 6  ·  ARTEMIS  —  R2: dome promoted, PLSS demoted, one stripe band", True, (240, 242, 250))
    sheet.blit(title, (20, 14))
    sub = SMALL.render("clear bubble dome (Pip's face shows through) + blue/red candy-stripes + squared PLSS", True, (170, 175, 190))
    sheet.blit(sub, (20, 38))

    GPW, GPH = 200, 280
    # Hero
    hero = hero_panel(build, 240, tilt=0.0, bg=(150, 196, 232))   # day-sky bg
    sheet.blit(hero, (20, 64))
    sheet.blit(SMALL.render("HERO (day-sky card)", True, (200, 205, 220)), (24, 308))

    # Gameplay day
    gp = gameplay_panel(build, GPW, GPH)
    sheet.blit(gp, (290, 64))
    sheet.blit(SMALL.render("GAMEPLAY (day)", True, (200, 205, 220)), (294, 348))

    # Gameplay night
    gpn = _gameplay_night(build, GPW, GPH)
    sheet.blit(gpn, (520, 64))
    sheet.blit(SMALL.render("GAMEPLAY (night)", True, (200, 205, 220)), (524, 348))

    # 40px truth reads
    ty = 380
    d40 = _truth40(build, day=True)
    n40 = _truth40(build, day=False)
    sheet.blit(d40, (20, ty))
    sheet.blit(SMALL.render("40px TRUTH — day (NEAREST)", True, (235, 235, 240)), (20, ty + 144))
    sheet.blit(n40, (200, ty))
    sheet.blit(SMALL.render("40px TRUTH — night (NEAREST)", True, (235, 235, 240)), (200, ty + 144))

    note = SMALL.render("Read target: white puffy body + clear dome with a face + blue/red stripes.", True, (160, 165, 182))
    sheet.blit(note, (380, ty + 60))
    note2 = SMALL.render("Keyline (#2A2D34) holds the white off the sky on both day & night.", True, (160, 165, 182))
    sheet.blit(note2, (380, ty + 82))

    out = "/home/user/skybit/docs/store_redesign/costume/astronaut/design_6/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
