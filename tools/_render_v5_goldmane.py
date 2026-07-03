"""Headless review-sheet render for GOLDMANE (viking palette v5).

Builds ONE labeled sheet: hero_panel + gameplay_panel + a NEAREST 40px truth
read x3 on BOTH day and night. Scratch-only; touches no production art.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib.util
import pygame
pygame.init()

from game import biome
from game.draw import get_sky_surface_biome
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import hero_panel, gameplay_panel

_spec = importlib.util.spec_from_file_location(
    "v5_goldmane", os.path.join(os.path.dirname(__file__),
                                "viking_palette_candidates", "v5.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BUILD = _mod.build

FONT = pygame.font.SysFont("dejavusans", 15, bold=True)
SMALL = pygame.font.SysFont("dejavusans", 12)


def _label(surf, x, y, text, col=(235, 230, 220)):
    surf.blit(SMALL.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(SMALL.render(text, True, col), (x, y))


def _truth_tile(phase, frame_idx, tilt, box=120):
    """A 40px NEAREST-scaled bird over a real biome sky at `phase`, then the
    whole tile nearest-upscaled so the reviewer sees exactly the runtime pixels."""
    pal = biome.palette_for_phase(phase)
    cell = pygame.Surface((40, 40))
    sky = get_sky_surface_biome(GW, GH, GROUND_Y, pal, 0)
    cell.blit(pygame.transform.scale(sky.subsurface((140, 240, 80, 80)).copy(), (40, 40)), (0, 0))
    frame = BUILD(frame_idx, tilt)
    small = pygame.transform.smoothscale(frame, (40, 40))
    cell.blit(small, (0, 0))
    return pygame.transform.scale(cell, (box, box))


def main():
    W, H = 1180, 720
    sheet = pygame.Surface((W, H))
    sheet.fill((28, 26, 24))

    title = FONT.render(
        "GOLDMANE — Viking palette v5 (plain fair-haired northman, de-frosted design_4)",
        True, (240, 224, 188))
    sheet.blit(title, (24, 16))

    # Hero shot (large product read).
    hero = hero_panel(BUILD, 300, bg=(30, 28, 40))
    sheet.blit(hero, (24, 50))
    _label(sheet, 24, 352, "HERO  (store-card product shot)")

    # Gameplay panel (day biome, in-scene).
    gp = gameplay_panel(BUILD, 250, 360)
    sheet.blit(gp, (344, 50))
    _label(sheet, 344, 414, "GAMEPLAY  (day biome, mid-flight)")

    # 40px NEAREST truth reads, day + night, three poses each.
    poses = [(0, 0.0), (2, 10.0), (3, -14.0)]
    x0 = 680
    for col, (fi, tl) in enumerate(poses):
        tx = x0 + col * 130
        sheet.blit(_truth_tile(0.0, fi, tl), (tx, 50))
        sheet.blit(_truth_tile(0.62, fi, tl), (tx, 200))
    _label(sheet, x0, 172, "40px DAY  (frame 0 / 2 / 3)")
    _label(sheet, x0, 322, "40px NIGHT (frame 0 / 2 / 3)")

    notes = [
        "DE-FROST: icicle beard -> plain braid tips + 1 gold ring;",
        "shield frost-crystals -> plain wood planks + iron boss/rim + gold rivets;",
        "horn tips bone/metal (not frost); brim drip dropped; ice flecks -> metal glints.",
        "Plain tan/blonde, not gilded jarl. Warm-brown keyline #2E2214 holds the day read.",
    ]
    for i, n in enumerate(notes):
        _label(sheet, 24, 470 + i * 22, n, (210, 200, 184))

    out = os.path.join(os.path.dirname(__file__), "..", "docs", "store_redesign",
                       "costume", "viking", "palette", "v5", "round_1.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("WROTE", out)


if __name__ == "__main__":
    main()
