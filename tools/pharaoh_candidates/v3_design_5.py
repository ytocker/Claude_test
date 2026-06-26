"""v3 DESIGN 5 — THE ADORNED SOVEREIGN (scratch builder).

ENRICH pass on the shipped PHARAOH: the gold+lapis striped nemes + gold uraeus
are rebuilt UNCHANGED (the identity core), then royal heraldry is layered on so
it reads as the SAME pharaoh, just richer/heraldic. Hero read = the twin "Two
Ladies" (nebty) brow emblems (uraeus cobra + vulture head) plus a fat-disc
shebyu collar; a chest sash carries a small cartouche name-ring; gold anklets.

Footprint law: every body ornament stays inside the base bird footprint —
nothing below the feet line (~HY+24..28), nothing balloons the body. Only the
nemes + the two brow emblems rise above CROWN_Y.

Scratch only — never registered in store_skins.BUILDERS.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Identity-core nemes/uraeus tones reused verbatim from _PH_* so the headdress
# is the SAME gold+lapis pharaoh, not a recolour.
_AS_GOLD   = (244, 196, 48)        # #F4C430 royal gold
_AS_GOLD_D = (188, 142, 34)        # gold shadow / disc separation
_AS_GOLD_H = (255, 238, 158)       # gold glint
_AS_LAPIS  = (27, 58, 140)         # #1B3A8C lapis (nemes blue / collar inlay)
_AS_LAPIS_D = (18, 40, 100)        # lapis shadow
_AS_TURQ   = (47, 184, 166)        # #2FB8A6 turquoise accent bead
_AS_WHITE  = (237, 233, 221)       # #EDE9DD vulture white
_AS_WHITE_D = (196, 190, 174)      # vulture white shadow
_AS_GLYPH  = (40, 30, 18)          # cartouche glyph ticks
_AS_EYE    = (208, 52, 52)         # uraeus eye / vulture eye scarlet


def _paint(surf, _a):
    cy = CROWN_Y

    # ── IDENTITY CORE: gold+lapis striped nemes + uraeus (rebuilt unchanged) ──
    # Side lappet — striped cloth falling beside the head.
    lappet = [(HX - 13, cy + 2), (HX - 5, cy + 2), (HX - 4, HY + 16),
              (HX - 12, HY + 16)]
    pygame.draw.polygon(surf, _AS_GOLD, lappet)
    for i in range(3):
        x = HX - 12 + i * 3
        col = _AS_LAPIS if i % 2 == 0 else _AS_GOLD_D
        pygame.draw.line(surf, col, (x, cy + 3), (x + 1, HY + 15), 2)
    pygame.draw.polygon(surf, _AS_GOLD_D, lappet, 1)

    # Domed headcloth cap over the crown.
    pygame.draw.ellipse(surf, _AS_GOLD_D, (HX - 13, cy - 5, 27, 18))
    pygame.draw.ellipse(surf, _AS_GOLD, (HX - 12, cy - 5, 25, 15))
    for i in range(-3, 4):
        x = HX + i * 3
        col = _AS_LAPIS if i % 2 == 0 else _AS_GOLD_D
        pygame.draw.line(surf, col, (x, cy - 4), (x, cy + 6), 2)
    # Front headband.
    pygame.draw.line(surf, _AS_LAPIS_D, (HX - 12, cy + 5), (HX + 13, cy + 4), 4)
    pygame.draw.line(surf, _AS_LAPIS, (HX - 12, cy + 4), (HX + 13, cy + 3), 2)
    pygame.draw.ellipse(surf, _AS_GOLD_H, (HX - 5, cy - 4, 8, 3))

    # ── SHEBYU COLLAR — 2 rows of FAT gold discs across the chest. Bolder and
    #    rounder than a bead collar; the lower body hero. Drawn before the brow
    #    emblems so the head/uraeus overlap cleanly. Arc follows the breast.
    row_y = (HY + 13, HY + 19)
    row_xs = (range(-3, 4), range(-3, 4))
    for ry, xr in zip(row_y, row_xs):
        for i in xr:
            dx = HX + i * 5
            # Arc the row down at the edges so the collar hugs the breast.
            dy = ry + abs(i) * abs(i) // 3
            pygame.draw.circle(surf, _AS_GOLD_D, (dx, dy + 1), 4)
            pygame.draw.circle(surf, _AS_GOLD, (dx, dy), 3)
            pygame.draw.circle(surf, _AS_GOLD_H, (dx - 1, dy - 1), 1)
    # Thin lapis spacer line between the two disc rows for depth.
    pygame.draw.line(surf, _AS_LAPIS, (HX - 14, HY + 16), (HX + 13, HY + 16), 1)

    # ── SASH down the body bearing a CARTOUCHE name-ring. A narrow gold band
    #    drops from the collar toward (but not past) the feet line; a clean
    #    oval cartouche with 2-3 dark glyph ticks rides on it.
    sx = HX - 4
    pygame.draw.line(surf, _AS_GOLD_D, (sx, HY + 21), (sx - 1, HY + 23), 5)
    pygame.draw.line(surf, _AS_GOLD, (sx, HY + 21), (sx - 1, HY + 23), 3)
    # Cartouche — a small clean oval ring (gold) with a flat tie-bar at the base.
    ccx, ccy = sx - 1, HY + 22
    pygame.draw.ellipse(surf, _AS_GOLD_D, (ccx - 5, ccy - 4, 11, 9))
    pygame.draw.ellipse(surf, _AS_LAPIS_D, (ccx - 4, ccy - 3, 9, 7))
    pygame.draw.ellipse(surf, _AS_GOLD, (ccx - 4, ccy - 3, 9, 7), 1)
    pygame.draw.line(surf, _AS_GOLD, (ccx - 4, ccy + 4), (ccx + 4, ccy + 4), 2)
    # Two clean glyph ticks inside — kept minimal so they don't fuss at 40px.
    pygame.draw.line(surf, _AS_GLYPH, (ccx - 1, ccy - 2), (ccx - 1, ccy + 1), 1)
    pygame.draw.circle(surf, _AS_GLYPH, (ccx + 1, ccy + 1), 1)

    # ── GOLD ANKLETS at the feet line — short bright bands, inside footprint.
    for fx in (27, 34):
        pygame.draw.line(surf, _AS_GOLD_D, (fx - 2, HY + 23), (fx + 2, HY + 23), 3)
        pygame.draw.line(surf, _AS_GOLD, (fx - 2, HY + 22), (fx + 2, HY + 22), 2)
        pygame.draw.circle(surf, _AS_GOLD_H, (fx, HY + 22), 1)

    # ── TWIN BROW EMBLEMS — the HERO read. The uraeus cobra (rebuilt unchanged)
    #    paired with a vulture head: the "Two Ladies" (nebty) of Upper + Lower
    #    Egypt. Both rear above the brow so they own the silhouette at 40px.

    # Uraeus cobra — pulled slightly left so the vulture sits beside it.
    bx = HX - 3
    pygame.draw.line(surf, _AS_GOLD_D, (bx, cy + 1), (bx - 1, cy - 9), 4)
    pygame.draw.line(surf, _AS_GOLD, (bx, cy + 1), (bx - 1, cy - 9), 2)
    pygame.draw.polygon(surf, _AS_GOLD,
                        [(bx - 4, cy - 8), (bx + 4, cy - 8), (bx, cy - 13)])
    pygame.draw.polygon(surf, _AS_GOLD_H,
                        [(bx - 2, cy - 9), (bx + 2, cy - 9), (bx, cy - 12)])
    pygame.draw.circle(surf, _AS_GOLD_H, (bx, cy - 12), 2)
    pygame.draw.circle(surf, _AS_EYE, (bx, cy - 12), 1)

    # Vulture head beside the cobra — gold neck rising to a white head with a
    # hooked gold beak. Bold gold + white so the twin emblem reads at 40px.
    vx = HX + 4
    pygame.draw.line(surf, _AS_GOLD_D, (vx, cy + 1), (vx + 1, cy - 7), 4)
    pygame.draw.line(surf, _AS_GOLD, (vx, cy + 1), (vx + 1, cy - 7), 2)
    # White head.
    pygame.draw.circle(surf, _AS_WHITE_D, (vx + 2, cy - 9), 4)
    pygame.draw.circle(surf, _AS_WHITE, (vx + 1, cy - 10), 3)
    # Hooked gold beak curving forward/down.
    pygame.draw.polygon(surf, _AS_GOLD_D,
                        [(vx + 4, cy - 10), (vx + 8, cy - 8), (vx + 4, cy - 7)])
    pygame.draw.polygon(surf, _AS_GOLD,
                        [(vx + 4, cy - 10), (vx + 7, cy - 9), (vx + 4, cy - 8)])
    # Dark eye dot.
    pygame.draw.circle(surf, _AS_EYE, (vx + 1, cy - 10), 1)


build = store_skins._make_skin(_paint)
