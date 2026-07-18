#!/usr/bin/env python3
"""
equipped-card v3.1 — sovereign-seal symbol on the regalia frame, round 1.

The regalia double-gold frame (approved in v3) tells you the card is equipped;
this round fills the empty upper-left quadrant the price tag vacated with a
pressed wax-seal medallion so an equipped card also reads "stamped /
authenticated / yours" — the personal-ownership beat the bare frame lacks.

The seal is built back-to-front like real pressed wax: a deep-gold rim, a warm
domed field with a faint rim-ward vignette, and a heraldic crown struck as an
INTAGLIO — recessed indigo with a single cream relief arc catching the light
along its upper contour, which is what sells "pressed into wax" rather than
"printed on". A few sub-pixel drip nubs give the wax an irregular, hand-struck
edge. Everything is fat enough to still resolve as a gold coin with a dark crown
notch once the card lands at the 162×100 tile size.
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


# ── regalia double-gold frame (verbatim construction from v3 round 2) ─────────
def draw_regalia_frame(surf, body):
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


# ── sovereign-seal medallion ─────────────────────────────────────────────────
def _lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_sovereign_seal(surf, cx=46, cy=52, R=20):
    """A pressed wax-seal medallion for the upper-left quadrant.

    Placed so the r=20 disc (reaches x66) clears the card's dome (~x110) and the
    opposite tier gem. Built back-to-front so the crown reads recessed."""
    RIM = (196, 158, 74)        # deep-gold pressed edge of the wax
    FIELD = (236, 202, 116)     # warm domed wax body (bright centre)
    FIELD_EDGE = (208, 173, 94) # slightly starved gold — the vignette floor
    INTAGLIO = (44, 40, 96)     # deep indigo struck-crown recess
    RELIEF = (250, 246, 232)    # cream light caught on the crown's upper contour
    DRIP_A = (250, 246, 232)
    DRIP_B = (206, 172, 92)

    # deep-gold rim ring — struck outer edge of the seal
    pygame.draw.circle(surf, RIM, (cx, cy), R, width=sc.m(1.0))

    # warm field with a faint rim-ward vignette: concentric fills interpolate the
    # bright centre out toward a starved-gold floor so the wax reads domed, not flat
    for rr in range(R - 2, 0, -1):
        t = rr / (R - 2)
        pygame.draw.circle(surf, _lerp(FIELD, FIELD_EDGE, t), (cx, cy), rr)

    # heraldic 3-point crown, struck as intaglio. Seated in the UPPER half of the
    # disc so the bright field centre (cx,cy) still shows below its base band.
    xl, xr = cx - 11, cx + 11
    y_base = cy - 1          # bottom of the crown's base band
    y_band = cy - 5          # top of base band / valley floor between the peaks
    y_tip = cy - 12          # blunt tips of the outer peaks
    y_tip_mid = cy - 14      # centre peak stands a touch taller
    p1, p2, p3 = cx - 7, cx, cx + 7     # peak centres
    v1, v2 = cx - 3.5, cx + 3.5         # valley centres
    b = 2                                # blunt-tip half-width

    contour = [
        (xl, y_band),
        (p1 - b, y_tip), (p1 + b, y_tip),
        (v1, y_band),
        (p2 - b, y_tip_mid), (p2 + b, y_tip_mid),
        (v2, y_band),
        (p3 - b, y_tip), (p3 + b, y_tip),
        (xr, y_band),
    ]
    crown = contour + [(xr, y_base), (xl, y_base)]
    pygame.draw.polygon(surf, INTAGLIO, crown)

    # single cream relief arc along the upper contour — the pressed-into-wax cue
    pygame.draw.aalines(surf, RELIEF, False, contour)

    # a few sub-pixel wax drips break the rim so it reads hand-struck, not
    # machined. Kept on the lower/left arc — wax runs downward, and it leaves the
    # struck top edge clean.
    import math
    for ang, col in ((235, DRIP_B), (300, DRIP_A), (205, DRIP_B), (150, DRIP_A)):
        a = math.radians(ang)
        dx, dy = cx + math.cos(a) * (R - 1), cy + math.sin(a) * (R - 1)
        pygame.draw.circle(surf, col, (round(dx), round(dy)), 2)


# ── Panel 0 — UNEQUIPPED (price tag visible) ─────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)


# ── Panel 1 — REGALIA FRAME ONLY (chip suppressed, frame, no seal) ───────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()
draw_regalia_frame(p1, rect)


# ── Panel 2 — CONCEPT (chip suppressed, frame + sovereign seal) ──────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()
draw_regalia_frame(p2, rect)
draw_sovereign_seal(p2)


# ── Compose the review sheet ─────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
ONE_W, ONE_H = sc.CARD_W, sc.CARD_H          # 162×100 true 1× card
ZOOM_W, ZOOM_H = ONE_W * 2, ONE_H * 2        # nearest-neighbour blow-up of 1×

GOLD = (236, 202, 116)
GREY = (150, 152, 168)
CREAM_LBL = (250, 246, 232)

N = 3
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD          # 1044
panel_y = PAD + HDR_H + LBL_H                              # 102
zlbl_y = panel_y + PANEL_H + SGAP                          # 322
zoom_y = zlbl_y + SLBL_H                                   # 346
sheet_h = zoom_y + ZOOM_H + PAD                            # 566
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render(
    "equipped v3.1 — sovereign-seal · round 1 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY),
          ("REGALIA FRAME ONLY", GREY),
          ("+ SOVEREIGN SEAL", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)                        # 20, 360, 700
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

# 1× strip: TRUE 162×100 tile of the concept, then nearest-neighbour 2× so the
# sheet shows exactly how the seal + frame resolve at the real card size.
px2 = PAD + 2 * (PANEL_W + GAP)                           # 700
card1x = pygame.transform.smoothscale(p2, (ONE_W, ONE_H))
zoom = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
zt = zlbl_f.render("@1× (162×100 tile, 2× nearest)", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(px2 + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
sheet.blit(zoom, (px2 + (PANEL_W - ZOOM_W) // 2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3_1", "sovereign_seal", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
