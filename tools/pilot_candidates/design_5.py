"""Pilot costume — Design 5: BUSH RUNNER (barnstormer / bush pilot).

Scratch exploration builder wrapped by the store-skin contract, NOT registered
in ``store_skins.BUILDERS``. Exposes ``build`` for the generic ninja_render
harness. The hero read at 40px is round BRASS GOGGLES worn DOWN OVER THE EYES
(the tell that sets it apart from the brow-goggle Ace), a battered soft canvas
flight cap, and a rolled MAP cylinder peeking from the wing-root — a scruffy,
gear-laden working pilot instead of a polished uniform.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pygame

from game.store_skins import (
    _pal, _build_parrot_with_palette, _make_skin, _poly, HX, HY, CROWN_Y,
)

# ── palette: re-plumage the macaw in warm field khaki ────────────────────────
# Khaki body so the brass goggles + pale map read as high-value marks ON warm
# canvas instead of gold-on-red; the head takes the canvas-cap tone so the soft
# cap welds to the crown, and the beak stays a warm bone so nothing scarlet
# survives the two-tone.
_CAP_CANVAS = (122, 106, 74)        # floppy cap body / head
_CAP_SHADOW = (92, 78, 54)          # cap creases
_BRASS      = (201, 162, 74)        # goggle rings / buckle
_GLASS      = (58, 74, 85)          # tinted lens fill
_KHAKI      = (184, 166, 108)       # shirt / belly
_MAP_PAPER  = (231, 219, 184)       # rolled map
_MAP_ROUTE  = (184, 92, 56)         # route lines on the map
_LEATHER    = (92, 70, 40)          # harness strap

P_BUSH = _pal(
    tail=[(120, 102, 68), (130, 110, 74), (140, 120, 82), (150, 130, 90)],
    tail_line=(96, 80, 52),
    body_shadow=(110, 90, 60),
    body_main=(150, 130, 90),
    body_chest=(196, 178, 120),
    body_belly=_KHAKI,
    sheen=(236, 224, 190, 55),
    wing_main=(130, 110, 74),
    wing_dark=(100, 84, 56),
    wing_tip=(146, 126, 86),
    wing_secondary=None,
    wing_highlight=(168, 148, 104),
    head_shadow=(92, 78, 54),
    head_main=_CAP_CANVAS,
    head_cheek=(140, 122, 88),
    head_crown=(134, 116, 82),
    lens_frame=(110, 90, 60),
    lens_body=_GLASS,
    lens_tint=None,
    lens_glint=None,
    beak_main=(180, 158, 90),
    beak_dark=(130, 105, 55),
    beak_gloss=(224, 204, 140),
    foot=(110, 90, 60),
)


def _bush_base(angle_deg):
    # Khaki-plumaged bird, no aviators — the brass goggles own the eye cluster.
    return _build_parrot_with_palette(angle_deg, P_BUSH, draw_lenses=False)


def _paint_bush(surf, wing_angle_deg):
    # Body centre in composite space (base body centre (32,32) + PARROT_DY=20).
    BCX, BCY = 32, 52

    # ── rolled map tucked at the wing-root (drawn FIRST so the body/wing overlap
    # its inner end and only the cylinder peeks out during the flap — the unique
    # "on a mission" cargo prop no polished uniform carries).
    pygame.draw.rect(surf, _MAP_PAPER, (BCX - 14, BCY - 2, 12, 6), border_radius=3)
    pygame.draw.ellipse(surf, (215, 202, 164), (BCX - 15, BCY - 1, 4, 4))
    pygame.draw.line(surf, _MAP_ROUTE, (BCX - 13, BCY + 1), (BCX - 4, BCY + 1), 1)
    pygame.draw.line(surf, _MAP_ROUTE, (BCX - 11, BCY + 3), (BCX - 5, BCY + 3), 1)

    # ── khaki shirt + diagonal leather harness strap shoulder-to-hip, with one
    # brass buckle so the rig reads as working gear, not bare plumage.
    pygame.draw.line(surf, _LEATHER, (BCX - 8, BCY - 14), (BCX + 10, BCY + 4), 3)
    pygame.draw.rect(surf, _BRASS, (BCX + 1, BCY - 5, 5, 4))
    pygame.draw.rect(surf, _LEATHER, (BCX + 2, BCY - 4, 3, 2))

    # ── battered soft canvas flight cap — a floppy rounded polygon over the crown
    # (saggier than the rigid officer caps), with a shadow crease across the top
    # and an ear-strap flap at the side.
    cap = [(HX - 10, CROWN_Y + 3), (HX - 5, CROWN_Y - 4), (HX + 6, CROWN_Y - 5),
           (HX + 10, CROWN_Y + 2), (HX + 9, CROWN_Y + 9), (HX - 8, CROWN_Y + 9)]
    _poly(surf, _CAP_CANVAS, cap)
    pygame.draw.line(surf, _CAP_SHADOW, (HX - 3, CROWN_Y + 1), (HX + 7, CROWN_Y - 2), 1)
    pygame.draw.rect(surf, _CAP_SHADOW, (HX + 9, CROWN_Y + 6, 4, 5))

    # ── round goggles worn DOWN OVER THE EYES (the hero read + the tell that
    # separates the bush pilot from the brow-goggle Ace): two big tinted lenses in
    # bright brass rings, bridged, each with a white glint, and a strap up to the
    # cap on one side.
    pygame.draw.line(surf, (160, 130, 60), (HX - 4, HY - 4), (HX - 10, CROWN_Y + 8), 1)
    for cx in (HX + 1, HX + 8):
        pygame.draw.circle(surf, _GLASS, (cx, HY - 4), 5)
        pygame.draw.circle(surf, _BRASS, (cx, HY - 4), 5, 2)
        pygame.draw.circle(surf, (255, 255, 255), (cx - 2, HY - 6), 1)
    pygame.draw.line(surf, _BRASS, (HX + 4, HY - 4), (HX + 6, HY - 4), 3)


build = _make_skin(_paint_bush, base_fn=_bush_base)
