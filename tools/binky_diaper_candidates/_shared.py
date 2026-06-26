"""Shared scaffold for the BINKY diaper-redo exploration.

The shipped BINKY (body recolour + pacifier + bib + eyes + cowlick) is LOCKED;
this round only re-explores the DIAPER. Each candidate `design_N.py` writes a
single `_diaper(surf)` and wraps it with `make_binky_build(_diaper)` — every
other beat is the real production BINKY, imported from `game.store_skins`, so
the candidates render identically to the live skin except for the nappy.

Geometry crib (COMPOSITE space, the surface the overlay paints into):
  * body main ellipse  : centre (32,52), radii 19x14  → spans x13–51, y38–66
  * belly ellipse      : centre (28,58), radii 12x6   → x16–40, y52–64
  * lower-body bottom  : ~y64–66
  * FEET descend at    : (28,65)->(26,69) and (34,65)->(36,69)  [x26–36, y65–69]
  * rump / tail (back) : back-LEFT, x2–22, y44–56
  * head centre HX,HY  : (47,41);  crown CROWN_Y=31

So a *natural* nappy wraps the lower belly + rump around y52–63 and the legs
emerge BELOW it (y65–69). The shipped version sat at cy≈64 — down among the
legs — which is the look this round replaces.

Exploration only — NEVER registered in store_skins.BUILDERS.
"""
from __future__ import annotations
import pygame

from game import store_skins
from game.store_skins import (
    HX, HY, CROWN_Y, P_BINKY,
    _bb_rimlight, _bb_bib, _bb_cowlick, _bb_eye_domes, _bb_pacifier,
    _BB_PINK_LT,
    # diaper-cloth palette the shipped skin used — candidates may reuse or shift.
    _BB_DIAP, _BB_DIAP_HI, _BB_DIAP_SH, _BB_DIAP_LN, _BB_PINK, _BB_TEAL_D,
)
from game.dollar_parrot_ghost import _build_parrot_with_palette


def make_binky_build(diaper_fn):
    """Wrap a candidate `diaper_fn(surf)` into a full BINKY build callable.

    Paint order mirrors the production `_paint_binky` exactly, with the
    candidate diaper swapped in where the shipped `_bb_diaper` sat: under the
    face props (so it never crowds the pacifier/eyes) and below the bib (so a
    clear powder-blue body gap stays between the two cream cloths)."""
    def _paint(surf, _a):
        _bb_rimlight(surf)
        _bb_bib(surf)
        diaper_fn(surf)
        _bb_cowlick(surf)
        _bb_eye_domes(surf)
        pygame.draw.circle(surf, _BB_PINK_LT, (HX + 9, HY + 7), 1)   # cheek blush
        _bb_pacifier(surf)
    return store_skins._make_skin(
        _paint, base_fn=lambda a: _build_parrot_with_palette(a, P_BINKY))
