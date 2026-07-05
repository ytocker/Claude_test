"""Assemble the MOONBLOOM MACAW (design_4) round sheet.

Renders the candidate in-gameplay over BOTH a day sky and a night sky, a clean
hero product-shot, a 40px NEAREST truth-read on BOTH skies (the make-or-break
for a bright pearl bird), and a 4-frame filmstrip (legendary anim check).
Reuses the shared ninja_render harness so previews match the deliverable.

Usage: python -m tools.parrot_wave2_candidates.make_round_4 [round_N]
"""
from __future__ import annotations
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import gameplay_panel, hero_panel
from tools.parrot_wave2_candidates.design_4 import build

ROUND = sys.argv[1] if len(sys.argv) > 1 else "round_1"
OUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "docs", "store_redesign", "parrot", "wave2", "design_4",
    f"{ROUND}.png")


def gameplay_panel_phase(source, w, h, phase, *, frame_idx=2, tilt=10.0):
    """gameplay_panel, but over an arbitrary biome phase so we can show the
    same bird on a NIGHT sky (where the additive moon-glow lives)."""
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


def truth_read(source, sky_color, *, frame_idx=2, tilt=10.0, box=120):
    """40px NEAREST downscale of the bird on a flat sky swatch, then NEAREST
    up so the judge sees exactly what survives at gameplay scale."""
    frame = source(frame_idx, tilt)
    small = pygame.transform.smoothscale(frame, (40, 40))
    sw = pygame.Surface((40, 40))
    sw.fill(sky_color)
    sw.blit(small, (0, 0))
    return pygame.transform.scale(sw, (box, box))   # NEAREST up


def filmstrip(source, cell, *, tilt=6.0, bg=(22, 20, 32)):
    strip = pygame.Surface((cell * 4, cell), pygame.SRCALPHA)
    for fi in range(4):
        panel = hero_panel(source, cell, frame_idx=fi, tilt=tilt, bg=bg)
        strip.blit(panel, (fi * cell, 0))
    return strip


# ── layout ────────────────────────────────────────────────────────────────────
PAD = 16
TITLE_H = 58
LABEL_H = 26
GP_W, GP_H = 200, 286            # gameplay panels (day, night)
HERO = 286                       # hero product shot box
TRUTH = 120                      # 40px truth-read box
FILM_CELL = 150

DAY_SKY = (96, 168, 228)         # bright daytime blue — the make-or-break read
NIGHT_SKY = (12, 18, 52)         # deep night

f_title = pygame.font.SysFont("DejaVuSans", 26, bold=True)
f_lab = pygame.font.SysFont("DejaVuSans", 16, bold=True)
f_small = pygame.font.SysFont("DejaVuSans", 13)

# Row 1: day gameplay | night gameplay | hero
row1_h = max(GP_H, HERO)
# Row 2: day 40px | night 40px | (notes)
row2_h = TRUTH
# Row 3: filmstrip
row3_h = FILM_CELL

fig_w = PAD * 4 + GP_W + GP_W + HERO
fig_h = (TITLE_H + PAD + row1_h + LABEL_H + PAD
         + row2_h + LABEL_H + PAD + row3_h + LABEL_H + PAD)

fig = pygame.Surface((fig_w, fig_h))
fig.fill((20, 19, 28))

title = f_title.render(
    "MOONBLOOM MACAW  —  LEGENDARY  (design_4, round 1)", True, (246, 232, 200))
fig.blit(title, (PAD, (TITLE_H - title.get_height()) // 2))
sub = f_small.render(
    "night-flora in moonlight: pearl/lilac body · opened-moonflower crest · "
    "pale-gold moon halo · petal-and-pollen tail",
    True, (180, 170, 200))
fig.blit(sub, (PAD, TITLE_H - 18))


def label(x, y, text, color=(232, 226, 240)):
    fig.blit(f_lab.render(text, True, color), (x, y))


# ── row 1 ──
y = TITLE_H + PAD
x = PAD
fig.blit(gameplay_panel_phase(build, GP_W, GP_H, 0.0), (x, y))
label(x, y + row1_h + 4, "GAMEPLAY · DAY")
x += GP_W + PAD
fig.blit(gameplay_panel_phase(build, GP_W, GP_H, 0.64375), (x, y))
label(x, y + row1_h + 4, "GAMEPLAY · NIGHT")
x += GP_W + PAD
fig.blit(hero_panel(build, HERO, frame_idx=2, tilt=0.0, bg=(26, 24, 38)), (x, y))
label(x, y + row1_h + 4, "HERO · product shot")

# ── row 2 ──
y = TITLE_H + PAD + row1_h + LABEL_H + PAD
x = PAD
fig.blit(truth_read(build, DAY_SKY), (x, y))
label(x, y + TRUTH + 4, "40px TRUTH · DAY", (120, 180, 230))
x += TRUTH + PAD
fig.blit(truth_read(build, NIGHT_SKY), (x, y))
label(x, y + TRUTH + 4, "40px TRUTH · NIGHT", (150, 150, 210))
# notes block
x += TRUTH + PAD
notes = [
    "40px reads are the make-or-break:",
    "the opaque pale-gold moon rim + lilac",
    "petal cores carry on DAY; the additive",
    "moon-glow + pollen are a NIGHT bonus.",
]
for i, ln in enumerate(notes):
    fig.blit(f_small.render(ln, True, (190, 182, 206)), (x, y + 6 + i * 18))

# ── row 3 ──
y = TITLE_H + PAD + row1_h + LABEL_H + PAD + row2_h + LABEL_H + PAD
x = PAD
fig.blit(filmstrip(build, FILM_CELL, bg=(26, 24, 38)), (x, y))
label(x, y + row3_h + 4, "4-FRAME FILMSTRIP (flap anim)")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(fig, os.path.normpath(OUT))
print("wrote", os.path.normpath(OUT), fig.get_size())
