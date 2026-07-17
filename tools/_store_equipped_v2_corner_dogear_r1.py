#!/usr/bin/env python3
"""
equipped-card v2 — corner-dogear concept, round 1.

Instead of the green EQUIPPED chip, the card's upper-left corner peels back like
a turned page: a warm-cream fold triangle sits in the empty quadrant the price
tag left behind. Reads as "dog-ear = I've marked/claimed this one." Top-left is
the one layout-safe quadrant (dome centred, gem top-right, ribbon/name/chip in
the lower half), so the fold never collides with live card content.

Drawn LAST over an equipped card whose green chip is suppressed: a crease shadow
edge, a soft cast shadow past the fold, a bright warm-cream fold face, a hot
crease highlight, and a gold serif tick. All clipped to the card body's rounded
silhouette so the flap follows the corner radius instead of a hard bite.
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
CREAM = (250, 246, 232)
HILITE = (255, 252, 240)
GOLD = (236, 202, 116)

# Everything lands on a panel-sized overlay so a single rounded-body mask clips
# the fold to the corner radius (a real peel follows the card silhouette).
dog = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)

# (1) Crease shadow edge — the dark gap under the lifted flap.
pygame.draw.line(dog, (10, 10, 28, 220),
                 (ri + FOLD, ri), (ri, ri + FOLD), 2)

# (2) Soft cast shadow of the flap onto the body, just past the crease.
shadow = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.polygon(shadow, (6, 6, 20, 160),
                    [(ri, ri), (ri + FOLD + 3, ri), (ri, ri + FOLD + 3)])
dog.blit(shadow, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)

# (3) Warm-cream fold face — bright + warm against the indigo body.
pygame.draw.polygon(dog, CREAM,
                    [(ri, ri), (ri + FOLD, ri), (ri, ri + FOLD)])

# (4) Crease highlight — the hottest pixel along the fold edge.
pygame.draw.line(dog, HILITE, (ri + FOLD, ri), (ri, ri + FOLD), 1)

# (5) Gold serif tick — "claimed", set in the lower-right quarter of the flap.
pygame.draw.lines(dog, GOLD, False,
                  [(ri + 9, ri + 22), (ri + 16, ri + 30), (ri + 30, ri + 11)],
                  3)

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
tt = title_f.render("equipped v2 — corner-dogear · skin_mummy", True, GOLD)
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
    "docs", "store_equipped_v2", "corner_dogear", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
