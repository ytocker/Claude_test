#!/usr/bin/env python3
"""Round-2 render for the `cord-stub-only` OWNED card state (store_owned_v2).

RE-ROLL from R1: R1's ~7×5 device-px cream nub collapsed to an invisible speck
at display scale, and the scrap sat on the wrong end (the knot). R2 builds the
MINIMUM LEGIBLE TORN STUB instead — the smallest paper remnant that still reads
as ripped at 40px display:

  • a ~25 device-px tall cream strip hanging from the GROMMET end (where paper
    physically tears when a swing-tag is yanked off), not the knot;
  • the RIP lives in the SILHOUETTE — a sawtooth bottom edge whose triangular
    teeth are large enough to survive one downscale (the only detail that reads
    as "torn" at 1×; surface texture would wash out);
  • a notch cut up under the grommet so the shared full ring's lower arc floats
    over the tear = a ruptured/torn-through grommet read;
  • fiber-lit peaks + valley shadow so the torn edge has relief;
  • 2 longer fray whiskers (one cream, one dark) — few enough to read as fibers,
    not dirt.

Cord + knot + grommet POSITION stay pixel-identical to the priced tag by routing
through `sc._draw_hang_tag`. Headless review render; ships nothing."""
import os, sys
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


def cord_stub_face(face):
    """Draw the torn-stub tag face on the shared cream `_TAG_W×_TAG_H` surface.

    The shared `_draw_hang_tag` punches the grommet hole + draws its full metal
    ring AFTER this fn, so the ruptured read is engineered by CUTTING the paper:
    a notch rises up under the grommet, and when the shared ring's lower arc then
    lands over that torn (transparent) gap it floats = the grommet tore through.
    The tear is authored in the SILHOUETTE (a sawtooth cut) because at 40px only
    a jagged outline survives downscale — a painted-on tear would wash out."""
    W, H = sc._TAG_W, sc._TAG_H            # 81 × 94 device px

    # Sawtooth tear profile across the full width. Downward-pointing triangular
    # teeth (tips BELOW the general cut line) give the hanging jagged silhouette;
    # the x=28 notch rises into the grommet's lower half for the ruptured read.
    # Irregular tip depths/valley heights so it reads torn, never pinked/serrated.
    profile = [
        (0,  19),
        (10, 26),   # tooth A tip
        (19, 18),   # valley
        (28, 15),   # grommet notch — cuts up under the ring
        (37, 21),   # tooth B tip (short)
        (45, 17),   # valley
        (53, 27),   # tooth C tip (deepest)
        (62, 18),   # valley
        (71, 25),   # tooth D tip
        (81, 20),
    ]

    # Cut everything below the tear line to alpha 0. Drawing a hard-edged polygon
    # in fully-transparent colour REPLACES those pixels on the SRCALPHA face, so
    # the surviving silhouette is exactly the jagged top strip (no AA feather
    # to soften the teeth away on downscale).
    cutter = profile + [(W, H), (0, H)]
    pygame.draw.polygon(face, (0, 0, 0, 0), cutter)

    # Torn-edge relief: a bright fiber-lit core riding one px above the cut, over
    # a dark valley shadow on the cut itself. Two stacked 1px polylines read as
    # lit torn paper fibres above their own micro-shadow at every tooth.
    hi = [(x, y - 1) for x, y in profile]
    pygame.draw.lines(face, (255, 240, 190), False, hi, 1)
    pygame.draw.lines(face, (46, 38, 18), False, profile, 1)

    # Two longer fray whiskers escaping the torn edge — single device-px strands
    # at unequal angles/lengths so they read as loose fibre, not grime. Drawn from
    # the deepest tips down into the (now transparent) region below the tear.
    pygame.draw.line(face, (246, 244, 232), (10, 26), (5, 35), 1)    # cream fibre
    pygame.draw.line(face, (60, 50, 30),    (53, 27), (60, 37), 1)   # dark fibre


# ── Panel 0 — UNOWNED (price hang-tag) ────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# ── Panel 1 — EQUIPPED BASE (regalia frame + ✓ tag, reference context) ────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# ── Panel 2 — CONCEPT: cord-stub-only R2 torn stub ────────────────────────────
# Suppress the base state_chip so no ✓ tag lands (the regalia frame still draws
# from the equipped path), restore, then route the torn stub through the shared
# hang-tag geometry so cord + knot + grommet POSITION stay pixel-identical.
_orig_state_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
sc.state_chip = _orig_state_chip

sc._draw_hang_tag(p2, 0, 0, draw_face_fn=cord_stub_face)


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
# the torn silhouette reads at the true resolution the player sees — this strip
# is the judge of whether the teeth survive downscale.
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
hg = hf.render("owned v2 — cord-stub-only · round 2 · min legible torn stub · skin_mummy",
               True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNOWNED (PRICE)", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ CORD-STUB-ONLY R2 (torn stub)", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2 (1× READ)", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_owned_v2", "cord_stub_only", "round_2.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
