#!/usr/bin/env python3
"""
equipped-card v3 — inset-plinth concept, round 1.

The equipped card grows a solid full-width bright-gold pedestal band across the
very base of its body, so the portrait reads as mounted "on display" — a museum
display mount. The plinth is a wide architectural ledge: a sunlit horizontal
TREAD (top-lit gold) meeting a shadowed vertical RISER (darker gold ramp), with
a crisp step-shadow seam between them. Because it is a solid full-width gold base
it stays crystal-clear at the true 162×100 thumbnail — the strongest possible
"seated/equipped" cue.

Drawn LAST over an equipped card whose green chip is suppressed, so the plinth is
the sole state signal on the concept panel. The plinth's lower corners are masked
to the card's rounded-rect so the ledge follows the body's corner radius cleanly.
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
rad = sc.m(sc.CARD_RAD)                                   # body corner radius (34)


# ── Panel 0 — UNEQUIPPED (price tag visible) ─────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)


# ── Panel 1 — STOCK EQUIPPED (green chip, reference) ─────────────────────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False)


# ── Panel 2 — CONCEPT EQUIPPED (chip suppressed, inset plinth) ───────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None          # suppress the green EQUIPPED chip
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()


def _vband(surf, x0, x1, y0, y1, top, bot):
    """A vertical gradient band filled row by row — the tread/riser faces. Kept
    local (no rounded corners) because the whole plinth is masked to the card
    body afterward, so the band can be authored as a plain rectangle."""
    h = max(1, y1 - y0)
    for y in range(y0, y1):
        t = (y - y0) / h
        c = sc.lerp_color(top, bot, t)
        pygame.draw.line(surf, c, (x0, y), (x1 - 1, y))


def _card_mask():
    """A white rounded-rect matching the card body — used with BLEND_RGBA_MIN to
    clip the plinth so its lower corners follow the body's corner radius."""
    mask = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), rect, border_radius=rad)
    return mask


def draw_inset_plinth(surf):
    """The full-width gold display plinth. Built on its own layer so the whole
    band can be corner-masked to the card body in one pass, then composited: an
    AO shadow where the body rests on the ledge, a sunlit tread, a step-shadow
    seam, a shadowed riser, and lit/keyline edges top and bottom."""
    LX0, LX1 = 14, 310                     # near-full width, inside the bevel

    plinth = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)

    # (1) Contact AO above the ledge — the card body casts a soft shadow as it
    # "rests" on the plinth, seating the two together.
    ao = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    for i, y in enumerate(range(166, 170)):
        a = int(80 * (1 - i / 4))
        pygame.draw.line(ao, (0, 0, 4, a), (LX0, y), (LX1 - 1, y))
    plinth.blit(ao, (0, 0))

    # (2) Top TREAD — the sunlit horizontal nosing surface.
    _vband(plinth, LX0, LX1, 168, 176, (252, 224, 150), (236, 200, 110))

    # (3) Step-shadow seam — front edge of the tread meeting the riser.
    pygame.draw.line(plinth, (120, 74, 20), (LX0, 176), (LX1 - 1, 176), 2)

    # (4) RISER — the shadowed vertical front face of the plinth.
    _vband(plinth, LX0, LX1, 177, 188, (196, 150, 68), (150, 100, 34))

    # (5) Top nosing cap — the very top lit edge of the tread.
    pygame.draw.line(plinth, (255, 242, 200), (LX0, 168), (LX1 - 1, 168), 1)

    # (6) Contact keyline — the seam where the plinth meets the indigo body.
    pygame.draw.line(plinth, (58, 36, 8), (LX0, 167), (LX1 - 1, 167), 1)

    # (7) Mask lower corners to the card body so the ledge follows its radius.
    plinth.blit(_card_mask(), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(plinth, (0, 0))

    # (8) Warm glow rising off the tread — masked to the body so it never spills
    # past the card edge.
    glow = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    g = pygame.Surface((110, 110), pygame.SRCALPHA)
    pygame.draw.circle(g, (246, 206, 120, 40), (55, 55), 50)
    glow.blit(g, (162 - 55, 168 - 55))
    glow.blit(_card_mask(), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(glow, (0, 0))


draw_inset_plinth(p2)


# ── Compose the review sheet ─────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
ONE_W, ONE_H = sc.CARD_W, sc.CARD_H          # 162×100 — true 1× card size
ZOOM_W, ZOOM_H = ONE_W * 2, ONE_H * 2        # nearest-neighbour blow-up of 1×

GOLD = (236, 202, 116)
GREY = (150, 152, 168)
CREAM_LBL = (250, 246, 232)

N = 3
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + SGAP + SLBL_H + ZOOM_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v3 — inset-plinth · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("STOCK EQUIPPED", GREY),
          ("INSET PLINTH", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)
panel_y = PAD + HDR_H + LBL_H          # = 102
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

    # 1× read: downscale to the true card size, then blow it back up nearest-
    # neighbour so the sheet shows exactly how the plinth resolves at 1×.
    card1x = pygame.transform.smoothscale(panel, (ONE_W, ONE_H))
    zoom = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
    zt = zlbl_f.render("@1× (rendered then 2× nearest)", True, GREY)
    sheet.blit(zt, zt.get_rect(midbottom=(px + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
    sheet.blit(zoom, (px + (PANEL_W - ZOOM_W) // 2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3", "inset_plinth", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
