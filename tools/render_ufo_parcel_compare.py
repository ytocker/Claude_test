"""Final comparison figure: ORIGINAL UFO parcel + 5 redesign candidates.

Each column = one variant. Pip mid-flight in a daytime gameplay scene (top),
hero 4× close-up (middle), 5× carry-zone crop (bottom).
Labels: ORIGINAL / DESIGN 1..5 with short design names.

Saves: docs/store_redesign/parcels/ufo/final_comparison.png
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

from tools.ufo_parcel_candidates._render_shared import (
    gameplay_panel, hero_panel, carry_zoom_panel,
)
from game.parcel_designs.ufo import build as _build_orig


def _load(name):
    path = os.path.join(os.path.dirname(__file__),
                        "ufo_parcel_candidates", f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build


SKINS = [
    ("ORIGINAL",              _build_orig),
    ("DESIGN 1\nROCKET-POP", _load("design_1")),
    ("DESIGN 2\nBUBBLE SCOUT",_load("design_2")),
    ("DESIGN 3\nGOLDEN GLYPH",_load("design_3")),
    ("DESIGN 4\nNEON DINER",  _load("design_4")),
    ("DESIGN 5\nDISCO BALL",  _load("design_5")),
]

# ── layout ──────────────────────────────────────────────────────────────────
N        = len(SKINS)
COL_W    = 180
PLAY_H   = 260
HERO_SZ  = 180
CARRY_SZ = 180          # carry_zoom_panel returns a square (zoom=5 → 180px)
LABEL_H  = 44
PAD      = 12

TOTAL_W  = N * COL_W + (N + 1) * PAD
TOTAL_H  = PAD + LABEL_H + PAD + PLAY_H + PAD + HERO_SZ + PAD + CARRY_SZ + PAD

BG        = (18, 16, 28)
LABEL_COL = (240, 235, 255)
LABEL_SZ  = 16

canvas = pygame.Surface((TOTAL_W, TOTAL_H))
canvas.fill(BG)

font    = pygame.font.SysFont("DejaVu Sans", LABEL_SZ, bold=True)
font_sm = pygame.font.SysFont("DejaVu Sans", 12)

# row y-offsets
y_label = PAD
y_play  = y_label + LABEL_H + PAD
y_hero  = y_play  + PLAY_H  + PAD
y_carry = y_hero  + HERO_SZ + PAD

for i, (label, build_fn) in enumerate(SKINS):
    x0 = PAD + i * (COL_W + PAD)
    cx = x0 + COL_W // 2

    # label
    for li, line in enumerate(label.split("\n")):
        surf = font.render(line, True, LABEL_COL)
        canvas.blit(surf, surf.get_rect(centerx=cx, y=y_label + li * (LABEL_SZ + 2)))

    # gameplay day
    gp = gameplay_panel(build_fn, COL_W, PLAY_H, night=False)
    canvas.blit(gp, (x0, y_play))

    # hero close-up
    hp = hero_panel(build_fn, HERO_SZ)
    canvas.blit(hp, hp.get_rect(centerx=cx, y=y_hero))

    # carry zone 5×
    cz = carry_zoom_panel(build_fn, zoom=5)
    canvas.blit(cz, cz.get_rect(centerx=cx, y=y_carry))

    # column divider
    if i > 0:
        pygame.draw.line(canvas, (50, 45, 70),
                         (x0 - PAD // 2, PAD),
                         (x0 - PAD // 2, TOTAL_H - PAD), 1)

# row labels on left margin
for row_y, row_lbl in [
    (y_play  + PLAY_H  // 2, "GAMEPLAY"),
    (y_hero  + HERO_SZ // 2, "HERO 4×"),
    (y_carry + CARRY_SZ// 2, "CARRY 5×"),
]:
    pass  # labels live inside each panel; no extra margin needed

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "docs", "store_redesign", "parcels", "ufo",
                   "final_comparison.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved → {out}")
