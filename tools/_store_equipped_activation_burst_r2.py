"""Headless review render for the `activation-burst` equipped-card — round 2.

Round-1 problems addressed:
  • White clipping: diamond bodies now draw at normal blend (solid mint, channels
    bounded by MINTGOLD_BODY) so the polygon silhouette stays readable.
  • Glints on-gem: both glints moved upper-left into the dark indigo body field
    where they read against the card, not lost inside the bright gem facets.
  • 3-glint fragmentation at 1x: reduced to 2 glints; short arm widened (2.2×)
    so each survives the smoothscale without dissolving into haze.
  • ADD bloom is a SEPARATE layer applied after the solid body, so the sparkle
    atmosphere is additive WITHOUT driving the body pixels to pure white.
  • 1× inset strip added so glints can be judged at real game scale.
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

# Panel is the SS=2 author canvas: 162*2 × 100*2
PANEL_W = 324
PANEL_H = 200
# Inset matches _INSET=4 at SS=2 so shadows + equipped halo land inside panel
rect = pygame.Rect(8, 8, 308, 184)

# Cool mint-white body: B lifted above G so it reads distinct from the warm
# emerald gasket and neutral gold rim — frozen crystal, not vegetal green.
MINTGOLD_BODY = (168, 235, 175)
# Near-white hot-point: still visibly mint, never paper-white.
MINTGOLD_HOT = (220, 252, 215)
# Pixel ceiling for the burst glow field (not the 1-2px hot pinpoint itself)
CLIP_CEIL = (235, 255, 220)


def draw_glint_solid(surf, cx, cy, long_r, short_r, angle_deg, color, hot):
    """Diamond body at normal blend, hot pinpoint as a tiny circle.

    Two overlapping rhombuses at 90° form the 4-point star. The short arm at
    2.2× (vs the earlier 2×) fills the squint arm wide enough to survive a
    smoothscale to 1× without fragmenting into disconnected specks.
    """
    a = math.radians(angle_deg)
    pa = a + math.pi / 2
    pts_long = [
        (cx + math.cos(a) * long_r,  cy + math.sin(a) * long_r),
        (cx + math.cos(pa) * short_r, cy + math.sin(pa) * short_r),
        (cx - math.cos(a) * long_r,  cy - math.sin(a) * long_r),
        (cx - math.cos(pa) * short_r, cy - math.sin(pa) * short_r),
    ]
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts_long])
    pts_short = [
        (cx + math.cos(pa) * short_r * 2.2, cy + math.sin(pa) * short_r * 2.2),
        (cx + math.cos(a) * short_r,        cy + math.sin(a) * short_r),
        (cx - math.cos(pa) * short_r * 2.2, cy - math.sin(pa) * short_r * 2.2),
        (cx - math.cos(a) * short_r,        cy - math.sin(a) * short_r),
    ]
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts_short])
    # Tiny pinpoint: the one pixel that looks like the exact "click" of equipping.
    pygame.draw.circle(surf, hot, (int(cx), int(cy)), max(1, sc.m(0.6)))


def _build_p3(bloom_peak_1, bloom_peak_2):
    """Render the activation-burst panel with given bloom peaks; returns surface."""
    p = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    sc.draw_card(p, "skin_mummy", rect, equipped=True, secret=False)
    sc._card_cache.clear()

    # Gem center (device-px) — same anchor as round 1
    gx, gy = rect.right - sc.m(19), rect.y + sc.m(19)   # (278, 46)

    # Both glints in the dark indigo field upper-left of the gem face, clear of
    # the bright facets so they aren't swallowed by the gem's own luminance.
    g1x, g1y = gx - sc.m(14), gy - sc.m(10)   # dominant, ~(250, 26)
    g2x, g2y = gx - sc.m(6),  gy - sc.m(12)   # small accent, ~(266, 22)

    # --- Solid diamond bodies at normal blend ---
    # Normal blend sets pixels to MINTGOLD_BODY directly; no channel can exceed
    # MINTGOLD_HOT — the solid polygon silhouette stays intact at all zoom levels.
    draw_glint_solid(p, g1x, g1y, sc.m(8), sc.m(2.5), 35, MINTGOLD_BODY, MINTGOLD_HOT)
    draw_glint_solid(p, g2x, g2y, sc.m(4), sc.m(1.5), 55, MINTGOLD_BODY, MINTGOLD_HOT)

    # --- ADD bloom layer separately ---
    # Built on its own SRCALPHA surface so the ADD compositing never touches the
    # solid body pixels until the final blit, giving the glow a soft halo without
    # driving the polygon arms to pure white.
    bloom = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    sc.soft_glow(bloom, g1x, g1y, sc.m(5), MINTGOLD_BODY, bloom_peak_1, layers=5)
    sc.soft_glow(bloom, g2x, g2y, sc.m(3), MINTGOLD_BODY, bloom_peak_2, layers=4)
    p.blit(bloom, (0, 0), special_flags=pygame.BLEND_ADD)

    return p, gx, gy, g1x, g1y, g2x, g2y


def _max_pixel_ring(surf, cx, cy, r_inner, r_outer):
    """Max RGB in an annular region — excludes the hot-pinpoint centre so the
    ceiling check captures the glow field, not the intentional bright spot."""
    mx = [0, 0, 0]
    for dy in range(-r_outer, r_outer + 1):
        y = cy + dy
        if y < 0 or y >= surf.get_height():
            continue
        for dx in range(-r_outer, r_outer + 1):
            d2 = dx * dx + dy * dy
            if d2 < r_inner * r_inner or d2 > r_outer * r_outer:
                continue
            x = cx + dx
            if x < 0 or x >= surf.get_width():
                continue
            c = surf.get_at((x, y))
            mx[0] = max(mx[0], c[0])
            mx[1] = max(mx[1], c[1])
            mx[2] = max(mx[2], c[2])
    return tuple(mx)


# ---- Panel 1 — UNEQUIPPED ---------------------------------------------------
orig_bal = sd.balance
sd.balance = lambda: 99999
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, "skin_mummy", rect, equipped=False, secret=False)
sd.balance = orig_bal
sc._card_cache.clear()

# ---- Panel 2 — BASE EQUIPPED ------------------------------------------------
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, "skin_mummy", rect, equipped=True, secret=False)
sc._card_cache.clear()

# ---- Panel 3 — ACTIVATION-BURST (with pixel ceiling guard) ------------------
BLOOM_P1, BLOOM_P2 = 30, 20

p3, gx, gy, g1x, g1y, g2x, g2y = _build_p3(BLOOM_P1, BLOOM_P2)

# Check glow field (ring just outside the solid body) for ceiling compliance.
# Inner radius excludes the intentional 1-2px hot pinpoint; outer captures the
# feathered bloom before it fades into the card body.
HOT_R    = max(2, sc.m(2))    # exclude hot-pinpoint core
CHECK_R  = sc.m(8)            # check out to bloom falloff edge

mp1 = _max_pixel_ring(p3, g1x, g1y, HOT_R, CHECK_R)
mp2 = _max_pixel_ring(p3, g2x, g2y, HOT_R, CHECK_R)
max_pixel = (max(mp1[0], mp2[0]), max(mp1[1], mp2[1]), max(mp1[2], mp2[2]))
print(f"burst glow-field max pixel: {max_pixel}  ceiling: {CLIP_CEIL}")

if (max_pixel[0] > CLIP_CEIL[0] or
        max_pixel[1] > CLIP_CEIL[1] or
        max_pixel[2] > CLIP_CEIL[2]):
    BLOOM_P1 = max(4, int(BLOOM_P1 * 0.55))
    BLOOM_P2 = max(4, int(BLOOM_P2 * 0.55))
    print(f"  → reducing bloom peaks to ({BLOOM_P1}, {BLOOM_P2}) and rebuilding")
    p3, gx, gy, g1x, g1y, g2x, g2y = _build_p3(BLOOM_P1, BLOOM_P2)
    mp1 = _max_pixel_ring(p3, g1x, g1y, HOT_R, CHECK_R)
    mp2 = _max_pixel_ring(p3, g2x, g2y, HOT_R, CHECK_R)
    max_pixel = (max(mp1[0], mp2[0]), max(mp1[1], mp2[1]), max(mp1[2], mp2[2]))
    print(f"  → after reduction: glow-field max pixel: {max_pixel}")

# ---- Compose the review sheet -----------------------------------------------
BG = (8, 8, 20)
PAD     = 20
GAP     = 16
HDR_H   = 48
LBL_H   = 34
SEP_H   = 28   # "1× GAME SCALE" separator row
STRIP_PAD = 14 # gap between 2x panels and 1x strip label

# CARD_W/CARD_H at 1×
CW1, CH1 = sc.CARD_W, sc.CARD_H   # 162, 100

panels = [
    ("UNEQUIPPED",       (170, 170, 185), p1),
    ("BASE EQUIPPED",    (170, 170, 185), p2),
    ("ACTIVATION-BURST", (168, 235, 175), p3),
]

sheet_w = PAD + 3 * PANEL_W + 2 * GAP + PAD
sheet_h = (PAD + HDR_H + LBL_H + PANEL_H
           + STRIP_PAD + SEP_H + CH1 + PAD)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_font = hud_font(26)
label_font = hud_font(18)
strip_font = hud_font(15)

# Title
title = title_font.render(
    "equipped card — activation-burst · skin_mummy  (round 2)",
    True, (232, 206, 128))
sheet.blit(title, (PAD, PAD + (HDR_H - title.get_height()) // 2))

# 2× panels row
for i, (label, col, panel) in enumerate(panels):
    px = PAD + i * (PANEL_W + GAP)
    ly = PAD + HDR_H
    lbl = label_font.render(label, True, col)
    sheet.blit(lbl, (px + (PANEL_W - lbl.get_width()) // 2,
                     ly + (LBL_H - lbl.get_height()) // 2))
    sheet.blit(panel, (px, ly + LBL_H))

# 1× strip separator
sep_y = PAD + HDR_H + LBL_H + PANEL_H + STRIP_PAD
sep_lbl = strip_font.render("— 1×  GAME SCALE —", True, (140, 140, 160))
sheet.blit(sep_lbl, ((sheet_w - sep_lbl.get_width()) // 2,
                     sep_y + (SEP_H - sep_lbl.get_height()) // 2))

# 1× panels — smoothscale each 324×200 panel down to 162×100
strip_y = sep_y + SEP_H
for i, (_, _, panel) in enumerate(panels):
    px = PAD + i * (PANEL_W + GAP)
    # Centre the 1× card in the same column as the 2× panel
    card_1x = pygame.transform.smoothscale(panel, (CW1, CH1))
    cx1 = px + (PANEL_W - CW1) // 2
    sheet.blit(card_1x, (cx1, strip_y))

out = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped", "activation_burst", "round_2.png"))
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved: {out}  size: {sheet.get_size()}")
