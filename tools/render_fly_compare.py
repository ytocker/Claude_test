"""Final comparison figure for the FLY animal-skin exploration.

Renders all 5 candidate designs side by side, each as Pip mid-flight over a
real daytime biome scene, plus a hero product-shot and a 40px truth read.
Saves docs/store_redesign/animal/fly/final_comparison.png.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()

from tools.fly_candidates.design_1 import build as build1
from tools.fly_candidates.design_2 import build as build2
from tools.fly_candidates.design_3 import build as build3
from tools.fly_candidates.design_4 import build as build4
from tools.fly_candidates.design_5 import build as build5

from game import biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

DESIGNS = [
    (build1, "DESIGN 1\nBLOWFLY BARON"),
    (build2, "DESIGN 2\nBUZZ THE HOUSEFLY"),
    (build3, "DESIGN 3\nVOLT-WING"),
    (build4, "DESIGN 4\nMORTIMER DEATHFLY"),
    (build5, "DESIGN 5\nPOP FLY"),
]

PANEL_W, PANEL_H = 280, 195
HERO_BOX = 195
TRUTH_W, TRUTH_H = 280, 65
PAD = 12
LABEL_H = 44
COL_W = PANEL_W + PAD
N = len(DESIGNS)

SHEET_W = PAD + N * COL_W
SHEET_H = PAD + LABEL_H + PANEL_H + PAD + HERO_BOX + PAD + TRUTH_H + PAD

BG = (18, 16, 28)
LABEL_FG = (220, 215, 235)
LABEL_BG = (32, 28, 50)


def _gameplay_panel(build_fn, w, h):
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.0)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=12, gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = build_fn(2, 10.0)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    crop_h = min(int(GH * 0.78), GH)
    crop_w = int(crop_h * w / h)
    if crop_w > GW:
        crop_w = GW
        crop_h = int(crop_w * h / w)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx + 20, pip_cy - 20)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))


def _hero_panel(build_fn, box):
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, (22, 20, 32), panel.get_rect(), border_radius=14)
    frame = build_fn(2, 0.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = (box * 0.82) / max(sw, sh)
    frame = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    panel.blit(frame, frame.get_rect(center=(box // 2, box // 2)))
    return panel


def _truth_strip(build_fn, w, h):
    strip = pygame.Surface((w, h), pygame.SRCALPHA)
    strip.fill((22, 20, 32))
    for fi in range(4):
        fr = build_fn(fi, 0.0)
        fr_h = int(40 * fr.get_height() / fr.get_width())
        fr40 = pygame.transform.scale(fr, (40, fr_h))
        strip.blit(fr40, (fi * (w // 4) + (w // 8) - 20, (h - fr_h) // 2))
    return strip


def _label(text, w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill(LABEL_BG)
    pygame.draw.rect(surf, (50, 44, 75), surf.get_rect(), 1, border_radius=6)
    try:
        font = pygame.font.SysFont("dejavusansmono,monospace", 13, bold=True)
    except Exception:
        font = pygame.font.Font(None, 16)
    lines = text.split("\n")
    total_h = len(lines) * 17
    y0 = (h - total_h) // 2
    for i, line in enumerate(lines):
        t = font.render(line, True, LABEL_FG)
        surf.blit(t, t.get_rect(centerx=w // 2, top=y0 + i * 17))
    return surf


sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill(BG)

for col, (build_fn, name) in enumerate(DESIGNS):
    x = PAD + col * COL_W
    y = PAD

    lbl = _label(name, PANEL_W, LABEL_H)
    sheet.blit(lbl, (x, y))
    y += LABEL_H + 4

    gp = _gameplay_panel(build_fn, PANEL_W, PANEL_H)
    sheet.blit(gp, (x, y))
    y += PANEL_H + PAD

    hp = _hero_panel(build_fn, HERO_BOX)
    sheet.blit(hp, (x + (PANEL_W - HERO_BOX) // 2, y))
    y += HERO_BOX + PAD

    ts = _truth_strip(build_fn, PANEL_W, TRUTH_H)
    sheet.blit(ts, (x, y))

out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "store_redesign", "animal", "fly")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "final_comparison.png")
pygame.image.save(sheet, out_path)
print(f"Saved {out_path}")
