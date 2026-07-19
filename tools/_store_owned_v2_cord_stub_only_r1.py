#!/usr/bin/env python3
"""Round-1 render for the `cord-stub-only` OWNED card state (store_owned_v2).

Concept: the whole swing-tag is GONE — ripped clean off. Only the cord + knot
survive (drawn pixel-identical to the priced state), with a tiny torn cream nub
(~8×6 device px) still crimped in the knot, plus 3–4 fiber whiskers fraying from
its underside. Maximum restraint — the near-absence itself reads "ripped clean
off", so nothing but the cord, knot, a scrap of paper, and stray fibers remain.

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


def draw_cord_stub(surf):
    """Cord + knot pixel-identical to the priced tag, but with the tag face torn
    clean away — only a scrap of cream paper crimped in the knot survives.

    The cord/knot geometry is replicated exactly from `_draw_hang_tag` (same
    fixed 324×200 anchors, same grommet-point cord fan, same knot disc + glint
    pip) so the surviving hardware lands in the identical spot the tag used to.
    Draw order stakes the read: whiskers first so the nub covers their roots,
    then the nub, then the knot disc on top so the knot visibly clamps the
    scrap's upper edge."""
    grommet    = (30, 13)
    tag_center = (44, 60)
    knot       = (22, 13)
    cord       = (190, 165, 115)
    gx, gy = sc._tag_rot_point(*grommet, tag_center)
    lw = m(1.5)

    # — the two cord strokes fanning from the (now empty) grommet point up to the
    #   knot, exactly as the intact tag draws them.
    pygame.draw.line(surf, cord, (gx, gy), (knot[0] - 1, knot[1] - 1), lw)
    pygame.draw.line(surf, cord, (gx, gy), (knot[0] + 2, knot[1] + 2), lw)

    # — fiber whiskers fray from the scrap's underside; drawn first so the nub
    #   caps their roots and they read as strands escaping from beneath it. Key
    #   ink, single device-px, unequal lengths + angles so none reads combed.
    key = (46, 38, 18)
    whiskers = [
        ((20.0, 21.0), (18.0, 27.5)),
        ((21.0, 22.0), (21.8, 30.0)),
        ((22.4, 21.5), (24.2, 26.5)),
        ((21.4, 22.0), (19.8, 25.0)),
    ]
    for a, b in whiskers:
        pygame.draw.line(surf, key, a, b, 1)

    # — the torn scrap: a lopsided 6-vertex polygon (no two edges parallel) so it
    #   reads as a bitten-off nub, never a neat bead. Tucked under the knot.
    cream = (248, 238, 210)
    nub = [
        (18.5, 17.5),   # top-left
        (22.0, 16.0),   # top, bitten up into the knot
        (25.5, 17.0),   # top-right
        (24.5, 20.5),   # right
        (21.0, 22.0),   # bottom point — whisker origin
        (17.5, 20.0),   # left
    ]
    pygame.draw.polygon(surf, cream, nub)

    # — fiber-lit highlight along the scrap's upper edge, self-shadow along its
    #   lower edge: 1px polylines that give the paper a torn top-left-lit relief.
    pygame.draw.lines(surf, (255, 240, 190), False, nub[0:3], 1)
    pygame.draw.lines(surf, (46, 38, 18), False, nub[2:6], 1)

    # — the knot disc + glint pip land LAST so the knot pinches the scrap's top,
    #   crimping it in place; copied exactly from the intact-tag draw.
    pygame.draw.circle(surf, cord, knot, m(1.5))
    pygame.draw.circle(surf, (min(cord[0] + 30, 255), min(cord[1] + 30, 255),
                              min(cord[2] + 30, 255)), knot, max(1, m(0.6)))


# ── Panel 0 — UNOWNED (price hang-tag) ────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# ── Panel 1 — EQUIPPED BASE (regalia frame + ✓ tag, reference context) ────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# ── Panel 2 — CONCEPT: cord-stub-only chip ────────────────────────────────────
# Suppress the base state_chip so no price/✓ tag lands, then drop the surviving
# cord + knot + torn nub through the replicated hang-tag geometry.
_orig_state_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=False, secret=False, owned=False)
sc.state_chip = _orig_state_chip

draw_cord_stub(p2)


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
# the surviving cord/knot/scrap read at the resolution the player actually sees.
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
hg = hf.render("owned v2 — cord-stub-only · round 1 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNOWNED (PRICE)", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ CORD-STUB-ONLY R1", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_owned_v2", "cord_stub_only", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
