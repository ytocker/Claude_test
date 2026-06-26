"""Assemble the BINKY diaper-redo comparison: the current shipped diaper +
the 5 redo candidates, each shown as a clean hero shot beside an in-gameplay
panel so the natural sit (and the legs poking out below the nappy) is legible.

Exploration deliverable only — loads the scratch candidate builders under
tools/binky_diaper_candidates/ and renders via the shared ninja_render harness.
The "current" cell renders the live skin_binky so the redo is judged against
exactly what ships today. Touches no production art.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib
import pygame
pygame.init()

from tools.ninja_render import gameplay_panel, hero_panel

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(
    HERE, "..", "..", "docs", "store_redesign", "parrot", "baby_parrot",
    "diaper_redo", "final_comparison.png")

NAMES = ["SNUG CLOTH", "PUFFY DISPOSABLE", "PINNED TERRY",
         "SAGGY LOAD", "FOLD-OVER FRONT"]

# (source, label) — current shipped skin first, then the 5 candidate builders.
CELLS = [("skin_binky", "CURRENT (shipped)")]
for n, nm in enumerate(NAMES, start=1):
    build = importlib.import_module(
        f"tools.binky_diaper_candidates.design_{n}").build
    CELLS.append((build, f"{n}. {nm}"))

HERO = 220                  # hero product-shot box
GW, GH = 150, 220           # gameplay panel (portrait)
LABEL_H = 30
PAD = 14
TITLE_H = 50
CELL_W = HERO + GW + PAD
CELL_H = max(HERO, GH) + LABEL_H + PAD
COLS = 2

rows = (len(CELLS) + COLS - 1) // COLS
fig_w = COLS * (CELL_W + PAD) + PAD
fig_h = TITLE_H + rows * CELL_H + PAD

fig = pygame.Surface((fig_w, fig_h))
fig.fill((16, 16, 24))

f_title = pygame.font.SysFont("DejaVuSans", 24, bold=True)
f_name = pygame.font.SysFont("DejaVuSans", 18, bold=True)

fig.blit(f_title.render(
    "BINKY diaper redo — current vs 5 candidates (legs poke out below)",
    True, (245, 245, 250)), (PAD, (TITLE_H - 24) // 2))

for i, (src, label) in enumerate(CELLS):
    r, c = divmod(i, COLS)
    x = PAD + c * (CELL_W + PAD)
    y = TITLE_H + r * CELL_H
    fig.blit(hero_panel(src, HERO), (x, y))
    fig.blit(gameplay_panel(src, GW, GH), (x + HERO + PAD, y))
    fig.blit(f_name.render(label, True, (235, 235, 240)),
             (x + 4, y + max(HERO, GH) + 4))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(fig, os.path.normpath(OUT))
print("wrote", os.path.normpath(OUT), fig.get_size())
