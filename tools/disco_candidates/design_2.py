"""DISCO candidate 2 — STARDUST DIVA (Studio 54 peak-glam showgirl).

Scratch exploration builder only: it layers a showgirl costume over the
UNRECOLOURED scarlet macaw (red head / blue wings / yellow beak stay
visible) so the glamour reads as worn-on-top, not a re-plumage. The read at
40px is a tall plumed silhouette — the ostrich feather is the vertical spike
that IDs "diva" instantly — over a sequinned halter and a fluffy boa.

Not registered in store_skins.BUILDERS; rendered via tools/ninja_render.py.
"""
import sys, os
sys.path.insert(0, '/home/user/skybit')

import pygame

from game.store_skins import (
    _make_skin, _poly, _spark, HX, HY, CROWN_Y,
    COMPOSITE_W, COMPOSITE_H, PARROT_DY,
)
from game.parrot import _build_frame


# Concept palette (fuchsia / grape / gold / silver) plus the value steps a
# shape needs to read round at 40px — a plume or a sequin only survives the
# downscale if it carries its own light-to-dark range instead of one flat fill.
_DV_FUCHSIA   = (235, 40, 130)     # plume root / hot sequin
_DV_FUCHSIA_H = (250, 120, 175)    # fuchsia lift
_DV_GRAPE     = (130, 50, 185)     # boa body
_DV_GRAPE_D   = (86, 30, 128)      # boa shadow / seam under a puff
_DV_GRAPE_H   = (178, 110, 224)    # boa fluff highlight
_DV_GOLD      = (242, 198, 61)     # headband / gold sequin
_DV_GOLD_H    = (255, 238, 158)    # gold glint
_DV_SILVER    = (217, 220, 230)    # silver sequin / platform heel
_DV_SILVER_H  = (250, 251, 255)    # heel glint
_DV_SILVER_D  = (150, 154, 168)    # heel shade
_DV_CREAM     = (255, 246, 238)    # plume tip

# Plume fluff graduates root→tip so the feather reads as one curved spike, not
# a stack of dots; each entry is (dx, dy, radius, colour) off the crown anchor.
_DV_PLUME = [
    (0,  -1, 4, _DV_FUCHSIA),
    (-2, -7, 4, _DV_FUCHSIA_H),
    (-5, -12, 4, (252, 168, 200)),
    (-7, -16, 3, (254, 214, 226)),
    (-8, -20, 3, _DV_CREAM),
]


def _paint_diva(surf, _a):
    # Feather boa FIRST, scalloped along the neck/chest edge that faces the
    # sky, so the body's front contour reads as fluff and the later sequins /
    # V-neck sit on top of it. Grape with a shadow seam under each puff + a lit
    # crown keeps the fluff round instead of a flat purple blob at 40px.
    boa = [(48, 40, 4), (47, 44, 4), (44, 48, 4),
           (41, 52, 4), (37, 55, 3), (33, 57, 3)]
    for bx, by, br in boa:
        pygame.draw.circle(surf, _DV_GRAPE_D, (bx, by + 1), br)
        pygame.draw.circle(surf, _DV_GRAPE, (bx, by), br)
        pygame.draw.circle(surf, _DV_GRAPE_H, (bx - 1, by - 1), max(1, br - 2))

    # Sequinned halter jumpsuit — a diamond grid of tiny facet dots across the
    # torso in alternating fuchsia / silver / gold. A diamond (offset) layout
    # reads as sewn sequins catching light; a couple carry a 1px white glint so
    # the "shimmer" survives the shrink where a flat dot would mud out.
    seq_cols = (_DV_FUCHSIA, _DV_SILVER, _DV_GOLD)
    n = 0
    for row, cy in enumerate(range(43, 62, 4)):
        x0 = 29 + (row % 2) * 2      # offset alternate rows → diamond grid
        for cx in range(x0, 47, 5):
            col = seq_cols[n % 3]
            pygame.draw.circle(surf, col, (cx, cy), 1)
            if n % 4 == 0:           # scattered facet glints = the shimmer
                pygame.draw.circle(surf, (255, 255, 255),
                                   (cx - 1, cy - 1), 1)
            n += 1

    # Deep halter V-neckline — two silver trim lines converging at chest centre
    # so the sequin field reads as a plunging jumpsuit, not just scattered dots.
    vx, vy = 39, 53                  # V point at chest centre
    pygame.draw.line(surf, _DV_SILVER, (32, 43), (vx, vy), 1)
    pygame.draw.line(surf, _DV_SILVER, (46, 42), (vx, vy), 1)
    pygame.draw.circle(surf, _DV_GOLD_H, (vx, vy), 1)

    # Jewelled glitter headband at brow level — a thin gold strip across the
    # forehead with two set jewels, the horizontal band that grounds the plume.
    hb_y = HY - 4
    pygame.draw.line(surf, _DV_GOLD, (HX - 11, hb_y + 1), (HX + 10, hb_y - 1), 3)
    pygame.draw.line(surf, _DV_GOLD_H, (HX - 9, hb_y), (HX + 2, hb_y - 1), 1)
    for jx, jc in ((HX - 6, _DV_FUCHSIA), (HX + 4, _DV_SILVER)):
        pygame.draw.circle(surf, jc, (jx, hb_y), 2)
        pygame.draw.circle(surf, (255, 255, 255), (jx - 1, hb_y - 1), 1)

    # Tall ostrich plume curving up-and-BACK off the crown — the hero shape that
    # breaks the silhouette dramatically upward and screams "showgirl" at any
    # size. A dark fuchsia quill threads the fluff so the curve reads as one
    # feather; the tip cools to cream so the spike still lands on night sky.
    ax, ay = HX, CROWN_Y
    quill = [(ax + dx, ay + dy) for dx, dy, _r, _c in _DV_PLUME]
    pygame.draw.lines(surf, _DV_GRAPE_D, False, [(ax + 1, ay + 2)] + quill, 2)
    for dx, dy, r, col in _DV_PLUME:
        px, py = ax + dx, ay + dy
        pygame.draw.circle(surf, col, (px, py), r)
        pygame.draw.circle(surf, (255, 255, 255), (px - 1, py - 1), 1)
    # A tiny sparkle off the plume tip so the diva always catches a light.
    _spark(surf, ax - 9, ay - 23, 2, (255, 255, 255))

    # Strappy silver platform heels at the base — a bright shoe box + a wedge
    # sole under each foot, with a thin strap up to the ankle so they read as
    # heels, not blocks, and break the lower silhouette just past the feet.
    for fx in (25, 33):
        pygame.draw.line(surf, _DV_SILVER, (fx + 3, 68), (fx + 3, 72), 1)  # ankle strap
        pygame.draw.rect(surf, _DV_SILVER, (fx, 72, 6, 4))                 # shoe
        pygame.draw.line(surf, _DV_SILVER_H, (fx, 72), (fx + 5, 72), 1)    # top glint
        _poly(surf, _DV_SILVER_D, [(fx, 76), (fx + 6, 76),
                                   (fx + 5, 78), (fx + 1, 78)])            # wedge sole


build = _make_skin(_paint_diva, base_fn=_build_frame)
