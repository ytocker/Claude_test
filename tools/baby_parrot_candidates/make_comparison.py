"""Assemble the baby-parrot comparison figure: original Pip + the 5 baby
finals, each mid-flight in the same real gameplay scene, side by side.

Exploration deliverable only — loads the scratch builders under
tools/baby_parrot_candidates/ and renders via the shared ninja_render harness
so the figure matches every in-loop preview. Touches no production art.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib
import pygame
pygame.init()

from tools.ninja_render import gameplay_panel

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(
    HERE, "..", "..", "docs", "store_redesign", "parrot", "baby_parrot",
    "final_comparison.png")


def _builder(n):
    return importlib.import_module(
        f"tools.baby_parrot_candidates.design_{n}").build


# (source, name, tier) — original Pip is the base fallback (sid None); the five
# baby finals are each candidate module's `build` callable.
PANELS = [
    (None, "ORIGINAL PIP", "base"),
    (_builder(1), "HATCHLING", "RARE"),
    (_builder(2), "DOWNBALL", "COMMON"),
    (_builder(3), "BIG-EYES", "RARE"),
    (_builder(4), "NEST-BABY", "RARE"),
    (_builder(5), "BINKY", "COMMON"),
]

PW, PH = 210, 300          # gameplay panel size (portrait — matches canvas crop)
LABEL_H = 46               # label strip under each panel
COLS = 3
PAD = 14
TITLE_H = 64

TIER_COLOR = {
    "base": (150, 150, 160), "COMMON": (170, 180, 190),
    "RARE": (90, 200, 255),
}

rows = (len(PANELS) + COLS - 1) // COLS
cell_w = PW + PAD
cell_h = PH + LABEL_H + PAD
fig_w = COLS * cell_w + PAD
fig_h = TITLE_H + rows * cell_h + PAD

fig = pygame.Surface((fig_w, fig_h))
fig.fill((18, 18, 26))

f_title = pygame.font.SysFont("DejaVuSans", 28, bold=True)
f_name = pygame.font.SysFont("DejaVuSans", 20, bold=True)
f_tier = pygame.font.SysFont("DejaVuSans", 15, bold=True)

title = f_title.render(
    "Pip — BABY PARROT concepts (same sprite size, 5 looks)",
    True, (240, 240, 245))
fig.blit(title, (PAD + 4, (TITLE_H - title.get_height()) // 2))

for i, (source, name, tier) in enumerate(PANELS):
    r, c = divmod(i, COLS)
    x = PAD + c * cell_w
    y = TITLE_H + r * cell_h
    panel = gameplay_panel(source, PW, PH)
    fig.blit(panel, (x, y))
    strip = pygame.Rect(x, y + PH, PW, LABEL_H)
    pygame.draw.rect(fig, (30, 30, 42), strip)
    nm = f_name.render(name, True, (235, 235, 240))
    fig.blit(nm, (x + 10, y + PH + 5))
    tcol = TIER_COLOR.get(tier, (200, 200, 200))
    tr = f_tier.render(tier, True, tcol)
    fig.blit(tr, (x + 10, y + PH + 26))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(fig, os.path.normpath(OUT))
print("wrote", os.path.normpath(OUT), fig.get_size())
