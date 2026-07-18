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


def draw_gold_pill_equipped(surf):
    """A gold stadium pill clasped over the card's top edge — the inner gold
    bead widened into a clasp, so the equipped badge reads as the frame's own
    material rather than a bolted-on token. Flat dark-key 'EQUIPPED' ink sits
    at its centre; a dark valley keyline rings it so the warm gold detaches
    cleanly from the regalia below."""
    cx, cy = 162, 26
    W, H = 96, 22
    rad = H // 2
    x0, y0 = cx - W // 2, cy - H // 2
    pr = pygame.Rect(x0, y0, W, H)

    # Soft drop shadow so the clasp lifts off the frame it grips.
    sh = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    shr = pygame.Rect(x0, y0 + sc.m(1.5), W, H)
    pygame.draw.rect(sh, (9, 9, 22, 100), shr, border_radius=rad + sc.m(2))
    surf.blit(sh, (0, 0))

    # Gold body — inner-bead ramp widened into the clasp.
    body = sc.vgrad_stops(W, H, rad,
                          [(0.0, (255, 240, 190)), (1.0, (236, 202, 116))],
                          255, gamma=1.04)
    surf.blit(body, pr.topleft)

    # Dark valley keyline — detaches the warm gold from the regalia below.
    pygame.draw.rect(surf, (9, 9, 22), pr, width=max(2, sc.m(1.5)),
                     border_radius=rad)

    # Flat dark-key 'EQUIPPED' stamp, tight tracking so seven letters fit.
    f = sc.font(9)
    sc.plain_text(surf, "EQUIPPED", f, (cx, cy), (46, 38, 18),
                  shadow_a=0, tracking=sc.m(0.5), weight=sc.m(0.8),
                  keyline=None)


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (regalia frame + check hang-tag, no new indicator)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + gold pill on top)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_gold_pill_equipped(p2)

# Compose review sheet
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
GOLD = (236, 202, 116); GREY = (150, 152, 168); CREAM_LBL = (250, 246, 232)
xs = [20, 360, 700]
panel_y = PAD + HDR_H + LBL_H  # 102
sheet_w = xs[-1] + PANEL_W + PAD
strip_w, strip_h = sc.CARD_W * 2, sc.CARD_H * 2
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H
sheet_h = zoom_y + strip_h + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)
title_f = hud_font(22, True)
tt = title_f.render("equipped v4b — gold-pill-equipped · round 1 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))
labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY), ("+ GOLD PILL EQUIPPED", CREAM_LBL)]
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
    "docs", "store_equipped_v4b", "gold_pill_equipped", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
