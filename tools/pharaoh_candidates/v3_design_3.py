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

# Priest palette. Gold/lapis match the nemes; leopard tan + near-black spots are
# the one patterned textile in the set; the leopard tan gets a shadow + highlight
# so the diagonal drape reads as cloth, not a flat bar, after downscale.
_PR_GOLD    = (244, 196, 48)       # #F4C430 ceremonial gold
_PR_GOLD_D  = (188, 142, 32)       # gold shadow / under-edge
_PR_GOLD_H  = (255, 238, 158)      # gold glint
_PR_LEO     = (201, 162, 75)       # #C9A24B leopard tan
_PR_LEO_D   = (158, 124, 52)       # leopard shadow (drape fold)
_PR_LEO_H   = (224, 192, 118)      # leopard highlight (lit ridge)
_PR_SPOT    = (26, 20, 16)         # #1A1410 rosette spots
_PR_LAPIS   = (27, 58, 140)        # #1B3A8C lapis


def _paint(surf, _a):
    cy = CROWN_Y

    # ── PRIEST REGALIA (painted first, under the head, so the nemes/collar
    #    overlap it cleanly) ────────────────────────────────────────────────

    # Leopard-skin sash draped diagonally over the near shoulder, crossing the
    # chest down to the far hip — kept inside the footprint. Drawn as a tapered
    # quad with a shadow under-edge + a lit upper ridge so the diagonal reads as
    # cloth. The spots ride ON the drape afterward.
    sash = [(HX + 4, HY + 6), (HX - 2, HY + 9),
            (HX - 20, HY + 25), (HX - 14, HY + 26)]
    sash_sh = [(HX - 2, HY + 9), (HX - 20, HY + 25),
               (HX - 14, HY + 26), (HX - 9, HY + 24)]
    _poly(surf, _PR_LEO, sash)
    _poly(surf, _PR_LEO_D, sash_sh)
    # Lit upper ridge of the drape — one bright edge so the band lifts off scarlet.
    pygame.draw.line(surf, _PR_LEO_H, (HX + 3, HY + 6), (HX - 18, HY + 24), 2)

    # Bold leopard rosettes — FEW + LARGE so the pattern survives 40px. Each is a
    # near-black dot with a thin tan break so it reads as a rosette, not a blob.
    for sx, sy, r in ((HX - 3, HY + 12, 3), (HX - 9, HY + 17, 3),
                      (HX - 15, HY + 22, 2), (HX + 1, HY + 9, 2)):
        pygame.draw.circle(surf, _PR_SPOT, (sx, sy), r)
        pygame.draw.circle(surf, _PR_LEO_H, (sx + 1, sy - 1), 1)

    # Gold anklets at the feet line — thin bright bands, inside the footprint.
    for fx in (28, 34):
        pygame.draw.line(surf, _PR_GOLD_D, (fx - 3, 64), (fx + 3, 64), 3)
        pygame.draw.line(surf, _PR_GOLD, (fx - 3, 63), (fx + 3, 63), 2)
        pygame.draw.line(surf, _PR_GOLD_H, (fx - 2, 62), (fx, 62), 1)

    # Upright gold ANKH held in the near wing — the HERO glyph. A clear looped
    # cross: a teardrop loop on top, a vertical shaft, a horizontal crossbar.
    # Held inside the silhouette (shaft foot stays above the feet line) so it
    # never dangles past the body. Gold-on-scarlet for the strongest contrast.
    ax = HX - 19
    loop_cy = HY + 9
    shaft_top = HY + 13
    shaft_bot = HY + 23
    bar_y = HY + 16
    # Loop (the head of the ankh) — drawn as a ring so the hole reads at size.
    pygame.draw.circle(surf, _PR_GOLD_D, (ax, loop_cy), 5)
    pygame.draw.circle(surf, _PR_GOLD, (ax, loop_cy), 4)
    pygame.draw.circle(surf, (190, 70, 70), (ax, loop_cy), 2)   # scarlet shows through
    pygame.draw.circle(surf, _PR_GOLD_H, (ax - 1, loop_cy - 2), 1)
    # Vertical shaft.
    pygame.draw.line(surf, _PR_GOLD_D, (ax + 1, shaft_top), (ax + 1, shaft_bot), 4)
    pygame.draw.line(surf, _PR_GOLD, (ax, shaft_top), (ax, shaft_bot), 2)
    pygame.draw.line(surf, _PR_GOLD_H, (ax - 1, shaft_top + 1), (ax - 1, shaft_bot - 3), 1)
    # Horizontal crossbar.
    pygame.draw.line(surf, _PR_GOLD_D, (ax - 5, bar_y + 1), (ax + 6, bar_y + 1), 4)
    pygame.draw.line(surf, _PR_GOLD, (ax - 5, bar_y), (ax + 6, bar_y), 2)
    pygame.draw.line(surf, _PR_GOLD_H, (ax - 4, bar_y - 1), (ax + 2, bar_y - 1), 1)

    # Gold collar at the throat — a simple bright band hugging the lower head,
    # tucked under the nemes lappet, inside the footprint.
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
