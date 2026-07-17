#!/usr/bin/env python3
"""
equipped-card corner-seal concept — round 2.

Round 1 validated the top-left "pinned badge" placement and the mint
keyline. Four elements failed at 162×100 final size and are replaced here:

  - Black shadow → two-arc light-lift: a bright arc upper-left (overhead
    light) plus a dim arc lower-right (shade), held together by a hairline
    dark separation ring. Physical depth without the muddy bleed.
  - Flat enamel → procedural radial dome: centre-col lighter, rim-col
    darker, drawn inside-out so the disc reads as convex struck enamel.
  - Sub-pixel scallops → a single-pixel gold ring, matching the card's own
    rim gold language at every size.
  - Thin checkmark → width m(4)=8, checkmark geometry scaled to fill ~63%
    of the disc so it survives the 2×→1× downscale legibly.

A 1× strip at the bottom shows all three states at the true 162×100 game
footprint for pixel-level sanity.
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

PANEL_W = sc.CARD_W * sc.SS   # 324
PANEL_H = sc.CARD_H * sc.SS   # 200
rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                   PANEL_W - 2 * sc.m(sc._INSET), PANEL_H - 2 * sc.m(sc._INSET))

SID = "skin_mummy"
lerp = lambda a, b, t: a + (b - a) * t


# ── Panel 1 — UNEQUIPPED ──────────────────────────────────────────────────────
# Force affordability so the price chip reads gold, not wallet-locked grey.
orig_bal = sd.balance
sd.balance = lambda: 99999
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=False, secret=False)
sd.balance = orig_bal
sc._card_cache.clear()


# ── Panel 2 — BASE EQUIPPED ───────────────────────────────────────────────────
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc._card_cache.clear()


# ── Panel 3 — CORNER-SEAL CONCEPT ─────────────────────────────────────────────
p3 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p3, SID, rect, equipped=True, secret=False)
sc._card_cache.clear()

cx_seal = rect.x + sc.m(20)   # 48 at SS=2
cy_seal = rect.y + sc.m(20)   # 48 at SS=2
R = sc.m(11)                   # 22 at SS=2 — trimmed 10% vs round 1

# (a) Thin dark separation ring — keeps the badge readable where it
#     crosses the card's gold rim without the bleed of a full shadow.
pygame.draw.circle(p3, (4, 5, 16), (cx_seal, cy_seal), R + 2, width=2)

# (b) Domed enamel disc — radial gradient, lightest at centre, darkest
#     at rim, drawn inside-out so concentric rings produce a convex dome.
center_col = (22, 110, 70)
edge_col   = (10,  70, 44)
for r_step in range(R, 0, -1):
    t  = 1 - r_step / R
    dr = int(lerp(center_col[0], edge_col[0], t))
    dg = int(lerp(center_col[1], edge_col[1], t))
    db = int(lerp(center_col[2], edge_col[2], t))
    pygame.draw.circle(p3, (dr, dg, db), (cx_seal, cy_seal), r_step)

# (c) Light-lift arcs — bright arc upper-left reads as overhead lighting;
#     dim arc lower-right provides the opposing shade pocket.
for angle in range(225, 360, 3):
    ax = cx_seal + int(math.cos(math.radians(angle)) * (R - 3))
    ay = cy_seal + int(math.sin(math.radians(angle)) * (R - 3))
    pygame.draw.circle(p3, (40, 160, 100, 180), (ax, ay), max(1, sc.m(0.8)))

for angle in range(45, 180, 3):
    ax = cx_seal + int(math.cos(math.radians(angle)) * (R - 3))
    ay = cy_seal + int(math.sin(math.radians(angle)) * (R - 3))
    pygame.draw.circle(p3, (6, 50, 30, 120), (ax, ay), max(1, sc.m(0.8)))

# (d) Gold outer ring — single-pixel ring at R+1 echoes the card's own
#     gold rim language; scallops are dropped because they vanish at 1×.
CARD_RING_BRIGHT = (236, 202, 116)
pygame.draw.circle(p3, (*CARD_RING_BRIGHT, 180), (cx_seal, cy_seal), R + 1,
                   width=max(1, sc.m(1)))

# (e) Mint keyline ring — the medal-face inner ring; adjusted radius for
#     the trimmed disc so the gap to the dome edge stays proportional.
pygame.draw.circle(p3, (100, 230, 148), (cx_seal, cy_seal), R - 3,
                   width=max(1, sc.m(1)))

# (f) Bold checkmark — width m(4)=8, geometry scaled to 63% of disc
#     interior so both strokes survive the 2×→1× downscale at any size.
check_pts = [
    (cx_seal - sc.m(6), cy_seal + sc.m(1)),
    (cx_seal - sc.m(1), cy_seal + sc.m(6)),
    (cx_seal + sc.m(8), cy_seal - sc.m(5)),
]
pygame.draw.lines(p3, (160, 248, 190), False, check_pts, width=max(1, sc.m(4)))


# ── Compose the 2-row review sheet ────────────────────────────────────────────
BG     = (8, 8, 20)
PAD    = 20
GAP    = 16
HDR_H  = 48
LBL_H  = 34

CARD_W1 = sc.CARD_W    # 162
CARD_H1 = sc.CARD_H    # 100
LBL1_H  = 28
STRIP_H = LBL1_H + CARD_H1 + 20

sheet_w = PAD + 3 * PANEL_W + 2 * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + GAP + STRIP_H + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render(
    "equipped card — corner-seal · skin_mummy · round 2", True, (236, 202, 116)
)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

GREY   = (150, 152, 168)
MINT   = (100, 230, 148)
labels = [("UNEQUIPPED", GREY), ("BASE EQUIPPED", GREY), ("CORNER-SEAL", MINT)]
panels = [p1, p2, p3]

lbl_f   = hud_font(15, True)
panel_y = PAD + HDR_H + LBL_H

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

# ── 1× strip — each panel smoothscaled to the true 162×100 game size ─────────
# The only reliable way to judge badge legibility is at the pixel count the
# player actually sees; the 2× author surface always looks deceptively good.
strip_y    = panel_y + PANEL_H + GAP
lbl1_f     = hud_font(13, False)
strip_head = lbl1_f.render("1× final pixels", True, (180, 180, 200))
sheet.blit(strip_head, strip_head.get_rect(midtop=(sheet_w // 2, strip_y)))

card_row_y = strip_y + LBL1_H
for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px     = PAD + i * (PANEL_W + GAP)
    small  = pygame.transform.smoothscale(panel, (CARD_W1, CARD_H1))
    dest_x = px + (PANEL_W - CARD_W1) // 2
    sheet.blit(small, (dest_x, card_row_y))
    lt1 = lbl1_f.render(label, True, col)
    sheet.blit(lt1, lt1.get_rect(midtop=(px + PANEL_W // 2, card_row_y + CARD_H1 + 4)))

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_equipped", "corner_seal", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
