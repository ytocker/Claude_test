"""Soccer v11 Design 1 — THE STRIKER.

A predominantly WHITE match jersey accented by three thin royal-blue
stripes, a bold squad number "9" on a clear chest panel, and a
black-and-white soccer ball at the feet — the primary identity prop.
Body oval is re-plumaged via the palette system; head stays macaw-red,
wings macaw-blue.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

_ROYAL   = ( 26,  62, 160)
_ROYAL_D = ( 16,  40, 112)
_WHITE   = (240, 240, 245)
_SEAM    = (150, 155, 175)
_CLEAT   = ( 24,  24,  32)

_PAL = _pal(
    tail=[(200,30,40),(240,95,40),(255,160,55),(255,220,80)],
    tail_line=(170,25,25),
    body_shadow=(180,185,205),
    body_main=(240,240,245),
    body_chest=(248,248,252),
    body_belly=(215,218,230),
    sheen=(255,255,255,100),
    wing_main=BIRD_WING, wing_dark=BIRD_WING_D, wing_tip=BIRD_TIP,
    wing_secondary=(255,200,60), wing_highlight=(170,210,255),
    head_shadow=(150,15,20), head_main=BIRD_RED,
    head_cheek=(255,130,130), head_crown=(255,170,170),
    lens_frame=(255,200,50), lens_body=(20,20,30),
    lens_tint=(35,55,90,130), lens_glint=(255,255,255),
    beak_main=BIRD_BEAK, beak_dark=BIRD_BEAK_D,
    beak_gloss=(255,230,150), foot=BIRD_BEAK_D,
)

BCX, BCY = 32, 52


def _base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # Thin outline anchors the white jersey against a bright sky.
    pygame.draw.ellipse(surf, (185,188,205), (BCX-19,BCY-14,38,28), 1)

    # Three thin royal stripes over the right of the chest — kept off the
    # centre-left so WHITE reads as the jersey field, not a blue box.
    old_clip = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX-19, BCY-14, 38, 28))
    for sx in (BCX+4, BCX+9, BCX+14):
        pygame.draw.rect(surf, _ROYAL, (sx, BCY-14, 2, 28))
    surf.set_clip(old_clip)

    # Royal V-collar below the red head.
    pygame.draw.line(surf, _ROYAL, (BCX-6, BCY-12), (BCX+2, BCY-8), 2)
    pygame.draw.line(surf, _ROYAL, (BCX+8, BCY-12), (BCX+2, BCY-8), 2)

    # Squad "9" — bold royal annular bowl + thick tail on the clear
    # white chest panel, ringed by a 1px dark edge so it never fades out.
    nx, ny = BCX-9, BCY-3
    pygame.draw.circle(surf, _ROYAL_D, (nx, ny), 5)
    pygame.draw.circle(surf, _ROYAL,   (nx, ny), 4)
    pygame.draw.circle(surf, _WHITE,   (nx, ny), 1)
    pygame.draw.line(surf, _ROYAL_D, (nx+4, ny), (nx+1, ny+8), 5)
    pygame.draw.line(surf, _ROYAL,   (nx+3, ny), (nx+1, ny+7), 3)

    # Hard hem seam — a crisp 2px step from jersey to shorts.
    pygame.draw.line(surf, _SEAM, (BCX-9, BCY+5), (BCX+11, BCY+5), 2)

    # Royal-blue shorts.
    pygame.draw.ellipse(surf, _ROYAL,   (BCX-9,BCY+6,20,9))
    pygame.draw.ellipse(surf, _ROYAL_D, (BCX-9,BCY+6,20,9), 1)
    _poly(surf, _WHITE, [(BCX-1,BCY+12),(BCX+3,BCY+12),(BCX+1,BCY+15)])

    # Two short white sock stubs + two near-black cleat blocks — no warm
    # sole stripe, which would fight the macaw's orange tail.
    for sx in (27, 35):
        pygame.draw.line(surf, _WHITE, (sx, BCY+12), (sx, BCY+15), 4)
    for cx in (23, 31):
        pygame.draw.rect(surf, _CLEAT, (cx, BCY+14, 9, 5), border_radius=2)

    # Soccer ball — the #1 identity prop, drawn LAST. Nudged left so the
    # black pentagons clear the orange tail-fire behind it.
    bx, by = BCX-10, BCY+24
    pygame.draw.circle(surf, (235,235,235), (bx, by), 6)
    pygame.draw.circle(surf, (20,20,20),    (bx, by), 6, 1)
    for px, py in [(bx-2,by-3),(bx+3,by-1),(bx-1,by+3)]:
        pygame.draw.circle(surf, (20,20,20), (px,py), 2)


build = _make_skin(_paint, base_fn=_base)
