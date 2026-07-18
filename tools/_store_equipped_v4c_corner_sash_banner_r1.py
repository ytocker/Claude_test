#!/usr/bin/env python3
"""Round-1 review render for the `corner-sash-banner` equipped indicator: a gold
diagonal ribbon folded across the card's top-right corner with "EQUIPPED" set
along the diagonal. Built with no dark masking rectangle — the sash is a gold
gradient clipped to a right-triangle, then re-clipped to the card's rounded
corner. Rendered headless onto a labeled review sheet; ships nothing."""
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
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)   # 8,8,308,184


def draw_corner_sash_banner(surf):
    """A gold 'certified-corner' sash folded across the top-right corner. The
    sash is a right-triangle [A, corner, B] filled with a gold gradient (masked,
    like _ribbon — no dark backing rect), lifted by a cream top-fold glint on the
    outer hypotenuse and a dark valley crease just inside it, with tiny dark
    tuck-tabs where it meets the card edges. The whole fold is re-clipped to the
    card's rounded corner so it never spills past the rim."""
    m = sc.m
    A = (228, 8)
    CORNER = (316, 8)
    B = (316, 96)

    layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)

    # (1) gold fill: a vertical gold ramp over the 88×88 bounding box, clipped to
    # the sash right-triangle with a white-fill BLEND_RGBA_MIN mask.
    BW = 88
    box_x, box_y = A[0], A[1]
    gold = sc.vgrad_stops(BW, BW, 0,
                          [(0.0, (255, 240, 190)), (1.0, (236, 202, 116))], 255)
    tri_local = [(A[0] - box_x, A[1] - box_y),
                 (CORNER[0] - box_x, CORNER[1] - box_y),
                 (B[0] - box_x, B[1] - box_y)]
    tmask = pygame.Surface((BW, BW), pygame.SRCALPHA)
    pygame.draw.polygon(tmask, (255, 255, 255, 255), tri_local)
    gold.blit(tmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    layer.blit(gold, (box_x, box_y))

    # (3) valley-dark under-fold crease: a 2px line on the inner parallel diagonal,
    # offset ~6px toward the corner from the A–B hypotenuse.
    nx, ny = 0.70710678, -0.70710678   # A–B perpendicular, pointing at the corner
    off = 6
    a_in = (A[0] + off * nx, A[1] + off * ny)
    b_in = (B[0] + off * nx, B[1] + off * ny)
    pygame.draw.line(layer, (9, 9, 22), a_in, b_in, 2)

    # (4) cream top-fold glint on the OUTER hypotenuse so the fold catches light.
    pygame.draw.line(layer, (255, 240, 190), A, B, 1)

    # (5) tuck-tabs — tiny dark triangles where the sash folds under each edge.
    pygame.draw.polygon(layer, (9, 9, 22),
                        [(A[0], A[1]), (A[0] + 8, A[1]), (A[0], A[1] + 8)])
    pygame.draw.polygon(layer, (9, 9, 22),
                        [(B[0], B[1]), (B[0], B[1] - 8), (B[0] - 8, B[1])])

    # (6) re-clip the whole fold to the card's rounded corner.
    cmask = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.rect(cmask, (255, 255, 255, 255), rect, border_radius=m(sc.CARD_RAD))
    layer.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # (7) composite onto the card.
    surf.blit(layer, (0, 0))

    # (8) "EQUIPPED" struck in dark key, rotated -45° along the A–B diagonal.
    f = sc.font(9)
    base = sc._stamp_bold(sc._glyph_base("EQUIPPED", f, m(0.8)), m(0.8))
    img = base.copy()
    img.fill((46, 38, 18, 255), special_flags=pygame.BLEND_RGBA_MULT)
    rot = pygame.transform.rotate(img, -45)
    mid = ((A[0] + B[0]) // 2, (A[1] + B[1]) // 2)   # (272, 52)
    surf.blit(rot, rot.get_rect(center=mid))


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (hang-tag + regalia frame, no sash)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + corner sash banner)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_corner_sash_banner(p2)


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

# zoom of panel 2
zoom = pygame.transform.smoothscale(p2, (162, 100))
zoom = pygame.transform.scale2x(zoom)   # 324×200

sheet_w = xs[-1] + PANEL_W + PAD
sheet_h = panel_y + PANEL_H + LBL_H + SGAP + SLBL_H + zoom.get_height() + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)


def label(txt, x, y, w, col, size=18):
    f = hud_font(size, True)
    g = f.render(txt, True, col)
    sheet.blit(g, (x + (w - g.get_width()) // 2, y))


# header
hf = hud_font(22, True)
hg = hf.render("equipped v4c — corner-sash-banner · round 1 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNEQUIPPED", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ CORNER SASH BANNER", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

# zoom strip beneath panel 2
zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_equipped_v4c", "corner_sash_banner", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
