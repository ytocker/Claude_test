#!/usr/bin/env python3
"""
equipped-card v3.1 — equipped-check-chip symbol, round 1.

Builds on the approved regalia double-gold-frame (round 2) and adds the single
most LITERAL equipped/selected read: a compact dark-indigo pill at the card's
bottom-centre carrying a bright cream checkmark. The tick is the universal
mobile-UX shorthand for "this one is on", so the card now carries BOTH the
ambient regalia frame (glanceable across a grid) AND an explicit yes/no symbol
(unambiguous on the focused card).

Placement note — the pill sits at the SAME cy the equipped state-chip already
occupies on this card (cy=178 device, SS=2), i.e. the card's designated chip
slot below the name lane. "MUMMY" is all-caps with no descenders, so the pill's
top edge clears the letterforms' bodies, and at 22 px tall the pill intrudes on
that lane FAR less than the shipped 40 px green chip while still clearing the
body's bottom edge — so no relocation is needed.

The regalia frame is redrawn over the card first; the check chip then lands ON
TOP of it at bottom-centre as an explicit badge. The chip must be last because
the frame's bottom-edge beads run through the pill's lower half — drawn under
the frame, the pill would be half-buried; drawn over it, the pill overlaps the
bottom border the way a "selected" tab clips onto a frame.
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


def draw_check_chip(surf):
    """The equipped-check-chip symbol at SS=2: a dark-indigo stadium pill with a
    gold hairline ring and a centred cream checkmark. Drawn straight at device
    scale so the pill lands at cx=162, cy=178 — the card's chip slot, below the
    name lane and clear of the body's bottom edge."""
    INDIGO = (24, 22, 58)      # dark pill body — a calm ground for the tick
    RING = (196, 158, 74)      # gold hairline: ties the pill to the gold frame
    CREAM = (250, 246, 232)    # the tick — hottest, most legible mark on the card

    cx, cy = 162, 178
    pw, ph = 46, 22
    pill = pygame.Rect(cx - pw // 2, cy - ph // 2, pw, ph)   # (139,167,46,22)
    prad = ph // 2                                           # stadium ends

    # slim drop so the pill lifts off the card body a touch
    shadow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 90), pill.move(0, sc.m(1.2)),
                     border_radius=prad)
    surf.blit(shadow, (0, 0))

    pygame.draw.rect(surf, INDIGO, pill, border_radius=prad)
    # gold hairline ring around the FULL outline — even weight on every edge
    pygame.draw.rect(surf, RING, pill, width=max(2, sc.m(1.5)), border_radius=prad)

    # Cream checkmark. The long (right-up) arm is pitched a touch steeper than a
    # true 45° so it sweeps up through the pill's upper-right while leaving the
    # pill's exact centre in the open notch — the tick reads crisp yet the dark
    # ground stays visible around it, not flooded.
    left_tip = (152, 177)
    vertex = (160, 186)
    right_tip = (172, 168)
    stroke = max(4, sc.m(2.5))          # >=4 at SS=2 so it survives 1x downscale
    pygame.draw.lines(surf, CREAM, False, [left_tip, vertex, right_tip], stroke)
    # round the caps + elbow so the tick doesn't shear at small size
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


# ── Panel 2 — CONCEPT (regalia frame + equipped-check-chip) ──────────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
draw_regalia_frame(p2, rect)
draw_check_chip(p2)            # badge ON TOP so it clears the frame's bottom beads


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
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H
sheet_h = zoom_y + strip_h + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v3.1 — equipped-check-chip · round 1 · skin_mummy",
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

# 1× strip: true 162×100 tile of the concept, then nearest-neighbour scale2x so
# the sheet shows exactly how the pill + tick resolve at the real card size.
card1x = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
strip = pygame.transform.scale2x(card1x)
zx = xs[-1] + (PANEL_W - strip_w) // 2
zt = zlbl_f.render("@1× (162×100 tile, 2× nearest)", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(xs[-1] + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
sheet.blit(strip, (zx, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3_1", "equipped_check_chip", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
