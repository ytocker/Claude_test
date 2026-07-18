#!/usr/bin/env python3
"""
Positional comparison for the cream cartouche equipped indicator (concept 3).
Two variants of the same cartouche, each overlaying everything:
  - TOP:    cartouche centred on the outer TOP bead  (cy≈13), hangs into the card body
  - BOTTOM: cartouche centred on the outer BOTTOM bead (cy≈187), hangs up from the bottom rail

The user said "overlay everything" — both are drawn AFTER draw_card(equipped=True),
sitting visibly on top of the regalia frame beads. No recess-under-frame ordering.
"""
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
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324×200
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)

OUTER_GOLD = (236, 202, 116)
CREAM_TOP  = (255, 240, 190)
CREAM_BOT  = (248, 238, 210)
VALLEY     = (9,   9,  22)
KEY        = (46,  38, 18)


def draw_cartouche(surf, cy, W=160, H=26, flip_relief=False):
    """Cream stadium cartouche at (cx=162, cy), overlaying all frame layers.

    flip_relief: True for the bottom variant — shadow lip on BOTTOM+RIGHT and
    catch-light on TOP+LEFT, so the light source still reads top-left even
    though the cartouche is anchored to the bottom rail.
    """
    m   = sc.m
    cx  = 162
    rad = H // 2
    r   = pygame.Rect(cx - W // 2, cy - H // 2, W, H)

    # ── drop shadow (always below the banner body) ────────────────────────────
    sh = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120), r.move(0, m(2)), border_radius=rad)
    surf.blit(sh, (0, 0))

    # ── dark valley ring — the "seat" that beds the cartouche into the frame ──
    wall = r.inflate(m(2), m(2))
    pygame.draw.rect(surf, VALLEY, wall, border_radius=rad + m(1))

    # ── cream fill — bright top, warmer base, real luminance range ────────────
    fill = sc.vgrad_stops(W, H, rad, [(0.0, CREAM_TOP), (1.0, CREAM_BOT)], 255)
    surf.blit(fill, r.topleft)

    # ── relief lips — shadow + catch-light define the emboss depth ────────────
    # Shadow lip (top-left when normal; bottom-right when flipped)
    lip = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(lip, VALLEY, lip.get_rect(), width=2, border_radius=rad)
    mask = pygame.Surface((W, H), pygame.SRCALPHA)
    if not flip_relief:
        pygame.draw.polygon(mask, (255,255,255,255), [(0,0),(W,0),(0,H)])   # top-left
    else:
        pygame.draw.polygon(mask, (255,255,255,255), [(W,0),(W,H),(0,H)])   # bot-right
    lip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(lip, r.topleft)

    # Catch-light (bottom-right when normal; top-left when flipped)
    glint = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(glint, (255, 248, 224), glint.get_rect(), width=2, border_radius=rad)
    gmask = pygame.Surface((W, H), pygame.SRCALPHA)
    if not flip_relief:
        pygame.draw.polygon(gmask, (255,255,255,255), [(W,0),(W,H),(0,H)])  # bot-right
    else:
        pygame.draw.polygon(gmask, (255,255,255,255), [(0,0),(W,0),(0,H)])  # top-left
    glint.blit(gmask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(glint, r.topleft)

    # ── gold outer keyline — ties the cartouche to the regalia gold family ────
    pygame.draw.rect(surf, OUTER_GOLD, r, width=max(1, sc.m(1)),
                     border_radius=rad)

    # ── "EQUIPPED" label ───────────────────────────────────────────────────────
    sc.plain_text(surf, "EQUIPPED", sc.font(11), (cx, cy), KEY,
                  shadow_a=0, tracking=sc.m(0.8), weight=sc.m(0.8))


# ── Panel 0 — EQUIPPED BASE ──────────────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=True, secret=False, owned=False)

# ── Panel 1 — TOP cartouche: centred on the outer top bead (cy≈13) ───────────
# Overlays the top frame area — bead y≈10-16, cartouche hangs into the body.
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)
draw_cartouche(p1, cy=13, W=160, H=26, flip_relief=False)

# ── Panel 2 — BOTTOM cartouche: centred on the outer bottom bead (cy≈187) ───
# Overlays the bottom frame area — bead y≈184-192, cartouche hangs up from it.
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_cartouche(p2, cy=187, W=160, H=26, flip_relief=True)


# ── compose review sheet ──────────────────────────────────────────────────────
BG        = (8, 8, 20)
GOLD_LBL  = (236, 202, 116)
GREY_LBL  = (130, 132, 148)
CREAM_LBL = (246, 242, 224)

PAD    = 20
HDR_H  = 48
LBL_H  = 34
SGAP   = 16
SLBL_H = 22

xs = [20, 360, 700]
panel_y = PAD + HDR_H + LBL_H   # 102

strip_w = sc.CARD_W * 2   # 324
strip_h = sc.CARD_H * 2   # 200

sheet_w = xs[-1] + PANEL_W + PAD
zlbl_y  = panel_y + PANEL_H + SGAP
zoom_y  = zlbl_y + SLBL_H
sheet_h = zoom_y + strip_h + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render(
    "equipped v4c — cream cartouche · position options · skin_mummy", True, GOLD_LBL)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

lbl_f  = hud_font(15, True)
zlbl_f = hud_font(13, True)

panels = [
    (p0, "EQUIPPED BASE",          GREY_LBL),
    (p1, "TOP — overlays top bead",    CREAM_LBL),
    (p2, "BOTTOM — overlays bot bead", CREAM_LBL),
]
for (panel, label, col), x in zip(panels, xs):
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(x + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (x, panel_y))

# Zoom strips for p1 and p2 side by side (each 1× → scale2x)
for pi, (panel, zoom_label) in enumerate([(p1, "@1× TOP"), (p2, "@1× BOTTOM")]):
    z1 = pygame.transform.smoothscale(panel, (sc.CARD_W, sc.CARD_H))
    strip = pygame.transform.scale2x(z1)
    zx = xs[1 + pi] + (PANEL_W - strip_w) // 2
    zt = zlbl_f.render(zoom_label, True, GREY_LBL)
    sheet.blit(zt, zt.get_rect(midbottom=(xs[1 + pi] + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
    sheet.blit(strip, (zx, zoom_y))

OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "docs", "store_equipped_v4c", "cartouche_positions.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
