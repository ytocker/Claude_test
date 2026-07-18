#!/usr/bin/env python3
"""
equipped-card v3.1 — corner-sash symbol, round 2 (final).

Builds on the approved regalia double-frame by slinging a diagonal cream ribbon
across the upper-left corner — but round 1's blank sash + single pip read as a
"NEW / SALE / HOT" promo ribbon. A glyph-less ribbon is decoration; it carries
no "owned" meaning. Round 2 fixes the SEMANTICS while keeping the diagonal
geometry that already survives the 162×100 downscale:

- The pip is replaced by a deep-indigo CHECKMARK centred on the band. A ✓ is the
  universal "owned / equipped / done" mark, so the ribbon now says exactly what
  the card's state is instead of shouting a fake promo. Indigo-on-cream keeps the
  proven ~200-luminance contrast, and the two chunky strokes (≥5px at SS=2)
  resolve as a check — not a smudge — once the tile shrinks to 1×.
- The sash's gold piping is shifted a half-shade LIGHTER/COOLER than the frame's
  gold so the two golds no longer fuse into one mass where they meet, and the
  sash is clipped to stop just SHORT of the frame's inner keyline so a hairline
  of dark card face reads as the seam of a layered object sitting ON the frame.
- The clip is tightened so the band terminates cleanly against the card's
  rounded-rect boundary with no stray cream fragments outside the stripe.
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
    """A diagonal cream ribbon across the upper-left corner carrying a deep-indigo
    checkmark — the "equipped / owned" mark. Built at ~45° with a constant band
    width so the silhouette is a clean stripe, then clipped to just inside the
    frame so a hairline of dark card face separates ribbon from bevel and the
    ribbon reads as a layered object sitting ON the frame.

    The 1× read is a cream diagonal with a bold ✓: cream body, LIGHT-cool gold
    piping on both long edges (a half-shade off the frame gold so the two golds
    don't fuse), a deep-gold fold shadow on the lower edge (fabric lift), and a
    chunky two-stroke indigo checkmark dead-centre — the mark that turns a
    decorative ribbon into an ownership badge."""
    CREAM = (250, 246, 232)     # sash body
    PIPING = (255, 220, 160)    # LIGHT-cool gold piping — a half-shade off the
                                # frame's (236,202,116) so the golds stay distinct
    FOLD = (196, 158, 74)       # deep-gold fold shadow on the lower edge
    CHECK = (44, 40, 96)        # deep-indigo checkmark — the ownership mark

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
    # is pure detail (it may fade at 1×; the checkmark carries the read).
    pygame.draw.line(sash, FOLD, outer[0], outer[1], max(1, sc.m(0.5)))

    # The mark: a chunky two-stroke checkmark centred on the band. A short arm
    # drops into the vertex, a longer arm rises up-right; both are thick enough
    # (≥5px at SS=2) to survive the 1× downscale as a recognisable ✓ rather than
    # a blob. Rounded joints/caps keep the strokes reading as one clean glyph.
    Lp = (32, 38)   # top of the short (left) arm
    Vp = (37, 43)   # bottom vertex where the strokes meet
    Rp = (47, 29)   # top of the long (right) arm
    cw = max(5, sc.m(2.5))                     # =5 device px → ~2.5px at 1×
    pygame.draw.line(sash, CHECK, Lp, Vp, cw)
    pygame.draw.line(sash, CHECK, Vp, Rp, cw)
    for cap in (Lp, Vp, Rp):
        pygame.draw.circle(sash, CHECK, cap, cw // 2)

    # Clip to just INSIDE the frame's inner keyline so the band stops short of the
    # gold and a hairline of dark card face shows as the seam — the ribbon then
    # sits ON the frame rather than fusing with the bevel. A rounded-rect mask
    # hard-edges the band against the card boundary (no stray cream fragments).
    clip_inset = 15
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
tt = title_f.render("equipped v3.1 — corner-sash · round 2 (final) · skin_mummy",
                    True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("REGALIA FRAME ONLY", GREY),
          ("FRAME + CORNER SASH + CHECKMARK", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

# 1× strip under panel 2 only: the true 162×100 tile, blown back up 2× nearest
# so the sheet shows exactly how the sash + checkmark resolve at the real card
# size.
px2 = PAD + 2 * (PANEL_W + GAP)
card1x = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
zoom = pygame.transform.scale2x(card1x)
zt = zlbl_f.render("@1× (162×100 tile, scale2x)", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(px2 + PANEL_W // 2, zlbl_y + SLBL_H - 6)))
sheet.blit(zoom, (px2 + (PANEL_W - zoom.get_width()) // 2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3_1", "corner_sash", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())

# ── In-script verification: confirm the fixes actually land ──────────────────
# Checkmark must read at 1×, and the corner seam must show dark card, not fused
# gold. Sample the true 162×100 tile + the device-res concept.
tile = card1x
indigo_hits = 0
for yy in range(14, 24):
    for xx in range(14, 26):
        r, g, b, _a = tile.get_at((xx, yy))
        if b > r + 20 and b > 60 and r < 120:      # deep-indigo checkmark pixels
            indigo_hits += 1
print("1x checkmark indigo pixels:", indigo_hits, "(want a solid cluster)")
print("concept sash body  (38,38):", p2.get_at((38, 38))[:3])
print("concept check core (37,39):", p2.get_at((37, 39))[:3])
