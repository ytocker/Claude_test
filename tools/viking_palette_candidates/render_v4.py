"""Compose the WOADGREEN (v4) review sheet.

hero + gameplay (day + night) + a NEAREST 40px truth read magnified 3x on BOTH
a day and a night sky. Headless:
  SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python <this>.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render
from tools.viking_palette_candidates.v4 import build

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

OUT = "docs/store_redesign/costume/viking/palette/v4/round_2.png"
TITLE = "VIKING PALETTE v4 — WOADGREEN  (woad-painted forest raider)"

# Night phase from biome.py's keyframe table (NIGHT keyframe).
NIGHT_PHASE = 0.64375


def _label(surf, text, x, y, size=18, color=(232, 240, 220)):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf.blit(font.render(text, True, color), (x, y))


def _gameplay(source, w, h, phase):
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
    frame = source(ninja_render.FRAME_IDX, ninja_render.TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _truth_read(box):
    """40px-in-motion test: NEAREST-shrink the bird to ~40px, then magnify 3x on
    day | night swatches so the reviewer judges the real on-screen read."""
    frame = build(ninja_render.FRAME_IDX, ninja_render.TILT)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40.0 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    tile = pygame.Surface((48, 48), pygame.SRCALPHA)
    panel = pygame.Surface((box, box))
    panel.fill((28, 32, 24))
    half = box // 2
    pygame.draw.rect(panel, (150, 200, 235), (0, 0, half, box))        # day sky
    pygame.draw.rect(panel, (14, 20, 18), (half, 0, box - half, box))  # night sky
    for ox in (half // 2 - 20, half + half // 2 - 20):
        t = tile.copy()
        t.blit(small, small.get_rect(center=(24, 24)))
        big = pygame.transform.scale(t, (48 * 3, 48 * 3))
        panel.blit(big, big.get_rect(center=(ox + 20, box // 2 + 8)))
    return panel


def main():
    box = 360
    gw = int(box * 9 / 16)
    hero = ninja_render.hero_panel(build, box)
    gp_day = _gameplay(build, gw, box, 0.0)
    gp_night = _gameplay(build, gw, box, NIGHT_PHASE)
    truth = _truth_read(box)

    pad = 18
    head = 56
    cap = 30
    widths = [box, gw, gw, box]
    W = pad * (len(widths) + 1) + sum(widths)
    H = head + box + cap + pad
    sheet = pygame.Surface((W, H))
    sheet.fill((20, 26, 16))
    _label(sheet, TITLE, pad, 16, size=22)

    xs, x = [], pad
    for w in widths:
        xs.append(x)
        x += w + pad
    y = head
    for x, panel in zip(xs, (hero, gp_day, gp_night, truth)):
        sheet.blit(panel, (x, y))
    for x, name in zip(xs, ("HERO PRODUCT SHOT", "IN-GAMEPLAY (day)",
                            "IN-GAMEPLAY (night)",
                            "40px TRUTH READ  (day | night, 3x)")):
        _label(sheet, name, x, y + box + 6, size=15, color=(196, 210, 176))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
