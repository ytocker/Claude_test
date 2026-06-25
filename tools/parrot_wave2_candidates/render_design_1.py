"""Round sheet for design_1 · THORNCREST MACAW.

Lays out the in-gameplay reads the brief demands: a day gameplay panel, a night
gameplay panel, a clean hero product-shot, and a 40px NEAREST truth-read on BOTH
skies (the make-or-break downscale check). Also drops a crest-masked 40px read so
the critic can see the rose body alone holds its silhouette. Exploration only.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import biome
from game.draw import (get_sky_surface_biome, draw_mountains, draw_ground,
                       draw_cloud)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from tools.ninja_render import hero_panel, FRAME_IDX, TILT
from tools.parrot_wave2_candidates import design_1

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "..", "docs", "store_redesign", "parrot", "wave2",
                   "design_1", "round_1.png")


def gameplay_panel_phase(source, w, h, phase, *, frame_idx=FRAME_IDX, tilt=TILT):
    """Pip mid-flight over a real biome scene at a chosen day/night phase."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    bucket = biome.phase_bucket(phase)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, bucket), (0, 0))
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


def truth_read(source, sky_rgb, *, box=160, crest_label=None):
    """A 40px NEAREST downscale of the bird on a flat sky swatch, then upscaled
    NEAREST to `box` so the pixel-truth at gameplay size is legible — the read
    that decides whether the skin lives or dies."""
    frame = source(FRAME_IDX, TILT)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy() if bb.width else frame
    sw, sh = frame.get_size()
    scale = 40 / max(sw, sh)
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    panel = pygame.Surface((box, box))
    panel.fill(sky_rgb)
    up = pygame.transform.scale(small, (small.get_width() * 3, small.get_height() * 3))
    panel.blit(up, up.get_rect(center=(box // 2, box // 2)))
    return panel


# Sky swatches: a bright day cyan + a deep night navy from the biome palettes.
DAY_SKY = biome.palette_for_phase(0.0)['sky_top']
NIGHT_SKY = biome.palette_for_phase(0.64375)['sky_top']

PW, PH = 230, 320
HERO = 320
TR = 160
PAD = 16
TITLE_H = 60
LABEL_H = 30

f_title = pygame.font.SysFont("DejaVuSans", 26, bold=True)
f_sub = pygame.font.SysFont("DejaVuSans", 15, bold=True)
f_lbl = pygame.font.SysFont("DejaVuSans", 14, bold=True)

# Layout: top row = day gameplay | night gameplay | hero. Bottom row = 4 truth
# reads (day full, night full, day crest-masked, night crest-masked).
top_h = PH + LABEL_H
tr_h = TR + LABEL_H
fig_w = PAD + PW + PAD + PW + PAD + HERO + PAD
fig_h = TITLE_H + top_h + PAD + tr_h + PAD

fig = pygame.Surface((fig_w, fig_h))
fig.fill((18, 18, 26))

title = f_title.render("THORNCREST MACAW — EPIC  ·  round 1", True, (242, 200, 210))
fig.blit(title, (PAD, 14))
sub = f_sub.render("briar-rose crest over a deep rose-red macaw  ·  matte, no glow",
                   True, (170, 150, 160))
fig.blit(sub, (PAD, 40))


def label(x, y, w, text, col=(225, 225, 232)):
    strip = pygame.Rect(x, y, w, LABEL_H)
    pygame.draw.rect(fig, (30, 30, 42), strip)
    t = f_lbl.render(text, True, col)
    fig.blit(t, (x + 6, y + 7))


# ── top row ──────────────────────────────────────────────────────────────────
x = PAD
y = TITLE_H
day = gameplay_panel_phase(design_1.build, PW, PH, 0.0)
fig.blit(day, (x, y)); label(x, y + PH, PW, "GAMEPLAY · DAY")
x += PW + PAD
night = gameplay_panel_phase(design_1.build, PW, PH, 0.64375)
fig.blit(night, (x, y)); label(x, y + PH, PW, "GAMEPLAY · NIGHT")
x += PW + PAD
hero = hero_panel(design_1.build, HERO, tilt=0.0, bg=(28, 22, 30))
# centre the hero box in its taller column slot
fig.blit(hero, (x, y))
label(x, y + PH, HERO, "HERO PRODUCT-SHOT")

# ── bottom row: four 40px truth reads ──────────────────────────────────────────
y2 = TITLE_H + top_h + PAD
cells = [
    (design_1.build, DAY_SKY, "40px TRUTH · DAY"),
    (design_1.build, NIGHT_SKY, "40px TRUTH · NIGHT"),
    (design_1.build_no_crest, DAY_SKY, "40px BODY-ONLY · DAY"),
    (design_1.build_no_crest, NIGHT_SKY, "40px BODY-ONLY · NIGHT"),
]
x = PAD
for src, sky, lbl in cells:
    panel = truth_read(src, sky, box=TR)
    fig.blit(panel, (x, y2))
    label(x, y2 + TR, TR, lbl)
    x += TR + PAD

os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(fig, os.path.normpath(OUT))
print("wrote", os.path.normpath(OUT), fig.get_size())
