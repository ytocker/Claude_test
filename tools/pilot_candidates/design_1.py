"""Pilot costume — Design 1: THE CAPTAIN (golden-age airline commander).

Scratch exploration builder wrapped by the store-skin contract, NOT registered
in ``store_skins.BUILDERS``. Exposes ``build`` for the generic ninja_render
harness.

The R4 rework paints the FULL captain's uniform ON TOP of the UNTOUCHED
scarlet macaw — no ``_build_parrot_with_palette`` recolor — so the bird stays
a red-headed, blue-winged, gold-beaked parrot that is WEARING a captain's
outfit, not a navy bird. The read at 40px: a flat-topped navy peaked cap
breaking the round crown, aviator shades on the scarlet face, a full navy
jacket body with a white shirt-V + gold buttons on the chest, and three gold
rank rings on a navy cuff riding the wing beat.
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
_JACKET   = (20, 33, 74)            # full navy jacket body over chest + belly
_LAPEL    = (15, 25, 55)            # darker navy lapels flanking the shirt-V
_SHIRT    = (244, 241, 234)         # shirt-front white showing between lapels
_TIE      = (14, 21, 61)            # single dark tie stripe down the collar-V
_GOLD     = (245, 197, 66)          # cap badge + jacket buttons + sleeve rings
_GOLD_H   = (255, 232, 150)         # badge glint
# Aviator shades on the scarlet face — the "stylish pilot" tell at 40px.
_AV_LENS   = (30, 25, 20)           # dark teardrop lens body
_AV_BRIDGE = (200, 165, 50)         # gold nose-bridge
_AV_RIM    = (180, 150, 40)         # 1px gold frame rim around each lens
_AV_GLINT  = (255, 255, 255)        # reflection dot


def _paint_captain(surf, wing_angle_deg):
    # Body centre in composite space (base body centre (32,32) + PARROT_DY=20).
    BCX = 32

    # ── FULL navy jacket body over the whole chest + belly. Shaped so the collar
    # meets the throat under the chin but the upper-right stays LOW, clear of the
    # scarlet face/aviators up-right — the head sits in FRONT of the right
    # shoulder, so the red head keeps reading over the uniform.
    jacket = [(23, 45), (26, 38), (31, 35), (38, 35), (43, 40),
              (46, 47), (50, 51), (46, 54), (29, 54), (22, 50)]
    _poly(surf, _JACKET, jacket)

    # ── darker-navy lapels flanking the shirt-V so the chest reads as an open
    # jacket-over-shirt. Drawn before the white wedge; the shirt laid on top leaves
    # only the outer lapel edges showing as a darker navy line either side.
    _poly(surf, _LAPEL, [(26, 36), (34, 37), (31, 50)])
    _poly(surf, _LAPEL, [(46, 36), (38, 37), (41, 50)])

    # ── white shirt-front V in the CENTRE of the jacket: apex at the throat
    # widening to ~8px at the belly, split ONLY by a single dark tie stripe. No
    # internal seams — at 40px any extra diagonal inside the wedge reads as noise.
    _poly(surf, _SHIRT, [(36, 36), (32, 50), (40, 50)])
    pygame.draw.line(surf, _TIE, (36, 37), (36, 49), 1)

    # ── three gold jacket buttons down the placket. Top button rides the navy
    # near the collar (gold pops on navy), the lower two on the widening shirt —
    # the row that says "uniform", not just "shirt".
    for by in (40, 44, 48):
        pygame.draw.circle(surf, _GOLD, (38, by), 2)

    # ── captain's-rank sleeve rings: THREE fat gold bands on a navy cuff over the
    # lower blue wing that ride the wing beat. The navy cuff keeps the gaps a clean
    # dark so the three bands never smear into one gold blob at the downscale.
    cuff = int(round(wing_angle_deg * 0.10))
    bx = BCX - 17
    pygame.draw.rect(surf, _CAP_NAVY, (bx - 1, 43 + cuff, 11, 9))
    for sy in (44, 47, 50):
        pygame.draw.rect(surf, _GOLD, (bx, sy + cuff, 9, 2))

    # ── classic aviator shades on the scarlet face (the bird faces RIGHT, so the
    # visible eye is around (HX, HY)). Two dark teardrop lenses — the near one
    # bigger, the far one partly cut by the beak side — joined by a gold bridge,
    # each gold-rimmed, with a single white glint. Painted OVER the red face so
    # the head still reads scarlet around them; the cap crown sits clear above.
    left_lens = [(HX - 7, HY), (HX - 5, HY - 3), (HX - 2, HY - 3),
                 (HX, HY - 1), (HX - 2, HY + 2), (HX - 5, HY + 2)]
    right_lens = [(HX + 2, HY), (HX + 4, HY - 2), (HX + 6, HY - 2),
                  (HX + 7, HY), (HX + 5, HY + 2), (HX + 3, HY + 2)]
    _poly(surf, _AV_LENS, left_lens)
    _poly(surf, _AV_LENS, right_lens)
    # Gold nose-bridge arcing between the two lenses.
    pygame.draw.line(surf, _AV_BRIDGE, (HX - 1, HY - 1), (HX + 2, HY - 1), 1)
    # 1px gold rim on each lens so the frames read as metal at 40px.
    pygame.draw.polygon(surf, _AV_RIM, left_lens, 1)
    pygame.draw.polygon(surf, _AV_RIM, right_lens, 1)
    # White reflection glint on the upper-right of the near lens.
    pygame.draw.circle(surf, _AV_GLINT, (HX - 2, HY - 2), 1)

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
