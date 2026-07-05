import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()

import tools.ninja_render as nr
from game.store_skins import _make_skin, _poly
from game.dollar_parrot_ghost import _build_parrot_with_palette, _pal

_P_CAP = _pal(
    tail=[(200,30,40),(240,95,40),(255,160,55),(255,220,80)],
    tail_line=(170,25,25),
    body_shadow=(14,21,55), body_main=(20,33,74),
    body_chest=(27,42,90), body_belly=(18,28,68),
    sheen=None,
    wing_main=(40,100,255), wing_dark=(20,55,180),
    wing_tip=(50,220,100), wing_secondary=None, wing_highlight=(80,160,255),
    head_shadow=(150,15,20), head_main=(240,55,55),
    head_cheek=(255,130,130), head_crown=(255,170,170),
    lens_frame=(180,150,40), lens_body=(30,25,20),
    lens_tint=None, lens_glint=(255,255,255),
    beak_main=(255,185,0), beak_dark=(200,130,0),
    beak_gloss=(255,215,100), foot=(200,130,0),
)
_CAP_NAVY=(27,42,74); _CAP_RIM=(42,59,95); _BRIM=(11,15,28)
_GOLD=(245,197,66); _GOLD_H=(255,232,150)

def _cap_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _P_CAP, draw_lenses=True)

def _cap_fn(draw_epaulette, draw_stripes):
    def _paint(surf, wing_angle_deg):
        # Peaked cap
        _poly(surf, _CAP_NAVY, [(38,32),(38,24),(40,22),(56,22),(58,24),(58,32)])
        _poly(surf, _BRIM,     [(37,32),(59,33),(59,35),(37,34)])
        pygame.draw.rect(surf, _GOLD, (44,29,5,2))
        pygame.draw.line(surf, _GOLD_H, (44,29),(48,29), 1)
        pygame.draw.line(surf, _CAP_RIM, (40,22),(56,22), 1)
        pygame.draw.line(surf, _CAP_RIM, (38,24),(38,31), 1)
        if draw_epaulette:
            sx, sy = 21, 39; sw, sh = 13, 7
            pygame.draw.rect(surf, _CAP_NAVY, (sx, sy, sw, sh))
            for ey in (40, 42, 44):
                pygame.draw.line(surf, _GOLD, (sx+1, ey), (sx+sw-2, ey), 1)
            pygame.draw.rect(surf, _GOLD, (sx, sy, sw, sh), 1)
        if draw_stripes:
            dy = int(round(wing_angle_deg * 0.10))
            bx = 15
            pygame.draw.rect(surf, _CAP_NAVY, (bx-1, 43+dy, 11, 10))
            for ry in (44, 47, 50):
                pygame.draw.rect(surf, _GOLD, (bx, ry+dy, 9, 2))
    return _paint

build_epaulette = _make_skin(_cap_fn(True, False),  base_fn=_cap_base)
build_stripes   = _make_skin(_cap_fn(False, True),  base_fn=_cap_base)

from game.hud import _font, _GOLD_PALE, _GOLD_DEEP

PANEL_W, PANEL_H = 220, 340
HERO_SZ = 240
GAP = 20
PAD = 24
TITLE_H = 44

W = PAD*2 + 2*(PANEL_W + HERO_SZ + GAP) + GAP
H = TITLE_H + PANEL_H + 16 + HERO_SZ + 36 + PAD

sheet = pygame.Surface((W, H))
sheet.fill((18, 16, 28))

title = _font(18, True).render("D1 CAPTAIN — rank options (pick one)", True, _GOLD_PALE)
sheet.blit(title, (PAD, 10))

OPTIONS = [
    (build_epaulette, "A — SHOULDER EPAULETTE",  "3 gold stripes on a navy board at the shoulder"),
    (build_stripes,   "B — SLEEVE STRIPES",       "3 fat gold stripes on the wing cuff (animates with flap)"),
]

name_f = _font(14, True)
sub_f  = _font(11, False)

for i, (src, label, sub) in enumerate(OPTIONS):
    col_x = PAD + i * (PANEL_W + HERO_SZ + GAP + GAP)

    gp = nr.gameplay_panel(src, PANEL_W, PANEL_H)
    pygame.draw.rect(sheet, _GOLD_DEEP, pygame.Rect(col_x-2, TITLE_H-2, PANEL_W+4, PANEL_H+4), width=2)
    sheet.blit(gp, (col_x, TITLE_H))

    hx = col_x + PANEL_W + GAP
    hp = nr.hero_panel(src, HERO_SZ)
    pygame.draw.rect(sheet, _GOLD_DEEP, pygame.Rect(hx-2, TITLE_H-2, HERO_SZ+4, HERO_SZ+4), width=2)
    sheet.blit(hp, (hx, TITLE_H))

    cy = TITLE_H + max(PANEL_H, HERO_SZ) + 8
    sheet.blit(name_f.render(label, True, _GOLD_PALE), (col_x, cy))
    sheet.blit(sub_f.render(sub,   True, (170,162,190)), (col_x, cy+18))

os.makedirs("docs/store_redesign/costume/pilot/design_1", exist_ok=True)
pygame.image.save(sheet, "docs/store_redesign/costume/pilot/design_1/rank_options.png")
print("SAVED")
