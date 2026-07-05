"""ONE comparison figure for the PARTY HAT redesign: the live ORIGINAL skin plus
the 5 final candidate builders, each Pip mid-flight over a real gameplay biome
scene, side by side. Scratch/deliverable tooling — touches no production art."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.hat_skins  # noqa: F401 — registers the live skin_hat_partyhat
from tools.ninja_render import _frame
from game import biome
from game.draw import (get_sky_surface_biome, draw_mountains, draw_ground,
                       draw_cloud)
from game.entities import Pipe
from game.config import W as GW, H as GH, GROUND_Y


def gameplay_panel(source, w, h, *, frame_idx=2, tilt=10.0):
    """Pip mid-flight over a real biome scene, cropped TIGHT around the bird so
    the hat reads clearly in a side-by-side comparison."""
    scene = pygame.Surface((GW, GH))
    palette = biome.palette_for_phase(0.0)
    scene.blit(get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0), (0, 0))
    for bx, by, sc, variant in ((40, 90, 0.9, 0), (260, 120, 1.1, 2), (300, 60, 0.7, 1)):
        draw_cloud(scene, bx, by, sc, variant=variant)
    draw_mountains(scene, 40.0, GROUND_Y, GW, palette['mtn_far'], palette['mtn_near'])
    Pipe(x=8, gap_y=250, gap_h=190).draw(scene, palette)
    Pipe(x=250, gap_y=300, gap_h=180).draw(scene, palette)
    draw_ground(scene, GROUND_Y, GW, GH, 40.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    pip_cx, pip_cy = 150, 250
    frame = _frame(source, frame_idx, tilt)
    scene.blit(frame, frame.get_rect(center=(pip_cx, pip_cy)))
    # Tight crop: ~96px tall window around the bird's head+body, scaled up.
    crop_h = 104
    crop_w = int(crop_h * w / h)
    crop = pygame.Rect(0, 0, crop_w, crop_h)
    crop.center = (pip_cx, pip_cy - 6)
    crop.clamp_ip(pygame.Rect(0, 0, GW, GH))
    return pygame.transform.smoothscale(scene.subsurface(crop).copy(), (w, h))

PANEL_W, PANEL_H = 240, 360
PAD = 16
LABEL_H = 30
COLS = 3
ROWS = 2

# (label, source) — source is a sid string (live) or a build callable (candidate)
def _build(n):
    mod = importlib.import_module(f"tools.partyhat_candidates.design_{n}")
    return mod.build

CELLS = [
    ("ORIGINAL", "skin_hat_partyhat"),
    ("DESIGN 1 · CONFETTI CONE", _build(1)),
    ("DESIGN 2 · BIRTHDAY CROWN", _build(2)),
    ("DESIGN 3 · JESTER CAP", _build(3)),
    ("DESIGN 4 · NYE TOP HAT", _build(4)),
    ("DESIGN 5 · BALLOON BOUQUET", _build(5)),
]

W = COLS * PANEL_W + (COLS + 1) * PAD
H = ROWS * (PANEL_H + LABEL_H) + (ROWS + 1) * PAD + 30

canvas = pygame.Surface((W, H))
canvas.fill((18, 18, 28))

title_font = pygame.font.SysFont("DejaVuSans,Arial", 22, bold=True)
lbl_font = pygame.font.SysFont("DejaVuSans,Arial", 16, bold=True)

title = title_font.render("PARTY HAT redesign — original vs. 5 finals (in gameplay)",
                          True, (255, 210, 90))
canvas.blit(title, (PAD, 8))

for i, (label, source) in enumerate(CELLS):
    col = i % COLS
    row = i // COLS
    x = PAD + col * (PANEL_W + PAD)
    y = 30 + PAD + row * (PANEL_H + LABEL_H + PAD)

    panel = gameplay_panel(source, PANEL_W, PANEL_H)
    canvas.blit(panel, (x, y))

    col_txt = (150, 200, 255) if i == 0 else (235, 240, 255)
    t = lbl_font.render(label, True, col_txt)
    canvas.blit(t, (x + (PANEL_W - t.get_width()) // 2, y + PANEL_H + 6))

OUT = "docs/store_redesign/hats/partyhat/final_comparison.png"
pygame.image.save(canvas, OUT)
print(f"Saved: {OUT}")
pygame.quit()
