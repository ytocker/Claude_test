#!/usr/bin/env python3
"""Round-1 render for the `diagonal-yank` OWNED card state (store_owned_v2).

Concept: the priced swing-tag has been torn on a DIAGONAL from near the
top-right corner down to near the bottom-left. The upper-left triangle — the one
carrying the grommet — survives on the cord; the lower-right triangle (which held
the price) is yanked away. The fibrous diagonal seam is the whole story: an
asymmetric hand-torn edge with irregular pitch and a few deep bites, a warm
fiber-core highlight riding its crest and a valley shadow pooled just inside the
surviving paper so it catches the top-left light like real torn card. The
survivor stays CLEAN cream — no sheared numeral ghosts, which at 40px would only
read as noise; the seam alone tells the story.

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


def diagonal_yank_face(face):
    """The diagonal-tear effect painted onto the cream tag face.

    Draw order: punch the lower-right triangle away along a hand-torn diagonal
    seam FIRST (zero-alpha polygon fill replaces RGBA outright, the same punch
    the grommet hole uses), THEN pool the valley shadow just inside the surviving
    paper and ride the fiber-core highlight along the crest so the diagonal reads
    as raw torn fibre catching the top-left light. The diagonal is placed so the
    grommet at (30,13) sits safely inside the surviving upper-left triangle."""
    W, H = sc._TAG_W, sc._TAG_H            # 81 × 94 at SS=2
    p_top = (W * 0.85, 0.0)                 # tear enters the top edge near the right
    p_bot = (0.0, H * 0.85)                 # and exits the left edge near the foot

    dx, dy = p_bot[0] - p_top[0], p_bot[1] - p_top[1]
    dlen = math.hypot(dx, dy)
    # Unit normal biased toward the removed lower-right side, so a +excursion
    # bulges the tear into the yanked triangle and a -excursion bites back into
    # the surviving paper.
    nx, ny = dy / dlen, -dx / dlen

    # Hand-authored asymmetric tear profile: (t along the diagonal, logical
    # excursion off the line). Uneven pitch and mixed excursions with three DEEP
    # bites (+8,-6,+10 → m(3)–m(5)) so no two teeth match — the read is raw fibre,
    # never a uniform scallop. Endpoints sit ON the line so the survivor's top and
    # left corners stay clean.
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

    def punch():
        # Everything lower-right of the seam: down the seam, hook past the
        # bottom-left corner, across the foot and up the right edge.
        poly = seam + [(0, H), (W, H), (W, 0)]
        pygame.draw.polygon(face, (0, 0, 0, 0),
                            [(int(round(x)), int(round(y))) for x, y in poly])

    # 1. rip the lower-right triangle away.
    punch()

    # 2. valley shadow — a warm dark polyline nudged into the surviving paper so
    # it pools behind the crest as the torn lip's self-shadow; the deep troughs
    # get a cooler, darker recess.
    sh = [(x - nx * m(1.1), y - ny * m(1.1)) for x, y in seam]
    pygame.draw.lines(face, (46, 38, 18), False,
                      [(int(round(x)), int(round(y))) for x, y in sh],
                      max(1, m(1.2)))
    for i, off in enumerate(offs):
        if off <= -3 and 0 < i < len(sh) - 1:
            a = sh[i - 1]; b = sh[i + 1]
            pygame.draw.line(face, (9, 9, 22),
                             (int(round(a[0])), int(round(a[1]))),
                             (int(round(b[0])), int(round(b[1]))), max(1, m(1)))

    # 3. fiber-core highlight — a warm bright polyline hugging the crest just
    # inside the torn edge; the out-jutting peaks catch it, giving lit fibre tips.
    hi = [(x - nx * m(0.4), y - ny * m(0.4)) for x, y in seam]
    pygame.draw.lines(face, (255, 240, 190), False,
                      [(int(round(x)), int(round(y))) for x, y in hi],
                      max(1, m(1)))
    for i, off in enumerate(offs):
        if off >= 3.5:                                 # deep out-jutting peak tip
            px, py = hi[i]
            pygame.draw.circle(face, (255, 240, 190),
                               (int(round(px)), int(round(py))), max(1, m(1)))

    # 4. re-punch so any highlight/shadow that spilled past the torn edge is
    # clipped back — the jagged silhouette stays crisp.
    punch()


# ── Panel 0 — UNOWNED (price hang-tag) ────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# ── Panel 1 — EQUIPPED BASE (regalia frame + ✓ tag, reference context) ────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# ── Panel 2 — CONCEPT: diagonal-yank ripped tag ───────────────────────────────
# Suppress the base state_chip so no price/✓ tag lands, then drop the diagonally
# torn tag through the shared hang-tag geometry (cord/knot/grommet intact).
_orig_state_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=False, secret=False, owned=False)
sc.state_chip = _orig_state_chip

sc._draw_hang_tag(p2, rect.centerx, rect.y + sc.m(88) - sc._CHIP_DY,
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

# Zoom panel 2 down to the live card size, then nearest-neighbour 2× back up so
# the diagonal torn seam reads at the resolution the player actually sees.
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
hg = hf.render("owned v2 — diagonal-yank · round 1 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNOWNED (PRICE)", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ DIAGONAL-YANK R1", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_owned_v2", "diagonal_yank", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
