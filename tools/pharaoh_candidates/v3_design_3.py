"""v3 DESIGN 3 — THE DIVINE PRIEST (scratch candidate, NOT registered).

ENRICH pass on the live `skin_pharaoh`: the gold+lapis striped NEMES + gold
URAEUS are rebuilt UNCHANGED (identity core), then priestly regalia is layered
on the scarlet body — a spotted leopard-skin sash (the only patterned textile),
a gold throat collar, an upright gold ANKH held in the near wing (the hero
glyph), and gold anklets.

The two heroes are the ankh and the leopard sash: both are kept BOLD (few large
rosette spots, one clear looped cross) so they survive the 40px-in-motion read
day AND night. Everything below the brow stays inside the base bird footprint —
nothing dips past the feet line (~HY+24..28) and nothing balloons the body; only
the nemes rises above CROWN_Y.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Priest palette. Gold/lapis match the nemes; the leopard tan is pushed DARKER
# (#A8842E) so the sash owns its own value lane — separated from both the warm
# scarlet body and the bright ceremonial gold. Spots are true rosettes (dark
# ring + tan centre hole) so the pattern survives the 40px downscale.
_PR_GOLD    = (244, 196, 48)       # #F4C430 ceremonial gold
_PR_GOLD_D  = (188, 142, 32)       # gold shadow / under-edge
_PR_GOLD_H  = (255, 238, 158)      # gold glint
_PR_LEO     = (168, 132, 46)       # #A8842E darker leopard tan (own value lane)
_PR_LEO_D   = (118, 92, 34)        # leopard shadow / lower-contour keyline
_PR_LEO_H   = (206, 170, 92)       # leopard highlight (lit ridge)
_PR_SPOT    = (24, 18, 14)         # #18120E near-black rosette ring
_PR_LAPIS   = (27, 58, 140)        # #1B3A8C lapis
_PR_SCARLET = (196, 60, 56)        # scarlet of the body — shows through the ankh loop


def _paint(surf, _a):
    cy = CROWN_Y

    # ── PRIEST REGALIA (painted first, under the head, so the nemes/collar
    #    overlap it cleanly) ────────────────────────────────────────────────

    # Leopard-skin sash draped diagonally across the LOWER chest down to the far
    # hip — pushed low + left so the upper chest stays clear scarlet for the ankh
    # hero. A tapered quad in the darker tan so it wins its own value lane between
    # the warm body and the bright gold; a 1px dark keyline on the lower contour
    # holds the diagonal-band silhouette against scarlet, a lit upper ridge lifts
    # it. Read target: a "spotted diagonal stripe," not a brown smear.
    sash = [(HX - 4, HY + 13), (HX - 9, HY + 14),
            (HX - 22, HY + 27), (HX - 16, HY + 28)]
    _poly(surf, _PR_LEO, sash)
    # Lit upper ridge + dark lower keyline — the two edges that hold the band.
    pygame.draw.line(surf, _PR_LEO_H, (HX - 5, HY + 13), (HX - 20, HY + 26), 1)
    pygame.draw.line(surf, _PR_LEO_D, (HX - 8, HY + 15), (HX - 21, HY + 28), 1)

    # Three LARGE true rosettes along the diagonal — each a ~3px near-black ring
    # with a 1px tan centre hole, so the pattern reads as spots, not solid dots,
    # after the downscale. Few + large is what survives 40px.
    for sx, sy in ((HX - 7, HY + 16), (HX - 12, HY + 20), (HX - 17, HY + 24)):
        pygame.draw.circle(surf, _PR_SPOT, (sx, sy), 3)
        pygame.draw.circle(surf, _PR_LEO, (sx, sy), 1)

    # Gold anklets — thinned + DARKENED to a single muted band each so they stop
    # competing with the collar down-low. No bright glint here on purpose: the
    # focal gold lives at the throat collar.
    for fx in (28, 34):
        pygame.draw.line(surf, _PR_GOLD_D, (fx - 3, 64), (fx + 3, 64), 2)
        pygame.draw.line(surf, _PR_GOLD, (fx - 2, 63), (fx + 2, 63), 1)

    # Upright gold ANKH on the CLEAR scarlet chest — the HERO glyph, enlarged ~35%
    # and isolated off the sash + collar gold so a looped cross reads at 40px. A
    # 1px lapis keyline rings every stroke so the gold never melts into adjacent
    # gold; the scarlet body shows through the loop hole. The crossbar is wider
    # than the loop and the shaft foot stays above the feet line (inside body).
    ax = HX - 13
    loop_cy = HY + 9
    shaft_top = HY + 14
    shaft_bot = HY + 26
    bar_y = HY + 18
    # Dark keyline pass — drawn slightly fat under every gold stroke so the glyph
    # carries a continuous dark edge against the gold collar/sash.
    pygame.draw.circle(surf, _PR_LAPIS, (ax, loop_cy), 7)
    pygame.draw.line(surf, _PR_LAPIS, (ax, shaft_top), (ax, shaft_bot + 1), 5)
    pygame.draw.line(surf, _PR_LAPIS, (ax - 7, bar_y), (ax + 7, bar_y), 4)
    # Loop (the head of the ankh) — a bold gold ring around a surviving scarlet hole.
    pygame.draw.circle(surf, _PR_GOLD_D, (ax, loop_cy), 6)
    pygame.draw.circle(surf, _PR_GOLD, (ax, loop_cy), 6, 2)
    pygame.draw.circle(surf, _PR_SCARLET, (ax, loop_cy), 4)
    pygame.draw.circle(surf, _PR_GOLD_H, (ax - 2, loop_cy - 3), 1)
    # Vertical shaft — 3px gold core.
    pygame.draw.line(surf, _PR_GOLD_D, (ax, shaft_top), (ax, shaft_bot), 3)
    pygame.draw.line(surf, _PR_GOLD, (ax, shaft_top), (ax, shaft_bot), 1)
    pygame.draw.line(surf, _PR_GOLD_H, (ax - 1, shaft_top + 1), (ax - 1, shaft_bot - 2), 1)
    # Horizontal crossbar — a clear 2px-tall bar WIDER than the loop.
    pygame.draw.line(surf, _PR_GOLD_D, (ax - 6, bar_y), (ax + 6, bar_y), 3)
    pygame.draw.line(surf, _PR_GOLD, (ax - 6, bar_y - 1), (ax + 6, bar_y - 1), 1)
    pygame.draw.line(surf, _PR_GOLD_H, (ax - 5, bar_y - 1), (ax, bar_y - 1), 1)

    # Gold collar at the throat — the SINGLE brightest gold note below the nemes.
    # A bold band hugging the lower head, tucked under the lappet, inside footprint.
    pygame.draw.arc(surf, _PR_GOLD_D, (HX - 12, HY + 1, 26, 14), 3.34, 6.08, 5)
    pygame.draw.arc(surf, _PR_GOLD, (HX - 12, HY + 1, 26, 14), 3.34, 6.08, 3)
    pygame.draw.arc(surf, _PR_LAPIS, (HX - 10, HY + 2, 22, 12), 3.34, 6.08, 1)
    pygame.draw.arc(surf, _PR_GOLD_H, (HX - 9, HY, 18, 12), 3.6, 5.6, 1)

    # ── IDENTITY CORE — the live nemes + uraeus, rebuilt UNCHANGED ───────────
    # Side lappet — striped cloth falling beside the head, fewer 2px stripes.
    lappet = [(HX - 13, cy + 2), (HX - 5, cy + 2), (HX - 4, HY + 16),
              (HX - 12, HY + 16)]
    pygame.draw.polygon(surf, store_skins._PH_GOLD, lappet)
    for i in range(3):
        x = HX - 12 + i * 3
        col = store_skins._PH_BLUE if i % 2 == 0 else store_skins._PH_GOLD_D
        pygame.draw.line(surf, col, (x, cy + 3), (x + 1, HY + 15), 2)
    pygame.draw.polygon(surf, store_skins._PH_GOLD_D, lappet, 1)

    # Domed headcloth cap over the crown.
    pygame.draw.ellipse(surf, store_skins._PH_GOLD_D, (HX - 13, cy - 5, 27, 18))
    pygame.draw.ellipse(surf, store_skins._PH_GOLD, (HX - 12, cy - 5, 25, 15))
    # Wider, fewer alternating stripes radiating over the cap (2px each).
    for i in range(-3, 4):
        x = HX + i * 3
        col = store_skins._PH_BLUE if i % 2 == 0 else store_skins._PH_GOLD_D
        pygame.draw.line(surf, col, (x, cy - 4), (x, cy + 6), 2)
    # Front headband.
    pygame.draw.line(surf, store_skins._PH_BLUE_D, (HX - 12, cy + 5), (HX + 13, cy + 4), 4)
    pygame.draw.line(surf, store_skins._PH_BLUE, (HX - 12, cy + 4), (HX + 13, cy + 3), 2)
    pygame.draw.ellipse(surf, store_skins._PH_GOLD_H, (HX - 5, cy - 4, 8, 3))

    # Enlarged uraeus cobra rearing from the brow — the hero accent.
    bx = HX
    pygame.draw.line(surf, store_skins._PH_GOLD_D, (bx, cy + 1), (bx - 1, cy - 9), 4)
    pygame.draw.line(surf, store_skins._PH_GOLD, (bx, cy + 1), (bx - 1, cy - 9), 2)
    # Flared hood.
    pygame.draw.polygon(surf, store_skins._PH_GOLD,
                        [(HX - 5, cy - 8), (HX + 3, cy - 8), (HX - 1, cy - 13)])
    pygame.draw.polygon(surf, store_skins._PH_GOLD_H,
                        [(HX - 3, cy - 9), (HX + 1, cy - 9), (HX - 1, cy - 12)])
    pygame.draw.circle(surf, store_skins._PH_GOLD_H, (HX - 1, cy - 12), 2)
    pygame.draw.circle(surf, (210, 50, 50), (HX - 1, cy - 12), 1)


build = store_skins._make_skin(_paint)
