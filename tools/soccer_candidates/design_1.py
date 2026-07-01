"""Soccer v8 Design 1 — FC BARCELONA (Blaugrana).

Inspired by FC Barcelona's iconic blaugrana kit: alternating deep-blue and
garnet vertical stripes across the full body oval. The palette sets the body
base to royal blue; the _paint pass clips to the oval and paints garnet bands
every 7 px, giving 5 garnet stripes over a blue base. Gold crest badge on
upper chest, white crew collar. Head stays macaw-red, wings macaw-blue.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

_BLUE    = ( 26,  63, 155)
_BLUE_D  = ( 15,  40, 105)
_GARNET  = (153,  28,  65)
_GARNET_D = (100,  15,  40)
_GOLD    = (255, 196,  32)
_WHITE   = (245, 245, 250)
_SHORTS  = ( 26,  63, 155)
_SHORTS_D = ( 15,  40, 105)
_SCK     = (245, 245, 250)
_SCK_H   = (153,  28,  65)
_CLEAT   = ( 28,  28,  36)

_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=( 15,  40, 105),
    body_main=( 26,  63, 155),
    body_chest=( 35,  80, 175),
    body_belly=( 18,  50, 128),
    sheen=(80, 120, 220, 80),
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
    # Blaugrana stripe pattern: clip to body oval, paint garnet bands over blue.
    # 4 px garnet every 7 px = 5–6 visible garnet stripes at this scale.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX - 19, BCY - 14, 38, 28))
    for x in range(BCX - 18, BCX + 20, 7):
        pygame.draw.rect(surf, _GARNET, (x, BCY - 14, 4, 28))
    surf.set_clip(clip_prev)
    pygame.draw.ellipse(surf, _BLUE_D, (BCX - 19, BCY - 14, 38, 28), 1)

    # White crew collar just below the head-body junction.
    pygame.draw.line(surf, _WHITE, (BCX - 7, BCY - 12), (BCX + 9, BCY - 12), 2)
    pygame.draw.line(surf, _BLUE_D, (BCX - 7, BCY - 11), (BCX + 9, BCY - 11), 1)

    # Gold crest badge on upper chest (circular pip).
    pygame.draw.circle(surf, _GARNET_D, (BCX + 4, BCY - 5), 4)
    pygame.draw.circle(surf, _GOLD, (BCX + 4, BCY - 5), 3)

    # Sleeve seam arcs — light marks at wing roots anchor the jersey read.
    pygame.draw.line(surf, _BLUE_D, (BCX + 8, BCY - 11), (BCX + 17, BCY - 5), 1)
    pygame.draw.line(surf, _BLUE_D, (BCX - 6, BCY - 11), (BCX - 14, BCY - 5), 1)

    # Thin gold hem stripe at jersey bottom.
    pygame.draw.ellipse(surf, _GOLD, (BCX - 9, BCY + 5, 20, 3), 1)

    # Royal-blue shorts.
    pygame.draw.ellipse(surf, _SHORTS, (BCX - 9, BCY + 6, 20, 9))
    pygame.draw.ellipse(surf, _SHORTS_D, (BCX - 9, BCY + 6, 20, 9), 1)

    # White socks, garnet turn-over hoop.
    for sx in (27, 35):
        pygame.draw.line(surf, _SCK, (sx, BCY + 11), (sx, BCY + 16), 4)
        pygame.draw.line(surf, _SCK_H, (sx, BCY + 12), (sx, BCY + 14), 3)

    # Near-black cleats.
    for cx in (23, 31):
        pygame.draw.rect(surf, _CLEAT, (cx, BCY + 14, 9, 5), border_radius=1)


build = _make_skin(_paint, base_fn=_base)
