"""Animal skin category overview figure.

Renders every registered animal skin (all 27 entries in store_catalog
group="animal") mid-flight over a real daytime biome scene, laid out in
a labeled grid. Secret items are shown with a "SECRET" badge.

Usage (from repo root):
    SDL_VIDEODRIVER=dummy python tools/render_animal_overview.py
Output:
    docs/store_redesign/animal/animal_overview.png
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()

from game import biome, store_catalog, parrot
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y

# All animal skins in catalog order (cost-ascending)
ANIMALS = [
    (sid, store_catalog.CATALOG[sid]["name"],
     store_catalog.CATALOG[sid].get("secret", False))
    for sid in store_catalog.ids_of_group("animal")
]

COLS = 6
ROWS = -(-len(ANIMALS) // COLS)   # ceiling division

PANEL_W, PANEL_H = 168, 120
LABEL_H = 36
PAD = 10
CELL_W = PANEL_W + PAD
CELL_H = PANEL_H + LABEL_H + PAD

SHEET_W = PAD + COLS * CELL_W
SHEET_H = PAD + ROWS * CELL_H + 50   # 50px title bar

BG        = (14, 13, 22)
TITLE_FG  = (240, 235, 255)
LABEL_BG  = (28, 25, 44)
LABEL_FG  = (210, 205, 230)
SECRET_FG = (255, 200, 80)
BORDER    = (52, 46, 80)


def _font(size, bold=False):
    try:
        return pygame.font.SysFont("dejavusansmono,monospace", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size + 4)


def _gameplay_panel(sid, w, h):
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.0)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette["mtn_far"], palette["mtn_near"])
    Pipe(x=12,  gap_y=250, gap_h=185).draw(scene, palette)
    Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette["ground_top"], palette["ground_mid"], (60, 40, 25))
    pip_cx, pip_cy = 96, 270
    frame = parrot.get_skin_frame(sid, 2, 10.0)
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


def _label_cell(name, is_secret, w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill(LABEL_BG)
    pygame.draw.rect(surf, BORDER, surf.get_rect(), 1, border_radius=4)
    f = _font(11, bold=True)
    fg = SECRET_FG if is_secret else LABEL_FG
    display = ("??? " if is_secret else "") + name
    txt = f.render(display, True, fg)
    surf.blit(txt, txt.get_rect(center=(w // 2, h // 2)))
    return surf


# ── build sheet ───────────────────────────────────────────────────────────────
sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill(BG)

# Title bar
title_f = _font(16, bold=True)
title = title_f.render(f"ANIMAL SKINS  ({len(ANIMALS)} items)", True, TITLE_FG)
sheet.blit(title, title.get_rect(centerx=SHEET_W // 2, top=14))

for idx, (sid, name, is_secret) in enumerate(ANIMALS):
    col = idx % COLS
    row = idx // COLS
    x = PAD + col * CELL_W
    y = 50 + PAD + row * CELL_H

    try:
        gp = _gameplay_panel(sid, PANEL_W, PANEL_H)
    except Exception as exc:
        gp = pygame.Surface((PANEL_W, PANEL_H))
        gp.fill((60, 20, 20))
        err = _font(10).render(str(exc)[:28], True, (255, 80, 80))
        gp.blit(err, (4, PANEL_H // 2))

    pygame.draw.rect(sheet, BORDER,
                     pygame.Rect(x - 1, y - 1, PANEL_W + 2, PANEL_H + 2), 1)
    sheet.blit(gp, (x, y))
    lbl = _label_cell(name, is_secret, PANEL_W, LABEL_H - 2)
    sheet.blit(lbl, (x, y + PANEL_H + 2))

out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "store_redesign", "animal")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "animal_overview.png")
pygame.image.save(sheet, out_path)
print(f"Saved {out_path}")
