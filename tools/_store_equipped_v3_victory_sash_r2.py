#!/usr/bin/env python3
"""
equipped-card v3 — victory-sash concept, round 2 (final).

A folded gold award ribbon caps the card's top-right as a TRUE corner
triangle: the band runs at 45deg with BOTH ends anchored — one on the top
edge, one on the right edge — so the silhouette stays stable when the 162x100
card shrinks to a thumbnail. A bold cream checkmark is stamped centred on the
band (the read that converts "ribbon" -> "equipped"); its stroke is heavy
enough to survive the 1x downscale. The sash core is pushed to white-gold so
it out-brightens the card's bevel rim instead of fusing gold-on-gold, and a
dark-indigo drop-shadow along the band's lower-left edge lifts it off the
frame. A darker folded underside tucks under the right-edge terminus for 3D,
and the tier gem is re-used as a rivet pinning the sash head.
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
    """White-gold band ramp across the strip width. The core is pushed toward
    (255,245,220) so its luminance clears the card's (222,190,108) bevel rim by
    ~20% — the sash reads as a separately lit metal band, not another gold lane
    fused into the frame."""
    if t < 0.55:
        return lerp((255, 249, 230), (255, 240, 198), t / 0.55)
    return lerp((255, 240, 198), (226, 182, 112), (t - 0.55) / 0.45)


def L(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


# True 45deg corner triangle: both long edges run at slope +1, each ending on
# the top edge AND the right edge. OUTER edge A→B hugs the corner (the lit
# face); INNER edge C→D seats into the card. The band is the strip between them.
A = (250.0, 8.0)      # outer edge, meets top
B = (316.0, 74.0)     # outer edge, meets right
C = (210.0, 8.0)      # inner edge, meets top
D = (316.0, 114.0)    # inner edge, meets right

ov = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)

# (1) Dark-indigo drop-shadow along the band's lower-left (inner) edge, offset
#     down-left, so the ribbon casts onto the card face and lifts off the frame
#     rather than fusing with it. Indigo (near the 8,8,20 sheet ground) keeps it
#     from reading as more brown gold.
for off, a in ((3, 150), (5, 90)):
    sh = [(C[0] - off, C[1] + off), (D[0] - off, D[1] + off),
          (D[0], D[1]), (C[0], C[1])]
    pygame.draw.polygon(ov, (8, 8, 20, a), sh)

# (2) Band fill — parallel strips outer→inner, brightest white-gold at the lit
#     outer (corner-facing) edge, cooling to mid gold at the inner edge.
STEPS = 48
for i in range(STEPS):
    k0, k1 = i / STEPS, (i + 1) / STEPS
    quad = [L(A, C, k0), L(B, D, k0), L(B, D, k1), L(A, C, k1)]
    pygame.draw.polygon(ov, grad3(k0), quad)

# (3) Folded underside — a darker gold flap tucking beneath the right-edge
#     terminus so the ribbon reads as a real fold, not a painted stripe.
fold = [(316.0, 110.0), (316.0, 148.0), (284.0, 128.0)]
pygame.draw.polygon(ov, (150, 96, 30), fold)
fold_lo = [(316.0, 130.0), (316.0, 148.0), (293.0, 133.0)]
pygame.draw.polygon(ov, (120, 72, 18), fold_lo)
pygame.draw.line(ov, (96, 56, 12), (316.0, 110.0), (284.0, 128.0), max(1, sc.m(0.8)))

# (4) Keylines — dark defining edge on BOTH long edges so the band sits in a
#     crisp contour against the dark body and the corner beyond it.
kd = max(1, sc.m(1))
pygame.draw.line(ov, (96, 56, 12), A, B, kd)              # outer long edge
pygame.draw.line(ov, (110, 66, 16), C, D, kd)             # inner long edge

# (5) Hot rim — a fine specular line just inside the lit outer edge; restrained
#     so the band's brightness comes from its body, not a glare stripe.
hr0, hr1 = L(A, C, 0.08), L(B, D, 0.08)
pygame.draw.line(ov, (255, 250, 232), hr0, hr1, max(1, sc.m(0.7)))

# (6) Cream checkmark — the equipped read. Stamped centred on the band, riding
#     its 45deg angle, with a heavy stroke (>=6px at SS=2) so the tick still
#     resolves after the 1x downscale. A dark keyline seats it into the ribbon.
theta = math.atan2(B[1] - A[1], B[0] - A[0])   # band length direction (~45°)
ct, st = math.cos(theta), math.sin(theta)
cxk, cyk = 273.0, 51.0                          # band centroid
local = [(-11.0, -1.0), (-2.5, 8.0), (14.0, -12.0)]
chk = [(cxk + px * ct - py * st, cyk + px * st + py * ct) for px, py in local]
chk_sh = [(x + 1.6, y + 1.6) for x, y in chk]
pygame.draw.lines(ov, (96, 56, 12), False, chk_sh, max(2, sc.m(3.6)))
pygame.draw.lines(ov, (248, 238, 210), False, chk, max(2, sc.m(3.2)))

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
tt = title_f.render("equipped v3 — victory-sash · skin_mummy · round 2", True, GOLD)
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
    "docs", "store_equipped_v3", "victory_sash", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
