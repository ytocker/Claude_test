"""Round sheet for design_2 · JADE-CARVING MACAW.

Renders the candidate in-gameplay over BOTH skies (day + night), a clean hero
product-shot, and a 40px NEAREST truth-read on each sky — the north-star
"lives at 40px in motion" check. Exploration deliverable only; touches no
production art.
"""
from __future__ import annotations
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import importlib
import pygame
pygame.init()

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import hero_panel, FRAME_IDX, TILT, _frame

design_2 = importlib.import_module("tools.parrot_wave2_candidates.design_2")
BUILD = design_2.build

ROUND = os.environ.get("ROUND", "2")
OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..",
    "docs", "store_redesign", "parrot", "wave2", "design_2", f"round_{ROUND}.png"))


def gameplay_panel_phase(source, w, h, phase, *, frame_idx=FRAME_IDX, tilt=TILT):
    """Pip mid-flight over a real biome scene at an arbitrary day/night phase —
    same composition as ninja_render.gameplay_panel but phase-parametrised so the
    candidate can be judged on the night sky too."""
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
    frame = _frame(source, frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop_w = min(crop_w, GW)
    crop_h = min(crop_h, GH)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def truth_read(source, sky_color, frame_idx=FRAME_IDX, tilt=TILT, box=140):
    """The make-or-break: the bird scaled to 40px with NEAREST (no smoothing) on a
    flat sky swatch, then nearest-upscaled into the cell so the pixel truth at
    thumbnail size is visible. This is what the player sees in motion."""
    cell = pygame.Surface((box, box))
    cell.fill(sky_color)
    frame = _frame(source, frame_idx, tilt)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40.0 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))     # NEAREST
    up = pygame.transform.scale(small, (small.get_width() * 3, small.get_height() * 3))
    cell.blit(up, up.get_rect(center=(box // 2, box // 2)))
    # also drop the actual-40px chip in the corner so true size is visible
    cell.blit(small, (6, 6))
    pygame.draw.rect(cell, (90, 90, 100), cell.get_rect(), 1)
    return cell


# ── compose the sheet ─────────────────────────────────────────────────────────
PW, PH = 220, 300
HERO = 300
TR = 140
PAD = 16
TITLE_H = 60
LABEL_H = 26

day_pal = biome.palette_for_phase(0.0)
night_pal = biome.palette_for_phase(0.64375)
day_sky = day_pal['sky_top']
night_sky = night_pal['sky_top']

# top row: day gameplay | night gameplay | hero
top_w = PW + PW + HERO + 4 * PAD
# bottom row: two truth reads (day, night)
fig_w = max(top_w, 2 * TR + 3 * PAD)
fig_h = TITLE_H + PH + LABEL_H + PAD + TR + LABEL_H + 2 * PAD

fig = pygame.Surface((fig_w, fig_h))
fig.fill((18, 18, 26))

f_title = pygame.font.SysFont("DejaVuSans", 26, bold=True)
f_lbl = pygame.font.SysFont("DejaVuSans", 16, bold=True)
f_small = pygame.font.SysFont("DejaVuSans", 13)

title = f_title.render(f"design_2 · JADE-CARVING MACAW — EPIC  (round {ROUND})",
                       True, (235, 240, 238))
fig.blit(title, (PAD, (TITLE_H - title.get_height()) // 2))


def label(x, y, text, color=(220, 235, 228)):
    fig.blit(f_lbl.render(text, True, color), (x, y))


y0 = TITLE_H
day_panel = gameplay_panel_phase(BUILD, PW, PH, 0.0)
night_panel = gameplay_panel_phase(BUILD, PW, PH, 0.64375)
hero = hero_panel(BUILD, HERO, tilt=0.0)

x = PAD
fig.blit(day_panel, (x, y0)); label(x, y0 + PH + 4, "GAMEPLAY — DAY SKY")
x += PW + PAD
fig.blit(night_panel, (x, y0)); label(x, y0 + PH + 4, "GAMEPLAY — NIGHT SKY")
x += PW + PAD
fig.blit(hero, (x, y0 + (PH - HERO) // 2 if PH > HERO else y0))
label(x, y0 + PH + 4, "HERO PRODUCT-SHOT")

# bottom row: truth reads
y1 = y0 + PH + LABEL_H + PAD
x = PAD
fig.blit(truth_read(BUILD, day_sky), (x, y1))
label(x, y1 + TR + 4, "40px TRUTH — DAY")
x += TR + PAD
fig.blit(truth_read(BUILD, night_sky), (x, y1))
label(x, y1 + TR + 4, "40px TRUTH — NIGHT")

# legend note
note = f_small.render(
    "ruyi cloud-scroll tail (hero) · 3 relief grooves · 1 cinnabar seal · smoky-jade aviators relit mint",
    True, (170, 200, 188))
fig.blit(note, (x + TR + 2 * PAD, y1 + 10))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(fig, OUT)
print("wrote", OUT, fig.get_size())
