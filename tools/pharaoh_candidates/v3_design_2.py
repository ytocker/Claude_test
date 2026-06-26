"""v3 DESIGN 2 — THE JEWELED PHARAOH (scratch exploration).

ENRICH pass on the live PHARAOH: keep the gold+lapis striped nemes + gold
uraeus brow cobra UNCHANGED (rebuilt verbatim from store_skins._paint_pharaoh)
so it reads as the SAME pharaoh, then layer jeweled regalia so it reads richer:
a jeweled chest PECTORAL (the hero), a gold wing armlet + wrist cuff, a
gem-studded brow band lifting the nemes front, and gold anklets.

Scratch only — wrapped by store_skins._make_skin, NEVER registered in BUILDERS.
Footprint law: all body jewelry stays inside the base bird footprint; only the
nemes rises above CROWN_Y.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Identity core (verbatim from the live pharaoh nemes/uraeus).
_PH_GOLD   = (245, 200, 70)
_PH_GOLD_D = (190, 145, 35)
_PH_GOLD_H = (255, 240, 160)
_PH_BLUE   = (44, 100, 188)
_PH_BLUE_D = (26, 64, 128)

# Jeweled regalia palette (brief): gold / carnelian / turquoise / lapis on the
# kept scarlet body. Each gem carries a dark seat + a bright facet so the inlay
# survives the 40px downscale on day AND night.
_JW_GOLD    = (244, 196, 48)       # #F4C430 regalia gold
_JW_GOLD_D  = (176, 130, 30)       # gold shadow / chasing
_JW_GOLD_H  = (255, 236, 150)      # gold facet glint
_JW_CARN    = (193, 69, 59)        # #C1453B carnelian
_JW_CARN_H  = (231, 120, 104)      # carnelian facet
_JW_TURQ    = (47, 184, 166)       # #2FB8A6 turquoise
_JW_TURQ_H  = (138, 230, 216)      # turquoise facet
_JW_LAPIS   = (27, 58, 140)        # #1B3A8C lapis
_JW_LAPIS_H = (86, 126, 220)       # lapis facet / scarab glow core


def _gem(surf, cx, cy, r, base, hi):
    """A round cabochon: dark gold seat, gem body, one bright off-centre facet —
    the three values keep an inlaid stone reading after the downscale."""
    pygame.draw.circle(surf, _JW_GOLD_D, (cx, cy), r + 1)
    pygame.draw.circle(surf, base, (cx, cy), r)
    pygame.draw.circle(surf, hi, (cx - 1, cy - 1), max(1, r - 2))


def _paint(surf, _a):
    cy = CROWN_Y

    # ── JEWELED PECTORAL (the HERO) ──────────────────────────────────────────
    # Painted first so the chain swag tucks under the nemes lappet that falls
    # over it. A broad gold chain swag arcs across the upper breast, dipping to
    # the medallion; the medallion is a clear gold disc carrying a central blue
    # scarab flanked by carnelian + turquoise inlay so it pops as ONE bold jewel
    # at 40px. Whole thing sits inside the body footprint (top ~HY+9, base
    # ~HY+22) — never balloons the body, never hangs below the feet.
    px, py = HX - 12, HY + 18            # medallion centre, on the chest
    swag = [(HX - 22, HY + 9), (px, HY + 14), (HX - 1, HY + 9)]
    pygame.draw.lines(surf, _JW_GOLD_D, False,
                      [(x, y + 1) for x, y in swag], 3)
    pygame.draw.lines(surf, _JW_GOLD, False, swag, 2)
    pygame.draw.lines(surf, _JW_GOLD_H, False,
                      [(swag[0][0] + 1, swag[0][1]), (px, HY + 13)], 1)
    # Two short hanger links dropping from the swag to the medallion crown.
    pygame.draw.line(surf, _JW_GOLD_D, (px, HY + 13), (px, HY + 16), 3)
    pygame.draw.line(surf, _JW_GOLD, (px, HY + 13), (px, HY + 16), 1)

    # Medallion disc — gold rim, lapis field (so the scarab + side gems pop on a
    # cool ground), then the inlay row.
    pygame.draw.circle(surf, _JW_GOLD_D, (px, py), 9)
    pygame.draw.circle(surf, _JW_GOLD, (px, py), 8)
    pygame.draw.circle(surf, _JW_LAPIS, (px, py), 6)
    pygame.draw.arc(surf, _JW_GOLD_H, (px - 8, py - 8, 16, 16), 0.5, 2.4, 1)
    # Flanking inlay: carnelian on the body side, turquoise on the wing side.
    _gem(surf, px - 4, py, 2, _JW_CARN, _JW_CARN_H)
    _gem(surf, px + 4, py, 2, _JW_TURQ, _JW_TURQ_H)
    # Central blue scarab — fat oval carapace, a split wing-case seam, a small
    # head nub, and a glow core so it reads as the hero stone day and night.
    pygame.draw.ellipse(surf, _JW_LAPIS_H, (px - 3, py - 4, 6, 8))
    pygame.draw.ellipse(surf, _JW_LAPIS, (px - 2, py - 3, 4, 6))
    pygame.draw.line(surf, _JW_LAPIS_H, (px, py - 3), (px, py + 2), 1)
    pygame.draw.circle(surf, _JW_GOLD_H, (px, py - 4), 1)        # gilded head
    pygame.draw.circle(surf, _JW_LAPIS_H, (px - 1, py - 1), 1)   # facet glint
    # Three tiny gold bead drops along the medallion bottom — the pectoral fringe.
    for dx in (-4, 0, 4):
        pygame.draw.circle(surf, _JW_GOLD, (px + dx, py + 9), 1)

    # ── NEAR-WING ARMLET + WRIST CUFF ────────────────────────────────────────
    # A gold band across the near wing root (armlet) with one inlaid turquoise
    # stud, and a chunkier wrist cuff lower on the same wing with a carnelian
    # stud — both hug the wing inside the footprint so nothing widens the body.
    pygame.draw.line(surf, _JW_GOLD_D, (HX - 24, HY + 13), (HX - 18, HY + 11), 5)
    pygame.draw.line(surf, _JW_GOLD, (HX - 24, HY + 13), (HX - 18, HY + 11), 3)
    pygame.draw.line(surf, _JW_GOLD_H, (HX - 23, HY + 12), (HX - 19, HY + 10), 1)
    _gem(surf, HX - 21, HY + 12, 2, _JW_TURQ, _JW_TURQ_H)

    pygame.draw.line(surf, _JW_GOLD_D, (HX - 26, HY + 21), (HX - 19, HY + 19), 6)
    pygame.draw.line(surf, _JW_GOLD, (HX - 26, HY + 21), (HX - 19, HY + 19), 4)
    pygame.draw.line(surf, _JW_GOLD_H, (HX - 25, HY + 20), (HX - 20, HY + 18), 1)
    _gem(surf, HX - 22, HY + 20, 2, _JW_CARN, _JW_CARN_H)

    # ── GOLD ANKLETS ─────────────────────────────────────────────────────────
    # Thin gold bands at the feet line (~HY+24) — at the bottom of the footprint,
    # never below it. A bright top edge keeps them off a dark night floor.
    for fx in (HX - 19, HX - 13):
        pygame.draw.line(surf, _JW_GOLD_D, (fx, HY + 25), (fx + 5, HY + 25), 3)
        pygame.draw.line(surf, _JW_GOLD, (fx, HY + 24), (fx + 5, HY + 24), 2)
        pygame.draw.line(surf, _JW_GOLD_H, (fx + 1, HY + 23), (fx + 4, HY + 23), 1)

    # ─────────────────────────────────────────────────────────────────────────
    # IDENTITY CORE — the live pharaoh nemes + uraeus, rebuilt verbatim so this
    # still reads as the SAME pharaoh. Painted AFTER the chest so the lappet
    # overlaps the pectoral swag, and the brow band slots under the headband.
    # ─────────────────────────────────────────────────────────────────────────
    # Side lappet — striped cloth falling beside the head.
    lappet = [(HX - 13, cy + 2), (HX - 5, cy + 2), (HX - 4, HY + 16),
              (HX - 12, HY + 16)]
    pygame.draw.polygon(surf, _PH_GOLD, lappet)
    for i in range(3):
        x = HX - 12 + i * 3
        col = _PH_BLUE if i % 2 == 0 else _PH_GOLD_D
        pygame.draw.line(surf, col, (x, cy + 3), (x + 1, HY + 15), 2)
    pygame.draw.polygon(surf, _PH_GOLD_D, lappet, 1)

    # Domed headcloth cap over the crown.
    pygame.draw.ellipse(surf, _PH_GOLD_D, (HX - 13, cy - 5, 27, 18))
    pygame.draw.ellipse(surf, _PH_GOLD, (HX - 12, cy - 5, 25, 15))
    for i in range(-3, 4):
        x = HX + i * 3
        col = _PH_BLUE if i % 2 == 0 else _PH_GOLD_D
        pygame.draw.line(surf, col, (x, cy - 4), (x, cy + 6), 2)

    # ── GEM-STUDDED BROW BAND lifting the nemes front ────────────────────────
    # A richer headband: the original blue band, then a row of tiny alternating
    # carnelian/turquoise studs set in gold across the brow — the jeweled lift.
    pygame.draw.line(surf, _PH_BLUE_D, (HX - 12, cy + 5), (HX + 13, cy + 4), 4)
    pygame.draw.line(surf, _PH_BLUE, (HX - 12, cy + 4), (HX + 13, cy + 3), 2)
    pygame.draw.line(surf, _JW_GOLD_D, (HX - 12, cy + 6), (HX + 13, cy + 5), 1)
    studs = [(_JW_CARN, _JW_CARN_H), (_JW_TURQ, _JW_TURQ_H)] * 4
    for i, (base, hi) in enumerate(studs):
        sx = HX - 11 + i * 3
        sy = cy + 4
        pygame.draw.circle(surf, _JW_GOLD_D, (sx, sy), 2)
        pygame.draw.circle(surf, base, (sx, sy), 1)
        pygame.draw.circle(surf, hi, (sx, sy - 1), 1)
    pygame.draw.ellipse(surf, _PH_GOLD_H, (HX - 5, cy - 4, 8, 3))

    # Enlarged uraeus cobra rearing from the brow — kept exactly as the live skin.
    bx = HX
    pygame.draw.line(surf, _PH_GOLD_D, (bx, cy + 1), (bx - 1, cy - 9), 4)
    pygame.draw.line(surf, _PH_GOLD, (bx, cy + 1), (bx - 1, cy - 9), 2)
    pygame.draw.polygon(surf, _PH_GOLD,
                        [(HX - 5, cy - 8), (HX + 3, cy - 8), (HX - 1, cy - 13)])
    pygame.draw.polygon(surf, _PH_GOLD_H,
                        [(HX - 3, cy - 9), (HX + 1, cy - 9), (HX - 1, cy - 12)])
    pygame.draw.circle(surf, _PH_GOLD_H, (HX - 1, cy - 12), 2)
    pygame.draw.circle(surf, (210, 50, 50), (HX - 1, cy - 12), 1)


build = store_skins._make_skin(_paint)
