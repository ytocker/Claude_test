"""Round sheet for GLACIER MACAW (wave2 design_1) — scratch exploration only.

Renders the candidate `build` in-gameplay so the preview matches how the skin
actually reads in play: a DAY and a NIGHT gameplay panel (the cold blue body
must hold on both skies), a clean hero close-up for detail, and the make-or-
break 40px NEAREST truth-read on day + night. Reuses tools.ninja_render's
biome compose; the night panel re-implements its day compose at a night phase
since the harness day panel is pinned to phase 0.0.
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
from game.hud import _font, _GOLD_PALE

build = importlib.import_module("tools.parrot_wave2_candidates.design_1").build


def gameplay_panel_phase(source, w, h, phase, *, frame_idx=2, tilt=10.0):
    """ninja_render.gameplay_panel, but at an arbitrary biome phase so we can
    show the same scene on a night sky."""
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


def truth_read_40(source, bg, *, frame_idx=2, tilt=10.0):
    """The make-or-break: the bird downscaled to 40px with NEAREST so we judge
    what actually survives at store-thumbnail size, on a tinted sky swatch."""
    frame = source(frame_idx, tilt)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40 / max(sw, sh)
    tiny = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    box = 64
    panel = pygame.Surface((box, box))
    panel.fill(bg)
    panel.blit(tiny, tiny.get_rect(center=(box // 2, box // 2)))
    return panel


# Layout: title, then a row of 5 panels — day gameplay, night gameplay, hero,
# 40px day, 40px night.
GP_W, GP_H = 240, 380
HERO = 380
TRUTH = 64
PAD, GUT = 28, 18
TITLE_H, CAP_H = 78, 30

panels = [
    ("DAY · IN-GAMEPLAY",   GP_W),
    ("NIGHT · IN-GAMEPLAY", GP_W),
    ("HERO CLOSE-UP",       HERO),
    ("40px DAY",            TRUTH * 2),
    ("40px NIGHT",          TRUTH * 2),
]
xs = []
x = PAD
for _, w in panels:
    xs.append(x)
    x += w + GUT
sheet_w = x - GUT + PAD
sheet_h = TITLE_H + GP_H + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((16, 18, 28))

title = _font(26, True).render(
    "GLACIER MACAW — EPIC  ·  wave2 design_1  ·  round 1  (the frozen counterpart to MAGMA)",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 22)))

cap_font = _font(13, True)
EPIC_COL = (108, 188, 252)   # icy border to suit the cold tier
y = TITLE_H

# Day + night gameplay.
day = gameplay_panel_phase(build, GP_W, GP_H, 0.0)
night = gameplay_panel_phase(build, GP_W, GP_H, 0.5)
sheet.blit(day, (xs[0], y))
sheet.blit(night, (xs[1], y))
for xi in (0, 1):
    pygame.draw.rect(sheet, EPIC_COL,
                     pygame.Rect(xs[xi] - 2, y - 2, GP_W + 4, GP_H + 4), width=2)

# Hero on a deep-navy card (matches the store card); box matched to row height.
hero = nr.hero_panel(build, GP_H, bg=(20, 26, 40))
sheet.blit(hero, (xs[2], y))
pygame.draw.rect(sheet, EPIC_COL,
                 pygame.Rect(xs[2] - 2, y - 2, GP_H + 4, GP_H + 4), width=2)

# Truth reads on day + night sky swatches, scaled up 2x NEAREST for the sheet
# (so the 40px render is visible) and stacked with a value-context swatch.
DAY_SKY = (120, 175, 220)
NIGHT_SKY = (28, 30, 70)
for xi, bg in ((3, DAY_SKY), (4, NIGHT_SKY)):
    t = truth_read_40(build, bg)
    t2 = pygame.transform.scale(t, (TRUTH * 2, TRUTH * 2))
    sheet.blit(t2, (xs[xi], y))
    pygame.draw.rect(sheet, EPIC_COL,
                     pygame.Rect(xs[xi] - 2, y - 2, TRUTH * 2 + 4, TRUTH * 2 + 4), width=2)

# Captions.
cy = y + GP_H + 8
for (label, w), xx in zip(panels, xs):
    sheet.blit(cap_font.render(label, True, (180, 200, 220)), (xx, cy))

out = os.path.join("docs", "store_redesign", "parrot", "wave2", "design_1", "round_1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
