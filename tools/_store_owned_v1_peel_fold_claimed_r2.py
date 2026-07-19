#!/usr/bin/env python3
"""Round-2 render for the `peel-fold-claimed` OWNED card state.

Concept: an intact cream swing-tag whose lower corner AWAY from the grommet
(bottom-right in face space) is peeled back as a generous triangular flap. The
flap shows its darker cream BACKSIDE with a fine fold-crease along the
hypotenuse and a soft drop-shadow so it reads as lifted, not printed. Where the
corner used to lie, the peel opens a pocket — but instead of a black void, the
recess now GLOWS warm gold (deep at the far corner, brightening toward the
hinge), so it signals "something good underneath." A single solid-gold coin,
sized to the pocket's inscribed circle and centred in the visible opening,
sits as the claimed / owned mark — deliberately NOT a dark ✓ (equipped state).

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


def _incircle(A, B, C):
    """Inscribed-circle centre + radius of triangle A,B,C. The incentre is the
    geometric middle of the pocket's *visible* opening, so a token placed there
    reads as centred gold rather than gold jammed into the deep corner."""
    a = math.hypot(B[0] - C[0], B[1] - C[1])   # side opposite A
    b = math.hypot(A[0] - C[0], A[1] - C[1])   # side opposite B
    c = math.hypot(A[0] - B[0], A[1] - B[1])   # side opposite C
    p = a + b + c or 1.0
    ix = (a * A[0] + b * B[0] + c * C[0]) / p
    iy = (a * A[1] + b * B[1] + c * C[1]) / p
    area = abs((B[0] - A[0]) * (C[1] - A[1]) - (C[0] - A[0]) * (B[1] - A[1])) / 2
    return (ix, iy), 2 * area / p


def _fill_pocket_warm(face, A, B, C):
    """Paint the corner pocket with a warm graded fill instead of a transparent
    punch: near-hinge (the fold line A→B) glows bright, the far corner C sinks
    deep. A warm recess reads as "reward under the paper"; a black hole read as
    torn damage. Small triangle (~35px), so a per-pixel scan is cheap."""
    lo = (150, 110, 40)   # deep, at the far corner C
    hi = (200, 160, 80)   # bright, at the hinge A→B
    # Fold-line normal, oriented so C is at the positive (deep) extreme.
    lnx, lny = -(B[1] - A[1]), (B[0] - A[0])
    ll = math.hypot(lnx, lny) or 1.0
    lnx, lny = lnx / ll, lny / ll
    dC = lnx * (C[0] - A[0]) + lny * (C[1] - A[1]) or 1.0

    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    minx = int(min(A[0], B[0], C[0])); maxx = int(max(A[0], B[0], C[0])) + 1
    miny = int(min(A[1], B[1], C[1])); maxy = int(max(A[1], B[1], C[1])) + 1
    for py in range(miny, maxy):
        for px in range(minx, maxx):
            p = (px + 0.5, py + 0.5)
            d1, d2, d3 = sign(p, A, B), sign(p, B, C), sign(p, C, A)
            if (d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0):
                continue                                   # outside the triangle
            t = (lnx * (p[0] - A[0]) + lny * (p[1] - A[1])) / dC
            t = 0.0 if t < 0 else 1.0 if t > 1 else t
            r = int(lo[0] * t + hi[0] * (1 - t))
            g = int(lo[1] * t + hi[1] * (1 - t))
            bl = int(lo[2] * t + hi[2] * (1 - t))
            face.set_at((px, py), (r, g, bl, 255))


def peel_fold_face(face):
    """The peeled-corner effect painted onto the cream tag face.

    Geometry: the fold runs A→B along the hypotenuse; C is the bottom-right
    corner. The POCKET (A,B,C) is filled with a warm gold gradient — its glow
    is what makes the gold token look like it nests UNDER the paper. The folded
    flap (A,B,C') is C mirrored over the fold, so its darker backside falls into
    the face interior above the fold line."""
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

    # 2. warm gold pocket — the glowing recess the token sits in.
    _fill_pocket_warm(face, A, B, C)

    # 3. claimed token: ONE solid-gold coin, sized to the pocket's inscribed
    #    circle and centred in the visible opening so gold (not void) is the mass
    #    the eye lands on. A single 1px dark ring is all the detail that survives
    #    at 40px — bands and cream cores just smear into mud at this size.
    (icx, icy), ir = _incircle(A, B, C)
    cr = max(m(4), int(ir) - 1)            # hug the opening, leave a hair of warm rim
    center = (int(round(icx)), int(round(icy)))
    pygame.draw.circle(face, (236, 202, 116), center, cr)              # solid gold
    pygame.draw.circle(face, (46, 38, 18), center, cr, max(1, m(1)))   # dark ring

    # 4. flap backside — a flat cream clearly darker than the face (a distinct
    #    folded plane at 40px), with a deeper wash toward the free tip.
    flap = [A, B, Cp]
    pygame.draw.polygon(face, (200, 175, 135), flap)
    tip_shade = [((A[0] + Cp[0]) / 2, (A[1] + Cp[1]) / 2),
                 ((B[0] + Cp[0]) / 2, (B[1] + Cp[1]) / 2), Cp]
    pygame.draw.polygon(face, (180, 150, 110), tip_shade)

    # 5. fold crease. A full-weight dark keyline on the pocket side is the
    #    shadowed base of the crease; a thin bright specular on the flap side is
    #    the standing paper edge catching the top-left key — that lit lip is what
    #    sells "lifted paper" over "printed line."
    off = 0.7
    kd0 = (A[0] - nx * off, A[1] - ny * off)
    kd1 = (B[0] - nx * off, B[1] - ny * off)
    pygame.draw.line(face, (70, 50, 22), kd0, kd1, max(1, m(1)))
    ks0 = (A[0] + nx * off, A[1] + ny * off)
    ks1 = (B[0] + nx * off, B[1] + ny * off)
    pygame.draw.line(face, (255, 248, 224), ks0, ks1, 1)


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
hg = hf.render("owned v1 — peel-fold-claimed · round 2 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNOWNED (PRICE)", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ PEEL-FOLD CLAIMED R2", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_owned_v1", "peel_fold_claimed", "round_2.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
