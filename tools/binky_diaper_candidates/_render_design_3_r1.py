"""Round-1 review sheet for the PINNED TERRY diaper (design_3).

Composites the standard deliverable: a hero product-shot, a daytime gameplay
panel, and 40px NEAREST truth-reads on BOTH day and navy-night skies — the
nappy lives or dies at that downscaled size on either sky, so both are shown.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import hero_panel, gameplay_panel, _frame, FRAME_IDX, TILT
from tools.binky_diaper_candidates.design_3 import build as BUILD

FONT = pygame.font.SysFont("DejaVu Sans", 16, bold=True)
SMALL = pygame.font.SysFont("DejaVu Sans", 12)


def _label(sheet, txt, x, y, col=(235, 235, 240)):
    sheet.blit((SMALL if len(txt) > 22 else FONT).render(txt, True, col), (x, y))


def _gameplay_night(w, h):
    """Like ninja_render.gameplay_panel but over the navy-night biome (phase
    0.6), to truth-check the cream's value hold against deep navy."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.6)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = _frame(BUILD, FRAME_IDX, TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _truth_tile(bg, box=200):
    """A 40px NEAREST downscale of the bird, re-upscaled NEAREST onto a flat
    swatch — the honest pixel-level read at shop-thumbnail size."""
    frame = _frame(BUILD, FRAME_IDX, 0.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40 / max(sw, sh)
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    big = pygame.transform.scale(small, (small.get_width() * 4, small.get_height() * 4))
    tile = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(tile, bg, tile.get_rect(), border_radius=14)
    tile.blit(big, big.get_rect(center=(box // 2, box // 2)))
    return tile


def main():
    pad = 16
    cw, ch = 300, 420  # gameplay panels: crop_w stays <=360 (GW) at this aspect
    cols = [hero_panel(BUILD, 300, tilt=0.0),
            gameplay_panel(BUILD, cw, ch),
            _gameplay_night(cw, ch)]
    titles = ["HERO product-shot", "GAMEPLAY  day biome", "GAMEPLAY  navy night"]

    truth = [_truth_tile((30, 110, 200)), _truth_tile((10, 11, 40))]
    ttitles = ["40px NEAREST  day swatch", "40px NEAREST  navy swatch"]

    row_h = max(c.get_height() for c in cols)
    row_w = pad + sum(c.get_width() for c in cols) + pad * len(cols)
    W = max(row_w, pad + 200 * 2 + pad * 2)
    H = 40 + row_h + 24 + 200 + pad * 2
    sheet = pygame.Surface((W, H))
    sheet.fill((24, 22, 30))

    _label(sheet, "BINKY diaper redo - design_3  PINNED TERRY  (round 1)", pad, 8)
    y0 = 40
    x = pad
    for col, t in zip(cols, titles):
        sheet.blit(col, (x, y0))
        _label(sheet, t, x, y0 + col.get_height() + 4)
        x += col.get_width() + pad

    y1 = y0 + row_h + 24
    x = pad
    for tile, t in zip(truth, ttitles):
        sheet.blit(tile, (x, y1))
        _label(sheet, t, x, y1 + 200 + 2)
        x += 200 + pad

    out = ("/home/user/skybit/docs/store_redesign/parrot/baby_parrot/"
           "diaper_redo/design_3/round_1.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
