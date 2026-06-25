"""Render the design_2 PRISM LORIKEET review sheet (exploration only).

Standard ninja_render layout, matched to the design_1 / design_3 sibling
sheets: gameplay_panel (day + night biome) + hero_panel in one row, then a
40px NEAREST truth read with a 4-frame strip on day and night swatches — the
in-motion downscale this skin lives or dies on, at the same scale as the
siblings so the crest + facets can be judged honestly.
Saves docs/store_redesign/parrot/design_2/round_2.png. Run headless:
    SDL_VIDEODRIVER=dummy python tools/parrot_rarity_candidates/render_design_2.py
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
from tools.ninja_render import gameplay_panel, hero_panel, _frame, FRAME_IDX, TILT
from tools.parrot_rarity_candidates.design_2 import build

OUT = "docs/store_redesign/parrot/design_2/round_2.png"
FONT = pygame.font.SysFont("Arial", 16, bold=True)
SMALL = pygame.font.SysFont("Arial", 13)


def _night_gameplay_panel(source, w, h, *, frame_idx=FRAME_IDX, tilt=TILT):  # noqa
    """Same as ninja_render.gameplay_panel but at the night biome phase, so the
    cool crystal mass + shard tips are verified against a dark sky."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.5)   # deep night
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


def _truth40(source, frame_idx=FRAME_IDX, tilt=TILT):
    """The 40px NEAREST downscale — the real-world store-list / in-flight size."""
    frame = _frame(source, frame_idx, tilt)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40 / max(sw, sh)
    return pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))


def _label(surf, text, x, y, color=(235, 235, 240)):
    surf.blit(FONT.render(text, True, color), (x, y))


def main():
    # Portrait gameplay panels at the sibling scale (PW, PH = 200, 280).
    PW, PH = 200, 280
    HERO = 200
    sheet = pygame.Surface((PW * 3 + 48, PH + 140))
    sheet.fill((18, 16, 22))
    _label(sheet, "design_2 · PRISM LORIKEET — EPIC", 16, 12, (150, 230, 226))
    sheet.blit(SMALL.render(
        "crystal-teal recolour · 3-shard crest · faceted body planes · refraction glints",
        True, (180, 180, 190)), (16, 36))

    y = 60
    day = gameplay_panel(build, PW, PH)
    night = _night_gameplay_panel(build, PW, PH)
    hero = hero_panel(build, HERO)
    for i, (panel, cap) in enumerate(
            ((day, "DAY sky · in-flight"), (night, "NIGHT sky · in-flight"),
             (hero, "hero product shot"))):
        x = 16 + i * (PW + 8)
        py = y + (PH - panel.get_height()) // 2
        sheet.blit(panel, (x, py))
        sheet.blit(SMALL.render(cap, True, (200, 200, 210)),
                   (x, y + PH + 4))

    # 40px truth reads on day-blue and night-navy swatches, plus a frame strip.
    ty = y + PH + 26
    _label(sheet, "40px truth read (NEAREST):", 16, ty, (160, 230, 226))
    bx = 230
    for sw_col, lbl in (((120, 175, 230), "day"), ((20, 22, 44), "night")):
        for fi in range(4):
            sw = pygame.Surface((46, 46))
            sw.fill(sw_col)
            t = _truth40(build, frame_idx=fi, tilt=TILT)
            sw.blit(t, t.get_rect(center=(23, 23)))
            sheet.blit(sw, (bx, ty - 2))
            bx += 50
        bx += 10

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
