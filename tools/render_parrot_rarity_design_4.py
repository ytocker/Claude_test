"""Render the design_4 · AURORA MACAW exploration sheet.

Legendary skin gets the full read-test battery: a gameplay panel over a DAY
and a NIGHT biome, a clean hero product-shot, a 40px NEAREST truth read (the
north star — it lives or dies there), and a 4-frame filmstrip so the baked
aurora's flap animation reads. Saves docs/store_redesign/parrot/design_4/.
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

from tools.ninja_render import gameplay_panel, hero_panel
from tools.parrot_rarity_candidates.design_4 import build

OUT = "/home/user/skybit/docs/store_redesign/parrot/design_4/round_3.png"
NIGHT_PHASE = 0.64375


def _night_gameplay_panel(source, w, h, *, frame_idx=2, tilt=10.0):
    """Mirror ninja_render.gameplay_panel but on the NIGHT biome — the dark sky
    is where the additive halo/ribbons are most at risk of blowing out."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(NIGHT_PHASE)
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


def _label(surf, text, x, y, color=(235, 235, 245), size=20):
    font = pygame.font.SysFont("Arial", size, bold=True)
    surf.blit(font.render(text, True, color), (x, y))


def main():
    W, H = 1180, 720
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 17, 30))
    _label(sheet, "design_4 · AURORA MACAW — LEGENDARY (~2800) · R3", 24, 16, (200, 230, 255), 26)
    _label(sheet, "halo crescent + connected nebula crest + green→magenta ribbon tail + starry plumage",
           24, 48, (150, 160, 190), 16)

    # Gameplay — DAY.
    gp_day = gameplay_panel(build, 270, 380)
    sheet.blit(gp_day, (24, 84))
    _label(sheet, "GAMEPLAY · DAY", 24, 470)

    # Gameplay — NIGHT (the make-or-break for an additive aura).
    gp_night = _night_gameplay_panel(build, 270, 380)
    sheet.blit(gp_night, (310, 84))
    _label(sheet, "GAMEPLAY · NIGHT", 310, 470)

    # Hero product-shot.
    hero = hero_panel(build, 320, frame_idx=2, tilt=0.0, bg=(20, 18, 34))
    sheet.blit(hero, (600, 84))
    _label(sheet, "HERO (store card)", 600, 414)

    # 40px NEAREST truth read on day + night swatches — the north star.
    tx = 600
    ty = 470
    _label(sheet, "40px TRUTH (NEAREST)", tx, ty - 26)
    for i, (bg, name) in enumerate(((biome.palette_for_phase(0.0)['sky_mid'], "day"),
                                    (biome.palette_for_phase(NIGHT_PHASE)['sky_top'], "night"))):
        frame = build(2, 10.0)
        bb = frame.get_bounding_rect()
        crop = frame.subsurface(bb).copy() if bb.width else frame
        small = pygame.transform.smoothscale(crop, (40, 40))
        cell = pygame.Surface((40, 40))
        cell.fill(bg)
        cell.blit(small, (0, 0))
        big = pygame.transform.scale(cell, (160, 160))   # NEAREST upscale
        box = tx + i * 180
        sheet.blit(big, (box, ty))
        _label(sheet, name, box, ty + 162, size=16)

    # 4-frame filmstrip — the flap animation read for a legendary.
    fy = 530
    _label(sheet, "FILMSTRIP · 4 frames (flap)", 24, fy - 4)
    night_bg = biome.palette_for_phase(NIGHT_PHASE)['sky_top']
    for fi in range(4):
        frame = build(fi, 6.0)
        bb = frame.get_bounding_rect()
        crop = frame.subsurface(bb).copy() if bb.width else frame
        sw, sh = crop.get_size()
        sc = 150 / max(sw, sh)
        scaled = pygame.transform.smoothscale(crop, (int(sw * sc), int(sh * sc)))
        cell = pygame.Surface((150, 150))
        cell.fill(night_bg)
        cell.blit(scaled, scaled.get_rect(center=(75, 75)))
        sheet.blit(cell, (24 + fi * 156, fy + 22))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
