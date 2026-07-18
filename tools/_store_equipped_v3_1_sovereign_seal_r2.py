#!/usr/bin/env python3
"""
equipped-card v3.1 — sovereign-seal symbol on the regalia frame, round 2.

Round 1's dome gold matched the frame gold exactly, so the seal fused into the
frame instead of reading as a distinct stamp. This round switches to the literal
wax-seal convention: a crimson/oxblood dome inside a near-black bronze crimp
ring, which separates from the gold frame by both hue and value and reads
"stamped / authenticated / yours" at a glance. The heraldic crown is rebuilt as
a bolder 3-prong indigo mass whose silhouette survives the downscale, and a
single ivory specular dot on the dome sells "polished wax sheen". Bold,
asymmetric drips (biased down-left, where wax flows) keep the hand-struck edge.
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


# ── sovereign-seal medallion — crimson wax stamp ─────────────────────────────
def _lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_sovereign_seal(surf, cx=46, cy=52, R=20):
    """A pressed CRIMSON-WAX seal for the upper-left quadrant.

    Wax red instead of gold is deliberate: two identical golds beside the frame
    fused the seal into the border, so the disc now separates by hue AND value.
    Built back-to-front like real wax — near-black bronze crimp ring, an oxblood
    dome that brightens toward its domed centre, a bold indigo crown struck as
    intaglio, one ivory sheen, and drips biased down-left where wax flows."""
    CRIMP = (72, 33, 12)        # near-black bronze crimp ring — sharp disc edge
    WAX_RIM = (124, 31, 31)     # deep oxblood where the dome meets the ring
    WAX_MID = (168, 50, 50)     # brighter crimson at the domed centre
    INTAGLIO = (44, 40, 96)     # deep indigo struck-crown recess
    SHEEN = (255, 248, 224)     # ivory specular hotspot — polished-wax gloss
    DRIP_D = (118, 30, 30)      # darker wax nub
    DRIP_L = (156, 46, 46)      # lit wax nub

    crimp_w = sc.m(1.5)

    # near-black bronze disc: the whole seal starts as the crimp ring so a sharp
    # ring survives once the dome is laid inside it
    pygame.draw.circle(surf, CRIMP, (cx, cy), R)

    # oxblood dome: concentric fills lerp from the domed bright centre out to the
    # starved rim so the wax reads convex, sitting inside the crimp ring
    inner = R - crimp_w
    for rr in range(inner, 0, -1):
        t = rr / inner
        pygame.draw.circle(surf, _lerp(WAX_MID, WAX_RIM, t), (cx, cy), rr)

    # heraldic 3-prong crown struck as intaglio, seated in the UPPER half so the
    # crimson dome centre (cx,cy) still shows below its base band. Bold blunt
    # prongs with wide notches down to the band so three distinct points still
    # resolve small — the indigo MASS, not a hairline, carries the silhouette.
    p_l, p_m, p_r = cx - 10, cx, cx + 10    # prong centres, wide gaps
    xl, xr = cx - 12, cx + 12               # base-band edges
    hw = sc.m(1.0)                          # prong half-width (parallel sides)
    y_base = cy - 1                          # bottom of the base band (above cy)
    y_strip = cy - 4                         # top of the thin base strip
    y_tip = cy - 14                          # outer prong tips
    y_tip_m = cy - 16                        # centre prong stands taller

    # Three parallel-sided bars on a thin base strip, NOT a trapezoid crown:
    # full-height wax gaps between the bars keep the three prongs distinct when
    # the tile is downscaled — a widening base would fuse them into one blob.
    pygame.draw.rect(surf, INTAGLIO, (xl, y_strip, xr - xl, y_base - y_strip))
    for px in (p_l, p_m, p_r):
        ty = y_tip_m if px == p_m else y_tip
        pygame.draw.rect(surf, INTAGLIO, (px - hw, ty, 2 * hw, y_base - ty))

    # single ivory specular on clear upper-left wax to read polished-wax gloss.
    # Two-stop dot: soft warm halo under a tight bright core. Kept clear of the
    # crown x-span so it lands on high-contrast crimson, never on indigo.
    sx, sy = cx - 13, cy - 4
    pygame.draw.circle(surf, (214, 150, 120), (sx, sy), sc.m(1.6))
    pygame.draw.circle(surf, SHEEN, (sx, sy), max(1, sc.m(0.9)))

    # bold asymmetric drips: heavier cluster down-left where wax runs, a couple to
    # the lower-right. Each nub is fat enough to survive the 1× tile.
    drips = [
        (108, R + 1, 3, DRIP_D),
        (126, R + 2, 3, DRIP_L),
        (144, R + 1, 3, DRIP_D),
        (162, R,     2, DRIP_L),
        (90,  R + 1, 2, DRIP_D),
        (66,  R,     2, DRIP_L),
    ]
    for deg, dist, r, col in drips:
        a = math.radians(deg)
        dx, dy = cx + math.cos(a) * dist, cy + math.sin(a) * dist
        pygame.draw.circle(surf, col, (round(dx), round(dy)), r)


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
    "equipped v3.1 — sovereign-seal · round 2 · skin_mummy", True, GOLD)
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

# 1× strip below panel 2: a GENUINE smoothscale 162×100 tile (how the card ships)
# beside a nearest-neighbour 2× blow-up so the seal's small-size read is honest.
px2 = PAD + 2 * (PANEL_W + GAP)                           # 700
card1x = pygame.transform.smoothscale(p2, (ONE_W, ONE_H))
zoom = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
zt = zlbl_f.render("@1× true 162×100 tile   ·   2× nearest", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(px2 + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
# true 1× tile on the left, 2× nearest blow-up to its right, within panel width
strip_gap = 24
group_w = ONE_W + strip_gap + ZOOM_W
gx = px2 + (PANEL_W - group_w) // 2
one_y = zoom_y + (ZOOM_H - ONE_H) // 2
sheet.blit(card1x, (gx, one_y))
sheet.blit(zoom, (gx + ONE_W + strip_gap, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3_1", "sovereign_seal", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
