#!/usr/bin/env python3
"""
equipped-card v3 — charm-drop concept, round 2 (final pass).

The equipped state hangs a chunky gold MEDAL pendant off the bottom-center edge
of the card. Round 2 sharpens the silhouette so it can never be misread as a
plain coin: a real bail LOOP (an O-ring) protrudes above the card edge, the disc
is nicked into a medal by a downward point at its foot, and the whole charm is
wrapped in a cream/ivory outline halo so the bright edge reads on ANY background
— not just the dark indigo store. The disc face is reduced to two flat values (a
warm-gold lit center + a single darker rim); the fussy star intaglio is dropped
because at 1× the SHAPE does the disambiguation, not surface detail.

The concept panel is drawn onto a TALLER 324×240 surface so the medal can hang
below the 324×200 card body. All three panels share that tall height so the
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


# ── Panel 2 — CONCEPT (chip suppressed, gold medal pendant below the body) ────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None           # the charm carries the state
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H_TALL), pygame.SRCALPHA)
p2_card = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2_card, SID, rect, equipped=True, secret=False)
p2.blit(p2_card, (0, 0))
sc.state_chip = orig_chip
sc._card_cache.clear()


# Charm palette — two flat disc values plus a bright cream lock-edge.
CREAM = (248, 238, 210)         # ivory outline halo — reads on light OR dark bg
GOLD_RIM = (198, 148, 58)       # single darker rim value
GOLD_LIT = (255, 230, 149)      # warm-gold lit center zone
GOLD_BAIL = (232, 196, 110)     # loop/link metal
DARK_KEY = (72, 46, 14)         # crisp struck keyline


def draw_pendant(surf):
    """A chunky gold MEDAL clipped over the card's bottom edge and hanging below
    it. Built back-to-front so each layer reads as physical metal catching a
    top-left light. The silhouette — a protruding bail O-ring, a pointed medal
    foot, and a cream lock-edge all the way round — is what sells 'pendant',
    never a coin."""
    edge_y = 192                # card body bottom edge (device px on this canvas)
    cx = 162                    # card horizontal center
    disc_cx, disc_cy = 162, 214
    disc_r = 18
    point_y = disc_cy + disc_r + 6      # medal foot tip, below the disc

    # (1) Cast shadow — a soft dark seat that lifts the hanging metal off the
    # dark sky. Covers disc + foot so the whole charm sits on one shadow.
    shadow = pygame.Surface((PANEL_W, PANEL_H_TALL), pygame.SRCALPHA)
    pygame.draw.circle(shadow, (0, 0, 0, 120), (disc_cx + 3, disc_cy + 4),
                       disc_r + 3)
    pygame.draw.polygon(shadow, (0, 0, 0, 90),
                        [(disc_cx - disc_r + 4, disc_cy + 6),
                         (disc_cx + disc_r + 2, disc_cy + 6),
                         (disc_cx + 3, point_y + 4)])
    surf.blit(shadow, (0, 0))

    # (2) Bail LOOP — a true O-ring straddling the card edge and protruding ABOVE
    # it, so the outline stops being a circle the instant the eye reaches the top.
    # A thick gold annulus (outer disc minus a punched hole) with a cream lock-edge
    # and a dark inner keyline reads as a metal ring you could thread a cord through.
    loop_cy = edge_y - 4                # center sits ABOVE the card bottom edge
    loop_ro, loop_ri = 7, 3
    pygame.draw.circle(surf, CREAM, (cx, loop_cy), loop_ro + 1)      # halo
    pygame.draw.circle(surf, GOLD_BAIL, (cx, loop_cy), loop_ro)      # ring body
    pygame.draw.circle(surf, DARK_KEY, (cx, loop_cy), loop_ro, 1)    # outer key
    # punch the hole clean through to the card/sky behind so it reads as open
    hole = pygame.Surface((loop_ri * 2 + 2, loop_ri * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(hole, (0, 0, 0, 0), (loop_ri + 1, loop_ri + 1), loop_ri)
    surf.blit(hole, (cx - loop_ri - 1, loop_cy - loop_ri - 1),
              special_flags=pygame.BLEND_RGBA_MULT)
    pygame.draw.circle(surf, DARK_KEY, (cx, loop_cy), loop_ri + 1, 1)  # hole rim
    # top-left glint on the ring so it reads as polished
    pygame.draw.line(surf, (255, 244, 200),
                     (cx - 4, loop_cy - 4), (cx - 1, loop_cy - 6), 1)

    # (3) Hang link — a short bar bridging the loop and the disc so the medal
    # reads as SUSPENDED from the ring, not fused to it.
    link = pygame.Rect(cx - 2, loop_cy + loop_ro - 1, 4, disc_cy - disc_r
                       - (loop_cy + loop_ro) + 3)
    pygame.draw.rect(surf, GOLD_BAIL, link, border_radius=2)
    pygame.draw.rect(surf, DARK_KEY, link, width=1, border_radius=2)
    pygame.draw.line(surf, (255, 240, 190), (link.x + 1, link.y + 1),
                     (link.x + 1, link.bottom - 1), 1)

    # (4) Medal FOOT — a downward point nicked out of the disc's bottom so the
    # circle is broken into a tag/medal. Cream-edged like the disc so the lock
    # halo is continuous around the whole silhouette.
    foot = [(disc_cx - 7, disc_cy + disc_r - 4),
            (disc_cx + 7, disc_cy + disc_r - 4),
            (disc_cx, point_y)]
    foot_halo = [(disc_cx - 9, disc_cy + disc_r - 4),
                 (disc_cx + 9, disc_cy + disc_r - 4),
                 (disc_cx, point_y + 2)]
    pygame.draw.polygon(surf, CREAM, foot_halo)
    pygame.draw.polygon(surf, GOLD_RIM, foot)
    pygame.draw.polygon(surf, DARK_KEY, foot, 1)

    # (5) Medal DISC — cream lock-halo backing, then a single darker rim value,
    # then the warm-gold lit center. Two flat face values; the shape (not surface
    # intaglio) carries the read at 1×.
    pygame.draw.circle(surf, CREAM, (disc_cx, disc_cy), disc_r + 2)   # halo
    pygame.draw.circle(surf, GOLD_RIM, (disc_cx, disc_cy), disc_r)    # rim value
    pygame.draw.circle(surf, GOLD_LIT, (disc_cx, disc_cy), disc_r - 7)  # lit face
    # a crisp struck line between the two face values so the rim reads deliberate
    pygame.draw.circle(surf, (150, 108, 44), (disc_cx, disc_cy), disc_r - 7, 1)

    # (6) Top-left rim highlight — a short bright arc so the polished metal catches
    # the same top-left light as the rest of the card.
    hl = pygame.Surface((disc_r * 2 + 6, disc_r * 2 + 6), pygame.SRCALPHA)
    c = disc_r + 3
    pygame.draw.arc(hl, (255, 250, 220, 235),
                    (c - disc_r + 2, c - disc_r + 2, disc_r * 2 - 4, disc_r * 2 - 4),
                    math.radians(108), math.radians(186), 2)
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
tt = title_f.render("equipped v3 — charm-drop · skin_mummy · round 2", True, GOLD)
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

    # 1× read: downscale the tall panel to true card width on the store indigo
    # ground, blow it back up nearest-neighbour so the sheet shows how the medal
    # resolves at 1× against the real background.
    ground = pygame.Surface((ONE_W, ONE_H))
    ground.fill(BG)                          # ~(8,8,20) store indigo
    card1x = pygame.transform.smoothscale(panel, (ONE_W, ONE_H))
    ground.blit(card1x, (0, 0))
    zoom = pygame.transform.scale(ground, (ZOOM_W, ZOOM_H))
    zt = zlbl_f.render("@1× on store bg (2× nearest)", True, GREY)
    sheet.blit(zt, zt.get_rect(midbottom=(px + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
    sheet.blit(zoom, (px + (PANEL_W - ZOOM_W) // 2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3", "charm_drop", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
