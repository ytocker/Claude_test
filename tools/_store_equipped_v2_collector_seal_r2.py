#!/usr/bin/env python3
"""
equipped-card v2 — collector-seal concept, round 2.

A RAISED gold-wax medallion planted in the upper-left quadrant: a proud,
dimensional badge with a coarse scalloped rim and a struck 5-point star center
— "authenticated / certified — this item is mine". It is the RAISED counterpart
to emboss-brand (raised vs pressed): the disc catches an upper-left key so rim
and star sit PROUD of the card body.

Drawn LAST over an equipped card whose green EQUIPPED chip is suppressed.
"""
import os
import sys
import math

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
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324×200
ri = sc.m(sc._INSET)                                      # 8
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)


# ── Panel 0 — UNEQUIPPED (price tag visible) ─────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)

# ── Panel 1 — STOCK EQUIPPED (green chip, reference) ─────────────────────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False)

# ── Panel 2 — CONCEPT EQUIPPED (chip suppressed, collector seal) ─────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None          # suppress the green EQUIPPED chip
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()


# ── Collector seal — a RAISED gold-wax medallion planted upper-left ──────────
# Well inside the card body Rect(8,8,308,184): center (54,58), R=32 leaves the
# disc envelope x=22-86, y=26-90 clear of the corner-clipped zones. Smaller than
# a coin so it reads as an authenticating badge, not currency.
SX, SY = 54, 58          # SS=2 coords — upper-left quadrant, inside body margin
R = 32                   # outer radius (SS=2 => 16px at 1×)


def _star_pts(cx, cy, r_out, r_in, n=5, rot=-math.pi / 2):
    """5-point star polygon: alternating outer/inner radii, first point up."""
    pts = []
    for i in range(n * 2):
        rr = r_out if i % 2 == 0 else r_in
        a = rot + i * math.pi / n
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


# 1) Drop shadow on its own SRCALPHA layer so the soft dark ground beneath the
#    disc sells the lift without darkening the whole card.
shadow = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.circle(shadow, (4, 4, 16, 140), (SX + 3, SY + 3), R + 2)
p2.blit(shadow, (0, 0))

# 2) Base amber disc
pygame.draw.circle(p2, (208, 164, 92), (SX, SY), R)

# 3) Scalloped rim — 10 CHUNKY teeth. High-frequency scallops smooth into a
#    plain circle at gameplay scale; fewer, deeper teeth survive the downscale
#    and keep the wax-seal silhouette. Fill full, then re-fill one notch in so
#    the teeth read as OUTWARD bumps.
N_TEETH = 10
NOTCH = 4
for i in range(N_TEETH):
    ang = i * 2 * math.pi / N_TEETH
    ox = SX + R * math.cos(ang)
    oy = SY + R * math.sin(ang)
    pygame.draw.circle(p2, (180, 138, 70), (int(round(ox)), int(round(oy))), NOTCH)
pygame.draw.circle(p2, (208, 164, 92), (SX, SY), R - NOTCH)

# 4) Bevel lighting (key from upper-left) — a lit arc up-left, a shadowed arc
#    down-right, and a hot specular catch make the disc dome toward the viewer.
bevel = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
lit_rect = pygame.Rect(SX - (R - NOTCH), SY - (R - NOTCH),
                       (R - NOTCH) * 2, (R - NOTCH) * 2)
pygame.draw.arc(bevel, (236, 202, 116, 230), lit_rect,
                math.radians(135), math.radians(315), 3)
pygame.draw.arc(bevel, (58, 48, 22, 200), lit_rect,
                math.radians(315), math.radians(360 + 135), 3)
p2.blit(bevel, (0, 0))
spec = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.circle(spec, (250, 245, 220, 200),
                   (SX - int(R * 0.6), SY - int(R * 0.6)), 4)
p2.blit(spec, (0, 0))

# 5) Inner disc face — a hair darker than the rim so the raised rim casts an
#    inward step and the center reads flat enough to hold the struck glyph.
pygame.draw.circle(p2, (188, 146, 78), (SX, SY), R - 6)

# 6) Struck center star — impressed into the wax, sold by a strong micro-bevel:
#    a dark down-right ghost + a bright up-left ghost with a wide brightness
#    delta so the star reads genuinely pressed (not a flat painted stamp).
star_out, star_in = 13, 6
pygame.draw.polygon(p2, (80, 58, 24), _star_pts(SX + 2, SY + 2, star_out, star_in))
pygame.draw.polygon(p2, (220, 190, 120), _star_pts(SX - 2, SY - 2, star_out, star_in))
pygame.draw.polygon(p2, (108, 80, 38), _star_pts(SX, SY, star_out, star_in))


# ── Compose the review sheet ─────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
ONE_W, ONE_H = sc.CARD_W, sc.CARD_H          # 162×100 — true 1× card size
ZOOM_W, ZOOM_H = ONE_W * 2, ONE_H * 2        # 2× blow-up of the true 1× inset

N = 3
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + SGAP + SLBL_H + ZOOM_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

GOLD = (236, 202, 116)
title_f = hud_font(22, True)
tt = title_f.render("equipped v2 — collector-seal · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

GREY = (150, 152, 168)
AMBER_LBL = (222, 178, 96)
labels = [("UNEQUIPPED", GREY), ("STOCK EQUIPPED", GREY),
          ("COLLECTOR SEAL", AMBER_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)
# Standard layout (matches emboss_brand): PAD + header + label lane so the panel
# sits at y=102, keeping the seal well inside the rounded card body.
panel_y = PAD + HDR_H + LBL_H              # 102
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

    # True 1× inset: smoothscale the panel to actual 162×100 card size, then 2×
    # up so the reviewer can judge whether the scallop rim + struck star survive
    # at live game resolution without aliasing hiding the read.
    card1x = pygame.transform.smoothscale(panel, (ONE_W, ONE_H))
    zoom = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
    zt = zlbl_f.render("@1× (smoothscaled to 162×100, shown 2×)", True, GREY)
    sheet.blit(zt, zt.get_rect(midbottom=(px + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
    sheet.blit(zoom, (px + (PANEL_W - ZOOM_W) // 2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v2", "collector_seal", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
