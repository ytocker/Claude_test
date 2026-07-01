"""Soccer v8 Design 3 — AC MILAN (Rossoneri) — R2 revision.

The R1 version used a red palette base, which collided with the macaw's own
red head. This revision inverts the dominant colour: the body oval is re-
plumaged near-black via palette, and the _paint pass clips to the oval and
paints two milan-red bands over the black base. Black-dominant rossoneri
(3 black + 2 red) avoids the head collision and reads instantly at 40px.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

_BLACK   = ( 10,  10,  12)   # near-black base (dominant colour)
_BLACK_M = ( 22,  22,  26)   # mid-black for outline
_RED     = (200,  30,  30)   # milan red (painted bands only)
_RED_D   = (140,  15,  15)
_WHITE   = (245, 245, 250)
_WHITE_D = (200, 200, 210)
_GOLD    = (200, 155,  30)
_SHORTS  = (245, 245, 250)   # white shorts (Milan's home pairing)
_SHORTS_D = (200, 200, 210)
_SCK     = (245, 245, 250)
_SCK_H   = (200,  30,  30)
_CLEAT   = ( 28,  28,  36)

_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(  6,   6,   8),
    body_main=( 10,  10,  12),
    body_chest=( 18,  18,  22),
    body_belly=(  7,   7,   9),
    sheen=( 60,  60,  80,  60),
    wing_main=BIRD_WING, wing_dark=BIRD_WING_D, wing_tip=BIRD_TIP,
    wing_secondary=(255, 200, 60), wing_highlight=(170, 210, 255),
    head_shadow=(150, 15, 20), head_main=BIRD_RED,
    head_cheek=(255, 130, 130), head_crown=(255, 170, 170),
    lens_frame=(255, 200, 50), lens_body=(20, 20, 30),
    lens_tint=(35, 55, 90, 130), lens_glint=(255, 255, 255),
    beak_main=BIRD_BEAK, beak_dark=BIRD_BEAK_D,
    beak_gloss=(255, 230, 150), foot=BIRD_BEAK_D,
)

BCX, BCY = 32, 52


def _base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # Rossoneri stripe pattern (inverted — black dominant): clip to body oval,
    # paint two milan-red bands over the near-black base.
    # Black|Red|Black|Red|Black = 3 black sections + 2 red bands across 38 px.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX - 19, BCY - 14, 38, 28))
    pygame.draw.rect(surf, _RED, (BCX - 13, BCY - 14, 7, 28))
    pygame.draw.rect(surf, _RED, (BCX +  4, BCY - 14, 7, 28))
    surf.set_clip(clip_prev)
    pygame.draw.ellipse(surf, _BLACK_M, (BCX - 19, BCY - 14, 38, 28), 1)

    # White crew collar on the near-black jersey.
    pygame.draw.line(surf, _WHITE, (BCX - 7, BCY - 12), (BCX + 9, BCY - 12), 2)
    pygame.draw.line(surf, _BLACK_M, (BCX - 7, BCY - 11), (BCX + 9, BCY - 11), 1)

    # Gold crest badge on the black upper-chest panel.
    pygame.draw.circle(surf, _BLACK_M, (BCX + 5, BCY - 5), 5)
    pygame.draw.circle(surf, _GOLD, (BCX + 5, BCY - 5), 4)

    # Sleeve seam arcs.
    pygame.draw.line(surf, _BLACK_M, (BCX + 8, BCY - 11), (BCX + 17, BCY - 5), 1)
    pygame.draw.line(surf, _BLACK_M, (BCX - 6, BCY - 11), (BCX - 14, BCY - 5), 1)

    # Thin dark hem line.
    pygame.draw.ellipse(surf, _BLACK_M, (BCX - 9, BCY + 5, 20, 3), 1)

    # White shorts (Milan's home kit pairing with red/black jersey).
    pygame.draw.ellipse(surf, _SHORTS, (BCX - 9, BCY + 6, 20, 9))
    pygame.draw.ellipse(surf, _SHORTS_D, (BCX - 9, BCY + 6, 20, 9), 1)

    # White socks, red hoop.
    for sx in (27, 35):
        pygame.draw.line(surf, _SCK, (sx, BCY + 11), (sx, BCY + 16), 4)
        pygame.draw.line(surf, _SCK_H, (sx, BCY + 12), (sx, BCY + 14), 3)

    # Near-black cleats.
    for cx in (23, 31):
        pygame.draw.rect(surf, _CLEAT, (cx, BCY + 14, 9, 5), border_radius=1)


build = _make_skin(_paint, base_fn=_base)
