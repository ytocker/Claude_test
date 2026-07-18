#!/usr/bin/env python3
import os, sys, math
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


def draw_gold_stud_seal(surf):
    """A larger notarial gold medallion riveted at the card's lower-RIGHT, half
    biting the inner frame bead so it reads as a wax seal struck into the regalia
    — 'officially equipped'. A bold checkmark is DEBOSSED into the recessed
    indigo well so the disc carries meaning instead of reading as a stray coin.
    All geometry authored at SS=2 pixel coords: a wide key-dark torus seat around
    the whole disc, a warm gold seat ring, a recessed indigo well stamped with a
    key-dark ✓ (lit cream on its top-left edge, as if struck), and a rivet stud."""
    cx, cy = 284, 172

    # Drop shadow lifts the disc off the frame it bites into.
    sh = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, 100), (cx + 2, cy + 2), 22)
    surf.blit(sh, (0, 0))

    # Wide key-dark torus seat wraps the whole disc, then a warm gold fill —
    # a 3px dark ring gives gold-on-gold contrast against the frame beads.
    pygame.draw.circle(surf, (46, 38, 18), (cx, cy), 20)
    pygame.draw.circle(surf, (236, 202, 116), (cx, cy), 17)

    # Top-left-lit rim — a tamed additive cream lobe simulates the source
    # without clipping the gold to pure white.
    lit = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.circle(lit, (255, 240, 190, 110), (cx - 6, cy - 6), 7)
    surf.blit(lit, (0, 0), special_flags=pygame.BLEND_ADD)

    # Recessed inner well — dark indigo with a thin key ring lip. The 3px gold
    # band between well (r14) and dark ring (r17) is the seat the ✓ sits in.
    pygame.draw.circle(surf, (28, 24, 42), (cx, cy), 14)
    pygame.draw.circle(surf, (46, 38, 18), (cx, cy), 14, width=1)

    # Lit arc across the seat top-left quadrant — the embossed highlight.
    tor = pygame.Rect(cx - 17, cy - 17, 34, 34)
    pygame.draw.arc(surf, (255, 240, 190), tor, math.pi * 0.5, math.pi, 2)

    # Central rivet stud with a single hot specular pixel.
    pygame.draw.circle(surf, (248, 238, 210), (cx, cy), 4)
    pygame.draw.circle(surf, (255, 255, 250), (cx - 1, cy - 1), 1)

    # Debossed ✓ struck into the well: angular-drop like the hang-tag. Cream
    # lit edge peeks below (offset up-left, drawn first) then key-dark ink over
    # it, so the mark reads as recessed and struck rather than printed.
    pts = [(cx - 8, cy + 4), (cx - 2, cy + 10), (cx + 10, cy - 6)]
    lit_pts = [(x - 1, y - 1) for (x, y) in pts]
    pygame.draw.lines(surf, (255, 240, 190), False, lit_pts, 1)
    pygame.draw.lines(surf, (46, 38, 18), False, pts, max(4, sc.m(2.0)))


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (regalia frame + check hang-tag, no new indicator)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT: the seal IS the equipped signal, so suppress the ✓ hang-tag
# here (stacking both markers double-signals). Monkey-patch the chip to a no-op
# for this render only, then stamp the seal over the finished card body.
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
sc.state_chip = orig_chip
draw_gold_stud_seal(p2)

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
tt = title_f.render("equipped v4b — gold-stud-seal · round 2 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))
labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY), ("+ GOLD STUD SEAL", CREAM_LBL)]
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
    "docs", "store_equipped_v4b", "gold_stud_seal", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
