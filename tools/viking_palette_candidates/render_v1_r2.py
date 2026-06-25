"""Compose the IRONCLAD round-2 review sheet (final polish pass).

Round 2 adds a NIGHT gameplay panel beside the day one so the two cheap polish
nudges — a lighter/cooler fur ruff and a darker oak plank ring — can be judged
both in bright daylight and against the moonlit night palette, alongside the
hero shot and the day|night 40px truth read.

Headless: SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python <this>.
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

from tools import ninja_render
from tools.viking_palette_candidates.v1 import build

OUT = "docs/store_redesign/costume/viking/palette/v1/round_2.png"
TITLE = ("VIKING PALETTE v1 — IRONCLAD  R2  "
         "(final polish: lighter/cooler fur ruff · darker oak plank ring)")

# NIGHT keyframe phase from game/biome.py — moonlit cool stone, star-filled sky.
NIGHT_PHASE = 0.64375


def _label(surf, text, x, y, size=18, color=(236, 238, 246)):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf.blit(font.render(text, True, color), (x, y))


def _gameplay_panel_phase(source, w, h, phase, *,
                          frame_idx=ninja_render.FRAME_IDX,
                          tilt=ninja_render.TILT):
    """Same composition as ninja_render.gameplay_panel, but parameterised on the
    biome phase so we can render the bird over both the day and night scene."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    bucket = int(round(phase * 1000))
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, bucket), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = ninja_render._frame(source, frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _truth_read(box):
    """The 40px-in-motion test: three flap poses NEAREST-shrunk to a ~40px bird
    then magnified so the reviewer judges the real on-screen read. Three rows ×
    two phase columns (day | night)."""
    frames = [build(fi, t) for fi, t in
              ((ninja_render.FRAME_IDX, ninja_render.TILT),
               (0, -8.0), (3, 22.0))]
    smalls = []
    for frame in frames:
        bb = frame.get_bounding_rect()
        frame = frame.subsurface(bb).copy()
        sw, sh = frame.get_size()
        scale = 40.0 / max(sw, sh)
        smalls.append(pygame.transform.scale(
            frame, (max(1, int(sw * scale)), max(1, int(sh * scale)))))

    panel = pygame.Surface((box, box))
    half = box // 2
    pygame.draw.rect(panel, (150, 200, 235), (0, 0, half, box))        # day sky
    pygame.draw.rect(panel, (16, 18, 34), (half, 0, box - half, box))  # night sky
    for row, small in enumerate(smalls):
        tile = pygame.Surface((48, 48), pygame.SRCALPHA)
        tile.blit(small, small.get_rect(center=(24, 24)))
        big = pygame.transform.scale(tile, (48 * 2, 48 * 2))
        ry = 28 + row * (box - 40) // 3
        for cx in (half // 2, half + half // 2):
            panel.blit(big, big.get_rect(center=(cx, ry + 48)))
    return panel


def main():
    box = 360
    gw = int(box * 9 / 16)
    hero = ninja_render.hero_panel(build, box)
    day = _gameplay_panel_phase(build, gw, box, 0.0)
    night = _gameplay_panel_phase(build, gw, box, NIGHT_PHASE)
    truth = _truth_read(box)

    pad = 18
    head = 56
    widths = [box, gw, gw, box]
    W = pad * (len(widths) + 1) + sum(widths)
    H = head + box + 30 + pad
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 17, 26))
    _label(sheet, TITLE, pad, 16, size=20)

    xs = []
    x = pad
    for w in widths:
        xs.append(x)
        x += w + pad
    y = head
    for x, panel in zip(xs, (hero, day, night, truth)):
        sheet.blit(panel, (x, y))
    names = ("HERO PRODUCT SHOT", "IN-GAMEPLAY (day biome)",
             "IN-GAMEPLAY (night biome)", "40px TRUTH READ  (day | night, 3 poses)")
    for x, name in zip(xs, names):
        _label(sheet, name, x, y + box + 6, size=15, color=(190, 194, 210))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
