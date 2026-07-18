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


def draw_top_center_banner(surf):
    """Emerald 'clasp' pill pinned to the card's top edge: a short enamel pill
    whose lower third bites over the inner gold bead so it reads as a physical
    fastener gripping the frame. Glyph-led — a bright power-pip + max-bold 'ON'
    token — and coloured by the equipped-green ramp so it never reads as the
    near-black ✓ ink on the cream hang-tag."""
    cx, cy = 162, 26
    W, H = 86, 22
    rad = H // 2
    x0, y0 = cx - W // 2, cy - H // 2
    pr = pygame.Rect(x0, y0, W, H)

    # Enamel body — equipped-green ramp, single smooth gradient.
    body = sc.vgrad_stops(W, H, rad, [(0.0, (18, 32, 24)), (1.0, (12, 22, 16))],
                          255, gamma=1.04)
    # Soft seat shadow so the pill lifts off the frame it clasps.
    sh = pygame.Surface((W + sc.m(6), H + sc.m(6)), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 150), sh.get_rect(), border_radius=rad + sc.m(3))
    surf.blit(sh, (x0 - sc.m(3), y0 - sc.m(2) + sc.m(3)))
    surf.blit(body, pr.topleft)

    # Dark contact keyline UNDER a bright mint bevel — the defined emerald edge.
    pygame.draw.rect(surf, (6, 20, 12), pr, width=max(1, sc.m(1.4)), border_radius=rad)
    sc.bevel_rim(surf, pr, rad, (20, 88, 44, 235), (100, 230, 148, 220),
                 w=max(1, sc.m(1.4)))

    # Power-pip — a bold vertical lozenge, bright enamel, at the pill's left.
    pw, ph = sc.m(5), sc.m(9)
    prad = pw // 2
    pip_cx = x0 + sc.m(15)
    pipimg = sc.vgrad_stops(pw, ph, prad,
                            [(0.0, (170, 252, 196)), (1.0, (64, 200, 118))],
                            255, gamma=1.02)
    pip_r = pipimg.get_rect(center=(pip_cx, cy))
    # dark seat ring so the pip pops off the dark enamel
    seat = pygame.Rect(pip_r.x - sc.m(1), pip_r.y - sc.m(1),
                       pw + sc.m(2), ph + sc.m(2))
    pygame.draw.rect(surf, (8, 24, 14), seat, border_radius=prad + sc.m(1))
    surf.blit(pipimg, pip_r.topleft)
    # single hot glint top-left of the pip
    gl = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.circle(gl, (240, 255, 246, 200), (prad, prad), max(1, sc.m(1)))
    surf.blit(gl, pip_r.topleft, special_flags=pygame.BLEND_ADD)

    # 'ON' token — max-bold cream-mint, to the right of the pip.
    f = sc.font(11)
    tok_cx = pip_cx + sc.m(9) + (pr.right - sc.m(6) - (pip_cx + sc.m(9))) // 2
    sc.plain_text(surf, "ON", f, (tok_cx, cy), (214, 248, 224),
                  shadow_a=140, tracking=sc.m(1.0), weight=sc.m(1.0),
                  keyline=(6, 22, 12), kw=max(1, sc.m(0.9)))

    # Two micro cream rivets at the pill ends — reads as a fastened clasp.
    for rx in (x0 + sc.m(4), pr.right - sc.m(4)):
        pygame.draw.circle(surf, (10, 26, 16), (rx, cy), max(1, sc.m(1.6)))
        pygame.draw.circle(surf, (238, 248, 232), (rx, cy), max(1, sc.m(1.2)))
        pygame.draw.circle(surf, (255, 255, 250, 220), (rx - 1, cy - 1),
                           max(1, sc.m(0.5)))


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (regalia frame + check hang-tag, no new indicator)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + banner on top)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_top_center_banner(p2)

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
tt = title_f.render("equipped v4 — top-center-banner · round 1 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))
labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY), ("+ TOP-CENTER BANNER", CREAM_LBL)]
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
    "docs", "store_equipped_v4", "top_center_banner", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
