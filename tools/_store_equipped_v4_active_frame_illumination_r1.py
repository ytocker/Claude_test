#!/usr/bin/env python3
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()
SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS  # 324×200
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2*ri, PANEL_H - 2*ri)

# Warm gold-cream aura hue — the same GOLD_PALE the frame keyline already uses,
# so the bloom reads as the frame's OWN light spilling inward, not a new colour.
GLOW_COL = (255, 236, 184)
PIP_COL = (80, 220, 130)
PIP_SPEC = (200, 255, 224)


def draw_active_frame_illumination(surf):
    rad = sc.m(sc.CARD_RAD)
    # 1) Soft warm bloom bleeding INWARD from the inner keyline. A stack of
    # rounded-rect strokes stepping in from the frame's inner edge, alpha fading
    # toward the card centre, so the border reads "lit from within" without
    # touching the locked double-bead gold itself. Blitted as one aura surface so
    # the overlapping strokes composite to a smooth gradient, not banded rings.
    aura = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    steps = sc.m(11)
    start_inset = sc.m(13)          # the frame's inner keyline (bead inset=13)
    for i in range(steps):
        inset = start_inset + i
        a = int(46 * (1 - i / steps) ** 1.5)
        if a <= 0:
            continue
        r = rect.inflate(-2 * inset, -2 * inset)
        pygame.draw.rect(aura, (*GLOW_COL, a), r,
                         width=max(1, sc.m(1.2)),
                         border_radius=max(1, rad - inset))
    surf.blit(aura, (0, 0))

    # 2) The lone emerald gem-pip pressed into the top gold bead at dead centre.
    # A dark seat ring first so it reads SUNK into the metal, then the filled
    # emerald, a shaded lower-right for roundness, and a single hot mint specular.
    cx, cy, r = 162, 18, sc.m(4)
    pygame.draw.circle(surf, (10, 26, 14, 210), (cx, cy + 1), r + sc.m(1))
    pygame.draw.circle(surf, PIP_COL, (cx, cy), r)
    pygame.draw.circle(surf, (44, 150, 88), (cx + 1, cy + 1), r,
                       max(1, sc.m(0.8)))
    pr = max(1, int(r * 0.34))
    spec = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(spec, (*PIP_SPEC, 255), (pr + 1, pr + 1), pr)
    surf.blit(spec, (cx - int(r * 0.32) - pr, cy - int(r * 0.32) - pr),
              special_flags=pygame.BLEND_ADD)


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + frame illumination on top)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_active_frame_illumination(p2)

# Compose review sheet
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
GOLD = (236, 202, 116); GREY = (150, 152, 168); CREAM_LBL = (250, 246, 232)
xs = [20, 360, 700]
panel_y = PAD + HDR_H + LBL_H
sheet_w = xs[-1] + PANEL_W + PAD
strip_w, strip_h = sc.CARD_W * 2, sc.CARD_H * 2
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H
sheet_h = zoom_y + strip_h + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)
title_f = hud_font(22, True)
tt = title_f.render("equipped v4 — active-frame-illumination · round 1 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))
labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY), ("+ FRAME ILLUMINATION", CREAM_LBL)]
panels = [p0, p1, p2]
lbl_f = hud_font(15, True); zlbl_f = hud_font(13, True)
for x, panel, (label, col) in zip(xs, panels, labels):
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(x + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (x, panel_y))
card1x = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
strip = pygame.transform.scale2x(card1x)
zx = xs[-1] + (PANEL_W - strip_w) // 2
zt = zlbl_f.render("@1x (162x100 tile, 2x nearest)", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(xs[-1] + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
sheet.blit(strip, (zx, zoom_y))
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
    "docs", "store_equipped_v4", "active_frame_illumination", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
