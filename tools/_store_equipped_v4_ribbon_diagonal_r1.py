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
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
RAD = sc.m(sc.CARD_RAD)

# Emerald EQUIPPED ramp (shared with the equipped status-chip enamel) so the
# fold reads as the same "you own this" material family, not a foreign badge.
BAND_TOP = (18, 32, 24)
BAND_BOT = (12, 22, 16)
UNDERFOLD = (9, 16, 12)      # reverse side of the sash, in shadow
INNER_EDGE = (6, 12, 9)      # dark contact crease on the inner diagonal
MINT_RIM = (100, 230, 148)   # the lit top-left bevel (equipped-chip mint)
STAR_FILL = (206, 242, 214)  # mint-cream glyph face
STAR_KEY = (10, 22, 14)


def _star(cx, cy, ro, r_in, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(n * 2):
        r = ro if i % 2 == 0 else r_in
        a = rot + math.pi * i / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_ribbon_diagonal(surf):
    """A folded corner SASH across the lower-left apex — a true fold, not a
    label. A 45° emerald band emerges from the rounded corner, drops its darker
    reverse side as a folded flap behind each end, catches a mint bevel on its
    lit outer edge, and carries a single star pip. Clipped to the card body so
    nothing pokes past the round."""
    # Footprint is pushed out to the corner-radius tangents so the band emerges
    # cleanly from the rounded corner instead of the fold being eaten by it; the
    # fold flaps then live on the STRAIGHT edges where they read intact.
    C = (ri, PANEL_H - ri)                    # lower-left apex ≈ (8, 192)
    o1, o2 = sc.m(18), sc.m(39)               # band spans ~40 px along each edge
    L_out = (C[0], C[1] - o1)                 # outer end on left edge
    B_out = (C[0] + o1, C[1])                 # outer end on bottom edge
    L_in = (C[0], C[1] - o2)                  # inner end on left edge
    B_in = (C[0] + o2, C[1])                  # inner end on bottom edge
    face = [L_out, B_out, B_in, L_in]

    layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)

    # 1) under-fold — the sash's darker reverse side folded behind each end. A
    #    right-triangle flap tucks past the inner crease down each edge, so the
    #    band reads as one strip physically folded under at both terminations.
    flap = sc.m(9)
    pygame.draw.polygon(layer, UNDERFOLD,
                        [B_in, (B_in[0] + flap, B_in[1]), (B_in[0], B_in[1] - flap)])
    pygame.draw.polygon(layer, UNDERFOLD,
                        [L_in, (L_in[0], L_in[1] - flap), (L_in[0] + flap, L_in[1])])

    # 2) band face — the emerald ramp swept across the fold's short axis, lit
    #    (18,32,24) on the top-left outer edge → darker (12,22,16) inner.
    band = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    c_out = L_out[0] - L_out[1]               # x-y along the outer diagonal
    c_in = L_in[0] - L_in[1]                  # x-y along the inner diagonal
    for c in range(int(c_out), int(c_in) + 1):
        t = (c - c_out) / max(1, (c_in - c_out))
        col = sc.lerp_color(BAND_TOP, BAND_BOT, t)
        pygame.draw.line(band, col, (0, -c), (PANEL_W, PANEL_W - c), 2)
    qmask = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.polygon(qmask, (255, 255, 255, 255), face)
    band.blit(qmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    layer.blit(band, (0, 0))

    # 3) edges — dark contact crease on the inner diagonal, mint bevel on the
    #    lit outer diagonal (top-left light).
    pygame.draw.line(layer, INNER_EDGE, L_in, B_in, max(1, sc.m(0.9)))
    pygame.draw.line(layer, MINT_RIM, L_out, B_out, max(1, sc.m(1.0)))

    # 4) the pip — one filled star centred on the band face.
    ctr = (sum(p[0] for p in face) / 4, sum(p[1] for p in face) / 4)
    star = _star(ctr[0], ctr[1], sc.m(5.4), sc.m(2.3))
    pygame.draw.polygon(layer, STAR_KEY, _star(ctr[0], ctr[1] + sc.m(0.6),
                                               sc.m(5.8), sc.m(2.5)))
    pygame.draw.polygon(layer, STAR_FILL, star)

    # 5) clip the whole fold to the card body rounded rect.
    clip = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.rect(clip, (255, 255, 255, 255), rect, border_radius=RAD)
    layer.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(layer, (0, 0))


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (regalia frame + check hang-tag, no new indicator)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + ribbon on top)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_ribbon_diagonal(p2)

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
tt = title_f.render("equipped v4 — ribbon-diagonal · round 1 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))
labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY), ("+ RIBBON DIAGONAL", CREAM_LBL)]
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
    "docs", "store_equipped_v4", "ribbon_diagonal", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
