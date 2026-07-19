#!/usr/bin/env python3
"""Round-1 render for the `torn-stub-redeemed` OWNED card state.

Concept: the price swing-tag reads as a REDEEMED voucher — torn horizontally
across its lower third so a stub survives at ~58% height (top bevel, grommet,
cord intact => a swing-tag, not a scrap). The tear is bitten by 4 bold
semicircle notches (coarse, never fine perforation). A single dark-key polyline
sits just under the torn lip as a self-shadow. A warm gold coin token centred on
the surviving stub face is the "paid / redeemed" mark — deliberately NO dark ✓
(that glyph belongs to the equipped state).

Headless review render; ships nothing."""
import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pygame; pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font
sd.load()

SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324×200
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)

m = sc.m


def torn_stub_face(face):
    """The redeemed-voucher effect painted onto the cream tag face.

    Draw order matters: punch the lower third + notches to transparent FIRST
    (draw ops on an SRCALPHA surface replace RGBA outright — the same
    zero-alpha punch the grommet hole uses), then the under-lip shadow and the
    coin token land on the surviving paper."""
    W, H = sc._TAG_W, sc._TAG_H            # 81 × 94 at SS=2
    y_tear = int(H * 0.58)                  # stub survives to ~58% height
    r = m(5)                                # coarse notch radius
    n = 4
    centers = [int((i + 0.5) / n * W) for i in range(n)]

    # 1. tear away everything below the lip.
    pygame.draw.rect(face, (0, 0, 0, 0), (0, y_tear, W, H - y_tear))
    # 2. bold semicircle notches bite UP into the stub along the tear line.
    for cxn in centers:
        pygame.draw.circle(face, (0, 0, 0, 0), (cxn, y_tear), r)

    # 3. a single dark-key polyline hugging the surviving edge, offset one px
    # into the paper so it reads as the lip's own self-shadow (top-left light).
    off = m(1)
    steps = 8
    pts = [(0, y_tear - off)]
    for cxn in centers:
        pts.append((cxn - r, y_tear - off))
        for s in range(steps + 1):
            th = math.pi + math.pi * s / steps     # top semicircle, 180°→360°
            pts.append((cxn + r * math.cos(th),
                        y_tear + r * math.sin(th) - off))
        pts.append((cxn + r, y_tear - off))
    pts.append((W, y_tear - off))
    pygame.draw.lines(face, (46, 38, 18), False, pts, max(1, m(1)))

    # 4. warm gold coin token = the redeemed / paid confirmation mark.
    ccx, ccy = W // 2, int(H * 0.38)
    cr = m(9)
    pygame.draw.circle(face, (236, 202, 116), (ccx, ccy), cr)          # gold disc
    pygame.draw.circle(face, (255, 248, 224),                          # cream core
                       (ccx - m(1), ccy - m(1)), int(cr * 0.6))
    pygame.draw.circle(face, (110, 80, 30), (ccx, ccy), cr, max(1, m(1)))  # rim


# ── Panel 0 — UNOWNED (price hang-tag) ────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# ── Panel 1 — EQUIPPED BASE (regalia frame + ✓ tag, reference context) ────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# ── Panel 2 — CONCEPT: torn-stub redeemed chip ────────────────────────────────
# Suppress the base state_chip so no price/✓ tag lands, then drop the custom
# torn-stub tag through the shared hang-tag geometry (cord/knot/grommet intact).
_orig_state_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=False, secret=False, owned=False)
sc.state_chip = _orig_state_chip

sc._draw_hang_tag(p2, rect.centerx, rect.y + sc.m(88) - sc._CHIP_DY,
                  draw_face_fn=torn_stub_face)


# ── compose review sheet ──────────────────────────────────────────────────────
BG = (8, 8, 20)
PAD = 20
LBL_H = 34
SGAP = 20
SLBL_H = 24
xs = [20, 360, 700]
panel_y = 102

GOLD = (236, 202, 116)
GREY = (150, 150, 168)
CREAM = (246, 244, 232)

# Zoom panel 2 down to the live card size, then nearest-neighbour 2× back up so
# the torn edge + coin token read at the resolution the player actually sees.
zoom = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
zoom = pygame.transform.scale2x(zoom)

sheet_w = xs[-1] + PANEL_W + PAD
sheet_h = panel_y + PANEL_H + LBL_H + SGAP + SLBL_H + zoom.get_height() + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)


def label(txt, x, y, w, col, size=18):
    f = hud_font(size, True)
    g = f.render(txt, True, col)
    sheet.blit(g, (x + (w - g.get_width()) // 2, y))


hf = hud_font(22, True)
hg = hf.render("owned v1 — torn-stub-redeemed · round 1 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNOWNED (PRICE)", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ TORN-STUB REDEEMED R1", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_owned_v1", "torn_stub_redeemed", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
