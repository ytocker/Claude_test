"""Pilot costume — Design 1: THE CAPTAIN (golden-age airline commander).

Scratch exploration builder, NOT registered in store_skins.BUILDERS.

R5: the body oval IS the jacket via _build_parrot_with_palette navy recolor.
Natural red head, blue wings, yellow beak remain. Overlays (collar, cap,
shades, stripes) are placed on the actual body ellipse surface.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import pygame
from game.store_skins import _make_skin, _poly, HX, HY, CROWN_Y
from game.dollar_parrot_ghost import _build_parrot_with_palette, _pal

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
    lens_frame=(200,165,50),
    lens_body=(30,25,20),
    lens_tint=None,
    lens_glint=(255,255,255),
    beak_main=(255,185,0),
    beak_dark=(200,130,0),
    beak_gloss=(255,215,100),
    foot=(200,130,0),
)

def _cap_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _P_CAP, draw_lenses=False)

_CAP_NAVY=(27,42,74); _CAP_RIM=(42,59,95); _BRIM=(11,15,28)
_GOLD=(245,197,66);   _GOLD_H=(255,232,150)
_SHIRT=(244,241,234); _SHIRT2=(220,217,210); _TIE=(14,21,61)
_AV_LENS=(30,25,20);  _AV_FRAME=(180,150,40); _AV_BRDG=(200,165,50)
_AV_GLINT=(255,255,255)

def _paint_captain(surf, wing_angle_deg):
    # Body ellipse composite: centre (32,52), rx=19, ry=14.
    # y_top(x)=52-14*sqrt(1-((x-32)/19)**2)
    # x=37->y39, x=42->y41, x=45->y43. No overlay floats above body surface.
    # Head ellipse centre (47,41), rx=12, ry=11 -- overlays stay clear.

    # Anatomy-correct collar: two small fabric tabs at the body-head junction,
    # placed at the actual ellipse top curve (y>=39 at these x values).
    _poly(surf, _SHIRT,  [(37,42),(42,39),(45,41),(44,46),(38,46)])
    _poly(surf, _SHIRT2, [(34,43),(39,41),(42,43),(40,47),(35,47)])
    pygame.draw.line(surf, _TIE, (41,40),(41,45), 1)

    # 3 fat gold sleeve stripes on lower wing/cuff, animated with flap.
    dy = int(round(wing_angle_deg * 0.10))
    bx = 15
    pygame.draw.rect(surf, _CAP_NAVY, (bx-1, 43+dy, 11, 10))
    for sy in (44, 47, 50):
        pygame.draw.rect(surf, _GOLD, (bx, sy+dy, 9, 2))

    # Aviator shades on the scarlet face.
    near=[(HX-7,HY),(HX-5,HY-3),(HX-1,HY-3),(HX+1,HY-1),(HX-1,HY+2),(HX-4,HY+2)]
    far =[(HX+2,HY-1),(HX+4,HY-3),(HX+7,HY-3),(HX+8,HY-1),(HX+7,HY+1),(HX+4,HY+1)]
    _poly(surf, _AV_LENS, near); _poly(surf, _AV_LENS, far)
    pygame.draw.polygon(surf, _AV_FRAME, near, 1)
    pygame.draw.polygon(surf, _AV_FRAME, far,  1)
    pygame.draw.line(surf, _AV_BRDG, (HX+1,HY-2),(HX+2,HY-2), 1)
    pygame.draw.circle(surf, _AV_GLINT, (HX-2,HY-2), 1)

    # Peaked officer's cap -- flat top breaks the round head silhouette.
    _poly(surf, _CAP_NAVY, [(38,32),(38,24),(40,22),(56,22),(58,24),(58,32)])
    _poly(surf, _BRIM,     [(37,32),(59,33),(59,35),(37,34)])
    pygame.draw.rect(surf, _GOLD, (44,29,5,2))
    pygame.draw.line(surf, _GOLD_H, (44,29),(48,29), 1)
    pygame.draw.line(surf, _CAP_RIM, (40,22),(56,22), 1)
    pygame.draw.line(surf, _CAP_RIM, (38,24),(38,31), 1)

build = _make_skin(_paint_captain, base_fn=_cap_base)
