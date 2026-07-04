"""Pilot costume — Design 1: THE CAPTAIN (golden-age airline commander).

Scratch builder, NOT registered in store_skins.BUILDERS.

R7: single rank item — shoulder epaulette only (sleeve stripes removed).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import pygame
from game.store_skins import _make_skin, _poly, HX, HY, CROWN_Y
from game.dollar_parrot_ghost import _build_parrot_with_palette, _pal

# Navy body palette — head/wing/beak stay natural.
# draw_lenses=True: the built-in round aviator shades are drawn in sprite-space
# at the correct eye position, with the gold-frame/dark-lens palette below.
_P_CAP = _pal(
    tail=[(200,30,40),(240,95,40),(255,160,55),(255,220,80)],
    tail_line=(170,25,25),
    body_shadow=(14,21,55),
    body_main=(20,33,74),
    body_chest=(27,42,90),
    body_belly=(18,28,68),
    sheen=None,
    wing_main=(40,100,255),
    wing_dark=(20,55,180),
    wing_tip=(50,220,100),
    wing_secondary=None,
    wing_highlight=(80,160,255),
    head_shadow=(150,15,20),
    head_main=(240,55,55),
    head_cheek=(255,130,130),
    head_crown=(255,170,170),
    # Round aviator shades drawn by _draw_lenses — gold frame, dark lens
    lens_frame=(180,150,40),
    lens_body=(30,25,20),
    lens_tint=None,
    lens_glint=(255,255,255),
    beak_main=(255,185,0),
    beak_dark=(200,130,0),
    beak_gloss=(255,215,100),
    foot=(200,130,0),
)

def _cap_base(angle_deg):
    # draw_lenses=True: big round aviators drawn in sprite-space on the red face
    return _build_parrot_with_palette(angle_deg, _P_CAP, draw_lenses=True)

_CAP_NAVY=(27,42,74); _CAP_RIM=(42,59,95); _BRIM=(11,15,28)
_GOLD=(245,197,66);   _GOLD_H=(255,232,150)

def _paint_captain(surf, wing_angle_deg):
    # ── Gold captain epaulette on the shoulder (not the face) ─────────────────
    # Shoulder is the upper-left body area where the wing meets the body.
    # In composite space this sits at x≈20-32, y≈38-46.
    # A small navy shoulder-board + 3 gold rank stripes = "captain".
    sx, sy = 21, 39          # epaulette top-left
    sw, sh = 13, 7           # epaulette width × height
    pygame.draw.rect(surf, _CAP_NAVY, (sx, sy, sw, sh))
    # 3 gold rank stripes across the epaulette
    for i, ey in enumerate((40, 42, 44)):
        pygame.draw.line(surf, _GOLD, (sx+1, ey), (sx+sw-2, ey), 1)
    # Thin gold border
    pygame.draw.rect(surf, _GOLD, (sx, sy, sw, sh), 1)

    # ── Peaked officer's cap ───────────────────────────────────────────────────
    _poly(surf, _CAP_NAVY, [(38,32),(38,24),(40,22),(56,22),(58,24),(58,32)])
    _poly(surf, _BRIM,     [(37,32),(59,33),(59,35),(37,34)])
    pygame.draw.rect(surf, _GOLD, (44,29,5,2))
    pygame.draw.line(surf, _GOLD_H, (44,29),(48,29), 1)
    pygame.draw.line(surf, _CAP_RIM, (40,22),(56,22), 1)
    pygame.draw.line(surf, _CAP_RIM, (38,24),(38,31), 1)

build = _make_skin(_paint_captain, base_fn=_cap_base)
