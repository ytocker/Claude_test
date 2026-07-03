"""Final comparison figure: ORIGINAL piñata burro (no tail) + 5 tail designs.

Each column = one variant, Pip mid-flight over a real daytime gameplay scene.
Top row: gameplay panel. Bottom row: hero shot.
Labels: ORIGINAL / DESIGN 1 (TASSEL) / DESIGN 2 (TUFT) /
        DESIGN 3 (RIBBON) / DESIGN 4 (PLUME) / DESIGN 5 (STAR)

Saves: docs/store_redesign/animal/pinata_burro/final_comparison.png
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util
import pygame
pygame.init()

from tools.ninja_render import gameplay_panel, hero_panel


def _load(name):
    path = os.path.join(os.path.dirname(__file__), "pinata_burro_candidates", f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build


SKINS = [
    ("ORIGINAL\n(no tail)",     "skin_pinata_burro"),
    ("DESIGN 1\nTASSEL",        _load("design_1")),
    ("DESIGN 2\nTUFT",          _load("design_2")),
    ("DESIGN 3\nRIBBON",        _load("design_3")),
    ("DESIGN 4\nPLUME",         _load("design_4")),
    ("DESIGN 5\nSTAR ★",        _load("design_5")),
]

# ── layout ─────────────────────────────────────────────────────────────────────
N         = len(SKINS)
COL_W     = 160
PLAY_H    = 240
HERO_H    = 160
LABEL_H   = 48
PAD       = 12
TOTAL_W   = N * COL_W + (N + 1) * PAD
TOTAL_H   = PAD + LABEL_H + PAD + PLAY_H + PAD + HERO_H + PAD

BG        = (18, 16, 28)
LABEL_COL = (240, 235, 255)
STAR_COL  = (255, 220, 60)
LABEL_SZ  = 18

canvas = pygame.Surface((TOTAL_W, TOTAL_H))
canvas.fill(BG)

font    = pygame.font.SysFont("DejaVu Sans", LABEL_SZ, bold=True)
font_sm = pygame.font.SysFont("DejaVu Sans", 14)

for i, (label, source) in enumerate(SKINS):
    x0 = PAD + i * (COL_W + PAD)

    for li, line in enumerate(label.split("\n")):
        col = STAR_COL if "★" in line else LABEL_COL
        surf = font.render(line, True, col)
        canvas.blit(surf, surf.get_rect(centerx=x0 + COL_W // 2,
                                        y=PAD + li * (LABEL_SZ + 2)))

    gp = gameplay_panel(source, COL_W, PLAY_H)
    canvas.blit(gp, (x0, PAD + LABEL_H + PAD))

    hp = hero_panel(source, HERO_H)
    canvas.blit(hp, hp.get_rect(centerx=x0 + COL_W // 2,
                                 y=PAD + LABEL_H + PAD + PLAY_H + PAD))

    if i > 0:
        pygame.draw.line(canvas, (50, 45, 70),
                         (x0 - PAD // 2, PAD),
                         (x0 - PAD // 2, TOTAL_H - PAD), 1)

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "docs", "store_redesign", "animal", "pinata_burro",
                   "final_comparison.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved → {out}")
