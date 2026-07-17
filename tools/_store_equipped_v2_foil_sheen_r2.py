#!/usr/bin/env python3
"""
equipped-card foil-sheen concept (v2) — round 2.

Ownership is signalled by a pre-baked gold CROWN watermark in the upper-left
quadrant (where the price tag lived) that reads on its own at rest, plus a warm
cream-gold foil sweep that is authored to pass THROUGH the crown so the sheen
lights the mark to full brightness as it crosses. The crown carries ownership on
a static frame; the sheen is the animated flourish that makes it bloom.

Warm-foil tuning: BLEND_RGB_ADD over the dark indigo body desaturates any cool
tint, so the additive channels are pushed hard toward gold (R >> B) — a
premultiplied cream->gold ramp — so the band core resolves warm cream-gold, not
grey/lavender. A second thinner parallel highlight + a faint spectral flank make
it read as foil MATERIAL rather than a single lighting smudge.

The equipped panel suppresses the stock EQUIPPED chip so crown + sheen alone
carry ownership. Strictly cream-gold — no prismatic/rainbow refraction.
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
    """White rounded-rect matching the card body — clips normal-alpha layers to
    the card silhouette so foil never bleeds into the margin."""
    mask = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), rect, border_radius=CARD_RAD)
    return mask


def _card_rgb_mask():
    """Black field, WHITE rounded-rect over the body. BLEND_RGB_ADD ignores alpha,
    so premultiplied additive layers get clipped by MULTIPLYING RGB against this
    (white=keep inside, black=kill outside)."""
    mask = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 255))
    pygame.draw.rect(mask, (255, 255, 255, 255), rect, border_radius=CARD_RAD)
    return mask


CARD_MASK = _card_mask()
CARD_RGB_MASK = _card_rgb_mask()


# ── Panel 0 — UNEQUIPPED ──────────────────────────────────────────────────────
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
# Suppress the stock chip: crown + sheen ARE the ownership signal.
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()

GOLD_WM = (236, 202, 116)     # crown watermark / revealed mark

# The crown lives where the price tag was — upper-left quadrant, centred on the
# band's bright core so the sweep OVERLAPS the mark. Single bold 5-point polygon.
CX_WM, CY_WM = 44, 52


def _crown_pts(cx, cy):
    """A bold 5-point crown silhouette centred on (cx, cy) — a wider base band
    with five spikes; the centre spike tallest so it reads unmistakably as a
    crown, not a checkmark, at a glance and at 1×."""
    return [
        (cx - 22, cy + 14),   # bottom-left
        (cx - 18, cy - 12),   # peak 1 (outer left)
        (cx - 13, cy),        # valley
        (cx - 9,  cy - 15),   # peak 2
        (cx - 4,  cy),        # valley
        (cx,      cy - 18),   # peak 3 (centre, tallest)
        (cx + 4,  cy),        # valley
        (cx + 9,  cy - 15),   # peak 4
        (cx + 13, cy),        # valley
        (cx + 18, cy - 12),   # peak 5 (outer right)
        (cx + 22, cy + 14),   # bottom-right
    ]


CROWN = _crown_pts(CX_WM, CY_WM)
JEWELS = [(CX_WM - 18, CY_WM - 12), (CX_WM, CY_WM - 18), (CX_WM + 18, CY_WM - 12)]
BASE_BAND = pygame.Rect(CX_WM - 22, CY_WM + 6, 44, 8)   # solid coronet base


def _draw_crown(alpha):
    """Bake the crown at a given alpha onto a fresh SRCALPHA layer, clipped to the
    card body, and return it — used both for the resting watermark and the
    band-masked bloom reveal."""
    layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.polygon(layer, (*GOLD_WM, alpha), CROWN)
    pygame.draw.rect(layer, (*GOLD_WM, alpha), BASE_BAND)
    for jx, jy in JEWELS:
        pygame.draw.circle(layer, (*GOLD_WM, alpha), (jx, jy), sc.m(1.4))
    layer.blit(CARD_MASK, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return layer


# Step 1 — bake the resting crown at baseline alpha 62: an ownership mark that
# survives a static frame WITHOUT the band.
p2.blit(_draw_crown(62), (0, 0))

# Step 2 — the warm cream-gold foil band, routed THROUGH the crown at (44,52) and
# on through the card centre. Diagonal top-left -> bottom-right.
# yc(x) is authored so yc(44)=52 (over the crown) and yc(162)=100 (card centre).
SLOPE = 0.42
band = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)         # premult foil
band_mask = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)    # alpha stencil

# BLEND_RGB_ADD over dark indigo desaturates cool tints, so the additive channels
# are pushed hard toward gold (R >> B). These premultiplied peaks are tuned so the
# core lifts the body to warm cream-gold (R≥210, G≥180, B≤150), never grey.
CORE_ADD  = (206, 172,  88)   # centre of the band — warm cream-gold
EDGE_ADD  = (188, 146,  56)   # flanks — deeper saturated gold (the cream->gold ramp)
HALF = 18                     # main band half-width (device px)

# secondary thinner parallel highlight, offset below the core at ~half the peak —
# gives the foil visible structure instead of one flat stripe.
OFF2 = 15
HALF2 = 7
SEC_ADD = (150, 122, 66)      # dimmer warm gold

# a very faint spectral flank on the LEADING (upper) edge — a slight cool hue
# shift, NOT a rainbow, so the sweep reads as material refraction.
OFF3 = -20
HALF3 = 5
SPEC_ADD = (58, 74, 96)       # cool cream hint, kept low


def _stripe(add_col, y_at, half, x):
    """Premultiplied triangular falloff for one stripe at column x; writes into
    `band` (additive premult) + `band_mask` (alpha) via max-compositing so the
    stripes stack without darkening one another."""
    y0 = max(0, int(y_at - half))
    y1 = min(PANEL_H - 1, int(y_at + half))
    for y in range(y0, y1 + 1):
        f = 1.0 - abs(y - y_at) / half
        if f <= 0:
            continue
        r = int(add_col[0] * f)
        g = int(add_col[1] * f)
        b = int(add_col[2] * f)
        pr, pg, pb, pa = band.get_at((x, y))
        band.set_at((x, y), (max(pr, r), max(pg, g), max(pb, b), 255))
        a = int(255 * f)
        _, _, _, ma = band_mask.get_at((x, y))
        band_mask.set_at((x, y), (255, 255, 255, max(ma, a)))


for x in range(PANEL_W):
    yc = CY_WM + (x - CX_WM) * SLOPE
    # cream->gold ramp: brighter cream core blending to saturated gold flanks.
    _stripe(EDGE_ADD, yc, HALF, x)
    _stripe(CORE_ADD, yc, HALF * 0.55, x)     # warm cream inner core
    _stripe(SEC_ADD, yc + OFF2, HALF2, x)     # second highlight line
    _stripe(SPEC_ADD, yc + OFF3, HALF3, x)    # faint cool spectral flank

band.blit(CARD_RGB_MASK, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
band_mask.blit(CARD_MASK, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
p2.blit(band, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

# Step 3 — reveal: the crown at FULL opacity, masked by the band alpha so it only
# blooms WHERE the sheen crosses it. Layered over the resting mark.
bloom = _draw_crown(255)
bloom.blit(band_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
p2.blit(bloom, (0, 0))
p2.blit(bloom, (0, 0))     # a second pass lifts the lit crown clear of the body

# Step 4 — thin cream catchlight along the top inner edge where the band exits.
catch = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.line(catch, (248, 238, 210, 55), (rect.left, rect.top + sc.m(2)),
                 (rect.right, rect.top + sc.m(2)), 1)
catch.blit(CARD_MASK, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
p2.blit(catch, (0, 0))


# ── Compose the review sheet: hero row + true-1× game-size strip ───────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 22, 26
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
labels = [("UNEQUIPPED", GREY), ("STOCK EQUIPPED", GREY), ("CROWN + FOIL SHEEN", GOLD_WM)]

lbl_f = hud_font(15, True)
row1_y = PAD + HDR_H + LBL_H
for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, row1_y - 6)))
    sheet.blit(panel, (px, row1_y))

# TRUE 1× strip: smoothscale each SS=2 panel down to the live 162×100 card, then
# nearest-scale ×2 to 324×200 so the reviewer sees the ACTUAL game-native pixels
# (the crown + band must survive the real downscale), not a same-size SS panel.
sub_y = row1_y + PANEL_H + SGAP
sub_f = hud_font(13, True)
st = sub_f.render(
    "TRUE 1× — smoothscaled to game-native 162×100, then nearest ×2 to show real pixels",
    True, GREY)
sheet.blit(st, st.get_rect(midbottom=(sheet_w // 2, sub_y + SLBL_H - 5)))
row2_y = sub_y + SLBL_H
for i, panel in enumerate(panels):
    card1x = pygame.transform.smoothscale(panel, (162, 100))
    disp = pygame.transform.scale(card1x, (PANEL_W, PANEL_H))   # nearest ×2
    px = PAD + i * (PANEL_W + GAP)
    sheet.blit(disp, (px, row2_y))

OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v2", "foil_sheen", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())


# ── Pixel verify — warm-foil tint + crown reveal must both survive ────────────
from PIL import Image
img = Image.open(OUT).convert("RGB")
x0_c, y0_c = PAD + 2 * (PANEL_W + GAP), row1_y     # concept panel origin
x0_u, y0_u = PAD, row1_y                            # unequipped panel origin

# band core over the card BODY (left of the dome) — must be warm cream-gold.
bx, by = 80, int(CY_WM + (80 - CX_WM) * SLOPE)
print(f"band core @body ({bx},{by}): {img.getpixel((x0_c + bx, y0_c + by))} "
      f"(target R>=210 G>=180 B<=150)")
# crown centre — resting vs lit; concept must differ from unequipped there.
print(f"crown ctr concept: {img.getpixel((x0_c + CX_WM, y0_c + CY_WM))}, "
      f"uneq same spot: {img.getpixel((x0_u + CX_WM, y0_u + CY_WM))}")
