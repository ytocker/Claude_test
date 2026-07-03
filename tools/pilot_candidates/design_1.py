"""Pilot costume — Design 1: THE CAPTAIN (golden-age airline commander).

Scratch exploration builder wrapped by the store-skin contract, NOT registered
in ``store_skins.BUILDERS``. Exposes ``build`` for the generic ninja_render
harness.

The R3 rework paints the uniform ON TOP of the UNTOUCHED scarlet macaw — no
``_build_parrot_with_palette`` recolor — so the bird stays a red-headed,
blue-winged, gold-beaked parrot that is WEARING a captain's outfit, not a
navy bird. The read at 40px: a flat-topped navy peaked cap breaking the round
crown, a white shirt-front V on the chest, and three gold rank rings on a navy
cuff riding the wing beat.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pygame

from game.store_skins import _make_skin, _poly, HX, HY, CROWN_Y

# ── costume palette (drawn OVER the natural red/blue/yellow macaw) ────────────
_CAP_NAVY = (27, 42, 74)            # flat-top peaked-cap crown
_CAP_RIM  = (42, 59, 95)            # 1px rim-light so the cap holds at night
_BRIM     = (11, 15, 28)            # patent black cap brim
_SHIRT    = (244, 241, 234)         # shirt-front white
_TIE      = (20, 33, 61)            # single tie stripe down the collar-V
_LAPEL    = (20, 33, 74)            # jacket lapels flanking the shirt
_GOLD     = (245, 197, 66)          # cap badge + sleeve rank rings
_GOLD_H   = (255, 232, 150)         # badge glint


def _paint_captain(surf, wing_angle_deg):
    # Body centre in composite space (base body centre (32,32) + PARROT_DY=20).
    BCX = 32

    # ── navy jacket lapels behind the shirt so the white wedge doesn't float and
    # the chest reads as jacket-over-shirt, not a bib. Drawn first; the white V
    # laid on top leaves only the outer lapel edges showing.
    _poly(surf, _LAPEL, [(BCX - 9, 37), (BCX, 38), (BCX - 7, 47)])
    _poly(surf, _LAPEL, [(BCX, 38), (BCX + 9, 37), (BCX + 7, 47)])

    # ── clean collar-V shirt-front over the red chest: a pale wedge, apex at the
    # throat widening to the chest, split ONLY by a single dark tie stripe. No
    # internal seams — at 40px any diagonal line inside the wedge reads as rigging.
    _poly(surf, _SHIRT, [(BCX, 38), (BCX - 7, 48), (BCX + 7, 48)])
    pygame.draw.line(surf, _TIE, (BCX, 39), (BCX, 47), 1)

    # ── captain's-rank sleeve rings: THREE fat gold bands on a navy cuff over the
    # lower blue wing that ride the wing beat. The navy cuff keeps the gaps a clean
    # dark so the three bands never smear into one gold blob at the downscale.
    cuff = int(round(wing_angle_deg * 0.10))
    bx = BCX - 17
    pygame.draw.rect(surf, _CAP_NAVY, (bx - 1, 43 + cuff, 11, 9))
    for sy in (44, 47, 50):
        pygame.draw.rect(surf, _GOLD, (bx, sy + cuff, 9, 2))

    # ── peaked officer's cap sitting ON the red head: a FLAT-TOPPED navy crown
    # (hard top edge at y22, no dome) with the red head still peeking out at the
    # sides below it, and a patent-black brim raked toward the beak. The dark brim
    # is the separator that lifts the cap off the scarlet crown.
    crown = [(38, 32), (38, 24), (40, 22), (56, 22), (58, 24), (58, 32)]
    _poly(surf, _CAP_NAVY, crown)
    # Patent brim: a 2px black band, right (forward) end dropped 1px so it rakes
    # down toward the beak.
    _poly(surf, _BRIM, [(37, 32), (59, 33), (59, 35), (37, 34)])

    # ── gold wings/cap-badge: a compact horizontal gold mark on the cap band, held
    # well clear of the gold beak (which sits ~9px lower and to the right).
    pygame.draw.rect(surf, _GOLD, (44, 29, 5, 2))
    pygame.draw.line(surf, _GOLD_H, (44, 29), (48, 29), 1)

    # ── 1px rim-light along the flat top + back edge of the cap so the navy crown
    # holds its silhouette against the dark night sky.
    pygame.draw.line(surf, _CAP_RIM, (40, 22), (56, 22), 1)
    pygame.draw.line(surf, _CAP_RIM, (38, 24), (38, 31), 1)


build = _make_skin(_paint_captain)
