"""Render the v2_design_1 BONEWHITE-MACAW review sheet (round_1).

ONE combined sheet proving the parrot-skeleton read: Pip mid-flight over a real
biome scene on a DAY sky and a NIGHT sky (white-on-bone must survive both), a
clean hero close-up, and a 40px NEAREST "truth read" thumbnail — the gameplay
bar the costume must clear. The two parrot tells (hooked bone beak + long bony
tail) must dominate at the 40px size.

Headless:
  SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/skeleton_candidates/render_v2_design_1.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib.util
import pygame
pygame.init()

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import hero_panel, FRAME_IDX, TILT

ROOT = "/home/user/skybit"
OUT_DIR = os.path.join(
    ROOT, "docs/store_redesign/costume/skeleton/v2/design_1")
os.makedirs(OUT_DIR, exist_ok=True)

_spec = importlib.util.spec_from_file_location(
    "v2_design_1", os.path.join(ROOT, "tools/skeleton_candidates/v2_design_1.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
build = _mod.build


def gameplay_panel_phase(source, w, h, phase):
    """ninja_render.gameplay_panel composite at an arbitrary biome phase so we
    prove the day AND night read on one sheet."""
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
    frame = source(FRAME_IDX, TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = min(int(crop_h * w / h), GW)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def truth_read_panel(source, box):
    """The bar: the in-flight frame shrunk to a 40px NEAREST thumbnail (no
    smoothing) on a 50/50 day/night split so it must read against both a bright
    and a dark gameplay backdrop."""
    panel = pygame.Surface((box, box))
    panel.fill((150, 195, 235))
    pygame.draw.rect(panel, (18, 20, 34), (box // 2, 0, box - box // 2, box))
    frame = source(FRAME_IDX, TILT)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    thumb = pygame.transform.scale(frame, (40, 40))   # NEAREST — the truth read
    panel.blit(thumb, thumb.get_rect(center=(box // 2, box // 2)))
    pygame.draw.rect(panel, (255, 255, 255), panel.get_rect(), 1)
    return panel


def labelled(surf, text, font):
    lab = font.render(text, True, (235, 238, 245))
    out = pygame.Surface((surf.get_width(),
                          surf.get_height() + 22), pygame.SRCALPHA)
    out.blit(surf, (0, 0))
    out.blit(lab, ((out.get_width() - lab.get_width()) // 2,
                   surf.get_height() + 4))
    return out


def main():
    font = pygame.font.SysFont("dejavusans", 14, bold=True)
    title_font = pygame.font.SysFont("dejavusans", 20, bold=True)

    PANEL_W, PANEL_H = 220, 300
    HERO = 240
    BAR = 200

    day = labelled(gameplay_panel_phase(build, PANEL_W, PANEL_H, 0.0),
                   "GAMEPLAY — DAY SKY", font)
    night = labelled(gameplay_panel_phase(build, PANEL_W, PANEL_H, 0.64375),
                     "GAMEPLAY — NIGHT SKY", font)
    hero = labelled(hero_panel(build, HERO, tilt=0.0, bg=(20, 20, 28)),
                    "HERO CLOSE-UP", font)
    bar = labelled(truth_read_panel(build, BAR),
                   "40px TRUTH READ (NEAREST)", font)

    pad = 24
    title_h = 44
    top_w = day.get_width() + night.get_width() + pad
    bot_w = hero.get_width() + bar.get_width() + pad
    sheet_w = max(top_w, bot_w, 540) + pad * 2
    sheet_h = (title_h + day.get_height() + pad
               + max(hero.get_height(), bar.get_height()) + pad * 2)

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 30, 38))
    title = title_font.render(
        "SKELETON v2 — design_1  BONEWHITE-MACAW  (round 1)",
        True, (255, 255, 255))
    sheet.blit(title, (pad, 14))

    y = title_h
    x = (sheet_w - top_w) // 2
    sheet.blit(day, (x, y))
    sheet.blit(night, (x + day.get_width() + pad, y))

    y += day.get_height() + pad
    x = (sheet_w - bot_w) // 2
    sheet.blit(hero, (x, y))
    sheet.blit(bar, (x + hero.get_width() + pad, y))

    out = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
