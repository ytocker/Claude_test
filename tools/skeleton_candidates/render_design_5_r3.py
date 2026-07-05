"""Render the AUREX (design_5) review sheet — scratch exploration only.

One sheet: day-sky gameplay (gold must read with near-zero glow assist),
night-sky gameplay (violet rune-fire blazes), a hero close-up, a 40px NEAREST
"truth read" (must clock GOLD SKULL → two violet socket points → gold crown),
and a 4-frame flap filmstrip. Day uses the near-silent-glow variant, night the
blazing one, so the day/night glow gating is honestly shown.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud,
)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

from tools.ninja_render import hero_panel
from tools.skeleton_candidates.design_5 import build_day, build_night

OUT = "docs/store_redesign/costume/skeleton/design_5/round_3.png"

FRAME_IDX = 2
TILT = 10.0
BONE = (255, 226, 122)
LABEL = (236, 230, 245)


def _gameplay_panel(source, w, h, phase, *, frame_idx=FRAME_IDX, tilt=TILT):
    """Pip mid-flight over a real biome scene at a given day-cycle phase, so
    the night panel actually renders under a dark sky with the rune-fire lit."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    bucket = int(round(phase * 64))
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, bucket), (0, 0))
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
    crop_w = min(crop_w, GW)
    crop_h = min(crop_h, GH)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _truth_read(source, box):
    """The 40px NEAREST downscale — must clock GOLD SKULL → two violet socket
    points → gold crown, gold the brightest legible mass."""
    frame = source(FRAME_IDX, 0.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    s = 40 / max(sw, sh)
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * s)), max(1, int(sh * s))))
    big = pygame.transform.scale(small, (box, box))   # NEAREST upscale
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, (22, 20, 32), panel.get_rect(), border_radius=10)
    panel.blit(big, big.get_rect(center=(box // 2, box // 2)))
    return panel


def _filmstrip(source, cell, n=4):
    """The 4 flap poses side by side — the gold wing sweeping; on the night
    variant a faint violet trail rides the swept-up poses."""
    strip = pygame.Surface((cell * n, cell), pygame.SRCALPHA)
    for i in range(n):
        pygame.draw.rect(strip, (20, 17, 30),
                         (i * cell + 2, 2, cell - 4, cell - 4), border_radius=8)
        frame = source(i, 0.0)
        bb = frame.get_bounding_rect()
        if bb.width and bb.height:
            frame = frame.subsurface(bb).copy()
        sw, sh = frame.get_size()
        s = (cell * 0.8) / max(sw, sh)
        f = pygame.transform.smoothscale(
            frame, (max(1, int(sw * s)), max(1, int(sh * s))))
        strip.blit(f, f.get_rect(center=(i * cell + cell // 2, cell // 2)))
    return strip


def _label(sheet, font, text, x, y):
    sheet.blit(font.render(text, True, LABEL), (x, y))


def main():
    pygame.font.init()
    small = pygame.font.SysFont("dejavusans", 13)

    pad = 18
    gp_w, gp_h = 240, 300        # gameplay panels
    hero = 300
    truth = 140
    cell = 132

    title_h = 54
    row1_h = max(gp_h, hero)
    strip_h = cell + 30
    sheet_w = pad * 4 + gp_w * 2 + hero
    sheet_h = title_h + row1_h + pad + max(truth, strip_h) + pad * 2 + 40

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((16, 14, 22))

    # Title.
    sheet.blit(pygame.font.SysFont("dejavusans", 26, bold=True).render(
        "SKELETON — design_5  AUREX  (cursed gold-lich)  round 3 (final)", True, BONE),
        (pad, 12))

    y0 = title_h
    # Day gameplay — gold carries, glow near-silent.
    day = _gameplay_panel(build_day, gp_w, gp_h, 0.0)
    sheet.blit(day, (pad, y0))
    _label(sheet, small, "gameplay — DAY sky (gold carries, glow near-silent)",
           pad + 4, y0 + gp_h + 2)

    # Night gameplay (rune-fire blazes).
    x1 = pad * 2 + gp_w
    night = _gameplay_panel(build_night, gp_w, gp_h, 0.64375)
    sheet.blit(night, (x1, y0))
    _label(sheet, small, "gameplay — NIGHT sky (violet rune-fire blazes)",
           x1 + 4, y0 + gp_h + 2)

    # Hero close-up (night variant for the showpiece detail).
    x2 = pad * 3 + gp_w * 2
    sheet.blit(hero_panel(build_night, hero, tilt=0.0, bg=(20, 16, 28)), (x2, y0))
    _label(sheet, small, "hero close-up", x2 + 4, y0 + hero + 2)

    # Second row: truth read (day variant — the honest 40px gold-first read)
    # plus the filmstrip (night variant for the wing trail).
    y1 = y0 + row1_h + pad + 18
    sheet.blit(_truth_read(build_day, truth), (pad, y1))
    _label(sheet, small, "40px truth read — GOLD SKULL > violet points > crown",
           pad + 4, y1 + truth + 2)

    xs = pad * 2 + truth
    sheet.blit(_filmstrip(build_night, cell), (xs, y1))
    _label(sheet, small, "4-frame flap filmstrip — gold wing + violet trail",
           xs + 4, y1 + cell + 2)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("wrote", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
