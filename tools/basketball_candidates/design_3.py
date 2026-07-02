"""Basketball costume — Design 3: THE RETRO '80s LEGEND.

A scratch exploration builder (never registered in store_skins.BUILDERS). The
read at 40px is a Celtics-green tank with a white chest stripe + "33", short
retro shorts, canvas high-tops, a thin brow headband, and a basketball held in
a passing pose near the near wing. The green body is a full re-plumage via the
palette system so the white kit trim reads as bright lines on green, not on
scarlet; the head stays the scarlet macaw so Pip is still recognisable.
"""
import math
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

# Body centre in composite space (parrot body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52

# Celtics green re-plumage; head stays scarlet so Pip's face is untouched. The
# kit trim (white/gold) is painted on top, so the body slots below feed the
# green mass the stripe + number sit against.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(0, 90, 45),
    body_main=(0, 130, 60),           # Celtics green
    body_chest=(10, 150, 70),
    body_belly=(0, 100, 45),
    sheen=(100, 255, 150, 50),
    wing_main=BIRD_WING, wing_dark=BIRD_WING_D, wing_tip=BIRD_TIP,
    wing_secondary=(255, 200, 60), wing_highlight=(170, 210, 255),
    head_shadow=(150, 15, 20), head_main=BIRD_RED,
    head_cheek=(255, 130, 130), head_crown=(255, 170, 170),
    lens_frame=(255, 200, 50), lens_body=(20, 20, 30),
    lens_tint=(35, 55, 90, 130), lens_glint=(255, 255, 255),
    beak_main=BIRD_BEAK, beak_dark=BIRD_BEAK_D,
    beak_gloss=(255, 230, 150), foot=BIRD_BEAK_D,
)

_GREEN = (0, 130, 60)
_GREEN_D = (0, 90, 45)
_WHITE = (245, 245, 248)
_GOLD = (200, 160, 10)             # Celtic shamrock gold trim
_CREAM = (240, 235, 215)           # Converse canvas


def _base(angle_deg):
    # Green-bodied macaw keeping the scarlet head + aviators; the tank + number
    # paint over the green torso.
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # Torso keyline so the tank stays welded to the green body mass at 40px.
    pygame.draw.ellipse(surf, _GREEN_D, (BCX - 19, BCY - 14, 38, 28), 1)

    # Sleeveless tank — narrow white shoulder straps in the Celtics retro cut.
    pygame.draw.line(surf, _WHITE, (BCX - 12, BCY - 13), (BCX - 9, BCY + 2), 2)
    pygame.draw.line(surf, _WHITE, (BCX + 10, BCY - 13), (BCX + 7, BCY + 2), 2)

    # White horizontal chest stripe with thin gold edges — the alternating
    # heritage band.
    pygame.draw.rect(surf, _WHITE, (BCX - 17, BCY - 5, 34, 4))
    pygame.draw.rect(surf, _GOLD, (BCX - 17, BCY - 5, 34, 1))
    pygame.draw.rect(surf, _GOLD, (BCX - 17, BCY - 2, 34, 1))

    # "33" in green on the white stripe — two block threes, centred.
    nx, ny = BCX - 5, BCY - 3
    pygame.draw.line(surf, _GREEN, (nx - 3, ny - 3), (nx + 2, ny - 3), 2)
    pygame.draw.line(surf, _GREEN, (nx - 3, ny), (nx + 2, ny), 2)
    pygame.draw.line(surf, _GREEN, (nx - 3, ny + 3), (nx + 2, ny + 3), 2)
    pygame.draw.line(surf, _GREEN, (nx + 2, ny - 3), (nx + 2, ny + 3), 2)
    nx2 = nx + 8
    pygame.draw.line(surf, _GREEN, (nx2 - 3, ny - 3), (nx2 + 2, ny - 3), 2)
    pygame.draw.line(surf, _GREEN, (nx2 - 3, ny), (nx2 + 2, ny), 2)
    pygame.draw.line(surf, _GREEN, (nx2 - 3, ny + 3), (nx2 + 2, ny + 3), 2)
    pygame.draw.line(surf, _GREEN, (nx2 + 2, ny - 3), (nx2 + 2, ny + 3), 2)

    # Hem seam under the tank.
    pygame.draw.line(surf, _GREEN_D, (BCX - 15, BCY + 5), (BCX + 13, BCY + 5), 1)

    # SHORT shorts — the retro tell (short, not baggy) with green side stripes.
    pygame.draw.ellipse(surf, _WHITE, (BCX - 9, BCY + 5, 20, 8))
    pygame.draw.ellipse(surf, (200, 205, 215), (BCX - 9, BCY + 5, 20, 8), 1)
    pygame.draw.line(surf, _GREEN, (BCX + 9, BCY + 6), (BCX + 9, BCY + 12), 2)
    pygame.draw.line(surf, _GREEN, (BCX - 11, BCY + 6), (BCX - 11, BCY + 12), 2)

    # Canvas Converse high-tops — classic cream low-ankle silhouette with a
    # green toe-cap dot.
    for hx in (22, 30):
        pygame.draw.rect(surf, (210, 210, 210), (hx, BCY + 13, 10, 4), border_radius=1)
        pygame.draw.rect(surf, _CREAM, (hx, BCY + 9, 10, 5), border_radius=2)
        pygame.draw.ellipse(surf, _CREAM, (hx + 1, BCY + 7, 8, 5))
        pygame.draw.circle(surf, _GREEN, (hx + 5, BCY + 10), 2)

    # Thin '80s brow headband across the crown.
    pygame.draw.line(surf, _WHITE, (HX - 10, CROWN_Y + 5), (HX + 10, CROWN_Y + 4), 3)
    pygame.draw.line(surf, _GREEN, (HX - 10, CROWN_Y + 4), (HX + 10, CROWN_Y + 3), 1)

    # Basketball in the "PASS" pose near the near wing — drawn LAST so it sits
    # over the kit as the held ball.
    bx, by = BCX + 12, BCY - 2
    pygame.draw.circle(surf, (230, 115, 30), (bx, by), 7)
    pygame.draw.circle(surf, (20, 20, 20), (bx, by), 7, 1)
    pygame.draw.line(surf, (20, 20, 20), (bx, by - 7), (bx, by + 7), 1)
    pygame.draw.arc(surf, (20, 20, 20), (bx - 9, by - 7, 12, 14), 0.3, math.pi - 0.3, 1)
    pygame.draw.arc(surf, (20, 20, 20), (bx - 3, by - 7, 12, 14), math.pi + 0.3, 2 * math.pi - 0.3, 1)


build = _make_skin(_paint, base_fn=_base)
