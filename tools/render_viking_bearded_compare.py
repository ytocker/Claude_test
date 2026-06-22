"""Before/after comparison for the refined Viking 'BEARDED' design.

Two rows — BEFORE (the rejected design_2 BERSERKER) and AFTER (the refined
bearded design: regular macaw face + beaded mustache + beard + back-carried
axe) — each in IRONCLAD and BLOODAXE (hero zoom + in-gameplay). Pure capture;
no production art touched.

Run headless from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_viking_bearded_compare.py``.
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


def _builds(modname):
    m = importlib.import_module(modname)
    return m.build_ironclad, m.build_bloodaxe


ROWS = [
    ("BEFORE  (old Berserker)", "tools.viking_face_candidates.design_2"),
    ("AFTER  (bearded)", "tools.viking_face_candidates.bearded"),
]

HERO, GW, GH = 168, 152, 270
PAD, GUT, LBL = 24, 16, 28
ROW_H = max(HERO, GH) + LBL
TITLE_H = 60
HALF_W = HERO + GUT + GW
ROW_W = HALF_W + 44 + HALF_W

sheet_w = PAD * 2 + ROW_W
sheet_h = TITLE_H + PAD + len(ROWS) * (ROW_H + GUT)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(26, True).render(
    "VIKING — refined BEARDED design (regular face + beaded 'stache/beard + back-carried axe)",
    True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 16)))
hdr = _font(15, True)
sheet.blit(hdr.render("IRONCLAD", True, (210, 180, 120)), (PAD + 4, TITLE_H - 4))
sheet.blit(hdr.render("BLOODAXE", True, (210, 130, 110)), (PAD + HALF_W + 44 + 4, TITLE_H - 4))

lbl_font = _font(15, True)


def _cell(build, x, y):
    hero = nr.hero_panel(build, HERO)
    sheet.blit(hero, hero.get_rect(midleft=(x, y + GH // 2)))
    gx = x + HERO + GUT
    pygame.draw.rect(sheet, (*_GOLD_DEEP,), pygame.Rect(gx - 1, y - 1, GW + 2, GH + 2), width=1)
    sheet.blit(nr.gameplay_panel(build, GW, GH), (gx, y))


for r, (label, modname) in enumerate(ROWS):
    y = TITLE_H + PAD + r * (ROW_H + GUT)
    iron, blood = _builds(modname)
    _cell(iron, PAD, y)
    _cell(blood, PAD + HALF_W + 44, y)
    sheet.blit(lbl_font.render(label, True, _GOLD_PALE), (PAD + 2, y + GH + 5))

out = os.path.join("docs", "store_redesign", "costume", "viking", "bearded", "final_comparison.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
