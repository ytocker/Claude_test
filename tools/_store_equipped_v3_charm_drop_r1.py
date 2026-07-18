#!/usr/bin/env python3
"""
equipped-card v3 — charm-drop concept, round 1.

Instead of a flat in-body chip, the equipped state hangs a chunky gold medallion
pendant off the bottom-center edge of the card — like a physical charm clipped to
the item. The pendant breaks the card's lower silhouette: the bail hooks over the
body edge (y=192) and the medallion disc hangs BELOW it (center ~y=214). That
silhouette delta is the whole read — "this one has a charm on it, it's equipped."
No green chip; the charm carries the state on its own.

The concept panel is drawn onto a TALLER 324×240 surface so the disc has room to
hang below the 324×200 card body. All three panels share that tall height so the
sheet's rows line up.
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
from game.draw import lerp_color

sd.load()

SID = "skin_mummy"
PANEL_W = sc.CARD_W * sc.SS   # 324
PANEL_H = sc.CARD_H * sc.SS   # 200 — standard card body height
PANEL_H_TALL = 240            # taller so the pendant can hang below the body
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)


# ── Panel 0 — UNEQUIPPED (price tag visible), padded to the tall canvas ──────
sc._card_cache.clear()
p0_base = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0_base, SID, rect, equipped=False, secret=False)
p0 = pygame.Surface((PANEL_W, PANEL_H_TALL), pygame.SRCALPHA)
p0.blit(p0_base, (0, 0))


# ── Panel 1 — STOCK EQUIPPED (green chip, reference), padded ──────────────────
sc._card_cache.clear()
p1_base = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1_base, SID, rect, equipped=True, secret=False)
p1 = pygame.Surface((PANEL_W, PANEL_H_TALL), pygame.SRCALPHA)
p1.blit(p1_base, (0, 0))


# ── Panel 2 — CONCEPT (chip suppressed, gold charm pendant below the body) ────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None           # the charm carries the state
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H_TALL), pygame.SRCALPHA)
p2_card = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2_card, SID, rect, equipped=True, secret=False)
p2.blit(p2_card, (0, 0))
sc.state_chip = orig_chip
sc._card_cache.clear()


def draw_pendant(surf):
    """A chunky gold medallion clipped over the card's bottom edge and hanging
    below it. Built back-to-front — cast shadow, bail hook, hang link, then the
    struck disc — so each layer reads as physical metal catching a top-left
    light, and so the disc's lower half clears the card silhouette."""
    edge_y = 192                # card body bottom edge (device px on this canvas)
    cx = 162                    # card horizontal center
    disc_cx, disc_cy = 162, 214
    disc_r = 18

    # (1) Cast shadow first, so the whole charm sits on a soft dark seat that
    # separates the hanging metal from the dark sky behind it.
    shadow = pygame.Surface((PANEL_W, PANEL_H_TALL), pygame.SRCALPHA)
    pygame.draw.circle(shadow, (0, 0, 0, 120), (disc_cx + 3, disc_cy + 3),
                       disc_r + 2)
    surf.blit(shadow, (0, 0))

    # (2) Hang link — a short gold bar bridging the bail and the disc so the
    # medallion reads as SUSPENDED, not floating.
    link = pygame.Rect(cx - 2, 196, 4, 9)
    pygame.draw.rect(surf, (220, 185, 100), link, border_radius=2)
    pygame.draw.rect(surf, (58, 48, 22), link, width=1, border_radius=2)
    pygame.draw.line(surf, (250, 224, 150), (cx - 1, 197), (cx - 1, 204), 1)

    # (3) Bail loop — a gold clip straddling the card edge, so it reads as hooked
    # OVER the body rather than glued on. A dark keyline defines it against both
    # the card body above and the sky below.
    bail = pygame.Rect(cx - 5, edge_y - 4, 10, 8)
    pygame.draw.rect(surf, (236, 202, 116), bail, border_radius=3)
    pygame.draw.rect(surf, (58, 48, 22), bail, width=1, border_radius=3)
    # hollow of the hook + a top-left glint so it looks like a ring, not a slab
    pygame.draw.circle(surf, (120, 92, 40), (cx, edge_y), 2)
    pygame.draw.line(surf, (255, 240, 190), (cx - 4, edge_y - 3),
                     (cx + 3, edge_y - 3), 1)

    # (4) Medallion disc — concentric gold rings from a dark rim inward to a hot
    # center pip approximate a struck-coin radial gradient (outer rim -> face ->
    # hot center) without per-pixel work; a top-left offset keeps the light read.
    RIM = (150, 96, 28)
    FACE = (240, 200, 130)
    HOT = (255, 236, 180)
    for i in range(disc_r, 0, -1):
        t = 1.0 - i / disc_r                # 0 at rim, 1 at center
        if t < 0.55:
            col = lerp_color(RIM, FACE, t / 0.55)
        else:
            col = lerp_color(FACE, HOT, (t - 0.55) / 0.45)
        # nudge the lit center up-left so the disc reads as a domed coin
        ox = int(round(1.0 * t))
        oy = int(round(1.0 * t))
        pygame.draw.circle(surf, col, (disc_cx - ox, disc_cy - oy), i)

    # dark contact keyline — the crisp struck edge against the sky
    pygame.draw.circle(surf, (64, 40, 10), (disc_cx, disc_cy), disc_r, 1)

    # recessed intaglio well — a darkened inner disc that reads as stamped depth
    well = pygame.Surface((disc_r * 2, disc_r * 2), pygame.SRCALPHA)
    pygame.draw.circle(well, (120, 80, 30, 180), (disc_r, disc_r), 10)
    surf.blit(well, (disc_cx - disc_r, disc_cy - disc_r))
    pygame.draw.circle(surf, (72, 46, 14), (disc_cx, disc_cy), 10, 1)

    # (5) Struck mark — a lit 5-point star ornament sunk into the well.
    star_r, star_ri = 8, 3.4
    pts = []
    for k in range(10):
        rr = star_r if k % 2 == 0 else star_ri
        ang = -math.pi / 2 + k * math.pi / 5
        pts.append((disc_cx + rr * math.cos(ang), disc_cy + rr * math.sin(ang)))
    pygame.draw.polygon(surf, (250, 220, 140), pts)
    pygame.draw.polygon(surf, (150, 104, 40), pts, 1)
    # a small hot facet on the star's upper-left tip
    pygame.draw.circle(surf, (255, 244, 200), (disc_cx - 2, disc_cy - 3), 1)

    # (6) Bright rim highlight — a short top-left arc so the disc's upper rim
    # catches the light and the whole charm reads as polished metal.
    hl = pygame.Surface((disc_r * 2 + 4, disc_r * 2 + 4), pygame.SRCALPHA)
    c = disc_r + 2
    pygame.draw.arc(hl, (255, 246, 200, 230),
                    (c - disc_r + 1, c - disc_r + 1, disc_r * 2 - 2, disc_r * 2 - 2),
                    math.radians(112), math.radians(184), 2)
    surf.blit(hl, (disc_cx - c, disc_cy - c))


