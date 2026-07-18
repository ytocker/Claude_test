#!/usr/bin/env python3
"""
equipped-card v3.1 — equipped-check-chip symbol, round 2 (final).

Round 1 planted a bottom-centre pill, but at true 1x its gold ring dissolved
into the frame's bottom-edge beads and the oversized, near-symmetric tick read
as a wedge. Round 2 answers every art-director note:

  * The badge moves to the BOTTOM-RIGHT corner — the dominant mobile "selected"
    convention. Top-right is owned by the faceted tier gem (cx=278, cy=46,
    r=22), which reaches to x~300, so a top-right token would crowd it; the
    bottom-right corner is clear dark card space.
  * It becomes a round token that FLOATS inside the inner track with a few px of
    dark padding to the frame, PLUS an explicit 2px dark-indigo halo ring
    (8,8,20) OUTSIDE the gold hairline — so the gold ring never touches a frame
    bead and the token reads as sitting ON TOP of the card, not dissolved into
    the border.
  * The tick shrinks to ~55% of the token interior with even padding, fully
    inside the ring, and is a PROPER asymmetric checkmark: a short steep left
    arm (~65deg down-left) and a long right arm (~50deg up-right) whose tip sits
    clearly higher than the left tip. That asymmetry is what separates a "check"
    from a "V" at thumbnail size.

Palette (dark-indigo / cream / gold), the gold hairline ring and the corner
anchor are kept from the approved regalia language. The token is drawn LAST, on
top of the regalia frame, as an explicit yes/no badge.
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
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
rad = sc.m(sc.CARD_RAD)


def draw_regalia_frame(surf, body):
    """The approved nested second gold frame, decoupled from bevel_rim so every
    bead is a CONSTANT-value stroke — equally hot on all four edges. Verbatim
    from the round-2 regalia concept so the two panels share one ring."""
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


# Token centre in device px — bottom-right corner. The inner track's dark card
# space runs to ~x=302 / y=178 before the bright inner bead; a radius-21 token
# centred here leaves ~3px of dark gap to the frame on both corner edges, so the
# 2px indigo halo never collides with a bead.
TOK_CX, TOK_CY = 278, 154
TOK_R = 21


def draw_check_token(surf):
    """The equipped-check-token: a dark-indigo disc, ringed in gold, floating in
    the card's bottom-right corner and carrying a compact cream checkmark. Drawn
    as concentric discs so the layer widths are exact: indigo body, a 2px gold
    hairline, then a 2px dark-indigo halo that guarantees separation from the
    regalia frame regardless of what sits under it."""
    INDIGO = (24, 22, 58)      # calm ground for the tick
    HALO = (8, 8, 20)          # dark card-shadow ring — divorces token from frame
    RING = (196, 158, 74)      # gold hairline: ties the token to the gold frame
    CREAM = (250, 246, 232)    # the tick — hottest, most legible mark on the card

    cx, cy = TOK_CX, TOK_CY

    # slim drop so the token lifts off the card body
    shadow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(shadow, (0, 0, 0, 100), (cx, cy + sc.m(1.2)), TOK_R)
    surf.blit(shadow, (0, 0))

    pygame.draw.circle(surf, HALO, (cx, cy), TOK_R)          # 21: dark halo
    pygame.draw.circle(surf, RING, (cx, cy), TOK_R - 2)      # 19: gold ring base
    pygame.draw.circle(surf, INDIGO, (cx, cy), TOK_R - 4)    # 17: indigo body

    # Cream checkmark — offsets from the token centre. Short steep left arm, long
    # up-right arm; the right tip sits well above the left tip so the mark reads
    # as a tick, not a symmetric V. Sized to ~55% of the interior with even
    # padding, every point kept a stroke-width clear of the gold ring.
    left_tip = (cx - 9, cy - 1)
    vertex = (cx - 5, cy + 9)
    right_tip = (cx + 9, cy - 9)
    stroke = max(4, sc.m(2.5))
    pygame.draw.lines(surf, CREAM, False, [left_tip, vertex, right_tip], stroke)
    for p in (left_tip, vertex, right_tip):
        pygame.draw.circle(surf, CREAM, p, stroke // 2)


# ── Panel 0 — UNEQUIPPED ─────────────────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)


# ── Panel 1 — REGALIA FRAME ONLY (chip suppressed) ───────────────────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
draw_regalia_frame(p1, rect)


# ── Panel 2 — CONCEPT (regalia frame + equipped-check-token) ─────────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
draw_regalia_frame(p2, rect)
draw_check_token(p2)          # badge ON TOP so it clears the frame's beads


# ── Compose the review sheet ─────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24

GOLD = (236, 202, 116)
GREY = (150, 152, 168)
CREAM_LBL = (250, 246, 232)

# fixed panel origins so the concept panel lands at x=700 (the review crop rect)
xs = [20, 360, 700]
panel_y = PAD + HDR_H + LBL_H                 # = 102
sheet_w = xs[-1] + PANEL_W + PAD              # = 1044
strip_w, strip_h = sc.CARD_W * 2, sc.CARD_H * 2   # scale2x of the 1× tile

# badge-zone zoom: a 40×40 1× crop around the token, blown up 3× nearest so a
# reviewer can confirm the tick resolves as a ✓ at true gameplay size.
BZ, BZS = 40, 3
bz_w = bz_h = BZ * BZS

strip_lbl_y = panel_y + PANEL_H + SGAP
strip_y = strip_lbl_y + SLBL_H
zoom_lbl_y = strip_y + strip_h + SGAP
zoom_y = zoom_lbl_y + SLBL_H
sheet_h = zoom_y + bz_h + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v3.1 — equipped-check-chip · round 2 · skin_mummy",
                    True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("REGALIA FRAME ONLY", GREY),
          ("FRAME + CHECK CHIP", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)

for x, panel, (label, col) in zip(xs, panels, labels):
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(x + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (x, panel_y))

# 1× strip: true 162×100 tile of the concept, nearest-neighbour scale2x.
card1x = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
strip = pygame.transform.scale2x(card1x)
sx0 = xs[-1] + (PANEL_W - strip_w) // 2
st = zlbl_f.render("@1× (162×100 tile, 2× nearest)", True, GREY)
sheet.blit(st, st.get_rect(midbottom=(xs[-1] + PANEL_W // 2, strip_lbl_y + SLBL_H - 4)))
sheet.blit(strip, (sx0, strip_y))

# badge-zone zoom: crop the 1× card around the token centre (device 278,154 →
# 1× 139,77) and scale 3× nearest so pixels stay honest.
tcx1, tcy1 = TOK_CX // sc.SS, TOK_CY // sc.SS
bz_rect = pygame.Rect(tcx1 - BZ // 2, tcy1 - BZ // 2, BZ, BZ)
bz_rect.clamp_ip(card1x.get_rect())
badge = pygame.transform.scale(card1x.subsurface(bz_rect), (bz_w, bz_h))
bx0 = xs[-1] + (PANEL_W - bz_w) // 2
zt = zlbl_f.render("@1× badge zone (×3 nearest) — confirm ✓ read", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(xs[-1] + PANEL_W // 2, zoom_lbl_y + SLBL_H - 4)))
sheet.blit(badge, (bx0, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3_1", "equipped_check_chip", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
