#!/usr/bin/env python3
"""
equipped-card v2 — corner-dogear concept, round 2.

Instead of the green EQUIPPED chip, the card's upper-left corner peels back like
a turned page: a warm-cream fold triangle sits in the empty quadrant the price
tag left behind. A gold checkmark seated in the fold's visual centre says
"claimed/owned", not merely "bookmarked". Top-left is the one layout-safe
quadrant (dome centred, gem top-right, ribbon/name/chip in the lower half), so
the fold never collides with live card content.

Round-2 physics rework over r1: a real cast shadow fans down-and-right onto the
body past the crease (so the flap reads *lifted*, not printed); the fold face
carries a paper-curl gradient — warm/bright at the crease, dimmer toward the
outer tip; the crease seam is lifted off pure black to an even (22,23,42); and
the checkmark is doubled in size and centred in the meaty middle of the fold,
ringed by clean cream so it survives a 1× read. All clipped to the card body's
rounded silhouette so the flap follows the corner radius.
"""
import os
import sys

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


# ── Panel 2 — CONCEPT EQUIPPED (chip suppressed, corner dog-ear) ─────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None          # suppress the green EQUIPPED chip
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()

FOLD = 46          # triangle leg at SS=2 — big enough to read a folded page at 1×
# The hypotenuse (the crease) is the line x+y = 2*ri+FOLD = 62 on the panel.
HYP_A = (ri + FOLD, ri)          # (54, 8)
HYP_B = (ri, ri + FOLD)          # (8, 54)

# Paper-curl ramp: warm+bright where the sheet lifts at the crease, dimmer and
# cooler as it curls back toward the outer tip — reads as a real page turn.
CURL_CREASE = (252, 245, 222)    # near crease: warm, faint gold cast → "owned"
CURL_TIP = (235, 229, 210)       # near outer corner: dimmer paper
HILITE = (255, 253, 244)         # hot pixel riding the fold edge
CREASE = (22, 23, 42)            # even, lifted seam (never crushed to black)
GOLD = (236, 202, 116)
GOLD_DK = (150, 105, 45)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# Everything lands on a panel-sized overlay so a single rounded-body mask clips
# the fold to the corner radius (a real peel follows the card silhouette).
dog = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)

# (1) Cast shadow — the flap floats above the body, so it throws a soft shadow
# down-and-right onto the card past the crease. Adjacent non-overlapping strips
# parallel to the crease keep the fade clean; darkest (≈body pulled toward
# (15,16,40)) right at the crease, gone within ~5px.
SH = (13, 14, 34)
SH_BASE, SH_SPAN, SH_STRIPS = 1.5, 5.0, 10
for k in range(SH_STRIPS):
    o1 = SH_BASE + SH_SPAN * k / SH_STRIPS
    o2 = SH_BASE + SH_SPAN * (k + 1) / SH_STRIPS
    a = int(200 * (1.0 - k / SH_STRIPS) ** 1.4)
    if a <= 0:
        continue
    pygame.draw.polygon(dog, (*SH, a), [
        (HYP_A[0] + o1, HYP_A[1] + o1), (HYP_B[0] + o1, HYP_B[1] + o1),
        (HYP_B[0] + o2, HYP_B[1] + o2), (HYP_A[0] + o2, HYP_A[1] + o2)])

# (2) Crease seam — the thin, even dark gap where the sheet folds over. Lifted
# to (22,23,42) so its tips read smooth, not the harsh near-black of r1.
pygame.draw.line(dog, (*CREASE, 235),
                 (HYP_A[0] + 0.8, HYP_A[1] + 0.8),
                 (HYP_B[0] + 0.8, HYP_B[1] + 0.8), 2)

# (3) Fold face with paper-curl gradient. Lines parallel to the crease sweep the
# corner tip (u=0, dim) → crease (u=1, warm/bright); opaque so they fully cover
# the indigo body corner. Slight overshoot width closes inter-line seams.
STEPS = 120
for i in range(STEPS + 1):
    u = i / STEPS
    col = _lerp(CURL_TIP, CURL_CREASE, u)
    pygame.draw.line(dog, col,
                     (ri + FOLD * u, ri), (ri, ri + FOLD * u), 2)

# (4) Crease highlight — the single hottest edge riding the fold line.
pygame.draw.line(dog, HILITE, HYP_A, HYP_B, 1)

# (5) Gold checkmark — centred in the fold's meaty middle (~x24/y22), ×2 the r1
# size and ringed by clean cream so it survives the 1× read. A darker-gold drop
# and rounded joints give it weight without muddying the tick.
TICK = [(17, 22), (23, 28), (33, 13)]
TICK_SH = [(x + 1, y + 1) for (x, y) in TICK]
pygame.draw.lines(dog, (*GOLD_DK, 175), False, TICK_SH, 4)
pygame.draw.lines(dog, GOLD, False, TICK, 4)
for (x, y) in TICK:
    pygame.draw.circle(dog, GOLD, (x, y), 2)

# Clip the whole peel to the card body's rounded silhouette.
mask = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.rect(mask, (255, 255, 255, 255), rect, border_radius=rad)
dog.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
p2.blit(dog, (0, 0))


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

title_f = hud_font(22, True)
tt = title_f.render("equipped v2 — corner-dogear · skin_mummy · r2", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

GREY = (150, 152, 168)
CREAM_LBL = (250, 246, 232)
labels = [("UNEQUIPPED", GREY), ("STOCK EQUIPPED", GREY),
          ("CORNER DOGEAR", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)
panel_y = PAD + HDR_H + LBL_H
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

    # 1× read: downscale the panel to true card size, then blow it back up
    # nearest-neighbour so the sheet shows how the peel resolves at 1×.
    card1x = pygame.transform.smoothscale(panel, (ONE_W, ONE_H))
    zoom = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
    zt = zlbl_f.render("@1× (rendered then 2× nearest)", True, GREY)
    sheet.blit(zt, zt.get_rect(midbottom=(px + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
    sheet.blit(zoom, (px + (PANEL_W - ZOOM_W) // 2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v2", "corner_dogear", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