draw_pendant(p2)


# ── Compose the review sheet ─────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
PANEL_H_SHEET = PANEL_H_TALL                 # 240 — all panels share tall height
SGAP, SLBL_H = 20, 24
# 1× strip: the tall panel (324×240) downscaled to true 1× card width (162) keeps
# its aspect, so 324×240 -> 162×120.
ONE_W, ONE_H = 162, 120
ZOOM_W, ZOOM_H = ONE_W * 2, ONE_H * 2        # nearest-neighbour blow-up of 1×

N = 3
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H_SHEET + SGAP + SLBL_H + ZOOM_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

GOLD = (236, 202, 116)
title_f = hud_font(22, True)
tt = title_f.render("equipped v3 — charm-drop · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

GREY = (150, 152, 168)
CREAM_LBL = (250, 246, 232)
labels = [("UNEQUIPPED", GREY), ("STOCK EQUIPPED", GREY), ("CHARM DROP", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)
panel_y = PAD + HDR_H + LBL_H                 # 102
zlbl_y = panel_y + PANEL_H_SHEET + SGAP
zoom_y = zlbl_y + SLBL_H

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

    # 1× read: downscale the tall panel to true card width, blow it back up
    # nearest-neighbour so the sheet shows how the pendant resolves at 1×.
    card1x = pygame.transform.smoothscale(panel, (ONE_W, ONE_H))
    zoom = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
    zt = zlbl_f.render("@1× (rendered then 2× nearest)", True, GREY)
    sheet.blit(zt, zt.get_rect(midbottom=(px + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
    sheet.blit(zoom, (px + (PANEL_W - ZOOM_W) // 2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3", "charm_drop", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
