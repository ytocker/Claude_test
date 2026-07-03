"""Render the design_2 MARIGOLD CALAVERA review sheet (scratch only).

Day-sky gameplay panel, night-sky gameplay panel, a hero close-up, and a 40px
NEAREST "truth read" thumbnail that must still parse as a skeleton.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
import pygame
pygame.init()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import gameplay_panel, hero_panel
from tools.skeleton_candidates.design_2 import build

OUT = os.path.join(os.path.dirname(__file__), "..", "..",
                   "docs", "store_redesign", "costume", "skeleton",
                   "design_2", "round_2.png")


def _night_gameplay_panel(source, w, h):
    """Same composition as gameplay_panel but on a deep night palette so we
    can judge the saturated marigold/cyan/magenta read on a dark sky."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.5)            # night phase
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


def _truth_thumb(source, px):
    """The bird frame scaled to px via NEAREST — the 'does it still read as a
    skeleton tiny and in motion' check."""
    frame = source(2, 10.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    return pygame.transform.scale(frame, (px, px))


def _label(surf, text, x, y):
    font = pygame.font.SysFont("dejavusans", 16, bold=True)
    surf.blit(font.render(text, True, (240, 240, 245)), (x, y))


def main():
    pad = 16
    pw, ph = 250, 360                # gameplay panels (aspect kept within the
                                     # 360px scene so the crop stays in bounds)
    hbox = 360                       # hero box
    sheet_w = pad * 3 + pw * 2
    sheet_h = pad * 4 + 24 + ph + 24 + hbox
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 24))

    title = pygame.font.SysFont("dejavusans", 22, bold=True)
    sheet.blit(title.render("SKELETON  design_2  MARIGOLD CALAVERA  round_2",
                            True, (255, 220, 180)), (pad, 6))

    y0 = 36
    _label(sheet, "GAMEPLAY — DAY", pad, y0)
    sheet.blit(gameplay_panel(build, pw, ph), (pad, y0 + 22))
    _label(sheet, "GAMEPLAY — NIGHT", pad * 2 + pw, y0)
    sheet.blit(_night_gameplay_panel(build, pw, ph), (pad * 2 + pw, y0 + 22))

    y1 = y0 + 22 + ph + 20
    _label(sheet, "HERO CLOSE-UP", pad, y1)
    sheet.blit(hero_panel(build, hbox), (pad, y1 + 22))

    # Truth-read column: 40px NEAREST thumbnail (the core legibility check),
    # plus a 4x blow-up of those exact pixels so the reviewer can see what the
    # 40px read actually resolves to.
    tx = pad * 2 + pw
    _label(sheet, "TRUTH READ — 40px NEAREST", tx, y1)
    thumb = _truth_thumb(build, 40)
    sheet.blit(thumb, (tx, y1 + 28))
    big = pygame.transform.scale(thumb, (160, 160))
    sheet.blit(big, (tx + 60, y1 + 28))
    _label(sheet, "40px", tx, y1 + 70)
    _label(sheet, "40px @4x (same pixels)", tx + 60, y1 + 192)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("wrote", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
