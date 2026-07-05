"""Final comparison figure for the pilot costume design exploration.

Six columns side by side — the BASE PARROT (plain macaw) plus the five final
designs (design_1 through design_5) — each Pip mid-flight over the same real
gameplay biome scene, with a zoomed hero shot below each gameplay panel.

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python -m tools.render_pilot_compare``.
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

COLUMNS = [
    ("ORIGINAL",  "BASE PARROT",          "skin_base"),
    ("DESIGN 1",  "THE CAPTAIN",          "design_1"),
    ("DESIGN 2",  "ACE",                  "design_2"),
    ("DESIGN 3",  "RED BARON",            "design_3"),
    ("DESIGN 4",  "VIPER",                "design_4"),
    ("DESIGN 5",  "BUSH RUNNER",          "design_5"),
]


def _source(spec):
    if spec == "skin_base":
        return "skin_base"
    mod = importlib.import_module(f"tools.pilot_candidates.{spec}")
    return mod.build


PANEL_W, PANEL_H = 200, 356
HERO_BOX = 200
HERO_GAP = 10
PAD, GUTTER = 22, 14
TITLE_H, CAP_H = 72, 50
n = len(COLUMNS)

sheet_w = PAD * 2 + n * PANEL_W + (n - 1) * GUTTER
sheet_h = TITLE_H + PANEL_H + HERO_GAP + HERO_BOX + CAP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(28, True).render(
    "PILOT COSTUME — BASE PARROT + ALL 5 DESIGNS (in gameplay)",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 20)))

name_font = _font(12, True)
tag_font  = _font(11, True)

for i, (tag, name, spec) in enumerate(COLUMNS):
    src = _source(spec)
    x = PAD + i * (PANEL_W + GUTTER)

    # --- gameplay row ---
    y = TITLE_H
    panel = nr.gameplay_panel(src, PANEL_W, PANEL_H)
    border = (170, 170, 170) if spec == "skin_base" else (*_GOLD_DEEP,)
    pygame.draw.rect(sheet, border,
                     pygame.Rect(x - 2, y - 2, PANEL_W + 4, PANEL_H + 4), width=2)
    sheet.blit(panel, (x, y))

    # --- hero/zoom row ---
    hy = y + PANEL_H + HERO_GAP
    hero = nr.hero_panel(src, HERO_BOX, tilt=0.0)
    pygame.draw.rect(sheet, border,
                     pygame.Rect(x - 2, hy - 2, HERO_BOX + 4, HERO_BOX + 4), width=2)
    sheet.blit(hero, (x, hy))

    # --- captions below hero ---
    cy = hy + HERO_BOX + 6
    tagimg  = tag_font.render(tag,  True, (170, 162, 190))
    nameimg = name_font.render(name, True, _GOLD_PALE)
    sheet.blit(tagimg,  (x + 2, cy))
    sheet.blit(nameimg, (x + 2, cy + 15))

out = os.path.join("docs", "store_redesign", "costume", "pilot",
                   "final_comparison.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
