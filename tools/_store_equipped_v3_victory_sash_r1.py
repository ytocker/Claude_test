#!/usr/bin/env python3
"""
equipped-card v3 — victory-sash concept, round 1.

Instead of the green EQUIPPED chip, a folded gold award sash corners the card's
top-right: a diagonal ribbon crossing from the top edge to the right edge, its
gold pushed BRIGHTER than the card's bevel rim so it reads as a lit metal band
rather than another frame lane. A darker folded underside tucks under the lower
end for 3D, a cream checkmark rides the band angle ("claimed"), and the tier gem
is re-used as a rivet pinning the sash near its upper-left head.

The whole sash is authored on a panel overlay and clipped to the card body's
rounded silhouette, so the band follows the corner radius instead of a hard
bite. Top-right is the layout-safe quadrant (dome centred, ribbon/name/chip in
the lower half), so the sash never collides with live card content.
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
rad = sc.m(sc.CARD_RAD)                                   # body corner radius


# ── Panel 0 — UNEQUIPPED (price tag visible) ─────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)


# ── Panel 1 — STOCK EQUIPPED (green chip, reference) ─────────────────────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False)


# ── Panel 2 — CONCEPT EQUIPPED (chip suppressed, victory sash) ───────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None          # suppress the green EQUIPPED chip
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()

pal = sc.RARITY[sc._rarity(SID)]


def lerp(a, b, t):
    return sc.lerp_color(a, b, max(0.0, min(1.0, t)))


def grad3(t):
    """Bright lit-gold ramp across the band width — MUST out-brightness the
    card's (236,202,116) bevel so the sash reads as a separate lit metal."""
    if t < 0.5:
        return lerp((255, 236, 170), (246, 200, 102), t / 0.5)
    return lerp((246, 200, 102), (210, 152, 54), (t - 0.5) / 0.5)


def L(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


# Two parallel diagonals define the strip: OUTER hypotenuse A→B (the lit
# upper-left edge) and INNER hypotenuse C→D (toward the corner). Both clipped
# to the card interior; the rounded-rect mask trims the ends to the radius.
A = (230.0, 8.0)      # outer edge, meets top
B = (316.0, 127.0)    # outer edge, meets right
C = (262.0, 8.0)      # inner edge, meets top
D = (316.0, 83.0)     # inner edge, meets right

ov = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)

# (1) Soft drop shadow — the band silhouette offset down-right so the sash lifts
#     off the card face (top-left light => shadow falls to lower-right).
for off, a in ((2, 60), (3, 110)):
    sh = [(x + off, y + off) for x, y in (A, C, D, B)]
    pygame.draw.polygon(ov, (0, 0, 0, a), sh)

# (2) Band fill — parallel strips outer->inner, brightest at the outer (lit)
#     edge so the ribbon carries a top-left-lit sheen across its width.
STEPS = 48
for i in range(STEPS):
    k0, k1 = i / STEPS, (i + 1) / STEPS
    quad = [L(A, C, k0), L(B, D, k0), L(B, D, k1), L(A, C, k1)]
    pygame.draw.polygon(ov, grad3(k0), quad)

# (3) Folded underside — a darker gold flap tucking under the lower-right end so
#     the ribbon reads as a real fold, not a painted stripe (~60% brightness).
fold = [(316.0, 118.0), (316.0, 152.0), (283.0, 132.0)]
pygame.draw.polygon(ov, (150, 96, 30), fold)
fold_lo = [(316.0, 135.0), (316.0, 152.0), (292.0, 138.0)]
pygame.draw.polygon(ov, (120, 72, 18), fold_lo)
pygame.draw.line(ov, (96, 56, 12), (316.0, 118.0), (283.0, 132.0), max(1, sc.m(0.8)))

# (4) Keylines — dark defining edge on BOTH long edges, so the band sits in a
#     crisp contour against both the dark body and the corner beyond it.
kd = max(1, sc.m(1))
pygame.draw.line(ov, (96, 56, 12), A, B, kd)              # outer long edge
pygame.draw.line(ov, (96, 56, 12), C, D, kd)              # inner long edge

# (5) Hot rim — a fine specular line just inside the lit outer edge.
hr0, hr1 = L(A, C, 0.07), L(B, D, 0.07)
pygame.draw.line(ov, (255, 246, 214), hr0, hr1, max(1, sc.m(0.7)))

# (6) Cream checkmark — rides the band angle so it reads as stamped INTO the
#     ribbon rather than floating on top; a dark keyline seats it.
theta = math.atan2(B[1] - A[1], B[0] - A[0])   # band length direction (~54°)
ct, st = math.cos(theta), math.sin(theta)
cxk, cyk = 270.0, 60.0
local = [(-9.0, -1.0), (-2.0, 7.0), (12.0, -10.0)]
chk = [(cxk + px * ct - py * st, cyk + px * st + py * ct) for px, py in local]
chk_sh = [(x + 1.4, y + 1.4) for x, y in chk]
pygame.draw.lines(ov, (96, 56, 12), False, chk_sh, max(2, sc.m(1.7)))
pygame.draw.lines(ov, (248, 238, 210), False, chk, max(2, sc.m(1.6)))

# Clip the whole sash to the card body's rounded silhouette.
mask = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.rect(mask, (255, 255, 255, 255), rect, border_radius=rad)
ov.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
p2.blit(ov, (0, 0))

# (7) Tier gem as a RIVET pinning the sash head — the same faceted tier cut the
#     card already uses, re-purposed as hardware sitting ON the band.
sc.facet_gem(p2, 247, 37, 14, pal["gem"], pal["deep"])


# ── Compose the review sheet ─────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
ONE_W, ONE_H = sc.CARD_W, sc.CARD_H          # 162×100 — true 1× card size
ZOOM_W, ZOOM_H = ONE_W * 2, ONE_H * 2        # nearest-neighbour blow-up of 1×

N = 3
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + SGAP + SLBL_H + ZOOM_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

GOLD = (236, 202, 116)
title_f = hud_font(22, True)
tt = title_f.render("equipped v3 — victory-sash · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

GREY = (150, 152, 168)
CREAM_LBL = (250, 246, 232)
labels = [("UNEQUIPPED", GREY), ("STOCK EQUIPPED", GREY),
          ("VICTORY SASH", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)
panel_y = PAD + HDR_H + LBL_H            # 102 — concept panel lands at x=700
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

    # 1× read: downscale the panel to true card size, then blow it back up
    # nearest-neighbour so the sheet shows how the sash resolves at 1×.
    card1x = pygame.transform.smoothscale(panel, (ONE_W, ONE_H))
    zoom = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
    zt = zlbl_f.render("@1× (rendered then 2× nearest)", True, GREY)
    sheet.blit(zt, zt.get_rect(midbottom=(px + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
    sheet.blit(zoom, (px + (PANEL_W - ZOOM_W) // 2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3", "victory_sash", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
