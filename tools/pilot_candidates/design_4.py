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
_HELMET       = (122, 128, 135)     # helmet shell gray
_HELMET_HI    = (155, 162, 170)     # dome top highlight
_HELMET_CROWN = (142, 148, 155)     # lifted top-right crown so the head separates
_HELMET_RIM   = (70, 76, 82)        # dark rim seam
_MASK         = (43, 47, 51)        # oxygen mask charcoal
_MASK_RIM     = (74, 79, 85)        # lit mask edge so it reads a separate chunk
_VISOR        = (28, 224, 160)      # mirrored visor green (band top)
_VISOR_D      = (10, 110, 88)       # visor band bottom (the mirror falloff)
_VISOR_SPEC   = (124, 255, 216)     # specular streak across the mirror
_OLIVE        = (91, 107, 58)       # G-suit body
_OLIVE_D      = (65, 78, 38)
_ORANGE       = (242, 101, 34)      # safety collar / rank patch
_ORANGE_D     = (190, 75, 24)
_HOSE         = (74, 79, 85)        # oxygen hose (corrugation ridges)
_HOSE_SEG     = _MASK               # darker corrugation valleys

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

    # ── faint additive visor bloom, kept subtle so the crisp band below (not a
    # wash) does the selling — only a soft green halo bleeds past the seam.
    glow = pygame.Surface((28, 16), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (10, 72, 52), (0, 0, 28, 16))
    surf.blit(glow, (HX - 14, HY - 9), special_flags=pygame.BLEND_RGB_ADD)

    # ── gray flight helmet — smooth dome swallowing the whole head. The crown is
    # lifted a step on the top-right curve so the helmet separates from the olive
    # body against the sky, the #1 gripe when both read as one grey-green mass.
    pygame.draw.ellipse(surf, _HELMET, (HX - 13, CROWN_Y - 2, 28, 24))
    pygame.draw.ellipse(surf, _HELMET_CROWN, (HX - 2, CROWN_Y - 1, 13, 8))
    pygame.draw.ellipse(surf, _HELMET_HI, (HX - 8, CROWN_Y, 12, 5))
    pygame.draw.ellipse(surf, _HELMET_RIM, (HX - 13, CROWN_Y - 2, 28, 24), 1)

    # ── mirrored visor — ONE clean horizontal slot across the eyes (the KEY
    # TELL). A bright top row falling to a dark bottom row reads as a mirror, and
    # a specular streak angled down-right is the glint that says "jet visor" at
    # 40px. Framed dark so it reads as a slot cut into the helmet, not a sticker.
    pygame.draw.rect(surf, (16, 20, 22), (HX - 8, HY - 6, 18, 6), border_radius=1)
    pygame.draw.rect(surf, _VISOR,   (HX - 7, HY - 5, 16, 2))
    pygame.draw.rect(surf, _VISOR_D, (HX - 7, HY - 3, 16, 2))
    pygame.draw.line(surf, _VISOR_SPEC, (HX - 4, HY - 5), (HX + 5, HY - 2), 2)

    # ── oxygen mask — a chunky charcoal LUMP cupping the beak/lower face, its tip
    # punched ~2px past the beak so it breaks the round silhouette (the #1 jet-
    # pilot tell). A lit rim on the top + left edge makes it read as a separate
    # chunk clamped onto the grey helmet rather than more shell.
    mask = [(HX - 3, HY + 2), (HX + 8, HY + 1), (HX + 17, HY + 4),
            (HX + 13, HY + 8), (HX, HY + 10), (HX - 3, HY + 6)]
    _poly(surf, _MASK, mask)
    pygame.draw.lines(surf, _MASK_RIM, False,
                      [(HX - 3, HY + 6), (HX - 3, HY + 2), (HX + 8, HY + 1),
                       (HX + 17, HY + 4)], 1)
    pygame.draw.circle(surf, (28, 32, 36), (HX + 6, HY + 5), 2)   # breather valve

    # ── corrugated oxygen hose from the mask bottom curving down-left to a chest
    # connector — the life-support silhouette-breaker. Alternating ridge/valley
    # segments give the ribbed look; the mid-dip bulges it below the neckline.
    p0, ctrl, p1 = (HX + 1, HY + 10), (HX - 6, HY + 16), (BCX + 2, BCY + 1)
    hose = []
    for i in range(11):
        t = i / 10.0
        mt = 1 - t
        hose.append((mt * mt * p0[0] + 2 * mt * t * ctrl[0] + t * t * p1[0],
                     mt * mt * p0[1] + 2 * mt * t * ctrl[1] + t * t * p1[1]))
    for i in range(len(hose) - 1):
        c = _HOSE if i % 2 == 0 else _HOSE_SEG
        pygame.draw.line(surf, c, hose[i], hose[i + 1], 2)
    pygame.draw.circle(surf, (90, 96, 102), p1, 3)
    pygame.draw.circle(surf, _MASK, p1, 3, 1)

    # ── safety-orange emergency collar — pulled DOWN to a thin arc hugging the
    # top of the olive chest so charcoal mask + orange collar read as two
    # distinct tells, not one confusing orange slab floating mid-face.
    collar = [(BCX - 2, BCY - 7), (BCX + 1, BCY - 3), (BCX + 6, BCY - 1),
              (BCX + 11, BCY - 3), (BCX + 14, BCY - 7)]
    pygame.draw.lines(surf, _ORANGE_D, False, [(x, y + 2) for x, y in collar], 3)
    pygame.draw.lines(surf, _ORANGE, False, collar, 3)

    # ── rank patch riding the upper wing/shoulder — cheap identity, a bright
    # safety-orange tab on the olive mass that flaps with the beat. Kept to the
    # shoulder (clear of the collar arc) so it reads as a second small warm mark.
    pygame.draw.rect(surf, _ORANGE, (25, 42, 4, 4), border_radius=1)
    pygame.draw.rect(surf, _ORANGE_D, (25, 42, 4, 4), 1, border_radius=1)
    pygame.draw.line(surf, (255, 190, 140), (26, 43), (27, 43), 1)


build = _make_skin(_paint_viper, base_fn=_viper_base)
