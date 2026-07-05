"""Capture the live store across EVERY category (all tabs, all pages) and
stitch them into one figure, grouped by category with a header per tab.

Renders the real StoreScene to the game canvas so the figure reflects the
shipped catalog exactly — rarity ribbons, tier gems, prices, secret ??? masks.
One row per category; that category's pages sit side by side, scaled down.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))            # StoreScene thumbnails need a display

from game.config import W, H
from game.store import StoreScene, _TABS

OUT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "docs", "store_redesign", "store_all_categories.png"))

SCALE = 0.52                               # page downscale (360x640 -> 187x333)
PW, PH = int(W * SCALE), int(H * SCALE)
PAD = 12
HEADER_H = 30
TITLE_H = 46

scene = StoreScene()
scene.view = "category"

# Capture every page of every tab, grouped by tab.
groups = []                                # [(label, [page_surface, ...]), ...]
max_cols = 1
for i, (label, _g) in enumerate(_TABS):
    scene.tab = i
    pages = []
    for p in range(scene.n_pages):
        scene.page = p
        full = pygame.Surface((W, H))
        scene.render(full)
        pages.append(pygame.transform.smoothscale(full, (PW, PH)))
    groups.append((label, pages))
    max_cols = max(max_cols, len(pages))

row_h = HEADER_H + PH + PAD
fig_w = PAD + max_cols * (PW + PAD)
fig_h = TITLE_H + len(groups) * row_h + PAD

fig = pygame.Surface((fig_w, fig_h))
fig.fill((14, 14, 22))

f_title = pygame.font.SysFont("DejaVuSans", 26, bold=True)
f_head = pygame.font.SysFont("DejaVuSans", 19, bold=True)

fig.blit(f_title.render("Skybit STORE — every category (live capture)",
                        True, (245, 245, 250)), (PAD, (TITLE_H - 26) // 2))

for r, (label, pages) in enumerate(groups):
    y = TITLE_H + r * row_h
    fig.blit(f_head.render(f"{label}  ({len(pages)} page{'s' if len(pages) > 1 else ''})",
                           True, (255, 210, 120)), (PAD, y + 4))
    for c, page in enumerate(pages):
        fig.blit(page, (PAD + c * (PW + PAD), y + HEADER_H))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(fig, OUT)
print("wrote", OUT, fig.get_size())
