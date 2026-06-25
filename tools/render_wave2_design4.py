"""Round-1 exploration sheet for design_4 · STAINED-GLASS MACAW (legendary).

In-gameplay reads, day AND night, so the back-lit panes + lead lines are judged
on both palettes the way the wave2 brief demands: a day gameplay panel, a night
gameplay panel, a clean hero close-up, a 40px NEAREST truth-read (does the
window survive the downscale), and a 4-frame filmstrip (legendary tell — the
glass tail/halo must read across the flap). Pure capture; nothing registered.

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_wave2_design4.py``.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud,
)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from game.hud import _font, _GOLD_PALE
import tools.ninja_render as nr
from tools.parrot_wave2_candidates.design_4 import build as BUILD


def _scene_panel(phase, w, h, *, frame_idx=2, tilt=10.0):
    """A gameplay crop around Pip mid-flight over the biome at the given phase,
    so day (0.0) and night (0.64375) can both be captured."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette,
                                     int(palette.get('star_alpha', 0))), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = BUILD(frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _truth40(bg):
    """The bird rendered then hard-downscaled to ~40px with NEAREST (no smooth),
    then blown back up NEAREST onto a tile — the 'lives or dies at 40px' check."""
    frame = BUILD(2, 8.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40.0 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    tile = pygame.Surface((140, 140))
    tile.fill(bg)
    big = pygame.transform.scale(small, (small.get_width() * 3, small.get_height() * 3))
    tile.blit(big, big.get_rect(center=(70, 70)))
    return tile


def _filmstrip(bg):
    """All four wing frames in a row, on a flat tile, so the baked halo/tail are
    judged across the whole flap cycle (the legendary motion tell)."""
    cell = 120
    strip = pygame.Surface((cell * 4, cell), pygame.SRCALPHA)
    strip.fill(bg)
    for i in range(4):
        frame = BUILD(i, 6.0)
        bb = frame.get_bounding_rect()
        f = frame.subsurface(bb).copy()
        sw, sh = f.get_size()
        sc = (cell * 0.84) / max(sw, sh)
        f = pygame.transform.smoothscale(f, (int(sw * sc), int(sh * sc)))
        strip.blit(f, f.get_rect(center=(i * cell + cell // 2, cell // 2)))
        pygame.draw.line(strip, (60, 56, 72), (i * cell, 8), (i * cell, cell - 8), 1)
    return strip


# ── compose the sheet ─────────────────────────────────────────────────────────
PAD = 24
TITLE_H = 70
GP_W, GP_H = 300, 420          # gameplay panels (day, night)
HERO = 300
DARK = (18, 16, 28)
NIGHTBG = (12, 14, 30)

day_panel = _scene_panel(0.0, GP_W, GP_H)
night_panel = _scene_panel(0.64375, GP_W, GP_H)
hero = nr.hero_panel(BUILD, HERO, tilt=0.0, bg=(26, 22, 36))
t40_day = _truth40((176, 214, 240))
t40_night = _truth40((20, 24, 48))
film_day = _filmstrip((26, 22, 36))
film_night = _filmstrip(NIGHTBG)

top_h = max(GP_H, HERO)
strip_h = film_day.get_height()
sheet_w = PAD * 4 + GP_W + GP_H + HERO  # not used directly; recompute below
# Layout: row 1 = [day gameplay | night gameplay | hero], row 2 = truth40 pair,
# row 3 = day filmstrip, row 4 = night filmstrip.
row1_w = GP_W + GP_W + HERO + PAD * 2
sheet_w = PAD * 2 + row1_w
strip_w = film_day.get_width()
sheet_w = max(sheet_w, PAD * 2 + strip_w)

t40_block_h = max(t40_day.get_height(), 140)
sheet_h = (TITLE_H + top_h + PAD + t40_block_h + PAD
           + strip_h + 28 + strip_h + PAD * 2)

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(DARK)

title = _font(28, True).render(
    "STAINED-GLASS MACAW · LEGENDARY (~3400) · wave2 design_4 · round 1",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 20)))
sub = _font(14, False).render(
    "rose-window halo + cathedral glass tail (back-lit) · leaded jewel panes · gothic-arch crest",
    True, (180, 172, 200))
sheet.blit(sub, sub.get_rect(midtop=(sheet_w // 2, 48)))

lab = _font(14, True)
y = TITLE_H
x = PAD
sheet.blit(day_panel, (x, y))
sheet.blit(lab.render("GAMEPLAY · DAY", True, _GOLD_PALE), (x + 4, y + GP_H + 4))
x += GP_W + PAD
sheet.blit(night_panel, (x, y))
sheet.blit(lab.render("GAMEPLAY · NIGHT", True, _GOLD_PALE), (x + 4, y + GP_H + 4))
x += GP_W + PAD
pygame.draw.rect(sheet, (26, 22, 36), pygame.Rect(x, y, HERO, HERO), border_radius=14)
sheet.blit(hero, (x, y))
sheet.blit(lab.render("HERO CLOSE-UP", True, _GOLD_PALE), (x + 4, y + HERO + 4))

y += top_h + PAD + 16
x = PAD
sheet.blit(t40_day, (x, y))
sheet.blit(lab.render("40px · DAY", True, _GOLD_PALE), (x + 4, y + t40_day.get_height() + 2))
x += t40_day.get_width() + PAD
sheet.blit(t40_night, (x, y))
sheet.blit(lab.render("40px · NIGHT", True, _GOLD_PALE), (x + 4, y + t40_night.get_height() + 2))
x += t40_night.get_width() + PAD
note = _font(13, False).render("40px NEAREST truth-read — does the window survive?",
                               True, (180, 172, 200))
sheet.blit(note, (x, y + 50))

y += t40_block_h + PAD + 16
sheet.blit(lab.render("4-FRAME FILMSTRIP · DAY (legendary motion tell)", True, _GOLD_PALE), (PAD, y - 14))
sheet.blit(film_day, (PAD, y))
y += strip_h + 28
sheet.blit(lab.render("4-FRAME FILMSTRIP · NIGHT", True, _GOLD_PALE), (PAD, y - 14))
sheet.blit(film_night, (PAD, y))

out_dir = os.path.join("docs", "store_redesign", "parrot", "wave2", "design_4")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "round_1.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
