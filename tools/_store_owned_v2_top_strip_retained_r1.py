#!/usr/bin/env python3
"""Round-1 render for the `top-strip-retained` OWNED card state (store_owned_v2).

Concept: the priced swing-tag has been RIPPED IN HALF. Only the top ~35% header
strip survives on the cord — grommet + top bevel intact, so it still reads as a
tag, not a scrap. The entire priced lower body is gone. The surviving strip's
bottom edge is a HAND-TORN jagged seam: asymmetric vertices, uneven pitch, and a
couple of deep bites — raw and organic, NOT a neat scallop/perforation (that
clean scalloped edge belongs to the kept-aside torn-stub-redeemed state). A
fiber-core highlight rides the down-jutting peaks; a valley shadow sits in the
recessed troughs, so the rip catches the top-left light like real torn paper.

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


def top_strip_retained_face(face):
    """The ripped-tag effect painted onto the cream tag face.

    Draw order: punch the whole lower body away along a hand-torn jagged seam
    FIRST (zero-alpha polygon fill replaces RGBA outright, the same punch the
    grommet hole uses), THEN lay the valley shadow just inside the surviving
    paper and the fiber-core highlight on the crest so the seam reads as raw
    torn fibre catching the top-left light."""
    W, H = sc._TAG_W, sc._TAG_H            # 81 × 94 at SS=2
    y_mean = int(H * 0.35)                  # header strip survives to ~35% height

    # Hand-authored asymmetric tear profile: (x-fraction, logical dy off mean).
    # Uneven x pitch + mixed excursions, with a couple of DEEP downward bites
    # (+5/+6) so no two teeth match — the read is raw, never a uniform scallop.
    profile = [
        (0.00, -1), (0.13, +3), (0.22, -3), (0.33, +6), (0.44, 0),
        (0.53, -4), (0.64, +5), (0.76, -2), (0.88, +4), (1.00, -1),
    ]
    seam = [(fx * (W - 1), y_mean + m(dy)) for fx, dy in profile]
    dys = [dy for _, dy in profile]

    # 1. rip the lower body away: fill the region UNDER the jagged seam with
    # zero alpha (down the right edge, across the foot, up the left edge).
    punch = seam + [(W, H), (0, H)]
    pygame.draw.polygon(face, (0, 0, 0, 0), punch)

    # 2. valley shadow — a dark polyline nudged UP into the surviving paper so it
    # pools in the recessed troughs and reads as the lip's self-shadow.
    off = m(1.2)
    shadow_pts = [(x, y - off) for x, y in seam]
    pygame.draw.lines(face, (46, 38, 18), False, shadow_pts, max(1, m(1.2)))

    # 3. fiber-core highlight — a warm bright polyline riding the crest edge; the
    # down-jutting peaks catch it, giving the torn fibre its lit tips.
    pygame.draw.lines(face, (255, 240, 190), False, seam, max(1, m(1)))

    # 4. bias each line to its terrain: brighten the deep peak tips, deepen the
    # deep trough recesses, so the rip never flattens into an even line.
    for (x, y), dy in zip(seam, dys):
        xi = int(x)
        if dy >= 4:                                    # deep down-jutting peak
            pygame.draw.circle(face, (255, 240, 190),
                               (xi, int(y - m(0.5))), max(1, m(1)))
        elif dy <= -3:                                 # deep torn-up trough
            pygame.draw.circle(face, (46, 38, 18),
                               (xi, int(y - m(1.6))), max(1, m(1)))


# ── Panel 0 — UNOWNED (price hang-tag) ────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# ── Panel 1 — EQUIPPED BASE (regalia frame + ✓ tag, reference context) ────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# ── Panel 2 — CONCEPT: top-strip-retained ripped tag ──────────────────────────
# Suppress the base state_chip so no price/✓ tag lands, then drop the ripped
# header strip through the shared hang-tag geometry (cord/knot/grommet intact).
_orig_state_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=False, secret=False, owned=False)
sc.state_chip = _orig_state_chip

sc._draw_hang_tag(p2, rect.centerx, rect.y + sc.m(88) - sc._CHIP_DY,
                  draw_face_fn=top_strip_retained_face)


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
# the raw torn seam reads at the resolution the player actually sees.
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
hg = hf.render("owned v2 — top-strip-retained · round 1 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNOWNED (PRICE)", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ TOP-STRIP RETAINED R1", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_owned_v2", "top_strip_retained", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
