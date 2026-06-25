"""Round-1 review sheet for shoe candidate design_1 — MEGA DAD.

Composites, side by side: the big store product-shot icon, Pip wearing the shoe
in a day biome gameplay crop and a dusk/night crop, the clean hero panel, and a
40px NEAREST "truth read" (1x and 4x, day + night) so we can confirm the worn
shoe still reads as feet at true gameplay scale. Scratch only — nothing is
registered in shoe_skins._DRAW or the catalog.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib.util
import pygame
pygame.init()

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))

# Load the scratch candidate by path so it never needs a package import.
_spec = importlib.util.spec_from_file_location(
    "shoe_design_1", os.path.join(_HERE, "design_1.py"))
design_1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(design_1)
draw_shoe = design_1.draw_shoe

from game import shoe_skins, biome, parrot
from game.store_skins import _make_skin
from game.shoe_skins import _foot_paint
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import gameplay_panel, hero_panel

build = _make_skin(_foot_paint(draw_shoe))

FONT = pygame.font.SysFont("dejavusans", 14, bold=True)
SMALL = pygame.font.SysFont("dejavusans", 11)


def _night_gameplay_panel(source, w, h):
    """gameplay_panel twin over a dusk/night biome so we can judge the worn
    shoe against a dark sky too."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.5)
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


def _truth_read(source, palette_phase):
    """The worn frame scaled to ~40px tall with NEAREST, on a sky-coloured
    backing, returned as (1x, 4x) so we confirm it reads as feet not mush."""
    frame = source(2, 10.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy() if bb.width else frame
    target_h = 40
    scale = target_h / frame.get_height()
    small = pygame.transform.scale(
        frame, (max(1, int(frame.get_width() * scale)), target_h))
    pal = biome.palette_for_phase(palette_phase)
    bg = pal['sky_top'] if isinstance(pal, dict) and 'sky_top' in pal else (120, 170, 220)
    one = pygame.Surface(small.get_size())
    one.fill(bg)
    one.blit(small, (0, 0))
    big = pygame.transform.scale(
        small, (small.get_width() * 4, small.get_height() * 4))
    four = pygame.Surface(big.get_size())
    four.fill(bg)
    four.blit(big, (0, 0))
    return one, four


def _label(sheet, text, x, y, font=FONT, color=(245, 245, 245)):
    sheet.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    sheet.blit(font.render(text, True, color), (x, y))


def main():
    sheet = pygame.Surface((1240, 720))
    sheet.fill((34, 36, 42))
    _label(sheet, "SHOES design_1 — MEGA DAD  (rare ~780)  ·  round 2", 18, 12,
           font=pygame.font.SysFont("dejavusans", 18, bold=True))

    # ── product-shot icon (the exact store/hero shot) ──────────────────────────
    icon = shoe_skins._build_icon(draw_shoe)
    icon_big = pygame.transform.smoothscale(
        icon, (int(icon.get_width() * 2.7), int(icon.get_height() * 2.7)))
    iw, ih = icon_big.get_size()
    pygame.draw.rect(sheet, (20, 22, 26), (18, 52, iw + 24, ih + 36),
                     border_radius=10)
    sheet.blit(icon_big, (30, 62))
    _label(sheet, "product-shot icon (store hero)", 30, 62 + ih + 10, font=SMALL)

    # ── gameplay panels: day + night, plus clean hero ──────────────────────────
    gx = 18 + iw + 50
    pw, ph = 178, 254
    day = gameplay_panel(build, pw, ph)
    night = _night_gameplay_panel(build, pw, ph)
    hero = hero_panel(build, 232)
    for i, (surf, cap) in enumerate(((day, "Pip — day biome"),
                                     (night, "Pip — dusk/night"),
                                     (hero, "hero panel"))):
        col = gx + i * (surf.get_width() + 22)
        sheet.blit(surf, (col, 60))
        _label(sheet, cap, col, 60 + surf.get_height() + 6, font=SMALL)

    # ── 40px NEAREST truth read — day + night, 1x and 4x ───────────────────────
    ty = 470
    _label(sheet, "40px truth read (NEAREST) — does it read as feet?", 18, ty,
           font=pygame.font.SysFont("dejavusans", 15, bold=True))
    ty += 26
    cx = 30
    for cap, phase in (("DAY", 0.0), ("NIGHT", 0.5)):
        one, four = _truth_read(build, phase)
        _label(sheet, cap, cx, ty, font=SMALL)
        sheet.blit(one, (cx, ty + 18))
        _label(sheet, "1x (40px tall)", cx, ty + 18 + one.get_height() + 4, font=SMALL)
        fx = cx + one.get_width() + 30
        sheet.blit(four, (fx, ty + 18))
        _label(sheet, "4x zoom", fx, ty + 18 + four.get_height() + 4, font=SMALL)
        cx = fx + four.get_width() + 70

    out_dir = os.path.join(_ROOT, "docs", "store_redesign", "shoes", "design_1")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, os.path.getsize(out_path), "bytes")


if __name__ == "__main__":
    main()
