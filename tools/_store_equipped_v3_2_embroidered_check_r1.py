#!/usr/bin/env python3
"""
equipped-card v3.2 — embroidered-check concept, round 1.

A raised satin-stitch cream check sewn DIRECTLY onto the card's indigo body at
the old tag area — varsity-patch / premium-merch feel, with NO backing disc and
NO tag plate at all. The mark is the sole ornament: an asymmetric tick (short
left arm down to the vertex, long arm up-right), built as a bold cream stroke
whose satin sheen is SUGGESTED — a run of short threads laid perpendicular
across the stroke, alternating a near-white highlight and a warm-tan shadow so
the stroke catches light like real floss. The threads are deliberately thin +
tightly stepped so at the 162×100 tile they collapse into ONE clean cream check
(the stitch grain is a close-inspection bonus, never 1× noise). A 1px dark
under-shadow lifts the whole mark off the indigo like proud embroidery.

Drawn LAST over an equipped card whose green chip is suppressed and whose
regalia double-frame is the surrounding state signal.
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


# ── Panel 0 — UNEQUIPPED (price tag visible) ─────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)


# ── regalia frame (verbatim copy of _store_equipped_v3_regalia_frame_r2.py) ──
def draw_regalia_frame(surf, body):
    """The nested second gold frame, decoupled from bevel_rim.

    Read outer→inner: a warm-gold OUTER bead hugging the card edge, a flat dark
    VALLEY that cleaves the two beads apart, a HOT constant INNER track (the hero
    line, hotter than the bevel on EVERY edge), a fine dark inner keyline, and
    four bright corner masses. Because each bead is a single flat-colour stroke —
    not a gradient — the sides and bottom stay exactly as bright as the top, so
    the double frame reads as an even jewelled ring at the 162×100 tile size."""
    OUTER = (236, 202, 116)     # warm-gold outer bead (the bevel-echo line)
    VALLEY = (9, 9, 22)         # flat near-body dark — clean, no indigo bleed
    INNER = (255, 240, 190)     # HOT constant inner track — hotter than the bevel
    KEY = (46, 38, 18)          # deep inner keyline: a defined inner boundary
    GLINT = (255, 248, 224)     # jewel highlight on the two top-lit corners

    def bead(inset, w, col, alpha=255):
        """A CONSTANT-colour rounded-rect stroke inset `inset` device-px from the
        card edge — the whole point of round 2: no top-lit falloff, so the stroke
        is equally hot on all four sides."""
        r = body.inflate(-2 * inset, -2 * inset)
        s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(s, (*col, alpha), r, width=w,
                         border_radius=max(1, rad - inset))
        surf.blit(s, (0, 0))

    # OUTER bead sits wide (surface ~10..16) so the near-edge zone reads gold on
    # every side; the VALLEY then opens INSIDE it so the dark channel never eats
    # the outer line on the flanks the way a top-lit gutter did in round 1.
    bead(inset=2,  w=sc.m(3.0), col=OUTER)           # outer bead
    bead(inset=8,  w=sc.m(1.4), col=VALLEY)          # flat dark valley (widened)
    bead(inset=10, w=sc.m(2.0), col=INNER)           # HOT inner track (hero line)
    bead(inset=13, w=max(1, sc.m(0.6)), col=KEY)     # fine inner keyline

    # Corner masses — filled gold wedges pinning each INNER-track corner so the
    # frame still resolves as "cornered regalia" once the art lands at 162×100.
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
    # a hot glint on the two upper corners keeps them jewel-bright
    for cxp, cyp, sx, sy in corners[:2]:
        pygame.draw.line(surf, GLINT, (cxp, cyp), (cxp + sx * leg, cyp),
                         max(1, sc.m(0.8)))


# ── embroidered satin-stitch check ───────────────────────────────────────────
# The mark's geometry lives at the (44,60) tag anchor every review script uses,
# so it lands exactly where the old hang-tag price chip did.
_CHK_CREAM = (250, 246, 232)     # base floss colour — the clean 1× read
_CHK_HI = (255, 252, 242)        # near-white highlight thread (lit crown of a stitch)
_CHK_SH = (214, 196, 158)        # warm-tan shadow thread (the trough between stitches)
_CHK_DARK = (20, 18, 44)         # under-shadow: lifts the embroidery off the body


def _satin_run(surf, p0, p1, hw, tilt_deg, phase):
    """Lay a run of short threads perpendicular-ish across the stroke p0→p1,
    alternating highlight / shadow so the stroke reads as ridged satin floss.
    Threads are thin (1 logical px) and tightly stepped (~1 logical px apart) so
    the alternation is sub-pixel at 1× and blurs back into the solid cream base —
    the grain only resolves under the SS=2 close-up."""
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length < 1:
        return
    ux, uy = dx / length, dy / length          # along the stroke
    nx, ny = -uy, ux                            # perpendicular to it
    # tilt each thread a touch off perpendicular so the lay reads like real
    # slanted satin floss rather than a mechanical ladder.
    a = math.radians(tilt_deg)
    tx = nx * math.cos(a) + ux * math.sin(a)
    ty = ny * math.cos(a) + uy * math.sin(a)
    step = sc.mf(1.05)
    tw = max(1, sc.m(1.0))
    n = int(length / step)
    for i in range(n + 1):
        t = i * step
        cx = x0 + ux * t
        cy = y0 + uy * t
        col = _CHK_HI if ((i + phase) % 2 == 0) else _CHK_SH
        ax, ay = cx - tx * hw, cy - ty * hw
        bx, by = cx + tx * hw, cy + ty * hw
        pygame.draw.line(surf, col, (ax, ay), (bx, by), tw)


def draw_embroidered_check(surf):
    """The whole raised satin check, drawn over the card body at the tag anchor."""
    # (44,60) at SS=2 is (m(22), m(30)); the asymmetric tick opens up-right.
    V = (sc.m(22), sc.m(30))     # vertex  → (44, 60)
    A = (sc.m(18), sc.m(26))     # short left arm crown → (36, 52)
    B = (sc.m(31.5), sc.m(19))   # long right arm crown → (63, 38)
    hw = sc.m(1.5)               # half-stroke: total ≈ 3 logical-px satin band
    segs = ((A, V), (V, B))

    # 1px under-shadow: the same stroke in body-dark, nudged down-right, so the
    # embroidery reads as proud of the indigo rather than printed into it.
    off = max(1, sc.m(0.6))
    for s, e in segs:
        pygame.draw.line(surf, _CHK_DARK, (s[0] + off, s[1] + off),
                         (e[0] + off, e[1] + off), int(hw * 2) + max(1, sc.m(0.7)))
    for pt in (A, V, B):
        pygame.draw.circle(surf, _CHK_DARK, (pt[0] + off, pt[1] + off),
                           hw + max(1, sc.m(0.35)))

    # solid cream base guarantees the clean bold 1× read; the satin grain rides
    # on top of it and averages back toward this cream when downscaled.
    for s, e in segs:
        pygame.draw.line(surf, _CHK_CREAM, s, e, int(hw * 2))
    for pt in (A, V, B):
        pygame.draw.circle(surf, _CHK_CREAM, pt, hw)

    # satin threads. Opposite phases on the two arms keep the stitch lay
    # continuous through the vertex rather than mirroring at the join.
    _satin_run(surf, A, V, hw, tilt_deg=16, phase=0)
    _satin_run(surf, V, B, hw, tilt_deg=16, phase=1)


# ── Panel 1 — REGALIA FRAME ONLY (chip suppressed) ───────────────────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None          # suppress the green EQUIPPED chip
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()
draw_regalia_frame(p1, rect)


# ── Panel 2 — CONCEPT (regalia frame + embroidered check) ────────────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()
draw_regalia_frame(p2, rect)
draw_embroidered_check(p2)


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
tt = title_f.render("equipped v3.2 — embroidered-check · round 1 · skin_mummy",
                    True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("REGALIA FRAME ONLY", GREY),
          ("EMBROIDERED CHECK", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)
panel_y = PAD + HDR_H + LBL_H          # = 102

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

# 1× read of the CONCEPT: true 162×100 tile (smoothscale down), blown back up
# nearest-neighbour so the sheet shows exactly how the satin grain resolves at
# the real card size — the stitches must fuse into one clean cream check.
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H
card1x = pygame.transform.smoothscale(p2, (ONE_W, ONE_H))
zoom = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
zt = zlbl_f.render("CONCEPT @1× (162×100 tile, 2× nearest)", True, GREY)
zx = PAD + 2 * (PANEL_W + GAP)
sheet.blit(zt, zt.get_rect(midbottom=(zx + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
sheet.blit(zoom, (zx + (PANEL_W - ZOOM_W) // 2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3_2", "embroidered_check", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
