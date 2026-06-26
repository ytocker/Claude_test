"""Round-1 review sheet for DESIGN 2 — CLAY COURT (tennis).

In-gameplay reads of the candidate clay-court tennis kit: a DAY gameplay panel +
a NIGHT gameplay panel + a clean hero product-shot, each next to a 40px NEAREST
"truth read" so the costume can be judged at the size it actually ships. Pure
capture — touches no production art (the candidate lives under
tools/tennis_candidates/).

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_tennis_design_2.py``.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib
import pygame
pygame.init()

import tools.ninja_render as nr
from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP

build = importlib.import_module("tools.tennis_candidates.design_2").build


def gameplay_panel_phase(source, w, h, phase, *, frame_idx=nr.FRAME_IDX, tilt=nr.TILT):
    """Same composite as nr.gameplay_panel but at an arbitrary biome phase so a
    NIGHT scene can be captured alongside the DAY one."""
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
    frame = nr._frame(source, frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def truth_read(source, px, bg):
    """The 40px NEAREST downscale — the real shipped icon size — on a flat panel
    so the legibility read is honest (no smoothscale flattering the detail)."""
    frame = nr._frame(source, nr.FRAME_IDX, 0.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = px / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    box = px + 24
    panel = pygame.Surface((box, box))
    panel.fill(bg)
    panel.blit(small, small.get_rect(center=(box // 2, box // 2)))
    return panel


PANEL_W, PANEL_H = 220, 392
HERO = 300
PAD, GUTTER = 28, 20
TITLE_H = 84

cols = []
cols.append(("DAY — GAMEPLAY", gameplay_panel_phase(build, PANEL_W, PANEL_H, 0.0)))
cols.append(("NIGHT — GAMEPLAY", gameplay_panel_phase(build, PANEL_W, PANEL_H, 0.5)))
cols.append(("HERO PRODUCT-SHOT", nr.hero_panel(build, PANEL_H)))

sheet_w = PAD * 2 + 2 * PANEL_W + GUTTER + PANEL_H + GUTTER
sheet_h = TITLE_H + PANEL_H + 56 + 40 + (40 + 24) + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(30, True).render(
    "TENNIS — DESIGN 2: CLAY COURT (Roland-Garros terracotta)  ·  round 1",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 24)))

name_font = _font(15, True)
tag_font = _font(12, True)

x = PAD
for cap, panel in cols:
    y = TITLE_H
    pw = panel.get_width()
    pygame.draw.rect(sheet, (*_GOLD_DEEP,), pygame.Rect(x - 2, y - 2, pw + 4, PANEL_H + 4), width=2)
    sheet.blit(panel, (x, y))
    sheet.blit(name_font.render(cap, True, _GOLD_PALE), (x + 2, y + PANEL_H + 8))
    x += pw + GUTTER

# 40px truth reads (day + night background) under the panels.
ty = TITLE_H + PANEL_H + 56
sheet.blit(tag_font.render("40px NEAREST truth read (shipped size):", True,
                           (170, 162, 190)), (PAD, ty - 4))
tx = PAD
for lab, bg in (("DAY", (150, 196, 232)), ("NIGHT", (28, 30, 58))):
    tr = truth_read(build, 40, bg)
    sheet.blit(tr, (tx, ty + 16))
    sheet.blit(tag_font.render(lab, True, (170, 162, 190)), (tx, ty + 16 + tr.get_height() + 2))
    tx += tr.get_width() + 18

out = os.path.join("docs", "store_redesign", "costume", "tennis", "design_2", "round_1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
