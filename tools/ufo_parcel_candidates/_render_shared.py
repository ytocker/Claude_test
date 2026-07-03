"""Shared render helpers for UFO parcel candidate review sheets.

A "build_fn" here is a parcel builder: build_fn(mode="normal") -> 22×22 Surface.
Each design_N.py exposes this as `build`. The harness composites it beneath Pip
mid-flight so the review sheet matches exactly what a buyer sees in gameplay.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pygame
pygame.init()

from game import biome, parrot
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y, PARCEL_Y_OFFSET

FONT    = pygame.font.SysFont("DejaVu Sans", 16, bold=True)
FONT_SM = pygame.font.SysFont("DejaVu Sans", 12)


def _scene(palette, night=False):
    scene = pygame.Surface((GW, GH))
    phase = 0.5 if night else 0.0
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12,  gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    return scene


def _composite_on_scene(build_fn, scene, pip_cx, pip_cy):
    """Blit the default parrot + the candidate parcel onto `scene` (mutates it)."""
    bird_frame = parrot.get_skin_frame("skin_parrot", 2, 10.0)
    scene.blit(bird_frame, bird_frame.get_rect(center=(pip_cx, pip_cy)))
    parcel_surf = build_fn()
    scene.blit(parcel_surf, parcel_surf.get_rect(center=(pip_cx, pip_cy + PARCEL_Y_OFFSET)))


def gameplay_panel(build_fn, w: int, h: int, *, night: bool = False) -> pygame.Surface:
    palette = biome.palette_for_phase(0.5 if night else 0.0)
    scene = _scene(palette, night=night)
    pip_cx, pip_cy = 96, 270
    _composite_on_scene(build_fn, scene, pip_cx, pip_cy)
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def carry_zoom_panel(build_fn, zoom: int = 5) -> pygame.Surface:
    """4×-zoomed crop of the actual carry position in a daytime gameplay scene.

    Shows exactly what the art-director needs to evaluate: the parcel hanging
    below Pip's tail against real sky, at a scale where every pixel is legible.
    The crop is 36×36px centred on the parcel's carry position.
    """
    palette = biome.palette_for_phase(0.0)
    scene = _scene(palette, night=False)
    pip_cx, pip_cy = 96, 270
    _composite_on_scene(build_fn, scene, pip_cx, pip_cy)
    carry_cy = pip_cy + PARCEL_Y_OFFSET
    crop_r = 18
    crop = pygame.Rect(pip_cx - crop_r, carry_cy - crop_r, crop_r * 2, crop_r * 2)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    raw = scene.subsurface(crop).copy()
    box = crop_r * 2 * zoom
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    panel.blit(pygame.transform.scale(raw, (box, box)), (0, 0))
    return panel


def hero_panel(build_fn, box: int) -> pygame.Surface:
    """A clean close-up: parcel at 4× on a dark card with the parrot above it."""
    bg = (22, 20, 32)
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, bg, panel.get_rect(), border_radius=14)
    # Draw at 4× scale for a big readable truth read.
    parcel_surf = build_fn()
    pw, ph = parcel_surf.get_size()
    big = pygame.transform.scale(parcel_surf, (pw * 4, ph * 4))
    panel.blit(big, big.get_rect(center=(box // 2, box // 2 + 10)))
    return panel


def truth_strip(build_fn, n_frames: int = 1) -> list[pygame.Surface]:
    """Return a list of 22×22 raw surfaces (the 1× truth read). n_frames=1 for
    parcels (mode-agnostic); kept as a list for consistent API."""
    return [build_fn() for _ in range(n_frames)]


def render_sheet(build_fn, title: str, out_path: str):
    """Render and save a 4-panel + truth-strip review sheet."""
    SHEET_W, SHEET_H = 1100, 400
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((30, 28, 38))

    title_surf = FONT.render(title, True, (235, 235, 240))
    sheet.blit(title_surf, (16, 10))

    PW, PH = 210, 300
    y0 = 40
    panels = [
        ("DAY GAMEPLAY",   gameplay_panel(build_fn, PW, PH, night=False)),
        ("NIGHT GAMEPLAY", gameplay_panel(build_fn, PW, PH, night=True)),
        ("HERO (4×)",      hero_panel(build_fn, PH)),
        ("CARRY ZONE (5×)", carry_zoom_panel(build_fn, zoom=5)),
    ]
    x = 16
    for label, panel in panels:
        pw = panel.get_width()
        sheet.blit(panel, (x, y0))
        pygame.draw.rect(sheet, (70, 66, 84), (x, y0, pw, PH), 1)
        lab = FONT_SM.render(label, True, (200, 200, 210))
        sheet.blit(lab, (x + 4, y0 + PH + 4))
        x += pw + 16

    # 22px NEAREST truth read strip
    strip_y = y0 + PH + 22
    sheet.blit(FONT_SM.render("22px NEAREST (truth read)", True, (200, 200, 210)),
               (16, strip_y - 2))
    raw = build_fn()
    # Show 8 repeats at 1× and one at 4× side by side
    for i in range(8):
        cell = pygame.Surface((24, 24))
        cell.fill((46, 44, 56))
        cell.blit(raw, (1, 1))
        sheet.blit(cell, (260 + i * 28, strip_y - 2))
    big_raw = pygame.transform.scale(raw, (88, 88))
    sheet.blit(big_raw, (260 + 8 * 28 + 8, strip_y - 18))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pygame.image.save(sheet, out_path)
    print(f"saved → {out_path}")
