"""Round-1 render sheet for DESIGN 5 — NIGHT MATCH (tennis).

In-gameplay reads for the night-match tennis costume: a DAY gameplay panel and a
NIGHT gameplay panel (so the night-sky pop can be judged), a clean hero product
shot, and a 40px NEAREST "truth read" of the bird in DAY and NIGHT so the
downscale legibility of the racket + polo is visible. Scratch only — touches no
production art.

Headless: ``SDL_VIDEODRIVER=dummy python tools/render_tennis_d5.py``.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

import tools.ninja_render as nr
from tools.tennis_candidates.design_5 import build as SOURCE
from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP


def gameplay_panel_phase(source, w, h, phase):
    """nr.gameplay_panel, but at an arbitrary biome phase so we can render the
    same scene by day AND by night."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(phase)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette,
                                     palette.get('star_alpha', 0)), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = nr._frame(source, nr.FRAME_IDX, nr.TILT)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = int(GH * 0.78)
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 34, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def truth_read(source, phase, box=120):
    """The bird raw-rendered then NEAREST-downscaled to 40px and blown back up —
    the honest 'does it read at thumbnail size' test — on the phase's sky tint."""
    palette = biome.palette_for_phase(phase)
    frame = nr._frame(source, nr.FRAME_IDX, nr.TILT)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    s = 40 / max(sw, sh)
    small = pygame.transform.smoothscale(frame, (max(1, int(sw * s)), max(1, int(sh * s))))
    big = pygame.transform.scale(small, (box, box))  # NEAREST blow-up
    panel = pygame.Surface((box, box))
    panel.fill(palette['sky_mid'])
    panel.blit(big, big.get_rect(center=(box // 2, box // 2)))
    return panel


DAY, NIGHT = 0.0, 0.64375

PANEL_W, PANEL_H = 240, 400
HERO = 300
TRUTH = 150
PAD, GUT = 28, 20
TITLE_H = 70

# Layout: [day gameplay][night gameplay][hero] across the top row; truth reads
# (day + night) tucked under the hero.
top_w = PANEL_W * 2 + HERO + GUT * 2
sheet_w = PAD * 2 + top_w
sheet_h = TITLE_H + PANEL_H + 60 + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((16, 18, 26))

title = _font(30, True).render(
    "TENNIS — DESIGN 5: NIGHT MATCH (hard-court blue) — round 1", True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 20)))

cap = _font(15, True)
x = PAD
y = TITLE_H

for label, ph in (("DAY — gameplay", DAY), ("NIGHT — gameplay", NIGHT)):
    panel = gameplay_panel_phase(SOURCE, PANEL_W, PANEL_H, ph)
    pygame.draw.rect(sheet, _GOLD_DEEP, (x - 2, y - 2, PANEL_W + 4, PANEL_H + 4), 2)
    sheet.blit(panel, (x, y))
    sheet.blit(cap.render(label, True, (180, 174, 200)), (x + 2, y + PANEL_H + 8))
    x += PANEL_W + GUT

# Hero shot + the two truth reads stacked beside it.
hero = nr.hero_panel(SOURCE, HERO, tilt=0.0)
sheet.blit(hero, (x, y))
sheet.blit(cap.render("HERO (product shot)", True, (180, 174, 200)),
           (x + 2, y + HERO + 8))

ty = y + HERO + 36
for label, ph in (("40px DAY", DAY), ("40px NIGHT", NIGHT)):
    tp = truth_read(SOURCE, ph, TRUTH)
    tx = x + (0 if label.endswith("DAY") else TRUTH + GUT)
    sheet.blit(tp, (tx, ty))
    sheet.blit(cap.render(label, True, (180, 174, 200)), (tx + 2, ty + TRUTH + 4))

out = os.path.join("docs", "store_redesign", "costume", "tennis", "design_5", "round_1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
