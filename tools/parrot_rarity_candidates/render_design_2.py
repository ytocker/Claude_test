"""Render the PRISM LORIKEET (design_2) review sheet.

gameplay_panel (day + night) + hero_panel + a 40px NEAREST truth read, so the
shard-crest silhouette and facet sharpness can be judged exactly as the store
thumbnail will show them. Scratch only — saves under docs/, never ships.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

import tools.ninja_render as NR
from tools.parrot_rarity_candidates.design_2 import build

OUT = "docs/store_redesign/parrot/design_2/round_1.png"
FONT = pygame.font.SysFont("sans", 16, bold=True)
SMALL = pygame.font.SysFont("sans", 12)


def _night_gameplay(source, w, h):
    """Same composition as ninja_render.gameplay_panel but on a night biome
    palette so the cool crystal mass + glints are checked against dark sky."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.5)   # deep night phase
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, v in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=v)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pcx, pcy = 96, 270
    fr = NR._frame(source, NR.FRAME_IDX, NR.TILT)
    scene.blit(fr, fr.get_rect(center=(pcx, pcy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pcx + 34, pcy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _truth_40(source):
    """Downscale the flat mid-flight frame to 40px with NEAREST — the honest
    thumbnail read the north star is judged on."""
    fr = NR._frame(source, NR.FRAME_IDX, NR.TILT)
    bb = fr.get_bounding_rect()
    if bb.width and bb.height:
        fr = fr.subsurface(bb).copy()
    sw, sh = fr.get_size()
    sc = 40 / max(sw, sh)
    return pygame.transform.scale(fr, (max(1, int(sw * sc)), max(1, int(sh * sc))))


def _label(sheet, text, x, y, font=FONT, col=(236, 240, 250)):
    sheet.blit(font.render(text, True, col), (x, y))


def main():
    W, H = 920, 600
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 16, 28))
    _label(sheet, "design_2 · PRISM LORIKEET — EPIC", 24, 16,
           col=(150, 230, 226))
    _label(sheet, "faceted crystal crest + rainbow refraction over a crystal-teal recolour",
           24, 40, font=SMALL, col=(170, 174, 190))

    # Day + night gameplay crops side by side.
    gw, gh = 250, 360
    day = NR.gameplay_panel(build, gw, gh)
    night = _night_gameplay(build, gw, gh)
    sheet.blit(day, (24, 70))
    sheet.blit(night, (24 + gw + 16, 70))
    _label(sheet, "in-game · DAY", 24, 70 + gh + 4, font=SMALL)
    _label(sheet, "in-game · NIGHT", 24 + gw + 16, 70 + gh + 4, font=SMALL)

    col_x = 24 + 2 * (gw) + 2 * 16
    # Hero product shots on dark navy store card + a light card.
    hero_dark = NR.hero_panel(build, 220, bg=(22, 20, 40))
    hero_lite = NR.hero_panel(build, 220, bg=(58, 54, 78))
    sheet.blit(hero_dark, (col_x, 70))
    sheet.blit(hero_lite, (col_x, 70 + 230))
    _label(sheet, "hero · navy card", col_x, 70 - 2 + 222, font=SMALL)

    # 40px NEAREST truth read, framed on both day-ish and dark patches.
    t = _truth_40(build)
    ty = 70 + 460
    for i, bg in enumerate(((120, 196, 230), (20, 18, 34))):
        cell = pygame.Surface((56, 56))
        cell.fill(bg)
        cell.blit(t, t.get_rect(center=(28, 28)))
        sheet.blit(cell, (col_x + i * 64, ty))
    _label(sheet, "40px truth", col_x, ty - 18, font=SMALL)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
