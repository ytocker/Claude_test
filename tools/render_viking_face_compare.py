"""Comparison figure for the Viking FACE + HELD-AXE redesign.

Rows: a REFERENCE row (the current v1/v2 face+axe) then the 5 new designs.
Columns per row: IRONCLAD (hero zoom + in-gameplay) and BLOODAXE (hero zoom +
in-gameplay), so the user can judge each design's face+axe in both palettes and
pick a design + colour. Pure capture; no production art touched.

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_viking_face_compare.py``.
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

# (label, ironclad_build, bloodaxe_build) — resolved lazily so a half-built
# design doesn't break the whole figure.
def _design(n):
    m = importlib.import_module(f"tools.viking_face_candidates.design_{n}")
    return m.build_ironclad, m.build_bloodaxe


def _ref():
    v1 = importlib.import_module("tools.viking_palette_candidates.v1").build
    v2 = importlib.import_module("tools.viking_palette_candidates.v2").build
    return v1, v2


ROWS = [
    ("CURRENT (v1/v2)", _ref),
    ("1 · WARCHIEF", lambda: _design(1)),
    ("2 · BERSERKER", lambda: _design(2)),
    ("3 · RAIDER", lambda: _design(3)),
    ("4 · JARL", lambda: _design(4)),
    ("5 · SKIRMISHER", lambda: _design(5)),
]

HERO, GW, GH = 150, 150, 267
PAD, GUT, LBL = 22, 16, 26
ROW_H = max(HERO, GH) + LBL
TITLE_H = 64
# row layout: [IRON hero][IRON game]  gap  [BLOOD hero][BLOOD game]
HALF_W = HERO + GUT + GW
ROW_W = HALF_W + 40 + HALF_W

sheet_w = PAD * 2 + ROW_W
sheet_h = TITLE_H + PAD + len(ROWS) * (ROW_H + GUT)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(28, True).render(
    "VIKING FACE + HELD AXE — 5 designs in IRONCLAD & BLOODAXE", True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 18)))
hdr = _font(15, True)
sheet.blit(hdr.render("IRONCLAD", True, (210, 180, 120)), (PAD + 4, TITLE_H - 6))
sheet.blit(hdr.render("BLOODAXE", True, (210, 130, 110)), (PAD + HALF_W + 40 + 4, TITLE_H - 6))

lbl_font = _font(15, True)


def _cell(build, x, y):
    hero = nr.hero_panel(build, HERO)
    sheet.blit(hero, hero.get_rect(midleft=(x, y + GH // 2)))
    gx = x + HERO + GUT
    pygame.draw.rect(sheet, (*_GOLD_DEEP,), pygame.Rect(gx - 1, y - 1, GW + 2, GH + 2), width=1)
    sheet.blit(nr.gameplay_panel(build, GW, GH), (gx, y))


for r, (label, getter) in enumerate(ROWS):
    y = TITLE_H + PAD + r * (ROW_H + GUT)
    iron, blood = getter()
    _cell(iron, PAD, y)
    _cell(blood, PAD + HALF_W + 40, y)
    sheet.blit(lbl_font.render(label, True, _GOLD_PALE), (PAD + 2, y + GH + 4))

out = os.path.join("docs", "store_redesign", "costume", "viking", "face", "final_comparison.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
