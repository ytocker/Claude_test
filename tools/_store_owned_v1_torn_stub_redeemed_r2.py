#!/usr/bin/env python3
"""Round-2 (final) render for the `torn-stub-redeemed` OWNED card state.

Concept: the price swing-tag reads as a REDEEMED voucher — torn horizontally
across its lower third so a stub survives at ~58% height (top bevel, grommet,
cord intact => a swing-tag, not a scrap). The tear now reads as a deliberate
perforation-stub: 3 wide, shallow scallops bitten up into the lip, with a single
CONTINUOUS dark-key self-shadow tracing the whole scalloped edge unbroken. A warm
gold coin token — lifted clear onto intact paper and stamped with a recessed key
ring so it reads as a "PAID" impression pressed into the stub, not a loose coin —
is the redeemed mark (deliberately NO dark ✓; that glyph is the equipped state).

R2 addresses the R1 critique: coin lifted to H*0.32 and shrunk to m(6) so it
clears the tear lip by m(6) with all scallops surviving; palette pulled onto the
key ink (cream core 255,240,190; rim/ring the 46,38,18 key, no muddy brown);
scallops widened + shallowed into a clean perforation; lip shadow made one
unbroken polyline; a recessed inner ring stamps the seal into the paper.

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

# Shared key ink — the tear shadow, the coin rim and the recessed stamp ring all
# sit on this one dark value so the token reads as ONE inked impression, never a
# brown coin floating over the paper.
KEY = (46, 38, 18)


def torn_stub_face(face):
    """The redeemed-voucher effect painted onto the cream tag face.

    Draw order matters: punch the lower third + scallops to transparent FIRST
    (draw ops on an SRCALPHA surface replace RGBA outright — the same zero-alpha
    punch the grommet hole uses), then the continuous under-lip shadow and the
    stamped coin token land on the surviving paper."""
    W, H = sc._TAG_W, sc._TAG_H            # 81 × 94 at SS=2
    y_tear = int(H * 0.58)                  # stub survives to ~58% height

    # 1. tear away everything below the lip.
    pygame.draw.rect(face, (0, 0, 0, 0), (0, y_tear, W, H - y_tear))

    # 2. three WIDE, SHALLOW scallops bite up into the stub — a deliberate
    # perforation-stub, not fine teeth. Circles are seated below the lip so only
    # a low, broad cap pokes into the paper (depth m(3) << width), which reads as
    # a torn-off ticket rather than a saw edge.
    R = m(6)
    depth = m(3)                            # how far each scallop eats upward
    seat = y_tear + (R - depth)             # circle center below the lip
    n = 3
    centers = [int((i + 0.5) / n * W) for i in range(n)]
    for cxn in centers:
        pygame.draw.circle(face, (0, 0, 0, 0), (cxn, seat), R)

    # 3. ONE continuous dark-key polyline hugging the whole surviving edge: flat
    # between scallops, arcing up over each cap, offset a hair into the paper so
    # it reads as the lip's own self-shadow (top-left light). Traced unbroken so
    # there are no dashed gaps.
    off = m(1)
    half = math.sqrt(max(0.0, R * R - (R - depth) ** 2))   # chord at the lip
    arc_steps = 10
    pts = [(0, y_tear - off)]
    for cxn in centers:
        pts.append((cxn - half, y_tear - off))
        for s in range(arc_steps + 1):
            x = -half + (2 * half) * s / arc_steps
            y = seat - math.sqrt(max(0.0, R * R - x * x))   # upper cap of the bite
            pts.append((cxn + x, y - off))
        pts.append((cxn + half, y_tear - off))
    pts.append((W, y_tear - off))
    pygame.draw.lines(face, KEY, False, pts, max(1, m(1)))

    # 4. the redeemed / paid token — a gold coin STAMPED into the stub. Lifted to
    # H*0.32 and shrunk to m(6) so it sits fully on intact paper (m(6) clear of
    # the lip) framed by a cream margin on all sides. A recessed inner key ring
    # + the outer key rim press it into the paper: an impression, not a loose
    # coin resting on a tag.
    ccx, ccy = W // 2, int(H * 0.32)
    cr = m(6)
    pygame.draw.circle(face, (236, 202, 116), (ccx, ccy), cr)               # gold disc
    pygame.draw.circle(face, (255, 240, 190),                                # cream core
                       (ccx - m(1), ccy - m(1)), int(cr * 0.55))
    pygame.draw.circle(face, KEY, (ccx, ccy), cr - m(1), max(1, m(1)))       # recessed stamp ring
    pygame.draw.circle(face, KEY, (ccx, ccy), cr, max(1, m(1)))              # outer key rim


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
hg = hf.render("owned v1 — torn-stub-redeemed · round 2 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNOWNED (PRICE)", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ TORN-STUB REDEEMED R2", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_owned_v1", "torn_stub_redeemed", "round_2.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
