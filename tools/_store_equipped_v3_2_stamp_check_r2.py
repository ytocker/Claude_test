#!/usr/bin/env python3
"""
equipped-card v3.2 — ink-stamped checkmark symbol, round 2 (final pass).

Same concept as round 1: a single BACKING-FREE ✓ struck straight onto the indigo
card body over the approved regalia double-frame — no disc, no tag, no cord. A
stamped tick is the most universal "confirmed / active / mine" mark, and with
nothing behind it the whole upper-left tag zone becomes the symbol.

Round 1 read as a flick/swoosh, not a tick, because the short arm was ~3.5:1
too short — it collapsed to a ~3px nub at 1× and the vertex risked rounding into
a comma. Round 2 rebalances the silhouette so it unambiguously reads as a check:

  * the short arm is lengthened to a ~2.2:1 ratio against the long arm (was
    ~3.5–4:1) so both arms carry real weight and the down-then-flick asymmetry
    still reads;
  * its terminal is fattened (half-width 1.7→2.5) so it downsamples to a legible
    arm at the 162×100 tile instead of a dot;
  * the along-stroke gradient is biased toward cream up the ramp so the raised
    short tip flares with the same crafted-metal highlight the long arm already
    had, not just the low vertex pool;
  * the vertex is kept low and given a generous cap so the inner elbow stays a
    crisp corner, never a comma; and
  * the whole mark is lifted a few px to sit better in the y:0–110 tag zone and
    give the long-arm tip more air above the corner mass.

Drawn LAST over an equipped card whose green chip is suppressed, so the frame +
stamp are the sole state signal on the concept panel.
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
from game.draw import lerp_color
from game.hud import _font as hud_font

sd.load()

SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324×200
ri = sc.m(sc._INSET)                                      # 8
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)   # card body
rad = sc.m(sc.CARD_RAD)                                   # body corner radius


def draw_regalia_frame(surf, body):
    """The approved nested second gold frame, decoupled from bevel_rim.

    Reproduced verbatim from v3 round 2 so the stamp sits on the exact frame the
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


# ── the stamp ─────────────────────────────────────────────────────────────────
# Centreline in device px on the 324×200 SS surface. Vertex sits low; the short
# arm rises up-left through the (30,50) tag-zone band, the long arm sweeps up-
# right through the (44,60) centre. The short:long length ratio is held near
# 2.2:1 so both arms read; every tip is pulled ≥4px inside the inner track
# (x≥18, y≥18) and clear of the corner masses.
_V = (40.0, 69.0)     # brush vertex — thickest, lowest (warm-gold pool)
_L = (30.0, 49.0)     # short arm tip — up-left, fattened terminal (~2.2:1 arm)
_R = (73.0, 32.0)     # long arm tip  — up-right, fine terminal (longest reach)
_HW_V = 4.8           # half-width at the vertex (fat pressed elbow)
_HW_TIP_L = 2.5       # fattened short terminal — downsamples to a legible arm
_HW_TIP_R = 1.8       # fine long terminal — keeps the crafted wedge taper


def _stamp_silhouette(dst, col):
    """Paint the tapered ✓ body onto `dst` in one flat colour: two tapered quads
    (fat at the shared vertex, pinched at each tip) plus round caps at the vertex
    and both tips so terminals read as pressed wedges, never flat-cut lines."""
    def quad(a, b, hwa, hwb):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        px, py = -dy / ln, dx / ln          # unit perpendicular
        return [(a[0] + px * hwa, a[1] + py * hwa),
                (b[0] + px * hwb, b[1] + py * hwb),
                (b[0] - px * hwb, b[1] - py * hwb),
                (a[0] - px * hwa, a[1] - py * hwa)]

    pygame.draw.polygon(dst, col, quad(_V, _L, _HW_V, _HW_TIP_L))
    pygame.draw.polygon(dst, col, quad(_V, _R, _HW_V, _HW_TIP_R))
    pygame.draw.circle(dst, col, (int(round(_V[0])), int(round(_V[1]))),
                       int(round(_HW_V)))                       # rounded vertex
    for tip, hw in ((_L, _HW_TIP_L), (_R, _HW_TIP_R)):
        pygame.draw.circle(dst, col, (int(round(tip[0])), int(round(tip[1]))),
                           max(1, int(round(hw))))              # rounded terminals


def draw_stamp_check(surf):
    """A backing-free ink-stamped ✓ struck onto the indigo body.

    Layer order gives it the bite of a pressed stamp: first a 1px dark ghost of
    the whole mark offset down-right (the ink squeezed past the die edge), then
    the gold body filled by a vertical warm-gold→cream ramp so the low vertex
    pools dark and both raised tips flare hot. The ramp is eased toward cream up
    its length so the raised SHORT tip carries the same crafted-metal highlight
    as the long arm, not just the vertex — the gradient runs along the stroke and
    obeys the frame's top-lit angle in one masked move."""
    WARM = (196, 158, 74)      # darker warm gold — the low vertex pool
    CREAM = (255, 240, 190)    # hot cream-gold — the raised tips
    DARK = (46, 38, 18)        # stamp-bite ghost
    sz = surf.get_size()

    # 1px (final-scale) dark offset ghost UNDER the stamp for pressed-in bite.
    ghost = pygame.Surface(sz, pygame.SRCALPHA)
    _stamp_silhouette(ghost, (*DARK, 255))
    surf.blit(ghost, (sc.m(1), sc.m(1)))

    # Gold body: paint a white silhouette, then intersect a vertical ramp so the
    # gradient is carried by the stroke shape (dark at the low vertex y, hot at
    # the high tip y). The ease exponent biases cream upward so the raised short
    # tip flares — top-lit, along-path, in a single masked gradient.
    sil = pygame.Surface(sz, pygame.SRCALPHA)
    _stamp_silhouette(sil, (255, 255, 255, 255))
    top_y, bot_y = min(_L[1], _R[1]), _V[1]    # brightest tip level → dark vertex
    grad = pygame.Surface(sz, pygame.SRCALPHA)
    for y in range(sz[1]):
        f = max(0.0, min(1.0, (y - top_y) / (bot_y - top_y)))
        c = lerp_color(CREAM, WARM, f ** 1.25)
        pygame.draw.line(grad, (*c, 255), (0, y), (sz[0], y))
    grad.blit(sil, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, (0, 0))


# ── Panel 0 — UNEQUIPPED ─────────────────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)

# ── Panels 1 & 2 — chip suppressed so the frame/stamp is the sole state signal ─
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None

sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)   # REGALIA FRAME ONLY
sc.draw_card(p1, SID, rect, equipped=True, secret=False)
draw_regalia_frame(p1, rect)

sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)   # CONCEPT: frame + stamp
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
draw_regalia_frame(p2, rect)
draw_stamp_check(p2)

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
tt = title_f.render("equipped v3.2 — stamp-check · round 2 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("REGALIA FRAME ONLY", GREY),
          ("CONCEPT (frame + stamp)", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

# 1× strip under panel 2 only: the true 162×100 tile, blown back up 2× nearest
# so the sheet shows exactly how the stamp resolves at the real card size.
px2 = PAD + 2 * (PANEL_W + GAP)
card1x = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
zoom = pygame.transform.scale2x(card1x)
zt = zlbl_f.render("@1× (162×100 tile, scale2x)", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(px2 + PANEL_W // 2, zlbl_y + SLBL_H - 6)))
sheet.blit(zoom, (px2 + (PANEL_W - zoom.get_width()) // 2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3_2", "stamp_check", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
