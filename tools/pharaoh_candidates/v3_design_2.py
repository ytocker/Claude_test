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


def _paint(surf, _a):
    cy = CROWN_Y

    # ── JEWELED PECTORAL (the HERO) ──────────────────────────────────────────
    # Painted first so a short hanger tucks under the nemes lappet. ONE bold
    # clean medallion: a solid GOLD disc (no lapis field, no side gems, no bead
    # fringe) carrying ONE big high-contrast lapis scarab. One stone, two values,
    # on gold — the only thing that survives the 40px downscale as a hero. Nudged
    # lower/centred (HX-9) and the lappet overlap is trimmed so the cloth no
    # longer clips the disc. Footprint: top ~HY+13, base ~HY+30, inside the body.
    px, py = HX - 9, HY + 21             # medallion centre, low and centred
    # Short twin hanger links from the breast down to the medallion crown.
    pygame.draw.line(surf, _JW_GOLD_D, (px - 3, HY + 12), (px - 2, HY + 13), 2)
    pygame.draw.line(surf, _JW_GOLD_D, (px + 3, HY + 12), (px + 2, HY + 13), 2)
    pygame.draw.line(surf, _JW_GOLD, (px - 3, HY + 12), (px - 2, HY + 13), 1)
    pygame.draw.line(surf, _JW_GOLD, (px + 3, HY + 12), (px + 2, HY + 13), 1)

    # Solid gold disc — broad gold rim, bright gold face, one arc glint. No inner
    # field colour, so the whole disc reads as a single warm gold coin.
    pygame.draw.circle(surf, _JW_GOLD_D, (px, py), 11)
    pygame.draw.circle(surf, _JW_GOLD, (px, py), 10)
    pygame.draw.arc(surf, _JW_GOLD_H, (px - 10, py - 10, 20, 20), 0.6, 2.5, 2)
    # ONE big lapis scarab carapace — ~6px tall blue body, single gold rim, one
    # bright facet. Two values of blue on a gold ground = unmistakable at 40px.
    pygame.draw.ellipse(surf, _JW_GOLD_D, (px - 5, py - 4, 10, 9))   # gold seat/rim
    pygame.draw.ellipse(surf, _JW_LAPIS, (px - 4, py - 3, 8, 7))     # lapis carapace
    pygame.draw.ellipse(surf, _JW_LAPIS_H, (px - 3, py - 2, 4, 3))   # bright facet
    pygame.draw.circle(surf, _JW_GOLD_H, (px, py - 4), 1)            # gilded head nub

    # ── NEAR-WING ARMLET + WRIST CUFF (gold only) ────────────────────────────
    # Gold-only bands across the near wing root (armlet) and lower (wrist cuff).
    # The inset turquoise/carnelian studs are dropped — they vanished at 40px and
    # muddied the gold; three values of gold alone read as clean wing richness.
    pygame.draw.line(surf, _JW_GOLD_D, (HX - 24, HY + 13), (HX - 18, HY + 11), 5)
    pygame.draw.line(surf, _JW_GOLD, (HX - 24, HY + 13), (HX - 18, HY + 11), 3)
    pygame.draw.line(surf, _JW_GOLD_H, (HX - 23, HY + 12), (HX - 19, HY + 10), 1)

    pygame.draw.line(surf, _JW_GOLD_D, (HX - 26, HY + 21), (HX - 19, HY + 19), 6)
    pygame.draw.line(surf, _JW_GOLD, (HX - 26, HY + 21), (HX - 19, HY + 19), 4)
    pygame.draw.line(surf, _JW_GOLD_H, (HX - 25, HY + 20), (HX - 20, HY + 18), 1)

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
    # Side lappet — striped cloth falling beside the head. Shortened (base lifted
    # to ~HY+12) and tucked outward so the falling cloth no longer clips the
    # medallion now sitting low and centred on the chest.
    lappet = [(HX - 13, cy + 2), (HX - 6, cy + 2), (HX - 6, HY + 12),
              (HX - 13, HY + 12)]
    pygame.draw.polygon(surf, _PH_GOLD, lappet)
    for i in range(2):
        x = HX - 11 + i * 3
        col = _PH_BLUE if i % 2 == 0 else _PH_GOLD_D
        pygame.draw.line(surf, col, (x, cy + 3), (x, HY + 11), 2)
    pygame.draw.polygon(surf, _PH_GOLD_D, lappet, 1)

    # Domed headcloth cap over the crown.
    pygame.draw.ellipse(surf, _PH_GOLD_D, (HX - 13, cy - 5, 27, 18))
    pygame.draw.ellipse(surf, _PH_GOLD, (HX - 12, cy - 5, 25, 15))
    for i in range(-3, 4):
        x = HX + i * 3
        col = _PH_BLUE if i % 2 == 0 else _PH_GOLD_D
        pygame.draw.line(surf, col, (x, cy - 4), (x, cy + 6), 2)

    # ── BROW BAND lifting the nemes front ────────────────────────────────────
    # The original crisp blue headband, then ONE symmetric trio of brow jewels in
    # gold: a carnelian cabochon centred at the uraeus base flanked by a single
    # turquoise either side (HX±5). One readable brow jewel-row, not a speckled
    # line — the 8-stud band read as noise at 40px.
    pygame.draw.line(surf, _PH_BLUE_D, (HX - 12, cy + 5), (HX + 13, cy + 4), 4)
    pygame.draw.line(surf, _PH_BLUE, (HX - 12, cy + 4), (HX + 13, cy + 3), 2)
    trio = ((HX - 5, _JW_TURQ, _JW_TURQ_H), (HX, _JW_CARN, _JW_CARN_H),
            (HX + 5, _JW_TURQ, _JW_TURQ_H))
    for sx, base, hi in trio:
        pygame.draw.circle(surf, _JW_GOLD_D, (sx, cy + 4), 2)
        pygame.draw.circle(surf, base, (sx, cy + 4), 1)
        pygame.draw.circle(surf, hi, (sx, cy + 3), 1)
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
