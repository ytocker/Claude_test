"""Pilot costume — Design 4: VIPER (modern jet-fighter pilot).

Scratch exploration builder wrapped by the store-skin contract, NOT registered
in ``store_skins.BUILDERS``. Exposes ``build`` for the generic ninja_render
harness. The hero read at 40px is a hard sci-fi flight helmet: a smooth gray
dome swallowing the whole head, a mirrored GREEN visor band that glows across
eye level, a chunky charcoal oxygen mask clamped over the beak, and an
olive G-suit body ringed by a SAFETY-ORANGE emergency collar — the fast-jet
aircrew silhouette, all straight edges against the round macaw.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pygame

from game.store_skins import (
    _pal, _build_parrot_with_palette, _make_skin, _poly, HX, HY, CROWN_Y,
)
from game.parrot import SPRITE_W, SPRITE_H, _aaellipse  # noqa: F401  (anchor imports)

# ── palette: re-plumage the macaw in olive G-suit + gray helmet ───────────────
# The helmet is the head, so head_main is already the gray shell and the beak
# region goes charcoal to read as the seam under the oxygen mask; no scarlet or
# lens survives, letting the green visor be the only saturated cool note.
_HELMET      = (122, 128, 135)      # helmet shell gray
_HELMET_HI   = (155, 162, 170)      # dome top highlight
_HELMET_RIM  = (70, 76, 82)         # dark rim seam
_MASK        = (43, 47, 51)         # oxygen mask charcoal
_VISOR       = (28, 224, 160)       # mirrored visor green
_OLIVE       = (91, 107, 58)        # G-suit body
_OLIVE_D     = (65, 78, 38)
_ORANGE      = (242, 101, 34)       # safety collar / patch
_HOSE        = (74, 79, 85)         # oxygen hose

P_VIPER = _pal(
    tail=[(60, 72, 40), (72, 86, 48), (84, 100, 56), (100, 118, 66)],
    tail_line=(48, 58, 32),
    body_shadow=_OLIVE_D,
    body_main=_OLIVE,
    body_chest=(120, 138, 80),
    body_belly=(120, 138, 80),
    sheen=(160, 180, 120, 45),
    wing_main=_OLIVE,
    wing_dark=_OLIVE_D,
    wing_tip=(74, 90, 46),
    wing_secondary=None,
    wing_highlight=(120, 138, 80),
    head_shadow=(90, 96, 102),
    head_main=_HELMET,
    head_cheek=(108, 114, 121),
    head_crown=(122, 128, 135),
    lens_frame=(60, 64, 70),
    lens_body=_MASK,
    lens_tint=None,
    lens_glint=None,
    beak_main=_MASK,
    beak_dark=(28, 32, 36),
    beak_gloss=(60, 64, 70),
    foot=_MASK,
)


def _viper_base(angle_deg):
    # Helmet owns the head — no aviator lenses under the sealed visor.
    return _build_parrot_with_palette(angle_deg, P_VIPER, draw_lenses=False)


def _paint_viper(surf, wing_angle_deg):
    # Body centre in composite space (base body centre (32,32) + PARROT_DY=20).
    BCX, BCY = 32, 52

    # ── additive visor bloom laid down FIRST so the helmet + visor cover it and
    # only a soft green halo bleeds past the seam — sells the mirrored glow.
    glow = pygame.Surface((36, 24), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (12, 90, 64), (0, 0, 36, 24))
    surf.blit(glow, (HX - 18, HY - 12), special_flags=pygame.BLEND_RGB_ADD)

    # ── gray flight helmet — smooth dome swallowing the whole head.
    pygame.draw.ellipse(surf, _HELMET, (HX - 13, CROWN_Y - 2, 28, 24))
    pygame.draw.ellipse(surf, _HELMET_HI, (HX - 8, CROWN_Y - 1, 16, 8))
    pygame.draw.ellipse(surf, _HELMET_RIM, (HX - 13, CROWN_Y - 2, 28, 24), 1)

    # ── mirrored visor band — the KEY TELL, a glowing strip across eye level.
    pygame.draw.rect(surf, (18, 22, 24), (HX - 12, HY - 6, 24, 10), border_radius=2)
    pygame.draw.rect(surf, _VISOR, (HX - 12, HY - 5, 24, 8), border_radius=2)
    pygame.draw.line(surf, (200, 255, 240), (HX - 8, HY - 4), (HX + 6, HY - 3), 2)

    # ── oxygen mask — chunky charcoal block clamped over the beak (silhouette
    # break), fed by a corrugated hose sweeping down to a chest connector.
    _poly(surf, _MASK, [(HX + 2, HY - 2), (HX + 14, HY + 2), (HX + 12, HY + 10),
                        (HX + 1, HY + 8), (HX - 2, HY + 2)])
    pygame.draw.line(surf, _HOSE, (HX + 8, HY + 8), (BCX + 12, BCY - 10), 3)
    pygame.draw.circle(surf, (90, 96, 102), (BCX + 12, BCY - 10), 3)
    pygame.draw.line(surf, (80, 86, 92), (HX + 4, HY - 1), (HX + 12, HY + 2), 1)

    # ── safety-orange emergency collar — the warm COLOR ANCHOR ringing the neck.
    pygame.draw.ellipse(surf, _ORANGE, (BCX - 8, BCY - 17, 24, 10))
    pygame.draw.ellipse(surf, (190, 75, 24), (BCX - 8, BCY - 17, 24, 10), 2)

    # ── shoulder patch on the wing root — a bright rank tab that rides the flap.
    pygame.draw.rect(surf, _ORANGE, (BCX - 12, BCY - 10, 8, 5), border_radius=1)
    pygame.draw.rect(surf, (20, 20, 20), (BCX - 12, BCY - 10, 8, 5), 1, border_radius=1)


build = _make_skin(_paint_viper, base_fn=_viper_base)
