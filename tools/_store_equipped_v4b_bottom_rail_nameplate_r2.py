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

# Palette (regalia bead DNA) — no green.
CREAM_FACE = (255, 240, 190)   # inner-bead cream gold plaque field
CREAM_LIT  = (255, 248, 224)   # incised highlight welling up from the cut
KEY_INK    = (46, 38, 18)      # engraved dark key
DARK_VALLEY = (9, 9, 22)       # bottom shadow / top valley bead
BEAD_EDGE  = (46, 38, 18)      # top dark separation line
OUTER_GOLD = (236, 202, 116)   # outer gold frame bead


def _fit_font(plaque_w):
    """The plaque is a fixed architectural band, so the engraving must be sized
    to live inside it rather than the reverse — step the face down until the
    tracked word clears the inner margins, keeping the frame proportions stable."""
    for size in (8.5, 8.0, 7.5):
        f = sc.font(size)
        w = sc._glyph_base("EQUIPPED", f, sc.m(2.0)).get_width()
        if w <= plaque_w - sc.m(8):
            return size, f, w
    return 7.5, sc.font(7.5), sc._glyph_base("EQUIPPED", sc.font(7.5), sc.m(2.0)).get_width()


def draw_bottom_rail_nameplate(surf, rect):
    """A dedicated cream-gold plaque band widened out of the frame's bottom bead
    into an engraved nameplate — the equipped state reads as regalia, not a
    sticker. Flat and architectural: the word EQUIPPED is incised (a cream
    highlight welling from below, key-ink groove on top) so it sits pressed into
    the metal, framed by a dark valley line above and an outer gold bead below."""
    plaque_x = rect.left + sc.m(11)
    plaque_y = rect.bottom - sc.m(11)
    plaque_h = sc.m(11)
    plaque_w = rect.right - sc.m(11) - plaque_x
    band = pygame.Rect(plaque_x, plaque_y, plaque_w, plaque_h)

    # Flat cream field — no radius so it reads as milled metal, not a pill.
    surf.fill(CREAM_FACE, band)
    # 1px top dark separation + 1px bottom shadow lift the plaque off the body
    # above and off the frame border below without adding volume.
    pygame.draw.line(surf, BEAD_EDGE, (band.left, band.top),
                     (band.right - 1, band.top), sc.m(0.5))
    pygame.draw.line(surf, DARK_VALLEY, (band.left, band.bottom - 1),
                     (band.right - 1, band.bottom - 1), sc.m(0.5))

    # Top valley bead — dark hairline just above the plaque separating it from
    # the card body, so the plaque sits BETWEEN two thin frame lines.
    pygame.draw.line(surf, DARK_VALLEY, (band.left, band.top - 1),
                     (band.right - 1, band.top - 1), sc.m(0.5))
    # Bottom outer gold bead — the frame's lit edge under the plaque.
    pygame.draw.line(surf, OUTER_GOLD, (band.left, band.bottom),
                     (band.right - 1, band.bottom), sc.m(0.5))

    # Engraving — sized to the band, centred at the plaque's mid-height so the
    # cut sits square in the field.
    size, f, gw = _fit_font(plaque_w)
    cx = band.centerx
    cy = band.centery
    tracking = sc.m(2.0)
    # Incised cut: cream highlight welling from one pixel below FIRST …
    sc.plain_text(surf, "EQUIPPED", f, (cx, cy + sc.m(0.5)), CREAM_LIT,
                  shadow_a=0, tracking=tracking, weight=sc.m(0.7), keyline=None)
    # … then the dark key-ink groove stamped on top.
    sc.plain_text(surf, "EQUIPPED", f, (cx, cy), KEY_INK,
                  shadow_a=0, tracking=tracking, weight=sc.m(0.7), keyline=None)
    return band, size, gw


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (regalia frame + check hang-tag, no new indicator)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + dedicated plaque band)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
_band, _size, _gw = draw_bottom_rail_nameplate(p2, rect)
print("plaque band:", _band, "font", _size, "glyph_w", _gw,
      "margin", _band.width - _gw)

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
tt = title_f.render("equipped v4b — bottom-rail-nameplate · round 2 · skin_mummy", True, GOLD)
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
    "docs", "store_equipped_v4b", "bottom_rail_nameplate", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
