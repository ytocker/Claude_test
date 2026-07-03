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
_NAVY_MAIN  = (27, 42, 100)         # jacket body
_CAP_NAVY   = (27, 42, 74)          # #1B2A4A flat-top cap crown (darker than head)
_CAP_RIM    = (42, 59, 95)          # #2A3B5F 1px rim-light so the cap holds at night
_SHIRT      = (244, 241, 234)       # shirt-front white
_TIE        = (20, 33, 61)          # #14213D single tie stripe down the collar-V
_GOLD       = (245, 197, 66)        # cap badge + sleeve stripes
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

    # ── clean collar-V shirt-front: a pale wedge, apex at the throat widening to
    # the chest, split ONLY by a single dark tie stripe. No internal seams — at
    # 40px any diagonal line inside this white wedge reads as sailboat rigging.
    _poly(surf, _SHIRT, [(BCX, 38), (BCX - 7, 48), (BCX + 7, 48)])
    pygame.draw.line(surf, _TIE, (BCX, 39), (BCX, 47), 1)

    # ── navy double-breasted lapels edging the wedge so the white doesn't float.
    pygame.draw.line(surf, _NAVY_DARK, (BCX - 1, 38), (BCX - 8, 46), 3)
    pygame.draw.line(surf, _NAVY_DARK, (BCX + 1, 38), (BCX + 8, 47), 2)

    # ── captain's-rank sleeve stripes: exactly THREE fat gold bands on the cuff
    # that ride the wing beat. A navy cuff backing keeps the gaps a clean navy so
    # the three bands never smear into one gold blob at the downscale.
    cuff = int(round(wing_angle_deg * 0.10))
    bx = BCX - 16
    pygame.draw.rect(surf, _CAP_NAVY, (bx - 1, 43 + cuff, 11, 9))
    for sy in (44, 47, 50):
        pygame.draw.rect(surf, _GOLD, (bx, sy + cuff, 9, 2))

    # ── peaked officer's cap — a FLAT-TOPPED navy dome (flat top edge at y26) that
    # breaks the round crown, with a patent-black brim raked toward the beak. The
    # dark brim is the separator that lifts the cap off the navy head.
    crown = [(38, 34), (38, 28), (40, 26), (56, 26), (58, 28), (58, 34)]
    _poly(surf, _CAP_NAVY, crown)
    # Patent brim: a 2px black band, right end dropped 1px so it rakes to the beak.
    _poly(surf, _BLACK, [(37, 34), (59, 35), (59, 37), (37, 36)])

    # ── compact cap badge: a small horizontal gold mark on the band, held clear
    # of the gold beak by a navy gap so the two never merge into one gold smear.
    pygame.draw.rect(surf, _GOLD, (44, 32, 5, 2))
    pygame.draw.line(surf, (255, 232, 150), (44, 32), (48, 32), 1)

    # ── 1px rim-light along the top + back of the cap crown and the upper back so
    # the navy silhouette holds against the dark night sky.
    pygame.draw.line(surf, _CAP_RIM, (40, 26), (56, 26), 1)
    pygame.draw.line(surf, _CAP_RIM, (38, 28), (38, 33), 1)
    pygame.draw.lines(surf, _CAP_RIM, False, [(16, 47), (20, 44), (25, 42)], 1)


build = _make_skin(_paint_captain, base_fn=_captain_base)
