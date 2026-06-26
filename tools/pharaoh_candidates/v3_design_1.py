"""THE GOLD KING — full royal regalia  (pharaoh v3, ENRICH candidate 1).

Scratch exploration only — NOT registered in store_skins.BUILDERS.

This is an ENRICH pass on the SHIPPED skin_pharaoh, not a re-theme. The identity
core — the gold+lapis striped NEMES headdress with flaring side lappets + the
gold URAEUS cobra at the brow — is rebuilt UNCHANGED from _paint_pharaoh (same
_PH_* values, reused here as _GK_*). Everything else is the new GOLD KING
regalia layered ON TOP of the kept scarlet body so it still reads as the SAME
pharaoh, only richer:

  - the broad USEKH collar (3 concentric bead rows gold/lapis/turquoise) arcing
    across the upper breast — the second-loudest read after the crook & flail;
  - the plaited FALSE BEARD straight down from the chin;
  - the CROOK & FLAIL crossed high on the CHEST in a gold X — THE HERO, the
    instant "king holding the symbols of authority" read;
  - thin gold ANKLETS on the feet line.

Footprint law: every body ornament stays INSIDE the base bird footprint —
nothing below the feet line (~HY+24), nothing balloons the body; only the nemes
rises above CROWN_Y. The crook & flail are crossed on the chest, NOT dangling
past the feet. Gold-on-scarlet is the strongest contrast, so the regalia is kept
bold + clean to survive the 40px read on day AND night.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# ── Identity-core palette — the SHIPPED nemes/uraeus colours, reused unchanged so
# the headdress is pixel-for-pixel the classic pharaoh (do NOT redesign these).
_GK_GOLD   = (245, 200, 70)        # nemes gold (= _PH_GOLD)
_GK_GOLD_D = (190, 145, 35)        # nemes gold shadow (= _PH_GOLD_D)
_GK_GOLD_H = (255, 240, 160)       # nemes gold highlight (= _PH_GOLD_H)
_GK_BLUE   = (44, 100, 188)        # nemes lapis stripe (= _PH_BLUE)
_GK_BLUE_D = (26, 64, 128)         # nemes lapis shadow (= _PH_BLUE_D)

# ── Regalia palette — the brief's spec hexes for the added royal pieces.
_GK_R_GOLD   = (244, 196, 48)      # #F4C430 regalia gold
_GK_R_GOLD_H = (255, 236, 150)     # regalia gold glint
_GK_LAPIS    = (27, 58, 140)       # #1B3A8C lapis bead row
_GK_TURQ     = (47, 184, 166)      # #2FB8A6 turquoise bead row
_GK_BRONZE   = (122, 74, 18)       # #7A4A12 bronze shadow (under-edges)


def _draw_nemes(surf):
    """The UNCHANGED identity core — the shipped _paint_pharaoh nemes + uraeus,
    rebuilt verbatim so the costume reads as the SAME classic gold-nemes pharaoh
    before any regalia is added. Lifted directly from store_skins._paint_pharaoh."""
    cy = CROWN_Y
    # Side lappet — striped cloth falling beside the head, fewer 2px stripes.
    lappet = [(HX - 13, cy + 2), (HX - 5, cy + 2), (HX - 4, HY + 16),
              (HX - 12, HY + 16)]
    pygame.draw.polygon(surf, _GK_GOLD, lappet)
    for i in range(3):
        x = HX - 12 + i * 3
        col = _GK_BLUE if i % 2 == 0 else _GK_GOLD_D
        pygame.draw.line(surf, col, (x, cy + 3), (x + 1, HY + 15), 2)
    pygame.draw.polygon(surf, _GK_GOLD_D, lappet, 1)

    # Domed headcloth cap over the crown.
    pygame.draw.ellipse(surf, _GK_GOLD_D, (HX - 13, cy - 5, 27, 18))
    pygame.draw.ellipse(surf, _GK_GOLD, (HX - 12, cy - 5, 25, 15))
    # Wider, fewer alternating stripes radiating over the cap (2px each).
    for i in range(-3, 4):
        x = HX + i * 3
        col = _GK_BLUE if i % 2 == 0 else _GK_GOLD_D
        pygame.draw.line(surf, col, (x, cy - 4), (x, cy + 6), 2)
    # Front headband.
    pygame.draw.line(surf, _GK_BLUE_D, (HX - 12, cy + 5), (HX + 13, cy + 4), 4)
    pygame.draw.line(surf, _GK_BLUE, (HX - 12, cy + 4), (HX + 13, cy + 3), 2)
    pygame.draw.ellipse(surf, _GK_GOLD_H, (HX - 5, cy - 4, 8, 3))

    # Enlarged uraeus cobra rearing from the brow — the hero accent.
    bx = HX
    pygame.draw.line(surf, _GK_GOLD_D, (bx, cy + 1), (bx - 1, cy - 9), 4)
    pygame.draw.line(surf, _GK_GOLD, (bx, cy + 1), (bx - 1, cy - 9), 2)
    # Flared hood.
    pygame.draw.polygon(surf, _GK_GOLD,
                        [(HX - 5, cy - 8), (HX + 3, cy - 8), (HX - 1, cy - 13)])
    pygame.draw.polygon(surf, _GK_GOLD_H,
                        [(HX - 3, cy - 9), (HX + 1, cy - 9), (HX - 1, cy - 12)])
    pygame.draw.circle(surf, _GK_GOLD_H, (HX - 1, cy - 12), 2)
    pygame.draw.circle(surf, (210, 50, 50), (HX - 1, cy - 12), 1)


def _draw_collar(surf, BCX, BCY):
    """Broad USEKH collar — 3 concentric bead rows (gold / lapis / turquoise)
    arcing across the upper breast just under the chin, inside the footprint.
    Drawn FIRST of the body pieces so the false beard + crook & flail overlap its
    top edge and the collar reads as worn UNDER the chest regalia. Wide gold-on-
    scarlet bands so it survives the 40px read; turquoise sits innermost where it
    has the warm body to pop against rather than fighting the lapis."""
    # The collar is a fan of three nested arcs centred on the throat, opening
    # downward across the breast. A bronze under-arc seats it on the body first.
    rect_out = pygame.Rect(BCX - 14, BCY - 16, 28, 24)
    pygame.draw.arc(surf, _GK_BRONZE, rect_out.inflate(2, 2), 3.45, 6.10, 5)
    # Row 1 (outermost) — gold.
    pygame.draw.arc(surf, _GK_R_GOLD, rect_out, 3.50, 6.05, 4)
    pygame.draw.arc(surf, _GK_R_GOLD_H, rect_out.inflate(-1, -1), 3.55, 4.55, 1)
    # Row 2 — lapis.
    rect_mid = rect_out.inflate(-7, -7)
    pygame.draw.arc(surf, _GK_LAPIS, rect_mid, 3.55, 6.00, 4)
    # Row 3 (innermost) — turquoise, popping on the warm body.
    rect_in = rect_out.inflate(-14, -14)
    pygame.draw.arc(surf, _GK_TURQ, rect_in, 3.60, 5.95, 4)
    # A few bead ticks across the gold row so it reads as strung beads, not a band.
    import math
    for t in (3.7, 4.05, 4.4, 4.75, 5.1, 5.45, 5.8):
        rx = BCX + (rect_out.width / 2 - 2) * math.cos(t)
        ry = BCY - 4 + (rect_out.height / 2 - 2) * math.sin(t)
        pygame.draw.circle(surf, _GK_BRONZE, (int(rx), int(ry)), 1)
    # The terminal lotus tabs at the two collar ends.
    pygame.draw.circle(surf, _GK_R_GOLD, (BCX - 13, BCY - 3), 2)
    pygame.draw.circle(surf, _GK_R_GOLD, (BCX + 13, BCY - 3), 2)


def _draw_beard(surf):
    """The plaited FALSE BEARD straight down from the chin — a narrow gold post
    with a slight forward tip flick and horizontal plait ticks. Kept slim + on the
    centre line so it never balloons the head, ending well above the collar core."""
    chin_x, chin_y = HX - 1, HY + 11
    beard = [(chin_x - 3, chin_y), (chin_x + 3, chin_y),
             (chin_x + 3, chin_y + 9), (chin_x + 5, chin_y + 12),
             (chin_x + 1, chin_y + 13), (chin_x - 3, chin_y + 10)]
    _poly(surf, _GK_BRONZE, [(x + 1, y) for x, y in beard])
    _poly(surf, _GK_R_GOLD, beard)
    # Plait ticks so it reads as the woven ceremonial beard, not a gold bar.
    for ty in range(chin_y + 2, chin_y + 11, 2):
        pygame.draw.line(surf, _GK_BRONZE, (chin_x - 2, ty), (chin_x + 2, ty), 1)
    pygame.draw.line(surf, _GK_R_GOLD_H, (chin_x - 2, chin_y + 1),
                     (chin_x - 2, chin_y + 8), 1)


def _draw_crook_flail(surf, BCX, BCY):
    """THE HERO — the CROOK & FLAIL crossed high on the chest in a gold X. The
    crook (shepherd's hook) runs lower-left → upper-right; the flail (handle +
    three beaded strands) runs lower-right → upper-left, so the two cross over the
    collar centre. Both are held INSIDE the silhouette — the heads clear the
    collar at the top of the chest, the bases stop above the feet line; nothing
    dangles past the feet. Bold gold with a bronze under-edge for the 40px read."""
    cx, cy = BCX, BCY - 2          # crossing point, high on the breast

    # ── CROOK — a straight gold shaft from lower-left up to upper-right, capped by
    # a hooked shepherd's crook curling forward at the top.
    cr_bot = (cx - 6, cy + 11)
    cr_top = (cx + 6, cy - 9)
    pygame.draw.line(surf, _GK_BRONZE, (cr_bot[0] + 1, cr_bot[1] + 1),
                     (cr_top[0] + 1, cr_top[1] + 1), 4)
    pygame.draw.line(surf, _GK_R_GOLD, cr_bot, cr_top, 3)
    pygame.draw.line(surf, _GK_R_GOLD_H, (cr_bot[0], cr_bot[1] - 1),
                     (cr_top[0], cr_top[1] - 1), 1)
    # Hooked head — a small forward curl off the crook top.
    pygame.draw.lines(surf, _GK_BRONZE, False,
                      [(cr_top[0] + 1, cr_top[1] - 1), (cr_top[0] + 4, cr_top[1] - 4),
                       (cr_top[0] + 1, cr_top[1] - 6), (cr_top[0] - 2, cr_top[1] - 4)], 4)
    pygame.draw.lines(surf, _GK_R_GOLD, False,
                      [(cr_top[0] + 1, cr_top[1] - 1), (cr_top[0] + 4, cr_top[1] - 4),
                       (cr_top[0] + 1, cr_top[1] - 6), (cr_top[0] - 2, cr_top[1] - 4)], 2)

    # ── FLAIL — a straight gold shaft from lower-right up to upper-left, with three
    # short beaded strands swinging off its top (the nekhakha). The strands stay
    # tucked toward the shoulder so they never break past the body edge.
    fl_bot = (cx + 6, cy + 11)
    fl_top = (cx - 6, cy - 9)
    pygame.draw.line(surf, _GK_BRONZE, (fl_bot[0] + 1, fl_bot[1] + 1),
                     (fl_top[0] + 1, fl_top[1] + 1), 4)
    pygame.draw.line(surf, _GK_R_GOLD, fl_bot, fl_top, 3)
    pygame.draw.line(surf, _GK_R_GOLD_H, (fl_bot[0], fl_bot[1] - 1),
                     (fl_top[0], fl_top[1] - 1), 1)
    # Three beaded strands off the flail head, fanning down-left but kept inside.
    for dx, dy in ((-4, 6), (-1, 7), (2, 6)):
        sx, sy = fl_top[0], fl_top[1] - 1
        ex, ey = sx + dx, sy + dy
        pygame.draw.line(surf, _GK_BRONZE, (sx + 1, sy), (ex + 1, ey), 2)
        pygame.draw.line(surf, _GK_R_GOLD, (sx, sy), (ex, ey), 1)
        pygame.draw.circle(surf, _GK_R_GOLD, (ex, ey), 2)
        pygame.draw.circle(surf, _GK_R_GOLD_H, (ex, ey - 1), 1)

    # A small bright boss where the two cross so the X has a clear focal centre.
    pygame.draw.circle(surf, _GK_BRONZE, (cx, cy), 3)
    pygame.draw.circle(surf, _GK_R_GOLD, (cx, cy), 2)
    pygame.draw.circle(surf, _GK_R_GOLD_H, (cx - 1, cy - 1), 1)


def _draw_anklets(surf):
    """Thin gold ANKLETS on the feet line — a small ringed band on each ankle, ON
    the line (~HY+23), never below the feet, so the bird keeps its true size."""
    for fx in (28, 34):
        pygame.draw.line(surf, _GK_BRONZE, (fx - 2, HY + 24), (fx + 2, HY + 24), 3)
        pygame.draw.line(surf, _GK_R_GOLD, (fx - 2, HY + 23), (fx + 2, HY + 23), 2)
        pygame.draw.circle(surf, _GK_R_GOLD_H, (fx, HY + 23), 1)


def _paint(surf, _a):
    BCX, BCY = 32, 52              # body centre in composite space

    # Body regalia bottom-up: collar seats on the breast first, the false beard
    # drops from the chin over its top edge, then the crook & flail X reads as the
    # held HERO above everything. Anklets close the look at the feet. Finally the
    # UNCHANGED nemes is painted last so the headdress crisply owns the head.
    _draw_collar(surf, BCX, BCY)
    _draw_beard(surf)
    _draw_crook_flail(surf, BCX, BCY)
    _draw_anklets(surf)
    _draw_nemes(surf)


build = store_skins._make_skin(_paint)
