"""Pilot costume — Design 1: THE CAPTAIN (golden-age airline commander).

Scratch exploration builder wrapped by the store-skin contract, NOT registered
in ``store_skins.BUILDERS``. Exposes ``build`` for the generic ninja_render
harness. The hero read at 40px is a peaked officer's cap flat-topping the round
head, a dark navy double-breasted jacket replacing the scarlet plumage, and
gold sleeve stripes that ride the wing beat — the airline-captain silhouette.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pygame

from game.store_skins import (
    _pal, _build_parrot_with_palette, _make_skin, _poly, HX, HY, CROWN_Y,
)

# ── palette: re-plumage the macaw in officer navy ────────────────────────────
# Navy jacket/cap so the costume paints gold trim ON navy instead of red-on-red;
# a pale-blue belly stands in for the white shirt-front the chest overlay refines,
# and the beak goes captain-gold so no warm scarlet survives the two-tone.
_NAVY_DARK  = (20, 33, 74)          # jacket / cap shadow
_NAVY_MAIN  = (27, 42, 100)         # cap + jacket body
_SHIRT      = (244, 241, 234)       # shirt-front white
_GOLD       = (245, 197, 66)        # wings badge + sleeve stripes
_GOLD_D     = (180, 140, 40)
_BLACK      = (11, 15, 28)          # patent cap brim / tie

P_CAPTAIN = _pal(
    tail=[(16, 27, 62), (20, 33, 74), (24, 38, 88), (30, 46, 108)],
    tail_line=(12, 20, 48),
    body_shadow=_NAVY_DARK,
    body_main=_NAVY_MAIN,
    body_chest=(200, 210, 232),
    body_belly=(180, 190, 220),
    sheen=(200, 214, 245, 55),
    wing_main=_NAVY_MAIN,
    wing_dark=_NAVY_DARK,
    wing_tip=(36, 54, 122),
    wing_secondary=None,
    wing_highlight=(70, 92, 168),
    head_shadow=_NAVY_DARK,
    head_main=_NAVY_MAIN,
    head_cheek=(34, 52, 116),
    head_crown=(30, 46, 108),
    lens_frame=(24, 38, 88),
    lens_body=_BLACK,
    lens_tint=None,
    lens_glint=None,
    beak_main=_GOLD,
    beak_dark=_GOLD_D,
    beak_gloss=(255, 232, 150),
    foot=_BLACK,
)


def _captain_base(angle_deg):
    # Navy-suited bird, no aviators — the peaked cap owns the head.
    return _build_parrot_with_palette(angle_deg, P_CAPTAIN, draw_lenses=False)


def _paint_captain(surf, wing_angle_deg):
    # Body centre in composite space (base body centre (32,32) + PARROT_DY=20).
    BCX, BCY = 32, 52

    # ── white shirt-front + navy tie (drawn first so the jacket lapels overlay it)
    _poly(surf, _SHIRT,
          [(BCX, BCY - 14), (BCX - 6, BCY + 4), (BCX + 6, BCY + 4)])
    pygame.draw.line(surf, _BLACK, (BCX, BCY - 13), (BCX, BCY + 3), 2)

    # ── navy double-breasted jacket lapels framing the shirt V
    pygame.draw.line(surf, _NAVY_DARK, (BCX - 2, BCY - 14), (BCX - 8, BCY - 6), 3)
    pygame.draw.line(surf, _NAVY_DARK, (BCX + 2, BCY - 14), (BCX + 8, BCY - 4), 2)

    # ── four gold sleeve stripes on the wing cuff — the animated captain's-rank
    # tell that rides the flap (the cuff sits at the near wing root).
    for cy in (BCY - 4, BCY - 1, BCY + 2, BCY + 5):
        pygame.draw.line(surf, _GOLD, (BCX - 14, cy), (BCX - 6, cy), 2)

    # ── peaked officer's cap — the dominant read: a flat-topped navy wedge over
    # the crown with a patent-black brim jutting forward of the beak.
    crown = [(HX - 11, CROWN_Y + 2), (HX - 6, CROWN_Y - 4),
             (HX + 6, CROWN_Y - 3), (HX + 9, CROWN_Y + 4),
             (HX + 7, CROWN_Y + 10), (HX - 9, CROWN_Y + 10)]
    _poly(surf, _NAVY_MAIN, crown)
    # Crown sheen so the flat top reads round-ish under light.
    pygame.draw.line(surf, (70, 92, 168),
                     (HX - 5, CROWN_Y - 2), (HX + 4, CROWN_Y - 1), 1)
    # Dark shadow under the front brim, then the patent brim sweeping forward past
    # the beak, then a thin cap-band separating crown from brim.
    pygame.draw.rect(surf, _BLACK, (HX - 4, CROWN_Y + 9, 14, 3))
    pygame.draw.line(surf, _BLACK, (HX - 8, CROWN_Y + 9), (HX + 12, CROWN_Y + 8), 3)
    pygame.draw.line(surf, _BLACK, (HX - 9, CROWN_Y + 7), (HX + 8, CROWN_Y + 7), 1)

    # ── gold wings badge on the cap band — two swept triangles flanking a hub,
    # the officer's insignia that names the costume at a glance.
    cx, cy = HX, CROWN_Y + 8
    _poly(surf, _GOLD, [(cx, cy - 2), (cx - 5, cy), (cx, cy + 1)])
    _poly(surf, _GOLD, [(cx, cy - 2), (cx + 5, cy), (cx, cy + 1)])
    pygame.draw.circle(surf, _GOLD, (cx, cy), 2)
    pygame.draw.circle(surf, (255, 232, 150), (cx, cy - 1), 1)


build = _make_skin(_paint_captain, base_fn=_captain_base)
