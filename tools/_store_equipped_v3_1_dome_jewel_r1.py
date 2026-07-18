#!/usr/bin/env python3
"""
equipped-card v3.1 — dome-jewel symbol, round 1.

Builds on the approved regalia double-frame (v3 round 2): keeps that frame
verbatim, then seats a small LIT activation jewel at the crown of the hero
cabochon's dome arc. The jewel is a dark indigo socket ringed in deep gold with
a single bright cream specular pip — a dark socket that has been "switched on".
Tying the equipped signal to the hero cabochon itself (rather than a frame bead
or a corner badge) makes "powered on / in use" read as a property of the gem,
not a decoration bolted onto the border.

Drawn LAST over an equipped card whose green chip is suppressed, so frame + jewel
are the sole state signals on the concept panel.
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
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)   # card body
rad = sc.m(sc.CARD_RAD)                                   # body corner radius


def draw_regalia_frame(surf, body):
    """The approved v3-r2 nested second gold frame, decoupled from bevel_rim.

    Each bead is a CONSTANT-value stroke so the ring stays equally hot on all
    four edges — the double frame reads as an even jewelled ring at 162×100."""
    OUTER = (236, 202, 116)     # warm-gold outer bead (the bevel-echo line)
    VALLEY = (9, 9, 22)         # flat near-body dark — clean, no indigo bleed
    INNER = (255, 240, 190)     # HOT constant inner track — hotter than the bevel
    KEY = (46, 38, 18)          # deep inner keyline: a defined inner boundary
    GLINT = (255, 248, 224)     # jewel highlight on the two top-lit corners

    def bead(inset, w, col, alpha=255):
        r = body.inflate(-2 * inset, -2 * inset)
        s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(s, (*col, alpha), r, width=w,
                         border_radius=max(1, rad - inset))
        surf.blit(s, (0, 0))

    bead(inset=2,  w=sc.m(3.0), col=OUTER)           # outer bead
    bead(inset=8,  w=sc.m(1.4), col=VALLEY)          # flat dark valley
    bead(inset=10, w=sc.m(2.0), col=INNER)           # HOT inner track (hero line)
    bead(inset=13, w=max(1, sc.m(0.6)), col=KEY)     # fine inner keyline

    track = body.inflate(-2 * 10, -2 * 10)
    leg = sc.m(7)
    corners = [
        (track.left,  track.top,     1,  1),   # TL (top-lit)
        (track.right, track.top,    -1,  1),   # TR (top-lit)
        (track.left,  track.bottom,  1, -1),   # BL
        (track.right, track.bottom, -1, -1),   # BR
    ]
    for cxp, cyp, sx, sy in corners:
        pygame.draw.polygon(surf, INNER, [
            (cxp, cyp),
            (cxp + sx * leg, cyp),
            (cxp, cyp + sy * leg),
        ])
    for cxp, cyp, sx, sy in corners[:2]:
        pygame.draw.line(surf, GLINT, (cxp, cyp), (cxp + sx * leg, cyp),
                         max(1, sc.m(0.8)))


def draw_dome_jewel(surf):
    """The lit activation jewel at the crown of the dome arc (SS=2 device px).

    Dome center is (162, 86) r=62, so the arc crown sits at y = 86 - 62 = 24.
    Back-to-front: a blurred indigo halo grounds the jewel against the bevel; a
    deep-gold rim is the setting; a deep-indigo interior is the dark socket; a
    single cream pip (offset upper-left) is the gleam that reads 'lit / on' —
    the dark socket + bright pip is what separates equipped from unequipped."""
    jx, jy = 162, 24
    px, py = 160, 22            # specular pip — upper-left of jewel centre

    # 1. Soft indigo halo — drawn on a local surface and box-blurred by scaling
    #    down then up, so it grounds the jewel without a hard edge.
    HALO_BOX = 34
    halo = pygame.Surface((HALO_BOX, HALO_BOX), pygame.SRCALPHA)
    pygame.draw.circle(halo, (12, 10, 30, 165), (HALO_BOX // 2, HALO_BOX // 2), 11)
    halo = pygame.transform.smoothscale(halo, (9, 9))
    halo = pygame.transform.smoothscale(halo, (HALO_BOX, HALO_BOX))
    surf.blit(halo, (jx - HALO_BOX // 2, jy - HALO_BOX // 2))

    # 2. Deep-gold rim ring — the setting the cabochon is bezel-set into.
    pygame.draw.circle(surf, (196, 158, 74), (jx, jy), 8, 2)

    # 3. Deep-indigo interior — the dark socket face.
    pygame.draw.circle(surf, (44, 40, 96), (jx, jy), 6)

    # 4. Cream specular pip — the "activated" gleam. KEY equipped tell.
    pygame.draw.circle(surf, (255, 248, 224), (px, py), 2)

    # 5. Fine radial shimmer — three short cream rays off the pip add sparkle at
    #    2× without crowding the socket at the true 162×100 tile size.
    for dx, dy in ((-3, -3), (3, -2), (-2, 3)):
        pygame.draw.line(surf, (255, 248, 224), (px, py), (px + dx, py + dy), 1)


# ── Panel 0 — UNEQUIPPED (price tag visible) ─────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)


# ── Panel 1 — REGALIA FRAME ONLY (chip suppressed, no jewel) ─────────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False)
sc._card_cache.clear()
draw_regalia_frame(p1, rect)


# ── Panel 2 — CONCEPT (regalia frame + lit dome jewel) ───────────────────────
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()
draw_regalia_frame(p2, rect)
draw_dome_jewel(p2)


# ── Compose the review sheet ─────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24

GOLD = (236, 202, 116)
GREY = (150, 152, 168)
CREAM_LBL = (250, 246, 232)

N = 3
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD          # 1044
strip = pygame.transform.scale2x(
    pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H)))   # 162×100 → 324×200
strip_w, strip_h = strip.get_size()

panel_y = PAD + HDR_H + LBL_H                              # 102
slbl_y = panel_y + PANEL_H + SGAP
strip_y = slbl_y + SLBL_H
sheet_h = strip_y + strip_h + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v3.1 — dome-jewel · round 1 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("REGALIA FRAME", GREY),
          ("DOME-JEWEL (lit)", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

# 1× read of the concept: TRUE 162×100 tile, blown back up nearest-neighbour so
# the sheet shows exactly how the lit jewel resolves at real card size.
px2 = PAD + 2 * (PANEL_W + GAP)
zt = zlbl_f.render("CONCEPT @1× (162×100 tile, 2× nearest)", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(px2 + PANEL_W // 2, slbl_y + SLBL_H - 4)))
sheet.blit(strip, (px2 + (PANEL_W - strip_w) // 2, strip_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3_1", "dome_jewel", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
