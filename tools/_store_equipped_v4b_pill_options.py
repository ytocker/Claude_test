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
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)

CREAM      = (255, 240, 190)   # inner bead colour
OUTER_GOLD = (236, 202, 116)   # outer bead colour
INNER_GOLD = (248, 238, 210)   # inner glow gold
KEY        = (46, 38, 18)      # dark ink
VALLEY     = (9, 9, 22)        # dark valley
GLINT      = (255, 248, 224)   # top rim highlight


def _label(surf, cx, cy):
    sc.plain_text(surf, "EQUIPPED", sc.font(9), (cx, cy), KEY,
                  shadow_a=0, tracking=sc.m(0.5), weight=sc.m(0.8),
                  keyline=None)


def draw_A(surf):
    """TOP · CREAM — the cream pill reads as the inner bead material simply
    widened, so no dark gap ever appears; no masking is needed at all."""
    cx, cy = 162, 21
    W, H = 116, 26
    rad = H // 2
    x0, y0 = cx - W // 2, cy - H // 2
    pill = pygame.Rect(x0, y0, W, H)
    pygame.draw.rect(surf, CREAM, pill, border_radius=rad)
    pygame.draw.rect(surf, VALLEY, pill, width=max(1, sc.m(1.0)),
                     border_radius=rad)
    pygame.draw.line(surf, GLINT, (x0 + rad, y0), (x0 + W - rad, y0), 1)
    _label(surf, cx, cy)


def draw_B(surf):
    """TOP · GOLD — the outer-bead gold fills the masked span, so the whole
    clasp reads as one gold material widened into the frame."""
    cx, cy = 162, 21
    W, H = 116, 26
    rad = H // 2
    x0, y0 = cx - W // 2, cy - H // 2
    pill = pygame.Rect(x0, y0, W, H)
    # Overwrite the dark-body bead stubs with outer gold before the gradient.
    pygame.draw.rect(surf, OUTER_GOLD, pygame.Rect(x0, y0, W, H))
    body = sc.vgrad_stops(W, H, rad,
                          [(0.0, INNER_GOLD), (1.0, OUTER_GOLD)],
                          255, gamma=1.04)
    surf.blit(body, pill.topleft)
    pygame.draw.rect(surf, VALLEY, pill, width=max(1, sc.m(1.0)),
                     border_radius=rad)
    pygame.draw.line(surf, GLINT, (x0 + rad, y0), (x0 + W - rad, y0), 1)
    pygame.draw.rect(surf, (4, 4, 14), pygame.Rect(x0, y0 + H, W, 2))
    _label(surf, cx, cy)


def draw_C(surf):
    """BOTTOM · CREAM — cream pill seated over the bottom frame bead area,
    with a soft drop shadow so it lifts off the tray."""
    cx, cy = 162, 181
    W, H = 116, 22
    rad = H // 2
    x0, y0 = cx - W // 2, cy - H // 2  # 104, 170
    # Soft contact shadow under the pill before it is drawn.
    sh = pygame.Surface((W + 4, H + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 70), sh.get_rect(), border_radius=rad)
    surf.blit(sh, (x0 - 2, y0 - 1 + 3))
    pill = pygame.Rect(x0, y0, W, H)
    pygame.draw.rect(surf, CREAM, pill, border_radius=rad)
    pygame.draw.rect(surf, VALLEY, pill, width=max(1, sc.m(1.0)),
                     border_radius=rad)
    pygame.draw.line(surf, GLINT, (x0 + rad, y0), (x0 + W - rad, y0), 1)
    _label(surf, cx, cy)


def draw_D(surf):
    """BOTTOM · GOLD — a wider, thinner gold nameplate banner spanning more of
    the bottom frame."""
    cx, cy = 162, 181
    W, H = 160, 20
    rad = H // 2
    x0, y0 = cx - W // 2, cy - H // 2  # 82, 171
    pill = pygame.Rect(x0, y0, W, H)
    body = sc.vgrad_stops(W, H, rad,
                          [(0.0, INNER_GOLD), (1.0, OUTER_GOLD)],
                          255, gamma=1.04)
    surf.blit(body, pill.topleft)
    pygame.draw.rect(surf, VALLEY, pill, width=max(1, sc.m(1.0)),
                     border_radius=rad)
    pygame.draw.line(surf, GLINT, (x0 + rad, y0), (x0 + W - rad, y0), 1)
    _label(surf, cx, cy)


OPTIONS = [
    ("A", draw_A, "TOP · CREAM"),
    ("B", draw_B, "TOP · GOLD"),
    ("C", draw_C, "BOTTOM · CREAM"),
    ("D", draw_D, "BOTTOM · GOLD"),
]


def build_panel(draw_fn):
    sc._card_cache.clear()
    p = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    sc.draw_card(p, SID, rect, equipped=True, secret=False, owned=False)
    draw_fn(p)
    return p


BG = (8, 8, 20)
GOLD = (236, 202, 116)
LABEL_CREAM = (246, 242, 224)
PAD = 20
GAP = 12
HDR_H = 48
LBL_H = 36

sheet_w = PAD * 2 + len(OPTIONS) * PANEL_W + (len(OPTIONS) - 1) * GAP
panel_y = PAD + HDR_H
sheet_h = panel_y + PANEL_H + LBL_H + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped pill options — natural frame integration",
                    True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

lbl_f = hud_font(14, True)
for i, (key, draw_fn, label) in enumerate(OPTIONS):
    x = PAD + i * (PANEL_W + GAP)
    panel = build_panel(draw_fn)
    sheet.blit(panel, (x, panel_y))
    lt = lbl_f.render(f"{key} — {label}", True, LABEL_CREAM)
    sheet.blit(lt, lt.get_rect(midtop=(x + PANEL_W // 2,
                                       panel_y + PANEL_H + 8)))

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
    "docs", "store_equipped_v4b", "pill_options.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
