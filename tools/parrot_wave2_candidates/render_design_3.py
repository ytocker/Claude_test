"""Round sheet for design_3 · EMBERMOTH MACAW (epic).

Lays out the in-gameplay reads the brief demands: a day gameplay panel, a night
gameplay panel, a clean hero product-shot, and a 40px NEAREST truth-read on BOTH
skies (the make-or-break downscale check for the eyespot tell + comb-plume). Also
drops a crest-masked 40px read so the critic can see the charcoal-mauve body
alone holds its silhouette on both biomes. Exploration only.
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
from tools.ninja_render import FRAME_IDX, TILT
from tools.parrot_wave2_candidates import design_3, design_1

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "..", "docs", "store_redesign", "parrot", "wave2",
                   "design_3", os.environ.get("ROUND_PNG", "round_1.png"))


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


def truth_read(source, sky_rgb, *, box=160):
    """A 40px NEAREST downscale of the bird on a flat sky swatch, then upscaled
    NEAREST to `box` so the pixel-truth at gameplay size is legible — the read
    that decides whether the eyespot tell + comb-plume survive."""
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


def hero_panel_crisp(source, box, *, frame_idx=FRAME_IDX, tilt=0.0, bg=(26, 20, 28)):
    """A CRISP, MATTE product-shot: the bird scaled up by an INTEGER NEAREST factor
    so the storefront thumbnail keeps the same pigment finish as the truth tiles —
    no smoothscale blur, no soft focus that would mis-sell the matte tier as
    legendary-glowy."""
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, bg, panel.get_rect(), border_radius=14)
    frame = source(frame_idx, tilt)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    # Largest integer factor that still fits within ~82% of the box — NEAREST so
    # every pixel stays hard-edged.
    factor = max(1, int((box * 0.82) / max(sw, sh)))
    big = pygame.transform.scale(frame, (sw * factor, sh * factor))
    panel.blit(big, big.get_rect(center=(box // 2, box // 2)))
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
# Bottom row now carries 5 truth tiles (the 4 EMBERMOTH reads + a THORNCREST
# night tile for the distinctness comparison), so the figure widens to fit them.
N_TR = 5
fig_w = max(PAD + PW + PAD + PW + PAD + HERO + PAD,
            PAD + N_TR * (TR + PAD))
fig_h = TITLE_H + top_h + PAD + tr_h + PAD

fig = pygame.Surface((fig_w, fig_h))
fig.fill((18, 16, 22))

title = f_title.render(
    "EMBERMOTH MACAW — EPIC  ·  " + os.environ.get("ROUND_LABEL", "round 1"),
    True, (236, 200, 158))
fig.blit(title, (PAD, 14))
sub = f_sub.render("forked moth-antenna plume + eyespot disc over a charcoal-mauve "
                   "macaw  ·  matte velvet, no glow", True, (160, 140, 150))
fig.blit(sub, (PAD, 40))


def label(x, y, w, text, col=(225, 225, 232)):
    strip = pygame.Rect(x, y, w, LABEL_H)
    pygame.draw.rect(fig, (30, 28, 38), strip)
    t = f_lbl.render(text, True, col)
    fig.blit(t, (x + 6, y + 7))


# ── top row ──────────────────────────────────────────────────────────────────
x = PAD
y = TITLE_H
day = gameplay_panel_phase(design_3.build, PW, PH, 0.0)
fig.blit(day, (x, y)); label(x, y + PH, PW, "GAMEPLAY · DAY")
x += PW + PAD
night = gameplay_panel_phase(design_3.build, PW, PH, 0.64375)
fig.blit(night, (x, y)); label(x, y + PH, PW, "GAMEPLAY · NIGHT")
x += PW + PAD
hero = hero_panel_crisp(design_3.build, HERO, tilt=0.0, bg=(26, 20, 28))
fig.blit(hero, (x, y))
label(x, y + PH, HERO, "HERO PRODUCT-SHOT · CRISP+MATTE")

# ── bottom row: four 40px truth reads ──────────────────────────────────────────
y2 = TITLE_H + top_h + PAD
# The THORNCREST night tile sits beside the EMBERMOTH night read so the critic
# can prove the moth fork + ocellus cannot be mistaken for a rose-red briar crest
# on navy — the two EPIC crests must be unmistakably distinct at 40px.
cells = [
    (design_3.build, DAY_SKY, "40px TRUTH · DAY", (225, 225, 232)),
    (design_3.build, NIGHT_SKY, "40px TRUTH · NIGHT", (225, 225, 232)),
    (design_3.build_no_crest, DAY_SKY, "40px BODY-ONLY · DAY", (225, 225, 232)),
    (design_3.build_no_crest, NIGHT_SKY, "40px BODY-ONLY · NIGHT", (225, 225, 232)),
    (design_1.build, NIGHT_SKY, "THORNCREST · NIGHT (compare)", (236, 168, 180)),
]
x = PAD
for src, sky, lbl, col in cells:
    panel = truth_read(src, sky, box=TR)
    fig.blit(panel, (x, y2))
    label(x, y2 + TR, TR, lbl, col=col)
    x += TR + PAD

os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(fig, os.path.normpath(OUT))
print("wrote", os.path.normpath(OUT), fig.get_size())
