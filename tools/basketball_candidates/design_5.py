"""THE STREETBALLER — the basketball candidate (DESIGN 5 of 5).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
roster is untouched.

Concept: the pickup-game blacktop look. Where the other kits read as team
uniforms, this one has no affiliation at all — a sleeveless jersey with a
charcoal shoulder yoke and a bold white "1", the longest baggy CHARCOAL shorts
in the set, and thick white-midsole high-tops as the streetball tell. The wing
is muted to charcoal/grey so the jersey reads as fabric instead of parrot
plumage. The #1 identity prop is a BASKETBALL held below the body against clear
sky — drawn LAST — where its hot orange pops instead of drowning in the warm
tail. The scarlet macaw head still crowns the kit so Pip is still Pip.
"""
import math

import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

BCX, BCY = 32, 52

# Neutral concrete-grey re-plumage: the torso goes flat grey so the jersey
# reads as fabric across the whole vest. The wing is muted to charcoal/grey too
# — a rainbow wing reads as parrot, not baller — leaving the scarlet macaw head
# and the hot basketball as the only saturated notes so Pip is still Pip.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(100, 100, 110),
    body_main=(135, 135, 145),       # concrete grey
    body_chest=(148, 148, 158),
    body_belly=(115, 115, 125),
    sheen=(200, 200, 215, 50),
    wing_main=(80, 80, 90),
    wing_dark=(55, 55, 65),
    wing_tip=(100, 100, 112),
    wing_secondary=(110, 112, 122),
    wing_highlight=(140, 142, 155),
    head_shadow=(150, 15, 20), head_main=BIRD_RED,
    head_cheek=(255, 130, 130), head_crown=(255, 170, 170),
    lens_frame=(255, 200, 50), lens_body=(20, 20, 30),
    lens_tint=(35, 55, 90, 130), lens_glint=(255, 255, 255),
    beak_main=BIRD_BEAK, beak_dark=BIRD_BEAK_D,
    beak_gloss=(255, 230, 150), foot=BIRD_BEAK_D,
)

_GREY     = (135, 135, 145)
_CHARCOAL = (48, 48, 58)             # shorts + jersey trim
_WHITE    = (240, 240, 245)
_J_BLACK  = (28, 28, 36)             # high-top black upper
_J_WHITE  = (240, 238, 230)          # thick white midsole — the shoe tell
_J_RED    = (200, 30, 40)            # ankle-collar accent


def _base(angle_deg):
    # Concrete-grey body + muted grey wing, scarlet macaw head, court shades.
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # Thin outline around the torso so the grey vest separates from a pale sky
    # instead of washing into it.
    pygame.draw.ellipse(surf, (100, 100, 110), (BCX - 19, BCY - 14, 38, 28), 1)

    # Charcoal shoulder yoke across the top of the body — a bold dark band that
    # reads instantly as a jersey collar/yoke at 40px, replacing the sub-pixel
    # mesh-dot field that just looked like noise.
    pygame.draw.line(surf, (60, 60, 70), (BCX - 15, BCY - 11), (BCX + 13, BCY - 11), 3)

    # Sleeveless armholes — charcoal seams where the arms pass through the vest,
    # the tell that says "tank", not a sleeved sweater.
    pygame.draw.line(surf, _CHARCOAL, (BCX - 17, BCY - 13), (BCX - 12, BCY + 3), 2)
    pygame.draw.line(surf, _CHARCOAL, (BCX + 15, BCY - 13), (BCX + 10, BCY + 3), 2)

    # Bold white "1" at chest centre — a thick vertical stroke with a short top
    # flag, unaffiliated, so the vest reads as a plain pickup jersey and the
    # number carries across the whole panel instead of vanishing.
    pygame.draw.line(surf, _WHITE, (BCX + 1, BCY - 7), (BCX + 1, BCY + 3), 4)
    pygame.draw.line(surf, _WHITE, (BCX - 3, BCY - 6), (BCX + 1, BCY - 7), 4)

    # Hem seam so the vest reads as a garment edge, not paint.
    pygame.draw.line(surf, _CHARCOAL, (BCX - 12, BCY + 5), (BCX + 12, BCY + 5), 1)

    # Baggy charcoal shorts — the longest cut in the set, the streetball read.
    pygame.draw.ellipse(surf, _CHARCOAL, (BCX - 11, BCY + 5, 24, 14))
    pygame.draw.ellipse(surf, (60, 60, 72), (BCX - 11, BCY + 5, 24, 14), 1)

    # High-tops — the streetball signature. The thick white midsole is the tell
    # at 40px, so it is built tall and capped with a dark top edge that snaps
    # the black upper away from the sole. The red ankle collar completes the
    # black/white/red high-top read.
    for hx in (21, 29):
        pygame.draw.rect(surf, _J_WHITE, (hx, BCY + 15, 11, 5), border_radius=1)
        pygame.draw.line(surf, _J_BLACK, (hx, BCY + 15), (hx + 10, BCY + 15), 1)
        pygame.draw.rect(surf, _J_BLACK, (hx, BCY + 10, 11, 6), border_radius=2)
        pygame.draw.ellipse(surf, _J_RED, (hx + 1, BCY + 8, 9, 5))
        pygame.draw.ellipse(surf, _J_WHITE, (hx + 2, BCY + 9, 7, 3))

    # BASKETBALL below the body against clear sky — the #1 identity prop, drawn
    # LAST over everything. Moved fully off the warm tail so its hot orange pops
    # against the sky instead of drowning orange-on-orange; a specular highlight
    # + vertical seam + two arc seams make it unmistakably a basketball.
    bx, by = BCX - 10, BCY + 26
    pygame.draw.circle(surf, (255, 140, 40), (bx, by), 9)
    pygame.draw.circle(surf, (20, 20, 20), (bx, by), 9, 1)
    pygame.draw.circle(surf, (255, 255, 255), (bx - 3, by - 3), 2)
    pygame.draw.line(surf, (20, 20, 20), (bx, by - 9), (bx, by + 9), 1)
    pygame.draw.arc(surf, (20, 20, 20), (bx - 11, by - 9, 15, 18), 0.3, math.pi - 0.3, 1)
    pygame.draw.arc(surf, (20, 20, 20), (bx - 4, by - 9, 15, 18),
                    math.pi + 0.3, 2 * math.pi - 0.3, 1)


build = _make_skin(_paint, base_fn=_base)
