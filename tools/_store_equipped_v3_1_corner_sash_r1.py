#!/usr/bin/env python3
"""
equipped-card v3.1 — corner-sash symbol, round 1.

Builds on the approved regalia double-frame (v3 round 2) by adding a single
SYMBOL: a diagonal cream ribbon slung across the upper-left corner. A sash is
the universal "decorated / awarded / collected" mark — a soldier's sash, an
award ribbon — so it reads as a *badge of ownership* the moment the card is
equipped, on top of the frame that already says "active".

The whole point is 1× parseability: the diagonal silhouette (a cream stripe
cutting the corner with one dark pip on it) has to resolve at the 162×100 tile
size BEFORE any fold-shadow or piping detail is visible. Gold-on-cream detail
vanishes at 1×, so the only interior mark is a deep-indigo pip — a dark dot on
a light stripe survives the downscale where a glyph would smear away.

Sash is drawn LAST (over the regalia frame) but CLIPPED to the inner card face,
so the double-gold frame still rings everything and the ribbon sits tucked
inside it rather than bleeding out over the bevel.
"""
import math
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
    """The approved nested second gold frame, decoupled from bevel_rim.

    Reproduced verbatim from v3 round 2 so the sash sits on the exact frame the
    art director signed off on. Read outer→inner: warm-gold OUTER bead, a flat
    dark VALLEY, a HOT constant INNER track (the hero line), a fine dark inner
    keyline, and four bright corner masses. Every bead is a single flat-colour
    stroke so the ring stays equally hot on all four edges at 162×100."""
    OUTER = (236, 202, 116)
    VALLEY = (9, 9, 22)
    INNER = (255, 240, 190)
    KEY = (46, 38, 18)
    GLINT = (255, 248, 224)

    def bead(inset, w, col, alpha=255):
        r = body.inflate(-2 * inset, -2 * inset)
        s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(s, (*col, alpha), r, width=w,
                         border_radius=max(1, rad - inset))
        surf.blit(s, (0, 0))

    bead(inset=2,  w=sc.m(3.0), col=OUTER)
    bead(inset=8,  w=sc.m(1.4), col=VALLEY)
    bead(inset=10, w=sc.m(2.0), col=INNER)
    bead(inset=13, w=max(1, sc.m(0.6)), col=KEY)

    track = body.inflate(-2 * 10, -2 * 10)
    leg = sc.m(7)
    corners = [
        (track.left,  track.top,     1,  1),
        (track.right, track.top,    -1,  1),
        (track.left,  track.bottom,  1, -1),
        (track.right, track.bottom, -1, -1),
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


def draw_corner_sash(surf, body):
    """A diagonal cream ribbon across the upper-left corner — the "collected"
    mark. Built at ~45° with a constant width so the silhouette is a clean
    stripe, then clipped to the inner card face so the gold frame still rings it
    and the ribbon never paints over the bevel.

    Layered so the 1× read is a cream diagonal with one dark pip: cream body,
    gold piping on both long edges (a full logical px so it survives downscale),
    a deep-gold fold shadow on the lower edge (fabric lift), and a lone
    deep-indigo pip dead-centre — the only interior mark that reads at 1×."""
    CREAM = (250, 246, 232)     # sash body
    PIPING = (214, 176, 92)     # gold edge piping (both long edges)
    FOLD = (196, 158, 74)       # deep-gold fold shadow on the lower edge
    PIP = (44, 40, 96)          # deep-indigo pip — the sole interior mark

    # Centreline crosses the corner from left edge to top edge; endpoints and
    # the ±half-width offset are in device px on the 324×200 surface.
    A = (18.0, 58.0)
    B = (58.0, 18.0)
    hw = 8.0                                   # half of the ~16px band width
    dx, dy = B[0] - A[0], B[1] - A[1]
    plen = math.hypot(dx, dy)
    # Perpendicular unit pointing toward the bottom-right (the LOWER long edge).
    perp = (-dy / plen, dx / plen)
    ox, oy = perp[0] * hw, perp[1] * hw

    inner = [(A[0] - ox, A[1] - oy), (B[0] - ox, B[1] - oy)]   # toward corner
    outer = [(A[0] + ox, A[1] + oy), (B[0] + ox, B[1] + oy)]   # away (lower edge)
    poly = [inner[0], inner[1], outer[1], outer[0]]

    # Paint the sash onto its own layer so it can be clipped as one unit.
    sash = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(sash, CREAM, poly)
    # Piping on BOTH long edges at a full logical px so the gold trim stays solid
    # once the tile is downscaled to 162×100.
    pygame.draw.line(sash, PIPING, inner[0], inner[1], sc.SS)
    pygame.draw.line(sash, PIPING, outer[0], outer[1], sc.SS)
    # Fold shadow: 1px deep-gold on the lower long edge only — a fabric lift that
    # is pure detail (it may fade at 1×; the pip carries the read).
    pygame.draw.line(sash, FOLD, outer[0], outer[1], max(1, sc.m(0.5)))
    # The sole mark: one deep-indigo pip centred on the band.
    pygame.draw.circle(sash, PIP, (int((A[0] + B[0]) / 2), int((A[1] + B[1]) / 2)),
                       sc.m(2))

    # Clip to the inner card face (inside the frame's keyline) so the ribbon sits
    # tucked within the double-gold ring, never over the bevel/frame.
    clip_inset = 14
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     body.inflate(-2 * clip_inset, -2 * clip_inset),
                     border_radius=max(1, rad - clip_inset))
    sash.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(sash, (0, 0))


# ── Panel 0 — UNEQUIPPED ─────────────────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)

# ── Panels 1 & 2 — chip suppressed so the frame/sash is the sole state signal ─
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None

sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)   # REGALIA FRAME ONLY
sc.draw_card(p1, SID, rect, equipped=True, secret=False)
draw_regalia_frame(p1, rect)

sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)   # CONCEPT: frame + sash
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
draw_regalia_frame(p2, rect)
draw_corner_sash(p2, rect)

sc.state_chip = orig_chip
sc._card_cache.clear()


# ── Compose the review sheet ─────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 34

GOLD = (236, 202, 116)
GREY = (150, 152, 168)
CREAM_LBL = (250, 246, 232)

N = 3
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
panel_y = PAD + HDR_H + LBL_H                     # = 102
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H
sheet_h = zoom_y + PANEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v3.1 — corner-sash · round 1 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("REGALIA FRAME ONLY", GREY),
          ("CONCEPT (frame + sash)", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

# 1× strip under panel 2 only: the true 162×100 tile, blown back up 2× nearest
# so the sheet shows exactly how the sash resolves at the real card size.
px2 = PAD + 2 * (PANEL_W + GAP)
card1x = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
zoom = pygame.transform.scale2x(card1x)
zt = zlbl_f.render("@1× (162×100 tile, scale2x)", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(px2 + PANEL_W // 2, zlbl_y + SLBL_H - 6)))
sheet.blit(zoom, (px2 + (PANEL_W - zoom.get_width()) // 2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3_1", "corner_sash", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
