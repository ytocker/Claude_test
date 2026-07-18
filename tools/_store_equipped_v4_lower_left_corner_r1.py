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
from game.draw import lerp_color

sd.load()
SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS  # 324×200
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2*ri, PANEL_H - 2*ri)


def draw_lower_left_corner(surf):
    """Struck emerald coin-boss badge inset into the free lower-left corner: a
    circular medallion that reads as a physically pressed mark of the equipped
    state — categorically a COIN, not a ribbon. Emerald-mint so it stays legible
    against the cream/ink upper-left ✓ hang-tag at the opposite corner."""
    cx, cy = 34, 168
    R = sc.m(12)

    # equipped-green enamel ramp — the same DNA as the EQUIPPED status chip so the
    # badge belongs to the same active-state family.
    C_HI = (18, 32, 24)
    C_LO = (12, 22, 16)
    MINT = (100, 230, 148)

    pad = sc.m(4)
    D = R * 2 + pad * 2
    disc = pygame.Surface((D, D), pygame.SRCALPHA)
    c = R + pad

    # bottom-right contact shadow anchoring the coin into the card body.
    for k in range(sc.m(3), 0, -1):
        a = int(70 * (k / sc.m(3)))
        pygame.draw.circle(disc, (0, 0, 0, a),
                           (c + sc.m(1.5), c + sc.m(2)), R + k)

    # radial dome — lit centre deepening to the rim gives the pressed-metal read
    # even though the light cue is carried by the rim glint + contact shadow.
    for i in range(R, 0, -1):
        t = (i / R) ** 1.25
        col = lerp_color(C_HI, C_LO, t)
        pygame.draw.circle(disc, (*col, 255), (c, c), i)

    # dark contact keyline seating the coin (drawn just inside so the rim glint
    # can sit one step brighter on top of it).
    pygame.draw.circle(disc, (5, 12, 8, 235), (c, c), R, max(1, sc.m(1.4)))

    # mint rim glint on the upper-left arc only — the single struck highlight.
    glint = pygame.Surface((D, D), pygame.SRCALPHA)
    pygame.draw.arc(glint, (*MINT, 230),
                    (c - R + sc.m(1), c - R + sc.m(1), R * 2 - sc.m(2), R * 2 - sc.m(2)),
                    math.radians(108), math.radians(205), max(1, sc.m(1)))
    disc.blit(glint, (0, 0), special_flags=pygame.BLEND_ADD)

    # embossed mint 5-point star at the centre: a dark drop first, then the mint
    # face one step up-left so the pip reads as pressed proud of the dome.
    def star_pts(scx, scy, ro, ri_):
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            rr = ro if k % 2 == 0 else ri_
            pts.append((scx + rr * math.cos(ang), scy + rr * math.sin(ang)))
        return pts

    ro, rin = R * 0.60, R * 0.26
    pygame.draw.polygon(disc, (4, 12, 8, 200),
                        star_pts(c + sc.m(0.6), c + sc.m(0.8), ro, rin))
    pygame.draw.polygon(disc, MINT,
                        star_pts(c - sc.m(0.4), c - sc.m(0.4), ro, rin))
    # tiny hot core glint on the star for the struck-metal kiss.
    pygame.draw.polygon(disc, (200, 255, 220),
                        star_pts(c - sc.m(0.4), c - sc.m(0.4), ro * 0.5, rin * 0.5))

    surf.blit(disc, (cx - c, cy - c))


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + medallion on top)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_lower_left_corner(p2)

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
tt = title_f.render("equipped v4 — lower-left-corner · round 1 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))
labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY), ("+ LOWER-LEFT CORNER", CREAM_LBL)]
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
    "docs", "store_equipped_v4", "lower_left_corner", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
