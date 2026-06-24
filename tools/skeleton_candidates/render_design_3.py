"""Render the WISP (design_3) skeleton review sheet — scratch exploration.

Day + night gameplay (the night is where additive bloom blooms on dark), a hero
close-up, a 40px NEAREST truth-read, and a 4-frame flap filmstrip showing the
clattering/trailing glowing wing across all four poses.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys

import pygame
pygame.init()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from game import biome
from game.draw import (get_sky_surface_biome, draw_mountains, draw_ground,
                       draw_cloud)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import gameplay_panel, hero_panel, _frame
from tools.skeleton_candidates.design_3 import build


def _gameplay_phase(source, w, h, phase, *, frame_idx=2, tilt=10.0):
    """gameplay_panel clone but parameterised on biome phase so we can flex the
    additive glow on a dark NIGHT sky (phase ~0.5) vs the DAY sky (phase 0.0)."""
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
    crop_w = min(crop_w, GW)
    crop_h = min(crop_h, GH)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


FONT = pygame.font.SysFont("dejavusans", 15, bold=True)
SMALL = pygame.font.SysFont("dejavusans", 12)


def _label(sheet, text, x, y):
    sheet.blit(SMALL.render(text, True, (220, 230, 226)), (x, y))


def main():
    pad = 16
    panel_w, panel_h = 230, 300
    hero_box = 230
    cols_top = 3  # day, night, hero
    sheet_w = pad + (panel_w + pad) * 2 + hero_box + pad
    # Ensure the 4-cell filmstrip (starting after the two truth-read swatches)
    # fits with its last frame label fully on-sheet.
    _strip_x = pad + (120 + 10) * 2 + 24
    sheet_w = max(sheet_w, _strip_x + (130 + 8) * 4 + pad)
    # filmstrip below
    strip_box = 130
    sheet_h = pad + 22 + panel_h + pad + 22 + max(strip_box, 200) + pad + 30

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((16, 18, 22))

    title = FONT.render("SKELETON · design_3 WISP — spectral ghost-fire (round 1)",
                        True, (180, 255, 220))
    sheet.blit(title, (pad, 6))

    y0 = 34
    # Day gameplay
    _label(sheet, "GAMEPLAY · DAY SKY", pad, y0)
    sheet.blit(_gameplay_phase(build, panel_w, panel_h, 0.0), (pad, y0 + 18))
    # Night gameplay (glow flex)
    x1 = pad + panel_w + pad
    _label(sheet, "GAMEPLAY · NIGHT SKY (glow flex)", x1, y0)
    sheet.blit(_gameplay_phase(build, panel_w, panel_h, 0.52), (x1, y0 + 18))
    # Hero close-up on dark panel
    x2 = x1 + panel_w + pad
    _label(sheet, "HERO CLOSE-UP", x2, y0)
    sheet.blit(hero_panel(build, hero_box, frame_idx=2, tilt=0.0, bg=(10, 14, 13)),
               (x2, y0 + 18))

    # ── bottom row: 40px truth-read + 4-frame flap filmstrip ──
    yb = y0 + 18 + panel_h + pad + 4
    _label(sheet, "40px TRUTH READ (NEAREST)", pad, yb)
    # Build the canonical mid-flight frame at native scale, crop, downsize to 40px.
    f = _frame(build, 2, 10.0)
    bb = f.get_bounding_rect()
    f = f.subsurface(bb).copy() if bb.width else f
    tiny = pygame.transform.smoothscale(f, (40, 40))
    # show on both a dark and light swatch, blown up NEAREST so the read is visible
    for i, swatch in enumerate(((12, 16, 14), (150, 190, 230))):
        sw = pygame.Surface((40, 40))
        sw.fill(swatch)
        sw.blit(tiny, (0, 0))
        big = pygame.transform.scale(sw, (120, 120))  # NEAREST upscale
        sheet.blit(big, (pad + i * (120 + 10), yb + 20))
    _label(sheet, "(40px on dark / on day-blue)", pad, yb + 20 + 122)

    # Filmstrip
    xf = pad + (120 + 10) * 2 + 24
    _label(sheet, "4-FRAME FLAP FILMSTRIP (clattering glow wing)", xf, yb)
    for i in range(4):
        cell = pygame.Surface((strip_box, strip_box))
        cell.fill((12, 16, 14))
        frame = _frame(build, i, 8.0)
        fb = frame.get_bounding_rect()
        fr = frame.subsurface(fb).copy() if fb.width else frame
        sc = (strip_box * 0.86) / max(fr.get_size())
        fr = pygame.transform.smoothscale(
            fr, (int(fr.get_width() * sc), int(fr.get_height() * sc)))
        cell.blit(fr, fr.get_rect(center=(strip_box // 2, strip_box // 2)))
        cx = xf + i * (strip_box + 8)
        sheet.blit(cell, (cx, yb + 20))
        _label(sheet, f"frame {i}", cx + 4, yb + 20 + strip_box + 2)

    out = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..",
        "docs", "store_redesign", "costume", "skeleton", "design_3", "round_1.png"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
