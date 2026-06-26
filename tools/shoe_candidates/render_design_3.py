"""Round-1 review sheet for shoe design_3 NEON CIRCUIT (exploration only).

Renders the product-shot icon, Pip wearing the shoe over a day AND a night
biome scene, a clean hero panel, and the 40px NEAREST truth read (1x + 4x,
day and night). The night reads are the crux: an emissive neon shoe lives or
dies on whether the glow POPS against a dark sky.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
import pygame
pygame.init()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import design_3
from game import shoe_skins, biome, parrot
from game.store_skins import _make_skin
from game.shoe_skins import _foot_paint
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
import tools.ninja_render as nr

FONT = pygame.font.SysFont("dejavusans", 15, bold=True)
SMALL = pygame.font.SysFont("dejavusans", 12)


def label(surf, text, x, y, color=(235, 240, 250)):
    surf.blit(FONT.render(text, True, color), (x, y))


def small(surf, text, x, y, color=(180, 188, 205)):
    surf.blit(SMALL.render(text, True, color), (x, y))


def scene_panel(build, w, h, phase):
    """Pip wearing the shoe over a biome scene at the given day/night phase."""
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
    frame = build(nr.FRAME_IDX, nr.TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = min(GH, int(GH * 0.78))
    crop_w = min(GW, int(crop_h * w / h))
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def truth_read(build, phase, target_h=40):
    """A worn frame shrunk to ~40px tall on a flat day/night-tinted bg, NEAREST,
    returned at 1x and 4x — the honest gameplay-scale read."""
    frame = build(nr.FRAME_IDX, nr.TILT)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = target_h / sh
    small_w = max(1, int(round(sw * scale)))
    one = pygame.transform.smoothscale(frame, (small_w, target_h))
    four = pygame.transform.scale(one, (small_w * 4, target_h * 4))  # NEAREST
    return one, four


def main():
    draw_shoe = design_3.draw_shoe
    build = _make_skin(_foot_paint(draw_shoe))

    W, H = 1180, 720
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 19, 26))

    # Title
    sheet.blit(pygame.font.SysFont("dejavusans", 22, bold=True).render(
        "SHOE design_3 — NEON CIRCUIT (epic ~1800) — round 2", True, (230, 236, 248)), (24, 16))

    # ── product-shot icon (big) ─────────────────────────────────────────────────
    icon = shoe_skins._build_icon(draw_shoe)
    bb = icon.get_bounding_rect()
    icon = icon.subsurface(bb).copy() if bb.width else icon
    big = pygame.transform.smoothscale(icon, (340, int(340 * icon.get_height() / icon.get_width())))
    card = pygame.Surface((380, 300), pygame.SRCALPHA)
    pygame.draw.rect(card, (10, 11, 17), card.get_rect(), border_radius=14)
    card.blit(big, big.get_rect(center=(190, 160)))
    sheet.blit(card, (24, 56))
    label(sheet, "product-shot icon", 36, 64)

    # ── Pip wearing it — DAY + NIGHT scenes ─────────────────────────────────────
    day = scene_panel(build, 360, 300, 0.0)
    night = scene_panel(build, 360, 300, 0.5)
    sheet.blit(day, (420, 56))
    sheet.blit(night, (790, 56))
    label(sheet, "worn — DAY scene", 432, 64)
    label(sheet, "worn — NIGHT scene", 802, 64)

    # ── hero panel (clean) ──────────────────────────────────────────────────────
    hero = nr.hero_panel(build, 240, bg=(16, 14, 24))
    sheet.blit(hero, (24, 380))
    label(sheet, "hero panel", 36, 388)

    # ── 40px NEAREST truth read — day + night, 1x and 4x ────────────────────────
    bx = 300
    for phase, tint, name in ((0.0, (96, 150, 210), "DAY"), (0.5, (14, 14, 26), "NIGHT")):
        one, four = truth_read(build, phase)
        cell = pygame.Surface((four.get_width() + 120, 240), pygame.SRCALPHA)
        pygame.draw.rect(cell, (*tint, 255), cell.get_rect(), border_radius=12)
        cell.blit(one, one.get_rect(midleft=(20, 120)))
        cell.blit(four, four.get_rect(midleft=(20 + one.get_width() + 28, 120)))
        sheet.blit(cell, (bx, 380))
        label(sheet, f"40px truth — {name}", bx + 14, 388, (245, 248, 255))
        small(sheet, "1x  +  4x NEAREST", bx + 14, 600, (40, 40, 55))
        bx += four.get_width() + 150

    out = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..",
        "docs", "store_redesign", "shoes", "design_3", "round_2.png"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("SAVED", out, "exists:", os.path.exists(out))


if __name__ == "__main__":
    main()
