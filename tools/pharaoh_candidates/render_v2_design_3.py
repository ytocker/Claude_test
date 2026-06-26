"""Compose the OSIRIS review sheet (hero + gameplay + 40px truth read).

Headless: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
PYTHONPATH=/home/user/skybit python tools/pharaoh_candidates/render_v2_design_3.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render
from tools.pharaoh_candidates.v2_design_3 import build

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

OUT = "docs/store_redesign/costume/pharaoh/v2_design_3/round_2.png"
TITLE = "v2 DESIGN 3 — OSIRIS  round 2"


def _gameplay_overlap(w, h):
    """The make-or-break read: Pip composited so his green body physically
    OVERLAPS a green pillar (and a leafy bush), to prove the teal recolor +
    dark rim separate from Skybit's foliage rather than camouflaging into it."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.0)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (240, 60, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    # A pillar planted right where the bird flies so its body laps the green edge.
    Pipe(x=70, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=230, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    # Bird centred over the left pillar's stone so its silhouette overlaps green.
    pip_cx, pip_cy = 96, 255
    frame = build(ninja_render.FRAME_IDX, ninja_render.TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 30, pip_cy - 16)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _label(surf, text, x, y, size=18, color=(236, 238, 246)):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf.blit(font.render(text, True, color), (x, y))


def _truth_read(box):
    """The 40px-in-motion test: render the bird, NEAREST-shrink to a ~40px bird
    then magnify 3x so the reviewer judges the real on-screen read — on a day sky
    half and a night sky half so the green body + white Atef are judged on both."""
    frame = build(ninja_render.FRAME_IDX, ninja_render.TILT)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40.0 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    tile = pygame.Surface((48, 48), pygame.SRCALPHA)
    panel = pygame.Surface((box, box))
    panel.fill((30, 28, 40))
    half = box // 2
    pygame.draw.rect(panel, (150, 200, 235), (0, 0, half, box))        # day sky
    pygame.draw.rect(panel, (12, 14, 30), (half, 0, box - half, box))  # night sky
    for i, ox in enumerate((half // 2 - 20, half + half // 2 - 20)):
        t = tile.copy()
        t.blit(small, small.get_rect(center=(24, 24)))
        big = pygame.transform.scale(t, (48 * 3, 48 * 3))
        panel.blit(big, big.get_rect(center=(ox + 20, box // 2 + 8)))
    return panel


def main():
    box = 360
    gw = int(box * 9 / 16)
    hero = ninja_render.hero_panel(build, box)
    gameplay = _gameplay_overlap(gw, box)
    truth = _truth_read(box)

    pad = 18
    head = 56
    cap = 30
    widths = [box, gw, box]
    W = pad * (len(widths) + 1) + sum(widths)
    H = head + box + cap + pad
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 17, 26))
    _label(sheet, TITLE, pad, 16, size=22)

    xs = []
    x = pad
    for w in widths:
        xs.append(x)
        x += w + pad
    y = head
    for x, panel in zip(xs, (hero, gameplay, truth)):
        sheet.blit(panel, (x, y))
    for x, name in zip(xs, ("HERO PRODUCT SHOT",
                            "IN-GAMEPLAY (body OVERLAPS green pillar)",
                            "40px TRUTH READ  (day | night, 3x)")):
        _label(sheet, name, x, y + box + 6, size=15, color=(190, 194, 210))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
