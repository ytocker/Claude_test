#!/usr/bin/env python3
"""
equipped-card foil-sheen concept (v2) — round 1.

The ownership signal is the SHINE itself: a single diagonal foil sweep in warm
cream slides across the card and, where it crosses a pre-baked gold watermark
tick, makes that mark bloom into view. At rest the tick is a near-invisible
gold ghost (~alpha 30); the sheen is what carries the "you own this" cue, not a
separate chip. Strictly cream-gold — no prismatic/rainbow refraction — so it
reads as gold foil, not an oil-slick hologram.

The equipped panel suppresses the stock EQUIPPED chip so the sheen alone speaks
for ownership. The band is authored to pass through the card centre AND across
the watermark, so the glint reveals the mark instead of merely decorating a
corner.
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
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
CARD_RAD = sc.m(sc.CARD_RAD)


def _card_mask():
    """White rounded-rect matching the card body — used to clip normal-alpha
    layers to the card silhouette so cream never bleeds into the margin."""
    mask = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), rect, border_radius=CARD_RAD)
    return mask


def _card_rgb_mask():
    """Black field with a WHITE rounded-rect over the body. BLEND_RGB_ADD ignores
    alpha, so premultiplied additive layers must be clipped by MULTIPLYING RGB
    against this (white=keep inside, black=kill outside)."""
    mask = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 255))
    pygame.draw.rect(mask, (255, 255, 255, 255), rect, border_radius=CARD_RAD)
    return mask


CARD_MASK = _card_mask()
CARD_RGB_MASK = _card_rgb_mask()


# ── Panel 0 — UNEQUIPPED ──────────────────────────────────────────────────────
# Force affordability so the price chip reads gold, not wallet-locked grey.
orig_bal = sd.balance
sd.balance = lambda: 99999
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)
sd.balance = orig_bal


# ── Panel 1 — STOCK EQUIPPED ──────────────────────────────────────────────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False)


# ── Panel 2 — FOIL-SHEEN CONCEPT ──────────────────────────────────────────────
# Suppress the stock chip: the sheen is the ownership signal, not a badge.
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()

GOLD_WM = (236, 202, 116)     # watermark ghost / revealed mark
CREAM = (248, 238, 210)       # the one foil colour — warm, never prismatic
# The hidden tick, authored so the diagonal band sweeps ALONG its length. Elbow
# low, two arms rising to the right — sits left-of-centre, partly under the dome.
TICK_PTS = [(96, 118), (120, 146), (158, 92)]
TICK_W = sc.m(5)

# Step 1 — bake the watermark into p2 as a near-invisible gold ghost.
wm = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.lines(wm, (*GOLD_WM, 30), False, TICK_PTS, TICK_W)
wm.blit(CARD_MASK, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
p2.blit(wm, (0, 0))

# Step 2 — the diagonal foil band at -30°, pivoted on the card centre so it
# passes through the middle and rides across the tick. Warm cream only.
band = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)         # premult cream
band_mask = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)    # alpha stencil
tan30 = math.tan(math.radians(30))
HALF = 20
# BLEND_RGB_ADD adds source RGB regardless of alpha, so the falloff is baked
# INTO the cream channels (premultiplied) — a raw alpha ramp would add full cream
# everywhere and blow the sweep to a flat white bar. The peak is tuned so dark
# card body lifts to a clear warm-cream glint while the dome only kisses hot.
cr, cg, cb = CREAM
PEAK = 108
for x in range(PANEL_W):
    yc = PANEL_H // 2 - (x - PANEL_W // 2) * tan30
    y0 = max(0, int(yc - HALF))
    y1 = min(PANEL_H - 1, int(yc + HALF))
    for y in range(y0, y1 + 1):
        a = int(PEAK * (1 - abs(y - yc) / HALF))
        if a <= 0:
            continue
        band.set_at((x, y), (cr * a // 255, cg * a // 255, cb * a // 255, 255))
        band_mask.set_at((x, y), (255, 255, 255, a))
band.blit(CARD_RGB_MASK, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
band_mask.blit(CARD_MASK, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
p2.blit(band, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

# Step 3 — reveal: a bright gold tick masked by the band, so the mark only
# blooms WHERE the sheen crosses it. Blitted twice to lift it clear of rest.
bright = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.lines(bright, (*GOLD_WM, 255), False, TICK_PTS, TICK_W)
reveal = bright.copy()
reveal.blit(band_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
p2.blit(reveal, (0, 0))
p2.blit(reveal, (0, 0))

# Step 4 — thin cream catchlight along the top inner edge where the band exits.
catch = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.line(catch, (*CREAM, 60), (rect.left, rect.top + sc.m(2)),
                 (rect.right, rect.top + sc.m(2)), 1)
catch.blit(CARD_MASK, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
p2.blit(catch, (0, 0))


# ── Compose the review sheet: hero row + 1× game-size strip ────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
N = 3
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + SGAP + SLBL_H + PANEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v2 — foil-sheen · skin_mummy", True, GOLD_WM)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

GREY = (150, 152, 168)
panels = [p0, p1, p2]
labels = [("UNEQUIPPED", GREY), ("STOCK EQUIPPED", GREY), ("FOIL SHEEN", GOLD_WM)]

lbl_f = hud_font(15, True)
row1_y = PAD + HDR_H + LBL_H
for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, row1_y - 6)))
    sheet.blit(panel, (px, row1_y))

# 1× strip: smoothscale to the live 162×100 card, then nearest-scale back up so
# the reviewer can judge how the sheen + reveal survive the real downscale.
sub_y = row1_y + PANEL_H + SGAP
sub_f = hud_font(13, True)
st = sub_f.render("AT GAME SIZE  (162×100, nearest-scaled ×2 to show pixels)",
                  True, GREY)
sheet.blit(st, st.get_rect(midbottom=(sheet_w // 2, sub_y + SLBL_H - 4)))
row2_y = sub_y + SLBL_H
for i, panel in enumerate(panels):
    card1x = pygame.transform.smoothscale(panel, (162, 100))
    disp = pygame.transform.scale(card1x, (PANEL_W, PANEL_H))
    px = PAD + i * (PANEL_W + GAP)
    sheet.blit(disp, (px, row2_y))

OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v2", "foil_sheen", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())


# ── Pixel verify — concept must differ from unequipped on the diagonal band ───
from PIL import Image
img = Image.open(OUT).convert("RGB")
x0_c, y0_c = PAD + 2 * (PANEL_W + GAP), row1_y     # concept panel origin
x0_u, y0_u = PAD, row1_y                            # unequipped panel origin
cx, cy = x0_c + PANEL_W // 2, y0_c + PANEL_H // 2
px_concept = img.getpixel((cx, cy))
px_uneq = img.getpixel((x0_u + PANEL_W // 2, y0_u + PANEL_H // 2))
print(f"Concept mid: {px_concept}, Uneq mid: {px_uneq}")
# also sample a point on the revealed tick to confirm the mark blooms
tx, ty = x0_c + 120, y0_c + 118
print(f"Concept on-tick: {img.getpixel((tx, ty))}, "
      f"Uneq same spot: {img.getpixel((x0_u + 120, y0_u + 118))}")
