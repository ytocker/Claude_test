"""Compose the NEON SEVER review sheet (hero + night-hero + in-gameplay +
40px truth read) and save it to docs/store_redesign/costume/ninja/design_5/.

Scratch only — renders the unregistered candidate builder via the shared
ninja_render harness. Run headless:
  SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python tools/ninja_candidates/render_5.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools.ninja_render import gameplay_panel, hero_panel
from tools.ninja_candidates.design_5 import build

from game import biome
from game.draw import (get_sky_surface_biome, draw_mountains, draw_ground,
                       draw_cloud)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y


def night_gameplay_panel(source, w, h):
    """Mirror of ninja_render.gameplay_panel but on the NIGHT biome palette,
    since neon edge-glow + the energy blade pop hardest against dark sky —
    the context this skin is tuned for. Same scene geometry / crop as the day
    panel so the two read as the same shot under two lights."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.64375)   # NIGHT keyframe
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2),
                                (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'],
                   palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = source(2, 10.0)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))

FONT = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
OUT = "/home/user/skybit/docs/store_redesign/costume/ninja/design_5/round_1.png"

BG = (16, 17, 24)
INK = (236, 240, 250)
SUB = (150, 156, 172)
ACCENT = (25, 224, 255)


def _label(sheet, text, x, y, size=20, color=INK):
    f = pygame.font.Font(FONT, size)
    sheet.blit(f.render(text, True, color), (x, y))


def _truth_read(box):
    """The '40px truth read': render the bird small, downscale to 40px with
    NEAREST neighbour (no smoothing — the honest in-flight pixel read), then
    magnify 3x, again NEAREST, so the reviewer sees exactly what survives."""
    frame = build(2, 10.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    big = pygame.transform.scale(small, (small.get_width() * 3,
                                         small.get_height() * 3))
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, (8, 9, 14), panel.get_rect(), border_radius=14)
    panel.blit(big, big.get_rect(center=(box // 2, box // 2)))
    return panel


def main():
    pygame.font.init()
    W, H = 980, 760
    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    _label(sheet, "NEON SEVER", 28, 22, 36, INK)
    _label(sheet, "Cyber-Kunoichi  ·  LEGENDARY  ·  ninja redesign / design_5",
           30, 64, 18, ACCENT)
    pygame.draw.line(sheet, (40, 44, 58), (28, 96), (W - 28, 96), 2)

    pad = 28
    top = 116

    # Hero on the standard navy product panel.
    hp = hero_panel(build, 300)
    sheet.blit(hp, (pad, top))
    _label(sheet, "HERO  ·  product panel", pad, top + 304, 16, SUB)

    # Hero on a near-black NIGHT panel — neon pops hardest here.
    night = hero_panel(build, 300, bg=(6, 7, 12))
    sheet.blit(night, (pad * 2 + 300, top))
    _label(sheet, "HERO  ·  near-black night sky", pad * 2 + 300, top + 304,
           16, SUB)

    # 40px truth read (NEAREST shrink, magnified 3x).
    tr = _truth_read(300)
    sheet.blit(tr, (pad * 3 + 600, top))
    _label(sheet, "40px TRUTH READ  ·  3x nearest", pad * 3 + 600, top + 304,
           16, SUB)

    # In-gameplay panels over the daytime AND night biome (the harness scene).
    # Kept near the 360x640 canvas aspect so the harness crop stays inside the
    # surface. Night is the headline read — this is where the neon lives.
    gp_y = top + 340
    gw, gh = 180, 260
    gp_day = gameplay_panel(build, gw, gh)
    sheet.blit(gp_day, (pad, gp_y))
    pygame.draw.rect(sheet, (40, 44, 58), (pad, gp_y, gw, gh), 2,
                     border_radius=6)
    _label(sheet, "IN-GAMEPLAY  ·  daytime biome", pad, gp_y + gh + 6, 16, SUB)

    gp_night = night_gameplay_panel(build, gw, gh)
    nx = pad * 2 + gw
    sheet.blit(gp_night, (nx, gp_y))
    pygame.draw.rect(sheet, (40, 44, 58), (nx, gp_y, gw, gh), 2,
                     border_radius=6)
    _label(sheet, "IN-GAMEPLAY  ·  NIGHT biome (neon home)", nx,
           gp_y + gh + 6, 16, ACCENT)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
