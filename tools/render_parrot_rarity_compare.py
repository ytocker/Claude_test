"""Final comparison figure for the PARROTS rarity-spectrum exploration.

Lays the tab's rarity ladder left→right so the spread reads at a glance: two
existing parrots (a common + the current rare ceiling) for context, then the
five new designs ascending through epic and legendary. Each Pip is rendered
mid-flight over the same real gameplay biome scene, bordered in its rarity
colour (the store's own gem hues), so the user can judge "does spectacle climb
with rarity" in context. Pure capture — the five candidates are scratch
builders under tools/parrot_rarity_candidates/; the two context birds are live
registered sids. No production art or catalog is touched.

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_parrot_rarity_compare.py``.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib
import pygame
pygame.init()

import tools.ninja_render as nr
from game.hud import _font, _GOLD_PALE

# Rarity gem hues, matching the store card tier colours (game/store_cards.py).
RARITY_COL = {
    "common":    (214, 206, 230),
    "rare":      (108, 188, 252),
    "epic":      (194, 122, 248),
    "legendary": (255, 202, 104),
}

# Ladder order: existing context birds first, then the five new designs. Each
# row is (rarity, price-tag, name, source). A source is either a live sid (str)
# or a scratch design module name resolved to its `build` callable.
COLUMNS = [
    ("common",    "EXISTING · 280",  "BLUE MACAW",     "skin_bluegold"),
    ("rare",      "EXISTING · 600",  "LORIKEET",       "skin_lorikeet"),
    ("epic",      "NEW · ~1100",     "STORM MACAW",    "design_1"),
    ("epic",      "NEW · ~1400",     "PRISM LORIKEET", "design_2"),
    ("epic",      "NEW · ~1700",     "MAGMA CONURE",   "design_3"),
    ("legendary", "NEW · ~2800",     "AURORA MACAW",   "design_4"),
    ("legendary", "NEW · ~3500",     "SOLAR QUETZAL",  "design_5"),
]


def _source(spec):
    if spec.startswith("design_"):
        return importlib.import_module(
            f"tools.parrot_rarity_candidates.{spec}").build
    return spec


PANEL_W, PANEL_H = 210, 460
PAD, GUTTER = 26, 16
TITLE_H, CAP_H = 80, 60
n = len(COLUMNS)

sheet_w = PAD * 2 + n * PANEL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + PANEL_H + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(30, True).render(
    "PARROTS — COMPLETING THE RARITY SPECTRUM  ·  existing (common→rare) + 5 new epic/legendary",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 22)))

name_font = _font(16, True)
tier_font = _font(13, True)
tag_font = _font(12, False)

for i, (rar, tag, name, spec) in enumerate(COLUMNS):
    x = PAD + i * (PANEL_W + GUTTER)
    y = TITLE_H
    col = RARITY_COL[rar]
    panel = nr.gameplay_panel(_source(spec), PANEL_W, PANEL_H)
    # New designs get a thicker rarity border; context birds a thin one.
    w = 3 if spec.startswith("design_") else 2
    pygame.draw.rect(sheet, col, pygame.Rect(x - w, y - w, PANEL_W + 2 * w, PANEL_H + 2 * w), width=w)
    sheet.blit(panel, (x, y))
    cy = y + PANEL_H + 9
    sheet.blit(tier_font.render(rar.upper(), True, col), (x + 2, cy))
    sheet.blit(name_font.render(name, True, _GOLD_PALE), (x + 2, cy + 17))
    sheet.blit(tag_font.render(tag, True, (170, 162, 190)), (x + 2, cy + 36))

out = os.path.join("docs", "store_redesign", "parrot", "final_comparison.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
