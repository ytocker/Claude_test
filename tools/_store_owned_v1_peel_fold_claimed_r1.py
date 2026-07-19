#!/usr/bin/env python3
"""Round-1 render for the `peel-fold-claimed` OWNED card state.

Concept: an intact cream swing-tag whose lower corner AWAY from the grommet
(bottom-right in face space) is peeled back as a generous triangular flap. The
flap shows its slightly-darker cream BACKSIDE with a fine fold-crease along the
hypotenuse and a soft drop-shadow so it reads as lifted, not printed. Where the
corner used to lie, the peel opens a pocket that reveals a warm GOLD coin token
underneath — gold is the "claimed" confirmation, deliberately NOT a dark ✓
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


def _reflect(p, a, b):
    """Mirror point p across the line through a,b — gives the folded flap's tip
    (the peeled corner rotated over the fold), so the backside triangle lands in
    the face interior instead of floating off the corner."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    d2 = dx * dx + dy * dy or 1.0
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / d2
    fx, fy = a[0] + t * dx, a[1] + t * dy
    return (2 * fx - p[0], 2 * fy - p[1])


def peel_fold_face(face):
    """The peeled-corner effect painted onto the cream tag face.

    Geometry: the fold runs A→B along the hypotenuse; C is the bottom-right
    corner. The POCKET (A,B,C) is punched to zero-alpha so the indigo card body
    reads through it — that void is what makes the gold token look like it sits
    UNDER the paper. The folded flap (A,B,C') is C mirrored over the fold, so its
    darker backside falls into the face interior above the fold line."""
    W, H = sc._TAG_W, sc._TAG_H            # 81 × 94 at SS=2
    A = (W, H * 0.62)                       # upper fold endpoint (right edge)
    B = (W * 0.60, H)                       # lower fold endpoint (bottom edge)
    C = (W, H)                              # peeled corner (right angle)
    Cp = _reflect(C, A, B)                  # folded flap tip, over the fold

    # Fold-normal (unit), biased to the flap side, so crease + shadow offset the
    # right way regardless of the exact fold angle.
    nx, ny = A[1] - B[1], B[0] - A[0]
    nl = math.hypot(nx, ny) or 1.0
    nx, ny = nx / nl, ny / nl
    if (nx * (Cp[0] - A[0]) + ny * (Cp[1] - A[1])) > 0:   # point toward flap side
        nx, ny = -nx, -ny

    # 1. soft triangular drop-shadow: the flap silhouette nudged down-right (away
    #    from the top-left key) so a dark sliver of cast shadow hugs the fold.
    shadow = [(x - nx * m(1.5) + m(1), y - ny * m(1.5) + m(2)) for (x, y) in (A, B, Cp)]
    sh = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (9, 9, 22, 95), shadow)
    face.blit(sh, (0, 0))

    # 2. flap backside — flat darker cream, with a second darker wash toward the
    #    free tip so the underside reads slightly graded (224,204,166 → 206,184,150).
    flap = [A, B, Cp]
    pygame.draw.polygon(face, (224, 204, 166), flap)
    tip_shade = [((A[0] + Cp[0]) / 2, (A[1] + Cp[1]) / 2),
                 ((B[0] + Cp[0]) / 2, (B[1] + Cp[1]) / 2), Cp]
    pygame.draw.polygon(face, (206, 184, 150), tip_shade)

    # 3. fold crease: a pale highlight lip UNDER a 1px dark keyline, both nudged a
    #    hair to the flap side of the fold so the pocket punch (below) can't eat
    #    them — the crease belongs to the standing flap edge, not the void.
    off = 1.0
    h0 = (A[0] + nx * off, A[1] + ny * off)
    h1 = (B[0] + nx * off, B[1] + ny * off)
    pygame.draw.line(face, (255, 248, 224), h0, h1, max(1, m(1)))
    pygame.draw.line(face, (110, 80, 30), h0, h1, 1)

    # 4. reveal the pocket: multiply the face's own alpha by a mask that is zero
    #    inside the corner triangle, so those pixels turn transparent and the card
    #    body indigo shows through behind the tag.
    pocket = [A, B, C]
    punch = pygame.Surface((W, H), pygame.SRCALPHA)
    punch.fill((255, 255, 255, 255))
    pygame.draw.polygon(punch, (255, 255, 255, 0), pocket)
    face.blit(punch, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # 5. warm gold coin token nested in the pocket = the claimed / owned mark.
    ccx = int((A[0] + B[0] + C[0]) / 3)
    ccy = int((A[1] + B[1] + C[1]) / 3)
    cr = m(4)
    pygame.draw.circle(face, (236, 202, 116), (ccx, ccy), cr)          # gold disc
    pygame.draw.circle(face, (255, 248, 224),                          # cream core
                       (ccx - m(1), ccy - m(1)), max(1, int(cr * 0.55)))
    pygame.draw.circle(face, (110, 80, 30), (ccx, ccy), cr, max(1, m(1)))  # rim


# ── Panel 0 — UNOWNED (price hang-tag) ────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# ── Panel 1 — EQUIPPED BASE (regalia frame + ✓ tag, reference context) ────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# ── Panel 2 — CONCEPT: peel-fold claimed chip ─────────────────────────────────
# Suppress the base state_chip so no price/✓ tag lands, then drop the custom
# peel-fold tag through the shared hang-tag geometry (cord/knot/grommet intact).
_orig_state_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=False, secret=False, owned=False)
sc.state_chip = _orig_state_chip

sc._draw_hang_tag(p2, rect.centerx, rect.y + sc.m(88) - sc._CHIP_DY,
                  draw_face_fn=peel_fold_face)


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
# the peel edge + coin token read at the resolution the player actually sees.
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
hg = hf.render("owned v1 — peel-fold-claimed · round 1 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNOWNED (PRICE)", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ PEEL-FOLD CLAIMED R1", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_owned_v1", "peel_fold_claimed", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
