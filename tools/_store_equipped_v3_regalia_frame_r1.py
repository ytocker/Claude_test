#!/usr/bin/env python3
"""
equipped-card v3 — regalia-frame concept, round 1.

The equipped card gains a SECOND full-perimeter gold frame nested just inside its
existing bevel rim, held off from it by a dark inset gutter — so an equipped card
reads as TWO concentric gold frames with a dark channel between them. Double frame
= selected/active is universal UI shorthand; here it's rendered as a jeweller's
inner track (hotter than the outer bevel so it out-reads it) with corner masses so
it still resolves as "framed" when the 324×200 art lands at the true 162×100 size.

Drawn LAST over an equipped card whose green chip is suppressed, so the frame is
the sole state signal on the concept panel.
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
rad = sc.m(sc.CARD_RAD)                                   # body corner radius


# ── Panel 0 — UNEQUIPPED (price tag visible) ─────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)


# ── Panel 1 — STOCK EQUIPPED (green chip, reference) ─────────────────────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False)


# ── Panel 2 — CONCEPT EQUIPPED (chip suppressed, regalia double-frame) ───────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None          # suppress the green EQUIPPED chip
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()


def draw_regalia_frame(surf):
    """The nested second gold frame. Outer→inner: a dark gutter that cleaves the
    new track off the bevel, a lit-bevel gold track hotter than the outer rim, a
    dark inner keyline for definition, and four bold corner masses so the framing
    survives the downscale to 162×100."""
    # (1) Dark inset gutter — the channel that visually SEPARATES the two frames.
    gutter = pygame.Rect(20, 20, 284, 160)
    pygame.draw.rect(surf, (6, 8, 20), gutter, width=4, border_radius=26)

    # (2) Inner gold track — a top-left-lit bevel deliberately BRIGHTER than the
    # outer bevel rim (236,202,116) so the double frame out-reads the single one.
    track = pygame.Rect(26, 26, 272, 148)
    trad = 22
    sc.bevel_rim(surf, track, trad, (58, 48, 22), (255, 240, 190), w=5)

    # (3) Inner keyline on the track's inside edge — a crisp dark line so the gold
    # lane has a defined inner boundary instead of bleeding into the tray.
    inner = track.inflate(-10, -10)
    pygame.draw.rect(surf, (58, 48, 22), inner, width=max(1, sc.m(0.6)),
                     border_radius=max(1, trad - 5))

    # (4) Corner masses — filled gold wedges pinning each inner corner. Bold enough
    # (~14px at SS=2) to still read as corner blocks at 1×, the regalia "cornered"
    # cue that keeps the frame legible once the art is scaled down.
    lit = (250, 232, 165)
    leg = 15
    corners = [
        (track.left,  track.top,    1,  1),   # TL
        (track.right, track.top,   -1,  1),   # TR
        (track.left,  track.bottom, 1, -1),   # BL
        (track.right, track.bottom, -1, -1),  # BR
    ]
    for cxp, cyp, sx, sy in corners:
        pygame.draw.polygon(surf, lit, [
            (cxp, cyp),
            (cxp + sx * leg, cyp),
            (cxp, cyp + sy * leg),
        ])
        # a hot inner glint on the two lit corners keeps them jewel-bright.
        pygame.draw.line(surf, (255, 246, 210),
                         (cxp, cyp), (cxp + sx * leg, cyp), max(1, sc.m(0.8)))


draw_regalia_frame(p2)


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
tt = title_f.render("equipped v3 — regalia-frame · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("STOCK EQUIPPED", GREY),
          ("REGALIA FRAME", CREAM_LBL)]
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

    # 1× read: downscale the panel to the true card size, then blow it back up
    # nearest-neighbour so the sheet shows exactly how the frame resolves at 1×.
    card1x = pygame.transform.smoothscale(panel, (ONE_W, ONE_H))
    zoom = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
    zt = zlbl_f.render("@1× (rendered then 2× nearest)", True, GREY)
    sheet.blit(zt, zt.get_rect(midbottom=(px + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
    sheet.blit(zoom, (px + (PANEL_W - ZOOM_W) // 2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3", "regalia_frame", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
