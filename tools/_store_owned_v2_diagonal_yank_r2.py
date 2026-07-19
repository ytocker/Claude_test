#!/usr/bin/env python3
"""Round-2 render for the `diagonal-yank` OWNED card state (store_owned_v2).

Concept unchanged from R1: the priced swing-tag is torn on a DIAGONAL from near
the top-right corner down to near the bottom-left. The grommet-bearing upper-left
triangle survives on the cord; the price-bearing lower-right triangle is yanked
away. The diagonal direction, seam angle and punch polygon are the concept's
equity and are held fixed.

R2 addresses the art-director's R1 critique:
  1. Brighter fiber-core highlight (near-white crest) riding OVER a thick dark
     valley band so the lit fibre tips read as light-over-dark, not light-on-cream.
  2. Valley self-shadow thickened to m(2) with near-black pooled recesses at the
     deep bites, so the seam survives the true 1× downsample.
  3. Ragged corner nicks bitten into the top edge (near the top termination) and
     the left edge (near the bottom termination) so the survivor can't be misread
     as a folded corner or a deliberately-cut badge.
  4. A short trail of 2–3 fibre flecks drifting off the ripped bottom-left tip
     toward lower-right, implying the direction the price section was yanked.
  5. The grommet demoted — smaller radius, nudged tighter into the top-left corner
     — so the eye's first read lands on the tear, not the hole.

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


def _int(pts):
    return [(int(round(x)), int(round(y))) for x, y in pts]


def _p(pt):
    return (int(round(pt[0])), int(round(pt[1])))


def diagonal_yank_face(face):
    """The diagonal-tear effect painted onto the cream tag face.

    Draw order: punch the lower-right triangle away along the (unchanged) hand-torn
    diagonal seam AND rag a couple of nicks into the machine edges where the seam
    terminates, THEN pool a thick valley self-shadow just inside the surviving
    paper, THEN ride a near-white fiber-core highlight along the crest so the
    diagonal reads as raw torn fibre catching the top-left light. The seam is
    placed so the demoted grommet stays safely inside the surviving upper-left
    triangle."""
    W, H = sc._TAG_W, sc._TAG_H            # 81 × 94 at SS=2
    p_top = (W * 0.85, 0.0)                 # tear enters the top edge near the right
    p_bot = (0.0, H * 0.85)                 # and exits the left edge near the foot

    dx, dy = p_bot[0] - p_top[0], p_bot[1] - p_top[1]
    dlen = math.hypot(dx, dy)
    # Unit normal biased toward the removed lower-right side, so a +excursion
    # bulges the tear into the yanked triangle and a -excursion bites back into
    # the surviving paper.
    nx, ny = dy / dlen, -dx / dlen

    # Hand-authored asymmetric tear profile (UNCHANGED from R1): (t along the
    # diagonal, logical excursion off the line). Uneven pitch and mixed excursions
    # with three DEEP bites so no two teeth match — the read is raw fibre, never a
    # uniform scallop. Endpoints sit ON the line; corner raggedness is added by the
    # separate nick punches below rather than by bending the seam.
    profile = [
        (0.00, 0), (0.06, -2), (0.13, +3), (0.20, -1), (0.27, +8),
        (0.33, +1.5), (0.40, -6), (0.46, +2), (0.53, -1.5), (0.60, +4),
        (0.66, -3), (0.72, +10), (0.79, -0.5), (0.86, +3.5), (0.93, -2.5),
        (1.00, 0),
    ]
    seam, offs = [], []
    for t, off in profile:
        bx, by = p_top[0] + dx * t, p_top[1] + dy * t
        seam.append((bx + nx * off, by + ny * off))
        offs.append(off)

    # Nicks bitten into the machine edges where the seam terminates — small alpha-0
    # triangles that interrupt the clean top edge (near the top termination) and
    # the clean left edge (near the bottom termination), so the survivor reads as
    # torn all the way to the corners rather than a folded/cut wedge.
    top_nicks = [
        [(65.0, 0.0), (68.0, 0.0), (66.3, m(2.4))],
        [(59.5, 0.0), (62.0, 0.0), (60.6, m(1.7))],
        [(53.5, 0.0), (55.6, 0.0), (54.4, m(1.3))],
    ]
    left_nicks = [
        [(0.0, 74.5), (0.0, 77.5), (m(2.4), 76.0)],
        [(0.0, 68.5), (0.0, 71.0), (m(1.7), 69.7)],
        [(0.0, 62.5), (0.0, 64.6), (m(1.3), 63.5)],
    ]

    def punch():
        # Everything lower-right of the seam: down the seam, hook past the
        # bottom-left corner, across the foot and up the right edge.
        poly = seam + [(0, H), (W, H), (W, 0)]
        pygame.draw.polygon(face, (0, 0, 0, 0), _int(poly))
        for nk in top_nicks + left_nicks:
            pygame.draw.polygon(face, (0, 0, 0, 0), _int(nk))

    # 1. rip the lower-right triangle away (+ rag the corners).
    punch()

    # 2. valley self-shadow — a THICK warm-dark band nudged just inside the
    # surviving paper so it pools behind the crest as the torn lip's self-shadow.
    # At m(2) it survives the 1× downsample; the deep troughs pool a near-black
    # recess so the biggest bites still read as recessed after downscale. This is
    # also the darker ground the bright highlight rides over.
    sh = [(x - nx * m(1.2), y - ny * m(1.2)) for x, y in seam]
    pygame.draw.lines(face, (52, 42, 18), False, _int(sh), max(2, m(2)))
    for i, off in enumerate(offs):
        if off <= -3 and 0 < i < len(sh) - 1:
            pygame.draw.circle(face, (11, 10, 24), _p(sh[i]), max(2, m(1.4)))

    # 3. fiber-core highlight — a NEAR-WHITE warm crest hugging the torn edge, sat
    # directly over the dark valley band so the lit fibre tips read as
    # light-over-dark against the cream paper (R1's (255,240,190) was invisible at
    # only ~7 values above the body). Out-jutting peaks catch an extra lit dab.
    hi = [(x - nx * m(0.35), y - ny * m(0.35)) for x, y in seam]
    pygame.draw.lines(face, (255, 253, 231), False, _int(hi), max(1, m(1)))
    for i, off in enumerate(offs):
        if off >= 3.5:                                 # deep out-jutting peak tip
            pygame.draw.circle(face, (255, 253, 231), _p(hi[i]), max(1, m(1)))

    # 4. re-punch so any highlight/shadow that spilled past the torn edge (and any
    # bevel inside the nicks) is clipped back — the jagged silhouette stays crisp.
    punch()

    # 5. fibre flecks — a short trail of 2–3 detached tufts drifting off the ripped
    # bottom-left tip toward lower-right, implying the direction the price section
    # was yanked. Drawn AFTER the final punch so they float in the torn-away void;
    # kept few and ≥m(1) so they read as fibre, not dirt. Each gets a faint dark
    # seat so it separates from the dark background.
    flecks = [((6.0, 84.0), m(1.4)), ((11.5, 88.0), m(1.1)), ((16.5, 91.0), m(1.0))]
    for (fx, fy), fr in flecks:
        pygame.draw.circle(face, (36, 30, 16, 150), (int(fx) + 1, int(fy) + 1), fr)
        pygame.draw.circle(face, (243, 234, 206), (int(fx), int(fy)), fr)


def _draw_hang_tag_r2(surf, cx, cy, draw_face_fn=None):
    """Local copy of sc._draw_hang_tag with the grommet DEMOTED for R2 — smaller
    radius and nudged tighter into the top-left corner so it stops competing with
    the tear for the first read. Kept in the review tool (not store_cards) because
    the live check/owned tags must keep the full-size grommet until the concept is
    chosen. Cord/knot/bevel/geometry are otherwise identical to the shared draw."""
    rad     = m(3)
    grommet = (27, 11)                     # was (30, 13): 3 px up-left, tighter corner
    g_r     = m(5) - 2                      # was m(5): shrunk so the hole reads smaller

    face  = pygame.Surface((sc._TAG_W, sc._TAG_H), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, sc._TAG_W, sc._TAG_H)
    body  = sc.vgrad_stops(sc._TAG_W, sc._TAG_H, rad,
                           [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                           255, gamma=1.04)
    face.blit(body, (0, 0))
    sc.bevel_rim(face, brect, rad, (80, 52, 12, 200),
                 (255, 240, 190, 200), w=max(1, m(1.2)))

    if draw_face_fn is not None:
        draw_face_fn(face)

    pygame.draw.circle(face, (0, 0, 0, 0), grommet, g_r)
    pygame.draw.circle(face, (110, 80, 30), grommet, g_r + 1, width=max(1, m(1)))

    rot  = pygame.transform.rotate(face, sc._TAG_TILT)
    cord = (190, 165, 115)
    tag_center = (44, 60)
    knot       = (22, 13)
    gx, gy = sc._tag_rot_point(*grommet, tag_center)
    lw = m(1.5)
    pygame.draw.line(surf, cord, (gx, gy), (knot[0] - 1, knot[1] - 1), lw)
    pygame.draw.line(surf, cord, (gx, gy), (knot[0] + 2, knot[1] + 2), lw)
    surf.blit(rot, rot.get_rect(center=tag_center))
    pygame.draw.circle(surf, cord, knot, m(1.5))
    pygame.draw.circle(surf, (min(cord[0]+30, 255), min(cord[1]+30, 255),
                              min(cord[2]+30, 255)), knot, max(1, m(0.6)))


# ── Panel 0 — UNOWNED (price hang-tag) ────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# ── Panel 1 — EQUIPPED BASE (regalia frame + ✓ tag, reference context) ────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# ── Panel 2 — CONCEPT: diagonal-yank ripped tag (R2) ──────────────────────────
# Suppress the base state_chip so no price/✓ tag lands, then drop the diagonally
# torn tag through the shared hang-tag geometry (cord/knot intact, grommet demoted).
_orig_state_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=False, secret=False, owned=False)
sc.state_chip = _orig_state_chip

_draw_hang_tag_r2(p2, rect.centerx, rect.y + sc.m(88) - sc._CHIP_DY,
                  draw_face_fn=diagonal_yank_face)


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

# Zoom panel 2 to the TRUE live card size (smoothscale to CARD_W×CARD_H), then
# nearest-neighbour 2× back up — this is the resolution the player actually sees,
# and where the seam highlight/shadow must still show a ≥2px wobble.
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
hg = hf.render("owned v2 — diagonal-yank · round 2 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNOWNED (PRICE)", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ DIAGONAL-YANK R2", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2 (TRUE 1× → 2×)", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_owned_v2", "diagonal_yank", "round_2.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
