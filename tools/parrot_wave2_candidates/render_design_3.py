"""Round-1 review sheet for design_3 · CONSTELLATION MACAW (legendary).

Composites the candidate via the shared ninja_render harness (so the previews
match the deliverable): day + night in-gameplay panels, a clean hero shot, a
40px NEAREST truth-read on BOTH skies (does the gold chart survive downscale?),
and a 4-frame filmstrip (legendary). Exploration only — touches no production
art. Writes docs/store_redesign/parrot/wave2/design_3/round_1.png.
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
from tools.ninja_render import gameplay_panel, hero_panel, _frame, FRAME_IDX, TILT
from tools.parrot_wave2_candidates.design_3 import build

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "..", "docs", "store_redesign", "parrot", "wave2",
                   "design_3", "round_2.png")

NIGHT_PHASE = 0.64375     # NIGHT keyframe — the dark-sky stress test


def night_gameplay_panel(source, w, h, *, frame_idx=FRAME_IDX, tilt=TILT):
    """gameplay_panel's twin on the NIGHT biome palette — the dark sky where the
    additive gold bloom must twinkle and the lapis body must not vanish."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(NIGHT_PHASE)
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
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def truth_read(source, sky_rgb, box=40):
    """The 40px NEAREST truth-read: the bird on a flat sky-coloured tile, scaled
    DOWN to 40px with no smoothing, then back UP nearest so the reviewer sees the
    exact pixels the store card renders. Two tiles (day + night sky) catch the
    fail where gold lines either vanish into the body or wash out on bright sky."""
    big = 120
    tile = pygame.Surface((big, big))
    tile.fill(sky_rgb)
    frame = _frame(source, FRAME_IDX, TILT)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = (big * 0.86) / max(sw, sh)
    frame = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    tile.blit(frame, frame.get_rect(center=(big // 2, big // 2)))
    small = pygame.transform.scale(tile, (box, box))            # nearest down
    return pygame.transform.scale(small, (big, big))            # nearest up


# ── compose the sheet ─────────────────────────────────────────────────────────
f_title = pygame.font.SysFont("DejaVuSans", 26, bold=True)
f_sub = pygame.font.SysFont("DejaVuSans", 15, bold=True)
f_lbl = pygame.font.SysFont("DejaVuSans", 14, bold=True)

PAD = 16
TITLE_H = 70
GP_W, GP_H = 210, 300          # gameplay panel (matches the comparison-figure crop)
HERO = 300                     # hero box
TR = 120                       # truth-read tile (upscaled)
FS = 110                       # filmstrip frame box

fig_w = PAD * 4 + GP_W * 2 + HERO
top_h = TITLE_H + GP_H + 30
strip_h = max(TR + 40, FS + 40)
fig_h = top_h + PAD + strip_h + PAD

fig = pygame.Surface((fig_w, fig_h))
fig.fill((18, 18, 26))

fig.blit(f_title.render("design_3 · CONSTELLATION MACAW · round 2", True,
                        (240, 240, 245)), (PAD, 14))
fig.blit(f_sub.render("LEGENDARY — gold star-chart on lapis · orbital halo · "
                      "crescent crest · comet tail", True, (255, 200, 90)),
         (PAD, 46))

# Row 1: day gameplay · night gameplay · hero
y0 = TITLE_H
x = PAD
for label, panel in (
        ("IN-GAMEPLAY · DAY SKY", gameplay_panel(build, GP_W, GP_H)),
        ("IN-GAMEPLAY · NIGHT SKY", night_gameplay_panel(build, GP_W, GP_H))):
    fig.blit(panel, (x, y0))
    fig.blit(f_lbl.render(label, True, (220, 220, 230)), (x, y0 + GP_H + 6))
    x += GP_W + PAD

hero = hero_panel(build, HERO, frame_idx=FRAME_IDX, tilt=8.0, bg=(20, 22, 40))
fig.blit(hero, (x, y0))
fig.blit(f_lbl.render("HERO (clean read)", True, (220, 220, 230)),
         (x, y0 + HERO + 6))

# Row 2: 40px truth-reads (day + night) · 4-frame filmstrip
y1 = top_h + PAD
x = PAD
fig.blit(f_sub.render("40px NEAREST truth-read", True, (230, 230, 235)), (x, y1 - 2))
day_sky = biome.palette_for_phase(0.0)['sky_top']
night_sky = biome.palette_for_phase(NIGHT_PHASE)['sky_top']
ty = y1 + 22
for label, sky in (("day sky", day_sky), ("night sky", night_sky)):
    fig.blit(truth_read(build, sky), (x, ty))
    fig.blit(f_lbl.render(label, True, (210, 210, 220)), (x, ty + TR + 4))
    x += TR + PAD

# Filmstrip — 4 wing frames on a flat night-ish panel so the flap + baked
# halo/comet drift read across the animation.
x += PAD
fig.blit(f_sub.render("4-frame filmstrip (flap)", True, (230, 230, 235)), (x, y1 - 2))
fy = y1 + 22
for i in range(4):
    cell = pygame.Surface((FS, FS), pygame.SRCALPHA)
    pygame.draw.rect(cell, (24, 26, 46), cell.get_rect(), border_radius=10)
    fr = _frame(build, i, 6.0)
    bb = fr.get_bounding_rect()
    if bb.width and bb.height:
        fr = fr.subsurface(bb).copy()
    sw, sh = fr.get_size()
    sc = (FS * 0.84) / max(sw, sh)
    fr = pygame.transform.smoothscale(fr, (max(1, int(sw * sc)), max(1, int(sh * sc))))
    cell.blit(fr, fr.get_rect(center=(FS // 2, FS // 2)))
    fig.blit(cell, (x, fy))
    fig.blit(f_lbl.render(f"f{i}", True, (200, 200, 210)), (x + 4, fy + FS + 2))
    x += FS + 8

os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(fig, os.path.normpath(OUT))
print("wrote", os.path.normpath(OUT), fig.get_size())
