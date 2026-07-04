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
_DV_FUCHSIA   = (235, 40, 130)     # plume root / fuchsia accent sequin
_DV_FUCHSIA_H = (250, 120, 175)    # fuchsia lift
_DV_GRAPE     = (130, 50, 185)     # boa body
_DV_GRAPE_D   = (86, 30, 128)      # boa shadow / seam under a puff
_DV_GRAPE_H   = (205, 150, 245)    # boa fluff highlight — pushed bright so the
                                   # sky-facing rim reads as lit fluff, not a
                                   # dark blob lost against the blue wing
_DV_GOLD      = (242, 198, 61)     # headband ONLY (gold is off the sequin grid)
_DV_GOLD_H    = (255, 238, 158)    # gold glint
_DV_SILVER    = (210, 215, 220)    # silver sequin
_DV_SILVER_H  = (250, 251, 255)    # heel glint / trim highlight
_DV_SILVER_D  = (150, 154, 168)    # heel shade
_DV_SILVER_P  = (188, 192, 202)    # platform base block
_DV_CREAM     = (255, 246, 238)    # plume tip

# Plume fluff graduates root→tip. Lower nodes stay near-vertical so the feather
# reads as a tall spike rooted at the crown; only the top two nodes sweep back,
# giving the swept-tip flick that says "showgirl plume". (dx, dy, radius, colour)
# off the crown anchor.
_DV_PLUME = [
    (0,  -1, 4, _DV_FUCHSIA),
    (-1, -6, 4, _DV_FUCHSIA_H),
    (-1, -11, 4, (252, 168, 200)),
    (-2, -16, 3, (254, 214, 226)),
    (-5, -21, 3, _DV_CREAM),
    (-9, -25, 3, _DV_CREAM),
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
        # A bright lit scallop on the sky-facing (up-left) rim of each puff —
        # this crescent of light is what separates the boa from the blue wing
        # and reads as soft feathers at 40px instead of one merged blob.
        pygame.draw.circle(surf, _DV_GRAPE_H, (bx - 1, by - 2), max(1, br - 1))
        pygame.draw.circle(surf, _DV_GRAPE, (bx, by), max(1, br - 2))
        pygame.draw.circle(surf, (255, 255, 255), (bx - 1, by - 2), 1)

    # Sequinned halter jumpsuit — one dominant hue reads as an organised
    # shimmer field, not multi-hue static noise. Silver dots on simple diagonal
    # rows carry a scattered 1px white glint so the shimmer survives the shrink;
    # only a couple of fuchsia accents break the field so it stays a costume,
    # not a colour salad. Gold is deliberately absent — reserved for the band.
    fuchsia_accents = {(37, 47), (33, 55), (43, 51)}   # sparse hot pops only
    n = 0
    for row, cy in enumerate(range(43, 62, 4)):
        x0 = 29 + (row % 2) * 3      # shift alternate rows → clean diagonal runs
        for cx in range(x0, 47, 6):
            if (cx, cy) in fuchsia_accents:
                pygame.draw.circle(surf, _DV_FUCHSIA, (cx, cy), 1)
            else:
                pygame.draw.circle(surf, _DV_SILVER, (cx, cy), 1)
                if n % 3 == 0:       # scattered facet glints = the shimmer
                    pygame.draw.circle(surf, (255, 255, 255),
                                       (cx - 1, cy - 1), 1)
            n += 1

    # Deep halter V-neckline — a SINGLE converging silver line for the plunge so
    # the sequin field beside it can breathe; a double line + gold dot crowded
    # the same tiny chest zone and fought the shimmer for attention.
    vx, vy = 39, 54                  # V point at chest centre
    pygame.draw.line(surf, _DV_SILVER, (33, 43), (vx, vy), 1)
    pygame.draw.line(surf, _DV_SILVER, (45, 42), (vx, vy), 1)

    # Jewelled glitter headband at brow level — a thin gold strip across the
    # forehead with two set jewels, the horizontal band that grounds the plume.
    hb_y = HY - 4
    pygame.draw.line(surf, _DV_GOLD, (HX - 11, hb_y + 1), (HX + 10, hb_y - 1), 3)
    pygame.draw.line(surf, _DV_GOLD_H, (HX - 9, hb_y), (HX + 2, hb_y - 1), 1)
    for jx, jc in ((HX - 6, _DV_FUCHSIA), (HX + 4, _DV_SILVER)):
        pygame.draw.circle(surf, jc, (jx, hb_y), 2)
        pygame.draw.circle(surf, (255, 255, 255), (jx - 1, hb_y - 1), 1)

    # Tall ostrich plume off the crown — a vertical spike whose lower two-thirds
    # stand near-straight and whose tip flicks back, the hero shape that breaks
    # the silhouette dramatically upward and screams "showgirl" at any size. A
    # dark fuchsia quill threads the fluff so the spike reads as one feather; the
    # tip cools to cream so it still lands cleanly on night sky.
    ax, ay = HX, CROWN_Y
    quill = [(ax + dx, ay + dy) for dx, dy, _r, _c in _DV_PLUME]
    pygame.draw.lines(surf, _DV_GRAPE_D, False, [(ax + 1, ay + 2)] + quill, 2)
    for dx, dy, r, col in _DV_PLUME:
        px, py = ax + dx, ay + dy
        pygame.draw.circle(surf, col, (px, py), r)
        pygame.draw.circle(surf, (255, 255, 255), (px - 1, py - 1), 1)
    # A tiny sparkle off the swept plume tip so the diva always catches a light.
    _spark(surf, ax - 10, ay - 27, 2, (255, 255, 255))

    # Strappy silver platform heels — a shoe box + a distinct wide platform base
    # block under each foot so "platform" reads as footwear, not a bright pixel
    # cluster. Beefed ~1px wider than R1 with a brighter top glint, plus an
    # ankle strap so they still ID as heels, not clogs, and break the lower
    # silhouette just past the feet.
    for fx in (24, 32):
        pygame.draw.line(surf, _DV_SILVER, (fx + 3, 68), (fx + 3, 72), 1)  # ankle strap
        pygame.draw.rect(surf, _DV_SILVER, (fx, 72, 7, 4))                 # shoe upper
        pygame.draw.line(surf, _DV_SILVER_H, (fx, 72), (fx + 6, 72), 1)    # bright top glint
        pygame.draw.rect(surf, _DV_SILVER_P, (fx - 1, 76, 9, 3))           # platform base block
        pygame.draw.line(surf, _DV_SILVER_D, (fx - 1, 78), (fx + 7, 78), 1)  # base shade


build = _make_skin(_paint_diva, base_fn=_build_frame)
