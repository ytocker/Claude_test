"""Review sheet for TENNIS DESIGN 4 — RETRO '70s (vintage cream).

In-gameplay product shot for the retro-tennis candidate: Pip mid-flight over a
real biome scene (DAY + NIGHT), a clean hero panel, and the 40px NEAREST truth
read (the size the costume actually has to survive in motion), both phases.
Pure capture — touches no production art (the candidate is a scratch builder
under tools/tennis_candidates/).

Hero + 40px panels scale with NEAREST (no smoothscale) so the review judges the
exact pixels the costume ships as, not a re-smoothed image. Run headless from
repo root:
``SDL_VIDEODRIVER=dummy python tools/render_tennis_design_4.py``.
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
from tools.tennis_candidates.design_4 import build as SRC


def gameplay_panel_phase(source, w, h, phase, *, frame_idx=nr.FRAME_IDX, tilt=nr.TILT):
    """nr.gameplay_panel, but with a selectable biome phase so we get a real
    DAY scene (phase 0.0) and a real NIGHT scene (phase 0.5)."""
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


def hero_panel_nearest(source, box, *, frame_idx=nr.FRAME_IDX, tilt=0.0, bg=(22, 20, 32)):
    """Hero product shot, but the bird is integer-NEAREST-scaled so the panel
    shows the exact procedural pixels (no smoothscale blur masking the read)."""
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, bg, panel.get_rect(), border_radius=14)
    frame = nr._frame(source, frame_idx, tilt)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    factor = max(1, int((box * 0.82) / max(sw, sh)))
    frame = pygame.transform.scale(frame, (sw * factor, sh * factor))
    panel.blit(frame, frame.get_rect(center=(box // 2, box // 2)))
    return panel


def truth_read(source, bg, *, frame_idx=nr.FRAME_IDX, tilt=nr.TILT):
    """The 40px NEAREST truth read — what the costume actually looks like in
    motion in the store grid / in flight, on a flat phase-tinted card. NEAREST
    on both the downscale and the blow-up so we judge the honest 40px pixels."""
    frame = nr._frame(source, frame_idx, tilt)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    big = pygame.transform.scale(small, (small.get_width() * 4, small.get_height() * 4))
    card = pygame.Surface((176, 176), pygame.SRCALPHA)
    pygame.draw.rect(card, bg, card.get_rect(), border_radius=12)
    card.blit(big, big.get_rect(center=(88, 88)))
    return card


# Layout: title, then two rows (DAY / NIGHT). Each row = gameplay panel + hero
# panel + 40px truth read.
PANEL_W, PANEL_H = 230, 392
HERO = 392
TRUTH = 176
PAD, GUTTER = 26, 20
TITLE_H = 84
ROW_GAP = 30
LABEL_H = 26

row_w = PANEL_W + GUTTER + HERO + GUTTER + TRUTH
sheet_w = PAD * 2 + row_w
sheet_h = TITLE_H + 2 * (LABEL_H + PANEL_H) + ROW_GAP + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(26, True).render(
    "TENNIS — DESIGN 4: RETRO '70s (vintage cream)  ·  in gameplay", True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 24)))
sub = _font(15, True).render(
    "honey WOOD racket · tri-stripe terry sweatband · ecru shawl-collar polo", True,
    (170, 162, 190))
sheet.blit(sub, sub.get_rect(midtop=(sheet_w // 2, 56)))

lab_font = _font(16, True)

ROWS = [("DAY", 0.0, (24, 30, 44)), ("NIGHT", 0.5, (14, 14, 26))]

for ri, (name, phase, hero_bg) in enumerate(ROWS):
    y = TITLE_H + ri * (LABEL_H + PANEL_H + ROW_GAP)
    sheet.blit(lab_font.render(name, True, _GOLD_PALE), (PAD, y))
    yp = y + LABEL_H
    x = PAD

    gp = gameplay_panel_phase(SRC, PANEL_W, PANEL_H, phase)
    pygame.draw.rect(sheet, (*_GOLD_DEEP,), pygame.Rect(x - 2, yp - 2, PANEL_W + 4, PANEL_H + 4), 2)
    sheet.blit(gp, (x, yp))
    x += PANEL_W + GUTTER

    hp = hero_panel_nearest(SRC, HERO, tilt=0.0, bg=hero_bg)
    sheet.blit(hp, (x, yp))
    x += HERO + GUTTER

    tr = truth_read(SRC, hero_bg)
    sheet.blit(tr, (x, yp))
    sheet.blit(_font(13, True).render("40px truth", True, (150, 150, 170)),
               (x, yp + TRUTH + 4))

out = os.path.join("docs", "store_redesign", "costume", "tennis", "design_4", "round_2.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
