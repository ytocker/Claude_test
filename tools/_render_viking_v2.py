"""Headless review-sheet builder for the BLOODAXE viking-palette candidate (v2).

Scratch-only. Renders the candidate the same way the ninja harness does
(hero + gameplay over a real biome), plus a NEAREST 40px truth read x3 on BOTH
day and night, onto one labeled sheet. Not shipped.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib.util
import pygame
pygame.init()

from game import biome
from game.draw import (get_sky_surface_biome, draw_mountains, draw_ground,
                       draw_cloud)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import hero_panel, FRAME_IDX, TILT

# Load the candidate builder.
_spec = importlib.util.spec_from_file_location(
    "viking_v2", "/home/user/skybit/tools/viking_palette_candidates/v2.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
build = _mod.build

DAY_PHASE = 0.0
NIGHT_PHASE = 0.644


def gameplay_panel_phase(source, w, h, phase):
    """ninja_render.gameplay_panel, but at an arbitrary biome phase."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2),
                                (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'],
                   palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0, palette['ground_top'],
                palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = build(FRAME_IDX, TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = min(GH, int(GH * 0.78))
    crop_w = min(GW, int(crop_h * w / h))
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def truth40(phase, bg):
    """A 40px NEAREST downscale of the bird on a flat biome-tinted swatch —
    the at-size truth read."""
    frame = build(FRAME_IDX, TILT)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy() if bb.width else frame
    sw, sh = frame.get_size()
    scale = 40 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    tile = pygame.Surface((56, 56))
    tile.fill(bg)
    tile.blit(small, small.get_rect(center=(28, 28)))
    return tile


def label(surf, text, x, y, color=(235, 235, 240), size=18):
    f = pygame.font.SysFont("dejavusans", size, bold=True)
    t = f.render(text, True, color)
    sh = f.render(text, True, (0, 0, 0))
    surf.blit(sh, (x + 1, y + 1))
    surf.blit(t, (x, y))


def main():
    W, H = 880, 620
    sheet = pygame.Surface((W, H))
    sheet.fill((24, 22, 30))
    label(sheet, "VIKING PALETTE v2 — BLOODAXE (warm rust/red raider)",
          16, 12, (255, 210, 180), 22)
    label(sheet, "round 2 — darker shield disc + proud iron rim + single stud "
          "+ brighter fur tuft", 16, 40, (180, 180, 190), 15)

    # Hero shots on day + night cards.
    hero_day = hero_panel(build, 230, frame_idx=FRAME_IDX, tilt=0.0,
                          bg=(34, 30, 40))
    hero_night = hero_panel(build, 230, frame_idx=FRAME_IDX, tilt=0.0,
                            bg=(14, 16, 30))
    sheet.blit(hero_day, (16, 70))
    sheet.blit(hero_night, (16, 320))
    label(sheet, "HERO / day card", 22, 74)
    label(sheet, "HERO / night card", 22, 324)

    # Gameplay panels day + night.
    gp_day = gameplay_panel_phase(build, 300, 230, DAY_PHASE)
    gp_night = gameplay_panel_phase(build, 300, 230, NIGHT_PHASE)
    sheet.blit(gp_day, (262, 70))
    sheet.blit(gp_night, (262, 320))
    label(sheet, "GAMEPLAY / day", 268, 74)
    label(sheet, "GAMEPLAY / night", 268, 324)

    # 40px NEAREST truth reads x3, day and night.
    day_bgs = [(118, 178, 222), (150, 200, 230), (90, 160, 210)]   # day sky tones
    night_bgs = [(28, 30, 60), (40, 36, 70), (18, 22, 48)]         # night tones
    tx = 580
    label(sheet, "40px NEAREST truth read", tx, 74, size=15)
    label(sheet, "DAY x3", tx, 96, (190, 220, 245), 14)
    for i, bg in enumerate(day_bgs):
        sheet.blit(truth40(DAY_PHASE, bg), (tx + i * 64, 118))
    label(sheet, "NIGHT x3", tx, 184, (170, 180, 230), 14)
    for i, bg in enumerate(night_bgs):
        sheet.blit(truth40(NIGHT_PHASE, bg), (tx + i * 64, 206))

    # Material swatch legend.
    label(sheet, "MATERIALS", tx, 290, size=15)
    swatches = [
        ("rust plumage", _mod.RUST_BODY), ("rust shadow", _mod.RUST_DARK),
        ("iron helm", _mod.IRON), ("iron hi", _mod.IRON_HI),
        ("dark fur", _mod.FUR), ("fur hi", _mod.FUR_HI),
        ("beard", _mod.BEARD), ("beard rings", _mod.RING_IRON),
        ("shield red", _mod.SHIELD_RED), ("brass studs", _mod.BRASS),
        ("bone horn", _mod.BONE), ("keyline", _mod.KEYLINE[:3]),
    ]
    for i, (nm, col) in enumerate(swatches):
        yy = 314 + i * 24
        pygame.draw.rect(sheet, col, (tx, yy, 20, 18))
        pygame.draw.rect(sheet, (90, 90, 100), (tx, yy, 20, 18), 1)
        label(sheet, nm, tx + 28, yy - 1, (210, 210, 215), 13)

    out = "/home/user/skybit/docs/store_redesign/costume/viking/palette/v2/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
