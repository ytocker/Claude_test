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


def draw_floating_gold_lozenge(surf):
    """A glyph-only heraldic diamond lozenge floated in the card's lower body —
    a pointed rhombus standing on point, certifying 'equipped' without a word.
    Authored at SS=2 pixel coords. A masked vertical gold gradient (clipped to
    the rhombus via a white polygon under BLEND_RGBA_MIN) gives the ONE gold a
    clean pointed silhouette without a bounding rectangle; a dark keyline seats
    it, cream bevels catch the top-left light, and a debossed 4-point star reads
    as the seal's device."""
    # Rhombus standing on point, centred at (162,173): hw=22, hh=18.
    poly = [(162, 155), (184, 173), (162, 191), (140, 173)]

    # Seat shadow — the diamond floats a touch above the body it sits on.
    dy = sc.m(2)
    sh = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), [(x, y + dy) for x, y in poly])
    surf.blit(sh, (0, 0))

    # Gold body — a vertical Ramp gradient on the 44×36 bounding box, then clip
    # to the rhombus with a white polygon under BLEND_RGBA_MIN so only the
    # pointed silhouette survives (no masking rectangle). Bright cream top ->
    # warm gold foot = a top-left-lit polished metal read, palette-pure.
    ox, oy = 140, 155
    bw, bh = 44, 36
    local = [(x - ox, y - oy) for x, y in poly]
    body = sc.vgrad_stops(bw, bh, 0,
                          [(0.0, (255, 240, 190)), (1.0, (236, 202, 116))], 255,
                          gamma=1.06)
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), local)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (ox, oy))

    # Dark keyline seats the jewel against the dark card body.
    pygame.draw.polygon(surf, (86, 50, 8), poly, width=max(2, sc.m(1.4)))

    # Cream bevel on the two top (light-facing) edges only — the lit facets.
    top, right, bot, left = poly
    bw2 = max(1, sc.m(1))
    pygame.draw.line(surf, (255, 240, 190), top, left, bw2)
    pygame.draw.line(surf, (255, 240, 190), top, right, bw2)

    # Debossed 4-point star (✦) as the device: 8-vertex polygon in dark-key,
    # ~60% of the lozenge half-extents, points meeting up/down/left/right.
    cx, cy = 162, 173
    ox_r, oy_r = 13, 11      # outer reach (x,y) — 60% of hw=22 / hh=18
    ix, iy = 5, 4            # inner (concave) notch
    star = [
        (cx, cy - oy_r),           # up point
        (cx + ix, cy - iy),
        (cx + ox_r, cy),           # right point
        (cx + ix, cy + iy),
        (cx, cy + oy_r),           # down point
        (cx - ix, cy + iy),
        (cx - ox_r, cy),           # left point
        (cx - ix, cy - iy),
    ]
    pygame.draw.polygon(surf, (46, 38, 18), star)
    # Single cream catch-light along the star's upper-left facet.
    pygame.draw.line(surf, (255, 240, 190),
                     (cx, cy - oy_r), (cx - ix, cy - iy), 1)


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (regalia frame + check hang-tag, no new indicator)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT: the equipped card with the floated gold lozenge stamped
# into the lower body over the finished art.
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_floating_gold_lozenge(p2)

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
tt = title_f.render("equipped v4c — floating-gold-lozenge · round 1 · skin_mummy",
                    True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))
labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY),
          ("+ FLOATING GOLD LOZENGE", CREAM_LBL)]
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
    "docs", "store_equipped_v4c", "floating_gold_lozenge", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
