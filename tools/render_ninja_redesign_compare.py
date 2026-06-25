"""Final comparison figure for the ninja redesign exploration.

Six columns side by side — the ORIGINAL live ninja plus the five explored
designs — each Pip mid-flight over the same real gameplay biome scene, so the
user can judge the redesign in context. Pure capture; touches no production
art (the five candidates are scratch builders under tools/ninja_candidates/,
the original is the live registered ``skin_ninja``).

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_ninja_redesign_compare.py``.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib
import pygame
pygame.init()

import tools.ninja_render as nr
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP

# Column order: original first, then the five designs in concept priority.
COLUMNS = [
    ("ORIGINAL", "CURRENT NINJA", "skin_ninja"),
    ("DESIGN 1", "SHADOWSTRIKE", "design_1"),
    ("DESIGN 2", "CRIMSON FANG", "design_2"),
    ("DESIGN 3", "IRON RONIN", "design_3"),
    ("DESIGN 4", "SMOKE PHANTOM", "design_4"),
    ("DESIGN 5", "NEON SEVER", "design_5"),
]


def _source(spec):
    """A registered sid (str) stays a str; a design module name resolves to its
    `build` callable."""
    if spec == "skin_ninja":
        return "skin_ninja"
    mod = importlib.import_module(f"tools.ninja_candidates.{spec}")
    return mod.build


# Layout: a horizontal strip of 6 gameplay panels with a two-line caption each.
PANEL_W, PANEL_H = 220, 392
PAD, GUTTER = 26, 18
TITLE_H, CAP_H = 76, 56
n = len(COLUMNS)

sheet_w = PAD * 2 + n * PANEL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + PANEL_H + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(32, True).render(
    "NINJA REDESIGN — ORIGINAL vs. 5 EXPLORED DESIGNS (in gameplay)",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 22)))

name_font = _font(17, True)
tag_font = _font(13, True)

for i, (tag, name, spec) in enumerate(COLUMNS):
    x = PAD + i * (PANEL_W + GUTTER)
    y = TITLE_H
    panel = nr.gameplay_panel(_source(spec), PANEL_W, PANEL_H)
    border = (210, 80, 80) if spec == "skin_ninja" else (*_GOLD_DEEP,)
    pygame.draw.rect(sheet, border, pygame.Rect(x - 2, y - 2, PANEL_W + 4, PANEL_H + 4), width=2)
    sheet.blit(panel, (x, y))
    cy = y + PANEL_H + 8
    tagimg = tag_font.render(tag, True, (170, 162, 190))
    sheet.blit(tagimg, (x + 2, cy))
    nameimg = name_font.render(name, True, _GOLD_PALE)
    sheet.blit(nameimg, (x + 2, cy + 18))

out = os.path.join("docs", "store_redesign", "costume", "ninja", "final_comparison.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
