"""Shared in-gameplay render harness for the ninja-redesign exploration.

Every design loop AND the final comparison figure composite their candidate
the same way, so the previews match the deliverable. A "source" is either a
registered skin id (str, e.g. the live ``skin_ninja``) or a candidate builder
callable ``(frame_idx, tilt_deg) -> pygame.Surface`` (what a scratch
``tools/ninja_candidates/design_<N>.py`` exposes as ``build``).

Reuses the exact biome/draw helpers the store-figure capture uses
(``tools/capture_store_figures.py``) — no production art is touched.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import parrot, biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

# Canonical mid-flight pose, matching the store-figure captures.
FRAME_IDX = 2
TILT = 10.0


def _frame(source, frame_idx: int, tilt: float) -> pygame.Surface:
    """Resolve a source to a parrot frame: a registered sid (str) goes through
    the live dispatch; a callable is a scratch candidate builder."""
    if callable(source):
        return source(frame_idx, tilt)
    return parrot.get_skin_frame(source, frame_idx, tilt)


def gameplay_panel(source, w: int, h: int, *,
                   frame_idx: int = FRAME_IDX, tilt: float = TILT) -> pygame.Surface:
    """Pip (wearing ``source``) mid-flight over a real daytime biome scene
    (sky + clouds + mountains + two pillars + ground), cropped to a panel
    around the bird and scaled to (w, h). Mirrors capture_store_figures."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.0)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = _frame(source, frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def hero_panel(source, box: int, *, frame_idx: int = FRAME_IDX,
               tilt: float = 0.0, bg=(22, 20, 32)) -> pygame.Surface:
    """A clean, large product-shot of the bird on a flat panel — for judging
    the costume detail the gameplay crop shrinks. Cropped to opaque content."""
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, bg, panel.get_rect(), border_radius=14)
    frame = _frame(source, frame_idx, tilt)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = (box * 0.82) / max(sw, sh)
    frame = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    panel.blit(frame, frame.get_rect(center=(box // 2, box // 2)))
    return panel
