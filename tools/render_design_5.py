"""Render the design_5 SOLAR QUETZAL review sheet.

Composites the legendary candidate the same way every loop figure does
(tools.ninja_render), then lays out the legendary review grid: in-gameplay
panels on day AND night sky, a clean hero product-shot, a 40px NEAREST
truth-read (the north star), and the legendary 4-frame filmstrip so the flap
+ trailing streamers can be judged in motion. Headless (SDL dummy); writes the
sheet under docs/ (kept out of the shipped bundle).
"""
from __future__ import annotations
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
from tools.ninja_render import gameplay_panel, hero_panel, _frame
from tools.parrot_rarity_candidates.design_5 import build
from tools.parrot_rarity_candidates.design_4 import build as build_aurora


_BG = (18, 16, 26)
_INK = (236, 232, 244)
_SUB = (150, 146, 164)


def _font(size, bold=False):
    f = pygame.font.SysFont("Arial", size, bold=bold)
    return f


def _label(surf, text, x, y, *, size=15, color=_INK, bold=False):
    surf.blit(_font(size, bold).render(text, True, color), (x, y))


def _night_gameplay(source, w, h, *, frame_idx=2, tilt=10.0):
    """A night-sky twin of ninja_render.gameplay_panel — same scene at a late
    biome phase, so the gold halo/streamers can be checked against dark sky."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.72)          # deep dusk/night
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


def _truth_read(source, cell, bg):
    """40px NEAREST downscale on a flat tile — the does-it-survive read. The
    bird is rendered then nearest-scaled to 40px and nearest-scaled back up so
    the actual on-screen pixels are visible."""
    tile = pygame.Surface((cell, cell), pygame.SRCALPHA)
    pygame.draw.rect(tile, bg, tile.get_rect(), border_radius=10)
    frame = _frame(source, 2, 10.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    show = max(2, (cell - 24) // max(small.get_width(), small.get_height()))
    big = pygame.transform.scale(
        small, (small.get_width() * show, small.get_height() * show))
    tile.blit(big, big.get_rect(center=(cell // 2, cell // 2)))
    return tile, small.get_size()


def _truth_bird(source, cell, bg):
    """A single 40px NEAREST truth-read tile for one build on `bg` — the same
    does-it-survive read as _truth_read, shared by the legendary-pair tile so
    design_5 and design_4 are downscaled identically side by side."""
    tile = pygame.Surface((cell, cell), pygame.SRCALPHA)
    pygame.draw.rect(tile, bg, tile.get_rect(), border_radius=10)
    frame = _frame(source, 2, 10.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    show = max(2, (cell - 24) // max(small.get_width(), small.get_height()))
    big = pygame.transform.scale(
        small, (small.get_width() * show, small.get_height() * show))
    tile.blit(big, big.get_rect(center=(cell // 2, cell // 2)))
    return tile


def main():
    W, H = 1180, 950
    sheet = pygame.Surface((W, H))
    sheet.fill(_BG)

    _label(sheet, "design_5  ·  SOLAR QUETZAL", 28, 22, size=26, bold=True)
    _label(sheet, "LEGENDARY  ~3500  ·  sun-disc halo + rays · gold crown-crest · "
                  "quetzal tail-streamers · radiant gold/emerald re-plumage",
           28, 56, size=14, color=_SUB)

    top = 92

    # Row 1: day + night in-gameplay, then the clean hero product-shot. Panels
    # are taller than wide so the gameplay_panel crop stays inside the 360-wide
    # virtual canvas (crop_w scales with w/h).
    gp_w, gp_h = 210, 300
    day = gameplay_panel(build, gp_w, gp_h)
    night = _night_gameplay(build, gp_w, gp_h)
    sheet.blit(day, (28, top + 22))
    sheet.blit(night, (28 + gp_w + 18, top + 22))
    _label(sheet, "IN-GAMEPLAY · DAY SKY", 28, top, size=14, bold=True)
    _label(sheet, "IN-GAMEPLAY · NIGHT SKY", 28 + gp_w + 18, top, size=14, bold=True)

    hero_x = 28 + (gp_w + 18) * 2
    hero = hero_panel(build, gp_h)
    sheet.blit(hero, (hero_x, top + 22))
    _label(sheet, "HERO PRODUCT-SHOT", hero_x, top, size=14, bold=True)

    # Row 2: the 40px truth read (day + night tile bg) + the legendary filmstrip.
    row2 = top + 22 + gp_h + 34
    _label(sheet, "40px TRUTH-READ (NEAREST)", 28, row2, size=14, bold=True)
    tr_day, px = _truth_read(build, 150, (210, 224, 236))     # pale day tile
    tr_night, _ = _truth_read(build, 150, (22, 24, 40))       # navy night tile
    sheet.blit(tr_day, (28, row2 + 22))
    sheet.blit(tr_night, (28 + 168, row2 + 22))
    _label(sheet, f"day  ·  {px[0]}x{px[1]}px", 28, row2 + 178, size=12, color=_SUB)
    _label(sheet, "navy store card", 28 + 168, row2 + 178, size=12, color=_SUB)

    # Legendary 4-frame filmstrip — the flap + trailing streamers in motion.
    fs_x = 28 + 168 * 2 + 18
    _label(sheet, "4-FRAME FILMSTRIP (flap + trailing streamers)",
           fs_x, row2, size=14, bold=True)
    cell = 150
    for i in range(4):
        strip = pygame.Surface((cell, cell), pygame.SRCALPHA)
        pygame.draw.rect(strip, (30, 28, 44), strip.get_rect(), border_radius=10)
        frame = _frame(build, i, 8.0)
        bb = frame.get_bounding_rect()
        if bb.width and bb.height:
            frame = frame.subsurface(bb).copy()
        sw, sh = frame.get_size()
        sc = (cell * 0.8) / max(sw, sh)
        frame = pygame.transform.smoothscale(
            frame, (max(1, int(sw * sc)), max(1, int(sh * sc))))
        strip.blit(frame, frame.get_rect(center=(cell // 2, cell // 2)))
        sheet.blit(strip, (fs_x + i * (cell + 10), row2 + 22))
        _label(sheet, f"frame {i}", fs_x + i * (cell + 10) + 6, row2 + 178,
               size=12, color=_SUB)

    # Row 3: the legendary-pair read — design_5 SOLAR next to design_4 AURORA on
    # the SAME navy store card at 40px, to prove the legendary pair reads
    # obviously-different-but-same-tier at thumbnail.
    row3 = row2 + 22 + 150 + 40
    _label(sheet, "LEGENDARY PAIR @ 40px ON NAVY STORE CARD "
                  "(different look · same tier)", 28, row3, size=14, bold=True)
    navy = (22, 24, 40)
    cmp_cell = 150
    pair = (("design_5 · SOLAR", build), ("design_4 · AURORA", build_aurora))
    for i, (name, src) in enumerate(pair):
        tile = _truth_bird(src, cmp_cell, navy)
        x = 28 + i * (cmp_cell + 14)
        sheet.blit(tile, (x, row3 + 22))
        _label(sheet, name, x + 4, row3 + 22 + cmp_cell + 4, size=12, color=_SUB)

    out = ("/home/user/skybit/docs/store_redesign/parrot/design_5/round_3.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
