#!/usr/bin/env python3
"""
equipped-card v3.1 — dome-jewel symbol, round 2 (final).

Round 1 marooned the jewel at a GEOMETRY constant (dome_center_y - dome_radius),
which landed it ~20px above the visible dome, touching the top frame gold, and
its dark indigo socket made the crest DIMMER — an inverted equipped tell.

Round 2 fixes both by measuring, not assuming:

  * The jewel's seat is found by SAMPLING the rendered frame-only card down the
    vertical centerline: the bright lit dome crest begins where luminance first
    climbs past the dark upper-glass band. The jewel's BOTTOM EDGE rests on that
    crest, so it sits ON the dome's glass surface (a dark contrasting backdrop),
    not in the frame gold above it.
  * The tell is flipped to LIT: a warm cream-gold bloom lifts the dark
    upper-dome band, a HOT glowing interior + a dominant specular pip read as
    "switched on", and a cool platinum bezel ringed by a dark contour separates
    the jewel silhouette from the warm frame gold so it can never camouflage.

Tying the equipped signal to the hero cabochon (not a frame bead or corner
badge) makes "powered on / in use" read as a property of the gem itself.
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
from game.draw import lerp_color
from game.hud import _font as hud_font

sd.load()

SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324×200
ri = sc.m(sc._INSET)                                      # 8
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)   # card body
rad = sc.m(sc.CARD_RAD)                                   # body corner radius

JX = rect.centerx                                         # 162 — dome centre x
JR = 11                                                   # bezel radius (SS=2 px)


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def find_dome_crest(panel, x=JX, y0=30, y1=86):
    """Return the y where the dome's LIT crest begins on the centreline.

    Scanning below the cabochon bezel, the dark upper-glass band stays dim until
    the domed glass catches the light and luminance climbs sharply — that rise
    is the visible crest the jewel must rest on. Measured, so the seat tracks the
    real render instead of a geometry constant that ignores the frame + bezel."""
    for y in range(y0, y1):
        if _lum(panel.get_at((x, y))) > 100:
            return y
    return 73                                            # measured fallback


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


def draw_dome_jewel(surf, crest_y):
    """The LIT activation jewel seated on the dome crest (SS=2 device px).

    Bottom edge rests on `crest_y` so the jewel sits ON the dome's upper glass —
    a dark backdrop the cool bezel separates cleanly from. Back-to-front: a warm
    cream-gold BLOOM lifts the dim upper-dome band (the crest reads warmer/
    brighter = 'on'); a dark contour ring + cool platinum bezel break it from the
    frame gold; a HOT glowing interior + a dominant cream pip are the lit tell —
    the inverse of round 1's dark switched-off socket."""
    jy = crest_y - JR                                    # bottom edge on the crest

    # 1. Warm bloom — a broad, low-alpha cream/gold halo that LIGHTS the dark
    #    upper-dome glass so the equipped crest is visibly warmer + brighter than
    #    the frame-only crest. Additive, so it lifts value without a hard edge.
    sc.soft_glow(surf, JX, jy, JR + sc.m(7), (255, 230, 160), 66, layers=11)

    # 2. Dark contour ring OUTSIDE the bezel — the silhouette separates from the
    #    adjacent warm frame gold (gold-on-gold would camouflage).
    pygame.draw.circle(surf, (40, 32, 14), (JX, jy), JR + 1)

    # 3. Cool platinum bezel — a silver rim reads apart from the warm gold frame.
    pygame.draw.circle(surf, (216, 216, 206), (JX, jy), JR, max(1, sc.m(1.2)))
    pygame.draw.circle(surf, (150, 150, 140), (JX, jy), JR - sc.m(0.9),
                       max(1, sc.m(0.6)))

    # 4. HOT lit interior — a radial from a cream-gold core to warm amber rim, so
    #    the socket reads GLOWING / powered-on rather than a dark, off well.
    ir = JR - sc.m(1.4)
    for i in range(ir, 0, -1):
        t = (i / ir) ** 1.1
        col = lerp_color((255, 242, 198), (208, 148, 60), t)
        pygame.draw.circle(surf, col, (JX, jy), i)

    # 5. Dominant cream specular pip — the KEY 'lit' tell, offset upper-left, with
    #    an additive core so it out-glows everything else in the cluster.
    px = JX - int(JR * 0.30)
    py = jy - int(JR * 0.30)
    pr = sc.m(3)                                         # ≥4px at SS=2 (device 6)
    pygame.draw.circle(surf, (255, 253, 244), (px, py), pr)
    core = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(core, (255, 244, 210, 235), (pr + 1, pr + 1),
                       max(1, pr - sc.m(0.8)))
    surf.blit(core, (px - pr - 1, py - pr - 1), special_flags=pygame.BLEND_ADD)

    # 6. Two short cream sparkle rays off the pip — sparkle that survives the 1×
    #    downscale without crowding the socket.
    for dx, dy in ((-sc.m(3.4), -sc.m(3.4)), (sc.m(3.6), -sc.m(2.2))):
        pygame.draw.line(surf, (255, 250, 232), (px, py),
                         (px + dx, py + dy), max(1, sc.m(0.8)))


# ── Panel 0 — UNEQUIPPED (price tag visible) ─────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)


# ── Panel 1 — REGALIA FRAME ONLY (no jewel) — the KEY brightness baseline ─────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False)
draw_regalia_frame(p1, rect)

# Measure the crest on the finished frame-only card so the jewel seats on the
# real render (identical base => valid P1-vs-P2 comparison).
CREST_Y = find_dome_crest(p1)


# ── Panel 2 — CONCEPT (regalia frame + LIT dome jewel) ───────────────────────
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
draw_regalia_frame(p2, rect)
draw_dome_jewel(p2, CREST_Y)


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
tt = title_f.render("equipped v3.1 — dome-jewel · round 2 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("REGALIA FRAME ONLY", GREY),
          ("FRAME + LIT DOME-JEWEL", CREAM_LBL)]
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
    "docs", "store_equipped_v3_1", "dome_jewel", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"

# Self-verify the two hard fixes: crest seated on real dome, and P2 > P1.
p1c = [_lum(p1.get_at((x, CREST_Y))) for x in range(JX - 7, JX + 8)]
p2c = [_lum(p2.get_at((x, CREST_Y - JR))) for x in range(JX - 7, JX + 8)]
print("saved", OUT, sheet.get_size())
print("crest_y (measured):", CREST_Y, "jewel centre y:", CREST_Y - JR)
print("P1 crest mean lum:", round(sum(p1c) / len(p1c), 1))
print("P2 jewel-band mean lum:", round(sum(p2c) / len(p2c), 1))
