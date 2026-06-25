"""Round-1 review sheet for JELLYCORE (shoes design_2). Scratch only."""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
import pygame
pygame.init()

# Allow running from anywhere.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from game import shoe_skins, biome
from game.store_skins import _make_skin
from game.shoe_skins import _foot_paint
from game.draw import (get_sky_surface_biome, draw_mountains, draw_ground,
                       draw_cloud)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.shoe_candidates.design_2 import draw_shoe
from tools.ninja_render import gameplay_panel, hero_panel

FONT = pygame.font.SysFont("dejavusans", 15, bold=True)
SMALL = pygame.font.SysFont("dejavusans", 12)


def night_gameplay_panel(source, w, h):
    """Same composition as ninja_render.gameplay_panel but at a dusk/night
    biome phase so the translucent sole can be judged over a dark sky."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.5)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
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


def truth_read(source, bg):
    """Worn frame at ~40px tall (nearest), shown 1x and ~4x over a flat bg —
    confirms the jelly look reads at true foot scale, not as mud."""
    frame = source(2, 10.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy() if bb.width else frame
    sw, sh = frame.get_size()
    target_h = 40
    scale = target_h / sh
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), target_h))
    big = pygame.transform.scale(
        small, (small.get_width() * 4, small.get_height() * 4))  # nearest
    panel = pygame.Surface((big.get_width() + small.get_width() + 30, 180),
                           pygame.SRCALPHA)
    pygame.draw.rect(panel, bg, panel.get_rect(), border_radius=10)
    panel.blit(small, small.get_rect(center=(20 + small.get_width() // 2, 90)))
    panel.blit(big, big.get_rect(center=(panel.get_width() - big.get_width() // 2 - 12, 90)))
    return panel


def label(surf, text, x, y, color=(255, 255, 255)):
    surf.blit(FONT.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(FONT.render(text, True, color), (x, y))


def main():
    build = _make_skin(_foot_paint(draw_shoe))

    icon = shoe_skins._build_icon(draw_shoe)
    icon_big = pygame.transform.smoothscale(
        icon, (icon.get_width() * 3, icon.get_height() * 3))

    gp_day = gameplay_panel(build, 240, 360)
    gp_night = night_gameplay_panel(build, 240, 360)
    hero = hero_panel(build, 260)
    tr_day = truth_read(build, (30, 34, 46))
    tr_night = truth_read(build, (10, 12, 22))

    W, H = 1280, 740
    sheet = pygame.Surface((W, H))
    sheet.fill((24, 22, 30))
    label(sheet, "JELLYCORE — shoes design_2 — epic ~1200 — round 1", 24, 16,
          (255, 180, 230))

    # Product-shot hero, top-left on a soft checker so translucency shows.
    card = pygame.Surface((icon_big.get_width() + 40, icon_big.get_height() + 56))
    card.fill((40, 38, 52))
    cw, ch = 14, 14
    for cy in range(0, card.get_height(), ch):
        for cx in range(0, card.get_width(), cw):
            if ((cx // cw) + (cy // ch)) % 2 == 0:
                pygame.draw.rect(card, (52, 50, 66), (cx, cy, cw, ch))
    card.blit(icon_big, (20, 36))
    sheet.blit(card, (24, 70))
    label(sheet, "PRODUCT SHOT (icon, 3x)", 34, 74)

    sheet.blit(hero, (24, 70 + card.get_height() + 24))
    label(sheet, "HERO — Pip", 34, 74 + card.get_height() + 24)

    x3 = 24 + card.get_width() + 24
    sheet.blit(gp_day, (x3, 60))
    label(sheet, "GAMEPLAY — DAY", x3 + 8, 64)
    sheet.blit(gp_night, (x3 + 256, 60))
    label(sheet, "GAMEPLAY — NIGHT/DUSK", x3 + 264, 64)

    x4 = x3 + 256 * 2
    sheet.blit(tr_day, (x4, 60))
    label(sheet, "40px TRUTH — DAY (1x|4x)", x4 + 4, 40)
    sheet.blit(tr_night, (x4, 270))
    label(sheet, "40px TRUTH — NIGHT (1x|4x)", x4 + 4, 250)

    out = os.path.join(_ROOT, "docs", "store_redesign", "shoes", "design_2",
                       "round_1.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, "exists:", os.path.exists(out))


if __name__ == "__main__":
    main()
