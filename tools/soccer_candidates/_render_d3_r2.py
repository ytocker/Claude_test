"""Round-2 review sheet for SOCCER DESIGN 3 — THE NÚMERO 10.

Renders the revised builder four ways the art-director judges it: a big HERO
NEAREST product shot, an in-gameplay shot, and the two 40px-in-motion reads
(day + night) that decide whether a skin lives. Writes the combined sheet to
docs/store_redesign/costume/soccer/design_3/round_2.png — scratch only.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

import importlib.util
import pygame.freetype

from game import parrot, biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import gameplay_panel, hero_panel

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("soccer_d3", os.path.join(HERE, "design_3.py"))
d3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d3)
build = d3.build

OUT = "/home/user/skybit/docs/store_redesign/costume/soccer/design_3/round_2.png"

# NEAREST hero so the pixels are judged as authored (no smoothing softening the
# collar/number reads); the 40px tiles use the real in-game smoothscale path.
FRAME_IDX, TILT = 2, 8.0


def _hero_nearest(box, bg):
    frame = build(FRAME_IDX, 0.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = int(max(1, (box * 0.78) / max(sw, sh)))
    frame = pygame.transform.scale(frame, (sw * scale, sh * scale))
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, bg, panel.get_rect(), border_radius=14)
    panel.blit(frame, frame.get_rect(center=(box // 2, box // 2)))
    return panel


def _scene_with(palette, clouds_day=True):
    scene = pygame.Surface((GW, GH))
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, v in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=v)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    return scene


def _forty_px(palette):
    """The skin as it ships: a real biome scene, the bird rendered then scaled
    so the body footprint is ~40px wide, on a tile."""
    scene = _scene_with(palette)
    frame = build(FRAME_IDX, TILT)
    # Scale the parrot down so its visible body reads at ~40px wide in the tile.
    bb = frame.get_bounding_rect()
    crop = frame.subsurface(bb).copy()
    target_w = 44
    sc = target_w / crop.get_width()
    small = pygame.transform.smoothscale(
        crop, (int(crop.get_width() * sc), int(crop.get_height() * sc)))
    pip_cx, pip_cy = 96, 250
    tile = scene.copy()
    tile.blit(small, small.get_rect(center=(pip_cx, pip_cy)))
    crop_r = pygame.Rect(0, 0, 150, 168)
    crop_r.center = (pip_cx + 6, pip_cy - 6)
    crop_r.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return tile.subsurface(crop_r).copy()


def main():
    pygame.freetype.init()
    font = pygame.freetype.SysFont("DejaVu Sans", 15)
    fontb = pygame.freetype.SysFont("DejaVu Sans", 19)

    W, H = 1040, 560
    sheet = pygame.Surface((W, H))
    sheet.fill((26, 24, 36))
    fontb.render_to(sheet, (20, 18),
                    "SOCCER · DESIGN 3 — THE NUMERO 10   (round 2 · chest collar fix)",
                    (236, 238, 246))

    day = biome.palette_for_phase(0.0)
    night = biome.palette_for_phase(0.5125)

    # Big HERO NEAREST on the left.
    hero = _hero_nearest(330, (22, 20, 32))
    sheet.blit(hero, (20, 55))
    font.render_to(sheet, (20, 392), "HERO (nearest)", (210, 212, 222))

    # In-gameplay product shot (portrait crop ratio the harness expects).
    gp = gameplay_panel(build, 228, 330)
    sheet.blit(gp, (406, 55))
    font.render_to(sheet, (406, 392), "IN GAMEPLAY", (210, 212, 222))

    # 40px day + night tiles on the right.
    d_tile = pygame.transform.scale(_forty_px(day), (150, 168))
    n_tile = pygame.transform.scale(_forty_px(night), (150, 168))
    sheet.blit(d_tile, (700, 55))
    font.render_to(sheet, (700, 230), "40px DAY", (210, 212, 222))
    sheet.blit(n_tile, (860, 55))
    font.render_to(sheet, (860, 230), "40px NIGHT", (210, 212, 222))

    font.render_to(sheet, (700, 270),
                   "Read check:", (235, 225, 150))
    for i, line in enumerate([
        "- collar = chest V at",
        "  neckline, NOT face",
        "- gold lace rungs inside",
        "- bold '10' legible",
        "- sky-blue sleeve + cuff",
        "- one sock fold-over hoop",
    ]):
        font.render_to(sheet, (700, 296 + i * 22), line, (198, 200, 210))

    pygame.image.save(sheet, OUT)
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
