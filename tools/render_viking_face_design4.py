"""Round-1 exploration sheet for the Viking FACE + HELD-AXE redesign, design_4
(JARL). For EACH palette (IRONCLAD then BLOODAXE) the sheet shows three reads:
a hero zoom (judge the detail), an in-gameplay panel (judge it in a real biome
crop), and a 40px NEAREST truth read (judge that the face + held axe survive
the actual on-screen size). Headless capture only; no production art touched.

Run from repo root:
``SDL_VIDEODRIVER=dummy python tools/render_viking_face_design4.py``.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

import tools.ninja_render as nr
from tools.viking_face_candidates import design_4 as D
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP

HERO = 168
GW, GH = 168, 300        # in-gameplay panel
TRUTH = 40               # the real on-screen read
TRUTH_BOX = 130          # framed area the 40px sprite sits centred in
PAD, GUT, LBL = 24, 16, 28
TITLE_H = 60
COL_HDR_H = 22

PANEL_H = max(HERO, GH, TRUTH_BOX)
ROW_W = HERO + GUT + GW + GUT + TRUTH_BOX
ROW_H = PANEL_H + LBL


def _truth_panel(build):
    """The honest 40px read: render the sprite at gameplay size, NEAREST-zoom
    it (no smoothing) so every pixel the player actually sees is shown."""
    frame = build(nr.FRAME_IDX, nr.TILT)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = TRUTH / max(sw, sh)
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    # checker so transparency is obvious
    box = pygame.Surface((TRUTH_BOX, TRUTH_BOX))
    for yy in range(0, TRUTH_BOX, 10):
        for xx in range(0, TRUTH_BOX, 10):
            c = (44, 42, 56) if (xx // 10 + yy // 10) % 2 == 0 else (34, 32, 44)
            box.fill(c, pygame.Rect(xx, yy, 10, 10))
    box.blit(small, small.get_rect(center=(TRUTH_BOX // 2, TRUTH_BOX // 2)))
    zoom = max(1, (TRUTH_BOX) // TRUTH)
    big = pygame.transform.scale(  # NEAREST, integer truth zoom
        small, (small.get_width() * zoom, small.get_height() * zoom))
    out = pygame.Surface((TRUTH_BOX, TRUTH_BOX))
    out.fill((20, 18, 30))
    out.blit(big, big.get_rect(center=(TRUTH_BOX // 2, TRUTH_BOX // 2)))
    pygame.draw.rect(out, _GOLD_DEEP, out.get_rect(), 1)
    return out


ROWS = [
    ("IRONCLAD", D.build_ironclad),
    ("BLOODAXE", D.build_bloodaxe),
]

sheet_w = PAD * 2 + ROW_W
sheet_h = TITLE_H + COL_HDR_H + PAD + len(ROWS) * (ROW_H + GUT)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(26, True).render(
    "VIKING FACE + HELD AXE — design_4 JARL (noble lord)", True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 16)))

hdr = _font(14, True)
hy = TITLE_H
sheet.blit(hdr.render("HERO ZOOM", True, (210, 180, 120)), (PAD, hy))
sheet.blit(hdr.render("IN-GAMEPLAY", True, (210, 180, 120)),
           (PAD + HERO + GUT, hy))
sheet.blit(hdr.render("40px TRUTH (nearest)", True, (210, 180, 120)),
           (PAD + HERO + GUT + GW + GUT, hy))

lbl_font = _font(16, True)

for r, (label, build) in enumerate(ROWS):
    y = TITLE_H + COL_HDR_H + PAD + r * (ROW_H + GUT)
    hero = nr.hero_panel(build, HERO)
    sheet.blit(hero, hero.get_rect(midleft=(PAD, y + PANEL_H // 2)))

    gx = PAD + HERO + GUT
    pygame.draw.rect(sheet, _GOLD_DEEP, pygame.Rect(gx - 1, y - 1, GW + 2, GH + 2), 1)
    sheet.blit(nr.gameplay_panel(build, GW, GH), (gx, y))

    tx = gx + GW + GUT
    truth = _truth_panel(build)
    sheet.blit(truth, truth.get_rect(midleft=(tx, y + PANEL_H // 2)))

    sheet.blit(lbl_font.render(f"design_4 JARL  ·  {label}", True, _GOLD_PALE),
               (PAD + 2, y + PANEL_H + 4))

out = os.path.join("docs", "store_redesign", "costume", "viking", "face",
                   "design_4", "round_1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
