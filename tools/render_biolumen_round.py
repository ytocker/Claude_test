"""Round sheet for design_3 · BIOLUMEN MACAW (LEGENDARY, wave 2).

Emissive light lives or dies on the day read AND the night read, so this sheet
shows the bird in BOTH a bright DAY biome and a NIGHT biome side by side, plus a
clean hero close-up, a 40px NEAREST truth-read (does the lure + glow survive
downscale at gameplay size), and a 4-frame filmstrip (a legendary's glow + jelly
tail must animate alive). Pure capture — design_3 is a scratch builder, no
production art touched.

Run headless: ``SDL_VIDEODRIVER=dummy python tools/render_biolumen_round.py``.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

import tools.ninja_render as nr
from game import biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud,
)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from game.hud import _font, _GOLD_PALE
from tools.parrot_wave2_candidates.design_3 import build

_LEG = (255, 202, 104)            # legendary gem hue


def biome_panel(phase, w, h, *, frame_idx=2, tilt=10.0):
    """Pip (BIOLUMEN) mid-flight over a real biome at the given day-cycle phase
    (0.0 = bright day, 0.64375 = night), cropped around the bird and scaled."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette,
                                     int(palette['star_alpha'])), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pcx, pcy = 96, 270
    frame = build(frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pcx, pcy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pcx + 34, pcy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def truth_read_40(bg, frame_idx=2, tilt=8.0):
    """The north-star test: scale the bird to ~40px gameplay height with NEAREST
    (no smoothing) so we see exactly the pixels that ship in motion."""
    frame = build(frame_idx, tilt)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy() if bb.width else frame
    sh = 40
    sw = max(1, int(frame.get_width() * sh / frame.get_height()))
    small = pygame.transform.scale(frame, (sw, sh))            # NEAREST
    box = 120
    panel = pygame.Surface((box, box))
    panel.fill(bg)
    up = pygame.transform.scale(small, (sw * 2, sh * 2))       # 2x NEAREST to view
    panel.blit(up, up.get_rect(center=(box // 2, box // 2)))
    return panel, small


def filmstrip(bg, n=4, box=120):
    """4 wing frames in a row so the lure sway + jelly billow read as alive."""
    panel = pygame.Surface((box * n, box))
    for i in range(n):
        cell = pygame.Surface((box, box))
        cell.fill(bg)
        frame = build(i, 6.0)
        bb = frame.get_bounding_rect()
        frame = frame.subsurface(bb).copy() if bb.width else frame
        sw, sh = frame.get_size()
        scale = (box * 0.84) / max(sw, sh)
        frame = pygame.transform.smoothscale(
            frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
        cell.blit(frame, frame.get_rect(center=(box // 2, box // 2)))
        panel.blit(cell, (i * box, 0))
    return panel


# ── compose the sheet ─────────────────────────────────────────────────────────
PAD = 26
GUT = 16
TITLE_H = 78
CAP = 22

GP_W, GP_H = 232, 420            # gameplay panels (day, night)
HERO = 280                       # hero close-up box
TR = 120                         # truth-read box
FS_BOX = 120

big_font = _font(24, True)
name_font = _font(18, True)
cap_font = _font(14, False)

# Left column: day + night gameplay. Right column: hero. Bottom band: 40px
# truth-reads (on day + night bg) and the 4-frame filmstrip.
col1_w = GP_W
top_h = GP_H
hero_y = TITLE_H

sheet_w = max(880, PAD * 2 + GP_W + GUT + HERO + GUT + GP_W)
bottom_y = TITLE_H + top_h + 34 + CAP
bottom_h = FS_BOX
sheet_h = bottom_y + bottom_h + 30 + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((16, 18, 30))

title = big_font.render(
    "BIOLUMEN MACAW  ·  LEGENDARY (~2900)  ·  wave 2 · round 1", True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 22)))


def _label(x, y, text, col=_GOLD_PALE, f=name_font):
    sheet.blit(f.render(text, True, col), (x, y))


# Day gameplay
x = PAD
day = biome_panel(0.0, GP_W, GP_H)
pygame.draw.rect(sheet, _LEG, (x - 3, TITLE_H - 3, GP_W + 6, GP_H + 6), width=3)
sheet.blit(day, (x, TITLE_H))
_label(x, TITLE_H + GP_H + 7, "DAY SKY — mid-flight")

# Night gameplay
x2 = PAD + GP_W + GUT
night = biome_panel(0.64375, GP_W, GP_H)
pygame.draw.rect(sheet, _LEG, (x2 - 3, TITLE_H - 3, GP_W + 6, GP_H + 6), width=3)
sheet.blit(night, (x2, TITLE_H))
_label(x2, TITLE_H + GP_H + 7, "NIGHT SKY — mid-flight")

# Hero close-up (right)
x3 = PAD + 2 * GP_W + 2 * GUT
hero = nr.hero_panel(build, HERO, frame_idx=2, tilt=0.0, bg=(10, 14, 26))
sheet.blit(hero, (x3, TITLE_H))
_label(x3, TITLE_H + HERO + 7, "HERO — lure-stalk / jelly tail / veins")

# Bottom band: two 40px truth-reads + filmstrip
by = bottom_y
tr_day, _ = truth_read_40((150, 205, 235))
tr_night, _ = truth_read_40((10, 14, 30))
sheet.blit(tr_day, (PAD, by))
sheet.blit(tr_night, (PAD + TR + GUT, by))
_label(PAD, by + TR + 4, "40px NEAREST · day bg", _GOLD_PALE, cap_font)
_label(PAD + TR + GUT, by + TR + 4, "40px NEAREST · night bg", _GOLD_PALE, cap_font)

fs_x = PAD + 2 * TR + 2 * GUT
fs = filmstrip((12, 16, 28))
sheet.blit(fs, (fs_x, by))
_label(fs_x, by + FS_BOX + 4, "4-FRAME FILMSTRIP — glow + jelly tail animate alive",
       _GOLD_PALE, cap_font)

out_dir = os.path.join("docs", "store_redesign", "parrot", "wave2", "design_3")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "round_1.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
