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


def draw_bottom_rail_nameplate(surf):
    """The word EQUIPPED incised straight into the full-width inner cream bead —
    no pill, no chip, no added object. Letters in the same near-black KEY ink as
    the bead's key-line read as shadows stamped down into the gold surface, and a
    single cream copy dropped one pixel below is the incised cut's highlight
    looking up from the groove — so the word reads as physically pressed into the
    rail rather than laid on top of it. Wide tracking lets it span the whole bead."""
    # Inner bead (inset=10) bottom-centre: body.bottom=192, bead bottom ≈ y=182.
    cx, cy = 162, 182
    KEY_INK = (46, 38, 18)
    CREAM = (255, 240, 190)
    f = sc.font(7.5)
    tracking = sc.m(2.0)

    # Cream lower bevel first — the highlight of the incised cut, seen from below.
    sc.plain_text(surf, "EQUIPPED", f, (cx, cy + 1), CREAM,
                  shadow_a=0, tracking=tracking, weight=sc.m(0.6), keyline=None)
    # Key-ink engraved letters on top — the dark groove of the stamp.
    sc.plain_text(surf, "EQUIPPED", f, (cx, cy), KEY_INK,
                  shadow_a=0, tracking=tracking, weight=sc.m(0.6), keyline=None)


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (regalia frame + check hang-tag, no new indicator)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + engraved nameplate on top)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_bottom_rail_nameplate(p2)

# Sanity: report engraved-word span so it stays inside the bead rail (x≈40-284).
_gb = sc._glyph_base("EQUIPPED", sc.font(7.5), sc.m(2.0))
_gw = _gb.get_width()
print("nameplate span x:", 162 - _gw // 2, "→", 162 + _gw // 2, "(width", _gw, ")")

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
tt = title_f.render("equipped v4b — bottom-rail-nameplate · round 1 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))
labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY), ("+ BOTTOM RAIL NAMEPLATE", CREAM_LBL)]
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
    "docs", "store_equipped_v4b", "bottom_rail_nameplate", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
