"""Round-2 review sheet for DESIGN 3 — NEON BASELINER (tennis).

Renders the scratch candidate (tools/tennis_candidates/design_3.py) in real
gameplay context — a DAY scene and a NIGHT scene — plus clean hero product
shots and 40px NEAREST "truth read" thumbnails so the night-read claim can be
judged. Hero + 40px panels use NEAREST scaling (no smoothscale) so the review
shows the same hard pixels the game blits, not a softened average. Touches no
production art.

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_tennis_design_3.py``.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP
import tools.ninja_render as nr
from tools.tennis_candidates.design_3 import build as SOURCE


def gameplay_panel_phase(source, w, h, phase):
    """nr.gameplay_panel, but parameterised by biome phase so we can show the
    same costume on a DAY (phase 0.0) and a NIGHT (phase 0.5) sky."""
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
    frame = nr._frame(source, nr.FRAME_IDX, nr.TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def hero_panel_nearest(source, box, bg):
    """Clean product-shot of the bird on a flat panel, scaled with NEAREST so the
    review shows the same hard pixels the game blits — no smoothed average that
    could flatter detail that won't actually survive."""
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, bg, panel.get_rect(), border_radius=14)
    frame = nr._frame(source, nr.FRAME_IDX, 0.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = int(max(1, (box * 0.82) // max(sw, sh)))
    frame = pygame.transform.scale(frame, (sw * scale, sh * scale))
    panel.blit(frame, frame.get_rect(center=(box // 2, box // 2)))
    return panel


def truth_read(source, sky, box=160):
    """40px NEAREST downscale on a flat sky, then NEAREST up to `box` — the
    honest "what survives the shrink" test on day vs. night backdrops. Both the
    downscale and the upscale use NEAREST so no smoothing softens the read."""
    frame = nr._frame(source, nr.FRAME_IDX, 0.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy() if bb.width else frame
    sw, sh = frame.get_size()
    scale = 40.0 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    panel = pygame.Surface((box, box))
    panel.fill(sky)
    up = pygame.transform.scale(small, (box - 24, int((box - 24) * small.get_height() / small.get_width())))
    panel.blit(up, up.get_rect(center=(box // 2, box // 2)))
    return panel


PANEL_W, PANEL_H = 230, 392
HERO, TRUTH = 230, 160
PAD, GUTTER = 26, 18
TITLE_H = 84

DAY_SKY = (150, 200, 235)
NIGHT_SKY = (20, 24, 52)

row_h = PANEL_H
sheet_w = max(540, PAD * 2 + PANEL_W + GUTTER + HERO + GUTTER + TRUTH)
sheet_h = TITLE_H + 2 * row_h + GUTTER + 40 + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(26, True).render(
    "TENNIS — DESIGN 3: NEON BASELINER (round 2, in gameplay)", True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 24)))

lab = _font(15, True)
small = _font(12, True)


def place_row(y, phase, sky, row_tag):
    x = PAD
    gp = gameplay_panel_phase(SOURCE, PANEL_W, row_h, phase)
    pygame.draw.rect(sheet, _GOLD_DEEP, pygame.Rect(x - 2, y - 2, PANEL_W + 4, row_h + 4), 2)
    sheet.blit(gp, (x, y))
    sheet.blit(small.render(row_tag + " GAMEPLAY", True, (180, 174, 200)), (x + 2, y + row_h + 4))

    x += PANEL_W + GUTTER
    hero = hero_panel_nearest(SOURCE, HERO, bg=(sky[0] // 3, sky[1] // 3, sky[2] // 2))
    sheet.blit(hero, (x, y))
    sheet.blit(small.render(row_tag + " HERO SHOT (nearest)", True, (180, 174, 200)), (x + 2, y + HERO + 4))

    x += HERO + GUTTER
    tr = truth_read(SOURCE, sky, TRUTH)
    pygame.draw.rect(sheet, _GOLD_DEEP, pygame.Rect(x - 2, y - 2, TRUTH + 4, TRUTH + 4), 2)
    sheet.blit(tr, (x, y))
    sheet.blit(small.render("40px TRUTH READ (nearest)", True, (180, 174, 200)), (x + 2, y + TRUTH + 4))


place_row(TITLE_H, 0.0, DAY_SKY, "DAY")
place_row(TITLE_H + row_h + 28, 0.6, NIGHT_SKY, "NIGHT")

out = os.path.join("docs", "store_redesign", "costume", "tennis", "design_3", "round_2.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
