"""Round-1 review sheet for v3_design_2 · X-RAY.

Headless: SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/skeleton_candidates/_render_v3_design_2.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import parrot, biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import hero_panel
from tools.skeleton_candidates.v3_design_2 import build as XRAY


def _scene_panel(source, w, h, phase, *, frame_idx=2, tilt=10.0):
    """Pip mid-flight over a real biome scene at the given day/night phase."""
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
    frame = source(frame_idx, tilt) if callable(source) else \
        parrot.get_skin_frame(source, frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_w = min(int(GW * 0.92), GW)
    crop_h = min(int(crop_w * h / w), GH)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _label(sheet, font, text, x, y, color=(235, 238, 246)):
    sheet.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    sheet.blit(font.render(text, True, color), (x, y))


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    M = 16
    sw, sh = 240, 300          # scene panels
    hb = 300                   # hero box
    sheet_w = M + sw + M + sw + M + hb + M
    sheet_h = 760
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 21, 28))

    y0 = 46
    _label(sheet, font, "v3_design_2 · X-RAY — full skeleton (Round 1)", M, 14)

    # DAY + NIGHT gameplay scenes.
    sheet.blit(_scene_panel(XRAY, sw, sh, 0.0), (M, y0))
    _label(sheet, small, "GAMEPLAY · DAY", M + 6, y0 + sh - 22)
    sheet.blit(_scene_panel(XRAY, sw, sh, 0.5), (M + sw + M, y0))
    _label(sheet, small, "GAMEPLAY · NIGHT", M + sw + M + 6, y0 + sh - 22)

    # Hero product shot.
    hx = M + sw + M + sw + M
    sheet.blit(hero_panel(XRAY, hb), (hx, y0))
    _label(sheet, small, "HERO", hx + 6, y0 + hb - 22)

    # ── bottom row: 40px truth read, filmstrip, original reference.
    y1 = y0 + sh + 30
    _label(sheet, font, "40px truth read · 4-frame flap filmstrip · original ref", M, y1 - 22)

    # 40px NEAREST upscaled truth read (day + night bg behind it).
    for i, (bg, lab) in enumerate(((( 60, 130, 210), "40px DAY"),
                                   ((18, 22, 44), "40px NIGHT"))):
        f40 = pygame.transform.smoothscale(XRAY(2, 0.0), (40, 40))
        big = pygame.transform.scale(f40, (160, 160))   # NEAREST
        tile = pygame.Surface((160, 184))
        tile.fill(bg)
        tile.blit(big, (0, 0))
        _label(tile, small, lab, 6, 162)
        sheet.blit(tile, (M + i * (160 + 12), y1))

    # 4-frame flap filmstrip (verify wing bones rotate with the flap).
    fx = M + 2 * (160 + 12) + 14
    for fi in range(4):
        f = XRAY(fi, 0.0)
        cell = pygame.Surface((92, 160), pygame.SRCALPHA)
        cell.fill((30, 32, 42))
        b = f.get_bounding_rect()
        fc = f.subsurface(b).copy() if b.width else f
        s = (88 * 0.92) / max(fc.get_width(), fc.get_height())
        fc = pygame.transform.smoothscale(
            fc, (max(1, int(fc.get_width() * s)), max(1, int(fc.get_height() * s))))
        cell.blit(fc, fc.get_rect(center=(46, 78)))
        _label(cell, small, f"f{fi}", 4, 142)
        sheet.blit(cell, (fx + fi * 96, y1))

    # Live ORIGINAL parrot (sid "default") — silhouette-fidelity reference.
    orig = hero_panel("default", 184, bg=(34, 30, 44))
    ox = sheet_w - M - 184
    sheet.blit(orig, (ox, y1))
    _label(sheet, small, "ORIGINAL Pip (ref)", ox + 6, y1 + 184 - 22)

    out = "docs/store_redesign/costume/skeleton/v3/design_2/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
