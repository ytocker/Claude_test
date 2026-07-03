"""Render PIP THE SKEETER (mosquito design_5) to a labeled review sheet:
a clean hero product-shot + an in-gameplay day crop + an in-gameplay NIGHT crop
(genuinely dark sky, dive pose) so the chibi read is judgeable at gameplay
scale on both skies. Headless."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.font.init()

from tools.ninja_render import hero_panel, _frame
from tools.mosquito_candidates.design_5 import build
from game import biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud,
)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

OUT = "/home/user/skybit/docs/store_redesign/animal/mosquito/design_5/round_1.png"

DAY_PHASE = 0.0
NIGHT_PHASE = 0.64375   # the NIGHT keyframe — sky_top ~ (5,8,30), truly dark


def _gameplay_panel(phase, w, h, *, frame_idx=2, tilt=10.0):
    """Pip (mid-flight) over a real biome scene at the given day/night phase,
    cropped around the bird and scaled to (w, h). Mirrors ninja_render but lets
    the sky phase vary so we get an honest night read."""
    scene = pygame.Surface((GW, GH))
    pal = biome.palette_for_phase(phase)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, pal,
                                     biome.phase_bucket(phase)), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2),
                                (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, pal['mtn_far'], pal['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, pal)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, pal)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                pal['ground_top'], pal['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = _frame(build, frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _font(sz, bold=True):
    return pygame.font.SysFont("Arial", sz, bold=bold)


def _label(surf, text, x, y, sz=18, col=(240, 240, 245)):
    surf.blit(_font(sz).render(text, True, col), (x, y))


def main():
    PAD = 18
    HERO = 300
    GPW, GPH = 220, 392
    top = 84

    hero = hero_panel(build, HERO, frame_idx=2, tilt=0.0)
    day = _gameplay_panel(DAY_PHASE, GPW, GPH, frame_idx=2, tilt=10.0)
    night = _gameplay_panel(NIGHT_PHASE, GPW, GPH, frame_idx=0, tilt=-8.0)

    W = PAD * 4 + HERO + GPW * 2
    H = top + max(HERO, GPH) + PAD + 26
    sheet = pygame.Surface((W, H))
    sheet.fill((24, 22, 32))

    _label(sheet, "DESIGN 5 — PIP THE SKEETER  ·  skin_mosquito_cutie (kawaii/chibi)",
           PAD, 20, sz=24, col=(255, 255, 255))
    _label(sheet, "GIANT glossy eye · cute straw proboscis · plump mint body + yellow bands · short springy legs · soft leaf wings",
           PAD, 52, sz=14, col=(175, 180, 195))

    sheet.blit(hero, (PAD, top))
    _label(sheet, "HERO (detail)", PAD + 6, top + HERO - 26, sz=15)

    x2 = PAD * 2 + HERO
    sheet.blit(day, (x2, top))
    _label(sheet, "GAMEPLAY (day)", x2 + 6, top + GPH - 26, sz=15)

    x3 = PAD * 3 + HERO + GPW
    sheet.blit(night, (x3, top))
    _label(sheet, "GAMEPLAY (night)", x3 + 6, top + GPH - 26, sz=15)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
