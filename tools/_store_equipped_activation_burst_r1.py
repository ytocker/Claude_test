"""Headless review render for the `activation-burst` equipped-card concept.

A frozen "just-equipped" sparkle: 2-3 crisp oriented diamond glints plus a tiny
base glow near the tier gem, in a warm mint-gold palette kept clearly distinct
from the rarity glow (blues/purples) and the gasket emerald. The card body, rim,
dome, ribbon and chip stay exactly as `draw_card` renders them — the burst is an
additive overlay so the equip moment reads as "activated / sparkling with newness"
captured statically. Output is a 3-panel comparison sheet, docs-only, never bundled.
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

PANEL_W, PANEL_H = sc.PANEL_W if hasattr(sc, "PANEL_W") else 324, 200
PANEL_W = 324
rect = pygame.Rect(8, 8, 308, 184)

# Warm mint-gold: yellowy-greens, deliberately off the pure emerald so the burst
# never blurs into the gasket or the cool rarity halo.
MINTGOLD_CORE = (222, 246, 196)
MINTGOLD_MID = (168, 224, 150)
HOT = (245, 255, 235)


def draw_glint(surf, cx, cy, long_r, short_r, angle_deg, color, hot=HOT):
    """Four-point star glint = two crossed diamonds + a hotter inner core.

    Oriented so each glint catches light from a slightly different angle, which
    keeps the trio from looking like one stamped symbol repeated.
    """
    a = math.radians(angle_deg)
    pa = a + math.pi / 2
    pts_long = [
        (cx + math.cos(a) * long_r, cy + math.sin(a) * long_r),
        (cx + math.cos(pa) * short_r, cy + math.sin(pa) * short_r),
        (cx - math.cos(a) * long_r, cy - math.sin(a) * long_r),
        (cx - math.cos(pa) * short_r, cy - math.sin(pa) * short_r),
    ]
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts_long])
    pts_short = [
        (cx + math.cos(pa) * short_r * 2, cy + math.sin(pa) * short_r * 2),
        (cx + math.cos(a) * short_r, cy + math.sin(a) * short_r),
        (cx - math.cos(pa) * short_r * 2, cy - math.sin(pa) * short_r * 2),
        (cx - math.cos(a) * short_r, cy - math.sin(a) * short_r),
    ]
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts_short])
    scale = 0.5
    pts_hot = [
        (cx + math.cos(a) * long_r * scale, cy + math.sin(a) * long_r * scale),
        (cx + math.cos(pa) * short_r * scale, cy + math.sin(pa) * short_r * scale),
        (cx - math.cos(a) * long_r * scale, cy - math.sin(a) * long_r * scale),
        (cx - math.cos(pa) * short_r * scale, cy - math.sin(pa) * short_r * scale),
    ]
    pygame.draw.polygon(surf, hot, [(int(x), int(y)) for x, y in pts_hot])


# ---- Panel 1 — UNEQUIPPED ---------------------------------------------------
# Stub balance so the unequipped chip renders its normal affordable state.
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

# ---- Panel 3 — ACTIVATION-BURST CONCEPT -------------------------------------
p3 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p3, "skin_mummy", rect, equipped=True, secret=False)
sc._card_cache.clear()

# Additive so the burst only ADDS light over the finished card — body, rim, dome,
# ribbon and chip pixels are never overwritten, only lit.
layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
gx, gy = rect.right - sc.m(19), rect.y + sc.m(19)  # tier-gem center (278, 46)

# Glint 1 — LONG diamond upper-left of the gem, seated on a small base glow.
sc.soft_glow(layer, gx - sc.m(9), gy - sc.m(7), sc.m(6), MINTGOLD_MID, 40, layers=6)
draw_glint(layer, gx - sc.m(9), gy - sc.m(7),
           long_r=sc.m(8), short_r=sc.m(1.5), angle_deg=35,
           color=MINTGOLD_MID)

# Glint 2 — SHORT diamond lower-right of the gem.
draw_glint(layer, gx + sc.m(8), gy + sc.m(6),
           long_r=sc.m(4), short_r=sc.m(1), angle_deg=15,
           color=MINTGOLD_CORE)

# Glint 3 — tiny accent just above the gem.
draw_glint(layer, gx, gy - sc.m(8),
           long_r=sc.m(2.5), short_r=sc.m(0.8), angle_deg=55,
           color=MINTGOLD_CORE)

p3.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

# ---- Compose the review sheet -----------------------------------------------
BG = (8, 8, 20)
PAD, GAP, HDR_H, LBL_H = 20, 16, 48, 34
panels = [
    ("UNEQUIPPED", (170, 170, 185), p1),
    ("BASE EQUIPPED", (170, 170, 185), p2),
    ("ACTIVATION-BURST", (168, 224, 150), p3),
]
sheet_w = PAD + 3 * PANEL_W + 2 * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_font = hud_font(26)
label_font = hud_font(18)

title = title_font.render("equipped card — activation-burst · skin_mummy",
                          True, (232, 206, 128))
sheet.blit(title, (PAD, PAD + (HDR_H - title.get_height()) // 2))

for i, (label, col, panel) in enumerate(panels):
    px = PAD + i * (PANEL_W + GAP)
    ly = PAD + HDR_H
    lbl = label_font.render(label, True, col)
    sheet.blit(lbl, (px + (PANEL_W - lbl.get_width()) // 2,
                     ly + (LBL_H - lbl.get_height()) // 2))
    sheet.blit(panel, (px, ly + LBL_H))

out = os.path.join(os.path.dirname(__file__), "..", "docs",
                   "store_equipped", "activation_burst", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved:", out, sheet.get_size())
