"""Render the DESIGN 1 — MIDNIGHT WHINE review sheet (hero | day | night)."""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

import pygame

pygame.init()

import tools.ninja_render as nr
from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.mosquito_candidates.design_1 import build

NIGHT_PHASE = 0.64375   # NIGHT keyframe — moonlit cool stone + stars


def night_panel(source, w, h, *, frame_idx=2, tilt=10.0):
    """Same composition as ninja_render.gameplay_panel but under the NIGHT
    biome palette, to prove the dark indigo body still reads against a dark
    sky (that's the whole reason for the outline pass)."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(NIGHT_PHASE)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette,
                                     int(palette['star_alpha'])), (0, 0))
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
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def strip_frames(box=96, bg=(16, 15, 26)):
    """The four flap frames side by side to prove the wings + sheen animate."""
    surf = pygame.Surface((box * 4, box), pygame.SRCALPHA)
    for i in range(4):
        cell = pygame.Surface((box, box), pygame.SRCALPHA)
        pygame.draw.rect(cell, bg, cell.get_rect(), border_radius=10)
        fr = build(i, 0.0)
        bb = fr.get_bounding_rect()
        if bb.width and bb.height:
            fr = fr.subsurface(bb).copy()
        sw, sh = fr.get_size()
        sc = (box * 0.86) / max(sw, sh)
        fr = pygame.transform.smoothscale(
            fr, (max(1, int(sw * sc)), max(1, int(sh * sc))))
        cell.blit(fr, fr.get_rect(center=(box // 2, box // 2)))
        surf.blit(cell, (i * box, 0))
    return surf


def main():
    PW, PH = 220, 392
    hero = nr.hero_panel(build, PH, tilt=0.0)          # square product shot
    day = nr.gameplay_panel(build, PW, PH)
    night = night_panel(build, PW, PH)
    strip = strip_frames()

    pad, top = 20, 66
    labels_h = 28
    grid_w = pad + PH + pad + PW + pad + PW + pad
    grid_h = top + PH + labels_h + pad + strip.get_height() + labels_h + pad
    sheet = pygame.Surface((grid_w, grid_h))
    sheet.fill((24, 22, 34))

    title_font = pygame.font.SysFont("arial", 30, bold=True)
    lab_font = pygame.font.SysFont("arial", 20, bold=True)
    sub_font = pygame.font.SysFont("arial", 15)

    t = title_font.render("DESIGN 1 — MIDNIGHT WHINE", True, (94, 200, 229))
    sheet.blit(t, (pad, 20))
    s = sub_font.render("dark elegant mosquito · long proboscis needle · single magenta compound eye",
                        True, (150, 158, 190))
    sheet.blit(s, (pad, 48))

    xs = [pad, pad + PH + pad, pad + PH + pad + PW + pad]
    for x, panel, name in ((xs[0], hero, "HERO"),
                           (xs[1], day, "GAMEPLAY · DAY"),
                           (xs[2], night, "GAMEPLAY · NIGHT")):
        sheet.blit(panel, (x, top))
        lab = lab_font.render(name, True, (230, 232, 245))
        sheet.blit(lab, (x, top + PH + 4))

    sy = top + PH + labels_h + pad
    sheet.blit(strip, (pad, sy))
    lab = lab_font.render("FLAP CYCLE (4 frames) — wing sweep + travelling teal→violet sheen",
                          True, (230, 232, 245))
    sheet.blit(lab, (pad, sy + strip.get_height() + 4))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "docs", "store_redesign", "animal",
        "mosquito", "design_1")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
