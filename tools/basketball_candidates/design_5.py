"""THE STREETBALLER — the basketball candidate (DESIGN 5 of 5).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
roster is untouched.

Concept: the pickup-game blacktop look. Where the other kits read as team
uniforms, this one has no affiliation at all — a plain concrete-GREY mesh vest
(the body is re-plumaged neutral grey through the palette so the mesh fabric
reads across the whole torso), the longest baggy CHARCOAL shorts in the set,
and Jordan 1 high-tops in black/white/red as the streetball signature. A tiny
unaffiliated "1" is the only marking. The #1 identity prop is a BASKETBALL held
at DRIBBLE HEIGHT off the near side, drawn LAST so it reads as the ball being
worked mid-motion. The scarlet macaw head still crowns the grey kit so Pip is
still Pip.
"""
import math

import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

BCX, BCY = 32, 52

# Neutral concrete-grey re-plumage: the torso goes flat grey so the mesh-dot
# pattern reads as fabric across the whole vest and the black/white/red Jordan
# 1s + warm basketball are the highest-value notes. The head keeps the scarlet
# macaw so Pip is still Pip; gold aviators stay on as court shades.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(100, 100, 110),
    body_main=(135, 135, 145),       # concrete grey
    body_chest=(148, 148, 158),
    body_belly=(115, 115, 125),
    sheen=(200, 200, 215, 50),
    wing_main=BIRD_WING, wing_dark=BIRD_WING_D, wing_tip=BIRD_TIP,
    wing_secondary=(255, 200, 60), wing_highlight=(170, 210, 255),
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
_J_BLACK  = (28, 28, 36)             # Jordan 1 black upper
_J_WHITE  = (240, 238, 230)          # Jordan 1 midsole
_J_RED    = (200, 30, 40)            # Jordan 1 red accent


def _base(angle_deg):
    # Concrete-grey body, scarlet macaw head, court shades kept on.
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # Thin outline around the torso so the grey vest separates from a pale sky
    # instead of washing into it.
    pygame.draw.ellipse(surf, (100, 100, 110), (BCX - 19, BCY - 14, 38, 28), 1)

    # Mesh-dot pattern over the chest panel — a field of tiny dots simulating the
    # open weave of a streetball mesh jersey, clipped to the chest so it stays on
    # the fabric.
    old_clip = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX - 16, BCY - 12, 32, 22))
    for dy in range(BCY - 12, BCY + 10, 3):
        for dx in range(BCX - 16, BCX + 16, 3):
            pygame.draw.circle(surf, (115, 115, 125), (dx, dy), 1)
    surf.set_clip(old_clip)

    # Sleeveless armholes — charcoal seams where the arms pass through the vest,
    # the tell that says "tank", not a sleeved sweater.
    pygame.draw.line(surf, _CHARCOAL, (BCX - 17, BCY - 13), (BCX - 12, BCY + 3), 2)
    pygame.draw.line(surf, _CHARCOAL, (BCX + 15, BCY - 13), (BCX + 10, BCY + 3), 2)

    # Unaffiliated "1" — a single dark vertical bar with a short top flag, no team
    # markings, so the vest reads as a plain pickup jersey.
    pygame.draw.line(surf, _CHARCOAL, (BCX + 1, BCY - 8), (BCX + 1, BCY + 3), 4)
    pygame.draw.line(surf, _CHARCOAL, (BCX - 2, BCY - 8), (BCX + 1, BCY - 8), 2)

    # Hem seam so the vest reads as a garment edge, not paint.
    pygame.draw.line(surf, _CHARCOAL, (BCX - 12, BCY + 5), (BCX + 12, BCY + 5), 1)

    # Baggy charcoal shorts — the longest cut in the set, the streetball read.
    pygame.draw.ellipse(surf, _CHARCOAL, (BCX - 11, BCY + 5, 24, 14))
    pygame.draw.ellipse(surf, (60, 60, 72), (BCX - 11, BCY + 5, 24, 14), 1)

    # Jordan 1 high-tops — the streetball signature. Built up in layers so the
    # black/white/red reads as an actual sneaker at 40px, not a dark lump: white
    # midsole slab, black leather upper, the red ankle collar the shoe is known
    # for, a white inner, and a suggestion of the swoosh.
    for hx in (21, 29):
        pygame.draw.rect(surf, _J_WHITE, (hx, BCY + 15, 11, 4), border_radius=1)
        pygame.draw.rect(surf, _J_BLACK, (hx, BCY + 10, 11, 6), border_radius=2)
        pygame.draw.ellipse(surf, _J_RED, (hx + 1, BCY + 8, 9, 5))
        pygame.draw.ellipse(surf, _J_WHITE, (hx + 2, BCY + 9, 7, 3))
        pygame.draw.line(surf, _J_WHITE, (hx + 1, BCY + 13), (hx + 7, BCY + 11), 1)

    # BASKETBALL at DRIBBLE HEIGHT — the #1 identity prop, drawn LAST over
    # everything. Sat at thigh level on the near side so it reads as the ball
    # being worked mid-dribble; two arcs + the seam line make it unmistakably a
    # basketball rather than a plain orange dot at 40px.
    bx, by = BCX - 16, BCY + 12
    pygame.draw.circle(surf, (230, 115, 30), (bx, by), 7)
    pygame.draw.circle(surf, (20, 20, 20), (bx, by), 7, 1)
    pygame.draw.line(surf, (20, 20, 20), (bx, by - 7), (bx, by + 7), 1)
    pygame.draw.arc(surf, (20, 20, 20), (bx - 9, by - 7, 12, 14), 0.3, math.pi - 0.3, 1)
    pygame.draw.arc(surf, (20, 20, 20), (bx - 3, by - 7, 12, 14),
                    math.pi + 0.3, 2 * math.pi - 0.3, 1)


build = _make_skin(_paint, base_fn=_base)
