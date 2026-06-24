"""Render the WISP (design_3) skeleton review sheet — round 3 (final), scratch.

Day + night gameplay (the night is where additive bloom blooms on dark), a hero
close-up, a 40px NEAREST truth-read, and a 4-frame flap filmstrip showing the
clattering/trailing glowing wing across all four poses.

Round-3 closes the lone blocker — the DAY read. The bone-set now rides on
opaque value (3px rib/spine in the #C9FFE3 core, an opaque dark keyline under
the whole bone-set) so the rib ladder + spine survive on bright blue instead of
flattening into a green blob; the wisp-dissolve floor is raised so the lower
body holds a faint shape instead of confetti.

The round-1 pirate-leak guard is kept: THIS design's build is loaded via an
isolated spec_from_file_location and every panel is asserted spectral-green
(no pirate red) before the sheet is written.

Headless:  SDL_VIDEODRIVER=dummy python tools/skeleton_candidates/render_design_3_r3.py
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import importlib.util
import sys

ROOT = "/home/user/skybit"
sys.path.insert(0, ROOT)

import pygame
pygame.init()

from game import biome
from game.draw import (get_sky_surface_biome, draw_mountains, draw_ground,
                       draw_cloud)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import hero_panel, _frame

# Load THIS design's build in isolation so no sibling candidate's `build` can
# bleed into any panel (the round-1 pirate-leak blocker).
_spec = importlib.util.spec_from_file_location(
    "skeleton_design_3_r3",
    os.path.join(ROOT, "tools/skeleton_candidates/design_3.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
build = _mod.build


def _gameplay_phase(source, w, h, phase, *, frame_idx=2, tilt=10.0):
    """gameplay_panel clone parameterised on biome phase so we can flex the
    additive glow on a dark NIGHT sky vs the DAY sky."""
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
    crop_w = min(int(crop_h * w / h), GW)
    crop_h = min(crop_h, GH)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _assert_green(surf, label):
    """Sheet-integrity guard: a WISP panel must be spectral-green and carry no
    pirate red. Catches a wrong-builder leak before the sheet is committed."""
    red = green = 0
    for x in range(0, surf.get_width(), 2):
        for y in range(0, surf.get_height(), 2):
            r, g, b = surf.get_at((x, y))[:3]
            if r > 130 and g < 90 and b < 90:
                red += 1
            if g > 150 and r < 150 and b < 170 and g - r > 40:
                green += 1
    if red > green:
        raise AssertionError(
            f"PANEL {label!r} reads RED ({red}) > GREEN ({green}) — wrong builder leaked")
    return green


FONT = pygame.font.SysFont("dejavusans", 15, bold=True)
SMALL = pygame.font.SysFont("dejavusans", 12)


def _label(sheet, text, x, y):
    sheet.blit(SMALL.render(text, True, (220, 230, 226)), (x, y))


def main():
    pad = 16
    panel_w, panel_h = 230, 300
    hero_box = 230
    sheet_w = pad + (panel_w + pad) * 2 + hero_box + pad
    _strip_x = pad + (120 + 10) * 2 + 24
    sheet_w = max(sheet_w, _strip_x + (130 + 8) * 4 + pad)
    strip_box = 130
    sheet_h = pad + 22 + panel_h + pad + 22 + max(strip_box, 200) + pad + 30

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((16, 18, 22))

    title = FONT.render(
        "SKELETON · design_3 WISP — spectral ghost-fire (round 3, final)",
        True, (180, 255, 220))
    sheet.blit(title, (pad, 6))

    y0 = 34
    day = _gameplay_phase(build, panel_w, panel_h, 0.0)
    night = _gameplay_phase(build, panel_w, panel_h, 0.52)
    hero = hero_panel(build, hero_box, frame_idx=2, tilt=0.0, bg=(10, 14, 13))
    _assert_green(day, "DAY")
    _assert_green(night, "NIGHT")
    _assert_green(hero, "HERO")

    _label(sheet, "GAMEPLAY · DAY SKY", pad, y0)
    sheet.blit(day, (pad, y0 + 18))
    x1 = pad + panel_w + pad
    _label(sheet, "GAMEPLAY · NIGHT SKY (glow flex)", x1, y0)
    sheet.blit(night, (x1, y0 + 18))
    x2 = x1 + panel_w + pad
    _label(sheet, "HERO CLOSE-UP", x2, y0)
    sheet.blit(hero, (x2, y0 + 18))

    # ── bottom row: 40px truth-read + 4-frame flap filmstrip ──
    yb = y0 + 18 + panel_h + pad + 4
    _label(sheet, "40px TRUTH READ (NEAREST)", pad, yb)
    f = _frame(build, 2, 10.0)
    bb = f.get_bounding_rect()
    f = f.subsurface(bb).copy() if bb.width else f
    tiny = pygame.transform.smoothscale(f, (40, 40))
    for i, swatch in enumerate(((12, 16, 14), (150, 190, 230))):
        sw = pygame.Surface((40, 40))
        sw.fill(swatch)
        sw.blit(tiny, (0, 0))
        big = pygame.transform.scale(sw, (120, 120))   # NEAREST upscale
        sheet.blit(big, (pad + i * (120 + 10), yb + 20))
    _label(sheet, "(40px on dark / on day-blue)", pad, yb + 20 + 122)

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

    out = os.path.join(
        ROOT, "docs/store_redesign/costume/skeleton/design_3/round_3.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
