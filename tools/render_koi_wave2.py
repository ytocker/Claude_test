"""Round-1 exploration sheet for design_2 · KOI MACAW (wave2 epic).

In-gameplay truth read: a day gameplay panel + a night gameplay panel (the
flap-driven fin streamers must hold on both skies), a clean hero close-up, a
4-frame flap filmstrip (so the streamer sway reads), and a 40px NEAREST
truth-read — the north star "lives or dies at 40px in motion". Pure capture;
the candidate is a scratch builder under tools/parrot_wave2_candidates/.
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
from game.hud import _font, _GOLD_PALE
import tools.ninja_render as nr
from tools.parrot_wave2_candidates.design_2 import build as KOI


def gameplay_panel(source, w, h, phase, *, frame_idx=2, tilt=10.0):
    """nr.gameplay_panel is daytime-only; reproduce it with a chosen biome
    phase so day (0.0) and night (~0.64) reads both get captured."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, biome.phase_bucket(phase)), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pcx, pcy = 96, 270
    frame = KOI(frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pcx, pcy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pcx + 34, pcy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def truth40(frame_idx, tilt, bg):
    """Render the bird, downscale to 40px tall with NEAREST (no smoothing), then
    upscale NEAREST so the pixels show — the honest 'in motion at distance' read."""
    f = KOI(frame_idx, tilt)
    bb = f.get_bounding_rect()
    f = f.subsurface(bb).copy()
    sw, sh = f.get_size()
    sc = 40 / sh
    small = pygame.transform.scale(f, (max(1, int(sw * sc)), 40))
    big = pygame.transform.scale(small, (small.get_width() * 4, small.get_height() * 4))
    tile = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    tile.fill(bg)
    tile.blit(big, (0, 0))
    return tile


PANEL_W, PANEL_H = 240, 470
HERO = 320
PAD, GUT = 28, 18
TITLE_H = 76

# Layout: title; row of [day gameplay | night gameplay | hero] ; row of
# [4-frame filmstrip] ; row of [40px truth on day + on night].
sheet_w = PAD * 2 + PANEL_W * 2 + HERO + GUT * 2
sheet_h = TITLE_H + PANEL_H + 250 + 180 + PAD * 3
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 26))

title = _font(28, True).render(
    "KOI MACAW — EPIC  ·  wave2 design_2  ·  round 2  ·  swept webbed fin crest + 2 cool-tipped streamers",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 22)))

lab = _font(15, True)
sub = _font(12, False)


def caption(x, y, name, note):
    sheet.blit(lab.render(name, True, _GOLD_PALE), (x, y))
    sheet.blit(sub.render(note, True, (170, 162, 190)), (x, y + 18))


# Row 1 — day / night gameplay + hero.
y0 = TITLE_H
day = gameplay_panel(KOI, PANEL_W, PANEL_H, 0.0)
night = gameplay_panel(KOI, PANEL_W, PANEL_H, 0.64375)
sheet.blit(day, (PAD, y0))
sheet.blit(night, (PAD + PANEL_W + GUT, y0))
hero = nr.hero_panel(KOI, HERO, tilt=0.0, bg=(30, 24, 36))
sheet.blit(hero, (PAD + PANEL_W * 2 + GUT * 2, y0 + (PANEL_H - HERO) // 2))
caption(PAD, y0 + PANEL_H + 6, "GAMEPLAY · DAY", "mid-flight over real biome")
caption(PAD + PANEL_W + GUT, y0 + PANEL_H + 6, "GAMEPLAY · NIGHT", "fins must hold on dark sky")
caption(PAD + PANEL_W * 2 + GUT * 2, y0 + PANEL_H + 6, "HERO CLOSE-UP", "judge marbling + crest detail")

# Row 2 — 4-frame flap filmstrip (streamer sway).
y1 = y0 + PANEL_H + 40
strip_box = 200
fx = PAD
for i in range(4):
    h = nr.hero_panel(KOI, strip_box, frame_idx=i, tilt=8.0, bg=(26, 22, 34))
    sheet.blit(h, (fx, y1))
    fx += strip_box + GUT
caption(PAD, y1 + strip_box + 6, "FLAP FILMSTRIP", "fin streamers + bubbles sway with the wing beat (frames 0-3)")

# Row 3 — 40px NEAREST truth-read on day + night backgrounds.
y2 = y1 + strip_box + 46
tx = PAD
for bg, tag in (((150, 205, 224), "on day sky"), ((26, 32, 58), "on night sky")):
    t = truth40(2, 10.0, bg)
    sheet.blit(t, (tx, y2))
    caption(tx, y2 + t.get_height() + 4, "40px TRUTH", tag)
    tx += t.get_width() + GUT * 3

out = os.path.join("docs", "store_redesign", "parrot", "wave2", "design_2", "round_2.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
