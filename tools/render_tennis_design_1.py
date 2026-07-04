"""Round-1 review sheet for DESIGN 1 — WIMBLEDON WHITES (tennis costume).

Scratch exploration only — touches no production art (the candidate lives under
tools/tennis_candidates/). Builds an in-gameplay review sheet: gameplay + hero
panels DAY and NIGHT, plus a 40px NEAREST "truth read" so the costume can be
judged at the real downscale it ships at.

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_tennis_design_1.py``.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib
import pygame
pygame.init()

from game import biome
from game.draw import (get_sky_surface_biome, draw_mountains, draw_ground,
                       draw_cloud)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP
import tools.ninja_render as nr

build = importlib.import_module("tools.tennis_candidates.design_1").build


def gameplay_panel_phase(source, w, h, phase, *, frame_idx=2, tilt=10.0):
    """Pip mid-flight over a real biome scene at a given day/night PHASE, cropped
    around the bird and scaled. Mirrors ninja_render.gameplay_panel but lets the
    palette phase vary so NIGHT legibility can be judged."""
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
    frame = source(frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def hero_panel_nearest(source, box, *, frame_idx=2, tilt=8.0, bg=(22, 20, 32)):
    """Large product-shot using NEAREST scaling (no bilinear smoothing) so the
    hero crop is crisp and matches the chunky pixels the player sees at scale."""
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, bg, panel.get_rect(), border_radius=14)
    frame = source(frame_idx, tilt)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = (box * 0.82) / max(sw, sh)
    frame = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    panel.blit(frame, frame.get_rect(center=(box // 2, box // 2)))
    return panel


def truth_read(source, phase, box=160, *, frame_idx=2, tilt=10.0):
    """The 40px NEAREST 'truth read': render the frame, hard-downscale to 40px
    with NEAREST (what the player actually sees at hero/store scale), then blow
    it back up NEAREST onto a phase-tinted panel so chunky pixels are visible."""
    bg = (216, 226, 236) if phase < 0.3 else (24, 26, 44)
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, bg, panel.get_rect(), border_radius=12)
    frame = source(frame_idx, tilt)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    small = pygame.transform.scale(frame, (40, 40))            # NEAREST downscale
    big = pygame.transform.scale(small, (box - 24, box - 24))  # NEAREST upscale
    panel.blit(big, big.get_rect(center=(box // 2, box // 2)))
    return panel


GP_W, GP_H = 230, 392
HERO, TRUTH = 230, 160
PAD, GUT = 28, 20
TITLE_H = 84
COL_W = GP_W
CAP_H = 30

# Layout: two rows (DAY / NIGHT), each row = gameplay | hero | truth-read.
row_w = GP_W + GUT + HERO + GUT + TRUTH
sheet_w = PAD * 2 + row_w
sheet_h = TITLE_H + 2 * (GP_H + CAP_H + PAD)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(30, True).render(
    "DESIGN 1 — WIMBLEDON WHITES  (tennis · in gameplay)", True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 24)))
sub = _font(15, True).render(
    "wood-frame racket · all-white polo · royal-green + aubergine trim",
    True, (170, 162, 190))
sheet.blit(sub, sub.get_rect(midtop=(sheet_w // 2, 56)))

cap_font = _font(15, True)
ROWS = [("DAY", 0.0), ("NIGHT", 0.64375)]

for r, (label, phase) in enumerate(ROWS):
    y = TITLE_H + r * (GP_H + CAP_H + PAD)
    x = PAD
    # gameplay
    gp = gameplay_panel_phase(build, GP_W, GP_H, phase)
    pygame.draw.rect(sheet, (*_GOLD_DEEP,),
                     pygame.Rect(x - 2, y - 2, GP_W + 4, GP_H + 4), width=2)
    sheet.blit(gp, (x, y))
    sheet.blit(cap_font.render(f"{label} — GAMEPLAY", True, _GOLD_PALE),
               (x + 2, y + GP_H + 6))
    # hero
    x2 = x + GP_W + GUT
    hy = y + (GP_H - HERO) // 2
    hero = hero_panel_nearest(build, HERO, tilt=8.0)
    sheet.blit(hero, (x2, hy))
    sheet.blit(cap_font.render(f"{label} — HERO", True, _GOLD_PALE),
               (x2 + 2, y + GP_H + 6))
    # truth read
    x3 = x2 + HERO + GUT
    ty = y + (GP_H - TRUTH) // 2
    tr = truth_read(build, phase, TRUTH)
    sheet.blit(tr, (x3, ty))
    sheet.blit(cap_font.render("40px TRUTH READ", True, _GOLD_PALE),
               (x3 + 2, y + GP_H + 6))

out = os.path.join("docs", "store_redesign", "costume", "tennis", "design_1",
                   "round_2.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
