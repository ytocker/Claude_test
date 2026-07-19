#!/usr/bin/env python3
"""Round-2 render for the `top-strip-retained` OWNED card state (store_owned_v2).

Concept unchanged: the priced swing-tag has been RIPPED IN HALF; only the top
header strip survives on the cord (grommet + top bevel intact) so it still reads
as a tag, not a scrap. R2 escalates the tear from "wavy edge" to "violent rip":

  - ~20 seam vertices with tight up-down-up reversals (mean neighbour delta far
    above the legibility floor), including one deep narrow V-notch that bites up
    toward the grommet baseline and one long downward paper TONGUE.
  - an asymmetric hanging strand — a ragged cream finger drooping well below the
    rest of the seam on one side only, the single strongest hand-torn signal.
  - torn-through price ink: the clipped top ~30% of struck price numerals shows
    right at the tear line, drawn BEFORE the punch so the rip clips them exactly
    at the seam — "the priced lower body was ripped away mid-price."
  - fibre-core highlight + valley shadow authored at m(2) width so the lit torn
    lip survives the downscale instead of vanishing as a 1px hairline.

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

KEY_INK = (46, 38, 18)          # valley shadow + torn-through price ink
FIBRE   = (255, 240, 190)       # lit torn-lip fibre core


# Hand-authored asymmetric tear profile: (x-fraction, logical dy off the mean
# seam line). Deliberately tight up/down/up alternation so neighbours reverse
# sign almost every step — the read is a violent rip, never a gentle undulation.
# Two authored landmarks:
#   x≈0.20  dy=-9  a DEEP NARROW V-notch biting up toward the grommet baseline
#   x≈0.72-0.80  the long downward TONGUE / asymmetric hanging strand (+9/+10)
_PROFILE = [
    (0.00, -1), (0.05, +3), (0.10, -3), (0.15, +4),
    (0.20, -9), (0.24, +2), (0.29, -4), (0.34, +5),
    (0.39, -2), (0.44, +4), (0.49, -3), (0.54, +3),
    (0.59, -4), (0.64, +2), (0.70, -2), (0.74, +9),
    (0.79, +10), (0.82, +2), (0.88, -3), (0.93, +4),
    (1.00, -1),
]


def top_strip_face(face):
    """The ripped-tag effect painted onto the (already cream-filled) tag face.

    Order is load-bearing: struck price numerals go down FIRST so the alpha
    punch clips them exactly at the torn seam; the punch then rips the lower
    body away; finally the valley shadow + fibre highlight lay the lit torn lip
    on the surviving edge."""
    W, H = sc._TAG_W, sc._TAG_H            # 81 × 94 at SS=2
    y_mean = int(H * 0.35)                  # header strip survives to ~35% height

    seam = [(fx * (W - 1), y_mean + m(dy)) for fx, dy in _PROFILE]
    dys = [dy for _, dy in _PROFILE]

    # 1. torn-through PRICE INK — struck numerals straddling the seam so only
    # their top ~30% sits above the mean line; everything lower is punched away
    # in step 2, leaving partial digit strokes bitten off at the tear.
    gbase = sc._stamp_bold(sc._glyph_base("1,480", sc.font(15), m(1)), m(0.9))
    ink = gbase.copy()
    ink.fill((*KEY_INK, 255), special_flags=pygame.BLEND_RGBA_MULT)
    gh = ink.get_height()
    face.blit(ink, ((W - ink.get_width()) // 2, y_mean - int(0.30 * gh)))

    # 2. rip the lower body away: fill the region UNDER the jagged seam with
    # zero alpha (down the right edge, across the foot, up the left edge). This
    # is the same RGBA-replacing punch the grommet hole uses — clean, no AA fringe.
    punch = seam + [(W, H), (0, H)]
    pygame.draw.polygon(face, (0, 0, 0, 0), punch)

    # 3. valley shadow — a key-ink band nudged UP into the surviving paper so it
    # pools in the recessed troughs and reads as the torn lip's self-shadow.
    # m(2) wide so it survives the 2× downscale instead of vanishing.
    shadow_pts = [(x, y - m(1.4)) for x, y in seam]
    pygame.draw.lines(face, KEY_INK, False, shadow_pts, max(1, m(2)))

    # 4. fibre-core highlight — a warm bright band riding the torn edge; the
    # down-jutting peaks and the tongue catch the top-left light. m(2) wide.
    pygame.draw.lines(face, FIBRE, False, seam, max(1, m(2)))

    # 5. bias each landmark to its terrain: hotten the deep peak / tongue tips,
    # deepen the deep-trough recesses, so the rip never averages back to a line.
    for (x, y), dy in zip(seam, dys):
        xi = int(x)
        if dy >= 5:                                    # deep peak / tongue tip
            pygame.draw.circle(face, FIBRE, (xi, int(y - m(0.5))), max(1, m(1.4)))
        elif dy <= -4:                                 # deep torn-up trough
            pygame.draw.circle(face, KEY_INK, (xi, int(y - m(1.8))), max(1, m(1.4)))


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
                  draw_face_fn=top_strip_face)


# ── downscale pixel check — the tear must survive the true 1× card size ────────
# Author the seam with the downscale in mind: measure the torn cream edge on an
# isolated face smoothscaled to 1× and confirm real peak-to-peak wobble ≥2px.
def _seam_wobble_check():
    face = pygame.Surface((sc._TAG_W, sc._TAG_H), pygame.SRCALPHA)
    face.blit(sc.vgrad_stops(sc._TAG_W, sc._TAG_H, m(3),
                             [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                             255, gamma=1.04), (0, 0))
    top_strip_face(face)
    w1, h1 = sc._TAG_W // sc.SS, sc._TAG_H // sc.SS
    small = pygame.transform.smoothscale(face, (w1, h1))
    edges = []
    for x in range(w1):
        low = None
        for y in range(h1):
            if small.get_at((x, y))[3] > 40:
                low = y
        if low is not None:
            edges.append(low)
    ptp = (max(edges) - min(edges)) if edges else 0
    deltas = [abs(dys - dyt) for dys, dyt in
              zip([dy for _, dy in _PROFILE][:-1], [dy for _, dy in _PROFILE][1:])]
    mean_delta_ss = (sum(deltas) / len(deltas)) * sc.SS
    print(f"seam: {len(_PROFILE)} vertices | mean neighbour delta "
          f"{mean_delta_ss:.1f} SS-px | 1x edge peak-to-peak {ptp}px")
    return ptp


_wobble = _seam_wobble_check()


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
hg = hf.render("owned v2 — top-strip-retained · round 2 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNOWNED (PRICE)", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ TOP-STRIP RETAINED R2", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label(f"ZOOM · PANEL 2 · 1x edge ptp {_wobble}px", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_owned_v2", "top_strip_retained", "round_2.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
