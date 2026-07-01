"""Soccer v8 Design 1 — FC BARCELONA (Blaugrana) — R2 revision.

The R1 version used royal blue as the jersey base, which collided with the
macaw's own blue wings. This revision inverts the dominant colour: the body
oval is re-plumaged deep garnet (dark crimson-purple), and the _paint pass
clips to the oval and paints wider navy stripes over it. The result is a
garnet-dominant jersey with 4 navy vertical bands — the same blaugrana read
with no hue collision against the bird's red head or blue wings.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

_GARNET  = (120,  22,  50)   # dark garnet — base body colour
_GARNET_D = ( 80,  12,  30)
_GARNET_L = (150,  40,  70)  # lighter garnet for chest
_NAVY    = (  8,  40, 110)   # navy stripes (distinct from macaw-blue wings)
_NAVY_D  = (  4,  25,  75)
_GOLD    = (255, 196,  32)
_WHITE   = (245, 245, 250)
_SHORTS  = (  8,  40, 110)   # navy shorts matching the stripe
_SHORTS_D = (  4,  25,  75)
_SCK     = (245, 245, 250)
_SCK_H   = (120,  22,  50)   # garnet sock hoop
_CLEAT   = ( 28,  28,  36)

_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=( 80,  12,  30),
    body_main=(120,  22,  50),
    body_chest=(150,  40,  70),
    body_belly=( 95,  15,  38),
    sheen=(200, 80, 110, 60),
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
    # Blaugrana stripe pattern: garnet base (palette), navy bands over it.
    # 5 px navy stripes every 9 px = 4 navy bands across the 38 px body oval.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX - 19, BCY - 14, 38, 28))
    for x in range(BCX - 16, BCX + 20, 9):
        pygame.draw.rect(surf, _NAVY, (x, BCY - 14, 5, 28))
    surf.set_clip(clip_prev)
    pygame.draw.ellipse(surf, _GARNET_D, (BCX - 19, BCY - 14, 38, 28), 1)

    # White crew collar just below the head-body junction.
    pygame.draw.line(surf, _WHITE, (BCX - 7, BCY - 12), (BCX + 9, BCY - 12), 2)
    pygame.draw.line(surf, _GARNET_D, (BCX - 7, BCY - 11), (BCX + 9, BCY - 11), 1)

    # Gold crest badge on garnet upper chest — large enough to survive 40px.
    pygame.draw.circle(surf, _GARNET_D, (BCX + 5, BCY - 5), 5)
    pygame.draw.circle(surf, _GOLD, (BCX + 5, BCY - 5), 4)

    # Sleeve seam arcs at wing roots.
    pygame.draw.line(surf, _GARNET_D, (BCX + 8, BCY - 11), (BCX + 17, BCY - 5), 1)
    pygame.draw.line(surf, _GARNET_D, (BCX - 6, BCY - 11), (BCX - 14, BCY - 5), 1)

    # Thin gold hem stripe at jersey bottom.
    pygame.draw.ellipse(surf, _GOLD, (BCX - 9, BCY + 5, 20, 3), 1)

    # Navy shorts matching the stripe colour.
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
