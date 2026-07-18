#!/usr/bin/env python3
import os, sys
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
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS  # 324×200
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2*ri, PANEL_H - 2*ri)

# Saturated amber-gold: R >> G >> B so the rim reads "gold heat" not fog.
# At SS=2 with the chosen alpha the inner stroke lifts R by the most,
# G in the middle, B barely — matching the target R>G>B gradient profile.
GLOW_COL = (255, 200, 72)

# Brighter emerald body boosts value contrast so the pip reads LED-lit
# regardless of hue perception — colorblind viewers key on value + shape.
PIP_COL = (110, 240, 148)

# Mint-white (no blue spike): pulled inside the gem face, drawn opaque so
# BLEND_ADD's white-blow-out alias risk is gone entirely.
PIP_SPEC = (230, 255, 240)


def draw_active_frame_illumination(surf):
    rad = sc.m(sc.CARD_RAD)

    # Warm rim: tight 3-4px live band from the inner keyline (inset=13) only.
    # Fewer steps + steep power (3.0) kills the long tail that made the aura
    # read as grey haze — the max stroke lands crisp at the gold bead, then
    # falls to zero before it's half-way across the card body.
    aura = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    steps = sc.m(4)              # ≈ 4 device-px = 2px live — tight cap
    start_inset = sc.m(13)      # locks bloom origin to the inner keyline
    for i in range(steps):
        inset = start_inset + i
        a = int(58 * (1 - i / steps) ** 3.0)   # steep cube falloff
        if a <= 0:
            continue
        r = rect.inflate(-2 * inset, -2 * inset)
        pygame.draw.rect(aura, (*GLOW_COL, a), r,
                         width=max(1, sc.m(1.2)),
                         border_radius=max(1, rad - inset))
    surf.blit(aura, (0, 0))

    # Emerald pip: grown one notch (r=m(5) ≈ 11px live).
    # Seat ring is r + m(2) so the dark bezel is ≥2px live after downscale —
    # that thin ring is the "bezel" that makes the pip read like a pressed LED
    # on the gold bead rather than a painted dot.
    cx, cy = 162, 18
    r = sc.m(5)
    seat_r = r + sc.m(2)                # ≥2px live bezel after SS=2 downscale
    pygame.draw.circle(surf, (10, 26, 14, 220), (cx, cy + 1), seat_r)
    pygame.draw.circle(surf, PIP_COL, (cx, cy), r)
    # Sphere-depth shadow stroke (lower-right arc, no fill)
    pygame.draw.circle(surf, (44, 155, 90), (cx + 1, cy + 1), r,
                       max(1, sc.m(0.8)))
    # 1px live mint-white spec drawn opaque INSIDE the gem face.
    # Position is upper-left of centre so it reads as reflected highlight.
    # Not BLEND_ADD — avoids white alias blow-out on any background.
    spec_r = max(1, sc.m(1))
    spec_off = max(1, int(r * 0.30))
    pygame.draw.circle(surf, PIP_SPEC,
                       (cx - spec_off, cy - spec_off), spec_r)


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (gold frame only, no pip/bloom)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + frame illumination)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_active_frame_illumination(p2)

# ── Review sheet ──────────────────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
GOLD = (236, 202, 116); GREY = (150, 152, 168); CREAM_LBL = (250, 246, 232)

xs = [20, 360, 700]
panel_y = PAD + HDR_H + LBL_H
sheet_w = xs[-1] + PANEL_W + PAD          # 1044

# Zoom strip row (2× nearest of the concept only)
strip_w, strip_h = sc.CARD_W * 2, sc.CARD_H * 2
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y  = zlbl_y + SLBL_H

# Money-shot row: two cards at true 162×100 to judge the delta at scan scale
MSHOT_GAP = 6
money_lbl_y = zoom_y + strip_h + SGAP
money_y     = money_lbl_y + SLBL_H
sheet_h = money_y + sc.CARD_H + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v4 — active-frame-illumination · round 2 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY), ("+ FRAME ILLUMINATION", CREAM_LBL)]
panels = [p0, p1, p2]
lbl_f  = hud_font(15, True)
zlbl_f = hud_font(13, True)

for x, panel, (label, col) in zip(xs, panels, labels):
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(x + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (x, panel_y))

# Zoom strip — concept at 2× to inspect pip + bloom edge detail
card1x = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
strip  = pygame.transform.scale2x(card1x)
zx = xs[-1] + (PANEL_W - strip_w) // 2   # centre under the concept panel
zt = zlbl_f.render("@2× zoom  (concept — nearest neighbour)", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(xs[-1] + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
sheet.blit(strip, (zx, zoom_y))

# Money-shot — TRUE 162×100 equipped base | concept side-by-side so the delta
# can be read at scan scale, exactly as it would look in the live store grid.
p1_1x = pygame.transform.smoothscale(p1, (sc.CARD_W, sc.CARD_H))
p2_1x = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
pair_w = sc.CARD_W * 2 + MSHOT_GAP
money_x = (sheet_w - pair_w) // 2

mt = zlbl_f.render(
    "MONEY-SHOT  ·  162×100 true scale  ·  EQUIPPED BASE  |  CONCEPT",
    True, CREAM_LBL)
sheet.blit(mt, mt.get_rect(midbottom=(sheet_w // 2, money_lbl_y + SLBL_H - 4)))
sheet.blit(p1_1x, (money_x, money_y))
sheet.blit(p2_1x, (money_x + sc.CARD_W + MSHOT_GAP, money_y))

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
    "docs", "store_equipped_v4", "active_frame_illumination", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
